import { NodeSDK } from "@opentelemetry/sdk-node";
import { context, diag, trace, Tracer, createContextKey, DiagLogLevel, SpanStatusCode, Span } from "@opentelemetry/api";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-proto";
import { Resource } from "@opentelemetry/resources";
import { ATTR_SERVICE_NAME } from "@opentelemetry/semantic-conventions";
import { Instrumentation } from "@opentelemetry/instrumentation";
import { KeywordsAIOptions, InstrumentationName } from "../types/clientTypes.js";
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
  return process.env.KEYWORDSAI_TRACE_CONTENT !== "false";
};

/**
 * Initialize all available instrumentations automatically.
 * This is used when no specific instrumentModules are provided.
 */

export const _resolveEndpoint = (baseUrl: string) => {
  const originalUrl = baseUrl;
  
  // Remove trailing slash if it exists
  if (baseUrl.endsWith("/")) {
    baseUrl = baseUrl.slice(0, -1);
  }
  // Remove trailing /api if it exists
  if (baseUrl.endsWith("/api")) {
    baseUrl = baseUrl.slice(0, -4);
  }
  
  // Debug logging for URL resolution
  if (originalUrl !== baseUrl) {
    console.debug(`[KeywordsAI Debug] URL resolved: "${originalUrl}" -> "${baseUrl}"`);
  } else {
    console.debug(`[KeywordsAI Debug] URL used as-is: "${baseUrl}"`);
  }
  
  return baseUrl;
};

