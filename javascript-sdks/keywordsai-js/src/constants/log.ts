// Mapping from Vercel AI SDK span types to KeywordsAI log types
// Define KeywordsAI log type enum
export enum KeywordsLogType {
  TEXT = "text",
  RESPONSE = "response",
  EMBEDDING = "embedding",
  TRANSCRIPTION = "transcription",
  SPEECH = "speech",
  WORKFLOW = "workflow",
  TASK = "task",
  TOOL = "tool",
  AGENT = "agent",
  HANDOFF = "handoff",
  GUARDRAIL = "guardrail",
  FUNCTION = "function",
  CUSTOM = "custom",
  GENERATION = "generation",
  UNKNOWN = "unknown",
}

export const VERCEL_SPAN_TO_KEYWORDS_LOG_TYPE: Record<string, KeywordsLogType> =
  {
    // Text generation spans
    "ai.generateText": KeywordsLogType.TEXT,
    "ai.generateText.doGenerate": KeywordsLogType.TEXT,
    "ai.streamText": KeywordsLogType.TEXT,
    "ai.streamText.doStream": KeywordsLogType.TEXT,

    // Object generation spans
    "ai.generateObject": KeywordsLogType.TEXT,
    "ai.generateObject.doGenerate": KeywordsLogType.TEXT,
    "ai.streamObject": KeywordsLogType.TEXT,
    "ai.streamObject.doStream": KeywordsLogType.TEXT,

    // Embedding spans
    "ai.embed": KeywordsLogType.EMBEDDING,
    "ai.embed.doEmbed": KeywordsLogType.EMBEDDING,
    "ai.embedMany": KeywordsLogType.EMBEDDING,
    "ai.embedMany.doEmbed": KeywordsLogType.EMBEDDING,

    // Tool call spans
    "ai.toolCall": KeywordsLogType.TOOL,

    // Stream events
    "ai.stream.firstChunk": KeywordsLogType.TEXT,

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
