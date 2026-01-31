"""Keywords AI Logger for sending trace data to the API."""

import requests
from typing import Any, Dict, Optional, List
from haystack import logging

logger = logging.getLogger(__name__)


class RespanLogger:
    """
    Logger class for sending trace and log data to Keywords AI API.
    
    This class handles the HTTP communication with Keywords AI's logging endpoints.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.respan.ai"):
        """
        Initialize the logger.
        
        Args:
            api_key: Keywords AI API key
            base_url: Base URL for the Keywords AI API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.traces_endpoint = f"{self.base_url}/v1/traces/ingest"

    def send_trace(self, spans: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Send a batch of spans to construct a trace in Keywords AI.
        
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
            
            logger.debug(f"Sending {len(spans)} spans to Keywords AI")
            
            response = requests.post(
                url=self.traces_endpoint,
                headers=headers,
                json=spans,
                timeout=10,
            )
            
            if response.status_code in [200, 201]:
                logger.debug("Successfully sent trace to Keywords AI")
                return response.json()
            else:
                logger.warning(
                    f"Failed to send trace to Keywords AI: {response.status_code} - {response.text}"
                )
                return None
                
        except requests.exceptions.Timeout:
            logger.warning("Request to Keywords AI timed out")
            return None
        except Exception as e:
            logger.warning(f"Error sending trace to Keywords AI: {e}")
            return None
