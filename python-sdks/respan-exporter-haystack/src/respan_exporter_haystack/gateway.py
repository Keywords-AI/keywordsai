"""Keywords AI Gateway Generator for Haystack pipelines."""

import os
from typing import Any, Dict, List, Optional, Union
from haystack import component, default_from_dict, default_to_dict, logging
from haystack.dataclasses import StreamingChunk

import requests

logger = logging.getLogger(__name__)


@component
class RespanGenerator:
    """
    A Haystack Generator component that routes LLM calls through Keywords AI gateway.
    
    This replaces OpenAIGenerator and routes all calls through Keywords AI for:
    - Automatic logging
    - Fallbacks and retries
    - Load balancing
    - Cost optimization
    - Prompt management (use platform-managed prompts)
    - All Keywords AI platform features
    
    Example usage:
        ```python
        from respan_exporter_haystack import RespanGenerator
        
        # Basic usage
        generator = RespanGenerator(
            model="gpt-4o-mini",
            api_key="your-keywords-ai-key"
        )
        result = generator.run(messages=[{"role": "user", "content": "Hello!"}])
        
        # With platform-managed prompts
        generator = RespanGenerator(
            model="gpt-4o-mini",
            prompt_id="042f5f",  # Prompt from Keywords AI platform
            api_key="your-keywords-ai-key"
        )
        result = generator.run(prompt_variables={"customer_name": "John"})
        ```
    
    Args:
        model: Model name (e.g., "gpt-4o-mini", "gpt-4"). Optional if using prompt_id.
        api_key: Keywords AI API key (defaults to RESPAN_API_KEY env var)
        base_url: Keywords AI API base URL (defaults to https://api.respan.ai)
        prompt_id: Optional prompt ID from Keywords AI platform for prompt management
        generation_kwargs: Additional parameters (temperature, max_tokens, etc.)
        streaming_callback: Optional callback for streaming responses
    """

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        prompt_id: Optional[str] = None,
        generation_kwargs: Optional[Dict[str, Any]] = None,
        streaming_callback: Optional[callable] = None,
    ):
        """Initialize the Keywords AI gateway generator."""
        self.model = model
        self.api_key = api_key or os.getenv("RESPAN_API_KEY")
        self.base_url = base_url or os.getenv(
            "RESPAN_BASE_URL", "https://api.respan.ai"
        )
        self.prompt_id = prompt_id
        self.generation_kwargs = generation_kwargs or {}
        self.streaming_callback = streaming_callback
        
        if not self.api_key:
            raise ValueError(
                "Keywords AI API key is required. Set RESPAN_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        if not self.model and not self.prompt_id:
            raise ValueError(
                "Either 'model' or 'prompt_id' must be provided. "
                "Use 'model' for direct model calls, or 'prompt_id' to use platform-managed prompts."
            )
        
        # Build endpoint - handle if base_url already has /api
        base = self.base_url.rstrip('/')
        if base.endswith('/api'):
            self.endpoint = f"{base}/chat/completions"
        else:
            self.endpoint = f"{base}/api/chat/completions"

    @component.output_types(replies=List[str], meta=List[Dict[str, Any]])
    def run(
        self,
        prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        generation_kwargs: Optional[Dict[str, Any]] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate text using Keywords AI gateway.
        
        Args:
            prompt: Simple prompt string (will be converted to user message)
            messages: List of message dicts with 'role' and 'content'
            generation_kwargs: Additional generation parameters (overrides init kwargs)
            prompt_variables: Variables for platform-managed prompt (requires prompt_id in init)
            
        Returns:
            Dictionary with:
                - replies: List of generated texts
                - meta: List of metadata dicts (model, tokens, cost, etc.)
        """
        # Handle prompt management mode
        if self.prompt_id:
            # Using platform-managed prompt
            # Messages are placeholder when using prompts
            messages = [{"role": "user", "content": "placeholder"}]
        else:
            # Convert prompt to messages format if provided
            if prompt is not None:
                messages = [{"role": "user", "content": prompt}]
            elif messages is None:
                raise ValueError("Either 'prompt' or 'messages' must be provided")
        # Merge generation kwargs
        kwargs = {**self.generation_kwargs, **(generation_kwargs or {})}
        
        # Build the request payload
        payload = {
            "messages": messages,
            **kwargs,
        }
        
        # Add model if provided (optional when using prompt_id)
        if self.model:
            payload["model"] = self.model
        
        # Add prompt management if prompt_id is set
        if self.prompt_id:
            prompt_config = {
                "prompt_id": self.prompt_id,
                "override": True,  # Use prompt config from platform
            }
            if prompt_variables:
                prompt_config["variables"] = prompt_variables
            payload["prompt"] = prompt_config
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            logger.debug(f"Calling Keywords AI gateway with model {self.model}")
            
            response = requests.post(
                url=self.endpoint,
                headers=headers,
                json=payload,
                timeout=60,
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract replies and metadata
            choices = data.get("choices", [])
            replies = [choice["message"]["content"] for choice in choices]
            
            # Build metadata
            meta = []
            usage = data.get("usage", {})
            
            for i, choice in enumerate(choices):
                meta.append({
                    "model": data.get("model", self.model),
                    "index": i,
                    "finish_reason": choice.get("finish_reason"),
                    "usage": usage,
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                    "cost": data.get("cost"),  # Keywords AI provides cost
                })
            
            logger.debug(f"Successfully generated {len(replies)} replies")
            
            return {
                "replies": replies,
                "meta": meta,
            }
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error from Keywords AI: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except requests.exceptions.Timeout:
            error_msg = "Request to Keywords AI timed out"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Error calling Keywords AI gateway: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize component to dictionary."""
        return default_to_dict(
            self,
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            prompt_id=self.prompt_id,
            generation_kwargs=self.generation_kwargs,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RespanGenerator":
        """Deserialize component from dictionary."""
        return default_from_dict(cls, data)


@component
class RespanChatGenerator:
    """
    Keywords AI Chat Generator for Haystack pipelines.
    
    Similar to RespanGenerator but with chat-specific features.
    Use this when you want ChatMessage support and chat-specific parameters.
    
    Example:
        ```python
        from haystack.dataclasses import ChatMessage
        from respan_exporter_haystack import RespanChatGenerator
        
        generator = RespanChatGenerator(
            model="gpt-4",
            api_key="your-keywords-ai-key"
        )
        
        messages = [
            ChatMessage.from_system("You are helpful"),
            ChatMessage.from_user("Hello!")
        ]
        
        result = generator.run(messages=messages)
        ```
    """

    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        generation_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the chat generator."""
        self.model = model
        self.api_key = api_key or os.getenv("RESPAN_API_KEY")
        self.base_url = base_url or os.getenv(
            "RESPAN_BASE_URL", "https://api.respan.ai"
        )
        self.generation_kwargs = generation_kwargs or {}
        
        if not self.api_key:
            raise ValueError(
                "Keywords AI API key is required. Set RESPAN_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Build endpoint - handle if base_url already has /api
        base = self.base_url.rstrip('/')
        if base.endswith('/api'):
            self.endpoint = f"{base}/chat/completions"
        else:
            self.endpoint = f"{base}/api/chat/completions"

    @component.output_types(replies=List["ChatMessage"], meta=List[Dict[str, Any]])
    def run(
        self,
        messages: List["ChatMessage"],
        generation_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate chat responses using Keywords AI gateway.
        
        Args:
            messages: List of ChatMessage objects
            generation_kwargs: Additional generation parameters
            
        Returns:
            Dictionary with:
                - replies: List of ChatMessage objects
                - meta: List of metadata dicts
        """
        from haystack.dataclasses import ChatMessage, ChatRole
        
        # Convert ChatMessage to dict format
        messages_dict = [
            {"role": msg.role.value, "content": msg.text if hasattr(msg, "text") else msg.content}
            for msg in messages
        ]
        
        # Merge generation kwargs
        kwargs = {**self.generation_kwargs, **(generation_kwargs or {})}
        
        # Build payload
        payload = {
            "model": self.model,
            "messages": messages_dict,
            **kwargs,
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            logger.debug(f"Calling Keywords AI gateway with model {self.model}")
            
            response = requests.post(
                url=self.endpoint,
                headers=headers,
                json=payload,
                timeout=60,
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract replies and convert back to ChatMessage
            choices = data.get("choices", [])
            replies = []
            
            for choice in choices:
                msg_data = choice["message"]
                role = ChatRole(msg_data["role"])
                content = msg_data["content"]
                replies.append(ChatMessage(role=role, content=content))
            
            # Build metadata
            meta = []
            usage = data.get("usage", {})
            
            for i, choice in enumerate(choices):
                meta.append({
                    "model": data.get("model", self.model),
                    "index": i,
                    "finish_reason": choice.get("finish_reason"),
                    "usage": usage,
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                    "cost": data.get("cost"),
                })
            
            logger.debug(f"Successfully generated {len(replies)} replies")
            
            return {
                "replies": replies,
                "meta": meta,
            }
            
        except Exception as e:
            error_msg = f"Error calling Keywords AI gateway: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize component to dictionary."""
        return default_to_dict(
            self,
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            generation_kwargs=self.generation_kwargs,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RespanChatGenerator":
        """Deserialize component from dictionary."""
        return default_from_dict(cls, data)
