import {
  OpenAITracingExporter,
  Trace,
  Span,
  OpenAITracingExporterOptions,
} from "@openai/agents";
import {
  KeywordsAIParams,
  KeywordsPayloadSchema,
} from "@keywordsai/keywordsai-sdk";

export class KeywordsAIOpenAIAgentsTracingExporter extends OpenAITracingExporter {
  constructor(options?: Partial<OpenAITracingExporterOptions>) {
    super(options);
  }
  export(items: (Trace | Span<any>)[], signal?: AbortSignal): Promise<void> {
    return super.export(items, signal);
  }
}
