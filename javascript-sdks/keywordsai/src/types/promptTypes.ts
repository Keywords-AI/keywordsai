/**
 * Prompt Type Definitions for Keywords AI SDK
 *
 * This module provides comprehensive type definitions for prompt operations in Keywords AI.
 * All types provide validation, serialization, and clear structure for API interactions.
 *
 * 🏗️ CORE TYPES:
 *
 * Prompt: Complete prompt information returned by the API
 * PromptVersion: Prompt version information with configuration details
 * PromptCreateResponse: Response type for prompt creation
 * PromptListResponse: Paginated list of prompts
 * PromptRetrieveResponse: Response type for prompt retrieval
 * PromptVersionCreateResponse: Response type for prompt version creation
 * PromptVersionListResponse: Paginated list of prompt versions
 * PromptVersionRetrieveResponse: Response type for prompt version retrieval
 *
 * 💡 USAGE PATTERNS:
 *
 * 1. CREATING PROMPTS:
 *    Use Prompt to create new prompts with basic information like name and description.
 *
 * 2. MANAGING VERSIONS:
 *    Use PromptVersion to create and manage different versions of prompts with
 *    specific configurations, messages, and model parameters.
 *
 * 3. LISTING PROMPTS:
 *    PromptListResponse provides paginated results with navigation metadata.
 *
 * 4. VERSION MANAGEMENT:
 *    PromptVersionListResponse provides paginated results for prompt versions.
 *
 * 📖 EXAMPLES:
 *
 * Basic prompt creation:
 *    ```typescript
 *    import { Prompt } from './promptTypes.js';
 *    
 *    // Create a basic prompt
 *    const prompt: Prompt = {
 *      name: "Customer Support Assistant",
 *      description: "AI assistant for customer support queries",
 *      prompt_id: "cust-support-001"
 *    };
 *    ```
 *
 * Prompt version with configuration:
 *    ```typescript
 *    import { PromptVersion } from './promptTypes.js';
 *    
 *    // Create a prompt version with specific configuration
 *    const version: PromptVersion = {
 *      prompt_version_id: "version-001",
 *      description: "Initial version with basic configuration",
 *      created_at: new Date(),
 *      updated_at: new Date(),
 *      version: 1,
 *      messages: [
 *        { role: "system", content: "You are a helpful customer support assistant." },
 *        { role: "user", content: "How can I help you today?" }
 *      ],
 *      model: "gpt-4o-mini",
 *      temperature: 0.7,
 *      max_tokens: 2048
 *    };
 *    ```
 *
 * 🔧 FIELD REFERENCE:
 *
 * Prompt Fields:
 * - id (number|string, optional): Unique identifier
 * - name (string): Human-readable prompt name
 * - description (string): Detailed description of prompt purpose
 * - prompt_id (string): Unique prompt identifier
 * - prompt_slug (string, optional): URL-friendly slug
 * - current_version (PromptVersion, optional): Current active version
 * - live_version (PromptVersion, optional): Live/published version
 * - prompt_versions (PromptVersion[], optional): All versions
 * - commit_count (number): Number of commits/versions
 * - starred (boolean): Whether prompt is starred
 * - tags (object[]): Associated tags
 *
 * PromptVersion Fields:
 * - id (number|string, optional): Unique identifier
 * - prompt_version_id (string): Unique version identifier
 * - description (string, optional): Version description
 * - created_at (Date): Creation timestamp
 * - updated_at (Date): Last update timestamp
 * - version (number): Version number
 * - messages (Message[]): Conversation messages
 * - model (string): AI model to use (default: "gpt-3.5-turbo")
 * - temperature (number): Model temperature (0.0-2.0)
 * - max_tokens (number): Maximum tokens to generate
 * - top_p (number): Nucleus sampling parameter
 * - frequency_penalty (number): Frequency penalty (-2.0 to 2.0)
 * - presence_penalty (number): Presence penalty (-2.0 to 2.0)
 * - reasoning_effort (string, optional): Reasoning effort level
 * - variables (object): Template variables
 * - readonly (boolean): Whether version is read-only
 * - fallback_models (string[], optional): Fallback model list
 * - tools (object[], optional): Available tools
 * - tool_choice (string|object, optional): Tool choice strategy
 * - response_format (object, optional): Response format specification
 *
 * ⚠️ IMPORTANT NOTES:
 * - All datetime fields should be timezone-aware
 * - Model parameters affect AI behavior and costs
 * - Messages follow OpenAI chat format
 * - Variables enable prompt templating
 * - Tools enable function calling capabilities
 */

// Re-export all prompt types from keywordsai-sdk
export type {
  Prompt,
  PromptVersion,
  PromptCreateResponse,
  PromptListResponse,
  PromptRetrieveResponse,
  PromptVersionCreateResponse,
  PromptVersionListResponse,
  PromptVersionRetrieveResponse,
} from "@keywordsai/keywordsai-sdk";
