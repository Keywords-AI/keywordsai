import { Instrumentation } from "@opentelemetry/instrumentation";
import { InstrumentationName, KeywordsAIOptions } from "../types/clientTypes.js";
import { loadInstrumentation } from "./loader.js";
import { 
  InstrumentationLoadResult, 
  InstrumentationConfig, 
  ManualInstrumentationConfig,
  INSTRUMENTATION_INFO 
} from "../types/index.js";

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
 * Get all loaded instrumentations
 */
export const getInstrumentations = (): Instrumentation[] => {
  return [...instrumentations];
};

/**
 * Get a specific instrumentation instance by name
 */
export const getInstrumentationInstance = (name: InstrumentationName): any => {
  switch (name) {
    case "openAI": return openAIInstrumentation;
    case "anthropic": return anthropicInstrumentation;
    case "azureOpenAI": return azureOpenAIInstrumentation;
    case "cohere": return cohereInstrumentation;
    case "googleVertexAI": return vertexaiInstrumentation;
    case "bedrock": return bedrockInstrumentation;
    case "langChain": return langchainInstrumentation;
    case "llamaIndex": return llamaIndexInstrumentation;
    case "pinecone": return pineconeInstrumentation;
    case "chromaDB": return chromadbInstrumentation;
    case "qdrant": return qdrantInstrumentation;
    case "together": return togetherInstrumentation;
    default: return undefined;
  }
};

/**
 * Configure trace content for instrumentations
 */
export const configureTraceContent = (enabled: boolean): void => {
  const traceContent = enabled;
  
  console.debug(
    `[KeywordsAI Debug] Configuring trace content: ${enabled ? 'enabled' : 'disabled'}`
  );

  openAIInstrumentation?.setConfig?.({ traceContent });
  anthropicInstrumentation?.setConfig?.({ traceContent });
  azureOpenAIInstrumentation?.setConfig?.({ traceContent });
  llamaIndexInstrumentation?.setConfig?.({ traceContent });
  vertexaiInstrumentation?.setConfig?.({ traceContent });
  bedrockInstrumentation?.setConfig?.({ traceContent });
  cohereInstrumentation?.setConfig?.({ traceContent });
  chromadbInstrumentation?.setConfig?.({ traceContent });
  togetherInstrumentation?.setConfig?.({ traceContent });
};

/**
 * Initialize all available instrumentations automatically.
 * This is used when no specific instrumentModules are provided.
 */
