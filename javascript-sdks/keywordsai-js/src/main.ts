import * as traceloop from "@traceloop/node-server-sdk";
import { DecoratorConfig } from "@traceloop/node-server-sdk";
import { OpenAI } from "openai";
import { withAgent, withTask, withWorkflow } from "src/decorators";
import { WithFunctionType } from "./types/decorator_types";

interface KeywordsAIOptions {
    appName: string;
    disableBatch?: boolean;
    baseUrl?: string;
    apiKey: string;
    // Add any other options you want to expose
    instrumentModules?: {
        openAI?: typeof OpenAI;
        // Add other modules as needed
    };
}

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

    public withAgent: WithFunctionType = (options, callback, ...args) => {
        return withAgent(options, callback, ...args);
    }

    public withTask: WithFunctionType = (options, callback, ...args) => {
        return withTask(options, callback, ...args);
    }

    public withWorkflow: WithFunctionType = (options, callback, ...args) => {
        return withWorkflow(options, callback, ...args);
    }

    // Add your methods here
}
