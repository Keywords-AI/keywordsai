import { NodeSDK } from "@opentelemetry/sdk-node";
import { context, diag, trace, Tracer, createContextKey, DiagLogLevel, SpanStatusCode, Span } from "@opentelemetry/api";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-proto";
import { Resource } from "@opentelemetry/resources";
import { ATTR_SERVICE_NAME } from "@opentelemetry/semantic-conventions";
import { Instrumentation } from "@opentelemetry/instrumentation";
import { KeywordsAIOptions } from "../types/clientTypes";
import { KeywordsAIParamsSchema, KeywordsAISpanAttributes, KEYWORDSAI_SPAN_ATTRIBUTES_MAP } from "@keywordsai/keywordsai-sdk";
import { SpanAttributes } from "@traceloop/ai-semantic-conventions";

// Global SDK and tracer instances (singletons)
// These are module-level variables that persist across function calls
let _sdk: NodeSDK;
let _tracer: Tracer;
let _initialized: boolean = false;

// Array to hold all instrumentations that will be loaded dynamically
const instrumentations: Instrumentation[] = [];

// Store instrumentation instances for configuration
let openAIInstrumentation: any | undefined;
let anthropicInstrumentation: any | undefined;
let azureOpenAIInstrumentation: any | undefined;
let cohereInstrumentation: any | undefined;
let vertexaiInstrumentation: any | undefined;
let bedrockInstrumentation: any | undefined;
let langchainInstrumentation: any | undefined;
let llamaIndexInstrumentation: any | undefined;
let pineconeInstrumentation: any | undefined;
let chromadbInstrumentation: any | undefined;
let qdrantInstrumentation: any | undefined;
let togetherInstrumentation: any | undefined;

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
export const WORKFLOW_NAME_KEY = createContextKey(SpanAttributes.TRACELOOP_WORKFLOW_NAME);

// Stores the hierarchical path of the current entity (e.g., "workflow.task.subtask")
export const ENTITY_NAME_KEY = createContextKey(SpanAttributes.TRACELOOP_ENTITY_NAME);

// Stores custom properties for associating related spans
export const ASSOCIATION_PROPERTIES_KEY = createContextKey(SpanAttributes.TRACELOOP_ASSOCIATION_PROPERTIES);

/**
 * Gets the singleton tracer instance.
 * The tracer is responsible for creating and managing spans.
 * 
 * @returns The global tracer instance
 */
export const getTracer = (): Tracer => {
  if (!_tracer) {
    // Create tracer with a unique name for this SDK
    _tracer = trace.getTracer("@keywordsai/tracing");
  }
  return _tracer;
};

/**
 * Retrieves the current entity path from the active context.
 * This builds the hierarchical path like "workflow.task.subtask".
 * 
 * @param ctx - The context to read from (defaults to current active context)
 * @returns The entity path string or undefined if not set
 */
export const getEntityPath = (ctx = context.active()): string | undefined => {
  return ctx.getValue(ENTITY_NAME_KEY) as string | undefined;
};

/**
 * Determines whether trace content (input/output data) should be captured.
 * This can be controlled via environment variable for security/privacy.
 * 
 * @returns true if traces should include content, false otherwise
 */
export const shouldSendTraces = (): boolean => {
  return process.env.KEYWORDS_AI_TRACE_CONTENT !== "false";
};

/**
 * Initialize all available instrumentations automatically.
 * This is used when no specific instrumentModules are provided.
 */
