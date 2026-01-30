import { ExportResult, ExportResultCode } from "@opentelemetry/core";
import { ReadableSpan, SpanExporter } from "@opentelemetry/sdk-trace-base";
import { KeywordsAIPayload, KeywordsAIPayloadSchema } from "@keywordsai/keywordsai-sdk";
import {
  compareHrTime,
  calculateLatency,
  deduplicateSpans,
  formatTimestamp,
  getParentSpanId,
  isAiSdkSpan,
} from "./utils/otel.js";
import {
  buildFullRequest,
  buildFullResponse,
  parseCompletionMessages,
  parseCompletionTokens,
  parseCost,
  parseCustomerParams,
  parseGenerationTime,
  parseLogType,
  parseMetadata,
  parseModel,
  parsePromptMessages,
  parsePromptTokens,
  parseTimeToFirstToken,
  parseToolCalls,
  parseToolChoice,
  parseTools,
  parseTotalRequestTokens,
  parseTtft,
  parseType,
  parseWarnings,
} from "./utils/span-parsers.js";

/**
 * AI SDK trace exporter that sends traces to KeywordsAI.
 * Observability provider reference: https://ai-sdk.dev/providers/observability/langfuse
 *
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
 * ```
 */
export class KeywordsAIExporter implements SpanExporter {
  private readonly debug: boolean;
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly url: string;

  private resolveURL(baseURL: string | undefined) {
    if (!baseURL) {
      return "https://api.keywordsai.co/api/v1/traces/ingest";
    }
    if (baseURL.endsWith("/api")) {
      return baseURL + "/v1/traces/ingest";
    }
    return baseURL + "/api/v1/traces/ingest";
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
    this.logDebug("KeywordsAIExporter initialized", {
      url: this.url,
      apiKey: this.apiKey.slice(0, 4) + "..." + this.apiKey.slice(-4),
      baseUrl: this.baseUrl,
    });
  }

