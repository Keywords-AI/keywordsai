// Mapping from Vercel AI SDK span types to Respan log types
import { LogType, RespanLogType } from "@respan/respan-sdk";

export const VERCEL_SPAN_TO_RESPAN_LOG_TYPE: Record<string, LogType> = {
  // Text generation spans
  "ai.generateText": RespanLogType.TEXT,
  "ai.generateText.doGenerate": RespanLogType.TEXT,
  "ai.streamText": RespanLogType.TEXT,
  "ai.streamText.doStream": RespanLogType.TEXT,

  // Object generation spans
  "ai.generateObject": RespanLogType.TEXT,
  "ai.generateObject.doGenerate": RespanLogType.TEXT,
  "ai.streamObject": RespanLogType.TEXT,
  "ai.streamObject.doStream": RespanLogType.TEXT,

  // Embedding spans
  "ai.embed": RespanLogType.EMBEDDING,
  "ai.embed.doEmbed": RespanLogType.EMBEDDING,
  "ai.embedMany": RespanLogType.EMBEDDING,
  "ai.embedMany.doEmbed": RespanLogType.EMBEDDING,

  // Tool call spans
  "ai.toolCall": RespanLogType.TOOL,

  // Stream events
  "ai.stream.firstChunk": RespanLogType.TEXT,

  // Agents and workflows
  "ai.agent": RespanLogType.AGENT,
  "ai.workflow": RespanLogType.WORKFLOW,
  "ai.agent.run": RespanLogType.AGENT,
  "ai.agent.step": RespanLogType.TASK,

  // Functions and handoffs
  "ai.function": RespanLogType.FUNCTION,
  "ai.handoff": RespanLogType.HANDOFF,

  // Other spans that might appear
  "ai.transcript": RespanLogType.TRANSCRIPTION,
  "ai.speech": RespanLogType.SPEECH,
  "ai.response": RespanLogType.RESPONSE,

  // Default to UNKNOWN for unrecognized spans
  default: RespanLogType.UNKNOWN,
};
