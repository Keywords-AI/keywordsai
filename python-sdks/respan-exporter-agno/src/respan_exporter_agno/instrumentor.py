"""Keywords AI OpenTelemetry redirect for Agno traces.

This instrumentor wraps OpenTelemetry span processors to intercept Agno spans
and export them to the Keywords AI tracing ingest endpoint.
"""

from __future__ import annotations

import logging
from collections import OrderedDict
from datetime import datetime, timezone
from threading import Lock
from typing import Collection, Dict, Iterable, List, Optional, Sequence

import wrapt
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.sdk.trace.export import SpanExportResult

from .exporter import RespanAgnoExporter

logger = logging.getLogger(__name__)

_instruments = ("agno >= 1.5.2", "openinference-instrumentation-agno >= 0.1.0")

_PATCHED = False


class _SpanDedupeCache:
    def __init__(self, max_size: int = 10000) -> None:
        self._max_size = max_size
        self._data: "OrderedDict[str, None]" = OrderedDict()
        self._lock = Lock()

    def add(self, trace_id: Optional[str], span_id: Optional[str]) -> bool:
        if not trace_id or not span_id:
            return True
        key = f"{trace_id}:{span_id}"
        with self._lock:
            if key in self._data:
                return False
            self._data[key] = None
            if len(self._data) > self._max_size:
                self._data.popitem(last=False)
        return True


_ACTIVE_EXPORTER: Optional[RespanAgnoExporter] = None
_ACTIVE_DEDUPE = _SpanDedupeCache()
_ACTIVE_PASSTHROUGH = False


def _ns_to_datetime(value: Optional[int]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromtimestamp(value / 1e9, tz=timezone.utc)


def _format_trace_id(trace_id: int) -> str:
    return format(trace_id, "032x")


def _format_span_id(span_id: int) -> str:
    return format(span_id, "016x")


def _is_agno_span(span: object) -> bool:
    scope = getattr(span, "instrumentation_scope", None) or getattr(
        span, "instrumentation_library", None
    )
    scope_name = getattr(scope, "name", "") or ""
    if "agno" in scope_name:
        return True
    attributes = getattr(span, "attributes", None) or {}
    if any(key.startswith("agno.") for key in attributes):
        return True
    if "openinference.span.kind" in attributes:
        return True
    if "graph.node.id" in attributes:
        return True
    return False


def _otel_span_to_dict(span: object) -> Dict[str, object]:
    attributes = dict(getattr(span, "attributes", None) or {})
    span_context = getattr(span, "context", None)
    trace_id = _format_trace_id(span_context.trace_id) if span_context else None
    span_id = _format_span_id(span_context.span_id) if span_context else None

    parent = getattr(span, "parent", None)
    parent_id = None
    if parent is not None and getattr(parent, "span_id", None) is not None:
        parent_id = _format_span_id(parent.span_id)

    span_kind = attributes.get("openinference.span.kind")
    if not span_kind:
        raw_kind = getattr(span, "kind", None)
        span_kind = getattr(raw_kind, "name", None) if raw_kind is not None else None
        if span_kind is None and raw_kind is not None:
            span_kind = str(raw_kind)

    status = getattr(span, "status", None)
    status_code = None
    error_message = None
    if status is not None:
        status_enum = getattr(status, "status_code", None)
        status_name = getattr(status_enum, "name", None)
        if status_name == "ERROR":
            status_code = 500
            error_message = getattr(status, "description", None) or "error"
        elif status_name == "OK":
            status_code = 200

    span_path = attributes.get("graph.node.id")

    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_id": parent_id,
        "name": getattr(span, "name", None),
        "span_type": span_kind,
        "kind": span_kind,
        "span_path": span_path,
        "start_time": _ns_to_datetime(getattr(span, "start_time", None)),
        "end_time": _ns_to_datetime(getattr(span, "end_time", None)),
        "attributes": attributes,
        "status_code": status_code,
        "error": error_message,
    }


def _group_spans_by_trace(spans: Sequence[Dict[str, object]]) -> Dict[str, List[Dict[str, object]]]:
    grouped: Dict[str, List[Dict[str, object]]] = {}
    for span in spans:
        trace_id = span.get("trace_id")
        if not isinstance(trace_id, str) or not trace_id:
            continue
        grouped.setdefault(trace_id, []).append(span)
    return grouped


