/**
 * Options for fetchWithRetry (exponential backoff + jitter).
 */
export interface FetchWithRetryOptions {
  url: string;
  init: RequestInit;
  maxRetries?: number;
  baseDelaySeconds?: number;
  maxDelaySeconds?: number;
  timeoutMs?: number;
}

/**
 * Shared utility: POST with exponential backoff and jitter.
 * Use this in exporters instead of inline retry logic.
 * - Retries on 5xx and network errors; does not retry on 4xx.
 * - Delay doubles each attempt, capped at maxDelaySeconds, with 10% jitter.
 */
export async function fetchWithRetry({
  url,
  init,
  maxRetries = 3,
  baseDelaySeconds = 1,
  maxDelaySeconds = 30,
  timeoutMs = 15000,
}: FetchWithRetryOptions): Promise<void> {
  let attempt = 0;
  let delaySeconds = baseDelaySeconds;

  while (true) {
    attempt += 1;
    const abortController = new AbortController();
    const timeoutHandle = setTimeout(() => {
      abortController.abort();
    }, timeoutMs);

    const mergedInit = { ...init, signal: abortController.signal };

    try {
      const response = await fetch(url, mergedInit);
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

    if (attempt >= maxRetries) {
      console.error(`Respan export failed after ${attempt} attempts`);
      return;
    }

    const jitterSeconds = Math.random() * 0.1 * delaySeconds;
    await new Promise((resolve) =>
      setTimeout(resolve, (delaySeconds + jitterSeconds) * 1000)
    );
    delaySeconds = Math.min(delaySeconds * 2, maxDelaySeconds);
  }
}
