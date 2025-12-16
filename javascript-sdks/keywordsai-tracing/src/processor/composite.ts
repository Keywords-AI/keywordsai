import { Context } from "@opentelemetry/api";
import {
  SpanProcessor,
  ReadableSpan,
} from "@opentelemetry/sdk-trace-base";
import { SpanAttributes } from "@traceloop/ai-semantic-conventions";
import { MultiProcessorManager } from "./manager.js";
import { getEntityPath } from "../utils/context.js";

/**
 * Composite processor that combines filtering with multi-processor routing.
 * 
 * Flow:
 * 1. Filter spans (keep only user-decorated spans and their children)
 * 2. Apply postprocess callback if configured
 * 3. Route filtered spans to appropriate processors
 * 
 * This ensures only meaningful spans are routed to processors.
 */
export class KeywordsAICompositeProcessor implements SpanProcessor {
  private readonly _processorManager: MultiProcessorManager;
  private readonly _postprocessCallback?: (span: ReadableSpan) => void;

  constructor(
    processorManager: MultiProcessorManager,
    postprocessCallback?: (span: ReadableSpan) => void
  ) {
    this._processorManager = processorManager;
    this._postprocessCallback = postprocessCallback;
  }

  onStart(span: ReadableSpan, parentContext: Context): void {
    // Check if this span is being created within an entity context
    // If so, add the entityPath attribute so it gets preserved by our filtering
    const entityPath = getEntityPath(parentContext);
    if (entityPath && !span.attributes[SpanAttributes.TRACELOOP_SPAN_KIND]) {
      // This is an auto-instrumentation span within an entity context
      // Add the entityPath attribute so it doesn't get filtered out
      console.debug(
        `[KeywordsAI Debug] Adding entityPath to auto-instrumentation span: ${span.name} (entityPath: ${entityPath})`
      );
      
      // We need to cast to any to set attributes during onStart
      (span as any).setAttribute(SpanAttributes.TRACELOOP_ENTITY_PATH, entityPath);
    }
    
    // Forward to processor manager
    this._processorManager.onStart(span, parentContext);
  }

  onEnd(span: ReadableSpan): void {
    const spanKind = span.attributes[SpanAttributes.TRACELOOP_SPAN_KIND];
    const entityPath = span.attributes[SpanAttributes.TRACELOOP_ENTITY_PATH];
    
    // Apply postprocess callback if provided
    if (this._postprocessCallback) {
      try {
        this._postprocessCallback(span);
      } catch (error) {
        console.error("[KeywordsAI] Error in span postprocess callback:", error);
      }
    }
    
    // Filter: only process spans that are user-decorated or within entity context
    if (spanKind) {
      // This is a user-decorated span (withWorkflow, withTask, etc.) - make it a root span
      console.debug(
        `[KeywordsAI Debug] Processing user-decorated span as root: ${span.name} (kind: ${spanKind})`
      );

      // Create a wrapper that makes the span appear as a root span
      const rootSpan = Object.create(Object.getPrototypeOf(span));
      Object.assign(rootSpan, span);
      
      // Override the parentSpanId to make it a root span
      Object.defineProperty(rootSpan, 'parentSpanId', {
        value: undefined,
        writable: false,
        configurable: true,
        enumerable: true
      });

      // Route to processors
      this._processorManager.onEnd(rootSpan);
    } else if (entityPath && entityPath !== "") {
      // This span doesn't have a kind but has entityPath - it's a child span within a withEntity context
      // Keep it as a normal child span (preserve parent relationships)
      console.debug(
        `[KeywordsAI Debug] Processing child span within entity context: ${span.name} (entityPath: ${entityPath})`
      );
      
      // Route to processors
      this._processorManager.onEnd(span);
    } else {
      // This span has neither kind nor entityPath - it's pure auto-instrumentation noise
      console.debug(
        `[KeywordsAI Debug] Filtering out auto-instrumentation span: ${span.name} (no TRACELOOP_SPAN_KIND or entityPath)`
      );
    }
  }

  async shutdown(): Promise<void> {
    await this._processorManager.shutdown();
  }

  async forceFlush(): Promise<void> {
    await this._processorManager.forceFlush();
  }

  /**
   * Get the entity path from context
   */
  // Removed - now using imported getEntityPath function

  /**
   * Get the processor manager (for adding new processors)
   */
  public getProcessorManager(): MultiProcessorManager {
    return this._processorManager;
  }
}
