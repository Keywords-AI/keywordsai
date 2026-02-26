"""Respan Logger for sending trace data to the API."""

import random
import time
from typing import Any, Dict, List, Optional

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
            max_retries: Number of retries on 5xx or transient errors (default 3)
            base_delay: Base delay in seconds for exponential backoff
            max_delay: Maximum delay in seconds between retries
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
        Retries on 5xx and transient errors with exponential backoff.

        Args:
            spans: List of span data (each span represents a component in the pipeline)

        Returns:
            Response from the API if successful, None otherwise
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            RESPAN_DOGFOOD_HEADER: "1",
        }
        delay = self.base_delay
        last_exc = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(
                    "Sending %s spans to Respan (attempt %s/%s)",
                    len(spans),
                    attempt,
                    self.max_retries,
                )
                response = requests.post(
                    url=self.traces_endpoint,
                    headers=headers,
                    json=spans,
                    timeout=10,
                )

                if response.status_code in (200, 201):
                    logger.debug("Successfully sent trace to Respan")
                    return response.json()

                if 400 <= response.status_code < 500:
                    logger.warning(
                        "Respan client error %s: %s",
                        response.status_code,
                        response.text,
                    )
                    return None

                last_exc = None
                logger.warning(
                    "Respan server error %s, retrying (%s/%s)",
                    response.status_code,
                    attempt,
                    self.max_retries,
                )
            except requests.exceptions.Timeout as e:
                last_exc = e
                logger.warning(
                    "Request to Respan timed out, retrying (%s/%s)",
                    attempt,
                    self.max_retries,
                )
            except requests.exceptions.RequestException as e:
                last_exc = e
                logger.warning(
                    "Request to Respan failed: %s, retrying (%s/%s)",
                    e,
                    attempt,
                    self.max_retries,
                )

            if attempt < self.max_retries:
                sleep_time = delay + random.uniform(0, 0.1 * delay)
                time.sleep(sleep_time)
                delay = min(delay * 2, self.max_delay)

        if last_exc:
            logger.warning("Error sending trace to Respan after %s attempts: %s", self.max_retries, last_exc)
        else:
            logger.warning(
                "Failed to send trace to Respan after %s attempts (server errors)",
                self.max_retries,
            )
        return None
