"""
Basic usage example for respan-exporter-anthropic-agents.

This script demonstrates three ways to use the exporter:
  1. Hooks-based (automatic) - exporter attaches to SDK hooks
  2. Manual tracking          - you call track_message() on each event
  3. Wrapped query            - exporter.query() does both

Prerequisites:
  pip install claude-agent-sdk respan-sdk respan-exporter-anthropic-agents

Environment variables:
  RESPAN_API_KEY   (or KEYWORDSAI_API_KEY) - your Respan ingest key
  ANTHROPIC_API_KEY                        - your Anthropic API key

Run:
  python examples/basic_usage.py
"""

import asyncio
import os

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
    query,
)

from respan_exporter_anthropic_agents import RespanAnthropicAgentsExporter
from respan_exporter_anthropic_agents.utils import (
    extract_session_id_from_system_message,
)


async def example_hooks_based() -> None:
    """Attach exporter hooks to ClaudeAgentOptions and run a query."""
    print("\n=== Example 1: Hooks-based (automatic) ===\n")

    exporter = RespanAnthropicAgentsExporter()  # reads RESPAN_API_KEY from env

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        max_turns=1,
    )
    # Attach exporter hooks — tool use, prompts, subagent stops are all captured
    options = exporter.with_options(options=options)

    session_id = None
    async for message in query(prompt="What is 2 + 2?", options=options):
        if isinstance(message, SystemMessage):
            session_id = extract_session_id_from_system_message(
                system_message=message
            )
            print(f"  System message (session_id={session_id})")
        elif isinstance(message, ResultMessage):
            print(f"  Result: subtype={message.subtype}, turns={message.num_turns}")
        else:
            print(f"  {type(message).__name__}")

    print(f"\n  Traces exported to Respan under session {session_id}")


async def example_manual_tracking() -> None:
    """Manually call track_message() on each SDK event."""
    print("\n=== Example 2: Manual tracking ===\n")

    exporter = RespanAnthropicAgentsExporter()

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        max_turns=1,
    )

    session_id = None
    async for message in query(prompt="Say hello", options=options):
        # Extract session ID for grouping
        if isinstance(message, SystemMessage):
            session_id = extract_session_id_from_system_message(
                system_message=message
            )
        if isinstance(message, ResultMessage):
            session_id = message.session_id

        # Export every message
        await exporter.track_message(message=message, session_id=session_id)
        print(f"  Tracked: {type(message).__name__}")

    print(f"\n  All messages exported under session {session_id}")


async def example_wrapped_query() -> None:
    """Use exporter.query() which handles both hooks and tracking."""
    print("\n=== Example 3: Wrapped query (simplest) ===\n")

    exporter = RespanAnthropicAgentsExporter()

    async for message in exporter.query(
        prompt="What day is today?",
        options=ClaudeAgentOptions(
            permission_mode="bypassPermissions",
            max_turns=1,
        ),
    ):
        print(f"  {type(message).__name__}")

    print("\n  Done — all traces exported automatically")


async def main() -> None:
    api_key = os.getenv("RESPAN_API_KEY") or os.getenv("KEYWORDSAI_API_KEY")
    if not api_key:
        print("Set RESPAN_API_KEY (or KEYWORDSAI_API_KEY) to export traces.")
        print("Running anyway — exporter will warn and skip uploads.\n")

    await example_hooks_based()
    await example_manual_tracking()
    await example_wrapped_query()


if __name__ == "__main__":
    asyncio.run(main())