const initInstrumentations = async () => {
  const exceptionLogger = (e: Error) => console.error("Instrumentation error:", e);

  // Clear the instrumentations array
  instrumentations.length = 0;

  // Add HTTP instrumentation to capture all HTTP requests
  try {
    const { HttpInstrumentation } = await import("@opentelemetry/instrumentation-http");
    console.log("Loading HTTP instrumentation");
    const httpInstrumentation = new HttpInstrumentation({
      ignoreIncomingRequestHook: (req) => {
        // Don't instrument incoming requests to avoid noise
        return true;
      },
      ignoreOutgoingRequestHook: (options) => {
        // Log all outgoing requests for debugging
        const url = typeof options === 'string' ? options : (options as any).hostname || (options as any).host;
        return false;
      }
    });
    instrumentations.push(httpInstrumentation);
    console.log("Added HTTP instrumentation");
  } catch (error) {
    console.error("Failed to load HTTP instrumentation:", error);
  }

  // Initialize all instrumentations that are available
  try {
    const { OpenAIInstrumentation } = await import("@elastic/opentelemetry-instrumentation-openai");
    console.log("Loaded Elastic OpenAI instrumentation");
    openAIInstrumentation = new OpenAIInstrumentation({
      enrichTokens: true,
      exceptionLogger: (e: Error) => console.error("OpenAI instrumentation error:", e),
    });
    console.log("Created Elastic OpenAI instrumentation instance");
    instrumentations.push(openAIInstrumentation);
    console.log("Added Elastic OpenAI instrumentation to list");
  } catch (error) {
    console.error("Failed to load Elastic OpenAI instrumentation:", error);
  }

  try {
    const { AnthropicInstrumentation } = await import("@traceloop/instrumentation-anthropic");
    anthropicInstrumentation = new AnthropicInstrumentation({ exceptionLogger });
    instrumentations.push(anthropicInstrumentation);
  } catch (error) {
    // Instrumentation not available, skip silently
  }

  try {
    const { AzureOpenAIInstrumentation } = await import("@traceloop/instrumentation-azure");
    azureOpenAIInstrumentation = new AzureOpenAIInstrumentation({ exceptionLogger });
    instrumentations.push(azureOpenAIInstrumentation);
  } catch (error) {
    // Instrumentation not available, skip silently
  }

  try {
    const { CohereInstrumentation } = await import("@traceloop/instrumentation-cohere");
    cohereInstrumentation = new CohereInstrumentation({ exceptionLogger });
    instrumentations.push(cohereInstrumentation);
  } catch (error) {
    // Instrumentation not available, skip silently
  }

  try {
    const { VertexAIInstrumentation } = await import("@traceloop/instrumentation-vertexai");
    vertexaiInstrumentation = new VertexAIInstrumentation({ exceptionLogger });
    instrumentations.push(vertexaiInstrumentation);
  } catch (error) {
    // Instrumentation not available, skip silently
  }

  try {
    const { BedrockInstrumentation } = await import("@traceloop/instrumentation-bedrock");
    bedrockInstrumentation = new BedrockInstrumentation({ exceptionLogger });
    instrumentations.push(bedrockInstrumentation);
  } catch (error) {
    // Instrumentation not available, skip silently
  }

  try {
    const { LangChainInstrumentation } = await import("@traceloop/instrumentation-langchain");
    langchainInstrumentation = new LangChainInstrumentation({ exceptionLogger });
    instrumentations.push(langchainInstrumentation);
  } catch (error) {
    // Instrumentation not available, skip silently
  }

  try {
    const { LlamaIndexInstrumentation } = await import("@traceloop/instrumentation-llamaindex");
    llamaIndexInstrumentation = new LlamaIndexInstrumentation({ exceptionLogger });
    instrumentations.push(llamaIndexInstrumentation);
  } catch (error) {
    // Instrumentation not available, skip silently
  }

  try {
    const { PineconeInstrumentation } = await import("@traceloop/instrumentation-pinecone");
    pineconeInstrumentation = new PineconeInstrumentation({ exceptionLogger });
    instrumentations.push(pineconeInstrumentation);
  } catch (error) {
    // Instrumentation not available, skip silently
  }

  try {
    const { ChromaDBInstrumentation } = await import("@traceloop/instrumentation-chromadb");
    chromadbInstrumentation = new ChromaDBInstrumentation({ exceptionLogger });
    instrumentations.push(chromadbInstrumentation);
  } catch (error) {
    // Instrumentation not available, skip silently
  }

  try {
    const { QdrantInstrumentation } = await import("@traceloop/instrumentation-qdrant");
    qdrantInstrumentation = new QdrantInstrumentation({ exceptionLogger });
    instrumentations.push(qdrantInstrumentation);
  } catch (error) {
    // Instrumentation not available, skip silently
  }

  try {
    const { TogetherInstrumentation } = await import("@traceloop/instrumentation-together");
    togetherInstrumentation = new TogetherInstrumentation({ exceptionLogger });
    instrumentations.push(togetherInstrumentation);
  } catch (error) {
    // Instrumentation not available, skip silently
  }
};

/**
 * Manually initialize instrumentations with provided modules.
 * This is similar to Traceloop's approach for environments like Next.js: https://github.com/traceloop/openllmetry-js/blob/main/packages/traceloop-sdk/src/lib/tracing/index.ts
 * where dynamic imports might not work properly.
 */
