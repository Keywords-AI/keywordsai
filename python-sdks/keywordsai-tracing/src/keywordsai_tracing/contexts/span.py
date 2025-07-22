from contextlib import contextmanager
import logging
from typing import Any, Dict, Union
from opentelemetry import trace
from opentelemetry.trace.span import Span
from keywordsai_sdk.keywordsai_types.span_types import KEYWORDSAI_SPAN_ATTRIBUTES_MAP, KeywordsAISpanAttributes
from keywordsai_sdk.keywordsai_types.param_types import KeywordsAIParams
from pydantic import ValidationError
from keywordsai_tracing.core.tracer import KeywordsAITracer
from keywordsai_tracing.utils.logging import get_keywordsai_logger


logger = get_keywordsai_logger('contexts.span')

@contextmanager
def keywordsai_span_attributes(keywordsai_params: Union[Dict[str, Any], KeywordsAIParams]):
    """Adds KeywordsAI-specific attributes to the current active span.
    
    Args:
        keywordsai_params: Dictionary of parameters to set as span attributes.
                          Must conform to KeywordsAIParams model structure.
    
    Notes:
        - If no active span is found, a warning will be logged and the context will continue
        - If params validation fails, a warning will be logged and the context will continue
        - If an attribute cannot be set, a warning will be logged and the context will continue
    """
    if not KeywordsAITracer.is_initialized():
        logger.warning("KeywordsAI Telemetry not initialized. Attributes will not be set.")
        yield
        return
        

    current_span = trace.get_current_span()
    
    if not isinstance(current_span, Span):
        logger.warning("No active span found. Attributes will not be set.")
        yield
        return

    try:
        # Keep your original validation
        validated_params = (
            keywordsai_params 
            if isinstance(keywordsai_params, KeywordsAIParams) 
            else KeywordsAIParams.model_validate(keywordsai_params)
        )
        
        for key, value in validated_params.model_dump(mode="json").items():
            if key in KEYWORDSAI_SPAN_ATTRIBUTES_MAP and key != "metadata":
                try:
                    current_span.set_attribute(KEYWORDSAI_SPAN_ATTRIBUTES_MAP[key], value)
                except (ValueError, TypeError) as e:
                    logger.warning(
                        f"Failed to set span attribute {KEYWORDSAI_SPAN_ATTRIBUTES_MAP[key]}={value}: {str(e)}"
                    )
            # Treat metadata as a special case
            if key == "metadata":
                for metadata_key, metadata_value in value.items():
                    current_span.set_attribute(f"{KeywordsAISpanAttributes.KEYWORDSAI_METADATA.value}.{metadata_key}", metadata_value)
        yield
    except ValidationError as e:
        logger.warning(f"Failed to validate params: {str(e.errors(include_url=False))}")
        yield
    except Exception as e:
        logger.exception(f"Unexpected error in span attribute context: {str(e)}")
        raise