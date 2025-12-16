import { NodeSDK } from "@opentelemetry/sdk-node";
import { diag, DiagLogLevel } from "@opentelemetry/api";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-proto";
import { Resource } from "@opentelemetry/resources";
import { ATTR_SERVICE_NAME } from "@opentelemetry/semantic-conventions";
import { KeywordsAIOptions, ProcessorConfig } from "../types/clientTypes.js";
import { MultiProcessorManager } from "../processor/manager.js";
import { KeywordsAICompositeProcessor } from "../processor/composite.js";
import { 
  getInstrumentations, 
  initInstrumentations, 
  manuallyInitInstrumentations,
  configureTraceContent
} from "../instrumentation/index.js";
import { shouldSendTraces } from "./context.js";

// Global SDK instance (singleton)
let _sdk: NodeSDK;
let _initialized: boolean = false;
let _compositeProcessor: KeywordsAICompositeProcessor | undefined;

/**
 * Helper function to resolve and clean up the base URL
 */
export const _resolveBaseURL = (baseURL: string) => {
  const originalUrl = baseURL;

  // Remove trailing slash if it exists
  if (baseURL.endsWith("/")) {
    baseURL = baseURL.slice(0, -1);
  }
  // Remove trailing /api if it exists
  if (baseURL.endsWith("/api")) {
    baseURL = baseURL.slice(0, -4);
  }

  // Debug logging for URL resolution
  if (originalUrl !== baseURL) {
    console.debug(
      `[KeywordsAI Debug] URL resolved: "${originalUrl}" -> "${baseURL}"`
    );
  } else {
    console.debug(`[KeywordsAI Debug] URL used as-is: "${baseURL}"`);
  }

  return baseURL;
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
    baseURL = process.env.KEYWORDSAI_BASE_URL || "https://api.keywordsai.co",
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
    resourceAttributes = {},
    spanPostprocessCallback,
  } = options;

  // Debug logging for configuration
  console.debug("[KeywordsAI Debug] Tracing configuration:", {
    appName,
    baseURL,
    logLevel,
    tracingEnabled,
    traceContent,
    hasApiKey: !!apiKey,
    apiKeyLength: apiKey?.length || 0,
    hasInstrumentModules: !!(
      instrumentModules && Object.keys(instrumentModules).length > 0
    ),
    instrumentModulesKeys: instrumentModules
      ? Object.keys(instrumentModules)
      : [],
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
    console.error(
      "[KeywordsAI Debug] WARNING: No API key provided. Traces may be rejected by the server."
    );
  } else if (apiKey.length < 10) {
    console.warn(
      "[KeywordsAI Debug] WARNING: API key seems unusually short. Please verify it's correct."
    );
  }

  // Initialize instrumentations with enhanced error logging
  try {
    if (instrumentModules && Object.keys(instrumentModules).length > 0) {
      console.debug(
        "[KeywordsAI Debug] Using manual instrumentation for modules:",
        Object.keys(instrumentModules)
      );
      await manuallyInitInstrumentations(
        instrumentModules,
        disabledInstrumentations
      );
    } else {
      console.debug(
        "[KeywordsAI Debug] Using automatic instrumentation discovery"
      );
      await initInstrumentations(disabledInstrumentations, false); // false = don't show warnings for auto-discovery
    }
    
    const instrumentationsList = getInstrumentations();
    console.debug(
      `[KeywordsAI Debug] Total instrumentations ready for SDK: ${instrumentationsList.length}`
    );
  } catch (error) {
    console.error(
      "[KeywordsAI Debug] Error during instrumentation initialization:",
      error
    );
    throw error;
  }

  // Configure trace content for instrumentations
  const shouldCapture = shouldSendTraces() && traceContent;
  configureTraceContent(shouldCapture);
  
  if (!shouldCapture) {
    console.debug(
      "[KeywordsAI Debug] Trace content disabled - sensitive data will not be captured"
    );
  } else {
    console.debug(
      "[KeywordsAI Debug] Trace content enabled - input/output data will be captured"
    );
  }

  // Set log level using proper DiagLogLevel
  const diagLogLevel =
    logLevel === "debug"
      ? DiagLogLevel.DEBUG
      : logLevel === "info"
      ? DiagLogLevel.INFO
      : logLevel === "warn"
      ? DiagLogLevel.WARN
      : DiagLogLevel.ERROR;

  console.debug(
    `[KeywordsAI Debug] Setting OpenTelemetry diagnostic log level to: ${logLevel}`
  );

  diag.setLogger(
    {
      error: (...args) => console.error("[KeywordsAI OpenTelemetry]", ...args),
      warn: (...args) => console.warn("[KeywordsAI OpenTelemetry]", ...args),
      info: (...args) => console.info("[KeywordsAI OpenTelemetry]", ...args),
      debug: (...args) => console.debug("[KeywordsAI OpenTelemetry]", ...args),
      verbose: (...args) =>
        console.debug("[KeywordsAI OpenTelemetry Verbose]", ...args),
    },
    diagLogLevel
  );

  // Create resource with custom attributes
  const resource = new Resource({
    [ATTR_SERVICE_NAME]: appName,
    ...resourceAttributes,
  });
  console.debug(
    "[KeywordsAI Debug] Created resource with service name:",
    appName,
    "and attributes:",
    resourceAttributes
  );

  // Prepare exporter URL and configuration
  const exporterUrl = `${_resolveBaseURL(baseURL)}/api/v1/traces`;
  const exporterHeaders = {
    Authorization: `Bearer ${apiKey}`,
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
  const traceExporter =
    exporter ||
    new OTLPTraceExporter({
      url: exporterUrl,
      headers: exporterHeaders,
    });

  console.debug("[KeywordsAI Debug] Created OTLP trace exporter");

  // Initialize multi-processor manager
  const processorManager = new MultiProcessorManager();
  
  // Add default KeywordsAI processor to the manager
  // This ensures backward compatibility: spans without a `processors` attribute
  // automatically go to the default KeywordsAI exporter
  processorManager.addProcessor({
    exporter: traceExporter,
    name: "default",
    priority: 0,
  });
  
  console.debug("[KeywordsAI Debug] Added default processor to multi-processor manager (backward compatibility)");

  // Create composite processor that does filtering + routing
  // Flow: SDK -> CompositeProcessor (filters) -> ProcessorManager (routes) -> Individual Processors
  _compositeProcessor = new KeywordsAICompositeProcessor(
    processorManager,
    spanPostprocessCallback
  );
  
  console.debug("[KeywordsAI Debug] Created composite processor - filters spans and routes to multiple processors");

  // Get instrumentations for SDK
  const instrumentationsList = getInstrumentations();

  // Initialize SDK
  console.debug(
    `[KeywordsAI Debug] Initializing NodeSDK with ${instrumentationsList.length} successfully loaded instrumentations:`,
    instrumentationsList.map((inst: any) => inst.constructor.name)
  );

  _sdk = new NodeSDK({
    resource,
    spanProcessors: [_compositeProcessor],
    instrumentations: instrumentationsList,
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
    console.error(
      "[KeywordsAI Debug] Failed to start OpenTelemetry SDK:",
      error
    );
    console.error("[KeywordsAI Debug] Error details:", {
      message: (error as Error).message,
      stack: (error as Error).stack,
      exporterUrl,
      instrumentationCount: instrumentationsList.length,
    });
    throw error;
  }
};

/**
 * Enhanced error logging for forceFlush
 */
export const forceFlush = async (): Promise<void> => {
  if (_sdk) {
    try {
      console.debug(
        "[KeywordsAI Debug] Shutting down SDK and flushing traces..."
      );
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
 * Add a processor to the SDK for routing spans.
 * This allows routing spans to different destinations based on processor names.
 * 
 * @param config - Processor configuration
 */
export const addProcessorToSDK = (config: ProcessorConfig): void => {
  if (!_compositeProcessor) {
    console.error("[KeywordsAI] Cannot add processor - SDK not initialized");
    return;
  }
  
  const processorManager = _compositeProcessor.getProcessorManager();
  processorManager.addProcessor(config);
  console.log(`[KeywordsAI] Added processor: ${config.name}`);
};