const manuallyInitInstrumentations = async (
  instrumentModules: NonNullable<KeywordsAIOptions['instrumentModules']>
) => {
  const exceptionLogger = (e: Error) => console.error("Instrumentation error:", e);

  // Clear the instrumentations array
  instrumentations.length = 0;

  if (instrumentModules.openAI) {
    try {
      const { OpenAIInstrumentation } = await import("@traceloop/instrumentation-openai");
      openAIInstrumentation = new OpenAIInstrumentation({
        enrichTokens: true,
        exceptionLogger,
      });
      instrumentations.push(openAIInstrumentation);
      openAIInstrumentation.manuallyInstrument(instrumentModules.openAI);
    } catch (error) {
      console.warn("Failed to initialize OpenAI instrumentation:", error);
    }
  }

  if (instrumentModules.anthropic) {
    try {
      const { AnthropicInstrumentation } = await import("@traceloop/instrumentation-anthropic");
      anthropicInstrumentation = new AnthropicInstrumentation({ exceptionLogger });
      instrumentations.push(anthropicInstrumentation);
      anthropicInstrumentation.manuallyInstrument(instrumentModules.anthropic);
    } catch (error) {
      console.warn("Failed to initialize Anthropic instrumentation:", error);
    }
  }

  if (instrumentModules.azureOpenAI) {
    try {
      const { AzureOpenAIInstrumentation } = await import("@traceloop/instrumentation-azure");
      azureOpenAIInstrumentation = new AzureOpenAIInstrumentation({ exceptionLogger });
      instrumentations.push(azureOpenAIInstrumentation);
      azureOpenAIInstrumentation.manuallyInstrument(instrumentModules.azureOpenAI);
    } catch (error) {
      console.warn("Failed to initialize Azure OpenAI instrumentation:", error);
    }
  }

  if (instrumentModules.cohere) {
    try {
      const { CohereInstrumentation } = await import("@traceloop/instrumentation-cohere");
      cohereInstrumentation = new CohereInstrumentation({ exceptionLogger });
      instrumentations.push(cohereInstrumentation);
      cohereInstrumentation.manuallyInstrument(instrumentModules.cohere);
    } catch (error) {
      console.warn("Failed to initialize Cohere instrumentation:", error);
    }
  }

  if (instrumentModules.google_vertexai) {
    try {
      const { VertexAIInstrumentation } = await import("@traceloop/instrumentation-vertexai");
      vertexaiInstrumentation = new VertexAIInstrumentation({ exceptionLogger });
      instrumentations.push(vertexaiInstrumentation);
      vertexaiInstrumentation.manuallyInstrument(instrumentModules.google_vertexai);
    } catch (error) {
      console.warn("Failed to initialize Vertex AI instrumentation:", error);
    }
  }

  if (instrumentModules.google_aiplatform) {
    try {
      const { AIPlatformInstrumentation } = await import("@traceloop/instrumentation-vertexai");
      const aiplatformInstrumentation = new AIPlatformInstrumentation({ exceptionLogger });
      instrumentations.push(aiplatformInstrumentation);
      aiplatformInstrumentation.manuallyInstrument(instrumentModules.google_aiplatform);
    } catch (error) {
      console.warn("Failed to initialize AI Platform instrumentation:", error);
    }
  }

  if (instrumentModules.bedrock) {
    try {
      const { BedrockInstrumentation } = await import("@traceloop/instrumentation-bedrock");
      bedrockInstrumentation = new BedrockInstrumentation({ exceptionLogger });
      instrumentations.push(bedrockInstrumentation);
      bedrockInstrumentation.manuallyInstrument(instrumentModules.bedrock);
    } catch (error) {
      console.warn("Failed to initialize Bedrock instrumentation:", error);
    }
  }

  if (instrumentModules.pinecone) {
    try {
      const { PineconeInstrumentation } = await import("@traceloop/instrumentation-pinecone");
      pineconeInstrumentation = new PineconeInstrumentation({ exceptionLogger });
      instrumentations.push(pineconeInstrumentation);
      pineconeInstrumentation.manuallyInstrument(instrumentModules.pinecone);
    } catch (error) {
      console.warn("Failed to initialize Pinecone instrumentation:", error);
    }
  }

  if (instrumentModules.langchain) {
    try {
      const { LangChainInstrumentation } = await import("@traceloop/instrumentation-langchain");
      langchainInstrumentation = new LangChainInstrumentation({ exceptionLogger });
      instrumentations.push(langchainInstrumentation);
      langchainInstrumentation.manuallyInstrument(instrumentModules.langchain);
    } catch (error) {
      console.warn("Failed to initialize LangChain instrumentation:", error);
    }
  }

  if (instrumentModules.llamaIndex) {
    try {
      const { LlamaIndexInstrumentation } = await import("@traceloop/instrumentation-llamaindex");
      llamaIndexInstrumentation = new LlamaIndexInstrumentation({ exceptionLogger });
      instrumentations.push(llamaIndexInstrumentation);
      llamaIndexInstrumentation.manuallyInstrument(instrumentModules.llamaIndex);
    } catch (error) {
      console.warn("Failed to initialize LlamaIndex instrumentation:", error);
    }
  }

  if (instrumentModules.chromadb) {
    try {
      const { ChromaDBInstrumentation } = await import("@traceloop/instrumentation-chromadb");
      chromadbInstrumentation = new ChromaDBInstrumentation({ exceptionLogger });
      instrumentations.push(chromadbInstrumentation);
      chromadbInstrumentation.manuallyInstrument(instrumentModules.chromadb);
    } catch (error) {
      console.warn("Failed to initialize ChromaDB instrumentation:", error);
    }
  }

  if (instrumentModules.qdrant) {
    try {
      const { QdrantInstrumentation } = await import("@traceloop/instrumentation-qdrant");
      qdrantInstrumentation = new QdrantInstrumentation({ exceptionLogger });
      instrumentations.push(qdrantInstrumentation);
      qdrantInstrumentation.manuallyInstrument(instrumentModules.qdrant);
    } catch (error) {
      console.warn("Failed to initialize Qdrant instrumentation:", error);
    }
  }

  if (instrumentModules.together) {
    try {
      const { TogetherInstrumentation } = await import("@traceloop/instrumentation-together");
      togetherInstrumentation = new TogetherInstrumentation({ exceptionLogger });
      instrumentations.push(togetherInstrumentation);
      togetherInstrumentation.manuallyInstrument(instrumentModules.together);
    } catch (error) {
      console.warn("Failed to initialize Together instrumentation:", error);
    }
  }
};

