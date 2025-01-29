import { trace, context, AttributeValue } from '@opentelemetry/api';
import { KeywordsAIParams } from '../types/baseTypes';
import { KEYWORDSAI_SPAN_ATTRIBUTES_MAP } from '../types/spanTypes';

/**
 * A context manager for setting KeywordsAI-specific attributes on the current span
 * 
 * @param fn - The function to execute within the context
 * @param params - Dictionary of parameters to set as span attributes
 * @returns The result of the function execution
 */
export async function withKeywordsAISpanAttributes<T>(
    fn: () => Promise<T> | T,
    params: Partial<KeywordsAIParams>
): Promise<T> {
    const currentSpan = trace.getSpan(context.active());
    
    if (!currentSpan) {
        console.warn("No active span found. Attributes will not be set.");
        return fn();
    }

    // Set attributes first, but don't let errors block execution
    try {
        Object.entries(params).forEach(([key, value]) => {
            if (key in KEYWORDSAI_SPAN_ATTRIBUTES_MAP && key !== "metadata") {
                try {
                    currentSpan.setAttribute(KEYWORDSAI_SPAN_ATTRIBUTES_MAP[key], value as AttributeValue);
                } catch (e) {
                    console.warn(`Failed to set span attribute ${KEYWORDSAI_SPAN_ATTRIBUTES_MAP[key]}=${value}: ${e}`);
                }
            }
        });

        if (params.metadata) {
            Object.entries(params.metadata).forEach(([key, value]) => {
                currentSpan.setAttribute(
                    `${KEYWORDSAI_SPAN_ATTRIBUTES_MAP.metadata}.${key}`,
                    JSON.stringify(value)
                );
            });
        }
    } catch (e) {
        console.warn(`Error setting span attributes: ${e}`);
    }

    return fn();
}
