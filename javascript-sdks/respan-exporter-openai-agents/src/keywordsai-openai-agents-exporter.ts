import {
  OpenAITracingExporter,
  Trace,
  Span,
  OpenAITracingExporterOptions,
  TracingExporter,
  TracingProcessor,
  BatchTraceProcessor,
} from "@openai/agents";
import {
  KeywordsPayload,
  KeywordsPayloadSchema,
} from "@respan/respan-sdk";

// Define span data types based on OpenAI Agents SDK
interface ResponseSpanData {
  type: string;
  response_id?: string;
  _input?: any[];
  _response?: {
    usage?: {
      input_tokens?: number;
      output_tokens?: number;
      total_tokens?: number;
    };
    model?: string;
    output?: any[];
    output_text?: string;
  };
}

interface FunctionSpanData {
  type: string;
  name: string;
  input?: any;
  output?: any;
}

interface GenerationSpanData {
  type: string;
  model?: string;
  input?: any;
  output?: any;
  model_config?: Record<string, any>;
  usage?: {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
  };
}

interface HandoffSpanData {
  type: string;
  from_agent: string;
  to_agent: string;
}

interface CustomSpanData {
  name: string;
  data: Record<string, any>;
}

interface AgentSpanData {
  type: string;
  name: string;
  output_type?: string;
  tools?: string[];
  handoffs?: string[];
}

interface GuardrailSpanData {
  name: string;
  triggered: boolean;
}

// Reference for respan logging format: https://docs.respan.co/api-endpoints/integration/request-logging-endpoint#logging-api
// Helper functions for converting span data to Respan log format
function responseDataToRespanLog(
  data: Partial<KeywordsPayload>,
  spanData: ResponseSpanData
): void {
  data.span_name = spanData.type; // response
  data.log_type = "response"; // The correct respan log type for response spans
  try {
    // Extract prompt messages from _input if available
    if (spanData._input) {
      if (Array.isArray(spanData._input)) {
        // Handle list of messages
        const messages: any[] = [];
        for (const item of spanData._input) {
          try {
            if (item.role) {
              // Convert OpenAI Agents message format to Respan format
              // const message = {
              //   role: item.role,
              //   content: Array.isArray(item.content)
              //     ? item.content.map((c: any) => c.text || c.type === "input_text" ? c.text : String(c)).join(" ")
              //     : String(item.content)
              // };
              // console.log('message', message);
              messages.push(item);
            } else if (
              item.type === "function_call" ||
              item.type === "function_call_result"
            ) {
              data.tool_calls = data.tool_calls || [];
              data.tool_calls.push({
                type: "function",
                id: item.callId || item.id,
                function: {
                  name: item.name,
                  arguments:
                    typeof item.arguments === "string"
                      ? item.arguments
                      : JSON.stringify(item.arguments || {}),
                },
                ...(item.output && {
                  result:
                    typeof item.output === "string"
                      ? item.output
                      : JSON.stringify(item.output),
                }),
              });
            } else {
              messages.push(item);
            }
          } catch (e) {
            console.warn(
              `Failed to convert item to Message: ${e}, item:`,
              item
            );
            data.output = (data.output || "") + String(item);
          }
        }
        if (messages.length > 0) {
          data.prompt_messages = messages;
        }
      } else if (typeof spanData._input === "string") {
        // Handle string input (convert to a single user message)
        data.input = spanData._input;
      }
    }

    // If _response object exists, extract additional data
    if (spanData._response) {
      const response = spanData._response;
      // Extract usage information if available
      if (response.usage) {
        const usage = response.usage;
        data.prompt_tokens = usage.input_tokens;
        data.completion_tokens = usage.output_tokens;
        data.total_request_tokens = usage.total_tokens;
      }

      // Extract model information if available
      if (response.model) {
        data.model = response.model;
      }

      // Extract completion message from response
      if (response.output) {
        const responseItems = response.output;
        const completionMessages: any[] = [];
        for (const item of responseItems) {
          if (typeof item === "object" && item !== null) {
            const itemType = (item as any).type;
            if (itemType === "message" && (item as any).role === "assistant") {
              // Convert assistant message
              const content = Array.isArray((item as any).content)
                ? (item as any).content.map((c: any) => {
                    if (
                      typeof c === "object" &&
                      c !== null &&
                      (c.type === "output_text" || c.type === "text")
                    ) {
                      // Handle output_text and text content with annotations
                      const contentItem: any = {
                        type: c.type,
                        text: c.text,
                      };
                      if (c.annotations && Array.isArray(c.annotations)) {
                        contentItem.annotations = c.annotations;
                      }
                      if (c.cache_control) {
                        contentItem.cache_control = c.cache_control;
                      }
                      return contentItem;
                    }
                    return c.text || String(c);
                  })
                : String((item as any).content);

              const message: any = {
                role: "assistant",
                content: content,
              };

              // If content is an array and has structured items with annotations, preserve the structure
              if (
                Array.isArray(content) &&
                content.some(
                  (c: any) =>
                    typeof c === "object" &&
                    (c.type === "output_text" || c.type === "text")
                )
              ) {
                message.content = content;
              } else if (Array.isArray(content)) {
                // Convert to string if no structured content
                message.content = content
                  .map((c: any) =>
                    typeof c === "object" ? c.text || String(c) : String(c)
                  )
                  .join(" ");
              }

              completionMessages.push(message);
            } else if (itemType === "function_call") {
              data.tool_calls = data.tool_calls || [];
              data.tool_calls.push({
                type: "function",
                id: (item as any).call_id || (item as any).id,
                function: {
                  name: (item as any).name,
                  arguments: (item as any).arguments,
                },
              });
            } else {
              data.output = (data.output || "") + String(item);
            }
          } else {
            data.output = (data.output || "") + String(item);
          }
        }
        if (completionMessages.length > 0) {
          data.completion_messages = completionMessages;
          data.completion_message = completionMessages[0];
        }
      }

      // Use output_text if available
      if (response.output_text) {
        data.output = response.output_text;
      }

      // Add full response for logging
      data.full_response = response;
    }
  } catch (e) {
    console.error(`Error converting response data to Respan log: ${e}`);
  }
}

