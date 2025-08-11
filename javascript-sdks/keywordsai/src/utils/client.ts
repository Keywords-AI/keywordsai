/**
 * Centralized HTTP Client for Keywords AI
 *
 * This module provides a centralized HTTP client for making API requests to Keywords AI services.
 * It handles authentication, common headers, and provides both async and sync interfaces.
 */

// Constants - these should be available from the keywordsai-sdk or defined here
const BASE_URL_SUFFIX = "/api";
const KEYWORDS_AI_DEFAULT_BASE_URL = "https://api.keywordsai.co";

export interface ClientOptions {
  apiKey?: string;
  baseUrl?: string;
}

export interface RequestOptions {
  params?: Record<string, any>;
  headers?: Record<string, string>;
}

/**
 * Centralized async HTTP client for Keywords AI API
 */
export class KeywordsAIClient {
  private baseUrl: string;
  private headers: Record<string, string>;

  /**
   * Initialize the Keywords AI client
   *
   * @param options - Configuration options
   * @param options.apiKey - Keywords AI API key
   * @param options.baseUrl - Base URL for the API
   */
  constructor(options: ClientOptions = {}) {
    let { apiKey, baseUrl } = options;
    
    if (!baseUrl) {
      // Try to get from environment if available (Node.js environment)
      try {
        baseUrl = (globalThis as any)?.process?.env?.KEYWORDS_AI_BASE_URL || KEYWORDS_AI_DEFAULT_BASE_URL;
      } catch {
        baseUrl = KEYWORDS_AI_DEFAULT_BASE_URL;
      }
    }
    if (!apiKey) {
      // Try to get from environment if available (Node.js environment)
      try {
        apiKey = (globalThis as any)?.process?.env?.KEYWORDSAI_API_KEY || '';
      } catch {
        apiKey = '';
      }
    }
    
    baseUrl = (baseUrl || '').replace(/\/$/, ''); // Remove trailing slash
    if (baseUrl.endsWith(BASE_URL_SUFFIX)) {
      baseUrl = baseUrl.slice(0, -BASE_URL_SUFFIX.length);
    }
    
    this.baseUrl = baseUrl;
    this.headers = {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    };
  }

  /**
   * Make a GET request
   *
   * @param endpoint - API endpoint (without base URL)
   * @param options - Request options
   * @returns Response JSON data
   */
  async get(endpoint: string, options: RequestOptions = {}): Promise<any> {
    const { params, headers } = options;
    const requestHeaders = { ...this.headers, ...headers };

    const url = new URL(`${this.baseUrl}/${endpoint.replace(/^\//, '')}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: requestHeaders,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Make a POST request
   *
   * @param endpoint - API endpoint (without base URL)
   * @param jsonData - JSON data to send
   * @param options - Request options
   * @returns Response JSON data
   */
  async post(endpoint: string, jsonData?: any, options: RequestOptions = {}): Promise<any> {
    const { headers } = options;
    const requestHeaders = { ...this.headers, ...headers };

    const response = await fetch(`${this.baseUrl}/${endpoint.replace(/^\//, '')}`, {
      method: 'POST',
      headers: requestHeaders,
      body: jsonData ? JSON.stringify(jsonData) : undefined,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Make a PATCH request
   *
   * @param endpoint - API endpoint (without base URL)
   * @param jsonData - JSON data to send
   * @param options - Request options
   * @returns Response JSON data
   */
  async patch(endpoint: string, jsonData?: any, options: RequestOptions = {}): Promise<any> {
    const { headers } = options;
    const requestHeaders = { ...this.headers, ...headers };

    const response = await fetch(`${this.baseUrl}/${endpoint.replace(/^\//, '')}`, {
      method: 'PATCH',
      headers: requestHeaders,
      body: jsonData ? JSON.stringify(jsonData) : undefined,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Make a DELETE request
   *
   * @param endpoint - API endpoint (without base URL)
   * @param jsonData - JSON data to send
   * @param options - Request options
   * @returns Response JSON data
   */
  async delete(endpoint: string, jsonData?: any, options: RequestOptions = {}): Promise<any> {
    const { headers } = options;
    const requestHeaders = { ...this.headers, ...headers };

    const response = await fetch(`${this.baseUrl}/${endpoint.replace(/^\//, '')}`, {
      method: 'DELETE',
      headers: requestHeaders,
      body: jsonData ? JSON.stringify(jsonData) : undefined,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }
}

/**
 * Create an async Keywords AI client
 *
 * @param apiKey - Keywords AI API key
 * @param baseUrl - Base URL for the API (default: KEYWORDS_AI_DEFAULT_BASE_URL)
 * @returns KeywordsAIClient instance
 */
export function createClient(apiKey: string, baseUrl?: string): KeywordsAIClient {
  return new KeywordsAIClient({ apiKey, baseUrl });
}
