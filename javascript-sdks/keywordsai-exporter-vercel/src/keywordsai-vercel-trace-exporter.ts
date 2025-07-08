import { ExportResult, ExportResultCode } from "@opentelemetry/core";
import { ReadableSpan, SpanExporter } from "@opentelemetry/sdk-trace-base";
import {
  KeywordsPayload,
  KeywordsPayloadSchema,
  LogType,
} from "@keywordsai/keywordsai-sdk";
import { VERCEL_SPAN_TO_KEYWORDS_LOG_TYPE } from "./constants/index.js";

/**
 * This is a Vercel AI SDK trace exporter that sends traces to KeywordsAI.
 * It is used to export traces from Vercel AI SDK to KeywordsAI.
 * Next JS telemetry reference: https://vercel.com/docs/otel
 * Langfuse integration: https://ai-sdk.dev/providers/observability/langfuse
 * @param params - The parameters for the exporter.
 * @param params.debug - Whether to enable debug mode.
 * @param params.apiKey - The API key for the exporter.
 * @param params.baseUrl - The base URL for the exporter.
 *
 * @example
 * ```ts
 * const exporter = new KeywordsAIExporter({
 *   apiKey: "your-api-key",
 *   baseUrl: "https://api.keywordsai.co/api",
 * });
 */
export class KeywordsAIExporter implements SpanExporter {
  private readonly debug: boolean;
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly url: string;
  private resolveURL(baseURL: string|undefined) {
    if (!baseURL) {
      return "https://api.keywordsai.co/api/integrations/v1/traces/ingest";
    }
    if (baseURL.endsWith("/api")) {
      return baseURL + "/integrations/v1/traces/ingest";
    }
    return baseURL + "/api/integrations/v1/traces/ingest";
  }
  constructor(
    params: { debug?: boolean; apiKey?: string; baseUrl?: string } = {}
  ) {
    this.debug = params.debug ?? false;
    this.apiKey = params.apiKey ?? (process.env.KEYWORDSAI_API_KEY || "");
    if (!this.apiKey) {
      throw new Error("KEYWORDSAI_API_KEY is required");
    }
    this.baseUrl = params.baseUrl ?? "https://api.keywordsai.co/api";
    this.url = this.resolveURL(this.baseUrl);
  }

  async export(
    spans: ReadableSpan[],
    resultCallback: (result: ExportResult) => void
  ): Promise<void> {
    try {
      const sortedSpans = spans
        .slice()
        .sort((a, b) => this.compareHrTime(a.startTime, b.startTime));

      // Filter for AI SDK spans instead of just generation spans
      const aiSdkSpans = sortedSpans.filter((span) => this.isAiSdkSpan(span));

      if (aiSdkSpans.length === 0) {
        this.logDebug("No AI SDK spans found");
        resultCallback({ code: ExportResultCode.SUCCESS });
        return;
      }

      // Deduplicate spans - prefer doStream/doGenerate over their parent spans
      const deduplicatedSpans = this.deduplicateSpans(aiSdkSpans);
      this.logDebug(
        `Filtered ${aiSdkSpans.length} spans to ${deduplicatedSpans.length} after deduplication`
      );

      // Prepare all payloads
      const allPayloads: KeywordsPayload[] = [];

      for (const span of deduplicatedSpans) {
        try {
          this.logDebug("Creating payload for span", span);
          const rawPayload = await this.createPayload(span, sortedSpans);
          try {
            const validatedPayload = KeywordsPayloadSchema.parse(rawPayload);
            allPayloads.push(validatedPayload);
          } catch (error) {
            this.logDebug("Payload validation failed", error);
            // If validation fails, include the raw payload in full_request
            try {
              const fallbackPayload = KeywordsPayloadSchema.parse({
                ...rawPayload,
                full_request: rawPayload,
              });
              allPayloads.push(fallbackPayload);
            } catch (fallbackError) {
              this.logDebug("Fallback validation also failed", fallbackError);
              // Last resort - create minimal valid payload with error info
              const minimalPayload = KeywordsPayloadSchema.parse({
                model: "unknown",
                prompt_messages: [
                  { role: "system", content: "Error processing span" },
                ],
                prompt_tokens: 0,
                timestamp: this.formatTimestamp(span.endTime),
                customer_identifier: "default_user",
                stream: false,
                metadata: {
                  error: String(error),
                  span_id: span.spanContext().spanId,
                  trace_id: span.spanContext().traceId,
                  span_name: span.name,
                },
              });
              allPayloads.push(minimalPayload);
            }
          }
        } catch (error) {
          this.logDebug("Failed to create payload for span", error);
        }
      }
      // Send all payloads in one request
      if (allPayloads.length > 0) {
        await this.sendToKeywords(allPayloads);
      }

      resultCallback({ code: ExportResultCode.SUCCESS });
    } catch (err) {
      this.logDebug("Export failed", err);
      resultCallback({
        code: ExportResultCode.FAILED,
        error: err instanceof Error ? err : new Error(String(err)),
      });
    }
  }

