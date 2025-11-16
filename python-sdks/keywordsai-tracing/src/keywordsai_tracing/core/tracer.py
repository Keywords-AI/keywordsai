import atexit
import logging
import os
from typing import Dict, Optional, Set, Callable
from threading import Lock

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider, ReadableSpan
from opentelemetry.sdk.trace.export import (
    SpanExporter,
    SimpleSpanProcessor,
    BatchSpanProcessor,
)
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.textmap import TextMapPropagator

from .processor import KeywordsAISpanProcessor, BufferingSpanProcessor
from .exporter import KeywordsAISpanExporter
from ..instruments import Instruments
from ..utils.notebook import is_notebook
from ..utils.instrumentation import init_instrumentations
from ..constants.tracing import TRACER_NAME

class KeywordsAITracer:
    """
    Direct OpenTelemetry implementation for KeywordsAI tracing.
    Replaces Traceloop dependency with native OpenTelemetry components.
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure only one tracer instance exists"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        app_name: str = "keywordsai",
        api_endpoint: str = "https://api.keywordsai.co/api",
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        is_batching_enabled: bool = True,
        resource_attributes: Optional[Dict[str, str]] = None,
        instruments: Optional[Set[Instruments]] = None,
        block_instruments: Optional[Set[Instruments]] = None,
        propagator: Optional[TextMapPropagator] = None,
        span_postprocess_callback: Optional[Callable[[ReadableSpan], None]] = None,
        is_enabled: bool = True,
        custom_exporter: Optional[SpanExporter] = None,
    ):
        # Prevent re-initialization
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.is_enabled = is_enabled
        
        if not is_enabled:
            logging.info("KeywordsAI tracing is disabled")
            return
            
        # Setup resource attributes
        resource_attributes = resource_attributes or {}
        resource_attributes[SERVICE_NAME] = app_name
        
        # Initialize OpenTelemetry components
        self._setup_tracer_provider(resource_attributes)
        self._setup_span_processor(
            api_endpoint, api_key, headers, is_batching_enabled, span_postprocess_callback, custom_exporter
        )
        self._setup_propagation(propagator)
        self._setup_instrumentations(instruments, block_instruments)
        
        # Register cleanup
        atexit.register(self._cleanup)
        
        if custom_exporter:
            logging.info(f"KeywordsAI tracing initialized with custom exporter")
        else:
            logging.info(f"KeywordsAI tracing initialized, sending to {api_endpoint}")
    
    def _setup_tracer_provider(self, resource_attributes: Dict[str, str]):
        """Initialize the OpenTelemetry TracerProvider"""
        resource = Resource(attributes=resource_attributes)
        self.tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(self.tracer_provider)
    
    def _setup_span_processor(
        self,
        api_endpoint: str,
        api_key: Optional[str],
        headers: Optional[Dict[str, str]],
        is_batching_enabled: bool,
        span_postprocess_callback: Optional[Callable[[ReadableSpan], None]],
        custom_exporter: Optional[SpanExporter] = None,
    ):
        """Setup span processor with KeywordsAI exporter or custom exporter"""
        # Create exporter
        if custom_exporter:
            # Use provided custom exporter
            exporter = custom_exporter
        else:
            # Default: use HTTP OTLP exporter
            exporter = KeywordsAISpanExporter(
                endpoint=api_endpoint,
                api_key=api_key,
                headers=headers or {},
            )
        
        # Store exporter reference for SpanCollector access
        self.exporter = exporter
        
        # Choose processor type based on environment
        if not is_batching_enabled or is_notebook():
            processor = SimpleSpanProcessor(exporter)
        else:
            processor = BatchSpanProcessor(exporter)
        
        # Wrap with custom processor for metadata injection
        keywordsai_processor = KeywordsAISpanProcessor(
            processor, span_postprocess_callback
        )
        
        # Wrap with BufferingSpanProcessor to enable SpanBuffer functionality
        # This processor checks context variables to route spans to buffers when active
        self.span_processor = BufferingSpanProcessor(keywordsai_processor)
        
        self.tracer_provider.add_span_processor(self.span_processor)
    
    def _setup_propagation(self, propagator: Optional[TextMapPropagator]):
        """Setup context propagation"""
        if propagator:
            set_global_textmap(propagator)
    
    def _setup_instrumentations(
        self,
        instruments: Optional[Set[Instruments]],
        block_instruments: Optional[Set[Instruments]],
    ):
        """Initialize library instrumentations (including threading)"""
        init_instrumentations(instruments, block_instruments)
    
    def get_tracer(self, name: str = TRACER_NAME):
        """Get OpenTelemetry tracer instance"""
        if not self.is_enabled:
            return trace.NoOpTracer()
        return self.tracer_provider.get_tracer(name)
    
    def flush(self):
        """Force flush all pending spans"""
        if hasattr(self, 'span_processor'):
            self.span_processor.force_flush()
    
    def _cleanup(self):
        """Cleanup resources on exit"""
        self.flush()
        if hasattr(self, 'span_processor'):
            self.span_processor.shutdown()
    
    @classmethod
    def is_initialized(cls) -> bool:
        """Check if tracer is initialized"""
        return cls._instance is not None and hasattr(cls._instance, '_initialized') 