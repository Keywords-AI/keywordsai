export const RESPAN_TRACING_INGEST_ENDPOINT =
  "https://api.respan.ai/api/v1/traces/ingest" as const;

export function resolveTracingIngestEndpoint(baseUrl?: string): string {
  if (!baseUrl) {
    return RESPAN_TRACING_INGEST_ENDPOINT;
  }

  const normalizedBaseUrl = baseUrl.replace(/\/$/, "");
  if (normalizedBaseUrl.endsWith("/api")) {
    return `${normalizedBaseUrl}/v1/traces/ingest`;
  }

  return `${normalizedBaseUrl}/api/v1/traces/ingest`;
}
