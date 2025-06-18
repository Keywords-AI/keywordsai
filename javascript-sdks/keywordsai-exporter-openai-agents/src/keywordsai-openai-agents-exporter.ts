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
} from "@keywordsai/keywordsai-sdk";

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

// Reference for keywordsai logging format: https://docs.keywordsai.co/api-endpoints/integration/request-logging-endpoint#logging-api
// Helper functions for converting span data to KeywordsAI log format
function responseDataToKeywordsAILog(
  data: Partial<KeywordsPayload>,
  spanData: ResponseSpanData
): void {
  data.span_name = spanData.type; // response
  data.log_type = "text"; // The corresponding keywordsai log type

  try {
    // Extract prompt messages from _input if available
    if (spanData._input) {
      if (Array.isArray(spanData._input)) {
        // Handle list of messages
        const messages: any[] = [];
        for (const item of spanData._input) {
          try {
            if (item.type === "message") {
              // Convert OpenAI Agents message format to KeywordsAI format
              const message = {
                role: item.role,
                content: Array.isArray(item.content) 
                  ? item.content.map((c: any) => c.text || c.type === "input_text" ? c.text : String(c)).join(" ")
                  : String(item.content)
              };
              messages.push(message);
            } else if (item.type === "function_call" || item.type === "function_call_result") {
              data.tool_calls = data.tool_calls || [];
              data.tool_calls.push({
                type: "function",
                id: item.callId || item.id,
                function: {
                  name: item.name,
                  arguments: typeof item.arguments === "string" ? item.arguments : JSON.stringify(item.arguments || {}),
                },
                ...(item.output && { result: typeof item.output === "string" ? item.output : JSON.stringify(item.output) })
              });
            }
          } catch (e) {
            console.warn(`Failed to convert item to Message: ${e}, item:`, item);
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
                ? (item as any).content.map((c: any) => c.text || String(c)).join(" ")
                : String((item as any).content);
              completionMessages.push({
                role: "assistant",
                content: content
              });
            } else if (itemType === "function_call") {
              data.tool_calls = data.tool_calls || [];
              data.tool_calls.push({
                type: "function",
                id: (item as any).call_id || (item as any).id,
                function: {
                  name: (item as any).name,
                  arguments: (item as any).arguments,
                }
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
    console.error(`Error converting response data to KeywordsAI log: ${e}`);
  }
}

function functionDataToKeywordsAILog(
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
    console.error(`Error converting function data to KeywordsAI log: ${e}`);
  }
}

function generationDataToKeywordsAILog(
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
    console.error(`Error converting generation data to KeywordsAI log: ${e}`);
  }
}

function handoffDataToKeywordsAILog(
  data: Partial<KeywordsPayload>,
  spanData: HandoffSpanData
): void {
  data.span_name = spanData.type; // handoff
  data.log_type = "handoff"; // The corresponding keywordsai log type
  data.span_handoffs = [`${spanData.from_agent} -> ${spanData.to_agent}`];
  data.metadata = {
    from_agent: spanData.from_agent,
    to_agent: spanData.to_agent,
  };
}

function customDataToKeywordsAILog(
  data: Partial<KeywordsPayload>,
  spanData: CustomSpanData
): void {
  data.span_name = spanData.name;
  data.log_type = "custom"; // The corresponding keywordsai log type
  data.metadata = spanData.data;

  // If the custom data contains specific fields that map to KeywordsAI fields, extract them
  const keys = ["input", "output", "model", "prompt_tokens", "completion_tokens"];
  for (const key of keys) {
    if (key in spanData.data) {
      (data as any)[key] = spanData.data[key];
    }
  }
}

function agentDataToKeywordsAILog(
  data: Partial<KeywordsPayload>,
  spanData: AgentSpanData
): void {
  data.span_name = spanData.name;
  data.log_type = "agent"; // The corresponding keywordsai log type
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

function guardrailDataToKeywordsAILog(
  data: Partial<KeywordsPayload>,
  spanData: GuardrailSpanData
): void {
  data.span_name = `guardrail:${spanData.name}`;
  data.log_type = "guardrail"; // The corresponding keywordsai log type
  data.has_warnings = spanData.triggered;
  if (spanData.triggered) {
    data.warnings_dict = data.warnings_dict || {};
    data.warnings_dict[`guardrail:${spanData.name}`] = "guardrail triggered";
  }
}

export class KeywordsAISpanExporter implements TracingExporter {
  private apiKey: string | null;
  private organization: string | null;
  private project: string | null;
  private endpoint: string;
  private maxRetries: number;
  private baseDelay: number;
  private maxDelay: number;

  constructor({
    apiKey = process.env.KEYWORDSAI_API_KEY || process.env.OPENAI_API_KEY || null,
    organization = process.env.OPENAI_ORG_ID || null,
    project = process.env.OPENAI_PROJECT_ID || null,
    endpoint = process.env.KEYWORDSAI_BASE_URL ? 
      `${process.env.KEYWORDSAI_BASE_URL}/openai/v1/traces/ingest` : 
      "https://api.keywordsai.co/api/openai/v1/traces/ingest",
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

  private keywordsAIExport(item: Trace | Span<any>): Partial<KeywordsPayload> | null {
    // First try the native export method
    if (this.isTrace(item)) {
      // This one is going to be the root trace. The span id will be the trace id
      return {
        trace_unique_id: item.traceId,
        span_unique_id: item.traceId,
        span_name: item.name,
        log_type: "agent",
      };
    } else if (this.isSpan(item)) {
      // Get the span ID - it could be named span_id or id depending on the implementation
      const parentId = item.parentId || item.traceId;

      // Create the base data dictionary with common fields
      const data: Partial<KeywordsPayload> = {
        trace_unique_id: item.traceId,
        span_unique_id: item.spanId,
        span_parent_id: parentId || undefined,
        start_time: item.startedAt || undefined,
        timestamp: item.endedAt || undefined,
        error_bit: item.error ? 1 : 0,
        status_code: item.error ? 400 : 200,
        error_message: item.error ? String(item.error) : undefined,
      };

      if (data.timestamp && data.start_time && data.timestamp instanceof Date && data.start_time instanceof Date) {
        data.latency = (data.timestamp.getTime() - data.start_time.getTime()) / 1000;
      }

      // Process the span data based on its type
      try {
        const spanData = item.spanData;
        
        // Log the span data for debugging
        console.log('Processing span data:', JSON.stringify(spanData, null, 2));
        
        if (this.isResponseSpanData(spanData)) {
          responseDataToKeywordsAILog(data, spanData);
        } else if (this.isFunctionSpanData(spanData)) {
          functionDataToKeywordsAILog(data, spanData);
        } else if (this.isGenerationSpanData(spanData)) {
          generationDataToKeywordsAILog(data, spanData);
        } else if (this.isHandoffSpanData(spanData)) {
          handoffDataToKeywordsAILog(data, spanData);
        } else if (this.isCustomSpanData(spanData)) {
          customDataToKeywordsAILog(data, spanData);
        } else if (this.isAgentSpanData(spanData)) {
          agentDataToKeywordsAILog(data, spanData);
        } else if (this.isGuardrailSpanData(spanData)) {
          guardrailDataToKeywordsAILog(data, spanData);
        } else {
          console.warn(`Unknown span data type:`, spanData);
          return null;
        }
        
        return data;
      } catch (e) {
        console.error(`Error converting span data to KeywordsAI log: ${e}`);
        return null;
      }
    } else {
      return null;
    }
  }

  // Type guards
  private isTrace(item: Trace | Span<any>): item is Trace {
    return 'traceId' in item && 'name' in item && !('spanId' in item);
  }

  private isSpan(item: Trace | Span<any>): item is Span<any> {
    return 'spanId' in item && 'spanData' in item;
  }

  private isResponseSpanData(data: any): data is ResponseSpanData {
    return data && data.type === 'response';
  }

  private isFunctionSpanData(data: any): data is FunctionSpanData {
    return data && data.type === 'function' && typeof data.name === 'string';
  }

  private isGenerationSpanData(data: any): data is GenerationSpanData {
    return data && data.type === 'generation';
  }

  private isHandoffSpanData(data: any): data is HandoffSpanData {
    return data && data.type === 'handoff' && 'from_agent' in data && 'to_agent' in data;
  }

  private isCustomSpanData(data: any): data is CustomSpanData {
    return data && typeof data.name === 'string' && 'data' in data && data.type !== 'agent' && data.type !== 'function' && data.type !== 'response';
  }

  private isAgentSpanData(data: any): data is AgentSpanData {
    return data && data.type === 'agent' && typeof data.name === 'string';
  }

  private isGuardrailSpanData(data: any): data is GuardrailSpanData {
    return data && typeof data.name === 'string' && typeof data.triggered === 'boolean';
  }

  async export(items: (Trace | Span<any>)[], signal?: AbortSignal): Promise<void> {
    if (!items.length) {
      return;
    }

    if (!this.apiKey) {
      console.warn("API key is not set, skipping trace export");
      return;
    }

    // Process each item with our custom exporter
    const processedData = items
      .map(item => this.keywordsAIExport(item))
      .filter((item): item is Partial<KeywordsPayload> => item !== null);

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
          console.error(`Keywords AI client error ${response.status}: ${errorText}`);
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
      await new Promise(resolve => setTimeout(resolve, sleepTime * 1000));
      delay = Math.min(delay * 2, this.maxDelay);
    }
  }
}

export class KeywordsAIOpenAIAgentsTracingExporter extends KeywordsAISpanExporter {
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

export class KeywordsAITraceProcessor extends BatchTraceProcessor {
  private keywordsExporter: KeywordsAISpanExporter;

  constructor({
    apiKey = process.env.KEYWORDSAI_API_KEY || process.env.OPENAI_API_KEY || null,
    organization = process.env.OPENAI_ORG_ID || null,
    project = process.env.OPENAI_PROJECT_ID || null,
    endpoint = process.env.KEYWORDSAI_BASE_URL ? 
      `${process.env.KEYWORDSAI_BASE_URL}/openai/v1/traces/ingest` : 
      "https://api.keywordsai.co/api/openai/v1/traces/ingest",
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
    const exporter = new KeywordsAISpanExporter({
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
