import { query } from "@anthropic-ai/claude-agent-sdk";
import { randomUUID } from "node:crypto";
import {
  type PendingToolState,
  RespanLogType,
  RespanPayload,
  RESPAN_TRACING_INGEST_ENDPOINT,
  type SessionState,
  fetchWithRetry,
} from "@respan/respan-sdk";
import {
  buildTraceNameFromPrompt,
  coerceInteger,
  toSerializableMetadata,
  toSerializableToolCalls,
  toSerializableValue,
} from "./utils.js";

export class RespanAnthropicAgentsExporter {
  private apiKey: string | null;
  private endpoint: string;
  private maxRetries: number;
  private baseDelaySeconds: number;
  private maxDelaySeconds: number;
  private timeoutMs: number;

  private sessions: Map<string, SessionState>;
  private lastSessionId: string | null;
  private lastModel: string | null;

  constructor({
    apiKey = process.env.RESPAN_API_KEY || process.env.KEYWORDSAI_API_KEY || null,
    endpoint,
    maxRetries = 3,
    baseDelaySeconds = 1,
    maxDelaySeconds = 30,
    timeoutMs = 15000,
  }: {
    apiKey?: string | null;
    endpoint?: string;
    maxRetries?: number;
    baseDelaySeconds?: number;
    maxDelaySeconds?: number;
    timeoutMs?: number;
  } = {}) {
    this.apiKey = apiKey;
    this.endpoint = endpoint || RESPAN_TRACING_INGEST_ENDPOINT;
    this.maxRetries = maxRetries;
    this.baseDelaySeconds = baseDelaySeconds;
    this.maxDelaySeconds = maxDelaySeconds;
    this.timeoutMs = timeoutMs;

    this.sessions = new Map();
    this.lastSessionId = null;
    this.lastModel = null;
  }
  setEndpoint(endpoint: string): void {
    this.endpoint = endpoint;
  }

  createHooks(
    existingHooks: Record<string, unknown[]> = {}
  ): Record<string, unknown[]> {
    const mergedHooks: Record<string, unknown[]> = { ...existingHooks };

    this.appendHook({
      hooks: mergedHooks,
      eventName: "UserPromptSubmit",
      matcher: undefined,
      callback: this.onUserPromptSubmit.bind(this),
    });
    this.appendHook({
      hooks: mergedHooks,
      eventName: "PreToolUse",
      matcher: undefined,
      callback: this.onPreToolUse.bind(this),
    });
    this.appendHook({
      hooks: mergedHooks,
      eventName: "PostToolUse",
      matcher: undefined,
      callback: this.onPostToolUse.bind(this),
    });
    this.appendHook({
      hooks: mergedHooks,
      eventName: "SubagentStop",
      matcher: undefined,
      callback: this.onSubagentStop.bind(this),
    });
    this.appendHook({
      hooks: mergedHooks,
      eventName: "Stop",
      matcher: undefined,
      callback: this.onStop.bind(this),
    });

    return mergedHooks;
  }

  withOptions(options: Record<string, unknown> = {}): Record<string, unknown> {
    const instrumentedOptions: Record<string, unknown> = { ...options };
    const optionHooks =
      options.hooks && typeof options.hooks === "object"
        ? (options.hooks as Record<string, unknown[]>)
        : {};
    instrumentedOptions.hooks = this.createHooks(optionHooks);
    return instrumentedOptions;
  }

  async *query({
    prompt,
    options = {},
  }: {
    prompt: string | AsyncIterable<any>;
    options?: Record<string, unknown>;
  }): AsyncGenerator<unknown, void, unknown> {
    const instrumentedOptions = this.withOptions(options);

    for await (const message of query({
      prompt,
      options: instrumentedOptions as any,
    })) {
      const resolvedSessionId = this.resolveMessageSessionId({
        message,
        fallbackSessionId: this.lastSessionId,
      });
      await this.trackMessage({
        message,
        sessionId: resolvedSessionId || undefined,
      });
      yield message;
    }
  }

  async trackMessage({
    message,
    sessionId,
  }: {
    message: any;
    sessionId?: string;
  }): Promise<void> {
    if (!message || typeof message !== "object") {
      return;
    }

    if (message.type === "system") {
      this.handleSystemMessage({ message, sessionId });
      return;
    }

    if (message.type === "assistant") {
      await this.handleAssistantMessage({ message, sessionId });
      return;
    }

    if (message.type === "result") {
      await this.handleResultMessage({ message });
      return;
    }

    if (message.type === "user") {
      await this.handleUserMessage({ message, sessionId });
      return;
    }

    if (message.type === "stream_event") {
      const streamSessionId =
        message.session_id || message.sessionId || sessionId || null;
      if (streamSessionId) {
        this.lastSessionId = String(streamSessionId);
      }
    }
  }

