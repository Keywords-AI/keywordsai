import json
import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import requests

logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = "https://api.respan.ai/api/v1/traces/ingest"

LOG_TYPE_MAP = {
    "workflow": "workflow",
    "trace": "workflow",
    "agent": "agent",
    "task": "task",
    "step": "task",
    "tool": "tool",
    "function": "tool",
    "llm": "generation",
    "generation": "generation",
    "model": "generation",
    "chat": "chat",
    "prompt": "prompt",
}


@dataclass
class TraceContext:
    trace_id: str
    trace_name: Optional[str]
    workflow_name: Optional[str]
    metadata: Dict[str, Any]
    session_identifier: Optional[Union[str, int]] = None
    trace_group_identifier: Optional[Union[str, int]] = None
    start_time: Optional[datetime] = None
    customer_identifier: Optional[Union[str, int]] = None


def _get_attr(obj: Any, *keys: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        for key in keys:
            if key in obj:
                return obj[key]
    for key in keys:
        if hasattr(obj, key):
            return getattr(obj, key)
    return default


def _as_dict(value: Any) -> Optional[Dict[str, Any]]:
    if value is None:
        return None
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "model_dump"):
        try:
            return value.model_dump()
        except Exception:
            return None
    if hasattr(value, "dict"):
        try:
            return value.dict()
        except Exception:
            return None
    return None


def _pick_metadata_value(metadata: Optional[Dict[str, Any]], *keys: str) -> Any:
    if not metadata:
        return None
    for key in keys:
        if key in metadata:
            return metadata[key]
    return None


def _coerce_datetime(value: Any, reference: Optional[datetime] = None) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    if isinstance(value, (int, float)):
        numeric_value = float(value)
        if reference and numeric_value < 1_000_000_000:
            return reference + timedelta(seconds=numeric_value)
        if numeric_value > 100_000_000_000:
            return datetime.fromtimestamp(numeric_value / 1000, tz=timezone.utc)
        return datetime.fromtimestamp(numeric_value, tz=timezone.utc)
    if isinstance(value, str):
        trimmed = value.strip()
        try:
            return datetime.fromisoformat(trimmed.replace("Z", "+00:00"))
        except ValueError:
            try:
                numeric_value = float(trimmed)
                if reference and numeric_value < 1_000_000_000:
                    return reference + timedelta(seconds=numeric_value)
                if numeric_value > 100_000_000_000:
                    return datetime.fromtimestamp(numeric_value / 1000, tz=timezone.utc)
                return datetime.fromtimestamp(numeric_value, tz=timezone.utc)
            except ValueError:
                return None
    return None


def _coerce_token_count(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return int(float(stripped))
        except ValueError:
            return None
    return None


def _coerce_cost_value(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return float(stripped)
        except ValueError:
            return None
    return None


_MODEL_PRICING_PER_MILLION = {
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},
    "gpt-4o-mini": {"prompt": 0.150, "completion": 0.600},
    "gpt-4o-2024-11-20": {"prompt": 2.50, "completion": 10.00},
    "gpt-4o-2024-08-06": {"prompt": 2.50, "completion": 10.00},
    "gpt-4o-2024-05-13": {"prompt": 5.00, "completion": 15.00},
    "gpt-4o-mini-2024-07-18": {"prompt": 0.150, "completion": 0.600},
    "gpt-4-turbo": {"prompt": 10.00, "completion": 30.00},
    "gpt-4": {"prompt": 30.00, "completion": 60.00},
    "gpt-3.5-turbo": {"prompt": 0.50, "completion": 1.50},
    "gpt-3.5-turbo-0125": {"prompt": 0.50, "completion": 1.50},
}


def _normalize_model_name(model: Optional[str]) -> Optional[str]:
    if not model:
        return None
    model_name = str(model).strip()
    if not model_name:
        return None
    if "/" in model_name:
        model_name = model_name.split("/")[-1]
    if ":" in model_name:
        model_name = model_name.split(":")[-1]
    return model_name


def _get_model_pricing(model_name: Optional[str]) -> Optional[Dict[str, float]]:
    if not model_name:
        return None
    if model_name in _MODEL_PRICING_PER_MILLION:
        return _MODEL_PRICING_PER_MILLION[model_name]
    for key, pricing in _MODEL_PRICING_PER_MILLION.items():
        if model_name.startswith(f"{key}-"):
            return pricing
    return None


def _calculate_cost(
    model: Optional[str],
    prompt_tokens: Optional[int],
    completion_tokens: Optional[int],
) -> Optional[float]:
    if not model or prompt_tokens is None or completion_tokens is None:
        return None
    model_name = _normalize_model_name(model)
    pricing = _get_model_pricing(model_name)
    if not pricing:
        return None
    prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
    completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]
    return prompt_cost + completion_cost