function functionDataToRespanLog(
  data: Partial<KeywordsPayload>,
  spanData: FunctionSpanData
): void {
  try {
    data.span_name = spanData.name;
    data.log_type = "tool"; // Changed to "tool" for function calls
    data.input = String(spanData.input);
    data.output = String(spanData.output);
    data.span_tools = [spanData.name];
  } catch (e) {
    console.error(`Error converting function data to Respan log: ${e}`);
  }
}

function generationDataToRespanLog(
  data: Partial<KeywordsPayload>,
  spanData: GenerationSpanData
): void {
  data.span_name = spanData.type; // generation
  data.log_type = "generation";
  data.model = spanData.model;

  try {
    // Extract prompt messages from input if available
    if (spanData.input) {
      data.input = String(spanData.input);
    }

    // Extract completion message from output if available
    if (spanData.output) {
      data.output = String(spanData.output);
    }

    // Add model configuration if available
    if (spanData.model_config) {
      // Extract common LLM parameters from model_config
      const params = [
        "temperature",
        "max_tokens",
        "top_p",
        "frequency_penalty",
        "presence_penalty",
      ];
      for (const param of params) {
        if (param in spanData.model_config) {
          (data as any)[param] = spanData.model_config[param];
        }
      }
    }

    // Add usage information if available
    if (spanData.usage) {
      data.prompt_tokens = spanData.usage.prompt_tokens;
      data.completion_tokens = spanData.usage.completion_tokens;
      data.total_request_tokens = spanData.usage.total_tokens;
    }
  } catch (e) {
    console.error(`Error converting generation data to Respan log: ${e}`);
  }
}

function handoffDataToRespanLog(
  data: Partial<KeywordsPayload>,
  spanData: HandoffSpanData
): void {
  data.span_name = spanData.type; // handoff
  data.log_type = "handoff"; // The correct respan log type
  data.span_handoffs = [`${spanData.from_agent} -> ${spanData.to_agent}`];
  data.metadata = {
    from_agent: spanData.from_agent,
    to_agent: spanData.to_agent,
  };
}

