import json
import inspect
from functools import wraps
from typing import Optional, TypeVar, Callable, Any, ParamSpec, Awaitable
from opentelemetry import trace, context as context_api
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.semconv_ai import TraceloopSpanKindValues, SpanAttributes
from keywordsai_sdk.constants.llm_logging import (
    LogMethodChoices
)
from keywordsai_sdk.keywordsai_types.span_types import KeywordsAISpanAttributes
from keywordsai_tracing.core.tracer import KeywordsAITracer
from keywordsai_tracing.constants.context_constants import (
    WORKFLOW_NAME_KEY, 
    ENTITY_PATH_KEY,
    ENABLE_CONTENT_TRACING_KEY
)


P = ParamSpec("P")
R = TypeVar("R")
F = TypeVar("F", bound=Callable[P, R | Awaitable[R]])


def _is_json_size_valid(json_str: str) -> bool:
    """Check if JSON string size is less than 1MB"""
    return len(json_str) < 1_000_000


def _should_send_prompts() -> bool:
    """Check if we should send prompt content in traces"""
    return context_api.get_value(ENABLE_CONTENT_TRACING_KEY) is not False


def _is_async_method(fn):
    """Check if function is async or async generator"""
    return inspect.iscoroutinefunction(fn) or inspect.isasyncgenfunction(fn)


def _setup_span(entity_name: str, span_kind: str, version: Optional[int] = None):
    """Setup OpenTelemetry span and context"""
    # Ensure span_kind is a string
    span_kind_str = span_kind.value if hasattr(span_kind, "value") else str(span_kind)
    entity_path = context_api.get_value(SpanAttributes.TRACELOOP_ENTITY_PATH) or ""

    # Set workflow name for workflow spans
    if span_kind_str in [
        TraceloopSpanKindValues.WORKFLOW.value,
        TraceloopSpanKindValues.AGENT.value,
    ]:
        context_api.attach(
            context_api.set_value(SpanAttributes.TRACELOOP_ENTITY_NAME, entity_name)
        )

    # Set entity path for task spans
    if span_kind_str in [
        TraceloopSpanKindValues.TASK.value,
        TraceloopSpanKindValues.TOOL.value,
    ]:
        entity_path = f"{entity_path}.{entity_name}" if entity_path else entity_name
        context_api.attach(context_api.set_value(SpanAttributes.TRACELOOP_ENTITY_PATH, entity_path))

    # Get tracer and start span
    tracer = KeywordsAITracer().get_tracer()
    span_name = f"{entity_name}.{span_kind_str}"
    span = tracer.start_span(span_name)

    # Set span attributes
    span.set_attribute(SpanAttributes.TRACELOOP_SPAN_KIND, span_kind_str)
    span.set_attribute(SpanAttributes.TRACELOOP_ENTITY_NAME, entity_name)
    span.set_attribute(SpanAttributes.TRACELOOP_ENTITY_PATH, entity_path)
    span.set_attribute(
        KeywordsAISpanAttributes.LOG_METHOD.value, LogMethodChoices.PYTHON_TRACING.value
    )
    if version:
        span.set_attribute(SpanAttributes.TRACELOOP_ENTITY_VERSION, version)

    # Set span in context
    ctx = trace.set_span_in_context(span)
    ctx_token = context_api.attach(ctx)

    return span, ctx_token


def _handle_span_input(span, args, kwargs):
    """Handle entity input logging"""
    try:
        if _should_send_prompts():
            json_input = json.dumps({"args": list(args), "kwargs": kwargs})
            if _is_json_size_valid(json_input):
                span.set_attribute(SpanAttributes.TRACELOOP_ENTITY_INPUT, json_input)
    except (TypeError, ValueError) as e:
        # Skip if serialization fails
        pass

def _handle_span_output(span, result):
    """Handle entity output logging"""
    try:
        if _should_send_prompts():
            json_output = json.dumps(result)
            if _is_json_size_valid(json_output):
                span.set_attribute(SpanAttributes.TRACELOOP_ENTITY_OUTPUT, json_output)
    except (TypeError, ValueError) as e:
        # Skip if serialization fails
        pass


def _cleanup_span(span, ctx_token):
    """End span and detach context"""
    span.end()
    context_api.detach(ctx_token)


def _handle_generator(span, ctx_token, generator):
    """Handle generator functions"""
    try:
        for item in generator:
            yield item
    except Exception as e:
        span.set_status(Status(StatusCode.ERROR, str(e)))
        span.record_exception(e)
        raise
    finally:
        _cleanup_span(span, ctx_token)


async def _ahandle_generator(span, ctx_token, async_generator):
    """Handle async generator functions"""
    try:
        async for item in async_generator:
            yield item
    except Exception as e:
        span.set_status(Status(StatusCode.ERROR, str(e)))
        span.record_exception(e)
        raise
    finally:
        _cleanup_span(span, ctx_token)


def _create_entity_method(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    span_kind: str = "task",
) -> Callable[[F], F]:
    """Create entity decorator for methods or classes"""

    if method_name is not None:
        # Class decorator
        return _create_entity_class(name, version, method_name, span_kind)
    else:
        # Method decorator
        return _create_entity_method_decorator(name, version, span_kind)


def _create_entity_method_decorator(
    name: Optional[str] = None,
    version: Optional[int] = None,
    span_kind: str = "task",
) -> Callable[[F], F]:
    """Create method decorator"""

    def decorator(fn: F) -> F:
        entity_name = name or fn.__name__

        if _is_async_method(fn):
            if inspect.isasyncgenfunction(fn):
                # Async generator
                @wraps(fn)
                async def async_gen_wrapper(*args: Any, **kwargs: Any) -> Any:
                    span, ctx_token = _setup_span(entity_name, span_kind, version)
                    _handle_span_input(span, args, kwargs)

                    try:
                        result = fn(*args, **kwargs)
                        async for item in _ahandle_generator(span, ctx_token, result):
                            yield item
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        _cleanup_span(span, ctx_token)
                        raise

                return async_gen_wrapper
            else:
                # Regular async function
                @wraps(fn)
                async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                    span, ctx_token = _setup_span(entity_name, span_kind, version)
                    _handle_span_input(span, args, kwargs)

                    try:
                        result = await fn(*args, **kwargs)
                        _handle_span_output(span, result)
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise
                    finally:
                        _cleanup_span(span, ctx_token)

                return async_wrapper
        else:
            # Sync function
            @wraps(fn)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                span, ctx_token = _setup_span(entity_name, span_kind, version)
                _handle_span_input(span, args, kwargs)

                try:
                    result = fn(*args, **kwargs)

                    # Handle generators
                    if inspect.isgeneratorfunction(fn):
                        return _handle_generator(span, ctx_token, result)
                    else:
                        _handle_span_output(span, result)
                        return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
                finally:
                    if not inspect.isgeneratorfunction(fn):
                        _cleanup_span(span, ctx_token)

            return sync_wrapper

    return decorator


def _create_entity_class(
    name: Optional[str],
    version: Optional[int],
    method_name: str,
    span_kind: str = "task",
):
    """Create class decorator"""

    def decorator(cls):
        entity_name = name or cls.__name__

        # Get the original method
        original_method = getattr(cls, method_name)

        # Create decorated method
        decorated_method = _create_entity_method_decorator(
            entity_name, version, span_kind
        )(original_method)

        # Replace the method
        setattr(cls, method_name, decorated_method)

        return cls

    return decorator