def _infer_trace_start_time(spans: Sequence[Any]) -> Optional[datetime]:
    earliest: Optional[datetime] = None
    for span in spans:
        raw_value = _get_attr(span, "start_time", "started_at", "start", "start_timestamp")
        if isinstance(raw_value, (int, float)) and float(raw_value) < 1_000_000_000:
            continue
        if isinstance(raw_value, str):
            trimmed = raw_value.strip()
            if trimmed:
                try:
                    numeric_value = float(trimmed)
                    if numeric_value < 1_000_000_000:
                        continue
                except ValueError:
                    pass
        candidate = _coerce_datetime(raw_value)
        if candidate and candidate.year < 2001:
            continue
        if candidate and (earliest is None or candidate < earliest):
            earliest = candidate
    return earliest


def _serialize_value(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        trimmed = value.strip()
        if trimmed:
            try:
                json.loads(trimmed)
                return trimmed
            except Exception:
                return json.dumps(value)
        return json.dumps(value)
    try:
        return json.dumps(value, default=str)
    except Exception:
        return json.dumps(str(value))


def _format_rfc3339(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _is_hex_string(value: str, length: int) -> bool:
    if len(value) != length:
        return False
    try:
        int(value, 16)
        return True
    except ValueError:
        return False


def _normalize_trace_id(trace_id: str) -> str:
    if _is_hex_string(trace_id, 32):
        return trace_id.lower()
    return uuid.uuid5(uuid.NAMESPACE_DNS, trace_id).hex


def _normalize_span_id(span_id: str, trace_id: str) -> str:
    if _is_hex_string(span_id, 16):
        return span_id.lower()
    stable_seed = f"{trace_id}:{span_id}"
    return uuid.uuid5(uuid.NAMESPACE_DNS, stable_seed).hex[:16]


def _clean_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in payload.items() if value not in (None, {}, [])}


def _parse_json_value(value: Any) -> Any:
    if isinstance(value, str):
        trimmed = value.strip()
        if trimmed:
            try:
                return json.loads(trimmed)
            except Exception:
                return value
        return value
    return value


def _extract_metadata_payload(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not metadata:
        return {}
    raw_meta = metadata.get("metadata")
    if isinstance(raw_meta, dict):
        return dict(raw_meta)
    if isinstance(raw_meta, str):
        parsed = _parse_json_value(raw_meta)
        if isinstance(parsed, dict):
            return parsed
    return {}


def _merge_openinference_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not metadata:
        return {}
    merged = dict(metadata)
    extracted = _extract_metadata_payload(merged)
    if extracted:
        merged.pop("metadata", None)
        merged.update(extracted)
    return merged


def _find_root_span(spans: Sequence[Any]) -> Optional[Any]:
    if not spans:
        return None
    span_ids = set()
    for span in spans:
        span_id = _get_attr(span, "span_id", "id", "uid")
        if span_id is not None:
            span_ids.add(str(span_id))
    for span in spans:
        parent_id = _get_attr(span, "parent_id", "parent_span_id", "parentId")
        if not parent_id or str(parent_id) not in span_ids:
            return span
    return spans[0]


def _extract_span_metadata(span: Any) -> Dict[str, Any]:
    raw_metadata = _as_dict(_get_attr(span, "metadata", "attributes", "tags", "data")) or {}
    return _merge_openinference_metadata(raw_metadata)


def _to_prompt_messages(value: Any) -> Optional[List[Dict[str, Any]]]:
    parsed = _parse_json_value(value)
    if isinstance(parsed, list) and parsed and all(isinstance(item, dict) for item in parsed):
        if all("role" in item and "content" in item for item in parsed):
            return parsed
    if isinstance(parsed, dict):
        if isinstance(parsed.get("messages"), list):
            messages = parsed.get("messages") or []
            if messages and all(isinstance(item, dict) for item in messages):
                return messages
        if "role" in parsed and "content" in parsed:
            return [parsed]
    return None


def _to_completion_message(value: Any) -> Optional[Dict[str, Any]]:
    parsed = _parse_json_value(value)
    if isinstance(parsed, dict):
        if "role" in parsed and "content" in parsed:
            return parsed
        choices = parsed.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                message = first.get("message")
                if isinstance(message, dict) and "content" in message:
                    return message
    if isinstance(parsed, list) and parsed:
        first = parsed[0]
        if isinstance(first, dict) and "content" in first:
            return first
    return None


def _extract_openinference_messages(
    metadata: Optional[Dict[str, Any]], prefix: str
) -> Optional[List[Dict[str, Any]]]:
    if not metadata:
        return None
    prefix_token = f"{prefix}."
    messages: Dict[int, Dict[str, Any]] = {}
    message_contents: Dict[int, List[str]] = {}
    for key, value in metadata.items():
        if not isinstance(key, str) or not key.startswith(prefix_token):
            continue
        remainder = key[len(prefix_token) :]
        parts = remainder.split(".")
        if len(parts) < 3:
            continue
        index_str, section, field = parts[0], parts[1], parts[2]
        if not index_str.isdigit() or section != "message":
            continue
        index = int(index_str)
        if field == "role":
            messages.setdefault(index, {})["role"] = value
        elif field == "content":
            messages.setdefault(index, {})["content"] = value
        elif field == "contents" and len(parts) >= 6:
            if parts[-2] == "message_content" and parts[-1] == "text":
                message_contents.setdefault(index, []).append(str(value))
    if not messages:
        if not message_contents:
            return None
        messages = {index: {} for index in message_contents.keys()}
    if message_contents:
        for index, contents in message_contents.items():
            if contents and not messages.setdefault(index, {}).get("content"):
                messages[index]["content"] = "\n".join(contents)
    return [messages[index] for index in sorted(messages)]


def _extract_openinference_choice_texts(
    metadata: Optional[Dict[str, Any]],
) -> Optional[List[str]]:
    if not metadata:
        return None
    prefix_token = "llm.choices."
    choices: Dict[int, str] = {}
    for key, value in metadata.items():
        if not isinstance(key, str) or not key.startswith(prefix_token):
            continue
        parts = key.split(".")
        if len(parts) < 4:
            continue
        index_str = parts[1]
        if not index_str.isdigit():
            continue
        if parts[2] != "completion" or parts[3] != "text":
            continue
        choices[int(index_str)] = str(value)
    if not choices:
        return None
    return [choices[index] for index in sorted(choices)]


def _messages_to_text(messages: Sequence[Dict[str, Any]]) -> Optional[str]:
    if not messages:
        return None
    parts: List[str] = []
    for message in messages:
        content = message.get("content")
        if content is None:
            continue
        if isinstance(content, (dict, list)):
            parts.append(json.dumps(content, default=str))
        else:
            parts.append(str(content))
    if not parts:
        return None
    return "\n".join(parts)


def _is_blank_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        trimmed = value.strip()
        if not trimmed:
            return True
        if trimmed in ("[]", "{}", "null"):
            return True
        try:
            parsed = json.loads(trimmed)
            return parsed in (None, [], {})
        except Exception:
            return False
    if isinstance(value, (list, tuple, dict)) and not value:
        return True
    return False


class RespanAgnoExporter:
    """
    Export Agno traces/spans to Keywords AI tracing endpoint.

    The exporter accepts:
    - a trace object with a .spans collection
    - a dict with a "spans" field
    - a list of span objects/dicts
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        base_url: Optional[str] = None,
        environment: Optional[str] = None,
        customer_identifier: Optional[Union[str, int]] = None,
        timeout: int = 10,
    ) -> None:
        self.api_key = api_key or os.getenv("RESPAN_API_KEY")
        if base_url is None:
            base_url = (
                os.getenv("RESPAN_BASE_URL")
                or os.getenv("KEYWORDS_AI_BASE_URL")
                or "https://api.respan.ai/api"
            )
        self.endpoint = endpoint or self._build_endpoint(base_url)
        self.environment = (
            environment
            or os.getenv("RESPAN_ENVIRONMENT")
            or os.getenv("KEYWORDS_AI_ENVIRONMENT")
            or "production"
        )
        self.customer_identifier = (
            customer_identifier
            or os.getenv("RESPAN_CUSTOMER_IDENTIFIER")
            or os.getenv("KEYWORDS_AI_CUSTOMER_IDENTIFIER")
        )
        self.timeout = timeout

    def _build_endpoint(self, base_url: Optional[str]) -> str:
        if not base_url:
            return DEFAULT_ENDPOINT
        base = base_url.rstrip("/")
        if base.endswith("/v1/traces/ingest"):
            return base
        if base.endswith("/v1/traces"):
            return f"{base}/ingest"
        if base.endswith("/api"):
            return f"{base}/v1/traces/ingest"
        return f"{base}/api/v1/traces/ingest"

    def export(self, trace_or_spans: Any) -> List[Dict[str, Any]]:
        payloads = self.build_payload(trace_or_spans)
        if not payloads:
            return payloads
        if not self.api_key:
            logger.warning(
                "Keywords AI API key is not set; skipping export to %s", self.endpoint
            )
            return payloads
        self._send(payloads)
        return payloads

    def export_trace(self, trace_or_spans: Any) -> List[Dict[str, Any]]:
        return self.export(trace_or_spans)

    def build_payload(self, trace_or_spans: Any) -> List[Dict[str, Any]]:
        trace_obj, spans = self._normalize_trace(trace_or_spans)
        if not spans:
            return []
        trace_context = self._extract_trace_context(trace_obj, spans)
        trace_hex_id = _normalize_trace_id(trace_context.trace_id)
        span_id_map: Dict[str, str] = {}
        for span in spans:
            raw_span_id = _get_attr(span, "span_id", "id", "uid")
            if raw_span_id is None:
                continue
            raw_span_id = str(raw_span_id)
            span_id_map[raw_span_id] = _normalize_span_id(raw_span_id, trace_context.trace_id)
        payloads: List[Dict[str, Any]] = []
        for span in spans:
            payload = self._span_to_respan(span, trace_context, span_id_map)
            if payload:
                payloads.append(payload)
        if payloads:
            trace_output: Optional[str] = None
            for payload in payloads:
                output_value = payload.get("output")
                if _is_blank_value(output_value):
                    continue
                log_type = payload.get("log_type")
                if log_type == "generation":
                    trace_output = output_value
                    break
                if trace_output is None:
                    trace_output = output_value
            if trace_output is not None:
                for payload in payloads:
                    if _is_blank_value(payload.get("output")) and payload.get("log_type") in (
                        "workflow",
                        "agent",
                        "task",
                    ):
                        payload["output"] = trace_output
        return payloads

    def _normalize_trace(self, trace_or_spans: Any) -> Tuple[Optional[Any], List[Any]]:
        if trace_or_spans is None:
            return None, []
        if isinstance(trace_or_spans, (list, tuple, set)):
            return None, list(trace_or_spans)
        if isinstance(trace_or_spans, dict):
            spans = trace_or_spans.get("spans")
            if spans is not None:
                return trace_or_spans, list(spans)
            return None, [trace_or_spans]
        spans = _get_attr(trace_or_spans, "spans", "span_events")
        if spans is not None:
            return trace_or_spans, list(spans)
        return None, [trace_or_spans]

    def _extract_trace_context(self, trace_obj: Optional[Any], spans: Sequence[Any]) -> TraceContext:
        trace_id = _get_attr(trace_obj, "trace_id", "id", "uid")
        trace_name = _get_attr(trace_obj, "name", "trace_name", "title")
        workflow_name = _get_attr(trace_obj, "workflow_name", "workflow")
        session_identifier = _get_attr(trace_obj, "session_identifier", "session_id")
        trace_group_identifier = _get_attr(
            trace_obj, "trace_group_identifier", "group_identifier", "group_id"
        )

        trace_metadata = _as_dict(
            _get_attr(trace_obj, "metadata", "attributes", "tags")
        ) or {}
        trace_metadata = _merge_openinference_metadata(trace_metadata)

        customer_identifier = _get_attr(
            trace_obj,
            "customer_identifier",
            "customer_id",
            "user_id",
            "user_identifier",
            "user",
        )
        if not customer_identifier and isinstance(trace_metadata, dict):
            for key in ("customer_identifier", "customer_id", "user_id", "user"):
                if key in trace_metadata:
                    customer_identifier = trace_metadata.get(key)
                    break
        if not customer_identifier:
            customer_identifier = self.customer_identifier

        trace_start_time = _coerce_datetime(
            _get_attr(trace_obj, "start_time", "started_at", "start", "start_timestamp")
        )

        root_span = _find_root_span(spans)
        root_metadata = _extract_span_metadata(root_span) if root_span is not None else {}
        if root_metadata:
            root_user_metadata = _extract_metadata_payload(root_metadata)
            if root_user_metadata:
                trace_metadata = {**root_user_metadata, **trace_metadata}

        if not trace_id:
            for span in spans:
                trace_id = _get_attr(span, "trace_id", "traceId")
                if trace_id:
                    break
        if not trace_id:
            trace_id = str(uuid.uuid4())

        if not trace_name:
            trace_name = _pick_metadata_value(
                root_metadata,
                "graph.node.name",
                "agent.name",
                "agno.workflow.name",
                "workflow.name",
            )
        if not trace_name and trace_id:
            trace_name = str(trace_id)

        if not workflow_name:
            workflow_name = trace_name

        if not session_identifier:
            session_identifier = _pick_metadata_value(
                root_metadata,
                "session.id",
                "session_id",
                "session",
            )

        if not customer_identifier:
            customer_identifier = _pick_metadata_value(
                root_metadata,
                "user.id",
                "user_id",
                "customer_identifier",
                "customer_id",
                "user",
            ) or customer_identifier

        if not trace_start_time:
            trace_start_time = _infer_trace_start_time(spans)

        return TraceContext(
            trace_id=str(trace_id),
            trace_name=str(trace_name) if trace_name else None,
            workflow_name=str(workflow_name) if workflow_name else None,
            metadata=trace_metadata,
            session_identifier=session_identifier,
            trace_group_identifier=trace_group_identifier,
            start_time=trace_start_time,
            customer_identifier=customer_identifier,
        )

    def _span_to_respan(
        self,
        span: Any,
        trace_context: TraceContext,
        span_id_map: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        span_id = _get_attr(span, "span_id", "id", "uid")
        parent_id = _get_attr(span, "parent_id", "parent_span_id", "parentId")
        span_name = _get_attr(span, "name", "span_name", "operation_name")
        span_kind = _get_attr(span, "type", "span_type", "kind")
        span_path = _get_attr(span, "span_path", "path")

        span_metadata = _as_dict(
            _get_attr(span, "metadata", "attributes", "tags", "data")
        ) or {}
        span_metadata = _merge_openinference_metadata(span_metadata)

        if span_kind is None and isinstance(span_metadata, dict):
            span_kind = _pick_metadata_value(
                span_metadata,
                "openinference.span.kind",
                "span.kind",
            )

        if not span_name and isinstance(span_metadata, dict):
            span_name = _pick_metadata_value(
                span_metadata,
                "graph.node.name",
                "agent.name",
            )

        if not span_path and isinstance(span_metadata, dict):
            span_path = _pick_metadata_value(span_metadata, "graph.node.id")

        span_input = _get_attr(span, "input", "input_data", "request", "prompt")
        if span_input is None and isinstance(span_metadata, dict) and "input" in span_metadata:
            span_input = span_metadata.pop("input")
        if span_input is None and isinstance(span_metadata, dict):
            for key in ("input.value", "input_value", "traceloop.entity.input"):
                if key in span_metadata:
                    span_input = span_metadata.get(key)
                    break

        span_output = _get_attr(span, "output", "output_data", "response")
        if span_output is None and isinstance(span_metadata, dict) and "output" in span_metadata:
            span_output = span_metadata.pop("output")
        if span_output is None and isinstance(span_metadata, dict):
            for key in ("output.value", "output_value", "traceloop.entity.output"):
                if key in span_metadata:
                    span_output = span_metadata.get(key)
                    break

        input_messages = None
        output_messages = None
        if isinstance(span_metadata, dict):
            input_messages = _extract_openinference_messages(
                span_metadata, "llm.input_messages"
            )
            output_messages = _extract_openinference_messages(
                span_metadata, "llm.output_messages"
            )
            if span_input is None and input_messages:
                span_input = input_messages
            if span_output is None and output_messages:
                span_output = output_messages

        prompt_messages = _to_prompt_messages(span_input) if span_input is not None else None
        completion_message = (
            _to_completion_message(span_output) if span_output is not None else None
        )
        if prompt_messages is None and input_messages:
            prompt_messages = input_messages
        if completion_message is None and output_messages:
            completion_message = output_messages[0] if output_messages else None

        if _is_blank_value(span_output):
            choice_texts = _extract_openinference_choice_texts(span_metadata)
            if choice_texts:
                span_output = "\n".join(choice_texts)
                if completion_message is None:
                    completion_message = {"role": "assistant", "content": span_output}
            elif output_messages:
                output_text = _messages_to_text(output_messages)
                if output_text:
                    span_output = output_text
                    if completion_message is None:
                        completion_message = {"role": "assistant", "content": output_text}
        if span_output is None and isinstance(completion_message, dict):
            completion_content = completion_message.get("content")
            if completion_content:
                span_output = completion_content
        if completion_message is None and isinstance(span_output, str) and span_output.strip():
            completion_message = {"role": "assistant", "content": span_output.strip()}
        if prompt_messages is None and isinstance(span_input, str) and span_input.strip():
            prompt_messages = [{"role": "user", "content": span_input.strip()}]

        model = _get_attr(span, "model", "model_name")
        if model is None and isinstance(span_metadata, dict) and "model" in span_metadata:
            model = span_metadata.pop("model")
        if model is None and isinstance(span_metadata, dict):
            model = _pick_metadata_value(
                span_metadata,
                "llm.model_name",
                "llm.model",
                "embedding.model_name",
            )

        usage = _get_attr(span, "usage", "token_usage")
        if usage is None and isinstance(span_metadata, dict) and "usage" in span_metadata:
            usage = span_metadata.pop("usage")
        usage = _as_dict(usage)
        prompt_tokens_value: Optional[int] = None
        completion_tokens_value: Optional[int] = None
        if usage is None and isinstance(span_metadata, dict):
            prompt_tokens = span_metadata.get("llm.token_count.prompt")
            completion_tokens = span_metadata.get("llm.token_count.completion")
            total_tokens = span_metadata.get("llm.token_count.total")
            if any(value is not None for value in (prompt_tokens, completion_tokens, total_tokens)):
                usage = {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                }

        error = _get_attr(span, "error", "exception", "err")
        if error is None and isinstance(span_metadata, dict) and "error" in span_metadata:
            error = span_metadata.pop("error")

        start_time = _coerce_datetime(
            _get_attr(span, "start_time", "started_at", "start", "start_timestamp"),
            trace_context.start_time,
        )
        end_time = _coerce_datetime(
            _get_attr(span, "end_time", "ended_at", "end", "end_timestamp", "timestamp"),
            trace_context.start_time,
        )

        now = datetime.now(timezone.utc)
        if start_time is None and end_time is None:
            start_time = now
            end_time = now
        elif start_time is None:
            start_time = end_time
        elif end_time is None:
            end_time = start_time
        if start_time and end_time and end_time < start_time:
            end_time = start_time

        latency = _get_attr(span, "latency", "duration")
        if latency is None and start_time and end_time:
            latency = (end_time - start_time).total_seconds()
        if latency is not None and latency < 0:
            latency = 0.0

        if not span_id:
            span_id = str(uuid.uuid4())
        span_id_str = str(span_id)
        if not span_name:
            span_name = span_id

        log_type = self._map_log_type(span_kind, parent_id, model)

        merged_metadata = {**trace_context.metadata, **(span_metadata or {})}
        trace_hex_id = _normalize_trace_id(trace_context.trace_id)
        if span_id_map and span_id_str in span_id_map:
            span_hex_id = span_id_map[span_id_str]
        else:
            span_hex_id = _normalize_span_id(span_id_str, trace_context.trace_id)
        parent_hex_id = (
            span_id_map.get(str(parent_id))
            if span_id_map and parent_id is not None
            else _normalize_span_id(str(parent_id), trace_context.trace_id)
            if parent_id
            else None
        )

        if "agno_trace_id" not in merged_metadata:
            merged_metadata["agno_trace_id"] = trace_context.trace_id
        if "agno_span_id" not in merged_metadata:
            merged_metadata["agno_span_id"] = str(span_id)
        if parent_id and "agno_parent_id" not in merged_metadata:
            merged_metadata["agno_parent_id"] = str(parent_id)

        input_value = _serialize_value(span_input) if span_input is not None else None
        output_value = _serialize_value(span_output) if span_output is not None else None

        payload = {
            "trace_unique_id": trace_hex_id,
            "trace_name": trace_context.trace_name,
            "span_unique_id": span_hex_id,
            "span_parent_id": parent_hex_id,
            "span_name": str(span_name) if span_name else None,
            "span_path": span_path,
            "span_workflow_name": trace_context.workflow_name,
            "trace_id": trace_hex_id,
            "span_id": span_hex_id,
            "parent_id": parent_hex_id,
            "environment": self.environment,
            "customer_identifier": trace_context.customer_identifier,
            "log_type": log_type,
            "start_time": _format_rfc3339(start_time),
            "timestamp": _format_rfc3339(end_time),
            "latency": latency,
            "input": input_value,
            "output": output_value,
            "model": model,
            "metadata": merged_metadata or None,
            "session_identifier": trace_context.session_identifier,
            "trace_group_identifier": trace_context.trace_group_identifier,
        }
        if "prompt_messages" not in payload and prompt_messages is not None:
            payload["prompt_messages"] = prompt_messages
        if "completion_message" not in payload and completion_message is not None:
            payload["completion_message"] = completion_message
        if "respan_params" not in payload:
            payload["respan_params"] = {
                "environment": self.environment,
                "has_webhook": False,
            }
        if "disable_log" not in payload:
            payload["disable_log"] = False

        if usage:
            prompt_tokens = usage.get("prompt_tokens") or usage.get("input_tokens")
            completion_tokens = usage.get("completion_tokens") or usage.get("output_tokens")
            total_tokens = usage.get("total_tokens") or usage.get("total")

            payload["prompt_tokens"] = prompt_tokens
            payload["completion_tokens"] = completion_tokens
            payload["total_request_tokens"] = total_tokens

            coerced_total = _coerce_token_count(total_tokens)
            if coerced_total is None or coerced_total == 0:
                prompt_tokens_value = _coerce_token_count(prompt_tokens)
                completion_tokens_value = _coerce_token_count(completion_tokens)
                coerced_prompt = prompt_tokens_value or 0
                coerced_completion = completion_tokens_value or 0
                if coerced_prompt or coerced_completion:
                    payload["total_request_tokens"] = coerced_prompt + coerced_completion
            else:
                prompt_tokens_value = _coerce_token_count(prompt_tokens)
                completion_tokens_value = _coerce_token_count(completion_tokens)

        cost = _coerce_cost_value(_get_attr(span, "cost"))
        if cost is None and isinstance(span_metadata, dict):
            cost = _coerce_cost_value(
                span_metadata.get("cost") or span_metadata.get("llm.cost.total")
            )
            if cost is None:
                prompt_cost = _coerce_cost_value(span_metadata.get("llm.cost.prompt"))
                completion_cost = _coerce_cost_value(
                    span_metadata.get("llm.cost.completion")
                )
                if prompt_cost is not None or completion_cost is not None:
                    cost = (prompt_cost or 0.0) + (completion_cost or 0.0)
        if cost is None:
            cost = _calculate_cost(model, prompt_tokens_value, completion_tokens_value)
        if cost is not None:
            payload["cost"] = cost

        if error:
            payload["error_message"] = str(error)
            payload["status_code"] = 500
        else:
            payload["status_code"] = _get_attr(span, "status_code") or 200

        tool_name = (
            _get_attr(span, "tool_name", "tool")
            or merged_metadata.get("tool_name")
            or merged_metadata.get("tool.name")
        )
        if tool_name:
            payload["span_tools"] = [str(tool_name)]

        if not payload.get("span_unique_id") and payload.get("trace_unique_id"):
            payload["span_unique_id"] = payload["trace_unique_id"]

        cleaned_payload = _clean_payload(payload)
        return cleaned_payload

    def _map_log_type(
        self, span_kind: Any, parent_id: Optional[str], model: Optional[str]
    ) -> str:
        if span_kind:
            kind_str = str(span_kind).lower()
            for key, value in LOG_TYPE_MAP.items():
                if key in kind_str:
                    return value
        if model:
            return "generation"
        if parent_id is None:
            return "workflow"
        return "task"

    def _send(self, payloads: List[Dict[str, Any]]) -> None:
        try:
            response = requests.post(
                self.endpoint,
                json=payloads,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )
            if response.status_code not in (200, 201):
                logger.warning(
                    "Keywords AI export failed with status %s: %s",
                    response.status_code,
                    response.text,
                )
        except Exception as exc:
            logger.warning("Keywords AI export request failed: %s", exc)
