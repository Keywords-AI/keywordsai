"""Instrumentor for Helicone Manual Logger.

This module intercepts the `send_log` method of `HeliconeManualLogger` and sends
logs to both Helicone and Keywords AI / Respan.
"""

import json
import logging
import os
import threading
from typing import Any, Dict, Optional, Union

import requests
import wrapt

from respan_sdk.constants.api_constants import DEFAULT_TRACES_INGEST_ENDPOINT
from respan_sdk.utils.time import format_timestamp

try:
    from helicone_helpers import HeliconeManualLogger
except ImportError:
    HeliconeManualLogger = None

logger = logging.getLogger(__name__)


class HeliconeInstrumentor:
    """An instrumentor that intercepts Helicone logs and sends them to Keywords AI / Respan.

    Usage:
        from respan_exporter_helicone import HeliconeInstrumentor
        from helicone_helpers import HeliconeManualLogger
        
        instrumentor = HeliconeInstrumentor()
        instrumentor.instrument(api_key="your-respan-api-key")
        
        # Helicone logs will now also go to Respan!
    """

    _api_key: Optional[str] = None
    _endpoint: Optional[str] = None

    def instrument(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout: int = 10,
    ) -> None:
        """Enable instrumentation.

        Args:
            api_key: Respan API key (uses RESPAN_API_KEY env var if not set)
            endpoint: Respan ingest endpoint
            timeout: Network timeout for the Respan API requests
        """
        self._api_key = api_key or os.getenv("RESPAN_API_KEY")
        self._endpoint = endpoint or os.getenv(
            "RESPAN_ENDPOINT",
            DEFAULT_TRACES_INGEST_ENDPOINT
        )
        self._timeout = timeout

        if not self._api_key:
            logger.warning(
                "RESPAN_API_KEY is not set. Helicone logs will not be exported to Respan."
            )
            return

        self._patch()
        logger.info("Helicone instrumentation enabled for Respan")

    def uninstrument(self) -> None:
        """Disable instrumentation by removing wrappers."""
        logger.info("Helicone instrumentation disabled")

    def _patch(self) -> None:
        """Patch HeliconeManualLogger.send_log to intercept data."""
        if HeliconeManualLogger is None:
            logger.error("helicone-helpers is not installed. Cannot instrument Helicone.")
            return

        def send_log_wrapper(wrapped: Any, instance: Any, args: Any, kwargs: Any) -> Any:
            """Wrapper for send_log that intercepts log events."""
            # Extract arguments based on HeliconeManualLogger signature
            provider = kwargs.get("provider")
            if not provider and len(args) > 0:
                provider = args[0]

            request = kwargs.get("request")
            if not request and len(args) > 1:
                request = args[1]

            response = kwargs.get("response")
            if not response and len(args) > 2:
                response = args[2]

            options = kwargs.get("options")
            if not options and len(args) > 3:
                options = args[3]

            try:
                # Still call the original send_log to ensure Helicone receives it
                result = wrapped(*args, **kwargs)
                
                # Transform and send to Respan in a background thread
                if self._api_key and request:
                    threading.Thread(
                        target=self._send_to_respan,
                        kwargs={
                            "provider": provider,
                            "request": request,
                            "response": response,
                            "options": options,
                        },
                        daemon=True,
                    ).start()
                return result
            except Exception as e:
                logger.error(f"Error in Helicone wrap: {e}")
                return wrapped(*args, **kwargs)

        wrapt.wrap_function_wrapper(
            module="helicone_helpers.manual_logger",
            name="HeliconeManualLogger.send_log",
            wrapper=send_log_wrapper
        )

    def _send_to_respan(
        self,
        provider: Optional[str],
        request: Dict[str, Any],
        response: Union[Dict[str, Any], str, None],
        options: Optional[Dict[str, Any]],
    ) -> None:
        """Transform Helicone log and send it to Respan API."""
        try:
            options = options or {}
            
            start_ts = options.get("start_time")
            end_ts = options.get("end_time")
            start_time = format_timestamp(ts=start_ts)
            timestamp = format_timestamp(ts=end_ts)
            
            latency = None
            if start_ts and end_ts:
                latency = max(0.0, end_ts - start_ts)

            # Build Respan payload
            payload = {
                "log_type": "generation",
                "start_time": start_time,
                "timestamp": timestamp,
                "latency": latency,
                "provider": provider,
            }

            # Extract model, input, output
            if isinstance(request, dict):
                payload["model"] = request.get("model")
                if "messages" in request:
                    payload["input"] = json.dumps(request["messages"])
                elif "prompt" in request:
                    payload["input"] = request["prompt"]
                else:
                    payload["input"] = json.dumps(request)

            if isinstance(response, dict):
                # Try to extract content or choices
                if "choices" in response:
                    payload["output"] = json.dumps(response["choices"])
                else:
                    payload["output"] = json.dumps(response)
                
                # Extract usage
                if "usage" in response:
                    usage = response["usage"]
                    if isinstance(usage, dict):
                        payload["prompt_tokens"] = usage.get("prompt_tokens")
                        payload["completion_tokens"] = usage.get("completion_tokens")
                        payload["total_request_tokens"] = usage.get("total_tokens")
            elif isinstance(response, str):
                payload["output"] = response

            # Process metadata and headers
            metadata = {}
            additional_headers = options.get("additional_headers", {})
            for key, value in additional_headers.items():
                if key.lower().startswith("helicone-"):
                    metadata[key] = value

            if metadata:
                payload["metadata"] = metadata
                # Map specific helicone properties to Respan customer_identifier or session_id
                # (e.g., Helicone-User-Id, Helicone-Session-Id)
                if "Helicone-User-Id" in metadata:
                    payload["customer_identifier"] = metadata["Helicone-User-Id"]
                if "Helicone-Session-Id" in metadata:
                    payload["session_identifier"] = metadata["Helicone-Session-Id"]

            # Send payload
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }
            
            resp = requests.post(
                url=self._endpoint,
                json=[payload],
                headers=headers,
                timeout=self._timeout,
            )
            
            if resp.status_code not in (200, 201):
                logger.warning(f"Respan export failed: {resp.status_code} - {resp.text}")

        except Exception as e:
            logger.error(f"Failed to send Helicone log to Respan: {e}", exc_info=True)