  private appendHook({
    hooks,
    eventName,
    matcher,
    callback,
  }: {
    hooks: Record<string, unknown[]>;
    eventName: string;
    matcher?: string;
    callback: (...args: any[]) => Promise<Record<string, unknown>>;
  }): void {
    const eventHooks = hooks[eventName] ? [...hooks[eventName]] : [];
    const callbackName = callback.name;
    const hasExistingCallback = eventHooks.some((eventHook) => {
      if (!eventHook || typeof eventHook !== "object") {
        return false;
      }
      const normalizedHook = eventHook as {
        matcher?: string;
        hooks?: Array<(...args: any[]) => Promise<Record<string, unknown>>>;
      };
      if (normalizedHook.matcher !== matcher) {
        return false;
      }
      if (!Array.isArray(normalizedHook.hooks)) {
        return false;
      }
      return normalizedHook.hooks.some((existingCallback) => {
        return existingCallback.name === callbackName;
      });
    });
    if (hasExistingCallback) {
      return;
    }

    if (matcher) {
      eventHooks.push({ matcher, hooks: [callback] });
    } else {
      eventHooks.push({ hooks: [callback] });
    }
    hooks[eventName] = eventHooks;
  }

  private async onUserPromptSubmit(
    input: Record<string, any>,
    toolUseId?: string
  ): Promise<Record<string, unknown>> {
    const sessionId = this.extractSessionIdFromHookInput({ input });
    const prompt = input.prompt;
    const traceName = this.buildTraceNameFromPrompt({ prompt });
    const sessionState = this.ensureSessionState({ sessionId, traceName });

    const now = new Date();
    const payload = this.createPayload({
      sessionState,
      spanUniqueId: randomUUID(),
      spanParentId: sessionState.traceId,
      spanName: "user_prompt",
      logType: RespanLogType.TASK,
      startTime: now,
      timestamp: now,
      inputValue: input,
      metadata: { hook_event_name: "UserPromptSubmit" },
    });
    await this.sendPayloads({ payloads: [payload] });
    return {};
  }

  private async onPreToolUse(
    input: Record<string, any>,
    toolUseId?: string
  ): Promise<Record<string, unknown>> {
    const sessionId = this.extractSessionIdFromHookInput({ input });
    const sessionState = this.ensureSessionState({ sessionId });

    const resolvedToolUseId = String(
      input.tool_use_id || toolUseId || randomUUID()
    );
    sessionState.pendingTools.set(resolvedToolUseId, {
      spanUniqueId: randomUUID(),
      startedAt: new Date(),
      toolName: String(input.tool_name || RespanLogType.TOOL),
      toolInput: input.tool_input,
    });
    return {};
  }

  private async onPostToolUse(
    input: Record<string, any>,
    toolUseId?: string
  ): Promise<Record<string, unknown>> {
    const sessionId = this.extractSessionIdFromHookInput({ input });
    const sessionState = this.ensureSessionState({ sessionId });
    const resolvedToolUseId = String(
      input.tool_use_id || toolUseId || randomUUID()
    );

    const pendingToolState = sessionState.pendingTools.get(resolvedToolUseId) || {
      spanUniqueId: randomUUID(),
      startedAt: new Date(),
      toolName: String(input.tool_name || RespanLogType.TOOL),
      toolInput: input.tool_input,
    };
    sessionState.pendingTools.delete(resolvedToolUseId);

    const toolName = String(
      input.tool_name || pendingToolState.toolName || RespanLogType.TOOL
    );
    const payload = this.createPayload({
      sessionState,
      spanUniqueId: pendingToolState.spanUniqueId,
      spanParentId: sessionState.traceId,
      spanName: toolName,
      logType: RespanLogType.TOOL,
      startTime: pendingToolState.startedAt,
      timestamp: new Date(),
      inputValue: pendingToolState.toolInput,
      outputValue: input.tool_response,
      metadata: {
        hook_event_name: "PostToolUse",
        tool_use_id: resolvedToolUseId,
      },
      spanTools: [toolName],
    });
    await this.sendPayloads({ payloads: [payload] });
    return {};
  }