/**
 * Initializes the OpenTelemetry SDK with KeywordsAI-specific configuration.
 * This sets up the entire tracing pipeline: collection, processing, and export.
 * 
 * @param options - Configuration options for the tracing setup
 */
export const startTracing = async (options: KeywordsAIOptions) => {
  // Prevent multiple initializations
  if (_initialized) {
    console.log("[KeywordsAI] Tracing already initialized, skipping...");
    return;
  }

  const {
    appName = "keywordsai-app",
    apiKey = process.env.KEYWORDS_AI_API_KEY || "",
    baseUrl = process.env.KEYWORDS_AI_BASE_URL || "https://api.keywordsai.co",
    logLevel = "error",
    exporter,
    headers = {},
    propagator,
    contextManager,
    silenceInitializationMessage = false,
    tracingEnabled = true,
    instrumentModules,
    traceContent = true,
  } = options;

  if (!tracingEnabled) {
    if (!silenceInitializationMessage) {
      console.log("KeywordsAI tracing is disabled");
    }
    return;
  }

  // Initialize instrumentations
  if (instrumentModules && Object.keys(instrumentModules).length > 0) {
    // Manual instrumentation path - for Next.js and other bundled environments
    await manuallyInitInstrumentations(instrumentModules);
  } else {
    // Automatic instrumentation path - for standard Node.js environments
    await initInstrumentations();
  }

  // Configure trace content for instrumentations
  if (!shouldSendTraces() || !traceContent) {
    openAIInstrumentation?.setConfig?.({ traceContent: false });
    azureOpenAIInstrumentation?.setConfig?.({ traceContent: false });
    llamaIndexInstrumentation?.setConfig?.({ traceContent: false });
    vertexaiInstrumentation?.setConfig?.({ traceContent: false });
    bedrockInstrumentation?.setConfig?.({ traceContent: false });
    cohereInstrumentation?.setConfig?.({ traceContent: false });
    chromadbInstrumentation?.setConfig?.({ traceContent: false });
    togetherInstrumentation?.setConfig?.({ traceContent: false });
  }

  // Set log level using proper DiagLogLevel
  const diagLogLevel = logLevel === "debug" ? DiagLogLevel.DEBUG 
    : logLevel === "info" ? DiagLogLevel.INFO 
    : logLevel === "warn" ? DiagLogLevel.WARN 
    : DiagLogLevel.ERROR;

  diag.setLogger(
    {
      error: (...args) => console.error("[KeywordsAI]", ...args),
      warn: (...args) => console.warn("[KeywordsAI]", ...args),
      info: (...args) => console.info("[KeywordsAI]", ...args),
      debug: (...args) => console.debug("[KeywordsAI]", ...args),
      verbose: (...args) => console.debug("[KeywordsAI]", ...args),
    },
    diagLogLevel
  );

  // Create resource
  const resource = new Resource({
    [ATTR_SERVICE_NAME]: appName,
  });

  // Create exporter
  const traceExporter = exporter || new OTLPTraceExporter({
    url: `${baseUrl}/v1/traces`,
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/x-protobuf",
      ...headers,
    },
  });

  // Initialize SDK
  console.log(`Initializing NodeSDK with ${instrumentations.length} instrumentations`);
  _sdk = new NodeSDK({
    resource,
    traceExporter,
    instrumentations,
    textMapPropagator: propagator,
    contextManager,
  });

  try {
    _sdk.start();
    _initialized = true;
    
    if (!silenceInitializationMessage) {
      console.log("KeywordsAI tracing initialized successfully");
    }
  } catch (error) {
    console.error("Failed to initialize KeywordsAI tracing:", error);
  }
};

