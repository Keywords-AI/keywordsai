import { trace, Tracer, Span, SpanStatusCode } from "@opentelemetry/api";
import { KEYWORDSAI_PACKAGE_NAME } from "../constants/index.js";
import {
  KeywordsAIParamsSchema,
  KeywordsAISpanAttributes,
  KEYWORDSAI_SPAN_ATTRIBUTES_MAP,
} from "@keywordsai/keywordsai-sdk";

// Global tracer instance (singleton)
let _tracer: Tracer;

/**
 * Gets the singleton tracer instance.
 * The tracer is responsible for creating and managing spans.
 *
 * @returns The global tracer instance
 */
export const getTracer = (): Tracer => {
  if (!_tracer) {
    // Create tracer with a unique name for this SDK
    _tracer = trace.getTracer(KEYWORDSAI_PACKAGE_NAME);
  }
  return _tracer;
};

/**
 * Gets the currently active span from the context.
 * This is the span that's currently being executed.
 *
 * @returns The active span or undefined if no span is active
 */
export const getCurrentSpan = () => {
  return trace.getActiveSpan();
};

/**
 * Update the current active span with new information.
 * This is the JavaScript equivalent of the Python update_current_span method.
 *
 * @param options - Configuration object for updating the span
 * @returns True if the span was updated successfully, False otherwise
 */
export const updateCurrentSpan = (
  options: {
    keywordsaiParams?: Record<string, any>;
    attributes?: Record<string, string | number | boolean>;
    status?: SpanStatusCode;
    statusDescription?: string;
    name?: string;
  } = {}
): boolean => {
  const currentSpan = getCurrentSpan();
  if (!currentSpan) {
    console.debug(
      "[KeywordsAI Debug] No active span found. Cannot update span."
    );
    return false;
  }

  try {
    const { keywordsaiParams, attributes, status, statusDescription, name } =
      options;

    console.debug("[KeywordsAI Debug] Updating current span with:", {
      hasKeywordsaiParams: !!keywordsaiParams,
      keywordsaiParamsKeys: keywordsaiParams
        ? Object.keys(keywordsaiParams)
        : [],
      hasAttributes: !!attributes,
      attributesKeys: attributes ? Object.keys(attributes) : [],
      hasStatus: status !== undefined,
      status,
      statusDescription,
      newName: name,
    });

    // Update span name if provided
    if (name) {
      currentSpan.updateName(name);
      console.debug(`[KeywordsAI Debug] Updated span name to: ${name}`);
    }

    // Set KeywordsAI-specific attributes
    if (keywordsaiParams) {
      setKeywordsAIAttributes(currentSpan, keywordsaiParams);
    }

    // Set generic attributes
    if (attributes) {
      Object.entries(attributes).forEach(([key, value]) => {
        try {
          currentSpan.setAttribute(key, value);
          console.debug(`[KeywordsAI Debug] Set attribute: ${key}=${value}`);
        } catch (error) {
          console.warn(
            `[KeywordsAI Debug] Failed to set attribute ${key}=${value}:`,
            error
          );
        }
      });
    }

    // Set status
    if (status !== undefined) {
      currentSpan.setStatus({
        code: status,
        message: statusDescription,
      });
      console.debug(
        `[KeywordsAI Debug] Set span status: ${status}${
          statusDescription ? ` (${statusDescription})` : ""
        }`
      );
    }

    return true;
  } catch (error) {
    console.error("[KeywordsAI Debug] Failed to update span:", error);
    return false;
  }
};

/**
 * Set KeywordsAI-specific attributes on a span.
 * This is the JavaScript equivalent of the Python _set_keywordsai_attributes method.
 * Uses the imported KEYWORDSAI_SPAN_ATTRIBUTES_MAP and validates with KeywordsAIParamsSchema.
 *
 * @param span - The span to set attributes on
 * @param keywordsaiParams - KeywordsAI parameters to set as span attributes
 */
