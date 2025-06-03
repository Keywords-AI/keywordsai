import os
import logging
from typing import Optional, Set, Dict, Callable
from opentelemetry.sdk.trace import ReadableSpan

from .decorators import workflow, task, agent, tool
from .core.tracer import KeywordsAITracer
from .instruments import Instruments
from .contexts.stdio import suppress_stdout


class KeywordsAITelemetry:
    """
    KeywordsAI Telemetry - Direct OpenTelemetry implementation.
    Replaces Traceloop dependency with native OpenTelemetry components.
    """

    def __init__(
        self,
        app_name: str = "keywordsai",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        disable_batch: Optional[bool] = None,
        instruments: Optional[Set[Instruments]] = None,
        block_instruments: Optional[Set[Instruments]] = None,
        headers: Optional[Dict[str, str]] = None,
        resource_attributes: Optional[Dict[str, str]] = None,
        span_postprocess_callback: Optional[Callable[[ReadableSpan], None]] = None,
        enabled: bool = True,
    ):
        # Get configuration from environment variables
        api_key = api_key or os.getenv("KEYWORDSAI_API_KEY")
        base_url = base_url or os.getenv(
            "KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"
        )
        disable_batch = disable_batch or (
            os.getenv("KEYWORDSAI_DISABLE_BATCH", "False").lower() == "true"
        )
        
        # Set default blocked instruments
        if block_instruments is None:
            block_instruments = {Instruments.REDIS, Instruments.REQUESTS}
        
        # Initialize the tracer
        with suppress_stdout():
            self.tracer = KeywordsAITracer(
                app_name=app_name,
                api_endpoint=base_url,
                api_key=api_key,
                disable_batch=disable_batch,
                instruments=instruments,
                block_instruments=block_instruments,
                headers=headers,
                resource_attributes=resource_attributes,
                span_postprocess_callback=span_postprocess_callback,
                enabled=enabled,
            )
        
        if enabled:
            logging.info(f"KeywordsAI telemetry initialized, sending to {base_url}")
        else:
            logging.info("KeywordsAI telemetry is disabled")

    def flush(self):
        """Force flush all pending spans"""
        self.tracer.flush()
    
    def is_initialized(self) -> bool:
        """Check if telemetry is initialized"""
        return KeywordsAITracer.is_initialized()

    # Expose decorators as instance methods for backward compatibility
    workflow = staticmethod(workflow)
    task = staticmethod(task)
    agent = staticmethod(agent)
    tool = staticmethod(tool)
