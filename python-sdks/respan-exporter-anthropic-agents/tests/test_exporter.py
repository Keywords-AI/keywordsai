# pyright: reportMissingImports=false
import os
import sys
import types
import unittest
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
PYTHON_EXPORTER_SRC = os.path.join(
    REPO_ROOT,
    "python-sdks",
    "respan-exporter-anthropic-agents",
    "src",
)

if PYTHON_EXPORTER_SRC not in sys.path:
    sys.path.insert(0, PYTHON_EXPORTER_SRC)


try:
    import claude_agent_sdk  # noqa: F401
except ImportError:
    claude_agent_sdk_module = types.ModuleType("claude_agent_sdk")

    @dataclass
    class HookMatcher:
        matcher: Optional[str] = None
        hooks: List[Callable[..., Any]] = field(default_factory=list)

    @dataclass
    class ClaudeAgentOptions:
        hooks: Optional[Dict[str, List[HookMatcher]]] = None

    @dataclass
    class AssistantMessage:
        content: List[Any]
        model: str

    @dataclass
    class UserMessage:
        content: Any

    @dataclass
    class SystemMessage:
        data: Dict[str, Any]

    @dataclass
    class ResultMessage:
        subtype: str
        duration_ms: int
        duration_api_ms: int
        is_error: bool
        num_turns: int
        session_id: str
        total_cost_usd: Optional[float] = None
        usage: Optional[Dict[str, Any]] = None
        result: Optional[str] = None
        structured_output: Any = None

    @dataclass
    class StreamEvent:
        session_id: str

    async def query(prompt: Any, options: Optional[ClaudeAgentOptions] = None):
        if False:
            yield prompt
            yield options

    claude_agent_sdk_module.HookMatcher = HookMatcher
    claude_agent_sdk_module.ClaudeAgentOptions = ClaudeAgentOptions
    claude_agent_sdk_module.AssistantMessage = AssistantMessage
    claude_agent_sdk_module.UserMessage = UserMessage
    claude_agent_sdk_module.SystemMessage = SystemMessage
    claude_agent_sdk_module.ResultMessage = ResultMessage
    claude_agent_sdk_module.StreamEvent = StreamEvent
    claude_agent_sdk_module.query = query
    sys.modules["claude_agent_sdk"] = claude_agent_sdk_module


try:
    import respan_sdk  # noqa: F401
