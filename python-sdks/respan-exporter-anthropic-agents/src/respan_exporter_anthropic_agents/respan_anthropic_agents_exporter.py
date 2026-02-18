"""Respan exporter for Anthropic Agent SDK hooks and message streams."""

import json
import logging
import os
import random
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from typing import Any, AsyncGenerator, AsyncIterable, Dict, List, Optional, Union

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage,
    SystemMessage,
    UserMessage,
    query,
)
# StreamEvent may be in __init__ or only in types across claude-agent-sdk versions
try:
    from claude_agent_sdk import StreamEvent
except ImportError:
    from claude_agent_sdk.types import StreamEvent
from respan_sdk.constants.llm_logging import (
    LOG_TYPE_AGENT,
    LOG_TYPE_GENERATION,
    LOG_TYPE_TASK,
    LOG_TYPE_TOOL,
)
from respan_sdk.respan_types._internal_types import Message
from respan_sdk.respan_types.param_types import RespanTextLogParams
from respan_exporter_anthropic_agents.utils import (
    build_trace_name_from_prompt,
    coerce_int,
    extract_assistant_content,
    extract_session_id_from_system_message,
    extract_user_text,
    resolve_export_endpoint,
    serialize_metadata,
    serialize_tool_calls,
    serialize_value,
    utc_now,
)

logger = logging.getLogger(__name__)