const initInstrumentations = async (disabledInstrumentations: InstrumentationName[] = [], showInstallWarnings: boolean = true) => {
  const exceptionLogger = (e: Error) => console.error("Instrumentation error:", e);

  console.info("[KeywordsAI] Initializing automatic instrumentation discovery...");
  
  // Track instrumentation loading results 
  const loadingResults: { name: string; status: 'success' | 'failed' | 'disabled'; description: string; error?: any }[] = [];
  
  // Clear the instrumentations array
  instrumentations.length = 0;

  // Add HTTP instrumentation to capture all HTTP requests (always enabled)
  try {
    console.debug("[KeywordsAI Debug] Attempting to load HTTP instrumentation...");
    const { HttpInstrumentation } = await import("@opentelemetry/instrumentation-http");
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
    loadingResults.push({ name: "http", status: "success", description: "HTTP requests instrumentation" });
    console.debug("[KeywordsAI Debug] Successfully loaded HTTP instrumentation");
  } catch (error) {
    loadingResults.push({ name: "http", status: "failed", description: "HTTP requests instrumentation", error });
    console.error("[KeywordsAI Debug] Failed to load HTTP instrumentation:", error);
  }

  // Define all instrumentations to attempt loading
  const instrumentationsToLoad: { name: InstrumentationName; description: string; loadFunction: () => Promise<any> }[] = [
    {
      name: "openAI",
      description: "OpenAI API instrumentation",
      loadFunction: async () => {
        const { OpenAIInstrumentation } = await import("@elastic/opentelemetry-instrumentation-openai");
        openAIInstrumentation = new OpenAIInstrumentation({
          enrichTokens: true,
          exceptionLogger: (e: Error) => console.error("OpenAI instrumentation error:", e),
        });
        return openAIInstrumentation;
      }
    },
    {
      name: "anthropic",
      description: "Anthropic API instrumentation",
      loadFunction: async () => {
        const { AnthropicInstrumentation } = await import("@traceloop/instrumentation-anthropic");
        anthropicInstrumentation = new AnthropicInstrumentation({ exceptionLogger });
        return anthropicInstrumentation;
      }
    },
    {
      name: "azureOpenAI",
      description: "Azure OpenAI instrumentation", 
      loadFunction: async () => {
        const { AzureOpenAIInstrumentation } = await import("@traceloop/instrumentation-azure");
        azureOpenAIInstrumentation = new AzureOpenAIInstrumentation({ exceptionLogger });
        return azureOpenAIInstrumentation;
      }
    },
    {
      name: "cohere",
      description: "Cohere API instrumentation",
      loadFunction: async () => {
        const { CohereInstrumentation } = await import("@traceloop/instrumentation-cohere");
        cohereInstrumentation = new CohereInstrumentation({ exceptionLogger });
        return cohereInstrumentation;
      }
    },
    {
      name: "googleVertexAI",
      description: "Google Vertex AI instrumentation",
      loadFunction: async () => {
        const { VertexAIInstrumentation } = await import("@traceloop/instrumentation-vertexai");
        vertexaiInstrumentation = new VertexAIInstrumentation({ exceptionLogger });
        return vertexaiInstrumentation;
      }
    },
    {
      name: "bedrock",
      description: "AWS Bedrock instrumentation",
      loadFunction: async () => {
        const { BedrockInstrumentation } = await import("@traceloop/instrumentation-bedrock");
        bedrockInstrumentation = new BedrockInstrumentation({ exceptionLogger });
        return bedrockInstrumentation;
      }
    },
    {
      name: "langChain",
      description: "LangChain framework instrumentation",
      loadFunction: async () => {
        const { LangChainInstrumentation } = await import("@traceloop/instrumentation-langchain");
        langchainInstrumentation = new LangChainInstrumentation({ exceptionLogger });
        return langchainInstrumentation;
      }
    },
    {
      name: "llamaIndex", 
      description: "LlamaIndex framework instrumentation",
      loadFunction: async () => {
        const { LlamaIndexInstrumentation } = await import("@traceloop/instrumentation-llamaindex");
        llamaIndexInstrumentation = new LlamaIndexInstrumentation({ exceptionLogger });
        return llamaIndexInstrumentation;
      }
    },
    {
      name: "pinecone",
      description: "Pinecone vector database instrumentation",
      loadFunction: async () => {
        const { PineconeInstrumentation } = await import("@traceloop/instrumentation-pinecone");
        pineconeInstrumentation = new PineconeInstrumentation({ exceptionLogger });
        return pineconeInstrumentation;
      }
    },
    {
      name: "chromaDB",
      description: "ChromaDB vector database instrumentation",
      loadFunction: async () => {
        const { ChromaDBInstrumentation } = await import("@traceloop/instrumentation-chromadb");
        chromadbInstrumentation = new ChromaDBInstrumentation({ exceptionLogger });
        return chromadbInstrumentation;
      }
    },
    {
      name: "qdrant",
      description: "Qdrant vector database instrumentation",
      loadFunction: async () => {
        const { QdrantInstrumentation } = await import("@traceloop/instrumentation-qdrant");
        qdrantInstrumentation = new QdrantInstrumentation({ exceptionLogger });
        return qdrantInstrumentation;
      }
    },
    {
      name: "together",
      description: "Together AI instrumentation",
      loadFunction: async () => {
        const { TogetherInstrumentation } = await import("@traceloop/instrumentation-together");
        togetherInstrumentation = new TogetherInstrumentation({ exceptionLogger });
        return togetherInstrumentation;
      }
    }
  ];

  // Load each instrumentation
  for (const { name, description, loadFunction } of instrumentationsToLoad) {
    if (disabledInstrumentations.includes(name)) {
      loadingResults.push({ name, status: "disabled", description });
      console.debug(`[KeywordsAI Debug] Skipping ${description} (disabled by configuration)`);
      continue;
    }

    try {
      console.debug(`[KeywordsAI Debug] Attempting to load ${description}...`);
      const instrumentation = await loadFunction();
      instrumentations.push(instrumentation);
      loadingResults.push({ name, status: "success", description });
      console.debug(`[KeywordsAI Debug] Successfully loaded ${description}`);
    } catch (error) {
      loadingResults.push({ name, status: "failed", description, error });
      
      // Provide installation instructions for failed instrumentations (only if showInstallWarnings is true)
      if (showInstallWarnings) {
        const info = INSTRUMENTATION_INFO[name];
        if (info) {
          console.info(`[KeywordsAI] ${description} is not available. To enable it, install the required package:\n   ${info.installCommand}`);
        }
      }
      console.debug(`[KeywordsAI Debug] Failed to load ${description}:`, error);
    }
  }

  // Print summary
  const successful = loadingResults.filter(r => r.status === 'success');
  const failed = loadingResults.filter(r => r.status === 'failed');
  const disabled = loadingResults.filter(r => r.status === 'disabled');

  console.info(`[KeywordsAI] Instrumentation loading complete: ${successful.length} loaded, ${failed.length} failed, ${disabled.length} disabled`);
  
  if (successful.length > 0) {
    console.info(`[KeywordsAI] Successfully loaded: ${successful.map(r => r.name).join(', ')}`);
  }
  
  if (disabled.length > 0) {
    console.info(`[KeywordsAI] Disabled instrumentations: ${disabled.map(r => r.name).join(', ')}`);
  }
  
  if (failed.length > 0) {
    console.debug(`[KeywordsAI Debug] Failed to load: ${failed.map(r => r.name).join(', ')}`);
  }
};

/**
 * Manually initialize instrumentations with provided modules.
 * This is similar to Traceloop's approach for environments like Next.js: https://github.com/traceloop/openllmetry-js/blob/main/packages/traceloop-sdk/src/lib/tracing/index.ts
 * where dynamic imports might not work properly.
 */
