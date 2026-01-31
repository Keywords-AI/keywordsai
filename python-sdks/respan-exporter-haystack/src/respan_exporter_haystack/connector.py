"""Keywords AI Connector component for Haystack pipelines."""

import os
from typing import Optional, Dict, Any
from haystack import component, default_from_dict, default_to_dict, logging

from .tracer import RespanTracer

logger = logging.getLogger(__name__)


@component
class RespanConnector:
    """
    A connector component that enables Keywords AI tracing and logging for Haystack pipelines.
    
    This component can be added to any Haystack pipeline to automatically capture execution
    traces and send them to Keywords AI for monitoring, debugging, and analysis.
    
    The component supports two modes:
    - "tracing": Uses Haystack's content tracing system (default, requires HAYSTACK_CONTENT_TRACING_ENABLED=true)
    - "gateway": Direct logging mode without content tracing
    
    Example usage:
        ```python
        from haystack import Pipeline
        from respan_exporter_haystack import RespanConnector
        
        pipeline = Pipeline()
        pipeline.add_component("tracer", RespanConnector("My Pipeline"))
        # Add other components and connections...
        
        response = pipeline.run(data={...})
        print(response["tracer"]["trace_url"])
        ```
    
    Args:
        name: Name of the pipeline/trace for identification in Keywords AI dashboard
        mode: Either "tracing" (default) or "gateway" for different logging modes
        api_key: Keywords AI API key (defaults to RESPAN_API_KEY env var)
        base_url: Keywords AI API base URL (defaults to RESPAN_BASE_URL env var)
        metadata: Additional metadata to attach to all traces/logs
    """

    def __init__(
        self,
        name: str,
        mode: str = "tracing",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the Keywords AI connector."""
        self.name = name
        self.mode = mode
        self.api_key = api_key or os.getenv("RESPAN_API_KEY")
        self.base_url = base_url or os.getenv(
            "RESPAN_BASE_URL", "https://api.respan.ai/api"
        )
        self.metadata = metadata or {}
        
        if not self.api_key:
            raise ValueError(
                "Keywords AI API key is required. Set RESPAN_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Initialize the tracer
        self.tracer = RespanTracer(
            name=self.name,
            api_key=self.api_key,
            base_url=self.base_url,
            metadata=self.metadata,
        )
        
        # Enable content tracing if in tracing mode
        if self.mode == "tracing":
            if not os.getenv("HAYSTACK_CONTENT_TRACING_ENABLED"):
                logger.warning(
                    "HAYSTACK_CONTENT_TRACING_ENABLED is not set. "
                    "Set it to 'true' to enable full tracing capabilities."
                )
            # Register the tracer with Haystack's content tracing system
            try:
                from haystack import tracing
                tracing.tracer.actual_tracer = self.tracer
                logger.info(f"Keywords AI tracer registered for '{self.name}'")
            except Exception as e:
                logger.warning(f"Could not register tracer: {e}")

    @component.output_types(name=str, trace_url=Optional[str])
    def run(self) -> Dict[str, Any]:
        """
        Run method for the connector component.
        
        NOTE: The trace is automatically sent when the pipeline completes.
        This method just returns the trace info.
        
        Returns:
            Dictionary containing:
                - name: The pipeline/trace name
                - trace_url: URL to view the trace in Keywords AI dashboard (if available)
        """
        # Don't send here - it will be sent automatically when the root span finishes
        # Just return the trace info
        return {
            "name": self.name,
            "trace_url": self.tracer.get_trace_url(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize component to dictionary."""
        return default_to_dict(
            self,
            name=self.name,
            mode=self.mode,
            api_key=self.api_key,
            base_url=self.base_url,
            metadata=self.metadata,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RespanConnector":
        """Deserialize component from dictionary."""
        return default_from_dict(cls, data)