class RespanAnthropicAgentsExporter:
    """Exporter that converts Anthropic Agent SDK events into Respan trace logs."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: int = 15,
        max_retries: int = 3,
        base_delay_seconds: float = 1.0,
        max_delay_seconds: float = 30.0,
    ) -> None:
        self.api_key = (
            api_key
            or os.getenv("RESPAN_API_KEY")
            or os.getenv("KEYWORDSAI_API_KEY")
            or None
        )
        self.endpoint = endpoint or self._build_endpoint(base_url=base_url)
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.base_delay_seconds = base_delay_seconds
        self.max_delay_seconds = max_delay_seconds

        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._last_session_id: Optional[str] = None

    def _build_endpoint(self, base_url: Optional[str] = None) -> str:
        """Build ingest endpoint URL from base URL."""
        resolved_base_url = (
            base_url
            or os.getenv("RESPAN_BASE_URL")
            or os.getenv("KEYWORDSAI_BASE_URL")
        )
        return resolve_export_endpoint(base_url=resolved_base_url)

    def set_endpoint(self, endpoint: str) -> None:
        """Dynamically override the ingest endpoint."""
        self.endpoint = endpoint

    def create_hooks(
        self,
        existing_hooks: Optional[Dict[str, List[HookMatcher]]] = None,
    ) -> Dict[str, List[HookMatcher]]:
        """Return a hook map that includes Respan instrumentation hooks."""
        merged_hooks = dict(existing_hooks or {})
        self._append_hook(
            hooks=merged_hooks,
            event_name="UserPromptSubmit",
            matcher=None,
            callback=self._on_user_prompt_submit,
        )
        self._append_hook(
            hooks=merged_hooks,
            event_name="PreToolUse",
            matcher=None,
            callback=self._on_pre_tool_use,
        )
        self._append_hook(
            hooks=merged_hooks,
            event_name="PostToolUse",
            matcher=None,
            callback=self._on_post_tool_use,
        )
        self._append_hook(
            hooks=merged_hooks,
            event_name="SubagentStop",
            matcher=None,
            callback=self._on_subagent_stop,
        )
        self._append_hook(
            hooks=merged_hooks,
            event_name="Stop",
            matcher=None,
            callback=self._on_stop,
        )
        return merged_hooks

    def with_options(
        self,
        options: Optional[ClaudeAgentOptions] = None,
    ) -> ClaudeAgentOptions:
        """Attach Respan hooks to SDK options."""
        instrumented_options = options or ClaudeAgentOptions()
        existing_hooks = instrumented_options.hooks or {}
        instrumented_options.hooks = self.create_hooks(existing_hooks=existing_hooks)
        return instrumented_options

    async def query(
        self,
        prompt: Union[str, AsyncIterable[Dict[str, Any]]],
        options: Optional[ClaudeAgentOptions] = None,
    ) -> AsyncGenerator[Any, None]:
        """
        Wrapped Claude query that auto-tracks all streamed messages.

        This keeps user code close to native SDK usage while ensuring
        hooks and message events are exported to Respan.
        """
        instrumented_options = self.with_options(options=options)
        active_session_id: Optional[str] = None

        async for message in query(prompt=prompt, options=instrumented_options):
            if isinstance(message, SystemMessage):
                detected_session_id = self._extract_session_id_from_system_message(
                    system_message=message
                )
                if detected_session_id:
                    active_session_id = detected_session_id
            if isinstance(message, ResultMessage):
                active_session_id = message.session_id
            await self.track_message(message=message, session_id=active_session_id)
            yield message

    async def track_message(
        self,
        message: Any,
        session_id: Optional[str] = None,
    ) -> None:
        """Track a single SDK message and export equivalent Respan spans."""
        if isinstance(message, SystemMessage):
            self._handle_system_message(
                system_message=message,
                explicit_session_id=session_id,
            )
            return

        if isinstance(message, AssistantMessage):
            self._handle_assistant_message(
                assistant_message=message,
                explicit_session_id=session_id,
            )
            return

        if isinstance(message, ResultMessage):
            self._handle_result_message(result_message=message)
            return

        if isinstance(message, UserMessage):
            self._handle_user_message(
                user_message=message,
                explicit_session_id=session_id,
            )
            return

        if isinstance(message, StreamEvent):
            self._handle_stream_event(stream_event=message)

    def _append_hook(
        self,
        hooks: Dict[str, List[HookMatcher]],
        event_name: str,
        matcher: Optional[str],
        callback: Any,
    ) -> None:
        event_hooks = list(hooks.get(event_name, []))
        callback_name = getattr(callback, "__name__", None)
        for existing_hook in event_hooks:
            existing_matcher = getattr(existing_hook, "matcher", None)
            existing_callbacks = getattr(existing_hook, "hooks", [])
            if existing_matcher != matcher:
                continue
            for existing_callback in existing_callbacks:
                existing_callback_name = getattr(existing_callback, "__name__", None)
                if existing_callback_name == callback_name:
                    return

        hook_matcher = HookMatcher(matcher=matcher, hooks=[callback])
        event_hooks.append(hook_matcher)
        hooks[event_name] = event_hooks

    async def _on_user_prompt_submit(
        self,
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        session_id = self._extract_session_id_from_hook_input(input_data=input_data)
        prompt = input_data.get("prompt")
        trace_name = self._build_trace_name_from_prompt(prompt=prompt)
        session_state = self._ensure_session_state(
            session_id=session_id,
            trace_name=trace_name,
        )

        now = self._utc_now()
        payload = self._create_payload(
            session_state=session_state,
            span_unique_id=str(uuid.uuid4()),
            span_parent_id=session_state["trace_id"],
            span_name="user_prompt",
            log_type=LOG_TYPE_TASK,
            start_time=now,
            timestamp=now,
            input_value=prompt,
            output_value=None,
            metadata={"hook_event_name": "UserPromptSubmit"},
            status_code=200,
        )
        self._send_payloads(payloads=[payload])
        return {}

    async def _on_pre_tool_use(
        self,
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        session_id = self._extract_session_id_from_hook_input(input_data=input_data)
        session_state = self._ensure_session_state(
            session_id=session_id,
            trace_name=None,
        )

        resolved_tool_use_id = str(
            input_data.get("tool_use_id") or tool_use_id or str(uuid.uuid4())
        )
        session_state["pending_tools"][resolved_tool_use_id] = {
            "span_unique_id": str(uuid.uuid4()),
            "started_at": self._utc_now(),
            "tool_name": input_data.get("tool_name") or "tool",
            "tool_input": input_data.get("tool_input"),
        }
        return {}

    async def _on_post_tool_use(
        self,
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        session_id = self._extract_session_id_from_hook_input(input_data=input_data)
        session_state = self._ensure_session_state(
            session_id=session_id,
            trace_name=None,
        )
        resolved_tool_use_id = str(
            input_data.get("tool_use_id") or tool_use_id or str(uuid.uuid4())
        )

        pending_tool_state = session_state["pending_tools"].pop(
            resolved_tool_use_id,
            None,
        )
        now = self._utc_now()
        if pending_tool_state is None:
            pending_tool_state = {
                "span_unique_id": str(uuid.uuid4()),
                "started_at": now,
                "tool_name": input_data.get("tool_name") or "tool",
                "tool_input": input_data.get("tool_input"),
            }

        tool_name = str(input_data.get("tool_name") or pending_tool_state["tool_name"])
        payload = self._create_payload(
            session_state=session_state,
            span_unique_id=pending_tool_state["span_unique_id"],
            span_parent_id=session_state["trace_id"],
            span_name=tool_name,
            log_type=LOG_TYPE_TOOL,
            start_time=pending_tool_state["started_at"],
            timestamp=now,
            input_value=pending_tool_state.get("tool_input"),
            output_value=input_data.get("tool_response"),
            metadata={
                "hook_event_name": "PostToolUse",
                "tool_use_id": resolved_tool_use_id,
            },
            span_tools=[tool_name],
            status_code=200,
        )
        self._send_payloads(payloads=[payload])
        return {}

    async def _on_subagent_stop(
        self,
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        session_id = self._extract_session_id_from_hook_input(input_data=input_data)
        session_state = self._ensure_session_state(
            session_id=session_id,
            trace_name=None,
        )
        now = self._utc_now()
        payload = self._create_payload(
            session_state=session_state,
            span_unique_id=str(uuid.uuid4()),
            span_parent_id=session_state["trace_id"],
            span_name="subagent_stop",
            log_type=LOG_TYPE_TASK,
            start_time=now,
            timestamp=now,
            metadata={
                "hook_event_name": "SubagentStop",
                "agent_id": input_data.get("agent_id"),
                "agent_type": input_data.get("agent_type"),
            },
            status_code=200,
        )
        self._send_payloads(payloads=[payload])
        return {}

    async def _on_stop(
        self,
        input_data: Dict[str, Any],
        tool_use_id: Optional[str],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {}

    def _handle_system_message(
        self,
        system_message: SystemMessage,
        explicit_session_id: Optional[str],
    ) -> None:
        session_id = explicit_session_id or self._extract_session_id_from_system_message(
            system_message=system_message
        )
        if not session_id:
            return

        self._last_session_id = session_id
        self._ensure_session_state(session_id=session_id, trace_name=None)

    def _handle_user_message(
        self,
        user_message: UserMessage,
        explicit_session_id: Optional[str],
    ) -> None:
        session_id = explicit_session_id or self._last_session_id
        if not session_id:
            return
        session_state = self._ensure_session_state(
            session_id=session_id,
            trace_name=None,
        )

        message_text = self._extract_user_text(user_message=user_message)
        if not message_text:
            return

        now = self._utc_now()
        payload = self._create_payload(
            session_state=session_state,
            span_unique_id=str(uuid.uuid4()),
            span_parent_id=session_state["trace_id"],
            span_name="user_message",
            log_type=LOG_TYPE_TASK,
            start_time=now,
            timestamp=now,
            input_value=message_text,
            output_value=None,
            metadata={"source": "stream_user_message"},
            status_code=200,
        )
        self._send_payloads(payloads=[payload])

    def _handle_assistant_message(
        self,
        assistant_message: AssistantMessage,
        explicit_session_id: Optional[str],
    ) -> None:
        session_id = explicit_session_id or self._last_session_id
        if not session_id:
            return
        session_state = self._ensure_session_state(
            session_id=session_id,
            trace_name=None,
        )
        extracted_content = self._extract_assistant_content(assistant_message=assistant_message)
        if (
            not extracted_content["output_text"]
            and not extracted_content["tool_calls"]
            and not extracted_content["reasoning"]
        ):
            return

        completion_message = None
        completion_messages = None
        if extracted_content["output_text"]:
            completion_message = Message(
                role="assistant",
                content=extracted_content["output_text"],
            )
            completion_messages = [completion_message]

        tool_names = []
        for tool_call in extracted_content["tool_calls"]:
            tool_name = tool_call.get("name")
            if tool_name:
                tool_names.append(str(tool_name))

        now = self._utc_now()
        payload = self._create_payload(
            session_state=session_state,
            span_unique_id=str(uuid.uuid4()),
            span_parent_id=session_state["trace_id"],
            span_name="assistant_message",
            log_type=LOG_TYPE_GENERATION,
            start_time=now,
            timestamp=now,
            input_value=None,
            output_value=extracted_content["output_text"],
            model=assistant_message.model,
            metadata={
                "reasoning": extracted_content["reasoning"] or None,
                "source": "stream_assistant_message",
            },
            span_tools=tool_names or None,
            tool_calls=extracted_content["tool_calls"] or None,
            completion_message=completion_message,
            completion_messages=completion_messages,
            status_code=200,
        )
        self._send_payloads(payloads=[payload])

    def _handle_result_message(self, result_message: ResultMessage) -> None:
        session_state = self._ensure_session_state(
            session_id=result_message.session_id,
            trace_name=None,
        )

        usage = result_message.usage or {}
        prompt_tokens = self._coerce_int(
            value=usage.get("input_tokens") or usage.get("prompt_tokens")
        )
        completion_tokens = self._coerce_int(
            value=usage.get("output_tokens") or usage.get("completion_tokens")
        )
        total_request_tokens = self._coerce_int(value=usage.get("total_tokens"))
        if total_request_tokens is None and (
            prompt_tokens is not None or completion_tokens is not None
        ):
            total_request_tokens = (prompt_tokens or 0) + (completion_tokens or 0)

        prompt_cache_hit_tokens = self._coerce_int(
            value=usage.get("cache_read_input_tokens")
        )
        prompt_cache_creation_tokens = self._coerce_int(
            value=usage.get("cache_creation_input_tokens")
        )

        now = self._utc_now()
        error_message = None
        status_code = 200
        if result_message.is_error:
            error_message = f"agent_result_error:{result_message.subtype}"
            status_code = 500

        payload = self._create_payload(
            session_state=session_state,
            span_unique_id=str(uuid.uuid4()),
            span_parent_id=session_state["trace_id"],
            span_name=f"result:{result_message.subtype}",
            log_type=LOG_TYPE_AGENT,
            start_time=now,
            timestamp=now,
            input_value=None,
            output_value=result_message.result or result_message.subtype,
            model=None,
            metadata={
                "duration_ms": result_message.duration_ms,
                "duration_api_ms": result_message.duration_api_ms,
                "num_turns": result_message.num_turns,
                "total_cost_usd": result_message.total_cost_usd,
                "structured_output": result_message.structured_output,
            },
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_request_tokens=total_request_tokens,
            prompt_cache_hit_tokens=prompt_cache_hit_tokens,
            prompt_cache_creation_tokens=prompt_cache_creation_tokens,
            status_code=status_code,
            error_message=error_message,
        )
        self._send_payloads(payloads=[payload])
        session_state["pending_tools"] = {}

    def _handle_stream_event(self, stream_event: StreamEvent) -> None:
        self._last_session_id = stream_event.session_id

    def _extract_assistant_content(self, assistant_message: AssistantMessage) -> Dict[str, Any]:
        return extract_assistant_content(assistant_message=assistant_message)

    def _extract_user_text(self, user_message: UserMessage) -> Optional[str]:
        return extract_user_text(user_message=user_message)

    def _extract_session_id_from_system_message(
        self,
        system_message: SystemMessage,
    ) -> Optional[str]:
        return extract_session_id_from_system_message(system_message=system_message)

    def _extract_session_id_from_hook_input(self, input_data: Dict[str, Any]) -> str:
        raw_session_id = input_data.get("session_id") or input_data.get("sessionId")
        if raw_session_id:
            normalized_session_id = str(raw_session_id)
            self._last_session_id = normalized_session_id
            return normalized_session_id

        if self._last_session_id:
            return self._last_session_id
        generated_session_id = str(uuid.uuid4())
        self._last_session_id = generated_session_id
        return generated_session_id

    def _build_trace_name_from_prompt(self, prompt: Any) -> Optional[str]:
        return build_trace_name_from_prompt(prompt=prompt)

    def _ensure_session_state(
        self,
        session_id: str,
        trace_name: Optional[str],
    ) -> Dict[str, Any]:
        existing_state = self._sessions.get(session_id)
        if existing_state is not None:
            if (
                trace_name
                and existing_state["trace_name"].startswith("anthropic-session-")
            ):
                existing_state["trace_name"] = trace_name
            self._last_session_id = session_id
            return existing_state

        resolved_trace_name = trace_name or f"anthropic-session-{session_id[:12]}"
        now = self._utc_now()
        state = {
            "session_id": session_id,
            "trace_id": session_id,
            "trace_name": resolved_trace_name,
            "started_at": now,
            "pending_tools": {},
            "root_emitted": False,
        }
        self._sessions[session_id] = state
        self._last_session_id = session_id
        self._emit_root_span(session_state=state)
        return state

    def _emit_root_span(self, session_state: Dict[str, Any]) -> None:
        if session_state["root_emitted"]:
            return
        root_payload = self._create_payload(
            session_state=session_state,
            span_unique_id=session_state["trace_id"],
            span_parent_id=None,
            span_name=session_state["trace_name"],
            log_type=LOG_TYPE_AGENT,
            start_time=session_state["started_at"],
            timestamp=session_state["started_at"],
            input_value=None,
            output_value=None,
            metadata={"source": "session_root"},
            status_code=200,
        )
        self._send_payloads(payloads=[root_payload])
        session_state["root_emitted"] = True

    def _create_payload(
        self,
        session_state: Dict[str, Any],
        span_unique_id: str,
        span_parent_id: Optional[str],
        span_name: str,
        log_type: str,
        start_time: Optional[datetime],
        timestamp: Optional[datetime],
        input_value: Any = None,
        output_value: Any = None,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        span_tools: Optional[List[str]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        completion_message: Optional[Message] = None,
        completion_messages: Optional[List[Message]] = None,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_request_tokens: Optional[int] = None,
        prompt_cache_hit_tokens: Optional[int] = None,
        prompt_cache_creation_tokens: Optional[int] = None,
        status_code: int = 200,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        resolved_start_time = start_time or self._utc_now()
        resolved_timestamp = timestamp or resolved_start_time
        latency_seconds = max(
            (resolved_timestamp - resolved_start_time).total_seconds(),
            0.0,
        )

        payload = RespanTextLogParams(
            trace_unique_id=session_state["trace_id"],
            span_unique_id=span_unique_id,
            span_parent_id=span_parent_id,
            trace_name=session_state["trace_name"],
            session_identifier=session_state["session_id"],
            span_name=span_name,
            span_workflow_name=session_state["trace_name"],
            log_type=log_type,
            start_time=resolved_start_time,
            timestamp=resolved_timestamp,
            latency=latency_seconds,
            status_code=status_code,
            error_bit=1 if error_message else 0,
            error_message=error_message,
            input=self._serialize_value(value=input_value),
            output=self._serialize_value(value=output_value),
            model=model,
            metadata=self._serialize_metadata(value=metadata),
            span_tools=span_tools,
            tool_calls=self._serialize_tool_calls(value=tool_calls),
            completion_message=completion_message,
            completion_messages=completion_messages,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_request_tokens=total_request_tokens,
            prompt_cache_hit_tokens=prompt_cache_hit_tokens,
            prompt_cache_creation_tokens=prompt_cache_creation_tokens,
        )
        return payload.model_dump(mode="json", exclude_none=True)

    def _serialize_metadata(self, value: Any) -> Optional[Dict[str, Any]]:
        return serialize_metadata(value=value)

    def _serialize_tool_calls(self, value: Any) -> Optional[List[Dict[str, Any]]]:
        return serialize_tool_calls(value=value)

    def _serialize_value(self, value: Any) -> Any:
        return serialize_value(value=value)

    def _send_payloads(self, payloads: List[Dict[str, Any]]) -> None:
        if not payloads:
            return

        if not self.api_key:
            logger.warning("Respan API key is not set; skipping exporter upload")
            return

        request_body = json.dumps({"data": payloads}, default=str).encode("utf-8")
        request_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        attempt = 0
        delay_seconds = self.base_delay_seconds

        while True:
            attempt += 1
            request = urllib.request.Request(
                url=self.endpoint,
                data=request_body,
                headers=request_headers,
                method="POST",
            )
            try:
                with urllib.request.urlopen(
                    url=request,
                    timeout=self.timeout_seconds,
                ) as response:
                    if response.status < 300:
                        return
                    response_body = response.read().decode("utf-8", errors="replace")
                    if 400 <= response.status < 500:
                        logger.error(
                            "Respan export client error %s: %s",
                            response.status,
                            response_body,
                        )
                        return
                    logger.warning(
                        "Respan export server error %s: %s",
                        response.status,
                        response_body,
                    )
            except urllib.error.HTTPError as error:
                error_body = error.read().decode("utf-8", errors="replace")
                if 400 <= error.code < 500:
                    logger.error(
                        "Respan export client error %s: %s",
                        error.code,
                        error_body,
                    )
                    return
                logger.warning(
                    "Respan export server error %s: %s",
                    error.code,
                    error_body,
                )
            except urllib.error.URLError as error:
                logger.warning("Respan export network error: %s", error)

            if attempt >= self.max_retries:
                logger.error("Respan export failed after %s attempts", attempt)
                return

            jitter_seconds = random.uniform(0, 0.1 * delay_seconds)
            time.sleep(delay_seconds + jitter_seconds)
            delay_seconds = min(delay_seconds * 2, self.max_delay_seconds)

    def _coerce_int(self, value: Any) -> Optional[int]:
        return coerce_int(value=value)

    def _utc_now(self) -> datetime:
        return utc_now()


class RespanSpanExporter(RespanAnthropicAgentsExporter):
    """Compatibility alias that mirrors OpenAI exporter naming."""


def instrument_options(
    exporter: RespanAnthropicAgentsExporter,
    options: Optional[ClaudeAgentOptions] = None,
) -> ClaudeAgentOptions:
    """Helper for attaching Respan hooks onto existing ClaudeAgentOptions."""
    return exporter.with_options(options=options)
