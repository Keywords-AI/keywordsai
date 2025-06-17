try:
    from keywordsai_exporter_openai_agents import (
        KeywordsAITraceProcessor,
        KeywordsAISpanExporter
    )
    AGENTS_AVAILABLE = True
except ImportError:
    raise ImportError(
        "OpenAI agents integration requires additional dependencies. "
        "Please install them with: pip install 'keywordsai-tracing[openai-agents]'"
    )