import { LogType, KeywordsLogType } from "@keywordsai/keywordsai-sdk";

// Mapping from AI SDK span types to KeywordsAI log types
export const AISDK_SPAN_TO_KEYWORDS_LOG_TYPE: Record<string, LogType> = {
  // Text generation spans
  "ai.generateText": KeywordsLogType.TEXT,
  "ai.generateText.doGenerate": KeywordsLogType.GENERATION,
  "ai.streamText": KeywordsLogType.TEXT,
  "ai.streamText.doStream": KeywordsLogType.GENERATION,

  // Object generation spans
  "ai.generateObject": KeywordsLogType.TEXT,
  "ai.generateObject.doGenerate": KeywordsLogType.GENERATION,
  "ai.streamObject": KeywordsLogType.TEXT,
  "ai.streamObject.doStream": KeywordsLogType.GENERATION,

  // Embedding spans
  "ai.embed": KeywordsLogType.EMBEDDING,
  "ai.embed.doEmbed": KeywordsLogType.EMBEDDING,
  "ai.embedMany": KeywordsLogType.EMBEDDING,
  "ai.embedMany.doEmbed": KeywordsLogType.EMBEDDING,

  // Tool call spans
  "ai.toolCall": KeywordsLogType.TOOL,

  // Stream events
  "ai.stream.firstChunk": KeywordsLogType.GENERATION,

  // Chat spans
  "ai.chat": "chat",

  // Agents and workflows
  "ai.agent": KeywordsLogType.AGENT,
  "ai.workflow": KeywordsLogType.WORKFLOW,
  "ai.agent.run": KeywordsLogType.AGENT,
  "ai.agent.step": KeywordsLogType.TASK,

  // Functions and handoffs
  "ai.function": KeywordsLogType.FUNCTION,
  "ai.handoff": KeywordsLogType.HANDOFF,

  // Other spans that might appear
  "ai.transcript": KeywordsLogType.TRANSCRIPTION,
  "ai.speech": KeywordsLogType.SPEECH,
  "ai.response": KeywordsLogType.RESPONSE,

  // Default to UNKNOWN for unrecognized spans
  default: KeywordsLogType.UNKNOWN,
};