const setKeywordsAIAttributes = (
  span: Span,
  keywordsaiParams: Record<string, any>
): void => {
  try {
    console.debug(
      "[KeywordsAI Debug] Setting KeywordsAI attributes:",
      keywordsaiParams
    );

    // Validate parameters using the imported schema
    let validatedParams: Record<string, any>;
    try {
      validatedParams = KeywordsAIParamsSchema.parse(keywordsaiParams);
      console.debug("[KeywordsAI Debug] Parameters validated successfully");
    } catch (validationError) {
      console.warn(
        "[KeywordsAI Debug] Failed to validate KeywordsAI params:",
        validationError
      );
      // Use original params if validation fails, but continue processing
      validatedParams = keywordsaiParams;
    }

    // Set attributes based on the imported mapping
    Object.entries(validatedParams).forEach(([key, value]) => {
      if (key in KEYWORDSAI_SPAN_ATTRIBUTES_MAP && key !== "metadata") {
        try {
          const attributeKey = KEYWORDSAI_SPAN_ATTRIBUTES_MAP[key];
          span.setAttribute(attributeKey, value);
          console.debug(
            `[KeywordsAI Debug] Set KeywordsAI attribute: ${attributeKey}=${value}`
          );
        } catch (error) {
          console.warn(
            `[KeywordsAI Debug] Failed to set span attribute ${KEYWORDSAI_SPAN_ATTRIBUTES_MAP[key]}=${value}:`,
            error
          );
        }
      }

      // Handle metadata specially using the proper enum
      if (key === "metadata" && typeof value === "object" && value !== null) {
        console.debug("[KeywordsAI Debug] Setting metadata attributes:", value);
        Object.entries(value as Record<string, any>).forEach(
          ([metadataKey, metadataValue]) => {
            try {
              const fullKey = `${KeywordsAISpanAttributes.KEYWORDSAI_METADATA}.${metadataKey}`;
              span.setAttribute(fullKey, metadataValue);
              console.debug(
                `[KeywordsAI Debug] Set metadata attribute: ${fullKey}=${metadataValue}`
              );
            } catch (error) {
              console.warn(
                `[KeywordsAI Debug] Failed to set metadata attribute ${metadataKey}=${metadataValue}:`,
                error
              );
            }
          }
        );
      }
    });
  } catch (error) {
    console.error(
      "[KeywordsAI Debug] Unexpected error setting KeywordsAI attributes:",
      error
    );
  }
};

/**
 * Adds an event to the currently active span.
 * Events are timestamped messages that provide additional context.
 *
 * @param name - Name of the event
 * @param attributes - Optional attributes for the event
 * @returns true if event was added, false if no active span
 */
export const addSpanEvent = (
  name: string,
  attributes?: Record<string, string | number | boolean>
): boolean => {
  const currentSpan = getCurrentSpan();
  if (!currentSpan) {
    console.warn("No active span to add event to");
    return false;
  }

  try {
    currentSpan.addEvent(name, attributes);
    return true;
  } catch (error) {
    console.error("Error adding span event:", error);
    return false;
  }
};

/**
 * Records an exception in the currently active span.
 * This is useful for capturing errors that don't necessarily end the span.
 *
 * @param exception - The error/exception to record
 * @returns true if exception was recorded, false if no active span
 */
export const recordSpanException = (exception: Error): boolean => {
  const currentSpan = getCurrentSpan();
  if (!currentSpan) {
    console.warn("No active span to record exception in");
    return false;
  }

  try {
    currentSpan.recordException(exception);
    return true;
  } catch (error) {
    console.error("Error recording span exception:", error);
    return false;
  }
};

/**
 * Sets the status of the currently active span.
 * This indicates whether the operation succeeded or failed.
 *
 * @param status - The status to set (OK or ERROR)
 * @param message - Optional message describing the status
 * @returns true if status was set, false if no active span
 */
export const setSpanStatus = (
  status: "OK" | "ERROR",
  message?: string
): boolean => {
  const currentSpan = getCurrentSpan();
  if (!currentSpan) {
    console.warn("No active span to set status on");
    return false;
  }

  try {
    currentSpan.setStatus({
      code: status === "OK" ? SpanStatusCode.OK : SpanStatusCode.ERROR,
      message,
    });
    return true;
  } catch (error) {
    console.error("Error setting span status:", error);
    return false;
  }
};

/**
 * Creates a manual span for custom tracing.
 * This is useful when you need to trace operations that aren't wrapped by withEntity.
 *
 * @param name - Name of the span
 * @param fn - Function to execute within the span
 * @param attributes - Optional attributes for the span
 * @returns The result of the function
 */
export const withManualSpan = <T>(
  name: string,
  fn: (span: import("@opentelemetry/api").Span) => T,
  attributes?: Record<string, string | number | boolean>
): T => {
  return getTracer().startActiveSpan(name, {}, (span) => {
    try {
      // Add attributes if provided
      if (attributes) {
        Object.entries(attributes).forEach(([key, value]) => {
          span.setAttribute(key, value);
        });
      }

      const result = fn(span);

      // Handle promises
      if (result instanceof Promise) {
        return result
          .then((res) => {
            span.setStatus({ code: SpanStatusCode.OK });
            span.end();
            return res;
          })
          .catch((error) => {
            span.recordException(error);
            span.setStatus({
              code: SpanStatusCode.ERROR,
              message: error.message,
            });
            span.end();
            throw error;
          }) as T;
      }

      // Handle synchronous results
      span.setStatus({ code: SpanStatusCode.OK });
      span.end();
      return result;
    } catch (error) {
      span.recordException(error as Error);
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: (error as Error).message,
      });
      span.end();
      throw error;
    }
  });
}; 