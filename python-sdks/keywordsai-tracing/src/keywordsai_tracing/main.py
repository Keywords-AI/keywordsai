import os
from .decorators import workflow, task
from traceloop.sdk import Traceloop
from .contexts.stdio import suppress_stdout
from keywordsai_sdk.utils.debug_print import print_info

class KeywordsAITelemetry:
    """
    KeywordsAITelemetry initializes and manages OpenTelemetry instrumentation for Keywords AI.
    """

    def __init__(
        self, api_key: str = None, base_url: str = None, disable_batch: bool = None
    ):
        self.tracer = Traceloop()
        KEYWORDSAI_API_KEY = os.getenv("KEYWORDSAI_API_KEY")
        KEYWORDSAI_BASE_URL = os.getenv(
            "KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"
        )
        KEYWORDSAI_DISABLE_BATCH = (
            os.getenv("KEYWORDSAI_DISABLE_BATCH", "False")
        ).lower() == "true"
        api_key = api_key or KEYWORDSAI_API_KEY
        base_url = base_url or KEYWORDSAI_BASE_URL
        disable_batch = disable_batch or KEYWORDSAI_DISABLE_BATCH
        self._initialize_telemetry(api_key, base_url, disable_batch)

    def _initialize_telemetry(self, api_key: str, base_url: str, disable_batch: bool):
        """Initialize the Traceloop SDK with Keywords AI configuration"""
        with suppress_stdout():
            self.tracer.init(
                app_name="keywordsai",
                api_endpoint=base_url,
                api_key=api_key,
                disable_batch=disable_batch,
            )
        print_info(f"Sending telemetry to Keywords AI at {base_url}")

    # Expose decorators as instance methods
    workflow = workflow
    task = task