except ImportError:
    respan_sdk_module = types.ModuleType("respan_sdk")
    respan_sdk_module.__path__ = []  # type: ignore[attr-defined]
    respan_sdk_constants_module = types.ModuleType("respan_sdk.constants")
    respan_sdk_constants_module.__path__ = []  # type: ignore[attr-defined]
    respan_sdk_llm_logging_module = types.ModuleType(
        "respan_sdk.constants.llm_logging"
    )
    respan_sdk_tracing_constants_module = types.ModuleType(
        "respan_sdk.constants.tracing_constants"
    )
    respan_sdk_types_module = types.ModuleType("respan_sdk.respan_types")
    respan_sdk_types_module.__path__ = []  # type: ignore[attr-defined]
    respan_sdk_internal_types_module = types.ModuleType(
        "respan_sdk.respan_types._internal_types"
    )
    respan_sdk_param_types_module = types.ModuleType(
        "respan_sdk.respan_types.param_types"
    )

    class Message:
        """Plain class stub for respan_sdk.respan_types._internal_types.Message."""

        def __init__(self, role: str, content: str) -> None:
            self.role = role
            self.content = content

    class RespanTextLogParams:
        def __init__(self, **kwargs: Any) -> None:
            self._values = kwargs

        def model_dump(
            self,
            mode: str = "json",
            exclude_none: bool = False,
        ) -> Dict[str, Any]:
            if not exclude_none:
                return dict(self._values)
            normalized_values: Dict[str, Any] = {}
            for key, value in self._values.items():
                if value is not None:
                    normalized_values[key] = value
            return normalized_values

    def resolve_tracing_ingest_endpoint(base_url: str) -> str:
        return f"{base_url.rstrip('/')}/v1/traces/ingest"

    respan_sdk_llm_logging_module.LOG_TYPE_AGENT = "agent"
    respan_sdk_llm_logging_module.LOG_TYPE_GENERATION = "generation"
    respan_sdk_llm_logging_module.LOG_TYPE_TASK = "task"
    respan_sdk_llm_logging_module.LOG_TYPE_TOOL = "tool"

    respan_sdk_tracing_constants_module.RESPAN_TRACING_INGEST_ENDPOINT = (
        "https://api.respan.ai/v1/traces/ingest"
    )
    respan_sdk_tracing_constants_module.resolve_tracing_ingest_endpoint = (
        resolve_tracing_ingest_endpoint
    )

    respan_sdk_internal_types_module.Message = Message
    respan_sdk_param_types_module.RespanTextLogParams = RespanTextLogParams
    respan_sdk_module.constants = respan_sdk_constants_module
    respan_sdk_module.respan_types = respan_sdk_types_module
    respan_sdk_constants_module.llm_logging = respan_sdk_llm_logging_module
    respan_sdk_constants_module.tracing_constants = (
        respan_sdk_tracing_constants_module
    )
    respan_sdk_types_module._internal_types = respan_sdk_internal_types_module
    respan_sdk_types_module.param_types = respan_sdk_param_types_module

    sys.modules["respan_sdk"] = respan_sdk_module
    sys.modules["respan_sdk.constants"] = respan_sdk_constants_module
    sys.modules["respan_sdk.constants.llm_logging"] = respan_sdk_llm_logging_module
    sys.modules["respan_sdk.constants.tracing_constants"] = (
        respan_sdk_tracing_constants_module
    )
    sys.modules["respan_sdk.respan_types"] = respan_sdk_types_module
    sys.modules["respan_sdk.respan_types._internal_types"] = (
        respan_sdk_internal_types_module
    )
    sys.modules["respan_sdk.respan_types.param_types"] = respan_sdk_param_types_module


from claude_agent_sdk import ResultMessage
from respan_exporter_anthropic_agents.respan_anthropic_agents_exporter import (
    RespanAnthropicAgentsExporter,
)


class RespanAnthropicExporterTests(unittest.IsolatedAsyncioTestCase):
    async def test_track_result_message_exports_payload(self) -> None:
        exporter = RespanAnthropicAgentsExporter(
            api_key="test-api-key",
            endpoint="https://example.com/ingest",
        )

        captured_batches: List[List[Dict[str, Any]]] = []

        def capture_payloads(payloads: List[Dict[str, Any]]) -> None:
            captured_batches.append(payloads)

        exporter._send_payloads = capture_payloads  # type: ignore[method-assign]

        result_message = ResultMessage(
            subtype="success",
            duration_ms=150,
            duration_api_ms=50,
            is_error=False,
            num_turns=2,
            session_id="session-1",
            total_cost_usd=0.01,
            usage={
                "input_tokens": 3,
                "output_tokens": 2,
                "total_tokens": 5,
                "cache_read_input_tokens": 1,
                "cache_creation_input_tokens": 0,
            },
            result="done",
        )

        await exporter.track_message(message=result_message, session_id="session-1")

        flattened_payloads = [payload for batch in captured_batches for payload in batch]
        self.assertTrue(flattened_payloads)

        result_payload = next(
            payload
            for payload in flattened_payloads
            if payload.get("span_name") == "result:success"
        )
        self.assertEqual(result_payload.get("trace_unique_id"), "session-1")
        self.assertEqual(result_payload.get("log_type"), "agent")
        self.assertEqual(result_payload.get("total_request_tokens"), 5)

    async def test_create_hooks_contains_expected_events(self) -> None:
        exporter = RespanAnthropicAgentsExporter(api_key="test-api-key")
        hooks = exporter.create_hooks(existing_hooks={})

        self.assertIn("UserPromptSubmit", hooks)
        self.assertIn("PreToolUse", hooks)
        self.assertIn("PostToolUse", hooks)
        self.assertIn("SubagentStop", hooks)
        self.assertIn("Stop", hooks)


if __name__ == "__main__":
    unittest.main()
