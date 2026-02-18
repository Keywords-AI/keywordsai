export type ExtractedAssistantContent = {
  outputText: string | null;
  toolCalls: Record<string, unknown>[];
  reasoning: Record<string, unknown>[];
  model: string | null;
};

export function buildTraceNameFromPrompt({
  prompt,
}: {
  prompt: unknown;
}): string | null {
  if (typeof prompt !== "string") {
    return null;
  }
  const normalizedPrompt = prompt.trim();
  if (!normalizedPrompt) {
    return null;
  }
  return normalizedPrompt.slice(0, 120);
}

export function toSerializableValue({ value }: { value: unknown }): unknown {
  if (value === null || value === undefined) {
    return undefined;
  }
  if (
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return value;
  }
  if (value instanceof Date) {
    return value.toISOString();
  }
  if (Array.isArray(value)) {
    return value.map((item) => toSerializableValue({ value: item }));
  }
  if (typeof value === "object") {
    const normalizedObject: Record<string, unknown> = {};
    Object.entries(value as Record<string, unknown>).forEach(([key, itemValue]) => {
      normalizedObject[key] = toSerializableValue({ value: itemValue });
    });
    return normalizedObject;
  }
  return String(value);
}

export function toSerializableMetadata({
  value,
}: {
  value: unknown;
}): Record<string, unknown> | undefined {
  const serialized = toSerializableValue({ value });
  if (serialized === undefined) {
    return undefined;
  }
  if (serialized && typeof serialized === "object" && !Array.isArray(serialized)) {
    return serialized as Record<string, unknown>;
  }
  return { value: serialized };
}

export function toSerializableToolCalls({
  value,
}: {
  value: unknown;
}): Record<string, unknown>[] | undefined {
  const serialized = toSerializableValue({ value });
  if (serialized === undefined) {
    return undefined;
  }
  if (Array.isArray(serialized)) {
    return serialized.map((item) => {
      if (item && typeof item === "object" && !Array.isArray(item)) {
        return item as Record<string, unknown>;
      }
      return { value: item };
    });
  }
  if (serialized && typeof serialized === "object") {
    return [serialized as Record<string, unknown>];
  }
  return [{ value: serialized }];
}

export function extractAssistantContent({
  message,
}: {
  message: any;
}): ExtractedAssistantContent {
  const assistantPayload =
    message.message && typeof message.message === "object"
      ? message.message
      : message;
  const content = Array.isArray(assistantPayload.content)
    ? assistantPayload.content
    : [];

  const outputParts: string[] = [];
  const toolCalls: Record<string, unknown>[] = [];
  const reasoning: Record<string, unknown>[] = [];

  content.forEach((contentBlock: any) => {
    if (!contentBlock || typeof contentBlock !== "object") {
      return;
    }

    if (typeof contentBlock.text === "string" && contentBlock.text.length > 0) {
      outputParts.push(contentBlock.text);
    }

    if (
      typeof contentBlock.thinking === "string" &&
      contentBlock.thinking.length > 0
    ) {
      reasoning.push({
        type: "thinking",
        thinking: contentBlock.thinking,
      });
    }

    if (contentBlock.type === "tool_use" || contentBlock.name || contentBlock.input) {
      toolCalls.push({
        type: contentBlock.type || "tool_use",
        id: contentBlock.id,
        name: contentBlock.name,
        input: toSerializableValue({ value: contentBlock.input }),
      });
    }

    if (contentBlock.type === "tool_result" || contentBlock.tool_use_id) {
      toolCalls.push({
        type: "tool_result",
        tool_use_id: contentBlock.tool_use_id,
        content: toSerializableValue({ value: contentBlock.content }),
      });
    }
  });

  const outputText = outputParts.length > 0 ? outputParts.join("\n").trim() : null;
  const model = assistantPayload.model ? String(assistantPayload.model) : null;

  return {
    outputText,
    toolCalls,
    reasoning,
    model,
  };
}

export function extractUserText({ message }: { message: any }): string | null {
  const userPayload =
    message.message && typeof message.message === "object"
      ? message.message
      : message;
  const content = userPayload.content;

  if (typeof content === "string") {
    const normalized = content.trim();
    return normalized.length > 0 ? normalized : null;
  }

  if (!Array.isArray(content)) {
    return null;
  }

  const parts: string[] = [];
  content.forEach((contentBlock: any) => {
    if (!contentBlock || typeof contentBlock !== "object") {
      return;
    }
    if (typeof contentBlock.text === "string" && contentBlock.text.length > 0) {
      parts.push(contentBlock.text);
    }
    if (
      typeof contentBlock.thinking === "string" &&
      contentBlock.thinking.length > 0
    ) {
      parts.push(contentBlock.thinking);
    }
  });

  if (parts.length === 0) {
    return null;
  }
  return parts.join("\n").trim();
}

export function coerceInteger({ value }: { value: unknown }): number | null {
  if (value === null || value === undefined) {
    return null;
  }
  const convertedValue = Number(value);
  if (!Number.isFinite(convertedValue)) {
    return null;
  }
  return Math.trunc(convertedValue);
}
