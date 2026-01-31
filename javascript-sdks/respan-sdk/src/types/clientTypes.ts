


/**
 * Options for initializing the Respan SDK.
 */
export interface RespanOptions {
    /**
     * The app name to be used when reporting traces.
     */
    appName?: string;

    /**
     * Sends traces and spans without batching, for local development.
     * Defaults to false.
     */
    disableBatch?: boolean;

    /**
     * The API endpoint for sending data.
     */
    baseUrl?: string;

    /**
     * The API Key for authentication.
     */
    apiKey: string;

    /**
     * Explicitly specify modules to instrument.
     */
    instrumentModules?: {
        openAI?: any;
        anthropic?: any;
        azureOpenAI?: any;
        cohere?: any;
        bedrock?: any;
        google_vertexai?: any;
        google_aiplatform?: any;
        pinecone?: any;
        langchain?: {
            chainsModule?: any;
            agentsModule?: any;
            toolsModule?: any;
            runnablesModule?: any;
            vectorStoreModule?: any;
        };
        llamaIndex?: any;
        chromadb?: any;
        qdrant?: any;
    };
}

/**
 * The main client options for Respan.
 */
export interface RespanClientOptions {
    apiKey: string;
    appName: string;
    baseUrl?: string;
}

/**
 * Base class for all Respan errors.
 */
export class RespanError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'RespanError';
    }
}

export class InitializationError extends RespanError {
    constructor(message?: string) {
        super(message || 'Failed to initialize Respan');
        this.name = 'InitializationError';
    }
}

export class NotInitializedError extends RespanError {
    constructor() {
        super('Respan has not been initialized');
        this.name = 'NotInitializedError';
    }
}
