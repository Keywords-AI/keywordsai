import * as traceloop from "@traceloop/node-server-sdk";
import { withTask, withWorkflow } from "./decorators";
import { WithFunctionType } from "./types/decoratorTypes";
import { KeywordsAIOptions } from "./types/clientTypes";
import { withKeywordsAISpanAttributes } from "./contexts/span";
export class KeywordsAITelemetry {
    private options: KeywordsAIOptions;

    constructor(options: KeywordsAIOptions) {
        this.options = {
            appName: options.appName || process.env.KEYWORDS_AI_APP_NAME || "default",
            disableBatch: options.disableBatch || false,
            baseUrl: options.baseUrl || process.env.KEYWORDS_AI_BASE_URL || "http://api.keywordsai.co",
            apiKey: options.apiKey || process.env.KEYWORDS_AI_API_KEY || "",
            instrumentModules: options.instrumentModules || {}
        };
        // Initialize traceloop with your options
        this._initialize(options);
    
    }

    private _initialize(
        {
            appName,
            disableBatch,
            baseUrl,
            apiKey,
            instrumentModules
        }: KeywordsAIOptions
    ) {
        traceloop.initialize({
            appName: appName || this.options.appName,
            disableBatch: disableBatch || this.options.disableBatch,
            baseUrl: baseUrl || this.options.baseUrl,
            apiKey: apiKey || this.options.apiKey,
            instrumentModules: instrumentModules || this.options.instrumentModules
        }) as traceloop.TraceloopClient;
    }

    public withTask: WithFunctionType = withTask;

    public withWorkflow: WithFunctionType = withWorkflow;

    public withKeywordsAISpanAttributes = withKeywordsAISpanAttributes;


    // Add your methods here
}
