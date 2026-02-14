import base64
import json
from typing import Dict, Optional, Sequence, List, Any

import requests
from opentelemetry.context import attach, detach, set_value
from opentelemetry.context import _SUPPRESS_INSTRUMENTATION_KEY
from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.trace import StatusCode

from ..utils.logging import get_respan_logger, build_spans_export_preview
from ..utils.preprocessing.span_processing import should_make_root_span
from ..constants.generic_constants import LOGGER_NAME_EXPORTER

logger = get_respan_logger(LOGGER_NAME_EXPORTER)


class ModifiedSpan:
    """A proxy wrapper that forwards all attributes to the original span except parent_span_id"""

    def __init__(self, original_span: ReadableSpan):
        self._original_span = original_span

    def __getattr__(self, name):
        """Forward all attribute access to the original span"""
        if name in ("parent_span_id", "parent", "_parent"):
            return None  # Override parent to None for root-promoted spans
        return getattr(self._original_span, name)


def _convert_attribute_value(value: Any) -> Optional[Dict[str, Any]]:
    """Convert a Python attribute value to OTLP JSON typed wrapper."""
    if value is None:
        return None
    if isinstance(value, bool):
        return {"boolValue": value}
    if isinstance(value, int):
        return {"intValue": str(value)}
    if isinstance(value, float):
        return {"doubleValue": value}
    if isinstance(value, str):
        return {"stringValue": value}
    if isinstance(value, bytes):
        return {"bytesValue": base64.b64encode(value).decode("ascii")}
    if isinstance(value, (list, tuple)):
        converted = []
        for item in value:
            v = _convert_attribute_value(item)
            if v is not None:
                converted.append(v)
        return {"arrayValue": {"values": converted}}
    # Fallback: stringify
    return {"stringValue": str(value)}


def _convert_attributes(attributes: Any) -> List[Dict[str, Any]]:
    """Convert a mapping of attributes to OTLP JSON key-value list."""
    if not attributes:
        return []
    result = []
    for key, value in attributes.items():
        converted = _convert_attribute_value(value)
        if converted is not None:
            result.append({"key": str(key), "value": converted})
    return result


def _span_to_otlp_json(span: ReadableSpan) -> Dict[str, Any]:
    """Convert a ReadableSpan (or ModifiedSpan) to OTLP JSON span dict."""
    ctx = span.get_span_context()

    trace_id = format(ctx.trace_id, "032x") if ctx else ""
    span_id = format(ctx.span_id, "016x") if ctx else ""

    # Parent span ID
    parent_span_id = ""
    parent = getattr(span, "parent", None)
    if parent is not None:
        parent_sid = getattr(parent, "span_id", None)
        if parent_sid:
            parent_span_id = format(parent_sid, "016x")

    # Timestamps as nanosecond strings
    start_time_ns = str(span.start_time) if span.start_time else "0"
    end_time_ns = str(span.end_time) if span.end_time else "0"

    # Span kind mapping: OTel Python SpanKind enum is 0-4 (INTERNAL=0, SERVER=1, ...)
    # but OTLP wire format is 1-5 (UNSPECIFIED=0, INTERNAL=1, SERVER=2, ...)
    kind_value = 0  # SPAN_KIND_UNSPECIFIED
    if span.kind is not None:
        raw = span.kind.value if hasattr(span.kind, "value") else int(span.kind)
        kind_value = raw + 1

    # Status
    status_dict = {}
    if span.status is not None:
        code = 0
        if span.status.status_code == StatusCode.OK:
            code = 1
        elif span.status.status_code == StatusCode.ERROR:
            code = 2
        status_dict["code"] = code
        if span.status.description:
            status_dict["message"] = span.status.description

    # Events
    events = []
    for event in span.events or []:
        event_dict = {
            "name": event.name,
            "timeUnixNano": str(event.timestamp) if event.timestamp else "0",
        }
        event_attrs = _convert_attributes(event.attributes)
        if event_attrs:
            event_dict["attributes"] = event_attrs
        events.append(event_dict)

    result = {
        "traceId": trace_id,
        "spanId": span_id,
        "name": span.name,
        "kind": kind_value,
        "startTimeUnixNano": start_time_ns,
        "endTimeUnixNano": end_time_ns,
        "attributes": _convert_attributes(span.attributes),
    }

    if parent_span_id:
        result["parentSpanId"] = parent_span_id
    if status_dict:
        result["status"] = status_dict
    if events:
        result["events"] = events

    return result


def _get_resource_key(span: ReadableSpan) -> str:
    """Build a hashable key for grouping spans by resource."""
    resource = getattr(span, "resource", None)
    if not resource or not resource.attributes:
        return ""
    # Sort for deterministic keys
    return json.dumps(dict(sorted(resource.attributes.items())), sort_keys=True, default=str)


