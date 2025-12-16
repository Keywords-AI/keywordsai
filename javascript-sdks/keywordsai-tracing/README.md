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
- **Span Management**: Full control over spans with `getClient()` API
- **Multi-Processor Routing**: Route spans to multiple destinations
- **Span Buffering**: Manual control over span export timing
- **KeywordsAI Parameters**: Add customer identifiers and trace group identifiers

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
    
    // Advanced options
    resourceAttributes?: Record<string, string>;  // Custom resource attributes
    spanPostprocessCallback?: (span: any) => void;  // Span postprocessing callback
    
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

- `initialize()` - Manually initialize tracing (returns Promise)
- `isInitialized()` - Check if tracing has been initialized
- `enableInstrumentation(name: string)` - Enable a specific instrumentation (dynamic method)
- `enableInstrumentations(names: string[])` - Enable multiple instrumentations (dynamic method)
- `addProcessor(config: ProcessorConfig)` - Add a processor for routing spans
- `getClient()` - Get the client API for span management
- `getSpanBufferManager()` - Get the span buffer manager
- `shutdown()` - Flush and shutdown tracing

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
    processors?: string | string[];      // Optional: Route to specific processor(s)
}
```

## Advanced Features

### Span Management with getClient()

Get full control over your spans with the client API:

```typescript
import { KeywordsAITelemetry, getClient } from '@keywordsai/tracing';

const kai = new KeywordsAITelemetry({ apiKey: 'your-key' });
await kai.initialize();

await kai.withTask({ name: 'process_data' }, async () => {
    const client = getClient();
    
    // Get current trace and span IDs
    const traceId = client.getCurrentTraceId();
    const spanId = client.getCurrentSpanId();
    console.log(`Trace: ${traceId}, Span: ${spanId}`);
    
    // Update span with KeywordsAI parameters
    client.updateCurrentSpan({
        keywordsaiParams: {
            customerIdentifier: 'user-123',
            traceGroupIdentifier: 'data-pipeline',
            metadata: {
                version: '1.0',
                environment: 'production'
            }
        }
    });
    
    // Add events to track progress
    client.addEvent('validation_started', { records: 1000 });
    
    // Your processing logic here
    
    client.addEvent('validation_completed', { status: 'success' });
    
    // Record exceptions
    try {
        // risky operation
    } catch (error) {
        client.recordException(error as Error);
        throw error;
    }
});
```

**Available Client Methods:**
- `getCurrentTraceId()` - Get the current trace ID
- `getCurrentSpanId()` - Get the current span ID
- `updateCurrentSpan(options)` - Update span attributes, name, status, or KeywordsAI params
- `addEvent(name, attributes?)` - Add an event to the current span
- `recordException(exception)` - Record an exception on the current span
- `isRecording()` - Check if the span is recording
- `getTracer()` - Get the tracer for manual span creation
- `flush()` - Force flush all pending spans

### Multi-Processor Routing

Route spans to different destinations based on processor names:

```typescript
import { KeywordsAITelemetry } from '@keywordsai/tracing';

const kai = new KeywordsAITelemetry({ apiKey: 'your-key' });

// Add a debug processor (in addition to default KeywordsAI processor)
kai.addProcessor({
    exporter: new YourCustomExporter(),
    name: 'debug',
    filter: (span) => span.attributes['environment'] === 'development'
});

// Route specific spans to debug processor
await kai.withTask(
    { name: 'debug_task', processors: 'debug' },
    async () => {
        // This span goes to the debug processor
    }
);

// Route to multiple processors
await kai.withTask(
    { name: 'important_task', processors: ['debug', 'analytics'] },
    async () => {
        // This span goes to both processors
    }
);

// Default behavior - no processors attribute
await kai.withTask(
    { name: 'normal_task' },
    async () => {
        // This span goes to the default KeywordsAI processor
    }
);
```

**Processor Configuration:**
```typescript
interface ProcessorConfig {
    exporter: SpanExporter;              // The span exporter to use
    name: string;                        // Processor identifier for routing
    filter?: (span: ReadableSpan) => boolean;  // Optional custom filter
    priority?: number;                   // Optional priority (higher = processed first)
}
```

### Span Buffering for Manual Control

Buffer spans and control when they're exported:

```typescript
import { KeywordsAITelemetry } from '@keywordsai/tracing';

const kai = new KeywordsAITelemetry({ apiKey: 'your-key' });
const manager = kai.getSpanBufferManager();

// Create a buffer (spans won't be auto-exported)
const buffer = manager.createBuffer('workflow-123');

// Add spans to the buffer
buffer.createSpan('validation', {
    status: 'success',
    duration_ms: 10
});

buffer.createSpan('processing', {
    status: 'success',
    duration_ms: 100
});

// Get buffered spans (they're transportable!)
const spans = buffer.getAllSpans();
console.log(`Collected ${spans.length} spans`);

// Conditionally process based on business logic
const isSuccessful = true;  // Your business logic
const isPremiumUser = true; // Your business logic

if (isSuccessful && isPremiumUser) {
    // Export to KeywordsAI
    await manager.processSpans(spans);
} else {
    // Discard spans
    buffer.clearSpans();
}
```

**Use Cases for Span Buffering:**
- Backend systems that need delayed span export
- Conditional export based on business logic
- Batch processing of spans
- Async span creation (create spans after execution)
- Experiment tracking with selective export

**SpanBuffer Methods:**
- `createSpan(name, attributes?, kind?)` - Create a span in the buffer
- `getAllSpans()` - Get all buffered spans as a transportable array
- `getSpanCount()` - Get the number of buffered spans
- `clearSpans()` - Discard all buffered spans without exporting

### KeywordsAI-Specific Parameters

Add customer and trace group identifiers to your spans:

```typescript
import { getClient } from '@keywordsai/tracing';

