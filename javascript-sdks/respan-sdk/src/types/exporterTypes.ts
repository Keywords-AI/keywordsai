/**
 * State for a single pending tool invocation within an exporter session.
 * Used by agent exporters (e.g. Anthropic Agents) to track in-flight tool spans.
 */
export interface PendingToolState {
  spanUniqueId: string;
  startedAt: Date;
  toolName: string;
  toolInput: unknown;
}

/**
 * Session state held by exporters that map agent sessions to traces.
 * Use SDK base types here so all exporters share the same contract.
 */
export interface ExporterSessionState {
  sessionId: string;
  traceId: string;
  traceName: string;
  startedAt: Date;
  pendingTools: Map<string, PendingToolState>;
  isRootEmitted: boolean;
}
