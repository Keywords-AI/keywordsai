import { ReadableSpan } from "@opentelemetry/sdk-trace-base";

export function compareHrTime(a: [number, number], b: [number, number]): number {
  if (a[0] !== b[0]) return a[0] - b[0];
  return a[1] - b[1];
}

export function formatTimestamp(hrTime: [number, number]): string {
  const epochMs = hrTime[0] * 1000 + hrTime[1] / 1e6;
  return new Date(epochMs).toISOString();
}

export function calculateLatency(span: ReadableSpan): number {
  return span.duration[0] + span.duration[1] / 1e9;
}

export function isGenerationSpan(span: ReadableSpan): boolean {
  return ["doGenerate", "doStream"].some((part) => span.name.includes(part));
}

export function isAiSdkSpan(span: ReadableSpan): boolean {
  const instrumentationScopeName =
    span.instrumentationScope?.name ||
    (span as ReadableSpan & { instrumentationLibrary?: { name?: string } })
      .instrumentationLibrary?.name;

  return (
    instrumentationScopeName === "ai" ||
    span.attributes["ai.sdk"] === true ||
    span.name.includes("ai.") ||
    Object.keys(span.attributes).some(
      (key) => key.startsWith("ai.") || key.startsWith("gen_ai.")
    )
  );
}

export function deduplicateSpans(spans: ReadableSpan[]): ReadableSpan[] {
  const traceGroups: Record<string, ReadableSpan[]> = {};

  for (const span of spans) {
    const traceId = span.spanContext().traceId;
    if (!traceGroups[traceId]) {
      traceGroups[traceId] = [];
    }
    traceGroups[traceId].push(span);
  }

  const deduplicatedSpans: ReadableSpan[] = [];

  Object.values(traceGroups).forEach((traceSpans: ReadableSpan[]) => {
    const operationGroups: Record<string, ReadableSpan[]> = {};

    for (const span of traceSpans) {
      let opKey = span.name;
      if (opKey.endsWith(".doStream")) {
        opKey = opKey.replace(".doStream", "");
      } else if (opKey.endsWith(".doGenerate")) {
        opKey = opKey.replace(".doGenerate", "");
      }

      if (!operationGroups[opKey]) {
        operationGroups[opKey] = [];
      }
      operationGroups[opKey].push(span);
    }

    Object.values(operationGroups).forEach((opSpans: ReadableSpan[]) => {
      if (opSpans.length > 1) {
        const detailedSpan = opSpans.find(
          (s: ReadableSpan) =>
            s.name.endsWith(".doStream") || s.name.endsWith(".doGenerate")
        );

        if (detailedSpan) {
          deduplicatedSpans.push(detailedSpan);
        } else {
          deduplicatedSpans.push(...opSpans);
        }
      } else {
        deduplicatedSpans.push(opSpans[0]);
      }
    });
  });

  return deduplicatedSpans;
}

export function getParentSpanId(span: ReadableSpan): string | undefined {
  const legacySpan = span as ReadableSpan & {
    parentSpanId?: string;
  };
  return legacySpan.parentSpanId || span.parentSpanContext?.spanId;
}

