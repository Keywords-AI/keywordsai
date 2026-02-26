"""Respan Gateway Generator for Haystack pipelines."""

from typing import Any, Callable, Dict, List, Optional

import requests
from haystack import component, default_from_dict, default_to_dict, logging
from haystack.dataclasses import ChatMessage

from respan_exporter_haystack.utils.chat_utils import (
    extract_response_text,
    to_chat_message,
    to_request_message,
)
from respan_exporter_haystack.utils.config_utils import (
    build_chat_completions_endpoint,
    resolve_api_key,
    resolve_base_url,
)

logger = logging.getLogger(__name__)


@component
class RespanGenerator:
    """
    A Haystack Generator component that routes LLM calls through Respan gateway.
    
    This replaces OpenAIGenerator and routes all calls through Respan for:
    - Automatic logging
    - Fallbacks and retries
    - Load balancing
    - Cost optimization
    - Prompt management (use platform-managed prompts)
    - All Respan platform features
    
    Example usage:
        ```python
        from respan_exporter_haystack.gateway import RespanGenerator
        
        # Basic usage
        generator = RespanGenerator(
            model="gpt-4o-mini",
            api_key="your-respan-api-key"
        )
        result = generator.run(messages=[{"role": "user", "content": "Hello!"}])
        
        # With platform-managed prompts
        generator = RespanGenerator(
            model="gpt-4o-mini",
            prompt_id="042f5f",  # Prompt from Respan platform
            api_key="your-respan-api-key"
        )
        result = generator.run(prompt_variables={"customer_name": "John"})
        ```
    
    Args:
        model: Model name (e.g., "gpt-4o-mini", "gpt-4"). Optional if using prompt_id.
        api_key: Respan API key (defaults to RESPAN_API_KEY env var)
        base_url: Respan API base URL (defaults to https://api.respan.ai)
        prompt_id: Optional prompt ID from Respan platform for prompt management
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
        streaming_callback: Optional[Callable[..., None]] = None,
    ):
        """Initialize the Respan gateway generator."""
        self.model = model
        self.api_key = resolve_api_key(api_key=api_key)
        self.base_url = resolve_base_url(base_url=base_url)
        self.prompt_id = prompt_id
        self.generation_kwargs = generation_kwargs or {}
        self.streaming_callback = streaming_callback
        
        if not self.api_key:
            raise ValueError(
                "Respan API key is required. Set RESPAN_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        if not self.model and not self.prompt_id:
            raise ValueError(
                "Either 'model' or 'prompt_id' must be provided. "
                "Use 'model' for direct model calls, or 'prompt_id' to use platform-managed prompts."
            )
        
        self.endpoint = build_chat_completions_endpoint(base_url=self.base_url)

    @component.output_types(replies=List[str], meta=List[Dict[str, Any]])
    def run(
        self,
        prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        generation_kwargs: Optional[Dict[str, Any]] = None,
        prompt_variables: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate text using Respan gateway.
        
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
            logger.debug(f"Calling Respan gateway with model {self.model}")
            
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
            replies = [
                extract_response_text(content=choice.get("message", {}).get("content"))
                for choice in choices
            ]
            
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
                    "cost": data.get("cost"),  # Respan provides cost
                })
            
            logger.debug(f"Successfully generated {len(replies)} replies")
            
            return {
                "replies": replies,
                "meta": meta,
            }
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error from Respan: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except requests.exceptions.Timeout:
            error_msg = "Request to Respan timed out"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Error calling Respan gateway: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize component to dictionary."""
        return default_to_dict(
            obj=self,
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            prompt_id=self.prompt_id,
            generation_kwargs=self.generation_kwargs,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RespanGenerator":
        """Deserialize component from dictionary."""
        return default_from_dict(cls=cls, data=data)


@component
class RespanChatGenerator:
    """
    Respan Chat Generator for Haystack pipelines.
    
    Similar to RespanGenerator but with chat-specific features.
    Use this when you want ChatMessage support and chat-specific parameters.
    
    Example:
        ```python
        from haystack.dataclasses import ChatMessage
        from respan_exporter_haystack.gateway import RespanChatGenerator
        
        generator = RespanChatGenerator(
            model="gpt-4",
            api_key="your-respan-api-key"
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
        self.api_key = resolve_api_key(api_key=api_key)
        self.base_url = resolve_base_url(base_url=base_url)
        self.generation_kwargs = generation_kwargs or {}
        
        if not self.api_key:
            raise ValueError(
                "Respan API key is required. Set RESPAN_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.endpoint = build_chat_completions_endpoint(base_url=self.base_url)

    @component.output_types(replies=List[ChatMessage], meta=List[Dict[str, Any]])
    def run(
        self,
        messages: List[ChatMessage],
        generation_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate chat responses using Respan gateway.
        
        Args:
            messages: List of ChatMessage objects
            generation_kwargs: Additional generation parameters
            
        Returns:
            Dictionary with:
                - replies: List of ChatMessage objects
                - meta: List of metadata dicts
        """
        # Convert ChatMessage to dict format
        messages_dict = [
            to_request_message(message=msg)
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
            logger.debug(f"Calling Respan gateway with model {self.model}")
            
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
                msg_data = choice.get("message", {})
                replies.append(to_chat_message(message_payload=msg_data))
            
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
            error_msg = f"Error calling Respan gateway: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize component to dictionary."""
        return default_to_dict(
            obj=self,
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            generation_kwargs=self.generation_kwargs,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RespanChatGenerator":
        """Deserialize component from dictionary."""
        return default_from_dict(cls=cls, data=data)