const manuallyInitInstrumentations = async (
  instrumentModules: NonNullable<KeywordsAIOptions['instrumentModules']>,
  disabledInstrumentations: InstrumentationName[] = []
) => {
  const exceptionLogger = (e: Error) => console.error("Instrumentation error:", e);

  console.info("[KeywordsAI] Initializing manual instrumentation with provided modules...");
  console.debug("[KeywordsAI Debug] Provided modules:", Object.keys(instrumentModules));
  
  // Track instrumentation loading results (using string for name to allow custom modules)
  const loadingResults: { name: string; status: 'success' | 'failed' | 'disabled' | 'not-provided'; description: string; error?: any }[] = [];

  // Clear the instrumentations array
  instrumentations.length = 0;

  // Define all possible manual instrumentations
  const manualInstrumentationConfigs: { name: InstrumentationName; description: string; moduleKey: keyof typeof instrumentModules; initFunction: (module: any) => Promise<any> }[] = [
    {
      name: "openAI",
      description: "OpenAI API instrumentation",
      moduleKey: "openAI" as keyof typeof instrumentModules,
      initFunction: async (module: any) => {
        const { OpenAIInstrumentation } = await import("@traceloop/instrumentation-openai");
        openAIInstrumentation = new OpenAIInstrumentation({
          enrichTokens: true,
          exceptionLogger,
        });
        instrumentations.push(openAIInstrumentation);
        openAIInstrumentation.manuallyInstrument(module);
        return openAIInstrumentation;
      }
    },
    {
      name: "anthropic",
      description: "Anthropic API instrumentation", 
      moduleKey: "anthropic" as keyof typeof instrumentModules,
      initFunction: async (module: any) => {
        const { AnthropicInstrumentation } = await import("@traceloop/instrumentation-anthropic");
        anthropicInstrumentation = new AnthropicInstrumentation({ exceptionLogger });
        instrumentations.push(anthropicInstrumentation);
        anthropicInstrumentation.manuallyInstrument(module);
        return anthropicInstrumentation;
      }
    },
    {
      name: "azureOpenAI", 
      description: "Azure OpenAI instrumentation",
      moduleKey: "azureOpenAI" as keyof typeof instrumentModules,
      initFunction: async (module: any) => {
        const { AzureOpenAIInstrumentation } = await import("@traceloop/instrumentation-azure");
        azureOpenAIInstrumentation = new AzureOpenAIInstrumentation({ exceptionLogger });
        instrumentations.push(azureOpenAIInstrumentation);
        azureOpenAIInstrumentation.manuallyInstrument(module);
        return azureOpenAIInstrumentation;
      }
    },
    {
      name: "cohere",
      description: "Cohere API instrumentation",
      moduleKey: "cohere" as keyof typeof instrumentModules, 
      initFunction: async (module: any) => {
        const { CohereInstrumentation } = await import("@traceloop/instrumentation-cohere");
        cohereInstrumentation = new CohereInstrumentation({ exceptionLogger });
        instrumentations.push(cohereInstrumentation);
        cohereInstrumentation.manuallyInstrument(module);
        return cohereInstrumentation;
      }
    },
    {
      name: "googleVertexAI",
      description: "Google Vertex AI instrumentation",
      moduleKey: "googleVertexAI" as keyof typeof instrumentModules,
      initFunction: async (module: any) => {
        const { VertexAIInstrumentation } = await import("@traceloop/instrumentation-vertexai");
        vertexaiInstrumentation = new VertexAIInstrumentation({ exceptionLogger });
        instrumentations.push(vertexaiInstrumentation);
        vertexaiInstrumentation.manuallyInstrument(module);
        return vertexaiInstrumentation;
      }
    },
    {
      name: "googleAIPlatform",
      description: "Google AI Platform instrumentation",
      moduleKey: "googleAIPlatform" as keyof typeof instrumentModules,
      initFunction: async (module: any) => {
        const { AIPlatformInstrumentation } = await import("@traceloop/instrumentation-vertexai");
        const aiplatformInstrumentation = new AIPlatformInstrumentation({ exceptionLogger });
        instrumentations.push(aiplatformInstrumentation);
        aiplatformInstrumentation.manuallyInstrument(module);
        return aiplatformInstrumentation;
      }
    },
    {
      name: "bedrock",
      description: "AWS Bedrock instrumentation",
      moduleKey: "bedrock" as keyof typeof instrumentModules,
      initFunction: async (module: any) => {
        const { BedrockInstrumentation } = await import("@traceloop/instrumentation-bedrock");
        bedrockInstrumentation = new BedrockInstrumentation({ exceptionLogger });
        instrumentations.push(bedrockInstrumentation);
        bedrockInstrumentation.manuallyInstrument(module);
        return bedrockInstrumentation;
      }
    },
    {
      name: "pinecone",
      description: "Pinecone vector database instrumentation",
      moduleKey: "pinecone" as keyof typeof instrumentModules,
      initFunction: async (module: any) => {
        const { PineconeInstrumentation } = await import("@traceloop/instrumentation-pinecone");
        pineconeInstrumentation = new PineconeInstrumentation({ exceptionLogger });
        instrumentations.push(pineconeInstrumentation);
        pineconeInstrumentation.manuallyInstrument(module);
        return pineconeInstrumentation;
      }
    },
    {
      name: "langChain",
      description: "LangChain framework instrumentation", 
      moduleKey: "langChain" as keyof typeof instrumentModules,
      initFunction: async (module: any) => {
        const { LangChainInstrumentation } = await import("@traceloop/instrumentation-langchain");
        langchainInstrumentation = new LangChainInstrumentation({ exceptionLogger });
        instrumentations.push(langchainInstrumentation);
        langchainInstrumentation.manuallyInstrument(module);
        return langchainInstrumentation;
      }
    },
    {
      name: "llamaIndex",
      description: "LlamaIndex framework instrumentation",
      moduleKey: "llamaIndex" as keyof typeof instrumentModules,
      initFunction: async (module: any) => {
        const { LlamaIndexInstrumentation } = await import("@traceloop/instrumentation-llamaindex");
        llamaIndexInstrumentation = new LlamaIndexInstrumentation({ exceptionLogger });
        instrumentations.push(llamaIndexInstrumentation);
        llamaIndexInstrumentation.manuallyInstrument(module);
        return llamaIndexInstrumentation;
      }
    },
    {
      name: "chromaDB",
      description: "ChromaDB vector database instrumentation",
      moduleKey: "chromaDB" as keyof typeof instrumentModules,
      initFunction: async (module: any) => {
        const { ChromaDBInstrumentation } = await import("@traceloop/instrumentation-chromadb");
        chromadbInstrumentation = new ChromaDBInstrumentation({ exceptionLogger });
        instrumentations.push(chromadbInstrumentation);
        chromadbInstrumentation.manuallyInstrument(module);
        return chromadbInstrumentation;
      }
    },
    {
      name: "qdrant",
      description: "Qdrant vector database instrumentation",
      moduleKey: "qdrant" as keyof typeof instrumentModules,
      initFunction: async (module: any) => {
        const { QdrantInstrumentation } = await import("@traceloop/instrumentation-qdrant");
        qdrantInstrumentation = new QdrantInstrumentation({ exceptionLogger });
        instrumentations.push(qdrantInstrumentation);
        qdrantInstrumentation.manuallyInstrument(module);
        return qdrantInstrumentation;
      }
    },
    {
      name: "together",
      description: "Together AI instrumentation",
      moduleKey: "together" as keyof typeof instrumentModules,
      initFunction: async (module: any) => {
        const { TogetherInstrumentation } = await import("@traceloop/instrumentation-together");
        togetherInstrumentation = new TogetherInstrumentation({ exceptionLogger });
        instrumentations.push(togetherInstrumentation);
        togetherInstrumentation.manuallyInstrument(module);
        return togetherInstrumentation;
      }
    }
  ];

  // Keep track of processed module keys
  const processedModuleKeys = new Set<string>();

  // Process each pre-defined instrumentation
  for (const { name, description, moduleKey, initFunction } of manualInstrumentationConfigs) {
    const module = instrumentModules[moduleKey];
    processedModuleKeys.add(moduleKey as string);
    
    if (disabledInstrumentations.includes(name)) {
      loadingResults.push({ name, status: "disabled", description });
      console.debug(`[KeywordsAI Debug] Skipping ${description} (disabled by configuration)`);
      continue;
    }
    
    if (!module) {
      loadingResults.push({ name, status: "not-provided", description });
      console.debug(`[KeywordsAI Debug] No module provided for ${description}`);
      continue;
    }

    try {
      console.debug(`[KeywordsAI Debug] Attempting to manually initialize ${description}...`);
      await initFunction(module);
      loadingResults.push({ name, status: "success", description });
      console.debug(`[KeywordsAI Debug] Successfully initialized ${description}`);
    } catch (error) {
      loadingResults.push({ name, status: "failed", description, error });
      
      // Provide installation instructions for failed instrumentations (always show for manual instrumentation)
      const info = INSTRUMENTATION_INFO[name];
      if (info) {
        console.info(`[KeywordsAI] ${description} failed to initialize. Make sure you have the required package installed:\n   ${info.installCommand}`);
      }
      console.debug(`[KeywordsAI Debug] Failed to initialize ${description}:`, error);
    }
  }

  // Process any additional modules not in our pre-defined list
  for (const [moduleKey, module] of Object.entries(instrumentModules)) {
    if (processedModuleKeys.has(moduleKey) || !module) {
      continue; // Skip already processed or null modules
    }

    const customName = moduleKey; // Use the actual module key name
    const customDescription = `Custom ${moduleKey} instrumentation`;

    console.debug(`[KeywordsAI Debug] Found custom module: ${moduleKey}, attempting generic instrumentation...`);

    try {
      // Generic approach: try to call manuallyInstrument if it exists
      if (typeof module.manuallyInstrument === 'function') {
        console.debug(`[KeywordsAI Debug] Attempting generic manual instrumentation for ${customDescription}...`);
        module.manuallyInstrument(module);
        loadingResults.push({ name: customName, status: "success", description: customDescription });
        console.debug(`[KeywordsAI Debug] Successfully initialized ${customDescription}`);
      } else {
        // Check if it's a valid instrumentation instance (has required OpenTelemetry methods)
        if (typeof module.setTracerProvider === 'function' && typeof module.getConfig === 'function') {
          console.debug(`[KeywordsAI Debug] Module ${moduleKey} appears to be an instrumentation instance, adding it...`);
          instrumentations.push(module);
          loadingResults.push({ name: customName, status: "success", description: customDescription });
          console.debug(`[KeywordsAI Debug] Successfully added ${customDescription} as instrumentation instance`);
        } else {
          // Not a valid instrumentation, skip it with a helpful message
          console.debug(`[KeywordsAI Debug] Module ${moduleKey} is not a valid OpenTelemetry instrumentation (missing required methods)`);
          loadingResults.push({ name: customName, status: "failed", description: customDescription, error: "Not a valid instrumentation" });
          console.info(`[KeywordsAI] Custom module '${moduleKey}' is not a valid OpenTelemetry instrumentation. It should either have a manuallyInstrument() method or be an Instrumentation instance.`);
        }
      }
    } catch (error) {
      loadingResults.push({ name: customName, status: "failed", description: customDescription, error });
      console.info(`[KeywordsAI] Failed to initialize custom module '${moduleKey}'. Make sure it's a valid OpenTelemetry instrumentation.`);
      console.debug(`[KeywordsAI Debug] Failed to initialize ${customDescription}:`, error);
    }
  }

  // Print summary
  const successful = loadingResults.filter(r => r.status === 'success');
  const failed = loadingResults.filter(r => r.status === 'failed'); 
  const disabled = loadingResults.filter(r => r.status === 'disabled');
  const notProvided = loadingResults.filter(r => r.status === 'not-provided');

  console.info(`[KeywordsAI] Manual instrumentation complete: ${successful.length} initialized, ${failed.length} failed, ${disabled.length} disabled, ${notProvided.length} not provided`);
  
  if (successful.length > 0) {
    console.info(`[KeywordsAI] Successfully initialized: ${successful.map(r => r.name).join(', ')}`);
  }
  
  if (disabled.length > 0) {
    console.info(`[KeywordsAI] Disabled instrumentations: ${disabled.map(r => r.name).join(', ')}`);
  }
  
  if (failed.length > 0) {
    console.debug(`[KeywordsAI Debug] Failed to initialize: ${failed.map(r => r.name).join(', ')}`);
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
    apiKey = process.env.KEYWORDSAI_API_KEY || "",
    baseUrl = _resolveEndpoint(process.env.KEYWORDSAI_BASE_URL || "https://api.keywordsai.co"),
    logLevel = "error",
    exporter,
    headers = {},
    propagator,
    contextManager,
    silenceInitializationMessage = false,
    tracingEnabled = true,
    instrumentModules,
    traceContent = true,
    disabledInstrumentations = [],
  } = options;

  // Debug logging for configuration
  console.debug("[KeywordsAI Debug] Tracing configuration:", {
    appName,
    baseUrl,
    logLevel,
    tracingEnabled,
    traceContent,
    hasApiKey: !!apiKey,
    apiKeyLength: apiKey?.length || 0,
    hasInstrumentModules: !!(instrumentModules && Object.keys(instrumentModules).length > 0),
    instrumentModulesKeys: instrumentModules ? Object.keys(instrumentModules) : [],
    customHeaders: Object.keys(headers),
    disabledInstrumentations: disabledInstrumentations || [],
  });

  if (!tracingEnabled) {
    if (!silenceInitializationMessage) {
      console.log("KeywordsAI tracing is disabled");
    }
    return;
  }

  // Debug API key validation
  if (!apiKey) {
    console.error("[KeywordsAI Debug] WARNING: No API key provided. Traces may be rejected by the server.");
  } else if (apiKey.length < 10) {
    console.warn("[KeywordsAI Debug] WARNING: API key seems unusually short. Please verify it's correct.");
  }

  // Initialize instrumentations with enhanced error logging
  try {
    if (instrumentModules && Object.keys(instrumentModules).length > 0) {
      console.debug("[KeywordsAI Debug] Using manual instrumentation for modules:", Object.keys(instrumentModules));
      await manuallyInitInstrumentations(instrumentModules, disabledInstrumentations);
    } else {
      console.debug("[KeywordsAI Debug] Using automatic instrumentation discovery");
      await initInstrumentations(disabledInstrumentations, false); // false = don't show warnings for auto-discovery
    }
    console.debug(`[KeywordsAI Debug] Successfully loaded ${instrumentations.length} instrumentations`);
  } catch (error) {
    console.error("[KeywordsAI Debug] Error during instrumentation initialization:", error);
    throw error;
  }

  // Configure trace content for instrumentations
  if (!shouldSendTraces() || !traceContent) {
    console.debug("[KeywordsAI Debug] Trace content disabled - sensitive data will not be captured");
    openAIInstrumentation?.setConfig?.({ traceContent: false });
    azureOpenAIInstrumentation?.setConfig?.({ traceContent: false });
    llamaIndexInstrumentation?.setConfig?.({ traceContent: false });
    vertexaiInstrumentation?.setConfig?.({ traceContent: false });
    bedrockInstrumentation?.setConfig?.({ traceContent: false });
    cohereInstrumentation?.setConfig?.({ traceContent: false });
    chromadbInstrumentation?.setConfig?.({ traceContent: false });
    togetherInstrumentation?.setConfig?.({ traceContent: false });
  } else {
    console.debug("[KeywordsAI Debug] Trace content enabled - input/output data will be captured");
  }

  // Set log level using proper DiagLogLevel
  const diagLogLevel = logLevel === "debug" ? DiagLogLevel.DEBUG 
    : logLevel === "info" ? DiagLogLevel.INFO 
    : logLevel === "warn" ? DiagLogLevel.WARN 
    : DiagLogLevel.ERROR;

  console.debug(`[KeywordsAI Debug] Setting OpenTelemetry diagnostic log level to: ${logLevel}`);

  diag.setLogger(
    {
      error: (...args) => console.error("[KeywordsAI OpenTelemetry]", ...args),
      warn: (...args) => console.warn("[KeywordsAI OpenTelemetry]", ...args),
      info: (...args) => console.info("[KeywordsAI OpenTelemetry]", ...args),
      debug: (...args) => console.debug("[KeywordsAI OpenTelemetry]", ...args),
      verbose: (...args) => console.debug("[KeywordsAI OpenTelemetry Verbose]", ...args),
    },
    diagLogLevel
  );

  // Create resource
  const resource = new Resource({
    [ATTR_SERVICE_NAME]: appName,
  });
  console.debug("[KeywordsAI Debug] Created resource with service name:", appName);

  // Prepare exporter URL and configuration
  const exporterUrl = `${baseUrl}/api/v1/traces`;
  const exporterHeaders = {
    "Authorization": `Bearer ${apiKey}`,
    "Content-Type": "application/x-protobuf",
    ...headers,
  };

  console.debug("[KeywordsAI Debug] Exporter configuration:", {
    url: exporterUrl,
    headersCount: Object.keys(exporterHeaders).length,
    hasAuth: exporterHeaders.Authorization ? "Yes" : "No",
    customHeaderKeys: Object.keys(headers),
  });

  // Create exporter with enhanced error handling
  const traceExporter = exporter || new OTLPTraceExporter({
    url: exporterUrl,
    headers: exporterHeaders,
  });

  console.debug("[KeywordsAI Debug] Created OTLP trace exporter");

  // Initialize SDK
  console.log(`[KeywordsAI Debug] Initializing NodeSDK with ${instrumentations.length} instrumentations:`, 
    instrumentations.map((inst: any) => inst.constructor.name)
  );

  _sdk = new NodeSDK({
    resource,
    traceExporter,
    instrumentations,
    textMapPropagator: propagator,
    contextManager,
  });

  try {
    console.debug("[KeywordsAI Debug] Starting OpenTelemetry SDK...");
    _sdk.start();
    _initialized = true;
    
    console.debug("[KeywordsAI Debug] SDK started successfully");
    
    if (!silenceInitializationMessage) {
      console.log("KeywordsAI tracing initialized successfully");
      console.log(`[KeywordsAI Debug] Traces will be sent to: ${exporterUrl}`);
    }
  } catch (error) {
    console.error("[KeywordsAI Debug] Failed to start OpenTelemetry SDK:", error);
    console.error("[KeywordsAI Debug] Error details:", {
      message: (error as Error).message,
      stack: (error as Error).stack,
      exporterUrl,
      instrumentationCount: instrumentations.length,
    });
    throw error;
  }
};