function customDataToRespanLog(
  data: Partial<KeywordsPayload>,
  spanData: CustomSpanData
): void {
  data.span_name = spanData.name;
  data.log_type = "custom"; // The corresponding respan log type
  data.metadata = spanData.data;

  // If the custom data contains specific fields that map to Respan fields, extract them
  const keys = [
    "input",
    "output",
    "model",
    "prompt_tokens",
    "completion_tokens",
  ];
  for (const key of keys) {
    if (key in spanData.data) {
      (data as any)[key] = spanData.data[key];
    }
  }
}

function agentDataToRespanLog(
  data: Partial<KeywordsPayload>,
  spanData: AgentSpanData
): void {
  data.span_name = spanData.name;
  data.log_type = "agent"; // The correct respan log type
  data.span_workflow_name = spanData.name;

  // Add tools if available
  if (spanData.tools) {
    data.span_tools = spanData.tools;
  }

  // Add handoffs if available
  if (spanData.handoffs) {
    data.span_handoffs = spanData.handoffs;
  }

  // Add metadata with agent information
  data.metadata = {
    output_type: spanData.output_type,
    agent_name: spanData.name,
  };
}

function guardrailDataToRespanLog(
  data: Partial<KeywordsPayload>,
  spanData: GuardrailSpanData
): void {
  data.span_name = `guardrail:${spanData.name}`;
  data.log_type = "guardrail"; // The correct respan log type
  data.has_warnings = spanData.triggered;
  if (spanData.triggered) {
    data.warnings_dict = data.warnings_dict || {};
    data.warnings_dict[`guardrail:${spanData.name}`] = "guardrail triggered";
  }
}

export class RespanSpanExporter implements TracingExporter {
  private apiKey: string | null;
  private organization: string | null;
  private project: string | null;
  private endpoint: string;
  private maxRetries: number;
  private baseDelay: number;
  private maxDelay: number;

  private resolveEndpoint(baseURL: string | undefined): string {
    if (!baseURL) {
      return `https://api.respan.co/api/v1/traces/ingest`;
    }
    if (baseURL.endsWith("/api")) {
      return `${baseURL}/v1/traces/ingest`;
    }
    return `${baseURL}/api/v1/traces/ingest`;
  }

  constructor({
    apiKey = process.env.RESPAN_API_KEY ||
      process.env.OPENAI_API_KEY ||
      null,
    organization = process.env.OPENAI_ORG_ID || null,
    project = process.env.OPENAI_PROJECT_ID || null,
    endpoint = this.resolveEndpoint(process.env.RESPAN_BASE_URL),
    maxRetries = 3,
    baseDelay = 1.0,
    maxDelay = 30.0,
  }: {
    apiKey?: string | null;
    organization?: string | null;
    project?: string | null;
    endpoint?: string;
    maxRetries?: number;
    baseDelay?: number;
    maxDelay?: number;
  } = {}) {
    this.apiKey = apiKey;
    this.organization = organization;
    this.project = project;
    this.endpoint = endpoint;
    this.maxRetries = maxRetries;
    this.baseDelay = baseDelay;
    this.maxDelay = maxDelay;
  }

  setEndpoint(endpoint: string): void {
    this.endpoint = endpoint;
    console.log(`Keywords AI exporter endpoint changed to: ${endpoint}`);
  }