await kai.withWorkflow({ name: 'user_workflow' }, async () => {
    const client = getClient();
    
    client.updateCurrentSpan({
        keywordsaiParams: {
            // Group traces by customer
            customerIdentifier: 'user-123',
            
            // Organize traces into groups
            traceGroupIdentifier: 'onboarding-flow',
            
            // Add custom metadata
            metadata: {
                plan: 'premium',
                region: 'us-east-1',
                version: '2.1.0'
            }
        }
    });
});
```

These parameters help you:
- Group traces by customer for user-level analytics
- Organize traces into logical groups (experiments, features, etc.)
- Add custom metadata for filtering and analysis

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

## Complete Examples

### Example 1: Full Workflow with Span Management

```typescript
import { KeywordsAITelemetry, getClient } from '@keywordsai/tracing';
import OpenAI from 'openai';

const kai = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY,
    appName: 'my-app',
    resourceAttributes: {
        environment: 'production',
        version: '1.0.0'
    }
});

await kai.initialize();
const openai = new OpenAI();

await kai.withWorkflow({ name: 'process_user_request', version: 1 }, async () => {
    const client = getClient();
    
    // Set customer context
    client.updateCurrentSpan({
        keywordsaiParams: {
            customerIdentifier: 'user-123',
            traceGroupIdentifier: 'onboarding'
        }
    });
    
    // Track progress with events
    client.addEvent('validation_started');
    
    // Nested task
    await kai.withTask({ name: 'validate_input' }, async () => {
        // Validation logic
    });
    
    client.addEvent('ai_processing_started');
    
    // LLM call (auto-instrumented)
    const response = await openai.chat.completions.create({
        model: 'gpt-3.5-turbo',
        messages: [{ role: 'user', content: 'Process this' }]
    });
    
    client.addEvent('ai_processing_completed', {
        tokens: response.usage?.total_tokens
    });
    
    return response.choices[0].message.content;
});
```

### Example 2: Backend Workflow with Span Buffering

```typescript
import { KeywordsAITelemetry } from '@keywordsai/tracing';

const kai = new KeywordsAITelemetry({ apiKey: 'your-key' });
const manager = kai.getSpanBufferManager();

// Ingest workflow results from backend
async function ingestWorkflow(workflowResult: any, orgId: string) {
    const buffer = manager.createBuffer(`workflow-${workflowResult.id}`);
    
    // Create spans from workflow results
    buffer.createSpan('workflow_execution', {
        organization_id: orgId,
        input: workflowResult.input,
        output: workflowResult.output,
        duration_ms: workflowResult.duration
    });
    
    for (const step of workflowResult.steps) {
        buffer.createSpan(`step_${step.name}`, {
            input: step.input,
            output: step.output,
            duration_ms: step.duration
        });
    }
    
    // Get transportable spans
    const spans = buffer.getAllSpans();
    
    // Conditionally export based on business logic
    const isPremium = orgId.includes('premium');
    
    if (isPremium) {
        await manager.processSpans(spans);
        console.log('Exported spans for premium org');
    } else {
        buffer.clearSpans();
        console.log('Skipped spans for free org');
    }
}
```

### Example 3: Multi-Destination Routing

```typescript
import { KeywordsAITelemetry } from '@keywordsai/tracing';
import { FileExporter, AnalyticsExporter } from './exporters';

const kai = new KeywordsAITelemetry({ apiKey: 'your-key' });

// Add debug file exporter
kai.addProcessor({
    exporter: new FileExporter('./debug-spans.jsonl'),
    name: 'debug'
});

// Add analytics exporter with filter
kai.addProcessor({
    exporter: new AnalyticsExporter(),
    name: 'analytics',
    filter: (span) => !span.name.includes('test')
});

// Route to default KeywordsAI processor
await kai.withTask(
    { name: 'production_task' },
    async () => { /* goes to KeywordsAI */ }
);

// Route to debug processor
await kai.withTask(
    { name: 'debug_task', processors: 'debug' },
    async () => { /* goes to file */ }
);

// Route to multiple processors
await kai.withTask(
    { name: 'important_task', processors: ['debug', 'analytics'] },
    async () => { /* goes to file + analytics */ }
);
```

## Browser Compatibility

The core package is designed to work in both Node.js and browser environments. However, some instrumentations may be Node.js only.

## Testing Builds

Before publishing, test the built package:

```bash
npm run test:build
```

This builds, packs, installs, and tests the package exactly as users will receive it.

## Examples Directory

Check out the `examples/` directory for more comprehensive examples:
- `span-management-example.ts` - Full span management with getClient()
- `multi-processor-example.ts` - Multi-processor routing examples
- `span-buffer-example.ts` - Span buffering patterns
- `basic-usage.ts` - Basic usage patterns
- `advanced-tracing-example.ts` - Advanced tracing patterns

## Migration from v1.0.x

All new features are **backward compatible**. Existing code will continue to work without modifications:

- Default processor is automatically configured
- New methods are additive (optional)
- No breaking changes to existing APIs

To use new features, simply import and use them:
```typescript
import { getClient } from '@keywordsai/tracing';  // New in v1.1.0
```

## License

Apache-2.0

