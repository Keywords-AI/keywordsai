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
        id: Optional[str] = None
        usage: Optional[Dict[str, Any]] = None

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
    from respan_sdk.respan_types.exporter_session_types import ExporterSessionState  # noqa: F401
    from respan_sdk.utils import RetryHandler  # noqa: F401
except (ImportError, ModuleNotFoundError):
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

    respan_sdk_exporter_session_types_module = types.ModuleType(
        "respan_sdk.respan_types.exporter_session_types"
    )
    respan_sdk_utils_module = types.ModuleType("respan_sdk.utils")
    respan_sdk_utils_module.__path__ = []  # type: ignore[attr-defined]

    @dataclass
    class ExporterSessionState:
        session_id: str
        trace_id: str
        trace_name: str
        started_at: Any
        pending_tools: Dict[str, Any] = field(default_factory=dict)
        is_root_emitted: bool = False

    @dataclass
    class PendingToolState:
        span_unique_id: str
        started_at: Any
        tool_name: str
        tool_input: Any = None

    class RetryHandler:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def execute(self, fn: Callable[..., Any], context: str = "") -> None:
            fn()

    respan_sdk_exporter_session_types_module.ExporterSessionState = ExporterSessionState
    respan_sdk_exporter_session_types_module.PendingToolState = PendingToolState
    respan_sdk_utils_module.RetryHandler = RetryHandler

    respan_sdk_internal_types_module.Message = Message
    respan_sdk_param_types_module.RespanTextLogParams = RespanTextLogParams
    respan_sdk_module.constants = respan_sdk_constants_module
    respan_sdk_module.respan_types = respan_sdk_types_module
    respan_sdk_module.utils = respan_sdk_utils_module
    respan_sdk_constants_module.llm_logging = respan_sdk_llm_logging_module
    respan_sdk_constants_module.tracing_constants = (
        respan_sdk_tracing_constants_module
    )
    respan_sdk_types_module._internal_types = respan_sdk_internal_types_module
    respan_sdk_types_module.param_types = respan_sdk_param_types_module
    respan_sdk_types_module.exporter_session_types = (
        respan_sdk_exporter_session_types_module
    )

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
    sys.modules["respan_sdk.respan_types.exporter_session_types"] = (
        respan_sdk_exporter_session_types_module
    )
    sys.modules["respan_sdk.utils"] = respan_sdk_utils_module


from unittest.mock import MagicMock, patch

