import logging
from typing import Any, Dict, Optional, Union
from opentelemetry import trace, context as context_api
from opentelemetry.trace.span import Span
from opentelemetry.trace import Status, StatusCode

from keywordsai_sdk.keywordsai_types.span_types import KEYWORDSAI_SPAN_ATTRIBUTES_MAP, KeywordsAISpanAttributes
from keywordsai_sdk.keywordsai_types.param_types import KeywordsAIParams
from pydantic import ValidationError

from .tracer import KeywordsAITracer
from ..utils.logging import get_keywordsai_logger


logger = get_keywordsai_logger('core.client')


class KeywordsAIClient:
    """
    Client for interacting with the current trace/span context.
    Provides a clean API for getting and updating trace information.
    """
    
    def __init__(self):
        """Initialize the client. Uses the singleton tracer instance."""
        self._tracer = KeywordsAITracer()
    
    def get_current_span(self) -> Optional[Span]:
        """
        Get the current active span.
        
        Returns:
            The current active span, or None if no span is active.
        """
        if not self._tracer.enabled or not KeywordsAITracer.is_initialized():
            logger.warning("KeywordsAI Telemetry not initialized or disabled.")
            return None
            
        current_span = trace.get_current_span()
        
        if not isinstance(current_span, Span):
            return None
            
        return current_span
    
    def get_current_trace_id(self) -> Optional[str]:
        """
        Get the current trace ID.
        
        Returns:
            The current trace ID as a string, or None if no active span.
        """
        span = self.get_current_span()
        if span:
            return format(span.get_span_context().trace_id, '032x')
        return None
    
    def get_current_span_id(self) -> Optional[str]:
        """
        Get the current span ID.
        
        Returns:
            The current span ID as a string, or None if no active span.
        """
        span = self.get_current_span()
        if span:
            return format(span.get_span_context().span_id, '016x')
        return None
    
    def update_current_span(
        self, 
        keywordsai_params: Optional[Union[Dict[str, Any], KeywordsAIParams]] = None,
        attributes: Optional[Dict[str, Any]] = None,
        status: Optional[Union[Status, StatusCode]] = None,
        status_description: Optional[str] = None,
        name: Optional[str] = None
    ) -> bool:
        """
        Update the current active span with new information.
        
        Args:
            keywordsai_params: KeywordsAI-specific parameters to set as span attributes
            attributes: Generic attributes to set on the span
            status: Status to set on the span (Status object or StatusCode)
            status_description: Description for the status
            name: New name for the span
            
        Returns:
            True if the span was updated successfully, False otherwise.
        """
        span = self.get_current_span()
        if not span:
            logger.warning("No active span found. Cannot update span.")
            return False
        
        try:
            # Update span name if provided
            if name:
                span.update_name(name)
            
            # Set KeywordsAI-specific attributes
            if keywordsai_params:
                self._set_keywordsai_attributes(span, keywordsai_params)
            
            # Set generic attributes
            if attributes:
                for key, value in attributes.items():
                    try:
                        span.set_attribute(key, value)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Failed to set attribute {key}={value}: {str(e)}")
            
            # Set status
            if status is not None:
                if isinstance(status, StatusCode):
                    span.set_status(Status(status, status_description))
                else:
                    span.set_status(status)
            
            return True
            
        except Exception as e:
            logger.exception(f"Failed to update span: {str(e)}")
            return False
    
    def _set_keywordsai_attributes(
        self, 
        span: Span, 
        keywordsai_params: Union[Dict[str, Any], KeywordsAIParams]
    ):
        """Set KeywordsAI-specific attributes on a span."""
        try:
            # Validate parameters
            validated_params = (
                keywordsai_params 
                if isinstance(keywordsai_params, KeywordsAIParams) 
                else KeywordsAIParams.model_validate(keywordsai_params)
            )
            
            # Set attributes based on the mapping
            for key, value in validated_params.model_dump(mode="json").items():
                if key in KEYWORDSAI_SPAN_ATTRIBUTES_MAP and key != "metadata":
                    try:
                        span.set_attribute(KEYWORDSAI_SPAN_ATTRIBUTES_MAP[key], value)
                    except (ValueError, TypeError) as e:
                        logger.warning(
                            f"Failed to set span attribute {KEYWORDSAI_SPAN_ATTRIBUTES_MAP[key]}={value}: {str(e)}"
                        )
                
                # Handle metadata specially
                if key == "metadata" and isinstance(value, dict):
                    for metadata_key, metadata_value in value.items():
                        try:
                            span.set_attribute(
                                f"{KeywordsAISpanAttributes.KEYWORDSAI_METADATA.value}.{metadata_key}", 
                                metadata_value
                            )
                        except (ValueError, TypeError) as e:
                            logger.warning(
                                f"Failed to set metadata attribute {metadata_key}={metadata_value}: {str(e)}"
                            )
                            
        except ValidationError as e:
            logger.warning(f"Failed to validate KeywordsAI params: {str(e.errors(include_url=False))}")
        except Exception as e:
            logger.exception(f"Unexpected error setting KeywordsAI attributes: {str(e)}")
    
    def add_event(
        self, 
        name: str, 
        attributes: Optional[Dict[str, Any]] = None,
        timestamp: Optional[int] = None
    ) -> bool:
        """
        Add an event to the current span.
        
        Args:
            name: Name of the event
            attributes: Optional attributes for the event
            timestamp: Optional timestamp (nanoseconds since epoch)
            
        Returns:
            True if the event was added successfully, False otherwise.
        """
        span = self.get_current_span()
        if not span:
            logger.warning("No active span found. Cannot add event.")
            return False
        
        try:
            span.add_event(name, attributes or {}, timestamp)
            return True
        except Exception as e:
            logger.exception(f"Failed to add event {name}: {str(e)}")
            return False
    
    def record_exception(
        self, 
        exception: Exception,
        attributes: Optional[Dict[str, Any]] = None,
        timestamp: Optional[int] = None,
        escaped: bool = False
    ) -> bool:
        """
        Record an exception on the current span.
        
        Args:
            exception: The exception to record
            attributes: Optional attributes for the exception
            timestamp: Optional timestamp (nanoseconds since epoch)
            escaped: Whether the exception escaped the span
            
        Returns:
            True if the exception was recorded successfully, False otherwise.
        """
        span = self.get_current_span()
        if not span:
            logger.warning("No active span found. Cannot record exception.")
            return False
        
        try:
            span.record_exception(exception, attributes, timestamp, escaped)
            # Also set the span status to error
            span.set_status(Status(StatusCode.ERROR, str(exception)))
            return True
        except Exception as e:
            logger.exception(f"Failed to record exception: {str(e)}")
            return False
    
    def get_context_value(self, key: str) -> Any:
        """
        Get a value from the current OpenTelemetry context.
        
        Args:
            key: The context key to retrieve
            
        Returns:
            The context value, or None if not found.
        """
        return context_api.get_value(key)
    
    def set_context_value(self, key: str, value: Any) -> bool:
        """
        Set a value in the current OpenTelemetry context.
        
        Args:
            key: The context key to set
            value: The value to set
            
        Returns:
            True if the context was updated successfully, False otherwise.
        """
        try:
            context_api.attach(context_api.set_value(key, value))
            return True
        except Exception as e:
            logger.exception(f"Failed to set context value {key}={value}: {str(e)}")
            return False
    
    def is_recording(self) -> bool:
        """
        Check if the current span is recording.
        
        Returns:
            True if the current span is recording, False otherwise.
        """
        span = self.get_current_span()
        return span.is_recording() if span else False
    
    def flush(self):
        """Force flush all pending spans."""
        self._tracer.flush() 