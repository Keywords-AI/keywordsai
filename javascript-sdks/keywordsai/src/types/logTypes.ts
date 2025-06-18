import { z } from "zod";

// Log type definition
export const LOG_TYPE_VALUES = [
  "text",
  "response", 
  "embedding",
  "transcription",
  "speech",
  "workflow",
  "task",
  "tool",
  "agent",
  "handoff",
  "guardrail",
  "function",
  "custom",
  "generation",
  "unknown",
] as const;

export type LogType = typeof LOG_TYPE_VALUES[number];

export const LOG_METHOD_VALUES = [
  "inference",
  "logging_api",
  "batch",
  "python_tracing",
  "ts_tracing",
] as const;

export type LogMethod = typeof LOG_METHOD_VALUES[number];

// Basic utility schemas
const StringOrNumberSchema = z.union([z.string(), z.number()]);
const DateTimeSchema = z.union([z.string(), z.date()]);

// Message content schemas
const ImageURLSchema = z.object({
  url: z.string(),
  detail: z.string().optional(),
});


const CacheControlSchema = z.object({
  type: z.string(),
});

const BaseContentSchema = z.object({
  type: z.string(),
});

const TextContentSchema = BaseContentSchema.extend({
  text: z.string(),
  cache_control: CacheControlSchema.optional(),
});

const ImageContentSchema = BaseContentSchema.extend({
  image_url: z.union([ImageURLSchema, z.string()]),
});


const InputImageSchema = BaseContentSchema.extend({
  file: z.string(),
  providerData: z.record(z.any()).optional(),
});


const FileContentSchema = BaseContentSchema.extend({
  file: z.string(),
  providerData: z.record(z.any()).optional(),
});


const ToolUseContentSchema = BaseContentSchema.extend({
  id: z.string().optional(),
  name: z.string().optional(),
  input: z.record(z.any()).optional(),
});

const ToolResultContentSchema = BaseContentSchema.extend({
  tool_use_id: z.string(),
  content: z.string(),
}).transform((data) => {
  if ("tool_use_id" in data) return data;
  return {
    type: (data as any).type,
    tool_use_id: (data as any).toolCallId,
    content: (data as any).result || (data as any).content,
  };
});

const OutputTextContentSchema = BaseContentSchema.extend({
  text: z.string(),
  annotations: z.array(z.union([z.record(z.any()), z.string()])).optional(),
  cache_control: CacheControlSchema.optional(),
});

// Combined message content schema with transform to handle string content
const MessageContentSchema = z
  .union([
    z.string(),
    z.array(
      z.union([
        TextContentSchema,
        ImageContentSchema,
        FileContentSchema,
        ToolUseContentSchema,
        ToolResultContentSchema,
        OutputTextContentSchema,
        InputImageSchema,
        z.object({
          type: z.string(),
          text: z.string(),
        }),
        // Catch-all for other content types
        z.record(z.any()),
      ])
    ),
  ])
  .transform((content) => {
    if (Array.isArray(content)) {
      // Try to extract text from array of objects with text field
      const textParts = content
        .map((item) => {
          if (typeof item === "object") {
            // Handle both camelCase and snake_case keys
            if ("text" in item) return item.text;
            if ("content" in item && typeof item.content === "string")
              return item.content;
            if ("result" in item && typeof item.result === "string")
              return item.result;
          }
          return null;
        })
        .filter((text) => text !== null);

      if (textParts.length > 0) {
        return textParts.join("\n");
      }
      // Just return the original array if transformation isn't possible
      return content;
    }
    return content;
  });

// Tool related schemas
const ToolCallFunctionSchema = z
  .object({
    name: z.string().optional(),
    arguments: z.union([z.string(), z.record(z.any())]).optional(),
  })
  .catchall(z.any()); // Allow additional properties

