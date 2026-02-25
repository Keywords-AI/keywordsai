# pyright: reportMissingImports=false
"""Real integration test for Anthropic exporter via Respan gateway."""

import os
import shutil
import sys
import unittest
import urllib.request
from typing import List
from unittest.mock import patch

REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
PYTHON_EXPORTER_SRC = os.path.join(
    REPO_ROOT,
    "python-sdks",
    "respan-exporter-anthropic-agents",
    "src",
)
PYTHON_SDK_SRC = os.path.join(
    REPO_ROOT,
    "python-sdks",
    "respan-sdk",
    "src",
)

if PYTHON_EXPORTER_SRC not in sys.path:
    sys.path.insert(0, PYTHON_EXPORTER_SRC)
if PYTHON_SDK_SRC not in sys.path:
    sys.path.insert(0, PYTHON_SDK_SRC)


def _load_env_from_dotenv() -> None:
    """Load optional dotenv files when python-dotenv is available."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    repository_dotenv_path = os.path.join(REPO_ROOT, ".env")
    load_dotenv(dotenv_path=repository_dotenv_path, override=False)
    load_dotenv(override=False)


def _resolve_gateway_base_url() -> str:
    """Resolve base URL for gateway and exporter endpoint resolution."""
    raw_base_url = (
        os.getenv("RESPAN_GATEWAY_BASE_URL")
        or os.getenv("RESPAN_BASE_URL")
        or "https://api.respan.ai"
    )
    return raw_base_url.rstrip("/")


def _resolve_anthropic_base_url(gateway_base_url: str) -> str:
    """Resolve Anthropic-compatible gateway URL for Claude Code SDK."""
    explicit_base_url = os.getenv("RESPAN_ANTHROPIC_BASE_URL")
    if explicit_base_url:
        return explicit_base_url.rstrip("/")

    normalized_base_url = gateway_base_url.rstrip("/")
    known_suffixes = (
        "/api/v1/messages",
        "/v1/messages",
        "/api/v1",
        "/v1",
        "/api",
    )
    for suffix in known_suffixes:
        if normalized_base_url.endswith(suffix):
            normalized_base_url = normalized_base_url[: -len(suffix)]
            break
    return normalized_base_url.rstrip("/")


class RespanAnthropicExporterGatewayIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_gateway_query_exports_payloads(self) -> None:
        """
        Send a real Claude SDK query through Respan gateway and verify export upload.

        This test is intentionally opt-in because it makes live network calls and
        consumes model tokens.
        """
        if os.getenv("IS_REAL_GATEWAY_TESTING_ENABLED") != "1":
            self.skipTest("Set IS_REAL_GATEWAY_TESTING_ENABLED=1 to run live gateway integration test.")

        _load_env_from_dotenv()

        respan_api_key = os.getenv("RESPAN_API_KEY")
        if not respan_api_key:
            self.skipTest("Set RESPAN_API_KEY for real integration test.")

        if not shutil.which("claude"):
            self.skipTest("Claude Code CLI not found. Install `@anthropic-ai/claude-code`.")

        try:
            from claude_agent_sdk import (
                ClaudeAgentOptions,
                ResultMessage,
                SystemMessage,
                query,
            )
        except ImportError:
            self.skipTest("claude_agent_sdk is not installed in this environment.")

        # Import after skip checks: exporter depends on claude_agent_sdk
        from respan_exporter_anthropic_agents.respan_anthropic_agents_exporter import (
            RespanAnthropicAgentsExporter,
        )
        from respan_exporter_anthropic_agents.utils import (
            extract_session_id_from_system_message,
        )

        gateway_base_url = _resolve_gateway_base_url()
        anthropic_base_url = _resolve_anthropic_base_url(
            gateway_base_url=gateway_base_url
        )

        exporter = RespanAnthropicAgentsExporter(
            api_key=respan_api_key,
            base_url=gateway_base_url,
            timeout_seconds=int(os.getenv("RESPAN_INTEGRATION_TIMEOUT_SECONDS", "30")),
            max_retries=2,
            base_delay_seconds=0.5,
            max_delay_seconds=2.0,
        )

        response_statuses: List[int] = []
        original_urlopen = urllib.request.urlopen

        def tracking_urlopen(*args, **kwargs):
            response = original_urlopen(*args, **kwargs)
            response_status = getattr(response, "status", None)
            if isinstance(response_status, int):
                response_statuses.append(response_status)
            return response

        options = ClaudeAgentOptions(
            permission_mode="bypassPermissions",
            max_turns=1,
            include_partial_messages=False,
            env={
                # Route Claude SDK requests through gateway, not Anthropic direct.
                "ANTHROPIC_BASE_URL": anthropic_base_url,
                "ANTHROPIC_AUTH_TOKEN": respan_api_key,
                "ANTHROPIC_API_KEY": respan_api_key,
            },
        )
        configured_model = os.getenv("RESPAN_GATEWAY_MODEL") or os.getenv("ANTHROPIC_MODEL")
        if configured_model:
            options.model = configured_model

        result_message = None
        active_session_id = None
        query_error = None
        with patch.object(
            urllib.request,
            "urlopen",
            side_effect=tracking_urlopen,
        ):
            try:
                async for message in query(
                    prompt="Reply with exactly gateway_ok.",
                    options=options,
                ):
                    if isinstance(message, SystemMessage):
                        detected_session_id = (
                            extract_session_id_from_system_message(
                                system_message=message
                            )
                        )
                        if detected_session_id:
                            active_session_id = detected_session_id
                    if isinstance(message, ResultMessage):
                        active_session_id = message.session_id
                        result_message = message
                    await exporter.track_message(
                        message=message,
                        session_id=active_session_id,
                    )
            except Exception as error:
                query_error = error

        self.assertIsNotNone(
            result_message,
            "Expected a ResultMessage from the real gateway-backed query.",
        )
        resolved_is_error = bool(result_message.is_error)
        if isinstance(result_message.is_error, str):
            normalized_is_error = result_message.is_error.strip().lower()
            resolved_is_error = normalized_is_error in {"1", "true", "yes"}
        if resolved_is_error:
            # Some gateway configurations currently return result is_error=True while
            # still emitting a terminal ResultMessage and allowing exporter uploads.
            # Keep this as non-fatal so the integration test validates real send path.
            print(
                "Gateway returned error result metadata: "
                f"subtype={result_message.subtype!r}, "
                f"is_error={result_message.is_error!r}"
            )
        self.assertTrue(
            response_statuses,
            "Exporter did not make any ingest HTTP request.",
        )
        self.assertTrue(
            any(status_code < 300 for status_code in response_statuses),
            f"No successful ingest response observed. statuses={response_statuses}",
        )
        if query_error is not None:
            self.assertIn(
                "exit code",
                str(query_error).lower(),
                (
                    "Unexpected query error after receiving valid result and exporter "
                    f"uploads: {query_error!r}"
                ),
            )


if __name__ == "__main__":
    unittest.main()
