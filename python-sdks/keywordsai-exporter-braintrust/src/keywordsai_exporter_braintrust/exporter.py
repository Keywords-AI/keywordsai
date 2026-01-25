from __future__ import annotations

import datetime
import logging
import os
import threading
import uuid
from typing import Any, Dict, Optional

import requests

try:
    import braintrust
    from braintrust.logger import _extract_attachments
    from braintrust.merge_row_batch import merge_row_batch
except ImportError:  # pragma: no cover - runtime dependency
    braintrust = None
    _extract_attachments = None
    merge_row_batch = None

DEFAULT_BASE_URL = "https://api.keywordsai.co/api"
DEFAULT_TRACE_PATH = "v1/traces/ingest"

SPAN_TYPE_TO_LOG_TYPE = {
    "llm": "generation",
    "chat": "chat",
    "score": "score",
    "function": "function",
    "eval": "workflow",
    "task": "task",
    "tool": "tool",
    "automation": "workflow",
    "facet": "custom",
    "preprocessor": "custom",
}

logger = logging.getLogger("keywordsai_exporter_braintrust")


class KeywordsAIExporter:
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
        self.api_key = api_key or os.getenv("KEYWORDSAI_API_KEY")
        if not self.api_key:
            raise ValueError("KEYWORDSAI_API_KEY must be set to use KeywordsAIExporter.")

        self.base_url = base_url or os.getenv("KEYWORDSAI_BASE_URL", DEFAULT_BASE_URL)
        self.log_endpoint = log_endpoint or self._build_log_endpoint(self.base_url)
        self.timeout = timeout
        self.raise_on_error = raise_on_error
        self.session = session or requests.Session()

        export_headers = headers.copy() if headers else {}
        export_headers.setdefault("Authorization", f"Bearer {self.api_key}")
        export_headers.setdefault("Content-Type", "application/json")
        self.headers = export_headers

        self._lock = threading.Lock()
        self._buffer: list[Any] = []
        self._previous_logger: Any | None = None
        self._masking_function: Optional[Any] = None

    def __enter__(self) -> "KeywordsAIExporter":
        self.install()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        del exc_type, exc_value, traceback
        self.uninstall()

    def install(self) -> "KeywordsAIExporter":
        if braintrust is None:
            raise ImportError("braintrust must be installed to use KeywordsAIExporter.")

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
            merged_batches = merge_row_batch(records)
            records = []
            for batch in merged_batches:
                records.extend(batch)

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

        message = f"KeywordsAIExporter request failed: {response.status_code} {response.text}"
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
        prompt_tokens, completion_tokens = self._extract_token_usage(record)
        total_request_tokens = self._compute_total_request_tokens(prompt_tokens, completion_tokens)

        if self._masking_function:
            input_value = self._apply_masking(input_value, "input")
            output_value = self._apply_masking(output_value, "output")
            if metadata is not None:
                metadata = self._apply_masking(metadata, "metadata")

        payload = {
            "log_method": "tracing_integration",
            "log_type": SPAN_TYPE_TO_LOG_TYPE.get(span_type_key, "custom"),
            "trace_unique_id": self._format_id(record.get("root_span_id")),
            "trace_name": span_attributes.get("name") if not span_parents else None,
            "span_unique_id": self._format_id(record.get("span_id")),
            "span_parent_id": self._format_id(span_parent_id),
            "span_name": span_attributes.get("name"),
            "input": input_value,
            "output": output_value,
            "error_message": record.get("error"),
            "metadata": metadata,
            "model": model,
            "latency": latency,
            "start_time": self._format_timestamp(start_time),
            "timestamp": self._format_timestamp(end_time),
            "status_code": 500 if record.get("error") else 200,
        }

        if model is None:
            payload.pop("model", None)
        if prompt_tokens is not None:
            payload["prompt_tokens"] = prompt_tokens
        if completion_tokens is not None:
            payload["completion_tokens"] = completion_tokens
        if total_request_tokens is not None:
            payload["total_request_tokens"] = total_request_tokens

        return self._sanitize_json(payload)

    @staticmethod
    def _coerce_int(value: Any) -> Optional[int]:
        if value is None or isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return None
        return None

    @staticmethod
    def _coerce_str(value: Any) -> Optional[str]:
        if value is None or isinstance(value, bool):
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float)):
            return str(value)
        return None

    @staticmethod
    def _format_id(value: Any) -> Optional[str]:
        if value is None or isinstance(value, bool):
            return None
        if isinstance(value, uuid.UUID):
            return value.hex
        if isinstance(value, str):
            try:
                return uuid.UUID(value).hex
            except ValueError:
                return value
        if isinstance(value, int):
            return str(value)
        return str(value)

    def _extract_model(self, record: Dict[str, Any]) -> Optional[str]:
        model = self._coerce_str(record.get("model"))
        if model:
            return model

        metadata = record.get("metadata")
        if isinstance(metadata, dict):
            for key in ("model", "model_name", "llm_model"):
                model = self._coerce_str(metadata.get(key))
                if model:
                    return model

        span_attributes = record.get("span_attributes")
        if isinstance(span_attributes, dict):
            for key in ("model", "model_name", "llm_model"):
                model = self._coerce_str(span_attributes.get(key))
                if model:
                    return model

        return None

    def _extract_token_usage(self, record: Dict[str, Any]) -> tuple[Optional[int], Optional[int]]:
        def read_tokens(source: Any) -> tuple[Optional[int], Optional[int]]:
            if not isinstance(source, dict):
                return None, None

            prompt = self._coerce_int(source.get("prompt_tokens"))
            completion = self._coerce_int(source.get("completion_tokens"))
            if prompt is None and completion is None:
                prompt = self._coerce_int(source.get("input_tokens"))
                completion = self._coerce_int(source.get("output_tokens"))

            return prompt, completion

        metrics = record.get("metrics")
        prompt_tokens, completion_tokens = read_tokens(metrics)
        if prompt_tokens is None and completion_tokens is None and isinstance(metrics, dict):
            usage = metrics.get("usage") or metrics.get("tokens")
            prompt_tokens, completion_tokens = read_tokens(usage)

        if prompt_tokens is None and completion_tokens is None:
            metadata = record.get("metadata")
            prompt_tokens, completion_tokens = read_tokens(metadata)
            if prompt_tokens is None and completion_tokens is None and isinstance(metadata, dict):
                usage = metadata.get("usage") or metadata.get("token_usage")
                prompt_tokens, completion_tokens = read_tokens(usage)

        return prompt_tokens, completion_tokens

    @staticmethod
    def _compute_total_request_tokens(
        prompt_tokens: Optional[int], completion_tokens: Optional[int]
    ) -> Optional[int]:
        if prompt_tokens is None and completion_tokens is None:
            return None
        return (prompt_tokens or 0) + (completion_tokens or 0)

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
            metadata["braintrust_metrics"] = record.get("metrics")
        if record.get("span_attributes") is not None:
            metadata["braintrust_span_attributes"] = record.get("span_attributes")
        if record.get("context") is not None:
            metadata["braintrust_context"] = record.get("context")
        if record.get("id") is not None:
            metadata["braintrust_log_id"] = self._format_id(record.get("id"))

        for field in ("project_id", "experiment_id", "dataset_id", "org_id"):
            if record.get(field) is not None:
                metadata[f"braintrust_{field}"] = self._format_id(record.get(field))

        return metadata or None

    def _apply_masking(self, value: Any, field_name: str) -> Any:
        if not self._masking_function:
            return value
        try:
            return self._masking_function(value)
        except Exception as exc:  # pragma: no cover - defensive
            error_type = type(exc).__name__
            return f"ERROR: Failed to mask field '{field_name}' - {error_type}"

    @staticmethod
    def _format_timestamp(value: Any) -> Optional[str]:
        if isinstance(value, (int, float)):
            return datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc).isoformat()
        if isinstance(value, datetime.datetime):
            return value.astimezone(datetime.timezone.utc).isoformat()
        return None

    @staticmethod
    def _build_log_endpoint(base_url: str) -> str:
        base_url = base_url.rstrip("/")
        if base_url.endswith("/api"):
            return f"{base_url}/{DEFAULT_TRACE_PATH}"
        return f"{base_url}/api/{DEFAULT_TRACE_PATH}"

    @staticmethod
    def _sanitize_json(value: Any) -> Any:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, datetime.datetime):
            return value.astimezone(datetime.timezone.utc).isoformat()
        if isinstance(value, dict):
            return {str(k): KeywordsAIExporter._sanitize_json(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [KeywordsAIExporter._sanitize_json(v) for v in value]
        return str(value)
