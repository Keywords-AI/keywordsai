/**
 * General-purpose retry with exponential backoff and jitter.
 * Matches Python RetryHandler contract: throws on exhausted retries (no silent swallow).
 */

export interface RetryHandlerOptions {
  maxRetries?: number;
  retryDelaySeconds?: number;
  backoffMultiplier?: number;
  maxDelaySeconds?: number;
  jitterFraction?: number;
  logRetries?: boolean;
}

const defaultOptions: Required<RetryHandlerOptions> = {
  maxRetries: 3,
  retryDelaySeconds: 1,
  backoffMultiplier: 2,
  maxDelaySeconds: 30,
  jitterFraction: 0.1,
  logRetries: true,
};

/**
 * General-purpose retry: execute an async function with retries; throws on final failure.
 */
export async function executeWithRetry<T>(
  fn: () => Promise<T>,
  context: string = "operation",
  options: RetryHandlerOptions = {}
): Promise<T> {
  const opts = { ...defaultOptions, ...options };
  let lastError: Error | undefined;
  for (let attempt = 0; attempt < opts.maxRetries; attempt++) {
    try {
      const result = await fn();
      if (attempt > 0 && opts.logRetries) {
        console.warn(
          `Success on retry ${attempt}/${opts.maxRetries - 1} for ${context}`
        );
      }
      return result;
    } catch (e) {
      lastError = e instanceof Error ? e : new Error(String(e));
      const isLast = attempt === opts.maxRetries - 1;
      if (opts.logRetries) {
        if (isLast) {
          console.error(
            `All ${opts.maxRetries} retries exhausted for ${context}:`,
            lastError
          );
        } else {
          console.warn(
            `Retry ${attempt + 1}/${opts.maxRetries} for ${context}:`,
            lastError
          );
        }
      }
      if (isLast) {
        throw lastError;
      }
      let delay =
        opts.retryDelaySeconds * Math.pow(opts.backoffMultiplier, attempt);
      if (opts.jitterFraction > 0) {
        delay += delay * opts.jitterFraction * Math.random();
      }
      delay = Math.min(delay, opts.maxDelaySeconds);
      await new Promise((resolve) => setTimeout(resolve, delay * 1000));
    }
  }
  throw lastError ?? new Error(`Retry handler failed for ${context}`);
}

export interface FetchWithRetryOptions {
  url: string;
  init: RequestInit;
  maxRetries?: number;
  baseDelaySeconds?: number;
  maxDelaySeconds?: number;
  timeoutMs?: number;
}

/**
 * POST with retry (uses executeWithRetry). Throws on exhausted retries (matches Python contract).
 * Retries on 5xx and network errors; does not retry on 4xx.
 */
export async function fetchWithRetry({
  url,
  init,
  maxRetries = 3,
  baseDelaySeconds = 1,
  maxDelaySeconds = 30,
  timeoutMs = 15000,
}: FetchWithRetryOptions): Promise<Response> {
  return executeWithRetry(
    async () => {
      const abortController = new AbortController();
      const timeoutHandle = setTimeout(() => {
        abortController.abort();
      }, timeoutMs);
      const mergedInit = { ...init, signal: abortController.signal };
      try {
        const response = await fetch(url, mergedInit);
        clearTimeout(timeoutHandle);
        if (response.status < 300) {
          return response;
        }
        const responseText = await response.text();
        if (response.status >= 400 && response.status < 500) {
          console.error(
            `Respan export client error ${response.status}: ${responseText}`
          );
          throw new Error(`Client error ${response.status}: ${responseText}`);
        }
        console.warn(
          `Respan export server error ${response.status}: ${responseText}`
        );
        throw new Error(`Server error ${response.status}: ${responseText}`);
      } catch (error) {
        clearTimeout(timeoutHandle);
        if ((error as Error).name === "AbortError") {
          throw new Error("Respan export request timeout");
        }
        console.warn("Respan export network error:", error);
        throw error;
      }
    },
    "export ingest",
    {
      maxRetries,
      retryDelaySeconds: baseDelaySeconds,
      backoffMultiplier: 2,
      maxDelaySeconds,
      jitterFraction: 0.1,
    }
  );
}