export const forceFlush = async (): Promise<void> => {
  if (_sdk) {
    try {
      await _sdk.shutdown();
    } catch (error) {
      console.error("Error during SDK shutdown:", error);
    }
  }
};

// Dynamic instrumentation loading
export const loadInstrumentation = async (name: string): Promise<Instrumentation | null> => {
  try {
    switch (name) {
      case "openai":
        const { OpenAIInstrumentation } = await import("@traceloop/instrumentation-openai");
        return new OpenAIInstrumentation({
          enrichTokens: true,
          exceptionLogger: (e: Error) => console.error("OpenAI instrumentation error:", e),
        });
      
      case "anthropic":
        const { AnthropicInstrumentation } = await import("@traceloop/instrumentation-anthropic");
        return new AnthropicInstrumentation({
          exceptionLogger: (e: Error) => console.error("Anthropic instrumentation error:", e),
        });
      
      case "azure":
        const { AzureOpenAIInstrumentation } = await import("@traceloop/instrumentation-azure");
        return new AzureOpenAIInstrumentation({
          exceptionLogger: (e: Error) => console.error("Azure instrumentation error:", e),
        });
      
      case "bedrock":
        const { BedrockInstrumentation } = await import("@traceloop/instrumentation-bedrock");
        return new BedrockInstrumentation({
          exceptionLogger: (e: Error) => console.error("Bedrock instrumentation error:", e),
        });
      
      case "cohere":
        const { CohereInstrumentation } = await import("@traceloop/instrumentation-cohere");
        return new CohereInstrumentation({
          exceptionLogger: (e: Error) => console.error("Cohere instrumentation error:", e),
        });
      
      case "langchain":
        const { LangChainInstrumentation } = await import("@traceloop/instrumentation-langchain");
        return new LangChainInstrumentation({
          exceptionLogger: (e: Error) => console.error("LangChain instrumentation error:", e),
        });
      
      case "llamaindex":
        const { LlamaIndexInstrumentation } = await import("@traceloop/instrumentation-llamaindex");
        return new LlamaIndexInstrumentation({
          exceptionLogger: (e: Error) => console.error("LlamaIndex instrumentation error:", e),
        });
      
      case "pinecone":
        const { PineconeInstrumentation } = await import("@traceloop/instrumentation-pinecone");
        return new PineconeInstrumentation({
          exceptionLogger: (e: Error) => console.error("Pinecone instrumentation error:", e),
        });
      
      case "chromadb":
        const { ChromaDBInstrumentation } = await import("@traceloop/instrumentation-chromadb");
        return new ChromaDBInstrumentation({
          exceptionLogger: (e: Error) => console.error("ChromaDB instrumentation error:", e),
        });
      
      case "qdrant":
        const { QdrantInstrumentation } = await import("@traceloop/instrumentation-qdrant");
        return new QdrantInstrumentation({
          exceptionLogger: (e: Error) => console.error("Qdrant instrumentation error:", e),
        });
      
      case "together":
        const { TogetherInstrumentation } = await import("@traceloop/instrumentation-together");
        return new TogetherInstrumentation({
          exceptionLogger: (e: Error) => console.error("Together instrumentation error:", e),
        });
      
      case "vertexai":
        const { VertexAIInstrumentation } = await import("@traceloop/instrumentation-vertexai");
        return new VertexAIInstrumentation({
          exceptionLogger: (e: Error) => console.error("VertexAI instrumentation error:", e),
        });
      
      default:
        console.warn(`Unknown instrumentation: ${name}`);
        return null;
    }
  } catch (error) {
    console.warn(`Failed to load instrumentation ${name}:`, error);
    return null;
  }
};