// Enhanced error logging for forceFlush
export const forceFlush = async (): Promise<void> => {
  if (_sdk) {
    try {
      console.debug("[KeywordsAI Debug] Shutting down SDK and flushing traces...");
      await _sdk.shutdown();
      console.debug("[KeywordsAI Debug] SDK shutdown completed");
    } catch (error) {
      console.error("[KeywordsAI Debug] Error during SDK shutdown:", error);
      console.error("[KeywordsAI Debug] Shutdown error details:", {
        message: (error as Error).message,
        stack: (error as Error).stack,
      });
    }
  } else {
    console.debug("[KeywordsAI Debug] No SDK to shutdown");
  }
};

// Instrumentation metadata for installation hints
const INSTRUMENTATION_INFO: Record<string, { 
  packageName: string; 
  importPackage: string; 
  description: string; 
  installCommand: string;
}> = {
  "openAI": {
    packageName: "@traceloop/instrumentation-openai",
    importPackage: "@traceloop/instrumentation-openai", 
    description: "OpenAI API instrumentation",
    installCommand: "npm install @traceloop/instrumentation-openai"
  },
  "anthropic": {
    packageName: "@traceloop/instrumentation-anthropic",
    importPackage: "@traceloop/instrumentation-anthropic",
    description: "Anthropic API instrumentation", 
    installCommand: "npm install @traceloop/instrumentation-anthropic"
  },
  "azureOpenAI": {
    packageName: "@traceloop/instrumentation-azure", 
    importPackage: "@traceloop/instrumentation-azure",
    description: "Azure OpenAI instrumentation",
    installCommand: "npm install @traceloop/instrumentation-azure"
  },
  "bedrock": {
    packageName: "@traceloop/instrumentation-bedrock",
    importPackage: "@traceloop/instrumentation-bedrock",
    description: "AWS Bedrock instrumentation", 
    installCommand: "npm install @traceloop/instrumentation-bedrock"
  },
  "cohere": {
    packageName: "@traceloop/instrumentation-cohere",
    importPackage: "@traceloop/instrumentation-cohere", 
    description: "Cohere API instrumentation",
    installCommand: "npm install @traceloop/instrumentation-cohere"
  },
  "langChain": {
    packageName: "@traceloop/instrumentation-langchain",
    importPackage: "@traceloop/instrumentation-langchain",
    description: "LangChain framework instrumentation",
    installCommand: "npm install @traceloop/instrumentation-langchain" 
  },
  "llamaIndex": {
    packageName: "@traceloop/instrumentation-llamaindex",
    importPackage: "@traceloop/instrumentation-llamaindex", 
    description: "LlamaIndex framework instrumentation",
    installCommand: "npm install @traceloop/instrumentation-llamaindex"
  },
  "pinecone": {
    packageName: "@traceloop/instrumentation-pinecone",
    importPackage: "@traceloop/instrumentation-pinecone",
    description: "Pinecone vector database instrumentation", 
    installCommand: "npm install @traceloop/instrumentation-pinecone"
  },
  "chromaDB": {
    packageName: "@traceloop/instrumentation-chromadb",
    importPackage: "@traceloop/instrumentation-chromadb",
    description: "ChromaDB vector database instrumentation",
    installCommand: "npm install @traceloop/instrumentation-chromadb"
  },
  "qdrant": {
    packageName: "@traceloop/instrumentation-qdrant", 
    importPackage: "@traceloop/instrumentation-qdrant",
    description: "Qdrant vector database instrumentation",
    installCommand: "npm install @traceloop/instrumentation-qdrant"
  },
  "together": {
    packageName: "@traceloop/instrumentation-together",
    importPackage: "@traceloop/instrumentation-together",
    description: "Together AI instrumentation", 
    installCommand: "npm install @traceloop/instrumentation-together"
  },
  "googleVertexAI": {
    packageName: "@traceloop/instrumentation-vertexai",
    importPackage: "@traceloop/instrumentation-vertexai",
    description: "Google Vertex AI instrumentation",
    installCommand: "npm install @traceloop/instrumentation-vertexai"
  },
  "googleAIPlatform": {
    packageName: "@traceloop/instrumentation-vertexai",
    importPackage: "@traceloop/instrumentation-vertexai", 
    description: "Google AI Platform instrumentation",
    installCommand: "npm install @traceloop/instrumentation-vertexai"
  }
};