export const initInstrumentations = async (
  disabledInstrumentations: InstrumentationName[] = [],
  showInstallWarnings: boolean = true
): Promise<void> => {
  const exceptionLogger = (e: Error) =>
    console.error("Instrumentation error:", e);

  console.info(
    "[KeywordsAI] Initializing automatic instrumentation discovery..."
  );

  // Track instrumentation loading results
  const loadingResults: InstrumentationLoadResult[] = [];

  // Clear the instrumentations array
  instrumentations.length = 0;

  // Define all instrumentations to attempt loading
  const instrumentationsToLoad: InstrumentationConfig[] = [
    {
      name: "openAI",
      description: "OpenAI API instrumentation",
      loadFunction: async () => {
        const { OpenAIInstrumentation } = await import(
          "@traceloop/instrumentation-openai"
        );
        openAIInstrumentation = new OpenAIInstrumentation({
          enrichTokens: true,
          exceptionLogger: (e: Error) =>
            console.error("OpenAI instrumentation error:", e),
        });
        return openAIInstrumentation;
      },
    },
    {
      name: "anthropic",
      description: "Anthropic API instrumentation",
      loadFunction: async () => {
        const { AnthropicInstrumentation } = await import(
          "@traceloop/instrumentation-anthropic"
        );
        anthropicInstrumentation = new AnthropicInstrumentation({
          exceptionLogger,
        });
        return anthropicInstrumentation;
      },
    },
    {
      name: "azureOpenAI",
      description: "Azure OpenAI instrumentation",
      loadFunction: async () => {
        const { AzureOpenAIInstrumentation } = await import(
          "@traceloop/instrumentation-azure"
        );
        azureOpenAIInstrumentation = new AzureOpenAIInstrumentation({
          exceptionLogger,
        });
        return azureOpenAIInstrumentation;
      },
    },
    {
      name: "cohere",
      description: "Cohere API instrumentation",
      loadFunction: async () => {
        const { CohereInstrumentation } = await import(
          "@traceloop/instrumentation-cohere"
        );
        cohereInstrumentation = new CohereInstrumentation({ exceptionLogger });
        return cohereInstrumentation;
      },
    },
    {
      name: "googleVertexAI",
      description: "Google Vertex AI instrumentation",
      loadFunction: async () => {
        const { VertexAIInstrumentation } = await import(
          "@traceloop/instrumentation-vertexai"
        );
        vertexaiInstrumentation = new VertexAIInstrumentation({
          exceptionLogger,
        });
        return vertexaiInstrumentation;
      },
    },
    {
      name: "bedrock",
      description: "AWS Bedrock instrumentation",
      loadFunction: async () => {
        const { BedrockInstrumentation } = await import(
          "@traceloop/instrumentation-bedrock"
        );
        bedrockInstrumentation = new BedrockInstrumentation({
          exceptionLogger,
        });
        return bedrockInstrumentation;
      },
    },
    {
      name: "langChain",
      description: "LangChain framework instrumentation",
      loadFunction: async () => {
        const { LangChainInstrumentation } = await import(
          "@traceloop/instrumentation-langchain"
        );
        langchainInstrumentation = new LangChainInstrumentation({
          exceptionLogger,
        });
        return langchainInstrumentation;
      },
    },
    {
      name: "llamaIndex",
      description: "LlamaIndex framework instrumentation",
      loadFunction: async () => {
        const { LlamaIndexInstrumentation } = await import(
          "@traceloop/instrumentation-llamaindex"
        );
        llamaIndexInstrumentation = new LlamaIndexInstrumentation({
          exceptionLogger,
        });
        return llamaIndexInstrumentation;
      },
    },
    {
      name: "pinecone",
      description: "Pinecone vector database instrumentation",
      loadFunction: async () => {
        const { PineconeInstrumentation } = await import(
          "@traceloop/instrumentation-pinecone"
        );
        pineconeInstrumentation = new PineconeInstrumentation({
          exceptionLogger,
        });
        return pineconeInstrumentation;
      },
    },
    {
      name: "chromaDB",
      description: "ChromaDB vector database instrumentation",
      loadFunction: async () => {
        const { ChromaDBInstrumentation } = await import(
          "@traceloop/instrumentation-chromadb"
        );
        chromadbInstrumentation = new ChromaDBInstrumentation({
          exceptionLogger,
        });
        return chromadbInstrumentation;
      },
    },
    {
      name: "qdrant",
      description: "Qdrant vector database instrumentation",
      loadFunction: async () => {
        const { QdrantInstrumentation } = await import(
          "@traceloop/instrumentation-qdrant"
        );
        qdrantInstrumentation = new QdrantInstrumentation({ exceptionLogger });
        return qdrantInstrumentation;
      },
    },
    {
      name: "together",
      description: "Together AI instrumentation",
      loadFunction: async () => {
        const { TogetherInstrumentation } = await import(
          "@traceloop/instrumentation-together"
        );
        togetherInstrumentation = new TogetherInstrumentation({
          exceptionLogger,
        });
        return togetherInstrumentation;
      },
    },
  ];

  // Load each instrumentation
  for (const { name, description, loadFunction } of instrumentationsToLoad) {
    if (disabledInstrumentations.includes(name)) {
      loadingResults.push({ name, status: "disabled", description });
      console.debug(
        `[KeywordsAI Debug] Skipping ${description} (disabled by configuration)`
      );
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
          console.info(
            `[KeywordsAI] ${description} is not available. To enable it, install the required package:\n   ${info.installCommand}`
          );
        }
      }
      console.debug(`[KeywordsAI Debug] Failed to load ${description}:`, error);
    }
  }

  // Print summary
  const successful = loadingResults.filter((r) => r.status === "success");
  const failed = loadingResults.filter((r) => r.status === "failed");
  const disabled = loadingResults.filter((r) => r.status === "disabled");

  console.info(
    `[KeywordsAI] Instrumentation loading complete: ${successful.length} loaded, ${failed.length} failed, ${disabled.length} disabled`
  );

  if (successful.length > 0) {
    console.info(
      `[KeywordsAI] Successfully loaded: ${successful
        .map((r) => r.name)
        .join(", ")}`
    );
  }

  if (disabled.length > 0) {
    console.info(
      `[KeywordsAI] Disabled instrumentations: ${disabled
        .map((r) => r.name)
        .join(", ")}`
    );
  }

  if (failed.length > 0) {
    console.debug(
      `[KeywordsAI Debug] Failed to load: ${failed
        .map((r) => r.name)
        .join(", ")}`
    );
  }
};

