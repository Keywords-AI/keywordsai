import os
import logging
from typing import Optional, Set, Dict, Callable, Literal, Union
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter
from .decorators import workflow, task, agent, tool
from .core.tracer import KeywordsAITracer
from .core.client import KeywordsAIClient
from .instruments import Instruments
from .utils.logging import get_main_logger

class KeywordsAITelemetry:
    """
    KeywordsAI Telemetry - Direct OpenTelemetry implementation.
    Replaces Traceloop dependency with native OpenTelemetry components.
    
    Args:
        app_name: Name of the application for telemetry identification
        api_key: KeywordsAI API key (can also be set via KEYWORDSAI_API_KEY env var)
        base_url: KeywordsAI API base URL (can also be set via KEYWORDSAI_BASE_URL env var)
        log_level: Logging level for KeywordsAI tracing (default: "INFO"). 
                  Can be "DEBUG", "INFO", "WARNING", "ERROR", or "CRITICAL".
                  Set to "DEBUG" to see detailed debug messages.
                  Can also be set via KEYWORDSAI_LOG_LEVEL environment variable.
        is_batching_enabled: Whether to enable batch span processing (default: True). 
                            When False, uses synchronous export (no background threads).
                            Useful for debugging or backends with custom exporters.
                            Can also be set via KEYWORDSAI_BATCHING_ENABLED environment variable.
        instruments: Set of instruments to enable (if None, enables default set)
        block_instruments: Set of instruments to explicitly disable
        headers: Additional headers to send with telemetry data
        resource_attributes: Additional resource attributes to attach to all spans
        span_postprocess_callback: Optional callback to process spans before export
        is_enabled: Whether telemetry is enabled (if False, becomes no-op)
        custom_exporter: Optional custom SpanExporter to use instead of the default 
            HTTP OTLP exporter. When provided, api_key and base_url are ignored.
            Useful for internal integrations that need custom export logic.
    
    Note:
        Threading instrumentation is ALWAYS enabled by default (even when specifying custom
        instruments) because it's critical for context propagation. To disable it explicitly:
        block_instruments={Instruments.THREADING}
    """

    def __init__(
        self,
        app_name: str = "keywordsai",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
        is_batching_enabled: Optional[bool] = None,
        instruments: Optional[Set[Instruments]] = None,
        block_instruments: Optional[Set[Instruments]] = None,
        headers: Optional[Dict[str, str]] = None,
        resource_attributes: Optional[Dict[str, str]] = None,
        span_postprocess_callback: Optional[Callable[[ReadableSpan], None]] = None,
        is_enabled: bool = True,
        custom_exporter: Optional[SpanExporter] = None,
    ):
        # Get configuration from environment variables
        api_key = api_key or os.getenv("KEYWORDSAI_API_KEY")
        base_url = base_url or os.getenv(
            "KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"
        )
        # Default to True if not specified
        if is_batching_enabled is None:
            is_batching_enabled = (
                os.getenv("KEYWORDSAI_BATCHING_ENABLED", "True").lower() == "true"
            )
        
        # Get log level from environment variable if not explicitly set
        env_log_level = os.getenv("KEYWORDSAI_LOG_LEVEL")
        if env_log_level and log_level == "INFO":  # Only use env var if user didn't specify
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if env_log_level.upper() in valid_levels:
                log_level = env_log_level.upper()  # type: ignore
        
        # Configure logging level for KeywordsAI tracing
        self._configure_logging(log_level)
        
        # Initialize the tracer
        self.tracer = KeywordsAITracer(
            app_name=app_name,
            api_endpoint=base_url,
            api_key=api_key,
            is_batching_enabled=is_batching_enabled,
            instruments=instruments,
            block_instruments=block_instruments,
            headers=headers,
            resource_attributes=resource_attributes,
            span_postprocess_callback=span_postprocess_callback,
            is_enabled=is_enabled,
            custom_exporter=custom_exporter,
        )
        
        if is_enabled:
            if custom_exporter:
                logging.info(f"KeywordsAI telemetry initialized with custom exporter")
            else:
                logging.info(f"KeywordsAI telemetry initialized, sending to {base_url}")
        else:
            logging.info("KeywordsAI telemetry is disabled")

    def _configure_logging(self, log_level: Union[str, int]):
        """Configure logging level for KeywordsAI tracing"""
        # Get the KeywordsAI logger using the utility function
        keywordsai_logger = get_main_logger()
        
        # Convert string log level to logging constant if needed
        if isinstance(log_level, str):
            log_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Set the log level
        keywordsai_logger.setLevel(log_level)
        
        # Ensure there's a handler if none exists
        if not keywordsai_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            keywordsai_logger.addHandler(handler)
        
        # Prevent duplicate messages from propagating to root logger
        # but allow child loggers to inherit the level
        keywordsai_logger.propagate = False

    def flush(self):
        """Force flush all pending spans"""
        self.tracer.flush()
    
    def is_initialized(self) -> bool:
        """Check if telemetry is initialized"""
        return KeywordsAITracer.is_initialized()

    def get_client(self) -> KeywordsAIClient:
        """
        Get a client for interacting with the current trace/span context.
        
        Returns:
            KeywordsAIClient instance for trace operations.
        """
        return KeywordsAIClient()

    # Expose decorators as instance methods for backward compatibility
    workflow = staticmethod(workflow)
    task = staticmethod(task)
    agent = staticmethod(agent)
    tool = staticmethod(tool)


# Module-level client instance for global access
_global_client: Optional[KeywordsAIClient] = None


def get_client() -> KeywordsAIClient:
    """
    Get a global KeywordsAI client instance.
    
    This function provides access to trace operations without needing to maintain
    a reference to the KeywordsAITelemetry instance. The client uses the singleton
    tracer instance internally.
    
    Returns:
        KeywordsAIClient instance for trace operations.
        
    Example:
        ```python
        from keywordsai_tracing import get_client
        
        client = get_client()
        
        # Get current trace information
        trace_id = client.get_current_trace_id()
        span_id = client.get_current_span_id()
        
        # Update current span
        client.update_current_span(
            keywordsai_params={"trace_group_identifier": "my-group"},
            attributes={"custom.attribute": "value"}
        )
        
        # Add events and handle exceptions
        client.add_event("processing_started")
        try:
            # Your code here
            pass
        except Exception as e:
            client.record_exception(e)
        ```
    """
    global _global_client
    if _global_client is None:
        _global_client = KeywordsAIClient()
    return _global_client



