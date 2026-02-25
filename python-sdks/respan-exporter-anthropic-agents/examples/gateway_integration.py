"""
Gateway integration example for respan-exporter-anthropic-agents.

Routes Claude Agent SDK traffic through the Respan gateway instead of
hitting Anthropic directly. This means you only need a Respan API key —
no separate Anthropic key required.

Prerequisites:
  pip install claude-agent-sdk respan-sdk respan-exporter-anthropic-agents

Environment variables (required):
  RESPAN_API_KEY   (or KEYWORDSAI_API_KEY) - your Respan key (used for both
                                              gateway auth and trace ingest)

Environment variables (optional):
  RESPAN_BASE_URL  - gateway base URL (default: https://api.respan.ai)

Run:
  python examples/gateway_integration.py
"""

import asyncio
import os
import sys

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


async def main() -> None:
    respan_api_key = os.getenv("RESPAN_API_KEY") or os.getenv("KEYWORDSAI_API_KEY")
    if not respan_api_key:
        print("ERROR: Set RESPAN_API_KEY (or KEYWORDSAI_API_KEY)")
        sys.exit(1)

    base_url = (
        os.getenv("RESPAN_BASE_URL")
        or os.getenv("KEYWORDSAI_BASE_URL")
        or "https://api.respan.ai"
    ).rstrip("/")

    print(f"Gateway base URL: {base_url}")
    print(f"API key: {respan_api_key[:8]}...")

    # Exporter sends traces to the ingest endpoint
    exporter = RespanAnthropicAgentsExporter(
        api_key=respan_api_key,
        base_url=base_url,
    )

    # Route Claude SDK through the Respan gateway
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        max_turns=1,
        env={
            "ANTHROPIC_BASE_URL": base_url,
            "ANTHROPIC_AUTH_TOKEN": respan_api_key,
            "ANTHROPIC_API_KEY": respan_api_key,
        },
    )
    options = exporter.with_options(options=options)

    print("\nSending query through gateway...\n")

    session_id = None
    result = None
    async for message in query(
        prompt="Reply with exactly: gateway_ok",
        options=options,
    ):
        if isinstance(message, SystemMessage):
            session_id = extract_session_id_from_system_message(
                system_message=message
            )
        if isinstance(message, ResultMessage):
            session_id = message.session_id
            result = message

        await exporter.track_message(message=message, session_id=session_id)
        print(f"  {type(message).__name__}")

    if result:
        print(f"\nResult: subtype={result.subtype}, turns={result.num_turns}")
        print(f"Usage: {result.usage}")

    print(f"\nTraces exported to Respan under session {session_id}")
    print(f"View at: https://platform.respan.ai/traces/{session_id}")


if __name__ == "__main__":
    asyncio.run(main())
