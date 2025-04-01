import { z } from "zod";
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
        ToolUseContentSchema,
        ToolResultContentSchema,
        OutputTextContentSchema,
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

// Posthog integration schema
const PostHogIntegrationSchema = z.object({
  posthog_api_key: z.string().optional(),
  posthog_base_url: z.string().optional(),
});

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

// Main payload schema - with more flexibility to handle various field types
export const KeywordsPayloadSchema = z
  .object({
    // Core fields
    model: z.string(),
    prompt_messages: z.array(MessageSchema),
    completion_message: MessageSchema.optional(),
    completion_messages: z.array(MessageSchema).optional(),

    // Request metadata
    timestamp: DateTimeSchema,
    start_time: DateTimeSchema.optional(),
    customer_identifier: StringOrNumberSchema.default("default_user"),
    thread_identifier: StringOrNumberSchema.optional(),

    // Token counts and costs
    prompt_tokens: z.number(),
    completion_tokens: z.number().optional(),
    prompt_unit_price: z.number().optional(),
    completion_unit_price: z.number().optional(),
    cost: z.number().optional(),

    // Performance metrics
    latency: z.number().optional(),
    time_to_first_token: z.number().optional(),
    routing_time: z.number().optional(),
    tokens_per_second: z.number().optional(),

    // Status and response info
    stream: z.boolean(),

    // Tools and functions
    tools: z.array(z.record(z.any())).optional(),
    tool_calls: z.array(z.record(z.any())).optional(),
    tool_choice: z.union([z.string(), ToolChoiceSchema]).optional(),

    // Customer related
    customer_email: z.string().optional(),
    customer_name: z.string().optional(),
    custom_identifier: StringOrNumberSchema.optional(),

    // Tracing related
    trace_unique_id: z.string().optional(),
    span_unique_id: z.string().optional(),
    span_name: z.string().optional(),
    span_parent_id: z.string().optional(),
    span_path: z.string().optional(),
    span_handoffs: z.array(z.string()).optional(),
    span_tools: z.array(z.string()).optional(),
    span_workflow_name: z.string().optional(),

    // Config and options
    log_type: z.string().optional(),
    posthog_integration: PostHogIntegrationSchema.optional(),

    // Miscellaneous
    metadata: MetadataSchema,
    usage: UsageSchema.optional(),
    full_request: z.union([z.record(z.any()), z.array(z.any())]).optional(),
    full_response: z.union([z.record(z.any()), z.array(z.any())]).optional(),
    environment: z.string().optional(),
  })
  .catchall(z.any());

export type KeywordsPayload = z.infer<typeof KeywordsPayloadSchema>;

