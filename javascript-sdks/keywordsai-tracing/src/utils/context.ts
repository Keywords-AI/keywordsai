import { context, Context, createContextKey } from "@opentelemetry/api";
import { SpanAttributes } from "@traceloop/ai-semantic-conventions";

/**
 * Context Keys: Type-safe identifiers for storing values in OpenTelemetry context
 *
 * Why context keys are needed:
 * 1. Type safety - prevents runtime errors from typos in key names
 * 2. Namespace isolation - prevents key collisions between different libraries
 * 3. Hierarchical data flow - allows parent spans to pass data to child spans
 * 4. Cross-cutting concerns - enables data to flow across async boundaries
 */

// Stores the name of the current workflow (top-level operation)
export const WORKFLOW_NAME_KEY = createContextKey(
  SpanAttributes.TRACELOOP_WORKFLOW_NAME
);

// Stores the hierarchical path of the current entity (e.g., "workflow.task.subtask")
export const ENTITY_NAME_KEY = createContextKey(
  SpanAttributes.TRACELOOP_ENTITY_NAME
);

// Stores custom properties for associating related spans
export const ASSOCIATION_PROPERTIES_KEY = createContextKey(
  SpanAttributes.TRACELOOP_ASSOCIATION_PROPERTIES
);

/**
 * Retrieves the current entity path from the active context.
 * This builds the hierarchical path like "workflow.task.subtask".
 *
 * @param ctx - The context to read from (defaults to current active context)
 * @returns The entity path string or undefined if not set
 */
export const getEntityPath = (ctx = context.active()): string | undefined => {
  // First check for full entity name (set by TOOL/TASK spans)
  const entityName = ctx.getValue(ENTITY_NAME_KEY) as string | undefined;
  if (entityName) {
    return entityName;
  }
  
  // Fall back to workflow name (set by WORKFLOW/AGENT spans)
  const workflowName = ctx.getValue(WORKFLOW_NAME_KEY) as string | undefined;
  return workflowName;
};

/**
 * Determines whether trace content (input/output data) should be captured.
 * This can be controlled via environment variable for security/privacy.
 *
 * @returns true if traces should include content, false otherwise
 */
export const shouldSendTraces = (): boolean => {
  return process.env.KEYWORDSAI_TRACE_CONTENT !== "false";
}; 