import json
import logging
from datetime import datetime
from datetime import timezone
from typing import Any, Dict, Optional

import requests
from respan_sdk.respan_types import RespanFullLogParams
from respan_sdk.respan_types import RespanParams
from respan_sdk.utils import RetryHandler


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
    input_value: Any,
    output_value: Any,
    error_message: Optional[str],
    export_params: Optional[RespanParams],
) -> Dict[str, Any]:
    params = export_params or RespanParams()

    payload: Dict[str, Any] = {
        "span_workflow_name": params.span_workflow_name or "superagent",
        "span_name": params.span_name or f"superagent.{method_name}",
        "log_type": params.log_type or "tool",
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

    if params.trace_unique_id:
        payload["trace_unique_id"] = params.trace_unique_id
        payload["trace_name"] = params.trace_name or payload["span_workflow_name"]

    if params.span_unique_id:
        payload["span_unique_id"] = params.span_unique_id
    if params.span_parent_id:
        payload["span_parent_id"] = params.span_parent_id

    if params.session_identifier:
        payload["session_identifier"] = params.session_identifier

    if params.customer_identifier:
        payload["customer_identifier"] = params.customer_identifier

    metadata: Dict[str, Any] = {}
    if params.metadata:
        metadata.update(params.metadata)
    metadata["integration"] = "superagent"
    metadata["method"] = method_name

    if metadata:
        payload["metadata"] = metadata

    return payload


def validate_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    validated = RespanFullLogParams(**payload)
    return validated.model_dump(mode="json", exclude_none=True)


def send_payloads(
    *,
    api_key: str,
    endpoint: str,
    timeout: int,
    payloads: list[Dict[str, Any]],
) -> None:
    handler = RetryHandler(max_retries=3, retry_delay=1.0, backoff_multiplier=2.0, max_delay=30.0)

    def _post() -> None:
        response = requests.post(
            endpoint,
            json=payloads,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )
        if response.status_code >= 500:
            raise RuntimeError(f"Respan ingest server error status_code={response.status_code}")
        if response.status_code >= 300:
            logger.warning("Respan ingest client error status_code=%s", response.status_code)

    try:
        handler.execute(func=_post, context="respan superagent ingest")
    except Exception as exc:
        logger.exception("Respan ingest failed after retries: %s", exc)