export const enableInstrumentation = async (name: string): Promise<void> => {
  const instrumentation = await loadInstrumentation(name);
  if (instrumentation) {
    instrumentations.push(instrumentation);
    console.log(`Enabled ${name} instrumentation`);
  }
};

/**
 * Gets the current SDK instance.
 * Useful for advanced configuration or checking if tracing is initialized.
 * 
 * @returns The NodeSDK instance or undefined if not initialized
 */
export const getClient = (): NodeSDK | undefined => {
  return _sdk;
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
export const updateCurrentSpan = (options: {
  keywordsaiParams?: Record<string, any>;
  attributes?: Record<string, string | number | boolean>;
  status?: SpanStatusCode;
  statusDescription?: string;
  name?: string;
} = {}): boolean => {
  const currentSpan = getCurrentSpan();
  if (!currentSpan) {
    console.warn("No active span found. Cannot update span.");
    return false;
  }

  try {
    const { keywordsaiParams, attributes, status, statusDescription, name } = options;

    // Update span name if provided
    if (name) {
      currentSpan.updateName(name);
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
        } catch (error) {
          console.warn(`Failed to set attribute ${key}=${value}:`, error);
        }
      });
    }

    // Set status
    if (status !== undefined) {
      currentSpan.setStatus({
        code: status,
        message: statusDescription
      });
    }

    return true;
  } catch (error) {
    console.error("Failed to update span:", error);
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
const setKeywordsAIAttributes = (span: Span, keywordsaiParams: Record<string, any>): void => {
  try {
    // Validate parameters using the imported schema
    let validatedParams: Record<string, any>;
    try {
      validatedParams = KeywordsAIParamsSchema.parse(keywordsaiParams);
    } catch (validationError) {
      console.warn("Failed to validate KeywordsAI params:", validationError);
      // Use original params if validation fails, but continue processing
      validatedParams = keywordsaiParams;
    }

    // Set attributes based on the imported mapping
    Object.entries(validatedParams).forEach(([key, value]) => {
      if (key in KEYWORDSAI_SPAN_ATTRIBUTES_MAP && key !== "metadata") {
        try {
          span.setAttribute(KEYWORDSAI_SPAN_ATTRIBUTES_MAP[key], value);
        } catch (error) {
          console.warn(`Failed to set span attribute ${KEYWORDSAI_SPAN_ATTRIBUTES_MAP[key]}=${value}:`, error);
        }
      }

      // Handle metadata specially using the proper enum
      if (key === "metadata" && typeof value === "object" && value !== null) {
        Object.entries(value as Record<string, any>).forEach(([metadataKey, metadataValue]) => {
          try {
            span.setAttribute(`${KeywordsAISpanAttributes.KEYWORDSAI_METADATA}.${metadataKey}`, metadataValue);
          } catch (error) {
            console.warn(`Failed to set metadata attribute ${metadataKey}=${metadataValue}:`, error);
          }
        });
      }
    });
  } catch (error) {
    console.error("Unexpected error setting KeywordsAI attributes:", error);
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
export const addSpanEvent = (name: string, attributes?: Record<string, string | number | boolean>): boolean => {
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
export const setSpanStatus = (status: 'OK' | 'ERROR', message?: string): boolean => {
  const currentSpan = getCurrentSpan();
  if (!currentSpan) {
    console.warn("No active span to set status on");
    return false;
  }

  try {
    currentSpan.setStatus({
      code: status === 'OK' ? SpanStatusCode.OK : SpanStatusCode.ERROR,
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