  private async createPayload(
    span: ReadableSpan,
    relatedSpans: ReadableSpan[]
  ): Promise<KeywordsPayload> {
    const metadata = this.parseMetadata(span);
    const isError = span.status.code !== 0;
    const model = this.parseModel(span);
    const toolCalls = this.parseToolCalls(span);
    const messages = this.parseCompletionMessages(span, toolCalls);

    const payload: KeywordsPayload = {
      model,
      start_time: this.formatTimestamp(span.startTime),
      timestamp: this.formatTimestamp(span.endTime),
      prompt_messages: this.parsePromptMessages(span),
      completion_message: messages[0],
      customer_identifier: metadata.userId || "default_user",
      thread_identifier: metadata.userId,
      prompt_tokens: this.parsePromptTokens(span),
      completion_tokens: this.parseCompletionTokens(span),
      cost: this.parseCost(span),
      generation_time: this.parseGenerationTime(span),
      latency: this.calculateLatency(span),
      ttft: this.parseTtft(span),
      metadata: {
        ...metadata,
        span_type: span.name, // Add span type to metadata
      },
      environment: process.env.NODE_ENV || "prod",
      time_to_first_token: this.parseTimeToFirstToken(span),
      trace_unique_id: span.spanContext().traceId,
      span_unique_id: span.spanContext().spanId,
      span_name: span.name,
      span_parent_id:
        span.attributes["span.parent_id"]?.toString() ||
        span.attributes["parentSpanId"]?.toString(),
      span_path: span.attributes["ai.path"]?.toString(),
      stream: span.name.includes("doStream"),
      status_code: isError ? 500 : 200,
      warnings: this.parseWarnings(span),
      error_message: span.status.message || "",
      type: this.parseType(span),
      log_type: this.parseLogType(span),
      is_test: process.env.NODE_ENV === "development",
      posthog_integration: process.env.POSTHOG_API_KEY
        ? {
            posthog_api_key: process.env.POSTHOG_API_KEY,
            posthog_base_url: "https://us.i.posthog.com",
          }
        : undefined,
      tool_choice: this.parseToolChoice(span),
      tools: this.parseTools(span),
      tool_calls: toolCalls,
      field_name: "data: ",
      delimiter: "\n\n",
      disable_log: false,
      request_breakdown: false,
      disable_fallback: false,
      ...this.parseCustomerParams(span),
    };

    return payload;
  }

  // Helper method to parse tool calls from span attributes
  private parseToolCalls(span: ReadableSpan): any[] | undefined {
    try {
      // Check for tool calls in various attribute formats
      const toolCallAttributes = [
        "ai.response.toolCalls",
        "ai.toolCall",
        "ai.toolCalls",
      ];

      // Try to find tool calls in any of the standard attribute locations
      for (const attr of toolCallAttributes) {
        if (span.attributes[attr]) {
          const rawData = span.attributes[attr];
          if (!rawData) continue;

          // Handle both string and object formats
          let parsed;
          try {
            parsed =
              typeof rawData === "string" ? JSON.parse(rawData) : rawData;
          } catch (e) {
            this.logDebug(`Failed to parse ${attr}:`, e);
            continue;
          }

          // Standardize to array
          const toolCalls = Array.isArray(parsed) ? parsed : [parsed];

          // Process each tool call with minimal transformation
          return toolCalls.map((call) => {
            // Ensure we have a valid object
            if (!call || typeof call !== "object") {
              return { type: "function" };
            }

            // Make a copy to avoid mutating the original
            const result = { ...call };

            // Ensure the object has a type
            if (!result.type) {
              result.type = "function";
            }

            // Handle ID normalization (only if needed)
            if (!result.id && (result.toolCallId || result.tool_call_id)) {
              result.id = result.toolCallId || result.tool_call_id;
            }

            return result;
          });
        }
      }

      // If we didn't find tool calls in the standard places, check for individual attributes
      if (
        span.attributes["ai.toolCall.id"] ||
        span.attributes["ai.toolCall.name"] ||
        span.attributes["ai.toolCall.args"]
      ) {
        // Build a tool call object from individual attributes
        const toolCall: Record<string, any> = { type: "function" };

        // Copy all tool call attributes
        for (const [key, value] of Object.entries(span.attributes)) {
          if (key.startsWith("ai.toolCall.")) {
            const propName = key.replace("ai.toolCall.", "");
            toolCall[propName] = value;
          }
        }

        return [toolCall];
      }

      return undefined;
    } catch (error) {
      this.logDebug("Error parsing tool calls:", error);
      return undefined;
    }
  }

