"""Keywords AI + Braintrust quickstart.

This mirrors the real-send smoke test:
1) installs the KeywordsAIExporter as Braintrust's background logger
2) logs a parent + child span
3) flushes to send to Keywords AI

Run:
    KEYWORDSAI_API_KEY="..." poetry run python examples/quickstart.py
"""

import os
import time

import braintrust

from keywordsai_exporter_braintrust import KeywordsAIExporter


def main() -> None:
    api_key = os.getenv("KEYWORDSAI_API_KEY")
    if not api_key:
        raise RuntimeError("KEYWORDSAI_API_KEY not set")

    exporter = KeywordsAIExporter(api_key=api_key, raise_on_error=True)
    with exporter:
        logger = braintrust.init_logger(
            project="KeywordsAI Braintrust Quickstart",
            project_id="keywordsai-braintrust-quickstart",
            api_key=braintrust.logger.TEST_API_KEY,
            async_flush=False,
            set_current=False,
        )

        with logger.start_span(name="keywordsai-braintrust-parent", type="task") as root_span:
            with root_span.start_span(name="keywordsai-braintrust-child", type="chat") as child_span:
                time.sleep(0.25)
                child_span.log(
                    input=[{"role": "user", "content": "Hello from Braintrust quickstart"}],
                    output="Hello from Keywords AI!",
                    metrics={"prompt_tokens": 5, "completion_tokens": 7},
                    metadata={"model": "gpt-4o-mini"},
                )

        logger.flush()

    print("✓ Sent Braintrust trace to Keywords AI (check Traces page).")


if __name__ == "__main__":
    main()