// Dynamic instrumentation loading with enhanced logging and installation hints
export const loadInstrumentation = async (name: string): Promise<Instrumentation | null> => {
  console.debug(`[KeywordsAI Debug] Attempting to load instrumentation: ${name}`);
  
  const info = INSTRUMENTATION_INFO[name];
  if (!info) {
    console.warn(`[KeywordsAI] Unknown instrumentation: ${name}`);
    return null;
  }

  try {
    console.debug(`[KeywordsAI Debug] Loading ${info.description}...`);
    
    switch (name) {
      case "openAI":
        const { OpenAIInstrumentation } = await import("@traceloop/instrumentation-openai");
        console.debug(`[KeywordsAI Debug] Successfully imported ${info.description}`);
        return new OpenAIInstrumentation({
          enrichTokens: true,
          exceptionLogger: (e: Error) => console.error("OpenAI instrumentation error:", e),
        });
      
      case "anthropic":
        const { AnthropicInstrumentation } = await import("@traceloop/instrumentation-anthropic");
        console.debug(`[KeywordsAI Debug] Successfully imported ${info.description}`);
        return new AnthropicInstrumentation({
          exceptionLogger: (e: Error) => console.error("Anthropic instrumentation error:", e),
        });
      
      case "azureOpenAI":
        const { AzureOpenAIInstrumentation } = await import("@traceloop/instrumentation-azure");
        console.debug(`[KeywordsAI Debug] Successfully imported ${info.description}`);
        return new AzureOpenAIInstrumentation({
          exceptionLogger: (e: Error) => console.error("Azure instrumentation error:", e),
        });
      
      case "bedrock":
        const { BedrockInstrumentation } = await import("@traceloop/instrumentation-bedrock");
        console.debug(`[KeywordsAI Debug] Successfully imported ${info.description}`);
        return new BedrockInstrumentation({
          exceptionLogger: (e: Error) => console.error("Bedrock instrumentation error:", e),
        });
      
      case "cohere":
        const { CohereInstrumentation } = await import("@traceloop/instrumentation-cohere");
        console.debug(`[KeywordsAI Debug] Successfully imported ${info.description}`);
        return new CohereInstrumentation({
          exceptionLogger: (e: Error) => console.error("Cohere instrumentation error:", e),
        });
      
      case "langChain":
        const { LangChainInstrumentation } = await import("@traceloop/instrumentation-langchain");
        console.debug(`[KeywordsAI Debug] Successfully imported ${info.description}`);
        return new LangChainInstrumentation({
          exceptionLogger: (e: Error) => console.error("LangChain instrumentation error:", e),
        });
      
      case "llamaIndex":
        const { LlamaIndexInstrumentation } = await import("@traceloop/instrumentation-llamaindex");
        console.debug(`[KeywordsAI Debug] Successfully imported ${info.description}`);
        return new LlamaIndexInstrumentation({
          exceptionLogger: (e: Error) => console.error("LlamaIndex instrumentation error:", e),
        });
      
      case "pinecone":
        const { PineconeInstrumentation } = await import("@traceloop/instrumentation-pinecone");
        console.debug(`[KeywordsAI Debug] Successfully imported ${info.description}`);
        return new PineconeInstrumentation({
          exceptionLogger: (e: Error) => console.error("Pinecone instrumentation error:", e),
        });
      
      case "chromaDB":
        const { ChromaDBInstrumentation } = await import("@traceloop/instrumentation-chromadb");
        console.debug(`[KeywordsAI Debug] Successfully imported ${info.description}`);
        return new ChromaDBInstrumentation({
          exceptionLogger: (e: Error) => console.error("ChromaDB instrumentation error:", e),
        });
      
      case "qdrant":
        const { QdrantInstrumentation } = await import("@traceloop/instrumentation-qdrant");
        console.debug(`[KeywordsAI Debug] Successfully imported ${info.description}`);
        return new QdrantInstrumentation({
          exceptionLogger: (e: Error) => console.error("Qdrant instrumentation error:", e),
        });
      
      case "together":
        const { TogetherInstrumentation } = await import("@traceloop/instrumentation-together");
        console.debug(`[KeywordsAI Debug] Successfully imported ${info.description}`);
        return new TogetherInstrumentation({
          exceptionLogger: (e: Error) => console.error("Together instrumentation error:", e),
        });
      
      case "googleVertexAI":
        const { VertexAIInstrumentation } = await import("@traceloop/instrumentation-vertexai");
        console.debug(`[KeywordsAI Debug] Successfully imported ${info.description}`);
        return new VertexAIInstrumentation({
          exceptionLogger: (e: Error) => console.error("VertexAI instrumentation error:", e),
        });

      case "googleAIPlatform":
        const { AIPlatformInstrumentation } = await import("@traceloop/instrumentation-vertexai");
        console.debug(`[KeywordsAI Debug] Successfully imported ${info.description}`);
        return new AIPlatformInstrumentation({
          exceptionLogger: (e: Error) => console.error("AI Platform instrumentation error:", e),
        });
      
      default:
        console.warn(`[KeywordsAI] Unknown instrumentation: ${name}`);
        return null;
    }
  } catch (error) {
    console.info(`[KeywordsAI] ${info.description} is not available. To enable it, install the required package:\n   ${info.installCommand}`);
    console.debug(`[KeywordsAI Debug] Failed to load ${name} instrumentation:`, error);
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
    console.debug("[KeywordsAI Debug] No active span found. Cannot update span.");
    return false;
  }

  try {
    const { keywordsaiParams, attributes, status, statusDescription, name } = options;

    console.debug("[KeywordsAI Debug] Updating current span with:", {
      hasKeywordsaiParams: !!keywordsaiParams,
      keywordsaiParamsKeys: keywordsaiParams ? Object.keys(keywordsaiParams) : [],
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
          console.warn(`[KeywordsAI Debug] Failed to set attribute ${key}=${value}:`, error);
        }
      });
    }

    // Set status
    if (status !== undefined) {
      currentSpan.setStatus({
        code: status,
        message: statusDescription
      });
      console.debug(`[KeywordsAI Debug] Set span status: ${status}${statusDescription ? ` (${statusDescription})` : ''}`);
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
const setKeywordsAIAttributes = (span: Span, keywordsaiParams: Record<string, any>): void => {
  try {
    console.debug("[KeywordsAI Debug] Setting KeywordsAI attributes:", keywordsaiParams);

    // Validate parameters using the imported schema
    let validatedParams: Record<string, any>;
    try {
      validatedParams = KeywordsAIParamsSchema.parse(keywordsaiParams);
      console.debug("[KeywordsAI Debug] Parameters validated successfully");
    } catch (validationError) {
      console.warn("[KeywordsAI Debug] Failed to validate KeywordsAI params:", validationError);
      // Use original params if validation fails, but continue processing
      validatedParams = keywordsaiParams;
    }

    // Set attributes based on the imported mapping
    Object.entries(validatedParams).forEach(([key, value]) => {
      if (key in KEYWORDSAI_SPAN_ATTRIBUTES_MAP && key !== "metadata") {
        try {
          const attributeKey = KEYWORDSAI_SPAN_ATTRIBUTES_MAP[key];
          span.setAttribute(attributeKey, value);
          console.debug(`[KeywordsAI Debug] Set KeywordsAI attribute: ${attributeKey}=${value}`);
        } catch (error) {
          console.warn(`[KeywordsAI Debug] Failed to set span attribute ${KEYWORDSAI_SPAN_ATTRIBUTES_MAP[key]}=${value}:`, error);
        }
      }

      // Handle metadata specially using the proper enum
      if (key === "metadata" && typeof value === "object" && value !== null) {
        console.debug("[KeywordsAI Debug] Setting metadata attributes:", value);
        Object.entries(value as Record<string, any>).forEach(([metadataKey, metadataValue]) => {
          try {
            const fullKey = `${KeywordsAISpanAttributes.KEYWORDSAI_METADATA}.${metadataKey}`;
            span.setAttribute(fullKey, metadataValue);
            console.debug(`[KeywordsAI Debug] Set metadata attribute: ${fullKey}=${metadataValue}`);
          } catch (error) {
            console.warn(`[KeywordsAI Debug] Failed to set metadata attribute ${metadataKey}=${metadataValue}:`, error);
          }
        });
      }
    });
  } catch (error) {
    console.error("[KeywordsAI Debug] Unexpected error setting KeywordsAI attributes:", error);
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