# Respan Exporter for Anthropic Agent SDK

**[respan.ai](https://respan.ai)** | **[Documentation](https://docs.respan.ai)**

Exporter for Anthropic Agent SDK telemetry to Respan.

## Quickstart

```typescript
import { RespanAnthropicAgentsExporter } from "@respan/exporter-anthropic-agents";

const exporter = new RespanAnthropicAgentsExporter();

for await (const message of exporter.query({
  prompt: "Review this repository and summarize architecture.",
  options: {
    allowedTools: ["Read", "Glob", "Grep"],
    permissionMode: "acceptEdits",
  },
})) {
  console.log(message);
}
```

