import { withTask, withWorkflow, withAgent, withTool } from "./decorators";
import { WithFunctionType } from "./types/decoratorTypes";
import { KeywordsAIOptions } from "./types/clientTypes";
import { withKeywordsAISpanAttributes } from "./contexts/span";
import { startTracing, enableInstrumentation, forceFlush } from "./utils/tracing";

export class KeywordsAITelemetry {
    private options: KeywordsAIOptions;
    private initialized: boolean = false;
    private initializing: boolean = false;

    constructor(options: KeywordsAIOptions) {
        this.options = {
            appName: options.appName || process.env.KEYWORDS_AI_APP_NAME || "default",
            disableBatch: options.disableBatch || false,
            baseUrl: options.baseUrl || process.env.KEYWORDS_AI_BASE_URL || "https://api.keywordsai.co",
            apiKey: options.apiKey || process.env.KEYWORDS_AI_API_KEY || "",
            instrumentModules: options.instrumentModules || {},
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
