import { withTask, withWorkflow, withAgent, withTool } from "./decorators/index.js";
import { WithFunctionType } from "./types/decoratorTypes.js";
import { KeywordsAIOptions } from "./types/clientTypes.js";
import { withKeywordsAISpanAttributes } from "./contexts/span.js";
import { startTracing, enableInstrumentation, forceFlush } from "./utils/tracing.js";

/**
 * KeywordsAI client for trace management and instrumentation.
 * This class provides an interface for initializing and managing OpenTelemetry-based tracing
 * for various AI/ML services and frameworks.
 * 
 * ## Instrumentation Management
 * 
 * ### Automatic Discovery (Default)
 * By default, KeywordsAI will attempt to load all available instrumentations automatically:
 * ```typescript
 * const keywordsAI = new KeywordsAITelemetry({
 *   apiKey: 'your-api-key',
 *   logLevel: 'info' // Shows what gets loaded successfully
 * });
 * ```
 * 
 * ### Manual Instrumentation (Next.js/Webpack environments)
 * For environments where dynamic imports don't work properly:
 * ```typescript
 * import OpenAI from 'openai';
 * import Anthropic from '@anthropic-ai/sdk';
 * 
 * const keywordsAI = new KeywordsAITelemetry({
 *   apiKey: 'your-api-key',
 *   instrumentModules: {
 *     openAI: OpenAI,
 *     anthropic: Anthropic
 *   }
 * });
 * ```
 * 
 * ### Disable Specific Instrumentations
 * Block instrumentations you don't want to use:
 * ```typescript
 * const keywordsAI = new KeywordsAITelemetry({
 *   apiKey: 'your-api-key',
 *   disabledInstrumentations: ['bedrock', 'chromaDB', 'qdrant']
 * });
 * ```
 * 
 * ### Available Instrumentations (consistent camelCase naming)
 * - `openAI` - OpenAI API instrumentation
 * - `anthropic` - Anthropic API instrumentation  
 * - `azureOpenAI` - Azure OpenAI instrumentation
 * - `cohere` - Cohere API instrumentation
 * - `bedrock` - AWS Bedrock instrumentation
 * - `googleVertexAI` - Google Vertex AI instrumentation
 * - `googleAIPlatform` - Google AI Platform instrumentation
 * - `pinecone` - Pinecone vector database instrumentation
 * - `together` - Together AI instrumentation
 * - `langChain` - LangChain framework instrumentation
 * - `llamaIndex` - LlamaIndex framework instrumentation
 * - `chromaDB` - ChromaDB vector database instrumentation
 * - `qdrant` - Qdrant vector database instrumentation
 * 
 * ### Debugging Instrumentation Loading
 * Set `logLevel: 'info'` or `logLevel: 'debug'` to see:
 * - Which instrumentations loaded successfully
 * - Which ones failed and installation instructions
 * - Which ones were disabled by configuration
 */
export class KeywordsAITelemetry {
    private options: KeywordsAIOptions;
    private initialized: boolean = false;
    private initializing: boolean = false;

    constructor(options: KeywordsAIOptions) {
        this.options = {
            appName: options.appName || process.env.KEYWORDSAI_APP_NAME || "default",
            disableBatch: options.disableBatch || false,
            baseUrl: options.baseUrl || process.env.KEYWORDSAI_BASE_URL || "https://api.keywordsai.co",
            apiKey: options.apiKey || process.env.KEYWORDSAI_API_KEY || "",
            instrumentModules: options.instrumentModules || {},
            disabledInstrumentations: options.disabledInstrumentations || [],
            tracingEnabled: options.tracingEnabled !== false,
            traceContent: options.traceContent !== false,
            logLevel: options.logLevel || "error",
            silenceInitializationMessage: options.silenceInitializationMessage || false,
        };
        
        // Don't auto-initialize - let user call initialize() explicitly
        // This prevents timing issues and double initialization
    }

    private async _initialize() {
        if (this.initialized || this.initializing) {
            return;
        }
        
        this.initializing = true;
        try {
            await startTracing(this.options);
            this.initialized = true;
        } catch (error) {
            console.error("Failed to initialize KeywordsAI tracing:", error);
        } finally {
            this.initializing = false;
        }
    }

    /**
     * Manually initialize tracing. This is useful if you want to ensure
     * tracing is fully initialized before proceeding.
     */
    public async initialize(): Promise<void> {
        await this._initialize();
    }

    /**
     * Check if tracing has been initialized
     */
    public isInitialized(): boolean {
        return this.initialized;
    }

    public withTask: WithFunctionType = withTask;

    public withWorkflow: WithFunctionType = withWorkflow;

    public withAgent: WithFunctionType = withAgent;

    public withTool: WithFunctionType = withTool;

    public withKeywordsAISpanAttributes = withKeywordsAISpanAttributes;

    /**
     * Enable instrumentation for a specific provider
     * @param name - The name of the instrumentation (e.g., 'openai', 'anthropic')
     */
    public async enableInstrumentation(name: string): Promise<void> {
        await enableInstrumentation(name);
    }

    /**
     * Enable multiple instrumentations
     * @param names - Array of instrumentation names
     */
    public async enableInstrumentations(names: string[]): Promise<void> {
        await Promise.all(names.map(name => enableInstrumentation(name)));
    }

    /**
     * Flush and shutdown tracing
     */
    public async shutdown(): Promise<void> {
        await forceFlush();
    }
}
