import { Instrumentation } from "@opentelemetry/instrumentation";
import { INSTRUMENTATION_INFO } from "../types/index.js";

/**
 * Dynamic instrumentation loading with enhanced logging and installation hints
 */
export const loadInstrumentation = async (
  name: string
): Promise<Instrumentation | null> => {
  console.debug(
    `[KeywordsAI Debug] Attempting to load instrumentation: ${name}`
  );

  const info = INSTRUMENTATION_INFO[name];
  if (!info) {
    console.warn(`[KeywordsAI] Unknown instrumentation: ${name}`);
    return null;
  }

  try {
    console.debug(`[KeywordsAI Debug] Loading ${info.description}...`);

    switch (name) {
      case "openAI":
        const { OpenAIInstrumentation } = await import(
          "@traceloop/instrumentation-openai"
        );
        console.debug(
          `[KeywordsAI Debug] Successfully imported ${info.description}`
        );
        return new OpenAIInstrumentation({
          enrichTokens: true,
          exceptionLogger: (e: Error) =>
            console.error("OpenAI instrumentation error:", e),
        });

      case "anthropic":
        const { AnthropicInstrumentation } = await import(
          "@traceloop/instrumentation-anthropic"
        );
        console.debug(
          `[KeywordsAI Debug] Successfully imported ${info.description}`
        );
        return new AnthropicInstrumentation({
          exceptionLogger: (e: Error) =>
            console.error("Anthropic instrumentation error:", e),
        });

      case "azureOpenAI":
        const { AzureOpenAIInstrumentation } = await import(
          "@traceloop/instrumentation-azure"
        );
        console.debug(
          `[KeywordsAI Debug] Successfully imported ${info.description}`
        );
        return new AzureOpenAIInstrumentation({
          exceptionLogger: (e: Error) =>
            console.error("Azure instrumentation error:", e),
        });

      case "bedrock":
        const { BedrockInstrumentation } = await import(
          "@traceloop/instrumentation-bedrock"
        );
        console.debug(
          `[KeywordsAI Debug] Successfully imported ${info.description}`
        );
        return new BedrockInstrumentation({
          exceptionLogger: (e: Error) =>
            console.error("Bedrock instrumentation error:", e),
        });

      case "cohere":
        const { CohereInstrumentation } = await import(
          "@traceloop/instrumentation-cohere"
        );
        console.debug(
          `[KeywordsAI Debug] Successfully imported ${info.description}`
        );
        return new CohereInstrumentation({
          exceptionLogger: (e: Error) =>
            console.error("Cohere instrumentation error:", e),
        });

      case "langChain":
        const { LangChainInstrumentation } = await import(
          "@traceloop/instrumentation-langchain"
        );
        console.debug(
          `[KeywordsAI Debug] Successfully imported ${info.description}`
        );
        return new LangChainInstrumentation({
          exceptionLogger: (e: Error) =>
            console.error("LangChain instrumentation error:", e),
        });

      case "llamaIndex":
        const { LlamaIndexInstrumentation } = await import(
          "@traceloop/instrumentation-llamaindex"
        );
        console.debug(
          `[KeywordsAI Debug] Successfully imported ${info.description}`
        );
        return new LlamaIndexInstrumentation({
          exceptionLogger: (e: Error) =>
            console.error("LlamaIndex instrumentation error:", e),
        });

      case "pinecone":
        const { PineconeInstrumentation } = await import(
          "@traceloop/instrumentation-pinecone"
        );
        console.debug(
          `[KeywordsAI Debug] Successfully imported ${info.description}`
        );
        return new PineconeInstrumentation({
          exceptionLogger: (e: Error) =>
            console.error("Pinecone instrumentation error:", e),
        });

      case "chromaDB":
        const { ChromaDBInstrumentation } = await import(
          "@traceloop/instrumentation-chromadb"
        );
        console.debug(
          `[KeywordsAI Debug] Successfully imported ${info.description}`
        );
        return new ChromaDBInstrumentation({
          exceptionLogger: (e: Error) =>
            console.error("ChromaDB instrumentation error:", e),
        });

      case "qdrant":
        const { QdrantInstrumentation } = await import(
          "@traceloop/instrumentation-qdrant"
        );
        console.debug(
          `[KeywordsAI Debug] Successfully imported ${info.description}`
        );
        return new QdrantInstrumentation({
          exceptionLogger: (e: Error) =>
            console.error("Qdrant instrumentation error:", e),
        });

      case "together":
        const { TogetherInstrumentation } = await import(
          "@traceloop/instrumentation-together"
        );
        console.debug(
          `[KeywordsAI Debug] Successfully imported ${info.description}`
        );
        return new TogetherInstrumentation({
          exceptionLogger: (e: Error) =>
            console.error("Together instrumentation error:", e),
        });

      case "googleVertexAI":
        const { VertexAIInstrumentation } = await import(
          "@traceloop/instrumentation-vertexai"
        );
        console.debug(
          `[KeywordsAI Debug] Successfully imported ${info.description}`
        );
        return new VertexAIInstrumentation({
          exceptionLogger: (e: Error) =>
            console.error("VertexAI instrumentation error:", e),
        });

      case "googleAIPlatform":
        const { AIPlatformInstrumentation } = await import(
          "@traceloop/instrumentation-vertexai"
        );
        console.debug(
          `[KeywordsAI Debug] Successfully imported ${info.description}`
        );
        return new AIPlatformInstrumentation({
          exceptionLogger: (e: Error) =>
            console.error("AI Platform instrumentation error:", e),
        });

      default:
        console.warn(`[KeywordsAI] Unknown instrumentation: ${name}`);
        return null;
    }
  } catch (error) {
    console.info(
      `[KeywordsAI] ${info.description} is not available. To enable it, install the required package:\n   ${info.installCommand}`
    );
    console.debug(
      `[KeywordsAI Debug] Failed to load ${name} instrumentation:`,
      error
    );
    return null;
  }
}; 