"""Respan Logger for sending trace data to the API."""

import requests
from haystack import logging

from respan_sdk.constants import RESPAN_DOGFOOD_HEADER, resolve_tracing_ingest_endpoint

logger = logging.getLogger(__name__)

DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0
DEFAULT_MAX_DELAY = 30.0


class RespanLogger:
    """
    Logger class for sending trace and log data to Respan API.

    This class handles the HTTP communication with Respan's logging endpoints.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.respan.ai",
        max_retries: int = DEFAULT_MAX_RETRIES,
        base_delay: float = DEFAULT_BASE_DELAY,
        max_delay: float = DEFAULT_MAX_DELAY,
    ):
        """
        Initialize the logger.

        Args:
            api_key: Respan API key
            base_url: Base URL for the Respan API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.traces_endpoint = resolve_tracing_ingest_endpoint(base_url=self.base_url)
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def send_trace(self, spans: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Send a batch of spans to construct a trace in Respan.
        
        Args:
            spans: List of span data (each span represents a component in the pipeline)

        Returns:
            Response from the API if successful, None otherwise
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            logger.debug(f"Sending {len(spans)} spans to Respan")
            
            response = requests.post(
                url=self.traces_endpoint,
                headers=headers,
                json=spans,
                timeout=10,
            )
            
            if response.status_code in [200, 201]:
                logger.debug("Successfully sent trace to Respan")
                return response.json()
            else:
                logger.warning(
                    f"Failed to send trace to Respan: {response.status_code} - {response.text}"
                )
                return None
                
        except requests.exceptions.Timeout:
            logger.warning("Request to Respan timed out")
            return None
        except Exception as e:
            logger.warning(f"Error sending trace to Respan: {e}")
            return None