from claude_agent_sdk import ResultMessage, AssistantMessage, SystemMessage, UserMessage
from respan_exporter_anthropic_agents.respan_anthropic_agents_exporter import (
    RespanAnthropicAgentsExporter,
)
from respan_exporter_anthropic_agents.utils import (
    build_trace_name_from_prompt,
    coerce_int,
    resolve_export_endpoint,
    serialize_metadata,
    serialize_tool_calls,
    serialize_value,
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

    async def test_track_assistant_message_exports_payload_with_usage(self) -> None:
        exporter = RespanAnthropicAgentsExporter(
            api_key="test-api-key",
            endpoint="https://example.com/ingest",
        )

        captured_batches: List[List[Dict[str, Any]]] = []

        def capture_payloads(payloads: List[Dict[str, Any]]) -> None:
            captured_batches.append(payloads)

        exporter._send_payloads = capture_payloads  # type: ignore[method-assign]

        assistant_message = AssistantMessage(
            content=[{"type": "text", "text": "Hello"}],
            model="claude-3-5-sonnet",
        )
        assistant_message.id = "msg-1"
        assistant_message.usage = {
            "input_tokens": 10,
            "output_tokens": 5,
            "total_tokens": 15,
            "cache_read_input_tokens": 2,
            "cache_creation_input_tokens": 3,
        }

        await exporter.track_message(message=assistant_message, session_id="session-1")

        flattened_payloads = [payload for batch in captured_batches for payload in batch]
        self.assertTrue(flattened_payloads)

        result_payload = next(
            payload
            for payload in flattened_payloads
            if payload.get("span_name") == "assistant_message"
        )
        self.assertEqual(result_payload.get("trace_unique_id"), "session-1")
        self.assertEqual(result_payload.get("span_unique_id"), "msg-1")
        self.assertEqual(result_payload.get("log_type"), "generation")
        self.assertEqual(result_payload.get("prompt_tokens"), 10)
        self.assertEqual(result_payload.get("completion_tokens"), 5)
        self.assertEqual(result_payload.get("total_request_tokens"), 15)
        self.assertEqual(result_payload.get("prompt_cache_hit_tokens"), 2)
        self.assertEqual(result_payload.get("prompt_cache_creation_tokens"), 3)

    async def test_create_hooks_contains_expected_events(self) -> None:
        exporter = RespanAnthropicAgentsExporter(api_key="test-api-key")
        hooks = exporter.create_hooks(existing_hooks={})

        self.assertIn("UserPromptSubmit", hooks)
        self.assertIn("PreToolUse", hooks)
        self.assertIn("PostToolUse", hooks)
        self.assertIn("SubagentStop", hooks)
        self.assertIn("Stop", hooks)


    async def test_result_message_error_sets_status_500(self) -> None:
        exporter = RespanAnthropicAgentsExporter(
            api_key="test-api-key",
            endpoint="https://example.com/ingest",
        )
        captured_batches: List[List[Dict[str, Any]]] = []

        def capture_payloads(payloads: List[Dict[str, Any]]) -> None:
            captured_batches.append(payloads)

        exporter._send_payloads = capture_payloads  # type: ignore[method-assign]

        error_message = ResultMessage(
            subtype="error",
            duration_ms=100,
            duration_api_ms=40,
            is_error=True,
            num_turns=1,
            session_id="session-err",
            result="something failed",
        )

        await exporter.track_message(message=error_message, session_id="session-err")

        flattened_payloads = [p for batch in captured_batches for p in batch]
        result_payload = next(
            p for p in flattened_payloads if p.get("span_name") == "result:error"
        )
        self.assertEqual(result_payload.get("status_code"), 500)
        self.assertEqual(result_payload.get("error_bit"), 1)
        self.assertIn("agent_result_error", result_payload.get("error_message", ""))

    async def test_send_payloads_skips_when_no_api_key(self) -> None:
        exporter = RespanAnthropicAgentsExporter(
            api_key=None,
            endpoint="https://example.com/ingest",
        )
        result_message = ResultMessage(
            subtype="success",
            duration_ms=100,
            duration_api_ms=40,
            is_error=False,
            num_turns=1,
            session_id="session-nokey",
        )
        # Should not raise — just logs a warning and returns
        await exporter.track_message(message=result_message, session_id="session-nokey")

    async def test_send_payloads_http_export_mocked(self) -> None:
        exporter = RespanAnthropicAgentsExporter(
            api_key="test-api-key",
            endpoint="https://example.com/ingest",
        )

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
            result_message = ResultMessage(
                subtype="success",
                duration_ms=100,
                duration_api_ms=40,
                is_error=False,
                num_turns=1,
                session_id="session-http",
                usage={"input_tokens": 5, "output_tokens": 3},
            )
            await exporter.track_message(
                message=result_message, session_id="session-http"
            )
            # Root span + result span = at least 2 calls
            self.assertGreaterEqual(mock_urlopen.call_count, 2)

    async def test_hook_user_prompt_submit_creates_span(self) -> None:
        exporter = RespanAnthropicAgentsExporter(
            api_key="test-api-key",
            endpoint="https://example.com/ingest",
        )
        captured_batches: List[List[Dict[str, Any]]] = []

        def capture_payloads(payloads: List[Dict[str, Any]]) -> None:
            captured_batches.append(payloads)

        exporter._send_payloads = capture_payloads  # type: ignore[method-assign]

        await exporter._on_user_prompt_submit(
            input_data={"session_id": "hook-session", "prompt": "Hello world"},
            tool_use_id=None,
            context={},
        )

        flattened_payloads = [p for batch in captured_batches for p in batch]
        prompt_payload = next(
            (p for p in flattened_payloads if p.get("span_name") == "user_prompt"),
            None,
        )
        self.assertIsNotNone(prompt_payload)
        self.assertEqual(prompt_payload.get("log_type"), "task")

    async def test_hook_tool_lifecycle(self) -> None:
        exporter = RespanAnthropicAgentsExporter(
            api_key="test-api-key",
            endpoint="https://example.com/ingest",
        )
        captured_batches: List[List[Dict[str, Any]]] = []

        def capture_payloads(payloads: List[Dict[str, Any]]) -> None:
            captured_batches.append(payloads)

        exporter._send_payloads = capture_payloads  # type: ignore[method-assign]

        await exporter._on_pre_tool_use(
            input_data={
                "session_id": "tool-session",
                "tool_use_id": "tool-1",
                "tool_name": "calculator",
                "tool_input": {"expression": "2+2"},
            },
            tool_use_id="tool-1",
            context={},
        )

        await exporter._on_post_tool_use(
            input_data={
                "session_id": "tool-session",
                "tool_use_id": "tool-1",
                "tool_name": "calculator",
                "tool_response": "4",
            },
            tool_use_id="tool-1",
            context={},
        )

        flattened_payloads = [p for batch in captured_batches for p in batch]
        tool_payload = next(
            (p for p in flattened_payloads if p.get("span_name") == "calculator"),
            None,
        )
        self.assertIsNotNone(tool_payload)
        self.assertEqual(tool_payload.get("log_type"), "tool")

    async def test_system_message_sets_session_id(self) -> None:
        exporter = RespanAnthropicAgentsExporter(
            api_key="test-api-key",
            endpoint="https://example.com/ingest",
        )
        captured_batches: List[List[Dict[str, Any]]] = []

        def capture_payloads(payloads: List[Dict[str, Any]]) -> None:
            captured_batches.append(payloads)

        exporter._send_payloads = capture_payloads  # type: ignore[method-assign]

        system_msg = SystemMessage(data={"session_id": "sys-session-1"})
        await exporter.track_message(message=system_msg)

        self.assertEqual(exporter._last_session_id, "sys-session-1")

    async def test_user_message_exports_payload(self) -> None:
        exporter = RespanAnthropicAgentsExporter(
            api_key="test-api-key",
            endpoint="https://example.com/ingest",
        )
        captured_batches: List[List[Dict[str, Any]]] = []

        def capture_payloads(payloads: List[Dict[str, Any]]) -> None:
            captured_batches.append(payloads)

        exporter._send_payloads = capture_payloads  # type: ignore[method-assign]

        user_msg = UserMessage(content="Hello from user")
        await exporter.track_message(
            message=user_msg, session_id="user-session-1"
        )

        flattened_payloads = [p for batch in captured_batches for p in batch]
        user_payload = next(
            (p for p in flattened_payloads if p.get("span_name") == "user_message"),
            None,
        )
        self.assertIsNotNone(user_payload)
        self.assertEqual(user_payload.get("log_type"), "task")


class UtilsTests(unittest.TestCase):
    def test_coerce_int_with_valid_values(self) -> None:
        self.assertEqual(coerce_int(42), 42)
        self.assertEqual(coerce_int("10"), 10)
        self.assertEqual(coerce_int(0), 0)
        self.assertEqual(coerce_int(3.7), 3)

    def test_coerce_int_with_invalid_values(self) -> None:
        self.assertIsNone(coerce_int(None))
        self.assertIsNone(coerce_int("abc"))
        self.assertIsNone(coerce_int([]))

    def test_build_trace_name_from_prompt(self) -> None:
        self.assertEqual(build_trace_name_from_prompt(prompt="Hello"), "Hello")
        self.assertIsNone(build_trace_name_from_prompt(prompt=None))
        self.assertIsNone(build_trace_name_from_prompt(prompt=""))
        self.assertIsNone(build_trace_name_from_prompt(prompt="   "))
        long_prompt = "x" * 200
        self.assertEqual(len(build_trace_name_from_prompt(prompt=long_prompt)), 120)

    def test_serialize_value_primitives(self) -> None:
        self.assertIsNone(serialize_value(None))
        self.assertEqual(serialize_value("hello"), "hello")
        self.assertEqual(serialize_value(42), 42)
        self.assertEqual(serialize_value(True), True)

    def test_serialize_value_dict_and_list(self) -> None:
        self.assertEqual(serialize_value({"a": 1}), {"a": 1})
        self.assertEqual(serialize_value([1, 2]), [1, 2])

    def test_serialize_metadata(self) -> None:
        self.assertIsNone(serialize_metadata(None))
        self.assertEqual(serialize_metadata({"key": "val"}), {"key": "val"})
        self.assertEqual(serialize_metadata("scalar"), {"value": "scalar"})

    def test_serialize_tool_calls(self) -> None:
        self.assertIsNone(serialize_tool_calls(None))
        self.assertEqual(
            serialize_tool_calls([{"name": "tool1"}]),
            [{"name": "tool1"}],
        )
        self.assertEqual(
            serialize_tool_calls({"name": "single"}),
            [{"name": "single"}],
        )

    def test_resolve_export_endpoint_default(self) -> None:
        endpoint = resolve_export_endpoint(base_url=None)
        self.assertIn("traces/ingest", endpoint)

    def test_resolve_export_endpoint_custom(self) -> None:
        endpoint = resolve_export_endpoint(base_url="https://custom.server")
        self.assertIn("traces/ingest", endpoint)


if __name__ == "__main__":
    unittest.main()
