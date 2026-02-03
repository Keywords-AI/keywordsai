import json
import logging
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Optional

import requests
from keywordsai_sdk.keywordsai_types.log_types import KeywordsAIFullLogParams

from respan_exporter_superagent.types import ErrorMessage
from respan_exporter_superagent.types import InputValue
from respan_exporter_superagent.types import OutputValue
from respan_exporter_superagent.types import Payload
from respan_exporter_superagent.types import RespanExportParams
from respan_exporter_superagent.types import ValidatedPayload


logger = logging.getLogger(__name__)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def safe_json_dumps(value: Any) -> str:
    try:
        return json.dumps(value, default=str)
    except Exception:
        return str(value)


def build_payload(
    *,
    method_name: str,
    start_time: datetime,
    end_time: datetime,
    status: str,
    input_value: InputValue,
    output_value: OutputValue,
    error_message: ErrorMessage,
    export_params: Optional[RespanExportParams],
) -> Payload:
    params = export_params or {}

    payload: Payload = {
        "span_workflow_name": params.get("workflow_name", "superagent"),
        "span_name": params.get("span_name", f"superagent.{method_name}"),
        "log_type": params.get("log_type", "tool"),
        "start_time": start_time.isoformat(),
        "timestamp": end_time.isoformat(),
        "latency": (end_time - start_time).total_seconds(),
        "status": status,
    }

    if input_value is not None:
        payload["input"] = safe_json_dumps(input_value) if not isinstance(input_value, str) else input_value
    if output_value is not None:
        payload["output"] = safe_json_dumps(output_value) if not isinstance(output_value, str) else output_value
    if error_message:
        payload["error_message"] = error_message

    trace_unique_id = params.get("trace_unique_id") or params.get("trace_id")
    if trace_unique_id:
        payload["trace_unique_id"] = trace_unique_id
        payload["trace_name"] = params.get("trace_name", payload["span_workflow_name"])

    span_unique_id = params.get("span_unique_id") or params.get("span_id")
    if span_unique_id:
        payload["span_unique_id"] = span_unique_id
    span_parent_id = params.get("span_parent_id") or params.get("parent_span_id")
    if span_parent_id:
        payload["span_parent_id"] = span_parent_id

    session_identifier = params.get("session_identifier")
    if session_identifier:
        payload["session_identifier"] = session_identifier

    customer_identifier = params.get("customer_identifier")
    if customer_identifier:
        payload["customer_identifier"] = customer_identifier

    metadata: Payload = {}
    if isinstance(params.get("metadata"), dict):
        metadata.update(params["metadata"])
    metadata["integration"] = "superagent"
    metadata["method"] = method_name

    if metadata:
        payload["metadata"] = metadata

    return payload


def validate_payload(payload: Payload) -> ValidatedPayload:
    validated = KeywordsAIFullLogParams(**payload)
    return validated.model_dump(mode="json", exclude_none=True)


def send_payloads(
    *,
    api_key: str,
    endpoint: str,
    timeout: int,
    payloads: list[ValidatedPayload],
) -> None:
    try:
        response = requests.post(
            endpoint,
            json=payloads,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )
        if response.status_code >= 300:
            logger.warning("Respan ingest error status_code=%s", response.status_code)
    except Exception as exc:
        logger.exception("Respan ingest request failed: %s", exc)