/**
 * Manually initialize instrumentations with provided modules.
 * This is similar to Traceloop's approach for environments like Next.js
 * where dynamic imports might not work properly.
 */
export const manuallyInitInstrumentations = async (
  instrumentModules: NonNullable<KeywordsAIOptions["instrumentModules"]>,
  disabledInstrumentations: InstrumentationName[] = []
): Promise<void> => {
  const exceptionLogger = (e: Error) =>
    console.error("Instrumentation error:", e);

  console.info(
    "[KeywordsAI] Initializing manual instrumentation with provided modules..."
  );
  console.debug(
    "[KeywordsAI Debug] Provided modules:",
    Object.keys(instrumentModules)
  );

  // Track instrumentation loading results (using string for name to allow custom modules)
  const loadingResults: InstrumentationLoadResult[] = [];

  // Clear the instrumentations array
  instrumentations.length = 0;

  // Define all possible manual instrumentations
  const manualInstrumentationConfigs: ManualInstrumentationConfig[] = [
    {
      name: "openAI",
      description: "OpenAI API instrumentation",
      moduleKey: "openAI",
      initFunction: async (module: any) => {
        const { OpenAIInstrumentation } = await import(
          "@traceloop/instrumentation-openai"
        );
        openAIInstrumentation = new OpenAIInstrumentation({
          enrichTokens: true,
          exceptionLogger,
        });
        instrumentations.push(openAIInstrumentation);
        openAIInstrumentation.manuallyInstrument(module);
        return openAIInstrumentation;
      },
    },
    {
      name: "anthropic",
      description: "Anthropic API instrumentation",
      moduleKey: "anthropic",
      initFunction: async (module: any) => {
        const { AnthropicInstrumentation } = await import(
          "@traceloop/instrumentation-anthropic"
        );
        anthropicInstrumentation = new AnthropicInstrumentation({
          exceptionLogger,
        });
        instrumentations.push(anthropicInstrumentation);
        anthropicInstrumentation.manuallyInstrument(module);
        return anthropicInstrumentation;
      },
    },
    {
      name: "azureOpenAI",
      description: "Azure OpenAI instrumentation",
      moduleKey: "azureOpenAI",
      initFunction: async (module: any) => {
        const { AzureOpenAIInstrumentation } = await import(
          "@traceloop/instrumentation-azure"
        );
        azureOpenAIInstrumentation = new AzureOpenAIInstrumentation({
          exceptionLogger,
        });
        instrumentations.push(azureOpenAIInstrumentation);
        azureOpenAIInstrumentation.manuallyInstrument(module);
        return azureOpenAIInstrumentation;
      },
    },
    {
      name: "cohere",
      description: "Cohere API instrumentation",
      moduleKey: "cohere",
      initFunction: async (module: any) => {
        const { CohereInstrumentation } = await import(
          "@traceloop/instrumentation-cohere"
        );
        cohereInstrumentation = new CohereInstrumentation({ exceptionLogger });
        instrumentations.push(cohereInstrumentation);
        cohereInstrumentation.manuallyInstrument(module);
        return cohereInstrumentation;
      },
    },
    {
      name: "googleVertexAI",
      description: "Google Vertex AI instrumentation",
      moduleKey: "googleVertexAI",
      initFunction: async (module: any) => {
        const { VertexAIInstrumentation } = await import(
          "@traceloop/instrumentation-vertexai"
        );
        vertexaiInstrumentation = new VertexAIInstrumentation({
          exceptionLogger,
        });
        instrumentations.push(vertexaiInstrumentation);
        vertexaiInstrumentation.manuallyInstrument(module);
        return vertexaiInstrumentation;
      },
    },
    {
      name: "googleAIPlatform",
      description: "Google AI Platform instrumentation",
      moduleKey: "googleAIPlatform",
      initFunction: async (module: any) => {
        const { AIPlatformInstrumentation } = await import(
          "@traceloop/instrumentation-vertexai"
        );
        const aiplatformInstrumentation = new AIPlatformInstrumentation({
          exceptionLogger,
        });
        instrumentations.push(aiplatformInstrumentation);
        aiplatformInstrumentation.manuallyInstrument(module);
        return aiplatformInstrumentation;
      },
    },
    {
      name: "bedrock",
      description: "AWS Bedrock instrumentation",
      moduleKey: "bedrock",
      initFunction: async (module: any) => {
        const { BedrockInstrumentation } = await import(
          "@traceloop/instrumentation-bedrock"
        );
        bedrockInstrumentation = new BedrockInstrumentation({
          exceptionLogger,
        });
        instrumentations.push(bedrockInstrumentation);
        bedrockInstrumentation.manuallyInstrument(module);
        return bedrockInstrumentation;
      },
    },
    {
      name: "pinecone",
      description: "Pinecone vector database instrumentation",
      moduleKey: "pinecone",
      initFunction: async (module: any) => {
        const { PineconeInstrumentation } = await import(
          "@traceloop/instrumentation-pinecone"
        );
        pineconeInstrumentation = new PineconeInstrumentation({
          exceptionLogger,
        });
        instrumentations.push(pineconeInstrumentation);
        pineconeInstrumentation.manuallyInstrument(module);
        return pineconeInstrumentation;
      },
    },
    {
      name: "langChain",
      description: "LangChain framework instrumentation",
      moduleKey: "langChain",
      initFunction: async (module: any) => {
        const { LangChainInstrumentation } = await import(
          "@traceloop/instrumentation-langchain"
        );
        langchainInstrumentation = new LangChainInstrumentation({
          exceptionLogger,
        });
        instrumentations.push(langchainInstrumentation);
        langchainInstrumentation.manuallyInstrument(module);
        return langchainInstrumentation;
      },
    },
    {
      name: "llamaIndex",
      description: "LlamaIndex framework instrumentation",
      moduleKey: "llamaIndex",
      initFunction: async (module: any) => {
        const { LlamaIndexInstrumentation } = await import(
          "@traceloop/instrumentation-llamaindex"
        );
        llamaIndexInstrumentation = new LlamaIndexInstrumentation({
          exceptionLogger,
        });
        instrumentations.push(llamaIndexInstrumentation);
        llamaIndexInstrumentation.manuallyInstrument(module);
        return llamaIndexInstrumentation;
      },
    },
    {
      name: "chromaDB",
      description: "ChromaDB vector database instrumentation",
      moduleKey: "chromaDB",
      initFunction: async (module: any) => {
        const { ChromaDBInstrumentation } = await import(
          "@traceloop/instrumentation-chromadb"
        );
        chromadbInstrumentation = new ChromaDBInstrumentation({
          exceptionLogger,
        });
        instrumentations.push(chromadbInstrumentation);
        chromadbInstrumentation.manuallyInstrument(module);
        return chromadbInstrumentation;
      },
    },
    {
      name: "qdrant",
      description: "Qdrant vector database instrumentation",
      moduleKey: "qdrant",
      initFunction: async (module: any) => {
        const { QdrantInstrumentation } = await import(
          "@traceloop/instrumentation-qdrant"
        );
        qdrantInstrumentation = new QdrantInstrumentation({ exceptionLogger });
        instrumentations.push(qdrantInstrumentation);
        qdrantInstrumentation.manuallyInstrument(module);
        return qdrantInstrumentation;
      },
    },
    {
      name: "together",
      description: "Together AI instrumentation",
      moduleKey: "together",
      initFunction: async (module: any) => {
        const { TogetherInstrumentation } = await import(
          "@traceloop/instrumentation-together"
        );
        togetherInstrumentation = new TogetherInstrumentation({
          exceptionLogger,
        });
        instrumentations.push(togetherInstrumentation);
        togetherInstrumentation.manuallyInstrument(module);
        return togetherInstrumentation;
      },
    },
  ];

  // Keep track of processed module keys
  const processedModuleKeys = new Set<string>();

  // Process each pre-defined instrumentation
  for (const {
    name,
    description,
    moduleKey,
    initFunction,
  } of manualInstrumentationConfigs) {
    const module = instrumentModules[moduleKey as keyof typeof instrumentModules];
    processedModuleKeys.add(moduleKey);

    if (disabledInstrumentations.includes(name)) {
      loadingResults.push({ name, status: "disabled", description });
      console.debug(
        `[KeywordsAI Debug] Skipping ${description} (disabled by configuration)`
      );
      continue;
    }

    if (!module) {
      loadingResults.push({ name, status: "not-provided", description });
      console.debug(`[KeywordsAI Debug] No module provided for ${description}`);
      continue;
    }

    try {
      console.debug(
        `[KeywordsAI Debug] Attempting to manually initialize ${description}...`
      );
      await initFunction(module);
      loadingResults.push({ name, status: "success", description });
      console.debug(
        `[KeywordsAI Debug] Successfully initialized ${description}`
      );
    } catch (error) {
      loadingResults.push({ name, status: "failed", description, error });

      // Provide installation instructions for failed instrumentations (always show for manual instrumentation)
      const info = INSTRUMENTATION_INFO[name];
      if (info) {
        console.info(
          `[KeywordsAI] ${description} failed to initialize. Make sure you have the required package installed:\n   ${info.installCommand}`
        );
      }
      console.debug(
        `[KeywordsAI Debug] Failed to initialize ${description}:`,
        error
      );
    }
  }

  // Process any additional modules not in our pre-defined list
  for (const [moduleKey, module] of Object.entries(instrumentModules)) {
    if (processedModuleKeys.has(moduleKey) || !module) {
      continue; // Skip already processed or null modules
    }

    const customName = moduleKey; // Use the actual module key name
    const customDescription = `Custom ${moduleKey} instrumentation`;

    console.debug(
      `[KeywordsAI Debug] Found custom module: ${moduleKey}, attempting generic instrumentation...`
    );

    try {
      // Generic approach: try to call manuallyInstrument if it exists
      if (typeof module.manuallyInstrument === "function") {
        console.debug(
          `[KeywordsAI Debug] Attempting generic manual instrumentation for ${customDescription}...`
        );
        module.manuallyInstrument(module);
        loadingResults.push({
          name: customName,
          status: "success",
          description: customDescription,
        });
        console.debug(
          `[KeywordsAI Debug] Successfully initialized ${customDescription}`
        );
      } else {
        // Check if it's a valid instrumentation instance (has required OpenTelemetry methods)
        if (
          typeof module.setTracerProvider === "function" &&
          typeof module.getConfig === "function"
        ) {
          console.debug(
            `[KeywordsAI Debug] Module ${moduleKey} appears to be an instrumentation instance, adding it...`
          );
          instrumentations.push(module);
          loadingResults.push({
            name: customName,
            status: "success",
            description: customDescription,
          });
          console.debug(
            `[KeywordsAI Debug] Successfully added ${customDescription} as instrumentation instance`
          );
        } else {
          // Not a valid instrumentation, skip it with a helpful message
          console.debug(
            `[KeywordsAI Debug] Module ${moduleKey} is not a valid OpenTelemetry instrumentation (missing required methods)`
          );
          loadingResults.push({
            name: customName,
            status: "failed",
            description: customDescription,
            error: "Not a valid instrumentation",
          });
          console.info(
            `[KeywordsAI] Custom module '${moduleKey}' is not a valid OpenTelemetry instrumentation. It should either have a manuallyInstrument() method or be an Instrumentation instance.`
          );
        }
      }
    } catch (error) {
      loadingResults.push({
        name: customName,
        status: "failed",
        description: customDescription,
        error,
      });
      console.info(
        `[KeywordsAI] Failed to initialize custom module '${moduleKey}'. Make sure it's a valid OpenTelemetry instrumentation.`
      );
      console.debug(
        `[KeywordsAI Debug] Failed to initialize ${customDescription}:`,
        error
      );
    }
  }

  // Print summary
  const successful = loadingResults.filter((r) => r.status === "success");
  const failed = loadingResults.filter((r) => r.status === "failed");
  const disabled = loadingResults.filter((r) => r.status === "disabled");
  const notProvided = loadingResults.filter((r) => r.status === "not-provided");

  console.info(
    `[KeywordsAI] Manual instrumentation complete: ${successful.length} initialized, ${failed.length} failed, ${disabled.length} disabled, ${notProvided.length} not provided`
  );

  if (successful.length > 0) {
    console.info(
      `[KeywordsAI] Successfully initialized: ${successful
        .map((r) => r.name)
        .join(", ")}`
    );
  }

  if (disabled.length > 0) {
    console.info(
      `[KeywordsAI] Disabled instrumentations: ${disabled
        .map((r) => r.name)
        .join(", ")}`
    );
  }

  if (failed.length > 0) {
    console.debug(
      `[KeywordsAI Debug] Failed to initialize: ${failed
        .map((r) => r.name)
        .join(", ")}`
    );
  }
};

/**
 * Add an instrumentation to the collection
 */
export const enableInstrumentation = async (name: string): Promise<void> => {
  const instrumentation = await loadInstrumentation(name);
  if (instrumentation) {
    instrumentations.push(instrumentation);
    console.log(`Enabled ${name} instrumentation`);
  }
}; 