def _get_scope_key(span: ReadableSpan) -> str:
    """Build a hashable key for grouping spans by instrumentation scope."""
    scope = getattr(span, "instrumentation_scope", None)
    if not scope:
        return ""
    return f"{scope.name or ''}|{scope.version or ''}"


def _build_otlp_payload(spans: Sequence[ReadableSpan]) -> Dict[str, Any]:
    """
    Group spans by resource and scope, then build OTLP JSON payload.

    Structure: { resourceSpans: [ { resource, scopeSpans: [ { scope, spans } ] } ] }
    """
    # Group: resource_key -> scope_key -> list of span dicts
    resource_groups: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    resource_attrs_map: Dict[str, Any] = {}
    scope_info_map: Dict[str, Any] = {}

    for span in spans:
        r_key = _get_resource_key(span)
        s_key = _get_scope_key(span)

        if r_key not in resource_groups:
            resource_groups[r_key] = {}
            resource = getattr(span, "resource", None)
            resource_attrs_map[r_key] = resource.attributes if resource else {}

        if s_key not in resource_groups[r_key]:
            resource_groups[r_key][s_key] = []
            scope = getattr(span, "instrumentation_scope", None)
            scope_info_map[s_key] = scope

        resource_groups[r_key][s_key].append(_span_to_otlp_json(span))

    # Build OTLP JSON
    resource_spans = []
    for r_key, scope_groups in resource_groups.items():
        scope_spans = []
        for s_key, span_dicts in scope_groups.items():
            scope_entry = {"spans": span_dicts}
            scope = scope_info_map.get(s_key)
            if scope:
                scope_dict = {}
                if scope.name:
                    scope_dict["name"] = scope.name
                if scope.version:
                    scope_dict["version"] = scope.version
                scope_entry["scope"] = scope_dict
            scope_spans.append(scope_entry)

        rs_entry = {"scopeSpans": scope_spans}
        r_attrs = resource_attrs_map.get(r_key, {})
        if r_attrs:
            rs_entry["resource"] = {"attributes": _convert_attributes(r_attrs)}
        resource_spans.append(rs_entry)

    return {"resourceSpans": resource_spans}


class RespanSpanExporter:
    """
    Custom span exporter for Respan that serializes spans as OTLP JSON
    and POSTs them to the /v2/traces endpoint.

    Anti-recursion: Uses OpenTelemetry's suppress_instrumentation context
    to prevent auto-instrumented HTTP libraries (requests, urllib3) from
    creating spans during export. This ensures no infinite trace loops
    even when the ingest endpoint is itself traced.
    """

    def __init__(
        self,
        endpoint: str,
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
    ):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._shutdown = False

        self._headers = {
            "Content-Type": "application/json",
        }
        if headers:
            self._headers.update(headers)
        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"

        self._traces_url = f"{self.endpoint}/v2/traces"
        logger.debug("OTLP JSON traces endpoint: %s", self._traces_url)

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans as OTLP JSON to /v2/traces."""
        if self._shutdown:
            return SpanExportResult.FAILURE

        # Apply root-span promotion logic
        modified_spans: List[ReadableSpan] = []
        for span in spans:
            if should_make_root_span(span):
                logger.debug("Making span a root span: %s", span.name)
                modified_spans.append(ModifiedSpan(span))
            else:
                modified_spans.append(span)

        # Debug preview
        try:
            if logger.isEnabledFor(10):  # logging.DEBUG
                preview = build_spans_export_preview(modified_spans)
                logger.debug("Export preview (sanitized): %s", preview)
        except Exception:
            pass

        # Build OTLP JSON payload
        payload = _build_otlp_payload(modified_spans)

        # Suppress OTel instrumentation during export to prevent recursion.
        # Without this, auto-instrumented `requests` would create spans for
        # the export POST, which would be exported, creating more spans, etc.
        token = attach(set_value(_SUPPRESS_INSTRUMENTATION_KEY, True))
        try:
            response = requests.post(
                url=self._traces_url,
                data=json.dumps(payload, default=str),
                headers=self._headers,
                timeout=self.timeout,
            )
            if response.status_code < 400:
                logger.debug(
                    "Exported %d spans successfully (HTTP %d)",
                    len(modified_spans),
                    response.status_code,
                )
                return SpanExportResult.SUCCESS
            else:
                logger.warning(
                    "Failed to export spans: HTTP %d — %s",
                    response.status_code,
                    response.text[:500],
                )
                return SpanExportResult.FAILURE
        except Exception as e:
            logger.warning("Failed to export spans: %s", e)
            return SpanExportResult.FAILURE
        finally:
            detach(token)

    def shutdown(self):
        """Shutdown the exporter."""
        self._shutdown = True

    def force_flush(self, timeout_millis: int = 30000):
        """Force flush — no-op for HTTP JSON exporter (each export is synchronous)."""
        return True
