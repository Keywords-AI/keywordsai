import { query } from "@anthropic-ai/claude-agent-sdk";
import { randomUUID } from "node:crypto";
import {
  type PendingToolState,
  RespanLogType,
  RespanPayload,
  RESPAN_TRACING_INGEST_ENDPOINT,
  type SessionState,
} from "@respan/respan-sdk";
import {
  buildTraceNameFromPrompt,
  coerceInteger,
  extractAssistantContent,
  extractUserText,
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
      inputValue: prompt,
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
    const userText = this.extractUserText({ message });
    if (!userText) {
      return;
    }

    const now = new Date();
    const payload = this.createPayload({
      sessionState,
      spanUniqueId: randomUUID(),
      spanParentId: sessionState.traceId,
      spanName: "user_message",
      logType: RespanLogType.TASK,
      startTime: now,
      timestamp: now,
      inputValue: userText,
      metadata: { source: "stream_user_message" },
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
    const extractedContent = this.extractAssistantContent({ message });

    if (
      !extractedContent.outputText &&
      extractedContent.toolCalls.length === 0 &&
      extractedContent.reasoning.length === 0
    ) {
      return;
    }

    const spanTools = extractedContent.toolCalls
      .map((toolCall) => {
        if (typeof toolCall.name === "string") {
          return toolCall.name;
        }
        return null;
      })
      .filter((toolName): toolName is string => Boolean(toolName));

    const completionMessage =
      extractedContent.outputText && extractedContent.outputText.length > 0
        ? {
            role: "assistant",
            content: extractedContent.outputText,
          }
        : undefined;

    const now = new Date();
    const payload = this.createPayload({
      sessionState,
      spanUniqueId: randomUUID(),
      spanParentId: sessionState.traceId,
      spanName: "assistant_message",
      logType: RespanLogType.GENERATION,
      startTime: now,
      timestamp: now,
      outputValue: extractedContent.outputText,
      model: extractedContent.model || null,
      metadata: {
        reasoning: extractedContent.reasoning.length > 0 ? extractedContent.reasoning : undefined,
        source: "stream_assistant_message",
      },
      spanTools: spanTools.length > 0 ? spanTools : undefined,
      toolCalls: extractedContent.toolCalls.length > 0 ? extractedContent.toolCalls : undefined,
      completionMessage,
      completionMessages: completionMessage ? [completionMessage] : undefined,
    });
    await this.sendPayloads({ payloads: [payload] });
  }

  private async handleResultMessage({ message }: { message: any }): Promise<void> {
    const sessionId = String(message.session_id || message.sessionId || this.lastSessionId || randomUUID());
    const sessionState = this.ensureSessionState({ sessionId });

    const usage = (message.usage && typeof message.usage === "object"
      ? message.usage
      : {}) as Record<string, unknown>;
    const promptTokens = this.coerceInteger({
      value: usage.input_tokens || usage.prompt_tokens,
    });
    const completionTokens = this.coerceInteger({
      value: usage.output_tokens || usage.completion_tokens,
    });
    let totalRequestTokens = this.coerceInteger({
      value: usage.total_tokens,
    });
    if (totalRequestTokens === null) {
      totalRequestTokens = (promptTokens || 0) + (completionTokens || 0);
    }

    const promptCacheHitTokens = this.coerceInteger({
      value: usage.cache_read_input_tokens,
    });
    const promptCacheCreationTokens = this.coerceInteger({
      value: usage.cache_creation_input_tokens,
    });

    const statusCode = message.is_error ? 500 : 200;
    const errorMessage = message.is_error
      ? `agent_result_error:${String(message.subtype || "error")}`
      : undefined;

    const now = new Date();
    const payload = this.createPayload({
      sessionState,
      spanUniqueId: randomUUID(),
      spanParentId: sessionState.traceId,
      spanName: `result:${String(message.subtype || "unknown")}`,
      logType: RespanLogType.AGENT,
      startTime: now,
      timestamp: now,
      outputValue: message.result || message.subtype,
      metadata: {
        duration_ms: message.duration_ms,
        duration_api_ms: message.duration_api_ms,
        num_turns: message.num_turns,
        total_cost_usd: message.total_cost_usd,
        structured_output: message.structured_output,
      },
      promptTokens,
      completionTokens,
      totalRequestTokens,
      promptCacheHitTokens,
      promptCacheCreationTokens,
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
      rootEmitted: false,
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
    if (sessionState.rootEmitted) {
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
    sessionState.rootEmitted = true;
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
    completionMessage,
    completionMessages,
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
    completionMessage?: Record<string, unknown>;
    completionMessages?: Record<string, unknown>[];
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
      completion_message: completionMessage as any,
      completion_messages: completionMessages as any,
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

  private extractAssistantContent({
    message,
  }: {
    message: any;
  }): {
    outputText: string | null;
    toolCalls: Record<string, unknown>[];
    reasoning: Record<string, unknown>[];
    model: string | null;
  } {
    return extractAssistantContent({ message });
  }

  private extractUserText({ message }: { message: any }): string | null {
    return extractUserText({ message });
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

    let attempt = 0;
    let delaySeconds = this.baseDelaySeconds;

    while (true) {
      attempt += 1;
      const abortController = new AbortController();
      const timeoutHandle = setTimeout(() => {
        abortController.abort();
      }, this.timeoutMs);

      try {
        const response = await fetch(this.endpoint, {
          method: "POST",
          headers,
          body,
          signal: abortController.signal,
        });
        clearTimeout(timeoutHandle);

        if (response.status < 300) {
          return;
        }

        const responseText = await response.text();
        if (response.status >= 400 && response.status < 500) {
          console.error(
            `Respan export client error ${response.status}: ${responseText}`
          );
          return;
        }

        console.warn(
          `Respan export server error ${response.status}: ${responseText}`
        );
      } catch (error) {
        clearTimeout(timeoutHandle);
        console.warn("Respan export network error:", error);
      }

      if (attempt >= this.maxRetries) {
        console.error(`Respan export failed after ${attempt} attempts`);
        return;
      }

      const jitterSeconds = Math.random() * 0.1 * delaySeconds;
      await new Promise((resolve) =>
        setTimeout(resolve, (delaySeconds + jitterSeconds) * 1000)
      );
      delaySeconds = Math.min(delaySeconds * 2, this.maxDelaySeconds);
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
