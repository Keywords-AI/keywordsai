import { SpanExporter, SpanProcessor } from "@opentelemetry/sdk-trace-base";
import { TextMapPropagator, ContextManager } from "@opentelemetry/api";

/**
 * Available instrumentation names for consistent camelCase naming.
 * Abbreviations like AI, API, DB are kept uppercase.
 */
export type InstrumentationName = 
    | 'http'
    | 'openAI'
    | 'anthropic'
    | 'azureOpenAI'
    | 'cohere'
    | 'bedrock'
    | 'googleVertexAI'
    | 'googleAIPlatform'
    | 'pinecone'
    | 'together'
    | 'langChain'
    | 'llamaIndex'
    | 'chromaDB'
    | 'qdrant';

/**
 * Options for initializing the KeywordsAI SDK.
 */
export interface KeywordsAIOptions {
    /**
     * The app name to be used when reporting traces. Optional.
     * Defaults to the package name.
     */
    appName?: string;

    /**
     * The API Key for sending traces data. Optional.
     * Defaults to the KEYWORDSAI_API_KEY environment variable.
     */
    apiKey?: string;

    /**
     * The OTLP endpoint for sending traces data. Optional.
     * Defaults to KEYWORDSAI_BASE_URL environment variable or https://api.keywordsai.co/
     */
    baseUrl?: string;

    /**
     * Sends traces and spans without batching, for local development. Optional.
     * Defaults to false.
     */
    disableBatch?: boolean;

    /**
     * Defines default log level for SDK and all instrumentations. Optional.
     * Defaults to error.
     */
    logLevel?: "debug" | "info" | "warn" | "error";

    /**
     * Whether to log prompts, completions and embeddings on traces. Optional.
     * Defaults to true.
     */
    traceContent?: boolean;

    /**
     * The OpenTelemetry SpanExporter to be used for sending traces data. Optional.
     * Defaults to the OTLP exporter.
     */
    exporter?: SpanExporter;

    /**
     * The headers to be sent with the traces data. Optional.
     */
    headers?: Record<string, string>;

    /**
     * The OpenTelemetry SpanProcessor to be used for processing traces data. Optional.
     * Defaults to the BatchSpanProcessor.
     */
    processor?: SpanProcessor;

    /**
     * The OpenTelemetry Propagator to use. Optional.
     * Defaults to OpenTelemetry SDK defaults.
     */
    propagator?: TextMapPropagator;

    /**
     * The OpenTelemetry ContextManager to use. Optional.
     * Defaults to OpenTelemetry SDK defaults.
     */
    contextManager?: ContextManager;

    /**
     * Whether to silence the initialization message. Optional.
     * Defaults to false.
     */
    silenceInitializationMessage?: boolean;

    /**
     * Whether to enable tracing. Optional.
     * Defaults to true.
     */
    tracingEnabled?: boolean;

    /**
     * Explicitly specify modules to instrument. Optional.
     * This is a workaround specific to Next.js and other environments where
     * dynamic imports might not work properly.
     * 
     * Usage example:
     * ```typescript
     * import OpenAI from 'openai';
     * import Anthropic from '@anthropic-ai/sdk';
     * 
     * const keywordsAI = new KeywordsAITelemetry({
     *   instrumentModules: {
     *     openAI: OpenAI,
     *     anthropic: Anthropic,
     *   }
     * });
     * ```
     */
    instrumentModules?: {
        openAI?: any; // typeof import('openai').OpenAI
        anthropic?: any; // typeof import('@anthropic-ai/sdk')
        azureOpenAI?: any; // typeof import('@azure/openai')
        cohere?: any; // typeof import('cohere-ai')
        bedrock?: any; // typeof import('@aws-sdk/client-bedrock-runtime')
        googleVertexAI?: any; // typeof import('@google-cloud/vertexai')
        googleAIPlatform?: any; // typeof import('@google-cloud/aiplatform')
        pinecone?: any; // typeof import('@pinecone-database/pinecone')
        together?: any; // typeof import('together-ai').Together
        langChain?: {
            chainsModule?: any; // typeof import('langchain/chains')
            agentsModule?: any; // typeof import('langchain/agents')
            toolsModule?: any; // typeof import('langchain/tools')
            runnablesModule?: any; // typeof import('@langchain/core/runnables')
            vectorStoreModule?: any; // typeof import('@langchain/core/vectorstores')
        };
        llamaIndex?: any; // typeof import('llamaindex')
        chromaDB?: any; // typeof import('chromadb')
        qdrant?: any; // typeof import('@qdrant/js-client-rest')
    };

    /**
     * List of instrumentation modules to disable. Optional.
     * Useful for preventing certain instrumentations from being loaded.
     * Uses consistent camelCase naming with abbreviations kept uppercase.
     * 
     * Usage example:
     * ```typescript
     * const keywordsAI = new KeywordsAITelemetry({
     *   disabledInstrumentations: ['bedrock', 'chromaDB', 'qdrant']
     * });
     * ```
     */
    disabledInstrumentations?: InstrumentationName[];
}

/**
 * The main client options for KeywordsAI.
 */
export interface KeywordsAIClientOptions {
    apiKey: string;
    appName: string;
    baseUrl?: string;
}

/**
 * Base class for all KeywordsAI errors.
 */
export class KeywordsAIError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'KeywordsAIError';
    }
}

export class InitializationError extends KeywordsAIError {
    constructor(message?: string) {
        super(message || 'Failed to initialize KeywordsAI');
        this.name = 'InitializationError';
    }
}

export class NotInitializedError extends KeywordsAIError {
    constructor() {
        super('KeywordsAI has not been initialized');
        this.name = 'NotInitializedError';
    }
}