  private parseCompletionMessages(
    span: ReadableSpan,
    toolCalls?: any[]
  ): any[] {
    const message = {
      role: "assistant",
      content: String(span.attributes["ai.response.text"] || span.attributes["ai.response.object"].response || ""),
      ...(toolCalls && toolCalls.length > 0 && { tool_calls: toolCalls }),
    };

    // Check if there's a tool result to add as a separate message
    const toolResults: any[] = [];

    if (span.attributes["ai.toolCall.result"]) {
      toolResults.push({
        role: "tool",
        tool_call_id: String(span.attributes["ai.toolCall.id"] || ""),
        content: String(span.attributes["ai.toolCall.result"] || ""),
      });
    }

    return toolResults.length > 0 ? [message, ...toolResults] : [message];
  }

  private calculateLatency(span: ReadableSpan): number {
    return span.duration[0] / 1e9 + span.duration[1] / 1e9;
  }

  private async sendToKeywords(payloads: KeywordsPayload[]): Promise<void> {
    if (payloads.length === 0) {
      this.logDebug("No payloads to send");
      return;
    }

    try {
      this.logDebug(`Sending ${payloads.length} payloads to Keywords`);

      const response = await fetch(this.url, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${this.apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payloads),
      });

      if (!response.ok) {
        const text = await response.text();
        this.logDebug("Failed to send to Keywords", text);
        throw new Error(`Failed to send to Keywords: ${response.statusText}`);
      } else {
        this.logDebug("Successfully sent payloads to Keywords");
      }
    } catch (error) {
      this.logDebug("Error sending to Keywords", error);
      throw error;
    }
  }

  private parseModel(span: ReadableSpan): string {
    const model = String(
      span.attributes["ai.model.id"] || "unknown"
    ).toLowerCase();

    if (model.includes("gemini-2.0-flash-001")) {
      return "gemini/gemini-2.0-flash";
    }

    if (model.includes("gemini-2.0-pro")) {
      return "gemini/gemini-2.0-pro-exp-02-05";
    }

    if (model.includes("claude-3-5-sonnet")) {
      return "claude-3-5-sonnet-20241022";
    }

    if (model.includes("deepseek")) {
      return "deepseek/" + model;
    }

    if (model.includes("o3-mini")) {
      return "o3-mini";
    }

    return model;
  }

  private parsePromptMessages(
    span: ReadableSpan
  ): KeywordsPayload["prompt_messages"] {
    try {
      const messages = span.attributes["ai.prompt.messages"];
      const parsedMessages = messages ? JSON.parse(String(messages)) : [];

      return KeywordsPayloadSchema.shape.prompt_messages.parse(parsedMessages);
    } catch (error) {
      this.logDebug("Error parsing messages:", error);
      return [
        {
          role: "user",
          content: String(span.attributes["ai.prompt"] || ""),
        },
      ];
    }
  }

  private parsePromptTokens(span: ReadableSpan): number {
    return parseInt(
      String(span.attributes["gen_ai.usage.input_tokens"] || "0")
    );
  }

  private parseCompletionTokens(span: ReadableSpan): number {
    return parseInt(
      String(span.attributes["gen_ai.usage.output_tokens"] || "0")
    );
  }

  private parseTimeToFirstToken(span: ReadableSpan): number {
    const msToFinish = span.attributes["ai.response.msToFinish"];
    const sToFinish = msToFinish ? (msToFinish as number) / 1000 : 0;
    return sToFinish;
  }

  private parseCost(span: ReadableSpan): number | undefined {
    const cost = span.attributes["gen_ai.usage.cost"];
    return cost ? parseFloat(String(cost)) : undefined;
  }

  private parseGenerationTime(span: ReadableSpan): number | undefined {
    const generationTime = span.attributes["gen_ai.usage.generation_time"];
    return generationTime ? parseFloat(String(generationTime)) : undefined;
  }

  private parseTtft(span: ReadableSpan): number | undefined {
    const ttft = span.attributes["gen_ai.usage.ttft"];
    return ttft ? parseFloat(String(ttft)) : undefined;
  }

  private parseWarnings(span: ReadableSpan): string | undefined {
    const warnings = span.attributes["gen_ai.usage.warnings"];
    return warnings ? String(warnings) : undefined;
  }

  private parseType(
    span: ReadableSpan
  ): "text" | "json_schema" | "json_object" | undefined {
    const type = span.attributes["gen_ai.usage.type"];
    return type ? (type as "text" | "json_schema" | "json_object") : undefined;
  }

  private parseMetadata(
    span: ReadableSpan
  ): Record<string, string | undefined> {
    return Object.entries(span.attributes)
      .filter(([key]) => key.startsWith("ai.telemetry.metadata."))
      .reduce((acc, [key, value]) => {
        const cleanKey = key.replace("ai.telemetry.metadata.", "");
        acc[cleanKey] = value?.toString();
        return acc;
      }, {} as Record<string, string | undefined>);
  }

  private isGenerationSpan(span: ReadableSpan): boolean {
    return ["doGenerate", "doStream"].some((part) => span.name.includes(part));
  }

  private isAiSdkSpan(span: ReadableSpan): boolean {
    // Check if the span is from the Vercel AI SDK
    return (
      // Check for ai-related attributes
      span.attributes["ai.sdk"] === true ||
      span.name.includes("ai.") ||
      // Check for other AI SDK related attributes
      Object.keys(span.attributes).some(
        (key) => key.startsWith("ai.") || key.startsWith("gen_ai.")
      )
    );
  }

  private logDebug(message: string, ...args: unknown[]): void {
    if (!this.debug) return;
    console.log(
      `[${new Date().toISOString()}] [KeywordsAIExporter] ${message}`,
      ...args
    );
  }

  async shutdown(): Promise<void> {
    // Nothing to clean up
  }

  private compareHrTime(a: [number, number], b: [number, number]): number {
    if (a[0] !== b[0]) return a[0] - b[0];
    return a[1] - b[1];
  }

  private findRootSpan(
    span: ReadableSpan,
    spans: ReadableSpan[]
  ): ReadableSpan | undefined {
    const parentId =
      span.attributes["span.parent_id"]?.toString() ||
      span.attributes["parentSpanId"]?.toString();
    if (!parentId) return span;
    return spans.find((s) => s.spanContext().spanId === parentId);
  }

  private formatTimestamp(hrTime: [number, number]): string {
    const epochMs = hrTime[0] * 1000 + hrTime[1] / 1e6;
    return new Date(epochMs).toISOString();
  }

  private parseToolChoice(
    span: ReadableSpan
  ): KeywordsPayload["tool_choice"] | undefined {
    try {
      const toolChoice = span.attributes["gen_ai.usage.tool_choice"];
      if (!toolChoice) return undefined;
      const parsed = JSON.parse(String(toolChoice));
      return {
        type: String(parsed.type),
        function: {
          name: String(parsed.function.name),
        },
      };
    } catch {
      return undefined;
    }
  }

  private parseTools(span: ReadableSpan): KeywordsPayload["tools"] | undefined {
    try {
      const tools = span.attributes["ai.prompt.tools"] || [];
      const parsed = Array.isArray(tools) ? tools : [tools];
      return parsed.map((tool) => JSON.parse(String(tool)));
    } catch {
      return undefined;
    }
  }
  private parseCustomerParams(span: ReadableSpan):
    | {
        customer_identifier: string;
        customer_email: string;
        customer_name: string;
      }
    | undefined {
    const customerParams =
      span.attributes["ai.telemetry.metadata.customer_params"];
    if (customerParams) {
      const parsed = JSON.parse(String(customerParams));
      return {
        customer_identifier: parsed.customer_identifier,
        customer_email: parsed.customer_email,
        customer_name: parsed.customer_name,
      };
    } else {
      const customerEmail =
        span.attributes["ai.telemetry.metadata.customer_email"];
      const customerName =
        span.attributes["ai.telemetry.metadata.customer_name"];
      const customerIdentifier =
        span.attributes["ai.telemetry.metadata.customer_identifier"];
      if (!customerIdentifier) return undefined;
      else {
        return {
          customer_email: String(customerEmail || ""),
          customer_name: String(customerName || ""),
          customer_identifier: String(customerIdentifier),
        };
      }
    }
  }

  private parseLogType(span: ReadableSpan): LogType {
    // Try to match span name directly to a known type
    const spanName = span.name;

    // Check if span name is in our mapping
    if (spanName in VERCEL_SPAN_TO_KEYWORDS_LOG_TYPE) {
      return VERCEL_SPAN_TO_KEYWORDS_LOG_TYPE[spanName] as LogType;
    }

    // For spans with operationId attribute, check for more specific mapping
    const operationId = span.attributes["ai.operationId"]?.toString();
    if (operationId && operationId in VERCEL_SPAN_TO_KEYWORDS_LOG_TYPE) {
      return VERCEL_SPAN_TO_KEYWORDS_LOG_TYPE[operationId] as LogType;
    }

    // Check for specific attributes that indicate the span type

    // Check for embedding-related attributes
    if (
      span.attributes["ai.embedding"] ||
      span.attributes["ai.embeddings"] ||
      spanName.includes("embed") ||
      operationId?.includes("embed")
    ) {
      return "embedding";
    }

    // Check for tool-related attributes
    if (
      span.attributes["ai.toolCall.id"] ||
      span.attributes["ai.toolCall.name"] ||
      span.attributes["ai.toolCall.args"] ||
      span.attributes["ai.toolCall.result"] ||
      span.attributes["ai.response.toolCalls"] ||
      spanName.includes("tool") ||
      operationId?.includes("tool")
    ) {
      return "tool";
    }

    // Check for agent-related attributes
    if (
      span.attributes["ai.agent.id"] ||
      spanName.includes("agent") ||
      operationId?.includes("agent")
    ) {
      return "agent";
    }

    // Check for workflow-related attributes
    if (
      span.attributes["ai.workflow.id"] ||
      spanName.includes("workflow") ||
      operationId?.includes("workflow")
    ) {
      return "workflow";
    }

    // Check for transcription-related attributes
    if (
      span.attributes["ai.transcript"] ||
      spanName.includes("transcript") ||
      operationId?.includes("transcript")
    ) {
      return "transcription";
    }

    // Check for speech-related attributes
    if (
      span.attributes["ai.speech"] ||
      spanName.includes("speech") ||
      operationId?.includes("speech")
    ) {
      return "speech";
    }

    // Default to TEXT for any generation-related spans
    if (this.isGenerationSpan(span)) {
      return "text";
    }

    // Fall back to unknown for anything else
    return "unknown";
  }

  // Add a new method to deduplicate spans
  private deduplicateSpans(spans: ReadableSpan[]): ReadableSpan[] {
    // First, group spans by their trace ID
    const traceGroups: Record<string, ReadableSpan[]> = {};

    // Group spans by trace ID
    for (const span of spans) {
      const traceId = span.spanContext().traceId;
      if (!traceGroups[traceId]) {
        traceGroups[traceId] = [];
      }
      traceGroups[traceId].push(span);
    }

    const deduplicatedSpans: ReadableSpan[] = [];

    // Process each trace group
    Object.values(traceGroups).forEach((traceSpans: ReadableSpan[]) => {
      // Group by base operation name
      const operationGroups: Record<string, ReadableSpan[]> = {};

      // Group spans by operation name (without .doStream or .doGenerate suffix)
      for (const span of traceSpans) {
        let opKey = span.name;
        if (opKey.endsWith(".doStream")) {
          opKey = opKey.replace(".doStream", "");
        } else if (opKey.endsWith(".doGenerate")) {
          opKey = opKey.replace(".doGenerate", "");
        }

        if (!operationGroups[opKey]) {
          operationGroups[opKey] = [];
        }
        operationGroups[opKey].push(span);
      }

      // Process each operation group
      Object.values(operationGroups).forEach((opSpans: ReadableSpan[]) => {
        // If we have multiple spans for the same operation, prefer the more detailed one
        if (opSpans.length > 1) {
          // Find doStream or doGenerate span
          const detailedSpan = opSpans.find(
            (s: ReadableSpan) =>
              s.name.endsWith(".doStream") || s.name.endsWith(".doGenerate")
          );

          if (detailedSpan) {
            // Only use the detailed span
            deduplicatedSpans.push(detailedSpan);
          } else {
            // No detailed span found, keep all spans
            deduplicatedSpans.push(...opSpans);
          }
        } else {
          // Only one span, keep it
          deduplicatedSpans.push(opSpans[0]);
        }
      });
    });

    return deduplicatedSpans;
  }
}