  private async onSubagentStop(
    input: Record<string, any>,
    toolUseId?: string
  ): Promise<Record<string, unknown>> {
    const sessionId = this.extractSessionIdFromHookInput({ input });
    const sessionState = this.ensureSessionState({ sessionId });

    const now = new Date();
    const payload = this.createPayload({
      sessionState,
      spanUniqueId: randomUUID(),
      spanParentId: sessionState.traceId,
      spanName: "subagent_stop",
      logType: RespanLogType.TASK,
      startTime: now,
      timestamp: now,
      metadata: {
        hook_event_name: "SubagentStop",
        agent_id: input.agent_id,
        agent_type: input.agent_type,
      },
    });
    await this.sendPayloads({ payloads: [payload] });
    return {};
  }

  private async onStop(
    input: Record<string, any>,
    toolUseId?: string
  ): Promise<Record<string, unknown>> {
    return {};
  }

  private handleSystemMessage({
    message,
    sessionId,
  }: {
    message: any;
    sessionId?: string;
  }): void {
    const resolvedSessionId =
      sessionId ||
      this.extractSessionIdFromSystemMessage({ message }) ||
      this.lastSessionId;
    if (!resolvedSessionId) {
      return;
    }

    this.lastSessionId = resolvedSessionId;
    this.ensureSessionState({ sessionId: resolvedSessionId });
  }

  private async handleUserMessage({
    message,
    sessionId,
  }: {
    message: any;
    sessionId?: string;
  }): Promise<void> {
    const resolvedSessionId = sessionId || this.lastSessionId;
    if (!resolvedSessionId) {
      return;
    }
    const sessionState = this.ensureSessionState({ sessionId: resolvedSessionId });
    const now = new Date();
    const payload = this.createPayload({
      sessionState,
      spanUniqueId: randomUUID(),
      spanParentId: sessionState.traceId,
      spanName: "user_message",
      logType: RespanLogType.TASK,
      startTime: now,
      timestamp: now,
      inputValue: message,
    });
    await this.sendPayloads({ payloads: [payload] });
  }

  private async handleAssistantMessage({
    message,
    sessionId,
  }: {
    message: any;
    sessionId?: string;
  }): Promise<void> {
    const resolvedSessionId = sessionId || this.lastSessionId;
    if (!resolvedSessionId) {
      return;
    }
    const sessionState = this.ensureSessionState({ sessionId: resolvedSessionId });

    const usage = (message?.usage && typeof message.usage === "object"
      ? message.usage
      : {}) as Record<string, unknown>;

    const model = (message?.model && String(message.model)) || null;
    if (model) {
      this.lastModel = model;
    }

    const contentBlocks: any[] = Array.isArray(message?.content) ? message.content : [];
    const textParts: string[] = [];
    const toolCalls: Record<string, unknown>[] = [];
    for (const block of contentBlocks) {
      if (block?.type === "text") {
        textParts.push(String(block.text ?? ""));
      } else if (block?.type === "tool_use") {
        toolCalls.push({
          id: block.id ?? null,
          name: block.name ?? null,
          input: block.input ?? null,
        });
      }
    }

    const outputText = textParts.length > 0 ? textParts.join("\n") : null;

    const now = new Date();
    const payload = this.createPayload({
      sessionState,
      spanUniqueId: (message?.id && String(message.id)) || randomUUID(),
      spanParentId: sessionState.traceId,
      spanName: "assistant_message",
      logType: RespanLogType.GENERATION,
      startTime: sessionState.startedAt,
      timestamp: now,
      inputValue: undefined,
      outputValue: outputText,
      model,
      toolCalls: toolCalls.length > 0 ? toolCalls : undefined,
      promptTokens: this.coerceInteger({ value: usage.input_tokens }),
      completionTokens: this.coerceInteger({ value: usage.output_tokens }),
      promptCacheHitTokens: this.coerceInteger({ value: usage.cache_read_input_tokens }),
      promptCacheCreationTokens: this.coerceInteger({ value: usage.cache_creation_input_tokens }),
    });
    await this.sendPayloads({ payloads: [payload] });
  }