const ToolCallSchema = z
  .object({
    type: z.string().default("function"), // Only require type, default to "function"
    id: z.string().optional(),
    function: ToolCallFunctionSchema.optional(),
  })
  .catchall(z.any()) // Allow any additional properties
  .transform((data) => {
    // Create a shallow copy to avoid modifying the original
    const result: Record<string, any> = { ...data };
    
    // Handle ID mapping for consistency (only if needed)
    if (!result.id && ((data as any).toolCallId || (data as any).tool_call_id)) {
      result.id = (data as any).toolCallId || (data as any).tool_call_id;
    }
    
    // If we have args/toolName but no function object, create basic structure
    if (((data as any).toolName || (data as any).name || (data as any).args) && !result.function) {
      result.function = {};
      
      if ((data as any).toolName || (data as any).name) {
        result.function.name = (data as any).toolName || (data as any).name;
      }
      
      if ((data as any).args) {
        result.function.arguments = typeof (data as any).args === 'string' 
          ? (data as any).args 
          : JSON.stringify((data as any).args);
      }
    }
    
    return result;
  });

const ToolChoiceSchema = z
  .object({
    type: z.string(),
    function: z
      .object({
        name: z.string(),
      })
      .optional(),
  })
  .optional();

// Function tool schema for BasicLLMParams
const FunctionToolSchema = z.object({
  type: z.literal("function"),
  function: z.object({
    name: z.string(),
    description: z.string().optional(),
    parameters: z.record(z.any()).optional(),
  }),
});

// Base message schema with flexible role
const MessageSchema = z
  .object({
    role: z.string(),
    content: MessageContentSchema.optional(),
    name: z.string().optional(),
    tool_call_id: z.string().optional(),
    tool_calls: z.array(ToolCallSchema).optional(),
    experimental_providerMetadata: z
      .object({
        anthropic: z.object({
          cacheControl: z.object({
            type: z.string(),
          }),
        }),
      })
      .optional(),
  })
  .transform((data) => {
    // Handle camelCase to snake_case conversion
    if ("toolCallId" in data) {
      return {
        ...data,
        tool_call_id: data.toolCallId,
      };
    }
    return data;
  });

// Metadata schema
const MetadataSchema = z.record(z.any()).optional();

// Usage schema
const UsageSchema = z.object({
  prompt_tokens: z.number().optional(),
  completion_tokens: z.number().optional(),
  total_tokens: z.number().optional(),
  cache_creation_input_tokens: z.number().optional(),
  cache_creation_prompt_tokens: z.number().optional(),
  cache_read_input_tokens: z.number().optional(),
  completion_tokens_details: z.record(z.any()).optional(),
  prompt_tokens_details: z.record(z.any()).optional(),
});

// Supporting schemas for KeywordsAI params
const OverrideConfigSchema = z.object({
  messages_override_mode: z.enum(["override", "append"]).optional().default("override"),
});

const EvaluatorToRunSchema = z.record(z.any()); // Placeholder for evaluator schema
const EvalInputsSchema = z.record(z.any()); // Placeholder for eval inputs schema

const EvaluationParamsSchema = z.object({
  evaluators: z.array(EvaluatorToRunSchema).optional().default([]),
  evaluation_identifier: StringOrNumberSchema.default(""),
  last_n_messages: z.number().optional().default(1),
  eval_inputs: EvalInputsSchema.optional().default({}),
  sample_percentage: z.number().optional(),
});

const LoadBalanceModelSchema = z.object({
  model: z.string(),
  credentials: z.record(z.any()).optional(),
  weight: z.number().refine((val) => val > 0, "Weight has to be greater than 0"),
});

const LoadBalanceGroupSchema = z.object({
  group_id: z.string(),
  models: z.array(LoadBalanceModelSchema).optional(),
});

const PostHogIntegrationSchema = z.object({
  posthog_api_key: z.string(),
  posthog_base_url: z.string(),
});

const CustomerSchema = z.object({
  customer_identifier: StringOrNumberSchema.optional(),
  name: z.string().optional(),
  email: z.string().optional(),
  period_start: DateTimeSchema.optional(),
  period_end: DateTimeSchema.optional(),
  budget_duration: z.enum(["daily", "weekly", "monthly", "yearly"]).optional(),
  period_budget: z.number().optional(),
  markup_percentage: z.number().optional(),
  total_budget: z.number().optional(),
  metadata: z.record(z.any()).optional(),
  rate_limit: z.number().optional(),
});

