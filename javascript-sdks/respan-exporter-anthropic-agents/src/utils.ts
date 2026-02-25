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
