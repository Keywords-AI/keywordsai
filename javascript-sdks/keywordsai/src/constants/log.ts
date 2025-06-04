// Mapping from Vercel AI SDK span types to KeywordsAI log types
import { LogType } from "../types/logTypes";

export const VERCEL_SPAN_TO_KEYWORDS_LOG_TYPE: Record<string, LogType> = {
  // Text generation spans
  "ai.generateText": "text",
  "ai.generateText.doGenerate": "text",
  "ai.streamText": "text",
  "ai.streamText.doStream": "text",

  // Object generation spans
  "ai.generateObject": "text",
  "ai.generateObject.doGenerate": "text",
  "ai.streamObject": "text",
  "ai.streamObject.doStream": "text",

  // Embedding spans
  "ai.embed": "embedding",
  "ai.embed.doEmbed": "embedding",
  "ai.embedMany": "embedding",
  "ai.embedMany.doEmbed": "embedding",

  // Tool call spans
  "ai.toolCall": "tool",

  // Stream events
  "ai.stream.firstChunk": "text",

  // Agents and workflows
  "ai.agent": "agent",
  "ai.workflow": "workflow",
  "ai.agent.run": "agent",
  "ai.agent.step": "task",

  // Functions and handoffs
  "ai.function": "function",
  "ai.handoff": "handoff",

  // Other spans that might appear
  "ai.transcript": "transcription",
  "ai.speech": "speech",
  "ai.response": "response",

  // Default to UNKNOWN for unrecognized spans
  default: "unknown",
};