  private keywordsAIExport(
    item: Trace | Span<any>,
    allItems?: (Trace | Span<any>)[]
  ): Partial<KeywordsPayload> | null {
    // First try the native export method
    if (this.isTrace(item)) {
      // Trace objects don't have timing data - they represent the workflow container
      // Calculate timing from child spans if available
      let startTime = new Date();
      let endTime = new Date();
      let latency = 0;

      if (allItems) {
        // Find all spans belonging to this trace
        const traceSpans = allItems.filter(
          (i) => this.isSpan(i) && i.traceId === item.traceId
        ) as Span<any>[];

        if (traceSpans.length > 0) {
          // Calculate earliest start and latest end from spans
          const earliestStart = traceSpans.reduce((earliest, span) => {
            const spanStart = span.startedAt ? new Date(span.startedAt) : null;
            if (!spanStart) return earliest;
            return !earliest || spanStart < earliest ? spanStart : earliest;
          }, null as Date | null);

          const latestEnd = traceSpans.reduce((latest, span) => {
            const spanEnd = span.endedAt ? new Date(span.endedAt) : null;
            if (!spanEnd) return latest;
            return !latest || spanEnd > latest ? spanEnd : latest;
          }, null as Date | null);

          if (earliestStart && latestEnd) {
            startTime = earliestStart;
            endTime = latestEnd;
            latency = (latestEnd.getTime() - earliestStart.getTime()) / 1000;
          }
        }
      }

      const traceData: Partial<KeywordsPayload> = {
        trace_unique_id: item.traceId,
        span_unique_id: item.traceId,
        span_name: item.name,
        log_type: "agent", // Root trace should be agent type
        span_workflow_name: item.name,
        start_time: startTime,
        timestamp: endTime,
        latency: latency,
      };

      // Extract custom metadata from trace if available
      try {
        const traceJson = JSON.parse(JSON.stringify(item));
        if (traceJson.metadata && typeof traceJson.metadata === "object") {
          // Merge trace metadata with any existing metadata
          traceData.metadata = {
            ...traceData.metadata,
            ...traceJson.metadata,
          };
        }
      } catch (e) {
        console.warn(`Failed to extract trace metadata: ${e}`);
      }

      return traceData;
    } else if (this.isSpan(item)) {
      // Get the span ID - it could be named span_id or id depending on the implementation
      const parentId = item.parentId || item.traceId;

      // Create the base data dictionary with common fields
      // Note: Span timing properties are accessed via the JSON structure
      const spanJson = JSON.parse(JSON.stringify(item));
      const data: Partial<KeywordsPayload> = {
        trace_unique_id: item.traceId,
        span_unique_id: item.spanId,
        span_parent_id: parentId || undefined,
        start_time: spanJson.started_at
          ? new Date(spanJson.started_at)
          : undefined,
        timestamp: spanJson.ended_at ? new Date(spanJson.ended_at) : undefined,
        error_bit: item.error ? 1 : 0,
        status_code: item.error ? 400 : 200,
        error_message: item.error ? String(item.error) : undefined,
      };

      // Calculate latency from timestamps
      if (
        data.timestamp &&
        data.start_time &&
        data.timestamp instanceof Date &&
        data.start_time instanceof Date
      ) {
        data.latency =
          (data.timestamp.getTime() - data.start_time.getTime()) / 1000;
      }

      // Process the span data based on its type
      try {
        const spanData = item.spanData;

        // Log the span data for debugging
        // console.log('Processing span data:', JSON.stringify(spanData, null, 2));

        if (this.isResponseSpanData(spanData)) {
          responseDataToRespanLog(data, spanData);
        } else if (this.isFunctionSpanData(spanData)) {
          functionDataToRespanLog(data, spanData);
        } else if (this.isGenerationSpanData(spanData)) {
          generationDataToRespanLog(data, spanData);
        } else if (this.isHandoffSpanData(spanData)) {
          handoffDataToRespanLog(data, spanData);
        } else if (this.isCustomSpanData(spanData)) {
          customDataToRespanLog(data, spanData);
        } else if (this.isAgentSpanData(spanData)) {
          agentDataToRespanLog(data, spanData);
        } else if (this.isGuardrailSpanData(spanData)) {
          guardrailDataToRespanLog(data, spanData);
        } else {
          console.warn(`Unknown span data type:`, spanData);
          // Don't return null, create a basic span with the available data
          data.span_name = spanData?.type || spanData?.name || "unknown_span";
          data.log_type = "custom";
          data.metadata = spanData;
        }

        // Ensure all spans have required fields for Respan
        if (!data.span_name) {
          data.span_name = spanData?.type || spanData?.name || item.spanId;
        }
        if (!data.log_type) {
          data.log_type = "custom";
        }

        return data;
      } catch (e) {
        console.error(`Error converting span data to Respan log: ${e}`);
        return null;
      }
    } else {
      return null;
    }
  }