class RespanAgnoInstrumentor(BaseInstrumentor):
    """Instrument OpenTelemetry exporters to send Agno traces to Keywords AI."""

    def __init__(self) -> None:
        super().__init__()
        self._exporter: Optional[RespanAgnoExporter] = None
        self._passthrough = False
        self._dedupe = _SpanDedupeCache()

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs) -> None:
        self._exporter = RespanAgnoExporter(
            api_key=kwargs.get("api_key"),
            endpoint=kwargs.get("endpoint"),
            base_url=kwargs.get("base_url"),
            environment=kwargs.get("environment"),
            customer_identifier=kwargs.get("customer_identifier"),
            timeout=kwargs.get("timeout", 10),
        )
        self._passthrough = bool(kwargs.get("passthrough", False))
        self._dedupe = _SpanDedupeCache(max_size=kwargs.get("dedupe_max_size", 10000))

        global _ACTIVE_EXPORTER, _ACTIVE_DEDUPE, _ACTIVE_PASSTHROUGH
        _ACTIVE_EXPORTER = self._exporter
        _ACTIVE_DEDUPE = self._dedupe
        _ACTIVE_PASSTHROUGH = self._passthrough

        self._patch_span_processors()
        logger.info("Keywords AI Agno instrumentation enabled")

    def _uninstrument(self, **kwargs) -> None:
        logger.info("Keywords AI Agno instrumentation disabled")

    def _patch_span_processors(self) -> None:
        global _PATCHED
        if _PATCHED:
            return

        def export_agno_spans(spans: Iterable[object]) -> SpanExportResult:
            exporter = _ACTIVE_EXPORTER
            dedupe = _ACTIVE_DEDUPE
            if exporter is None:
                return SpanExportResult.SUCCESS

            agno_span_dicts: List[Dict[str, object]] = []
            for span in spans:
                if not _is_agno_span(span):
                    continue
                span_dict = _otel_span_to_dict(span)
                if not dedupe.add(
                    span_dict.get("trace_id"),
                    span_dict.get("span_id"),
                ):
                    continue
                agno_span_dicts.append(span_dict)

            if not agno_span_dicts:
                return SpanExportResult.SUCCESS

            payloads: List[Dict[str, object]] = []
            grouped = _group_spans_by_trace(agno_span_dicts)
            for trace_spans in grouped.values():
                payloads.extend(exporter.build_payload(trace_spans))

            if not payloads:
                return SpanExportResult.SUCCESS

            if not exporter.api_key:
                logger.warning("Keywords AI API key is not set; skipping Agno export")
                return SpanExportResult.SUCCESS

            exporter._send(payloads)
            return SpanExportResult.SUCCESS

        def batch_export_wrapper(wrapped, instance, args, kwargs):
            spans = list(args[0]) if args else list(kwargs.get("spans", []))
            if not spans:
                return wrapped(*args, **kwargs)

            agno_spans = []
            other_spans = []
            for span in spans:
                if _is_agno_span(span):
                    agno_spans.append(span)
                else:
                    other_spans.append(span)

            if not agno_spans:
                return wrapped(*args, **kwargs)

            try:
                export_result = export_agno_spans(agno_spans)
            except Exception as exc:
                logger.warning("Failed to export Agno spans: %s", exc, exc_info=True)
                export_result = SpanExportResult.FAILURE

            if _ACTIVE_PASSTHROUGH:
                return wrapped(*args, **kwargs)

            if other_spans:
                return wrapped(other_spans, **kwargs)

            return export_result

        def on_end_wrapper(wrapped, instance, args, kwargs):
            span = args[0] if args else kwargs.get("span")
            if span is None or not _is_agno_span(span):
                return wrapped(*args, **kwargs)

            try:
                export_agno_spans([span])
            except Exception as exc:
                logger.warning("Failed to export Agno span: %s", exc, exc_info=True)

            if _ACTIVE_PASSTHROUGH:
                return wrapped(*args, **kwargs)
            return None

        try:
            from opentelemetry.sdk.trace import export as trace_export

            if hasattr(trace_export.BatchSpanProcessor, "_export"):
                wrapt.wrap_function_wrapper(
                    module="opentelemetry.sdk.trace.export",
                    name="BatchSpanProcessor._export",
                    wrapper=batch_export_wrapper,
                )
            else:
                wrapt.wrap_function_wrapper(
                    module="opentelemetry.sdk.trace.export",
                    name="BatchSpanProcessor.on_end",
                    wrapper=on_end_wrapper,
                )
        except Exception as exc:
            logger.debug("Failed to patch BatchSpanProcessor: %s", exc)

        wrapt.wrap_function_wrapper(
            module="opentelemetry.sdk.trace.export",
            name="SimpleSpanProcessor.on_end",
            wrapper=on_end_wrapper,
        )

        _PATCHED = True
        logger.debug("Patched OpenTelemetry span processors for Agno export")
