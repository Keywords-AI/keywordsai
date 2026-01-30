import { ReadableSpan } from "@opentelemetry/sdk-trace-base";
import {
  KeywordsAIPayload,
  KeywordsAIPayloadSchema,
  LogType,
  LOG_TYPE_VALUES,
} from "@keywordsai/keywordsai-sdk";
import { AISDK_SPAN_TO_KEYWORDS_LOG_TYPE } from "../constants/logs.js";
import { isGenerationSpan } from "./otel.js";

type DebugLogger = (message: string, ...args: unknown[]) => void;

// Prices are USD per 1M tokens (input/output).
// Keep this small: it is only a fallback when the span has no explicit cost.
const MODEL_PRICES_PER_1M_TOKENS: Record<string, { input: number; output: number }> = {
  // OpenAI
  "openai/gpt-4o-mini": { input: 0.15, output: 0.6 },
  "openai/gpt-4o": { input: 5.0, output: 15.0 },
};

export function parseMetadata(
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

export function parseCustomerParams(
  span: ReadableSpan
):
  | {
      customer_identifier: string;
      customer_email: string;
      customer_name: string;
    }
  | undefined {
  const customerParams = span.attributes["ai.telemetry.metadata.customer_params"];
  if (customerParams) {
    const parsed = JSON.parse(String(customerParams));
    return {
      customer_identifier: parsed.customer_identifier,
      customer_email: parsed.customer_email,
      customer_name: parsed.customer_name,
    };
  }

  const customerEmail = span.attributes["ai.telemetry.metadata.customer_email"];
  const customerName = span.attributes["ai.telemetry.metadata.customer_name"];
  const customerIdentifier =
    span.attributes["ai.telemetry.metadata.customer_identifier"];
  if (!customerIdentifier) return undefined;

  return {
    customer_email: String(customerEmail || ""),
    customer_name: String(customerName || ""),
    customer_identifier: String(customerIdentifier),
  };
}

export function parseToolCalls(
  span: ReadableSpan,
  logDebug?: DebugLogger
): any[] | undefined {
  try {
    const toolCallAttributes = ["ai.response.toolCalls", "ai.toolCall", "ai.toolCalls"];

    for (const attr of toolCallAttributes) {
      if (span.attributes[attr]) {
        const rawData = span.attributes[attr];
        if (!rawData) continue;

        let parsed;
        try {
          parsed = typeof rawData === "string" ? JSON.parse(rawData) : rawData;
        } catch (e) {
          logDebug?.(`Failed to parse ${attr}:`, e);
          continue;
        }

        const toolCalls = Array.isArray(parsed) ? parsed : [parsed];

        return toolCalls.map((call) => {
          if (!call || typeof call !== "object") {
            return { type: "function" };
          }

          const result = { ...call };

          if (!result.type) {
            result.type = "function";
          }

          if (!result.id && (result.toolCallId || result.tool_call_id)) {
            result.id = result.toolCallId || result.tool_call_id;
          }

          return result;
        });
      }
    }

    if (
      span.attributes["ai.toolCall.id"] ||
      span.attributes["ai.toolCall.name"] ||
      span.attributes["ai.toolCall.args"]
    ) {
      const toolCall: Record<string, any> = { type: "function" };

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
    logDebug?.("Error parsing tool calls:", error);
    return undefined;
  }
}

export function parseCompletionMessages(
  span: ReadableSpan,
  toolCalls?: any[],
  logDebug?: DebugLogger
): any[] {
  let content = "";

  if (span.attributes["ai.response.object"]) {
    try {
      const response = JSON.parse(String(span.attributes["ai.response.object"]));
      content = String((response as any).response || "");
    } catch (error) {
      logDebug?.("Error parsing ai.response.object:", error);
      content = String(span.attributes["ai.response.text"] || "");
    }
  } else {
    content = String(span.attributes["ai.response.text"] || "");
  }

  const message = {
    role: "assistant",
    content,
    ...(toolCalls && toolCalls.length > 0 && { tool_calls: toolCalls }),
  };

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

export function parsePromptMessages(
  span: ReadableSpan,
  logDebug?: DebugLogger
): KeywordsAIPayload["prompt_messages"] {
  try {
    const messages = span.attributes["ai.prompt.messages"];
    const parsedMessages = messages ? JSON.parse(String(messages)) : [];

    return KeywordsAIPayloadSchema.shape.prompt_messages.parse(parsedMessages);
  } catch (error) {
    logDebug?.("Error parsing messages:", error);
    return [
      {
        role: "user",
        content: String(span.attributes["ai.prompt"] || ""),
      },
    ];
  }
}

export function parseToolChoice(
  span: ReadableSpan
): KeywordsAIPayload["tool_choice"] | undefined {
  try {
    const toolChoice = span.attributes["gen_ai.usage.tool_choice"];
    if (!toolChoice) return undefined;
    const parsed = JSON.parse(String(toolChoice));
    return {
      type: String((parsed as any).type),
      function: {
        name: String((parsed as any).function.name),
      },
    };
  } catch {
    return undefined;
  }
}

export function parseTools(span: ReadableSpan): KeywordsAIPayload["tools"] | undefined {
  try {
    const tools = span.attributes["ai.prompt.tools"] || [];
    const parsed = Array.isArray(tools) ? tools : [tools];
    return parsed
      .map((tool) => {
        try {
          return JSON.parse(String(tool));
        } catch {
          return undefined;
        }
      })
      .filter(Boolean)
      .map((tool: any) => {
        if (tool && tool.type === "function") {
          if (tool.function && typeof tool.function === "object") return tool;
          const { name, description, parameters, ...rest } = tool as any;
          return {
            ...rest,
            type: "function",
            function: {
              name,
              ...(description ? { description } : {}),
              ...(parameters ? { parameters } : {}),
            },
          };
        }
        return tool;
      });
  } catch {
    return undefined;
  }
}

export function parsePromptTokens(span: ReadableSpan): number {
  return parseInt(
    String(
      span.attributes["gen_ai.usage.input_tokens"] ||
        span.attributes["gen_ai.usage.prompt_tokens"] ||
        span.attributes["ai.usage.promptTokens"] ||
        "0"
    )
  );
}

export function parseCompletionTokens(span: ReadableSpan): number {
  return parseInt(
    String(
      span.attributes["gen_ai.usage.output_tokens"] ||
        span.attributes["gen_ai.usage.completion_tokens"] ||
        span.attributes["ai.usage.completionTokens"] ||
        "0"
    )
  );
}

export function parseTotalRequestTokens(
  params: {
    span: ReadableSpan;
    promptTokens: number;
    completionTokens: number;
  }
): number | undefined {
  const { span, promptTokens, completionTokens } = params;
  const totalFromAttr =
    span.attributes["gen_ai.usage.total_tokens"] ??
    span.attributes["gen_ai.usage.total_request_tokens"];

  if (totalFromAttr !== undefined) {
    const parsed = parseInt(String(totalFromAttr));
    if (!Number.isNaN(parsed)) return parsed;
  }

  const hasTokenAttrs =
    span.attributes["gen_ai.usage.input_tokens"] !== undefined ||
    span.attributes["gen_ai.usage.prompt_tokens"] !== undefined ||
    span.attributes["gen_ai.usage.output_tokens"] !== undefined ||
    span.attributes["gen_ai.usage.completion_tokens"] !== undefined ||
    span.attributes["ai.usage.promptTokens"] !== undefined ||
    span.attributes["ai.usage.completionTokens"] !== undefined;

  if (!hasTokenAttrs) return undefined;

  return promptTokens + completionTokens;
}

export function parseGenerationTime(span: ReadableSpan): number | undefined {
  const generationTime = span.attributes["gen_ai.usage.generation_time"];
  return generationTime ? parseFloat(String(generationTime)) : undefined;
}

export function parseTtft(span: ReadableSpan): number | undefined {
  const ttft = span.attributes["gen_ai.usage.ttft"];
  return ttft ? parseFloat(String(ttft)) : undefined;
}

export function parseWarnings(span: ReadableSpan): string | undefined {
  const warnings = span.attributes["gen_ai.usage.warnings"];
  return warnings ? String(warnings) : undefined;
}

export function parseType(
  span: ReadableSpan
): "text" | "json_schema" | "json_object" | undefined {
  const type = span.attributes["gen_ai.usage.type"];
  return type ? (type as "text" | "json_schema" | "json_object") : undefined;
}

export function parseTimeToFirstToken(span: ReadableSpan): number {
  const msToFinish = span.attributes["ai.response.msToFinish"];
  const sToFinish = msToFinish ? (msToFinish as number) / 1000 : 0;
  return sToFinish;
}

export function parseModel(span: ReadableSpan): string {
  const rawModel = String(span.attributes["ai.model.id"] || "unknown");
  const model = rawModel.toLowerCase();

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

  if (model.includes("/")) return model;

  const providerRaw = span.attributes["ai.model.provider"] ?? span.attributes["gen_ai.system"];
  const provider = providerRaw ? String(providerRaw).toLowerCase() : undefined;

  if (provider) {
    if (provider.includes("openai")) return `openai/${model}`;
    if (provider.includes("anthropic")) return `anthropic/${model}`;
    if (provider.includes("cohere")) return `cohere/${model}`;
    if (provider.includes("mistral")) return `mistral/${model}`;
    if (provider.includes("groq")) return `groq/${model}`;
    if (provider.includes("xai") || provider.includes("grok")) return `xai/${model}`;
  }

  return model;
}

export function parseCost(
  params: {
    span: ReadableSpan;
    model: string;
    promptTokens: number;
    completionTokens: number;
  }
): number | undefined {
  const { span, model, promptTokens, completionTokens } = params;
  const cost = span.attributes["gen_ai.usage.cost"];
  if (cost !== undefined && cost !== null && cost !== "") {
    const parsed = parseFloat(String(cost));
    return Number.isFinite(parsed) ? parsed : undefined;
  }

  if (!promptTokens && !completionTokens) return undefined;

  const price = MODEL_PRICES_PER_1M_TOKENS[model];
  if (!price) return undefined;

  const estimated =
    (promptTokens * price.input + completionTokens * price.output) / 1_000_000;

  return Number.isFinite(estimated) && estimated >= 0 ? estimated : undefined;
}

export function parseLogType(span: ReadableSpan): LogType {
  const spanName = span.name;
  const explicitLogType =
    span.attributes["keywordsai.log_type"] ??
    span.attributes["ai.log_type"] ??
    span.attributes["log_type"];

  if (explicitLogType !== undefined) {
    const normalized = String(explicitLogType).toLowerCase();
    if (LOG_TYPE_VALUES.includes(normalized as LogType)) {
      return normalized as LogType;
    }
  }

  if (spanName in AISDK_SPAN_TO_KEYWORDS_LOG_TYPE) {
    return AISDK_SPAN_TO_KEYWORDS_LOG_TYPE[spanName] as LogType;
  }

  const operationId = span.attributes["ai.operationId"]?.toString();
  if (operationId && operationId in AISDK_SPAN_TO_KEYWORDS_LOG_TYPE) {
    return AISDK_SPAN_TO_KEYWORDS_LOG_TYPE[operationId] as LogType;
  }

  if (
    span.attributes["ai.embedding"] ||
    span.attributes["ai.embeddings"] ||
    spanName.includes("embed") ||
    operationId?.includes("embed")
  ) {
    return "embedding";
  }

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

  if (
    span.attributes["ai.agent.id"] ||
    spanName.includes("agent") ||
    operationId?.includes("agent")
  ) {
    return "agent";
  }

  if (
    span.attributes["ai.workflow.id"] ||
    spanName.includes("workflow") ||
    operationId?.includes("workflow")
  ) {
    return "workflow";
  }

  if (
    span.attributes["ai.transcript"] ||
    spanName.includes("transcript") ||
    operationId?.includes("transcript")
  ) {
    return "transcription";
  }

  if (
    span.attributes["ai.speech"] ||
    spanName.includes("speech") ||
    operationId?.includes("speech")
  ) {
    return "speech";
  }

  if (isGenerationSpan(span)) {
    return "generation";
  }

  return "unknown";
}

export function safeJsonParse(value: unknown): unknown | undefined {
  if (value === undefined || value === null) return undefined;
  if (typeof value !== "string") return value;
  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

export function sanitizeForJson(value: unknown): unknown {
  if (
    value === null ||
    value === undefined ||
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return value;
  }

  if (typeof value === "bigint") return value.toString();

  if (Array.isArray(value)) return value.map((v) => sanitizeForJson(v));

  if (typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
      out[k] = sanitizeForJson(v);
    }
    return out;
  }

  return String(value);
}

export function buildFullRequest(
  span: ReadableSpan,
  params: {
    model: string;
    prompt_messages: KeywordsAIPayload["prompt_messages"];
    tools?: KeywordsAIPayload["tools"];
    tool_choice?: KeywordsAIPayload["tool_choice"];
    log_type: LogType;
  }
): Record<string, unknown> {
  const operationId = span.attributes["ai.operationId"]?.toString();

  return {
    span_name: span.name,
    operation_id: operationId,
    log_type: params.log_type,
    model: params.model,
    prompt: span.attributes["ai.prompt"]?.toString(),
    prompt_messages: params.prompt_messages,
    tools: params.tools,
    tool_choice: params.tool_choice,
    raw: sanitizeForJson({
      "ai.prompt.messages": safeJsonParse(span.attributes["ai.prompt.messages"]),
      "ai.prompt.tools": safeJsonParse(span.attributes["ai.prompt.tools"]),
      "ai.prompt": span.attributes["ai.prompt"],
      "ai.model.id": span.attributes["ai.model.id"],
    }),
  };
}

export function buildFullResponse(
  span: ReadableSpan,
  params: {
    completion_message: KeywordsAIPayload["completion_message"];
    tool_calls?: any[] | undefined;
  }
): Record<string, unknown> {
  return {
    span_name: span.name,
    response_text: span.attributes["ai.response.text"]?.toString(),
    response_object: safeJsonParse(span.attributes["ai.response.object"]),
    response_tool_calls: safeJsonParse(span.attributes["ai.response.toolCalls"]),
    completion_message: params.completion_message,
    tool_calls: params.tool_calls,
    raw: sanitizeForJson({
      "ai.response.text": span.attributes["ai.response.text"],
      "ai.response.object": safeJsonParse(span.attributes["ai.response.object"]),
      "ai.response.toolCalls": safeJsonParse(span.attributes["ai.response.toolCalls"]),
      "ai.toolCall.id": span.attributes["ai.toolCall.id"],
      "ai.toolCall.name": span.attributes["ai.toolCall.name"],
      "ai.toolCall.args": safeJsonParse(span.attributes["ai.toolCall.args"]),
      "ai.toolCall.result": safeJsonParse(span.attributes["ai.toolCall.result"]),
    }),
  };
}