  // Type guards
  private isTrace(item: Trace | Span<any>): item is Trace {
    return "traceId" in item && "name" in item && !("spanId" in item);
  }

  private isSpan(item: Trace | Span<any>): item is Span<any> {
    return "spanId" in item && "spanData" in item;
  }

  private isResponseSpanData(data: any): data is ResponseSpanData {
    return data && data.type === "response";
  }

  private isFunctionSpanData(data: any): data is FunctionSpanData {
    return data && data.type === "function" && typeof data.name === "string";
  }

  private isGenerationSpanData(data: any): data is GenerationSpanData {
    return data && data.type === "generation";
  }

  private isHandoffSpanData(data: any): data is HandoffSpanData {
    return (
      data &&
      data.type === "handoff" &&
      "from_agent" in data &&
      "to_agent" in data
    );
  }

  private isCustomSpanData(data: any): data is CustomSpanData {
    return (
      data &&
      typeof data.name === "string" &&
      "data" in data &&
      data.type !== "agent" &&
      data.type !== "function" &&
      data.type !== "response"
    );
  }

  private isAgentSpanData(data: any): data is AgentSpanData {
    return data && data.type === "agent" && typeof data.name === "string";
  }

  private isGuardrailSpanData(data: any): data is GuardrailSpanData {
    return (
      data &&
      typeof data.name === "string" &&
      typeof data.triggered === "boolean"
    );
  }

  async export(
    items: (Trace | Span<any>)[],
    signal?: AbortSignal
  ): Promise<void> {
    if (!items.length) {
      return;
    }

    if (!this.apiKey) {
      console.warn("API key is not set, skipping trace export");
      return;
    }

    // Items processing: Trace objects represent workflow containers, Spans contain actual timing data

    // Process each item with our custom exporter
    const processedData = items
      .map((item) => this.keywordsAIExport(item, items))
      .filter((item): item is Partial<KeywordsPayload> => item !== null);

    // If we have spans but no trace, create a synthetic root trace with calculated timing
    const spans = items.filter((item) => this.isSpan(item)) as Span<any>[];
    const traces = items.filter((item) => this.isTrace(item)) as Trace[];

    if (spans.length > 0 && traces.length === 0) {
      // Create a synthetic root trace from span data
      const traceId = spans[0].traceId;
      const earliestStart = spans.reduce((earliest, span) => {
        const spanStart = span.startedAt ? new Date(span.startedAt) : null;
        if (!spanStart) return earliest;
        return !earliest || spanStart < earliest ? spanStart : earliest;
      }, null as Date | null);

      const latestEnd = spans.reduce((latest, span) => {
        const spanEnd = span.endedAt ? new Date(span.endedAt) : null;
        if (!spanEnd) return latest;
        return !latest || spanEnd > latest ? spanEnd : latest;
      }, null as Date | null);

      if (earliestStart && latestEnd) {
        const syntheticTrace: Partial<KeywordsPayload> = {
          trace_unique_id: traceId,
          span_unique_id: traceId,
          span_name: "My Trace",
          log_type: "agent",
          span_workflow_name: "My Trace",
          start_time: earliestStart,
          timestamp: latestEnd,
          latency: (latestEnd.getTime() - earliestStart.getTime()) / 1000,
        };

        // Try to extract metadata from the first span if available
        try {
          const firstSpan = spans[0];
          const spanJson = JSON.parse(JSON.stringify(firstSpan));
          if (
            spanJson._trace &&
            spanJson._trace.metadata &&
            typeof spanJson._trace.metadata === "object"
          ) {
            // Merge trace metadata with any existing metadata
            syntheticTrace.metadata = {
              ...syntheticTrace.metadata,
              ...spanJson._trace.metadata,
            };
          }
        } catch (e) {
          console.warn(
            `Failed to extract metadata from span for synthetic trace: ${e}`
          );
        }

        processedData.unshift(syntheticTrace);
      }
    }

    if (!processedData.length) {
      return;
    }

    const payload = { data: processedData };

    const headers: Record<string, string> = {
      Authorization: `Bearer ${this.apiKey}`,
      "Content-Type": "application/json",
      "OpenAI-Beta": "traces=v1",
    };

    if (this.organization) {
      headers["OpenAI-Organization"] = this.organization;
    }

    if (this.project) {
      headers["OpenAI-Project"] = this.project;
    }

    // Exponential backoff loop
    let attempt = 0;
    let delay = this.baseDelay;

    while (true) {
      attempt++;
      try {
        const response = await fetch(this.endpoint, {
          method: "POST",
          headers,
          body: JSON.stringify(payload),
          signal,
        });

        // If the response is successful, break out of the loop
        if (response.status < 300) {
          console.log(`Exported ${processedData.length} items to Keywords AI`);
          return;
        }

        // If the response is a client error (4xx), we won't retry
        if (response.status >= 400 && response.status < 500) {
          const errorText = await response.text();
          console.error(
            `Keywords AI client error ${response.status}: ${errorText}`
          );
          return;
        }

        // For 5xx or other unexpected codes, treat it as transient and retry
        console.warn(`Server error ${response.status}, retrying.`);
      } catch (error) {
        if (signal?.aborted) {
          console.log("Export aborted");
          return;
        }
        // Network or other I/O error, we'll retry
        console.warn(`Request failed: ${error}`);
      }

      // If we reach here, we need to retry or give up
      if (attempt >= this.maxRetries) {
        console.error("Max retries reached, giving up on this batch.");
        return;
      }

      // Exponential backoff + jitter
      const sleepTime = delay + Math.random() * 0.1 * delay; // 10% jitter
      await new Promise((resolve) => setTimeout(resolve, sleepTime * 1000));
      delay = Math.min(delay * 2, this.maxDelay);
    }
  }
}

