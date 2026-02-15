"""Respan Braintrust Exporter.

RespanBraintrustExporter - Exports Braintrust logs to Respan for tracing.
"""

from __future__ import annotations

import logging
import math
import os
import threading
from typing import Any, Dict, Optional

import requests

from respan_sdk.constants.api_constants import (
    DEFAULT_RESPAN_API_BASE_URL,
    TRACES_INGEST_PATH,
)
from respan_sdk.constants.llm_logging import LOG_TYPE_CUSTOM, LogMethodChoices
from respan_sdk.respan_types.log_types import RespanFullLogParams

from respan_exporter_braintrust.constants import BRAINTRUST_SPAN_TYPE_TO_LOG_TYPE
from respan_exporter_braintrust.utils import (
    coerce_str,
    compute_total_request_tokens,
    extract_token_usage,
    format_id,
    format_timestamp,
    json_dumps_safe,
    sanitize_json,
)

try:
    import braintrust
    from braintrust.logger import _extract_attachments
    from braintrust.merge_row_batch import merge_row_batch
except ImportError:  # pragma: no cover - runtime dependency
    braintrust = None
    _extract_attachments = None
    merge_row_batch = None

logger = logging.getLogger(__name__)


class RespanBraintrustExporter:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        log_endpoint: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 10.0,
        raise_on_error: bool = False,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("RESPAN_API_KEY")
        if not self.api_key:
            raise ValueError("RESPAN_API_KEY must be set to use RespanBraintrustExporter.")

        self.base_url = base_url or os.getenv(
            "RESPAN_BASE_URL",
            DEFAULT_RESPAN_API_BASE_URL,
        )
        self.log_endpoint = log_endpoint or self._build_log_endpoint(self.base_url)
        self.timeout = timeout
        self.raise_on_error = raise_on_error
        self.session = session or requests.Session()
        if session is None:
            # Avoid unexpected proxy-related failures from environment variables.
            self.session.trust_env = False

        export_headers = headers.copy() if headers else {}
        export_headers.setdefault("Authorization", f"Bearer {self.api_key}")
        export_headers.setdefault("Content-Type", "application/json")
        self.headers = export_headers

        self._lock = threading.Lock()
        self._buffer: list[Any] = []
        self._previous_logger: Any | None = None
        self._masking_function: Optional[Any] = None

    def __enter__(self) -> "RespanBraintrustExporter":
        self.install()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        del exc_type, exc_value, traceback
        self.uninstall()

    def install(self) -> "RespanBraintrustExporter":
        if braintrust is None:
            raise ImportError("braintrust must be installed to use RespanBraintrustExporter.")

        state = braintrust._internal_get_global_state()
        self._previous_logger = getattr(state._override_bg_logger, "logger", None)
        state._override_bg_logger.logger = self
        return self

    def uninstall(self) -> None:
        if braintrust is None:
            return
        state = braintrust._internal_get_global_state()
        if getattr(state._override_bg_logger, "logger", None) is self:
            state._override_bg_logger.logger = self._previous_logger
        self._previous_logger = None

    def enforce_queue_size_limit(self, enforce: bool) -> None:
        del enforce
        return

    def set_masking_function(self, masking_function: Optional[Any]) -> None:
        self._masking_function = masking_function

    def log(self, *args: Any) -> None:
        with self._lock:
            self._buffer.extend(args)

    def flush(self, batch_size: int | None = None) -> None:
        del batch_size
        with self._lock:
            if not self._buffer:
                return
            items = self._buffer
            self._buffer = []

        records = [item.get() for item in items]
        if merge_row_batch is not None:
            records = merge_row_batch(records)

        attachments: list[Any] = []
        payloads: list[Dict[str, Any]] = []
        for record in records:
            if _extract_attachments is not None:
                _extract_attachments(record, attachments)

            payloads.append(self._build_payload(record))

        if payloads:
            self._post_payload(payloads)

    def _post_payload(self, payloads: list[Dict[str, Any]]) -> None:
        response = self.session.post(
            self.log_endpoint,
            headers=self.headers,
            json=payloads,
            timeout=self.timeout,
        )
        if response.ok:
            return

        message = f"RespanBraintrustExporter request failed: {response.status_code} {response.text}"
        if self.raise_on_error:
            raise RuntimeError(message)
        logger.warning(message)

    def _build_payload(self, record: Dict[str, Any]) -> Dict[str, Any]:
        span_attributes = record.get("span_attributes") or {}
        span_type = span_attributes.get("type")
        if isinstance(span_type, str):
            span_type_key = span_type.lower()
        else:
            span_type_key = None

        span_parents = record.get("span_parents") or []
        span_parent_id = span_parents[0] if span_parents else None

        metrics = record.get("metrics") or {}
        start_time = metrics.get("start")
        end_time = metrics.get("end")
        latency = None
        if isinstance(start_time, (int, float)) and isinstance(end_time, (int, float)):
            latency = max(0.0, end_time - start_time)

        input_value = record.get("input")
        output_value = record.get("output")
        metadata = self._build_metadata(record)
        model = self._extract_model(record)
        prompt_tokens, completion_tokens = extract_token_usage(record=record)
        total_request_tokens = compute_total_request_tokens(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        if self._masking_function:
            input_value = self._apply_masking(input_value, "input")
            output_value = self._apply_masking(output_value, "output")
            if metadata is not None:
                metadata = self._apply_masking(metadata, "metadata")

        payload = {
            "log_method": LogMethodChoices.TRACING_INTEGRATION.value,
            "log_type": BRAINTRUST_SPAN_TYPE_TO_LOG_TYPE.get(span_type_key or "", LOG_TYPE_CUSTOM),
            "trace_unique_id": format_id(record.get("root_span_id")),
            "trace_name": span_attributes.get("name") if not span_parents else None,
            "span_unique_id": format_id(record.get("span_id")),
            "span_parent_id": format_id(span_parent_id),
            "span_name": span_attributes.get("name"),
            "input": input_value,
            "output": output_value,
            "error_message": record.get("error"),
            "metadata": metadata,
            "model": model,
            "latency": latency,
            "start_time": format_timestamp(start_time),
            "timestamp": format_timestamp(end_time),
            "status_code": 500 if record.get("error") else 200,
        }

        # Populate full_request / full_response for easier debugging in UI.
        # These should be JSON-serializable objects (dict/list) rather than strings.
        full_request: Dict[str, Any] = {}
        if input_value is not None:
            full_request["input"] = input_value
        if record.get("metadata") is not None:
            full_request["metadata"] = record.get("metadata")
        if record.get("span_attributes") is not None:
            full_request["span_attributes"] = record.get("span_attributes")
        if model is not None:
            full_request["model"] = model

        full_response: Dict[str, Any] = {}
        if output_value is not None:
            full_response["output"] = output_value
        if record.get("error") is not None:
            full_response["error"] = record.get("error")
        if record.get("scores") is not None:
            full_response["scores"] = record.get("scores")
        if record.get("metrics") is not None:
            full_response["metrics"] = record.get("metrics")

        if full_request:
            payload["full_request"] = full_request
        if full_response:
            payload["full_response"] = full_response

        if model is None:
            payload.pop("model", None)
        if prompt_tokens is not None:
            payload["prompt_tokens"] = prompt_tokens
        if completion_tokens is not None:
            payload["completion_tokens"] = completion_tokens
        if total_request_tokens is not None:
            payload["total_request_tokens"] = total_request_tokens

        # Some downstream pipelines prefer usage.* fields; include them when we have token counts.
        if prompt_tokens is not None or completion_tokens is not None:
            payload["usage"] = {
                "prompt_tokens": prompt_tokens or 0,
                "completion_tokens": completion_tokens or 0,
                "total_tokens": total_request_tokens or (prompt_tokens or 0) + (completion_tokens or 0),
            }

        sanitized_payload = sanitize_json(payload)
        validated_payload = RespanFullLogParams.model_validate(
            sanitized_payload
        ).model_dump(mode="json", exclude_none=True)

        # Keep stable explicit nulls for key trace fields (tests/UI expect presence).
        if "span_parent_id" not in validated_payload and "span_parent_id" in sanitized_payload:
            validated_payload["span_parent_id"] = None
        if "trace_name" not in validated_payload and "trace_name" in sanitized_payload:
            validated_payload["trace_name"] = None

        return validated_payload

    def _extract_model(self, record: Dict[str, Any]) -> Optional[str]:
        model = coerce_str(record.get("model"))
        if model:
            return model

        metadata = record.get("metadata")
        if isinstance(metadata, dict):
            for key in ("model", "model_name", "llm_model"):
                model = coerce_str(metadata.get(key))
                if model:
                    return model

        span_attributes = record.get("span_attributes")
        if isinstance(span_attributes, dict):
            for key in ("model", "model_name", "llm_model"):
                model = coerce_str(span_attributes.get(key))
                if model:
                    return model

        return None

    def _build_metadata(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        metadata: Dict[str, Any] = {}
        base_metadata = record.get("metadata")
        if isinstance(base_metadata, dict):
            metadata.update(base_metadata)
        elif base_metadata is not None:
            metadata["braintrust_metadata"] = base_metadata

        if record.get("tags") is not None:
            metadata["braintrust_tags"] = record.get("tags")
        if record.get("scores") is not None:
            metadata["braintrust_scores"] = record.get("scores")
        if record.get("metrics") is not None:
            # UI safety: keep metrics readable, but avoid sending nested objects
            # that some pretty renderers might try to render as a React child.
            metadata["braintrust_metrics"] = json_dumps_safe(record.get("metrics"))
        if record.get("span_attributes") is not None:
            metadata["braintrust_span_attributes"] = record.get("span_attributes")
        if record.get("context") is not None:
            metadata["braintrust_context"] = record.get("context")
        if record.get("id") is not None:
            metadata["braintrust_log_id"] = format_id(record.get("id"))

        for field in ("project_id", "experiment_id", "dataset_id", "org_id"):
            if record.get(field) is not None:
                metadata[f"braintrust_{field}"] = format_id(record.get(field))

        if not metadata:
            return None

        # UI safety: ensure every metadata value is a primitive (or None).
        # React error #31 happens when a UI tries to render an object directly.
        safe_metadata: Dict[str, Any] = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, bool)) or value is None:
                safe_metadata[key] = value
                continue
            if isinstance(value, float):
                safe_metadata[key] = value if math.isfinite(value) else None
                continue

            safe_metadata[key] = json_dumps_safe(value)

        return safe_metadata

    def _apply_masking(self, value: Any, field_name: str) -> Any:
        if not self._masking_function:
            return value
        try:
            return self._masking_function(value)
        except Exception as exc:  # pragma: no cover - defensive
            error_type = type(exc).__name__
            return f"ERROR: Failed to mask field '{field_name}' - {error_type}"

    @staticmethod
    def _build_log_endpoint(base_url: str) -> str:
        base_url = base_url.rstrip("/")
        if base_url.endswith("/api"):
            return f"{base_url}/{TRACES_INGEST_PATH}"
        return f"{base_url}/api/{TRACES_INGEST_PATH}"