const CacheOptionsSchema = z.object({
  cache_by_customer: z.boolean().optional(),
  omit_log: z.boolean().optional(),
});

const RetryParamsSchema = z.object({
  num_retries: z.number().optional().default(3).refine((val) => val > 0, "num_retries has to be greater than 0"),
  retry_after: z.number().optional().default(0.2).refine((val) => val > 0, "retry_after has to be greater than 0"),
  retry_enabled: z.boolean().optional().default(true),
});

const KeywordsAIAPIControlParamsSchema = z.object({
  block: z.boolean().optional(),
});

const PromptParamSchema = z.object({
  prompt_id: z.string().optional(),
  is_custom_prompt: z.boolean().optional().default(false),
  version: z.number().optional(),
  variables: z.record(z.any()).optional(),
  echo: z.boolean().optional().default(true),
  override: z.boolean().optional().default(false),
  override_params: z.record(z.any()).optional(), // BasicLLMParams placeholder
  override_config: OverrideConfigSchema.optional(),
});

const LinkupParamsSchema = z.record(z.any()); // Placeholder
const Mem0ParamsSchema = z.record(z.any()); // Placeholder
const ProviderCredentialTypeSchema = z.record(z.any()); // Placeholder

// Basic LLM Parameters Schema
const BasicLLMParamsSchema = z.object({
  echo: z.boolean().optional(),
  frequency_penalty: z.number().optional(),
  logprobs: z.boolean().optional(),
  logit_bias: z.record(z.number()).optional(),
  messages: z.array(MessageSchema).optional(),
  model: z.string().optional(),
  max_tokens: z.number().optional(),
  max_completion_tokens: z.number().optional(),
  n: z.number().optional(),
  parallel_tool_calls: z.boolean().optional(),
  presence_penalty: z.number().optional(),
  stop: z.union([z.array(z.string()), z.string()]).optional(),
  stream: z.boolean().optional(),
  stream_options: z.record(z.any()).optional(),
  temperature: z.number().optional(),
  timeout: z.number().optional(),
  tools: z.array(FunctionToolSchema).optional(),
  response_format: z.record(z.any()).optional(),
  reasoning_effort: z.string().optional(),
  tool_choice: z.union([z.enum(["auto", "none", "required"]), ToolChoiceSchema]).optional(),
  top_logprobs: z.number().optional(),
  top_p: z.number().optional(),
});

// Basic Embedding Parameters Schema (placeholder)
const BasicEmbeddingParamsSchema = z.object({
  input: z.union([z.string(), z.array(z.string())]).optional(),
  model: z.string().optional(),
  encoding_format: z.string().optional(),
  dimensions: z.number().optional(),
  user: z.string().optional(),
});