  async export(
    spans: ReadableSpan[],
    resultCallback: (result: ExportResult) => void
  ): Promise<void> {
    try {
      const sortedSpans = spans
        .slice()
        .sort((a, b) => compareHrTime(a.startTime, b.startTime));

      const aiSdkSpans = sortedSpans.filter((span) => isAiSdkSpan(span));

      if (aiSdkSpans.length === 0) {
        this.logDebug("No AI SDK spans found");
        resultCallback({ code: ExportResultCode.SUCCESS });
        return;
      }

      const deduplicatedSpans = deduplicateSpans(aiSdkSpans);

      this.logDebug(
        `Filtered ${aiSdkSpans.length} spans to ${deduplicatedSpans.length} after deduplication`
      );

      const allPayloads: KeywordsAIPayload[] = [];

      for (const span of deduplicatedSpans) {
        try {
          this.logDebug("Creating payload for span", span);
          const rawPayload = await this.createPayload(span);
          try {
            const validatedPayload = KeywordsAIPayloadSchema.parse(rawPayload);
            allPayloads.push(validatedPayload);
          } catch (error) {
            this.logDebug("Payload validation failed", error);
            try {
              const fallbackPayload = KeywordsAIPayloadSchema.parse({
                ...rawPayload,
                full_request: rawPayload,
              });
              allPayloads.push(fallbackPayload);
            } catch (fallbackError) {
              this.logDebug("Fallback validation also failed", fallbackError);
              const minimalPayload = KeywordsAIPayloadSchema.parse({
                model: "unknown",
                prompt_messages: [
                  { role: "system", content: "Error processing span" },
                ],
                prompt_tokens: 0,
              timestamp: formatTimestamp(span.endTime),
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

  private async createPayload(span: ReadableSpan): Promise<KeywordsAIPayload> {
    const logDebug = this.logDebug.bind(this);

    const metadata = parseMetadata(span);
    const isError = span.status.code !== 0;
    const model = parseModel(span);
    const toolCalls = parseToolCalls(span, logDebug);
    const messages = parseCompletionMessages(span, toolCalls, logDebug);
    const parentSpanId = getParentSpanId(span);
    const promptTokens = parsePromptTokens(span);
    const completionTokens = parseCompletionTokens(span);
    const totalRequestTokens = parseTotalRequestTokens({
      span,
      promptTokens,
      completionTokens,
    });
    const customerEmail = metadata.customer_email;
    const customerName = metadata.customer_name;
    const promptMessages = parsePromptMessages(span, logDebug);
    const tools = parseTools(span);
    const toolChoice = parseToolChoice(span);
    const logType = parseLogType(span);
    const cost = parseCost({ span, model, promptTokens, completionTokens });

    const payload: KeywordsAIPayload = {
      model,
      start_time: formatTimestamp(span.startTime),
      timestamp: formatTimestamp(span.endTime),
      prompt_messages: promptMessages,
      completion_message: messages[0],
      customer_identifier: metadata.userId || "default_user",
      thread_identifier: metadata.userId,
      prompt_tokens: promptTokens,
      completion_tokens: completionTokens,
      ...(totalRequestTokens !== undefined && {
        total_request_tokens: totalRequestTokens,
        usage: {
          prompt_tokens: promptTokens,
          completion_tokens: completionTokens,
          total_tokens: totalRequestTokens,
        },
      }),
      ...(customerEmail && { customer_email: customerEmail }),
      ...(customerName && { customer_name: customerName }),
      cost,
      generation_time: parseGenerationTime(span),
      latency: calculateLatency(span),
      ttft: parseTtft(span),
      metadata: {
        ...metadata,
        span_type: span.name,
      },
      ...(metadata.prompt_unit_price && {
        prompt_unit_price: parseFloat(metadata.prompt_unit_price),
      }),
      ...(metadata.completion_unit_price && {
        completion_unit_price: parseFloat(metadata.completion_unit_price),
      }),
      environment: process.env.NODE_ENV || "prod",
      time_to_first_token: parseTimeToFirstToken(span),
      trace_unique_id: span.spanContext().traceId,
      span_unique_id: span.spanContext().spanId,
      span_name: span.name,
      span_parent_id:
        parentSpanId ||
        span.attributes["span.parent_id"]?.toString() ||
        span.attributes["parentSpanId"]?.toString(),
      span_path: span.attributes["ai.path"]?.toString(),
      stream: span.name.includes("doStream"),
      status_code: isError ? 500 : 200,
      warnings: parseWarnings(span),
      error_message: span.status.message || "",
      type: parseType(span),
      log_type: logType,
      is_test: process.env.NODE_ENV === "development",
      posthog_integration: process.env.POSTHOG_API_KEY
        ? {
            posthog_api_key: process.env.POSTHOG_API_KEY,
            posthog_base_url: "https://us.i.posthog.com",
          }
        : undefined,
      tool_choice: toolChoice,
      tools,
      tool_calls: toolCalls,
      field_name: "data: ",
      delimiter: "\n\n",
      disable_log: false,
      request_breakdown: false,
      disable_fallback: false,
      full_request: buildFullRequest(span, {
        model,
        prompt_messages: promptMessages,
        tools,
        tool_choice: toolChoice,
        log_type: logType,
      }),
      full_response: buildFullResponse(span, {
        completion_message: messages[0],
        tool_calls: toolCalls,
      }),
      ...parseCustomerParams(span),
    };

    return payload;
  }

  private async sendToKeywords(payloads: KeywordsAIPayload[]): Promise<void> {
    if (payloads.length === 0) {
      this.logDebug("No payloads to send");
      return;
    }

    try {
      this.logDebug(
        `Sending ${payloads.length} payloads to Keywords at ${this.url}`
      );

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

  // All parsing/deduping helpers live in `src/utils/*`.
}
