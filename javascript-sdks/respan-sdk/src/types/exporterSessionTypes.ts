/**
 * Types for exporter session state (cross-language match with Python
 * respan_sdk.respan_types.exporter_session_types).
 */

/** State for a tool call that has started but not yet completed. */
export type PendingToolState = {
  spanUniqueId: string;
  startedAt: Date;
  toolName: string;
  toolInput: unknown;
};

/** Session state held by exporters (e.g. Anthropic agents) per session. */
export type SessionState = {
  sessionId: string;
  traceId: string;
  traceName: string;
  startedAt: Date;
  pendingTools: Map<string, PendingToolState>;
  rootEmitted: boolean;
};

/** Alias for cross-language consistency with Python ExporterSessionState. */
export type ExporterSessionState = SessionState;