export class RespanOpenAIAgentsTracingExporter extends RespanSpanExporter {
  constructor(options?: {
    apiKey?: string | null;
    organization?: string | null;
    project?: string | null;
    endpoint?: string;
    maxRetries?: number;
    baseDelay?: number;
    maxDelay?: number;
  }) {
    super(options);
  }
}

export class RespanTraceProcessor extends BatchTraceProcessor {
  private keywordsExporter: RespanSpanExporter;

  constructor({
    apiKey = process.env.RESPAN_API_KEY ||
      process.env.OPENAI_API_KEY ||
      null,
    organization = process.env.OPENAI_ORG_ID || null,
    project = process.env.OPENAI_PROJECT_ID || null,
    endpoint = process.env.RESPAN_BASE_URL
      ? `${process.env.RESPAN_BASE_URL}/v1/traces/ingest`
      : "https://api.respan.co/api/v1/traces/ingest",
    maxRetries = 3,
    baseDelay = 1.0,
    maxDelay = 30.0,
    maxQueueSize = 8192,
    maxBatchSize = 128,
    scheduleDelay = 5.0,
    exportTriggerRatio = 0.7,
  }: {
    apiKey?: string | null;
    organization?: string | null;
    project?: string | null;
    endpoint?: string;
    maxRetries?: number;
    baseDelay?: number;
    maxDelay?: number;
    maxQueueSize?: number;
    maxBatchSize?: number;
    scheduleDelay?: number;
    exportTriggerRatio?: number;
  } = {}) {
    // Create the exporter
    const exporter = new RespanSpanExporter({
      apiKey,
      organization,
      project,
      endpoint,
      maxRetries,
      baseDelay,
      maxDelay,
    });

    // Initialize the BatchTraceProcessor with our exporter
    super(exporter, {
      maxQueueSize,
      maxBatchSize,
      scheduleDelay,
      exportTriggerRatio,
    });

    // Store the exporter for easy access
    this.keywordsExporter = exporter;
  }

  setEndpoint(endpoint: string): void {
    this.keywordsExporter.setEndpoint(endpoint);
  }
}
