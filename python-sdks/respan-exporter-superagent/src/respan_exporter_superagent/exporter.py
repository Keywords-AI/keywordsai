import logging
import os
import threading
from typing import Any
from typing import Optional

from respan_exporter_superagent.types import RespanExportParams
from respan_exporter_superagent.utils import build_payload
from respan_exporter_superagent.utils import now_utc
from respan_exporter_superagent.utils import send_payloads
from respan_exporter_superagent.utils import validate_payload

try:
    from safety_agent import create_client as superagent_create_client
except Exception:  # pragma: no cover
    superagent_create_client = None


logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = "https://api.respan.ai/api/v1/traces/ingest"


class RespanSuperagentClient:
    """
    Wrapper for Superagent Python SDK (`safety-agent`) that exports call logs to Respan.

    Methods supported:
    - guard
    - redact
    - scan
    - test
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout: int = 10,
        client: Optional[Any] = None,
    ) -> None:
        # Prefer Respan env vars, but keep KeywordsAI aliases for backward compatibility.
        self.api_key = api_key or os.getenv("RESPAN_API_KEY") or os.getenv("KEYWORDSAI_API_KEY")
        self.endpoint = (
            endpoint
            or os.getenv("RESPAN_ENDPOINT")
            or os.getenv("KEYWORDSAI_ENDPOINT")
            or DEFAULT_ENDPOINT
        )
        self.timeout = timeout

        if client is not None:
            self._client = client
        else:
            if superagent_create_client is None:
                raise RuntimeError("safety-agent must be installed to create a Superagent client")
            self._client = superagent_create_client()

    async def guard(self, *, keywordsai_params: Optional[RespanExportParams] = None, **kwargs: Any) -> Any:
        return await self._call_and_export(method_name="guard", keywordsai_params=keywordsai_params, **kwargs)

    async def redact(self, *, keywordsai_params: Optional[RespanExportParams] = None, **kwargs: Any) -> Any:
        return await self._call_and_export(method_name="redact", keywordsai_params=keywordsai_params, **kwargs)

    async def scan(self, *, keywordsai_params: Optional[RespanExportParams] = None, **kwargs: Any) -> Any:
        return await self._call_and_export(method_name="scan", keywordsai_params=keywordsai_params, **kwargs)

    async def test(self, *, keywordsai_params: Optional[RespanExportParams] = None, **kwargs: Any) -> Any:
        return await self._call_and_export(method_name="test", keywordsai_params=keywordsai_params, **kwargs)

    async def _call_and_export(
        self,
        *,
        method_name: str,
        keywordsai_params: Optional[RespanExportParams],
        **kwargs: Any,
    ) -> Any:
        params: RespanExportParams = keywordsai_params or {}
        if params.get("disable_log") is True:
            method = getattr(self._client, method_name)
            return await method(**kwargs)

        start_time = now_utc()
        end_time = now_utc()
        error_message: Optional[str] = None
        status = "success"

        def _export(result: Any) -> None:
            if not self.api_key:
                return

            input_value = None
            if "input" in kwargs:
                input_value = kwargs.get("input")
            elif "text" in kwargs:
                input_value = kwargs.get("text")
            elif "repo" in kwargs:
                input_value = kwargs.get("repo")

            try:
                payload = build_payload(
                    method_name=method_name,
                    start_time=start_time,
                    end_time=end_time,
                    status=status,
                    input_value=input_value,
                    output_value=result,
                    error_message=error_message,
                    export_params=params,
                )
                validated_payload = validate_payload(payload)
            except Exception as exc:
                logger.exception("Failed to validate Respan payload: %s", exc)
                return

            threading.Thread(
                target=send_payloads,
                kwargs={
                    "api_key": self.api_key,
                    "endpoint": self.endpoint,
                    "timeout": self.timeout,
                    "payloads": [validated_payload],
                },
                daemon=True,
            ).start()

        try:
            method = getattr(self._client, method_name)
            result = await method(**kwargs)
            end_time = now_utc()
            _export(result)
            return result
        except Exception as exc:
            end_time = now_utc()
            status = "error"
            error_message = str(exc)
            _export(None)
            raise


def create_client(
    *,
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    timeout: int = 10,
    client: Optional[Any] = None,
) -> RespanSuperagentClient:
    """
    Create a Respan-exporting Superagent client.

    This intentionally mirrors `safety_agent.create_client()` while adding:
    - `RESPAN_API_KEY` / `RESPAN_ENDPOINT` (and `KEYWORDSAI_*` aliases) forwarding
    - automatic export of `guard`, `redact`, `scan`, `test` call logs
    """
    return RespanSuperagentClient(api_key=api_key, endpoint=endpoint, timeout=timeout, client=client)


# Backwards-compatible aliases
KeywordsAISuperagentClient = RespanSuperagentClient