  private async handleResultMessage({ message }: { message: any }): Promise<void> {
    const sessionId = String(message.session_id || message.sessionId || this.lastSessionId || randomUUID());
    const sessionState = this.ensureSessionState({ sessionId });

    const usage = (message.usage && typeof message.usage === "object"
      ? message.usage
      : {}) as Record<string, unknown>;

    const statusCode = message.is_error ? 500 : 200;
    const errorMessage = message.is_error
      ? `agent_result_error:${String(message.subtype || "error")}`
      : undefined;

    const resultOutput = message.result ?? message.structured_output ?? null;

    const metadata: Record<string, unknown> = {};
    if (message.num_turns != null) {
      metadata.num_turns = message.num_turns;
    }
    if (message.total_cost_usd != null) {
      metadata.sdk_total_cost_usd = message.total_cost_usd;
    }

    const now = new Date();
    const payload = this.createPayload({
      sessionState,
      spanUniqueId: randomUUID(),
      spanParentId: sessionState.traceId,
      spanName: `result:${String(message.subtype || "unknown")}`,
      logType: RespanLogType.AGENT,
      startTime: sessionState.startedAt,
      timestamp: now,
      inputValue: undefined,
      outputValue: resultOutput,
      model: this.lastModel,
      metadata: Object.keys(metadata).length > 0 ? metadata : undefined,
      promptTokens: this.coerceInteger({ value: usage.input_tokens }),
      completionTokens: this.coerceInteger({ value: usage.output_tokens }),
      promptCacheHitTokens: this.coerceInteger({ value: usage.cache_read_input_tokens }),
      promptCacheCreationTokens: this.coerceInteger({ value: usage.cache_creation_input_tokens }),
      statusCode,
      errorMessage,
    });
    await this.sendPayloads({ payloads: [payload] });
    sessionState.pendingTools.clear();
  }

  private resolveMessageSessionId({
    message,
    fallbackSessionId,
  }: {
    message: any;
    fallbackSessionId?: string | null;
  }): string | null {
    if (!message || typeof message !== "object") {
      return fallbackSessionId || null;
    }

    const directSessionId = message.session_id || message.sessionId;
    if (directSessionId) {
      this.lastSessionId = String(directSessionId);
      return String(directSessionId);
    }

    if (message.type === "system") {
      const systemSessionId = this.extractSessionIdFromSystemMessage({ message });
      if (systemSessionId) {
        this.lastSessionId = systemSessionId;
        return systemSessionId;
      }
    }

    if (fallbackSessionId) {
      return fallbackSessionId;
    }
    return null;
  }

  private extractSessionIdFromSystemMessage({ message }: { message: any }): string | null {
    if (!message || typeof message !== "object") {
      return null;
    }
    const data = message.data && typeof message.data === "object" ? message.data : {};
    const rawSessionId = data.session_id || data.sessionId || data.id || null;
    if (!rawSessionId) {
      return null;
    }
    return String(rawSessionId);
  }

  private extractSessionIdFromHookInput({
    input,
  }: {
    input: Record<string, any>;
  }): string {
    const hookSessionId = input.session_id || input.sessionId;
    if (hookSessionId) {
      const normalizedSessionId = String(hookSessionId);
      this.lastSessionId = normalizedSessionId;
      return normalizedSessionId;
    }
    if (this.lastSessionId) {
      return this.lastSessionId;
    }
    const generatedSessionId = randomUUID();
    this.lastSessionId = generatedSessionId;
    return generatedSessionId;
  }

  private buildTraceNameFromPrompt({ prompt }: { prompt: unknown }): string | null {
    return buildTraceNameFromPrompt({ prompt });
  }

  private ensureSessionState({
    sessionId,
    traceName,
  }: {
    sessionId: string;
    traceName?: string | null;
  }): SessionState {
    const existingSessionState = this.sessions.get(sessionId);
    if (existingSessionState) {
      if (
        traceName &&
        existingSessionState.traceName.startsWith("anthropic-session-")
      ) {
        existingSessionState.traceName = traceName;
      }
      this.lastSessionId = sessionId;
      return existingSessionState;
    }

    const resolvedTraceName =
      traceName && traceName.trim().length > 0
        ? traceName.trim()
        : `anthropic-session-${sessionId.slice(0, 12)}`;

    const newSessionState: SessionState = {
      sessionId,
      traceId: sessionId,
      traceName: resolvedTraceName,
      startedAt: new Date(),
      pendingTools: new Map(),
      isRootEmitted: false,
    };
    this.sessions.set(sessionId, newSessionState);
    this.lastSessionId = sessionId;
    void this.emitRootSpan({ sessionState: newSessionState });
    return newSessionState;
  }

  private async emitRootSpan({
    sessionState,
  }: {
    sessionState: SessionState;
  }): Promise<void> {
    if (sessionState.isRootEmitted) {
      return;
    }
    const payload = this.createPayload({
      sessionState,
      spanUniqueId: sessionState.traceId,
      spanParentId: undefined,
      spanName: sessionState.traceName,
      logType: RespanLogType.AGENT,
      startTime: sessionState.startedAt,
      timestamp: sessionState.startedAt,
      metadata: { source: "session_root" },
    });
    await this.sendPayloads({ payloads: [payload] });
    sessionState.isRootEmitted = true;
  }

