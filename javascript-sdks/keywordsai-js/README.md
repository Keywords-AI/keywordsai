# KeywordsAI Tracing SDK

A lightweight OpenTelemetry-based tracing SDK for KeywordsAI, built with minimal dependencies and optional instrumentation support.
Inspired by [Openllmetry](https://github.com/traceloop/openllmetry-js)

## Features

- **Lightweight Core**: Minimal dependencies for browser and Node.js compatibility
- **Optional Instrumentations**: Install only the instrumentations you need
- **OpenTelemetry Native**: Built directly on OpenTelemetry without wrapper dependencies
- **Decorator Pattern**: Easy-to-use decorators for workflows, tasks, agents, and tools
- **Dynamic Loading**: Instrumentations are loaded on-demand
- **Manual Instrumentation**: Support for manual instrumentation (Next.js compatible)

## Installation

### Core Package
```bash
npm install @keywordsai/tracing
```

### Optional Instrumentations
Install only the instrumentations you need:

```bash
# OpenAI
npm install @traceloop/instrumentation-openai

# Anthropic
npm install @traceloop/instrumentation-anthropic

# Azure OpenAI
npm install @traceloop/instrumentation-azure

# AWS Bedrock
npm install @traceloop/instrumentation-bedrock

# Cohere
npm install @traceloop/instrumentation-cohere

# LangChain
npm install @traceloop/instrumentation-langchain

# LlamaIndex
npm install @traceloop/instrumentation-llamaindex

# Vector Databases
npm install @traceloop/instrumentation-pinecone
npm install @traceloop/instrumentation-chromadb
npm install @traceloop/instrumentation-qdrant

# Other providers
npm install @traceloop/instrumentation-together
npm install @traceloop/instrumentation-vertexai
```

## Quick Start

### Method 1: Dynamic Instrumentation (Recommended for Node.js)

```typescript
import { KeywordsAITelemetry } from '@keywordsai/tracing';
import OpenAI from 'openai';

// Initialize the SDK
const keywordsAi = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY,
    baseURL: process.env.KEYWORDSAI_BASE_URL,
    appName: 'my-app'
});

// Enable instrumentations you need
await keywordsAi.enableInstrumentation('openai');

const openai = new OpenAI();

// Use decorators to trace your functions
const generateJoke = async () => {
    return await keywordsAi.withTask(
        { name: 'joke_generation' },
        async () => {
            const completion = await openai.chat.completions.create({
                messages: [{ role: 'user', content: 'Tell me a joke' }],
                model: 'gpt-3.5-turbo'
            });
            return completion.choices[0].message.content;
        }
    );
};
```

### Method 2: Manual Instrumentation (Recommended for Next.js)

```typescript
import { KeywordsAITelemetry } from '@keywordsai/tracing';
import OpenAI from 'openai';
import Anthropic from '@anthropic-ai/sdk';

// Manual instrumentation - pass the actual imported modules
const keywordsAi = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY,
    baseURL: process.env.KEYWORDSAI_BASE_URL,
    appName: 'my-app',
    // Specify modules to instrument manually
    instrumentModules: {
        openAI: OpenAI,
        anthropic: Anthropic,
        // Add other modules as needed
    }
});

// Wait for initialization (optional but recommended)
await keywordsAi.initialize();

// Create clients - they will be automatically instrumented
const openai = new OpenAI();
const anthropic = new Anthropic();

// Use decorators to trace your functions
const generateContent = async () => {
    return await keywordsAi.withWorkflow(
        { name: 'content_generation', version: 1 },
        async () => {
            const result = await openai.chat.completions.create({
                messages: [{ role: 'user', content: 'Generate content' }],
                model: 'gpt-3.5-turbo'
            });
            return result.choices[0].message.content;
        }
    );
};
```

## When to Use Each Method

### Dynamic Instrumentation
- **Best for**: Standard Node.js applications, serverless functions
- **Pros**: Simple setup, automatic loading
- **Cons**: May not work in all bundling environments

### Manual Instrumentation  
- **Best for**: Next.js, Webpack bundled apps, environments with import restrictions
- **Pros**: Works in all environments, explicit control, better for tree-shaking
- **Cons**: Requires importing modules explicitly

## API Reference

### KeywordsAITelemetry

#### Constructor Options

```typescript
interface KeywordsAIOptions {
    appName?: string;                    // App name for traces
    apiKey?: string;                     // KeywordsAI API key
    baseURL?: string;                    // KeywordsAI base URL
    disableBatch?: boolean;              // Disable batching for development
    logLevel?: "debug" | "info" | "warn" | "error";
    traceContent?: boolean;              // Log prompts and completions
    tracingEnabled?: boolean;            // Enable/disable tracing
    silenceInitializationMessage?: boolean;
    
    // Manual instrumentation modules
    instrumentModules?: {
        openAI?: typeof OpenAI;
        anthropic?: typeof Anthropic;
        azureOpenAI?: typeof AzureOpenAI;
        cohere?: typeof Cohere;
        bedrock?: typeof BedrockRuntime;
        google_vertexai?: typeof VertexAI;
        google_aiplatform?: typeof AIPlatform;
        pinecone?: typeof Pinecone;
        together?: typeof Together;
        langchain?: {
            chainsModule?: typeof ChainsModule;
            agentsModule?: typeof AgentsModule;
            toolsModule?: typeof ToolsModule;
            runnablesModule?: typeof RunnableModule;
            vectorStoreModule?: typeof VectorStoreModule;
        };
        llamaIndex?: typeof LlamaIndex;
        chromadb?: typeof ChromaDB;
        qdrant?: typeof Qdrant;
    };
}
```

#### Methods

- `initialize()`: Manually initialize tracing (returns Promise)
- `isInitialized()`: Check if tracing has been initialized
- `enableInstrumentation(name: string)`: Enable a specific instrumentation (dynamic method)
- `enableInstrumentations(names: string[])`: Enable multiple instrumentations (dynamic method)
- `shutdown()`: Flush and shutdown tracing

### Decorators

#### withWorkflow
Trace high-level workflows:
```typescript
await keywordsAi.withWorkflow(
    { name: 'my_workflow', version: 1 },
    async () => {
        // Your workflow logic
    }
);
```

#### withTask
Trace individual tasks:
```typescript
await keywordsAi.withTask(
    { name: 'my_task' },
    async () => {
        // Your task logic
    }
);
```

#### withAgent
Trace agent operations:
```typescript
await keywordsAi.withAgent(
    { name: 'my_agent', associationProperties: { type: 'assistant' } },
    async () => {
        // Your agent logic
    }
);
```

#### withTool
Trace tool usage:
```typescript
await keywordsAi.withTool(
    { name: 'my_tool' },
    async () => {
        // Your tool logic
    }
);
```

### Decorator Configuration

```typescript
interface DecoratorConfig {
    name: string;                        // Required: Name of the operation
    version?: number;                    // Optional: Version number
    associationProperties?: Record<string, string>; // Optional: Additional metadata
    traceContent?: boolean;              // Optional: Override trace content setting
    inputParameters?: unknown[];         // Optional: Custom input parameters
    suppressTracing?: boolean;           // Optional: Suppress tracing for this operation
}
```

## Available Instrumentations

The following instrumentations can be enabled dynamically:

- `openai` - OpenAI API calls
- `anthropic` - Anthropic API calls
- `azure` - Azure OpenAI API calls
- `bedrock` - AWS Bedrock API calls
- `cohere` - Cohere API calls
- `langchain` - LangChain operations
- `llamaindex` - LlamaIndex operations
- `pinecone` - Pinecone vector database
- `chromadb` - ChromaDB vector database
- `qdrant` - Qdrant vector database
- `together` - Together AI API calls
- `vertexai` - Google Vertex AI API calls

## Environment Variables

- `KEYWORDSAI_API_KEY`: Your KeywordsAI API key
- `KEYWORDSAI_BASE_URL`: KeywordsAI base URL (default: https://api.keywordsai.co)
- `KEYWORDSAI_APP_NAME`: Default app name
- `KEYWORDSAI_TRACE_CONTENT`: Enable/disable content tracing (default: true)

## Browser Compatibility

The core package is designed to work in both Node.js and browser environments. However, some instrumentations may be Node.js only.

## License

Apache-2.0

