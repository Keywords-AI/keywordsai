


/**
 * Options for initializing the KeywordsAI SDK.
 */
export interface KeywordsAIOptions {
    /**
     * The app name to be used when reporting traces.
     */
    appName: string;

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