  private createPayload({
    sessionState,
    spanUniqueId,
    spanParentId,
    spanName,
    logType,
    startTime,
    timestamp,
    inputValue,
    outputValue,
    model,
    metadata,
    spanTools,
    toolCalls,
    promptTokens,
    completionTokens,
    totalRequestTokens,
    promptCacheHitTokens,
    promptCacheCreationTokens,
    statusCode = 200,
    errorMessage,
  }: {
    sessionState: SessionState;
    spanUniqueId: string;
    spanParentId?: string;
    spanName: string;
    logType: RespanLogType;
    startTime?: Date;
    timestamp?: Date;
    inputValue?: unknown;
    outputValue?: unknown;
    model?: string | null;
    metadata?: Record<string, unknown>;
    spanTools?: string[];
    toolCalls?: Record<string, unknown>[];
    promptTokens?: number | null;
    completionTokens?: number | null;
    totalRequestTokens?: number | null;
    promptCacheHitTokens?: number | null;
    promptCacheCreationTokens?: number | null;
    statusCode?: number;
    errorMessage?: string;
  }): Partial<RespanPayload> {
    const resolvedStartTime = startTime || new Date();
    const resolvedTimestamp = timestamp || resolvedStartTime;
    const latencySeconds = Math.max(
      (resolvedTimestamp.getTime() - resolvedStartTime.getTime()) / 1000,
      0
    );

    const payload: Partial<RespanPayload> = {
      trace_unique_id: sessionState.traceId,
      span_unique_id: spanUniqueId,
      span_parent_id: spanParentId,
      trace_name: sessionState.traceName,
      session_identifier: sessionState.sessionId,
      span_name: spanName,
      span_workflow_name: sessionState.traceName,
      log_type: logType,
      start_time: resolvedStartTime,
      timestamp: resolvedTimestamp,
      latency: latencySeconds,
      status_code: statusCode,
      error_bit: errorMessage ? 1 : 0,
      error_message: errorMessage,
      input: this.toSerializableValue({ value: inputValue }) as any,
      output: this.toSerializableValue({ value: outputValue }) as any,
      model: model || undefined,
      metadata: this.toSerializableMetadata({ value: metadata }),
      span_tools: spanTools,
      tool_calls: this.toSerializableToolCalls({ value: toolCalls }) as any,
      prompt_tokens: promptTokens ?? undefined,
      completion_tokens: completionTokens ?? undefined,
      total_request_tokens: totalRequestTokens ?? undefined,
      prompt_cache_hit_tokens: promptCacheHitTokens ?? undefined,
      prompt_cache_creation_tokens: promptCacheCreationTokens ?? undefined,
    };

    return payload;
  }

  private toSerializableMetadata({
    value,
  }: {
    value: unknown;
  }): Record<string, unknown> | undefined {
    return toSerializableMetadata({ value });
  }

  private toSerializableToolCalls({
    value,
  }: {
    value: unknown;
  }): Record<string, unknown>[] | undefined {
    return toSerializableToolCalls({ value });
  }

  private toSerializableValue({ value }: { value: unknown }): unknown {
    return toSerializableValue({ value });
  }

  private async sendPayloads({
    payloads,
  }: {
    payloads: Partial<RespanPayload>[];
  }): Promise<void> {
    if (payloads.length === 0) {
      return;
    }

    if (!this.apiKey) {
      console.warn("Respan API key is not set; skipping exporter upload");
      return;
    }

    const body = JSON.stringify({ data: payloads });
    const headers: Record<string, string> = {
      Authorization: `Bearer ${this.apiKey}`,
      "Content-Type": "application/json",
    };

    try {
      await fetchWithRetry({
        url: this.endpoint,
        init: {
          method: "POST",
          headers,
          body,
        },
        maxRetries: this.maxRetries,
        baseDelaySeconds: this.baseDelaySeconds,
        maxDelaySeconds: this.maxDelaySeconds,
        timeoutMs: this.timeoutMs,
      });
    } catch (error) {
      console.error("Respan export failed:", error);
    }
  }

  private coerceInteger({ value }: { value: unknown }): number | null {
    return coerceInteger({ value });
  }
}

export class RespanSpanExporter extends RespanAnthropicAgentsExporter {}

export function instrumentOptions({
  exporter,
  options = {},
}: {
  exporter: RespanAnthropicAgentsExporter;
  options?: Record<string, unknown>;
}): Record<string, unknown> {
  return exporter.withOptions(options);
}
