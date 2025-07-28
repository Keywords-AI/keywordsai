import { InstrumentationName } from "./clientTypes.js";

export interface InstrumentationInfo {
  packageName: string;
  importPackage: string;
  description: string;
  installCommand: string;
}

export interface InstrumentationLoadResult {
  name: string;
  status: "success" | "failed" | "disabled" | "not-provided";
  description: string;
  error?: any;
}

export interface InstrumentationConfig {
  name: InstrumentationName;
  description: string;
  loadFunction: () => Promise<any>;
}

export interface ManualInstrumentationConfig {
  name: InstrumentationName;
  description: string;
  moduleKey: string;
  initFunction: (module: any) => Promise<any>;
}

// Instrumentation metadata for installation hints
export const INSTRUMENTATION_INFO: Record<string, InstrumentationInfo> = {
  openAI: {
    packageName: "@traceloop/instrumentation-openai",
    importPackage: "@traceloop/instrumentation-openai",
    description: "OpenAI API instrumentation",
    installCommand: "npm install @traceloop/instrumentation-openai",
  },
  anthropic: {
    packageName: "@traceloop/instrumentation-anthropic",
    importPackage: "@traceloop/instrumentation-anthropic",
    description: "Anthropic API instrumentation",
    installCommand: "npm install @traceloop/instrumentation-anthropic",
  },
  azureOpenAI: {
    packageName: "@traceloop/instrumentation-azure",
    importPackage: "@traceloop/instrumentation-azure",
    description: "Azure OpenAI instrumentation",
    installCommand: "npm install @traceloop/instrumentation-azure",
  },
  bedrock: {
    packageName: "@traceloop/instrumentation-bedrock",
    importPackage: "@traceloop/instrumentation-bedrock",
    description: "AWS Bedrock instrumentation",
    installCommand: "npm install @traceloop/instrumentation-bedrock",
  },
  cohere: {
    packageName: "@traceloop/instrumentation-cohere",
    importPackage: "@traceloop/instrumentation-cohere",
    description: "Cohere API instrumentation",
    installCommand: "npm install @traceloop/instrumentation-cohere",
  },
  langChain: {
    packageName: "@traceloop/instrumentation-langchain",
    importPackage: "@traceloop/instrumentation-langchain",
    description: "LangChain framework instrumentation",
    installCommand: "npm install @traceloop/instrumentation-langchain",
  },
  llamaIndex: {
    packageName: "@traceloop/instrumentation-llamaindex",
    importPackage: "@traceloop/instrumentation-llamaindex",
    description: "LlamaIndex framework instrumentation",
    installCommand: "npm install @traceloop/instrumentation-llamaindex",
  },
  pinecone: {
    packageName: "@traceloop/instrumentation-pinecone",
    importPackage: "@traceloop/instrumentation-pinecone",
    description: "Pinecone vector database instrumentation",
    installCommand: "npm install @traceloop/instrumentation-pinecone",
  },
  chromaDB: {
    packageName: "@traceloop/instrumentation-chromadb",
    importPackage: "@traceloop/instrumentation-chromadb",
    description: "ChromaDB vector database instrumentation",
    installCommand: "npm install @traceloop/instrumentation-chromadb",
  },
  qdrant: {
    packageName: "@traceloop/instrumentation-qdrant",
    importPackage: "@traceloop/instrumentation-qdrant",
    description: "Qdrant vector database instrumentation",
    installCommand: "npm install @traceloop/instrumentation-qdrant",
  },
  together: {
    packageName: "@traceloop/instrumentation-together",
    importPackage: "@traceloop/instrumentation-together",
    description: "Together AI instrumentation",
    installCommand: "npm install @traceloop/instrumentation-together",
  },
  googleVertexAI: {
    packageName: "@traceloop/instrumentation-vertexai",
    importPackage: "@traceloop/instrumentation-vertexai",
    description: "Google Vertex AI instrumentation",
    installCommand: "npm install @traceloop/instrumentation-vertexai",
  },
  googleAIPlatform: {
    packageName: "@traceloop/instrumentation-vertexai",
    importPackage: "@traceloop/instrumentation-vertexai",
    description: "Google AI Platform instrumentation",
    installCommand: "npm install @traceloop/instrumentation-vertexai",
  },
}; 