// KeywordsAI Parameters Schema with regions
const KeywordsAIParamsSchema = z.object({
  //#region time
  start_time: DateTimeSchema.optional(),
  timestamp: DateTimeSchema.optional(),
  hour_group: DateTimeSchema.optional(),
  minute_group: DateTimeSchema.optional(),
  //#endregion time

  //#region authentication
  api_key: z.string().optional(),
  user_id: StringOrNumberSchema.optional(),
  user_email: z.string().optional(),
  organization_id: StringOrNumberSchema.optional(),
  organization_name: z.string().optional(),
  unique_organization_id: z.string().optional(),
  organization_key_id: z.string().optional(),
  organization_key_name: z.string().optional(),
  //#endregion authentication

  //#region environment
  is_test: z.boolean().optional(),
  environment: z.string().optional(),
  //#endregion environment

  //#region unique identifiers
  id: StringOrNumberSchema.optional(),
  unique_id: z.string().optional(),
  custom_identifier: StringOrNumberSchema.optional(),
  response_id: z.string().optional(),
  //#endregion unique identifiers

  //#region status
  //#region error handling
  error_bit: z.number().optional(),
  error_message: z.string().optional(),
  recommendations: z.string().optional(),
  recommendations_dict: z.record(z.any()).optional(),
  warnings: z.string().optional(),
  warnings_dict: z.record(z.any()).optional(),
  has_warnings: z.boolean().optional(),
  //#endregion error handling
  status: z.string().optional(),
  status_code: z.number().optional(),
  //#endregion status

  //#region log identifier/grouping
  load_balance_group_id: z.string().optional(),
  group_identifier: StringOrNumberSchema.optional(),
  evaluation_identifier: StringOrNumberSchema.optional(),
  //#endregion log identifier/grouping

  //#region log input/output
  storage_object_key: z.string().optional(),
  input: z.string().optional(),
  output: z.string().optional(),
  prompt_messages: z.array(MessageSchema).optional(),
  completion_message: MessageSchema.optional(),
  completion_messages: z.array(MessageSchema).optional(),
  completion_tokens: z.number().optional(),
  system_text: z.string().optional(),
  prompt_text: z.string().optional(),
  completion_text: z.string().optional(),
  input_array: z.array(z.string()).optional(),
  full_request: z.union([z.record(z.any()), z.array(z.any())]).optional(),
  full_response: z.union([z.record(z.any()), z.array(z.any())]).optional(),
  is_fts_enabled: z.boolean().optional(),
  full_text: z.string().optional(),
  //#region special response types
  tool_calls: z.array(z.record(z.any())).optional(),
  has_tool_calls: z.boolean().optional(),
  reasoning: z.array(z.record(z.any())).optional(),
  //#endregion special response types
  //#endregion log input/output

  //#region display
  blurred: z.boolean().optional(),
  //#endregion display

  //#region cache params
  cache_enabled: z.boolean().optional(),
  cache_hit: z.boolean().optional(),
  cache_bit: z.number().optional(),
  cache_miss_bit: z.number().optional(),
  cache_options: CacheOptionsSchema.optional(),
  cache_ttl: z.number().optional(),
  cache_key: z.string().optional(),
  redis_cache_ttl: z.number().optional(),
  cache_request_content: z.string().optional(),
  //#endregion cache params

  //#region usage
  //#region cost related
  cost: z.number().optional(),
  covered_by: z.string().optional(),
  evaluation_cost: z.number().optional(),
  prompt_unit_price: z.number().optional(),
  completion_unit_price: z.number().optional(),
  used_custom_credential: z.boolean().optional(),
  //#endregion cost related

  //#region time period
  period_start: DateTimeSchema.optional(),
  period_end: DateTimeSchema.optional(),
  //#endregion time period

  //#region token usage
  prompt_tokens: z.number().optional(),
  prompt_cache_hit_tokens: z.number().optional(),
  prompt_cache_creation_tokens: z.number().optional(),
  usage: UsageSchema.optional(),
  //#endregion token usage
  //#endregion usage

  //#region llm proxy credentials
  credential_override: z.record(z.record(z.any())).optional(),
  customer_credentials: z.record(ProviderCredentialTypeSchema).optional(),
  //#endregion llm proxy credentials

  //#region llm deployment
  models: z.array(z.string()).optional(),
  model_name_map: z.record(z.string()).optional(),
  deployment_name: z.string().optional(),
  full_model_name: z.string().optional(),
  //#endregion llm deployment

  //#region user analytics
  customer_email: z.string().optional(),
  customer_name: z.string().optional(),
  customer_identifier: StringOrNumberSchema.optional(),
  customer_user_unique_id: z.string().optional(),
  customer_params: CustomerSchema.optional(),
  //#endregion user analytics

  //#region keywordsai llm response control
  field_name: z.string().optional().default("data: "),
  delimiter: z.string().optional().default("\n\n"),
  disable_log: z.boolean().optional().default(false),
  request_breakdown: z.boolean().optional().default(false),
  //#endregion keywordsai llm response control

  //#region keywordsai logging control
  is_log_omitted: z.boolean().optional(),
  keywordsai_api_controls: KeywordsAIAPIControlParamsSchema.optional(),
  mock_response: z.string().optional(),
  log_method: z.enum(LOG_METHOD_VALUES).optional(),
  log_type: z.enum(LOG_TYPE_VALUES).optional(),
  //#endregion keywordsai logging control

  //#region keywordsai proxy options
  disable_fallback: z.boolean().optional().default(false),
  exclude_models: z.array(z.string()).optional(),
  exclude_providers: z.array(z.string()).optional(),
  fallback_models: z.array(z.string()).optional(),
  load_balance_group: LoadBalanceGroupSchema.optional(),
  load_balance_models: z.array(LoadBalanceModelSchema).optional(),
  retry_params: RetryParamsSchema.optional(),
  keywordsai_params: z.record(z.any()).optional(),
  //#endregion keywordsai proxy options

  //#region embedding
  embedding: z.array(z.number()).optional(),
  base64_embedding: z.string().optional(),
  provider_id: z.string().optional(),
  //#endregion embedding

  //#region audio
  audio_input_file: z.string().optional(),
  audio_output_file: z.string().optional(),
  //#endregion audio

  //#region evaluation
  note: z.string().optional(),
  category: z.string().optional(),
  eval_params: EvaluationParamsSchema.optional(),
  for_eval: z.boolean().optional(),
  positive_feedback: z.boolean().optional(),
  //#endregion evaluation

  //#region request metadata
  ip_address: z.string().optional(),
  request_url_path: z.string().optional(),
  //#endregion request metadata

  //#region technical integrations
  linkup_params: LinkupParamsSchema.optional(),
  mem0_params: Mem0ParamsSchema.optional(),
  posthog_integration: PostHogIntegrationSchema.optional(),
  //#endregion technical integrations

  //#region custom properties
  metadata: z.record(z.any()).optional(),
  //#region Deprecated, clickhouse allow filters to be applied efficiently enough
  metadata_indexed_string_1: z.string().optional(),
  metadata_indexed_string_2: z.string().optional(),
  metadata_indexed_numerical_1: z.number().optional(),
  //#endregion deprecated
  //#endregion custom properties

  //#region prompt
  prompt: z.union([PromptParamSchema, z.string()]).optional(),
  prompt_id: z.string().optional(),
  prompt_name: z.string().optional(),
  prompt_version_number: z.number().optional(),
  prompt_messages_template: z.array(MessageSchema).optional(),
  variables: z.record(z.any()).optional(),
  //#endregion prompt

  //#region llm response timing metrics
  generation_time: z.number().optional(),
  latency: z.number().optional(),
  ttft: z.number().optional(),
  time_to_first_token: z.number().optional(),
  routing_time: z.number().optional(),
  tokens_per_second: z.number().optional(),
  //#endregion llm response timing metrics

  //#region tracing
  total_request_tokens: z.number().optional(),
  trace_unique_id: z.string().optional(),
  trace_name: z.string().optional(),
  trace_group_identifier: z.string().optional(),
  span_unique_id: z.string().optional(),
  span_name: z.string().optional(),
  span_parent_id: z.string().optional(),
  span_path: z.string().optional(),
  span_handoffs: z.array(z.string()).optional(),
  span_tools: z.array(z.string()).optional(),
  span_workflow_name: z.string().optional(),

  //#region thread, deprecated
  thread_identifier: StringOrNumberSchema.optional(),
  thread_unique_id: z.string().optional(),
  //#endregion thread, deprecated

  //#endregion tracing
});

// Combined KeywordsPayloadSchema that merges KeywordsAIParams, BasicLLMParams, and BasicEmbeddingParams
export const KeywordsPayloadSchema = KeywordsAIParamsSchema
  .merge(BasicLLMParamsSchema)
  .merge(BasicEmbeddingParamsSchema)
  .catchall(z.any());

export type KeywordsPayload = z.infer<typeof KeywordsPayloadSchema>;

// Export individual schemas for use elsewhere
export { 
  KeywordsAIParamsSchema, 
  BasicLLMParamsSchema, 
  BasicEmbeddingParamsSchema,
  MessageSchema,
  ToolCallSchema,
  ToolChoiceSchema,
  FunctionToolSchema,
  UsageSchema,
  MetadataSchema,
  PostHogIntegrationSchema,
  CustomerSchema,
  CacheOptionsSchema,
  RetryParamsSchema,
  LoadBalanceGroupSchema,
  LoadBalanceModelSchema,
  EvaluationParamsSchema,
  PromptParamSchema,
  OverrideConfigSchema,
};

