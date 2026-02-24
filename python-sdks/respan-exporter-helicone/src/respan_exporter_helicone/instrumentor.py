"""Instrumentor for Helicone Manual Logger.

This module intercepts the `send_log` method of `HeliconeManualLogger` and sends
logs to both Helicone and Keywords AI / Respan.
"""

import json
import logging
import os
import threading
from typing import Any, Dict, Optional, Tuple, Union

import requests
import wrapt

from respan_sdk.constants.api_constants import DEFAULT_TRACES_INGEST_ENDPOINT
from respan_sdk.utils.time import format_timestamp

try:
    from helicone_helpers import HeliconeManualLogger
except ImportError:
    HeliconeManualLogger = None

logger = logging.getLogger(__name__)

HELICONE_LOGGER_MODULE = "helicone_helpers.manual_logger"
HELICONE_SEND_LOG_FUNCTION = "HeliconeManualLogger.send_log"
HELICONE_USER_ID_HEADER = "helicone-user-id"
HELICONE_SESSION_ID_HEADER = "helicone-session-id"


class HeliconeInstrumentor:
    """An instrumentor that intercepts Helicone logs and sends them to Keywords AI / Respan.

    Usage:
        from respan_exporter_helicone import HeliconeInstrumentor
        from helicone_helpers import HeliconeManualLogger
        
        instrumentor = HeliconeInstrumentor()
        instrumentor.instrument(api_key="your-respan-api-key")
        
        # Helicone logs will now also go to Respan!
    """

    def __init__(self) -> None:
        self._api_key: Optional[str] = None
        self._endpoint: Optional[str] = None
        self._timeout = 10
        self._is_patched = False

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
        if self._is_patched and hasattr(wrapt, "unwrap_function_wrapper"):
            try:
                wrapt.unwrap_function_wrapper(
                    module=HELICONE_LOGGER_MODULE,
                    name=HELICONE_SEND_LOG_FUNCTION,
                )
            except Exception as exc:
                logger.warning(
                    "Failed to unwrap Helicone instrumentation cleanly: %s",
                    exc,
                )
        self._is_patched = False
        logger.info("Helicone instrumentation disabled")

    def _patch(self) -> None:
        """Patch HeliconeManualLogger.send_log to intercept data."""
        if self._is_patched:
            return

        if HeliconeManualLogger is None:
            logger.error("helicone-helpers is not installed. Cannot instrument Helicone.")
            return

        def send_log_wrapper(
            wrapped: Any,
            instance: Any,
            args: Tuple[Any, ...],
            kwargs: Dict[str, Any],
        ) -> Any:
            """Wrapper for send_log that intercepts log events."""
            del instance
            provider, request, response, options = self._resolve_send_log_args(
                args=args,
                kwargs=kwargs,
            )

            # Always call original send_log exactly once so Helicone behavior is preserved.
            result = wrapped(*args, **kwargs)

            if self._api_key and isinstance(request, dict):
                try:
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
                except Exception as exc:
                    logger.error("Error in Helicone wrapper: %s", exc)
            return result

        wrapt.wrap_function_wrapper(
            module=HELICONE_LOGGER_MODULE,
            name=HELICONE_SEND_LOG_FUNCTION,
            wrapper=send_log_wrapper,
        )
        self._is_patched = True

    @staticmethod
    def _resolve_send_log_args(
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Union[Dict[str, Any], str, None], Optional[Dict[str, Any]]]:
        """Resolve Helicone send_log args regardless of positional/keyword calling style."""
        provider = kwargs.get("provider", args[0] if len(args) > 0 else None)
        request = kwargs.get("request", args[1] if len(args) > 1 else None)
        response = kwargs.get("response", args[2] if len(args) > 2 else None)
        options = kwargs.get("options", args[3] if len(args) > 3 else None)
        return provider, request, response, options

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
            if isinstance(additional_headers, dict):
                for key, value in additional_headers.items():
                    if isinstance(key, str) and key.lower().startswith("helicone-"):
                        metadata[key] = value

            if metadata:
                payload["metadata"] = metadata
                # Map specific helicone properties to Respan customer_identifier or session_id
                # (e.g., Helicone-User-Id, Helicone-Session-Id)
                normalized_metadata = {
                    key.lower(): value for key, value in metadata.items()
                }
                if HELICONE_USER_ID_HEADER in normalized_metadata:
                    payload["customer_identifier"] = normalized_metadata[HELICONE_USER_ID_HEADER]
                if HELICONE_SESSION_ID_HEADER in normalized_metadata:
                    payload["session_identifier"] = normalized_metadata[HELICONE_SESSION_ID_HEADER]

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

        except Exception as exc:
            logger.error("Failed to send Helicone log to Respan: %s", exc, exc_info=True)
