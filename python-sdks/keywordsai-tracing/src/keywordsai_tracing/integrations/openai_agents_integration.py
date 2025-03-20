try:
    from agents.tracing.processors import BatchTraceProcessor, BackendSpanExporter
    from agents.tracing.traces import Trace
    from agents.tracing.spans import SpanImpl, Span
    from agents.tracing.span_data import (
        ResponseSpanData,
        FunctionSpanData,
        GenerationSpanData,
        HandoffSpanData,
        CustomSpanData,
        AgentSpanData,
        GuardrailSpanData,
    )
    import httpx

    AGENTS_AVAILABLE = True
except ImportError:
    raise ImportError(
        "OpenAI agents integration requires additional dependencies. "
        "Please install them with: pip install 'keywordsai-tracing[openai-agents]'"
    )


from typing import Any, Dict, Optional, Union
from keywordsai_sdk.keywordsai_types.param_types import KeywordsAITextLogParams
from keywordsai_sdk.keywordsai_types._internal_types import Message
from openai.types.responses.response_output_item import (
    ResponseOutputMessage,
    ResponseFunctionToolCall,
    ResponseFunctionWebSearch,
    ResponseFileSearchToolCall,
)
from openai.types.responses.response_input_item_param import (
    ResponseFunctionToolCallParam,
    FunctionCallOutput,
)
import random
import time
import logging

logger = logging.getLogger(__name__)


# Internal helper functions for converting span data to KeywordsAI log format
def _response_data_to_keywordsai_log(
    data: KeywordsAITextLogParams, span_data: ResponseSpanData
) -> KeywordsAITextLogParams:
    """
    Convert ResponseSpanData to KeywordsAI log format.

    Args:
        data: Base data dictionary with trace and span information
        span_data: The ResponseSpanData to convert

    Returns:
        Dictionary with ResponseSpanData fields mapped to KeywordsAI log format
    """
    data.span_name = span_data.type # response
    data.log_type = "text" # The corresponding keywordsai log type
    try:
        # Extract prompt messages from input if available
        if span_data.input:
            if isinstance(span_data.input, list):
                # Handle list of messages
                for item in span_data.input:
                    try:
                        data.prompt_messages = data.prompt_messages or []
                        data.prompt_messages.append(Message.model_validate(dict(item)))
                    except Exception as e:
                        if isinstance(item, dict):
                            item_type = item.get("type")
                            if item_type == "function_call" or item_type == "function_call_output":
                                data.tool_calls = data.tool_calls or []
                                data.tool_calls.append(item)
                            elif item_type == "user":
                                data.output = "" + str(item)
                        elif isinstance(item, ResponseFunctionToolCallParam):
                            data.tools = data.tools or []
                            data.tools.append(item.model_dump())
                        elif isinstance(item, ResponseFileSearchToolCall):
                            data.tool_calls = data.tool_calls or []
                            data.tool_calls.append(item.model_dump())
                        else:
                            logger.warning(f"Failed to convert item to Message: {e}, type: {item}")
                            data.output = "" + str(item)
            elif isinstance(span_data.input, str):
                # Handle string input (convert to a single user message)
                data.input = span_data.input

        # If response object exists, extract additional data
        if span_data.response:
            response = span_data.response
            # Extract usage information if available
            if hasattr(response, "usage") and response.usage:
                usage = span_data.response.usage
                data.prompt_tokens = usage.input_tokens
                data.completion_tokens = usage.output_tokens
                data.total_request_tokens = usage.total_tokens


            # Extract model information if available
            if hasattr(response, "model"):
                data.model = response.model

            # Extract completion message from response
            if hasattr(response, "output") and response.output:
                response_items = response.output
                for item in response_items:
                    if isinstance(item, dict):
                        item_type = item.get("type")
                        if item_type == "file_search_call":
                            data.tool_calls = data.tool_calls or []
                            data.tool_calls.append(item)
                        elif item_type == "web_search_call":
                            data.tool_calls = data.tool_calls or []
                            data.tool_calls.append(item)
                        else:
                            data.output = "" + str(item)
                    elif isinstance(item, ResponseOutputMessage):
                        data.completion_messages = data.completion_messages or []
                        data.completion_messages.append(
                            Message.model_validate(item.model_dump())
                        )
                        if data.completion_messages and not data.completion_message:
                            data.completion_message = data.completion_messages[0]
                    elif isinstance(item, ResponseFunctionToolCall):
                        data.tool_calls = data.tool_calls or []
                        data.tool_calls.append(item.model_dump())
                    elif isinstance(item, ResponseFunctionWebSearch):
                        data.tool_calls = data.tool_calls or []
                        data.tool_calls.append(item.model_dump())
                    elif isinstance(item, ResponseFileSearchToolCall):
                        data.tool_calls = data.tool_calls or []
                        data.tool_calls.append(item.model_dump())
                    else:
                        data.output = "" + str(item.model_dump())

            # Add full response for logging
            data.full_response = response.model_dump(mode="json")
    except Exception as e:
        logger.error(f"Error converting response data to KeywordsAI log: {e}")


def _function_data_to_keywordsai_log(
    data: KeywordsAITextLogParams, span_data: FunctionSpanData
) -> KeywordsAITextLogParams:
    """
    Convert FunctionSpanData to KeywordsAI log format.

    Args:
        data: Base data dictionary with trace and span information
        span_data: The FunctionSpanData to convert

    Returns:
        Dictionary with FunctionSpanData fields mapped to KeywordsAI log format
    """
    try:
        data.span_name = span_data.name
        data.log_type = "function" # The corresponding keywordsai log type
        data.input = span_data.input
        data.output = span_data.output
        data.span_tools = [span_data.name]

        # Try to extract tool calls if the input is in a format that might contain them
        if span_data.input:
            data.log_type = "tool"
            data.input = span_data.input
    except Exception as e:
        logger.error(f"Error converting function data to KeywordsAI log: {e}")


def _generation_data_to_keywordsai_log(
    data: KeywordsAITextLogParams, span_data: GenerationSpanData
) -> KeywordsAITextLogParams:
    """
    Convert GenerationSpanData to KeywordsAI log format.

    Args:
        data: Base data dictionary with trace and span information
        span_data: The GenerationSpanData to convert

    Returns:
        Dictionary with GenerationSpanData fields mapped to KeywordsAI log format
    """
    data.span_name = span_data.type # generation
    data.log_type = "generation"
    data.model = span_data.model

    try:
        # Extract prompt messages from input if available
        if span_data.input:
            # Try to extract messages from input
            data.input = str(span_data.input)

        # Extract completion message from output if available
        if span_data.output:
            # Try to extract completion from output
            data.output = str(span_data.output)

        # Add model configuration if available
        if span_data.model_config:
            # Extract common LLM parameters from model_config
            for param in [
                "temperature",
                "max_tokens",
                "top_p",
                "frequency_penalty",
                "presence_penalty",
            ]:
                if param in span_data.model_config:
                    data[param] = span_data.model_config[param]

        # Add usage information if available
        if span_data.usage:
            data.prompt_tokens = span_data.usage.get("prompt_tokens")
            data.completion_tokens = span_data.usage.get("completion_tokens")
            data.total_request_tokens = span_data.usage.get("total_tokens")
    except Exception as e:
        logger.error(f"Error converting generation data to KeywordsAI log: {e}")


def _handoff_data_to_keywordsai_log(
    data: KeywordsAITextLogParams, span_data: HandoffSpanData
) -> KeywordsAITextLogParams:
    """
    Convert HandoffSpanData to KeywordsAI log format.

    Args:
        data: Base data dictionary with trace and span information
        span_data: The HandoffSpanData to convert

    Returns:
        Dictionary with HandoffSpanData fields mapped to KeywordsAI log format
    """
    data.span_name = span_data.type # handoff
    data.log_type = "handoff" # The corresponding keywordsai log type
    data.span_handoffs = [f"{span_data.from_agent} -> {span_data.to_agent}"]
    data.metadata = {
        "from_agent": span_data.from_agent,
        "to_agent": span_data.to_agent,
    }


def _custom_data_to_keywordsai_log(
    data: KeywordsAITextLogParams, span_data: CustomSpanData
) -> KeywordsAITextLogParams:
    """
    Convert CustomSpanData to KeywordsAI log format.

    Args:
        data: Base data dictionary with trace and span information
        span_data: The CustomSpanData to convert

    Returns:
        Dictionary with CustomSpanData fields mapped to KeywordsAI log format
    """
    data.span_name = span_data.name
    data.log_type = "custom" # The corresponding keywordsai log type
    data.metadata = span_data.data

    # If the custom data contains specific fields that map to KeywordsAI fields, extract them
    for key in ["input", "output", "model", "prompt_tokens", "completion_tokens"]:
        if key in span_data.data:
            data[key] = span_data.data[key]

    return data


def _agent_data_to_keywordsai_log(
    data: KeywordsAITextLogParams, span_data: AgentSpanData
) -> KeywordsAITextLogParams:
    """
    Convert AgentSpanData to KeywordsAI log format.

    Args:
        data: Base data dictionary with trace and span information
        span_data: The AgentSpanData to convert

    Returns:
        Dictionary with AgentSpanData fields mapped to KeywordsAI log format
    """
    data.span_name = span_data.name
    data.log_type = "agent" # The corresponding keywordsai log type
    data.span_workflow_name = span_data.name

    # Add tools if available
    if span_data.tools:
        data.span_tools = span_data.tools

    # Add handoffs if available
    if span_data.handoffs:
        data.span_handoffs = span_data.handoffs

    # Add metadata with agent information
    data.metadata = {
        "output_type": span_data.output_type,
        "agent_name": span_data.name,
    }

    # Add agent name to metadata
    data.metadata["agent_name"] = span_data.name

    # Add tools to metadata if available
    if span_data.tools:
        data.span_tools = span_data.tools

    # Add handoffs to metadata if available
    if span_data.handoffs:
        data.span_handoffs = span_data.handoffs

    # Set metadata in log data
    data.metadata = data.metadata

    return data


def _guardrail_data_to_keywordsai_log(
    data: KeywordsAITextLogParams, span_data: GuardrailSpanData
) -> KeywordsAITextLogParams:
    """
    Convert GuardrailSpanData to KeywordsAI log format.

    Args:
        data: Base data dictionary with trace and span information
        span_data: The GuardrailSpanData to convert

    Returns:
        Dictionary with GuardrailSpanData fields mapped to KeywordsAI log format
    """
    data.span_name = f"guardrail:{span_data.name}"
    data.log_type = "guardrail" # The corresponding keywordsai log type
    data.has_warnings = span_data.triggered
    if span_data.triggered:
        data.warnings_dict = data.warnings_dict or {}
        data.warnings_dict =  {
            f"guardrail:{span_data.name}": "guardrail triggered"
        }

    return data


class KeywordsAISpanExporter(BackendSpanExporter):
    """
    Custom exporter for Keywords AI that handles all span types and allows for dynamic endpoint configuration.
    """

    def __init__(
        self,
        api_key: Union[str, None] = None,
        organization: Union[str, None] = None,
        project: Union[str, None] = None,
        endpoint: str = "https://api.keywordsai.co/api/",
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
    ):
        """
        Initialize the Keywords AI exporter.

        Args:
            api_key: The API key for authentication. Defaults to os.environ["OPENAI_API_KEY"] if not provided.
            organization: The organization ID. Defaults to os.environ["OPENAI_ORG_ID"] if not provided.
            project: The project ID. Defaults to os.environ["OPENAI_PROJECT_ID"] if not provided.
            endpoint: The HTTP endpoint to which traces/spans are posted.
            max_retries: Maximum number of retries upon failures.
            base_delay: Base delay (in seconds) for the first backoff.
            max_delay: Maximum delay (in seconds) for backoff growth.
        """
        super().__init__(
            api_key=api_key,
            organization=organization,
            project=project,
            endpoint=endpoint,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

    def set_endpoint(self, endpoint: str) -> None:
        """
        Dynamically change the endpoint URL.

        Args:
            endpoint: The new endpoint URL to use for exporting spans.
        """
        self.endpoint = endpoint
        logger.info(f"Keywords AI exporter endpoint changed to: {endpoint}")

    def _keywordsai_export(
        self, item: Union[Trace, Span[Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Process different span types and extract all JSON serializable attributes.

        Args:
            item: A Trace or Span object to export.

        Returns:
            A dictionary with all the JSON serializable attributes of the span,
            or None if the item cannot be exported.
        """
        # First try the native export method
        if isinstance(item, Trace):
            # This one is going to be the root trace. The span id will be the trace id
            return KeywordsAITextLogParams(
                trace_unique_id=item.trace_id,
                span_unique_id=item.trace_id,
                span_name=item.name,
                log_type="agent"
            ).model_dump(mode="json")
        elif isinstance(item, SpanImpl):
            # Get the span ID - it could be named span_id or id depending on the implementation
            parent_id = item.parent_id
            if not parent_id:
                parent_id = item.trace_id

            # Create the base data dictionary with common fields
            data = KeywordsAITextLogParams(
                trace_unique_id=item.trace_id,
                span_unique_id=item.span_id,
                span_parent_id=parent_id,
                start_time=item.started_at,
                timestamp=item.ended_at,
                error_bit=1 if item.error else 0,
                status_code=400 if item.error else 200,
                error_message=str(item.error) if item.error else None,
            )
            data.latency = (data.timestamp - data.start_time).total_seconds()
            # Process the span data based on its type
            try:
                if isinstance(item.span_data, ResponseSpanData):
                    _response_data_to_keywordsai_log(data, item.span_data)
                elif isinstance(item.span_data, FunctionSpanData):
                    _function_data_to_keywordsai_log(data, item.span_data)
                elif isinstance(item.span_data, GenerationSpanData):
                    _generation_data_to_keywordsai_log(data, item.span_data)
                elif isinstance(item.span_data, HandoffSpanData):
                    _handoff_data_to_keywordsai_log(data, item.span_data)
                elif isinstance(item.span_data, CustomSpanData):
                    _custom_data_to_keywordsai_log(data, item.span_data)
                elif isinstance(item.span_data, AgentSpanData):
                    _agent_data_to_keywordsai_log(data, item.span_data)
                elif isinstance(item.span_data, GuardrailSpanData):
                    _guardrail_data_to_keywordsai_log(data, item.span_data)
                else:
                    logger.warning(f"Unknown span data type: {item.span_data}")
                    return None
                return data.model_dump(mode="json")
            except Exception as e:
                logger.error(
                    f"Error converting span data of {item.span_data} to KeywordsAI log: {e}"
                )
                return None
        else:
            return None

    def export(self, items: list[Union[Trace, Span[Any]]]) -> None:
        """
        Export traces and spans to the Keywords AI backend.

        Args:
            items: List of Trace or Span objects to export.
        """
        if not items:
            return

        if not self.api_key:
            logger.warning("API key is not set, skipping trace export")
            return

        # Process each item with our custom exporter
        data = [self._keywordsai_export(item) for item in items]
        # Filter out None values
        data = [item for item in data if item]

        if not data:
            return

        payload = {"data": data}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "traces=v1",
        }

        # Exponential backoff loop
        attempt = 0
        delay = self.base_delay
        while True:
            attempt += 1
            try:
                response = self._client.post(
                    url=self.endpoint, headers=headers, json=payload
                )

                # If the response is successful, break out of the loop
                if response.status_code < 300:
                    logger.debug(f"Exported {len(data)} items to Keywords AI")
                    return

                # If the response is a client error (4xx), we won't retry
                if 400 <= response.status_code < 500:
                    logger.error(
                        f"Keywords AI client error {response.status_code}: {response.text}"
                    )
                    return

                # For 5xx or other unexpected codes, treat it as transient and retry
                logger.warning(f"Server error {response.status_code}, retrying.")
            except httpx.RequestError as exc:
                # Network or other I/O error, we'll retry
                logger.warning(f"Request failed: {exc}")

            # If we reach here, we need to retry or give up
            if attempt >= self.max_retries:
                logger.error("Max retries reached, giving up on this batch.")
                return

            # Exponential backoff + jitter
            sleep_time = delay + random.uniform(0, 0.1 * delay)  # 10% jitter
            time.sleep(sleep_time)
            delay = min(delay * 2, self.max_delay)


class KeywordsAITraceProcessor(BatchTraceProcessor):
    """
    A processor that uses KeywordsAISpanExporter to send traces and spans to Keywords AI.
    """

    def __init__(
        self,
        api_key: Union[str, None] = None,
        organization: Union[str, None] = None,
        project: Union[str, None] = None,
        endpoint: str = "https://api.keywordsai.co/api/openai/v1/traces/ingest",
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        max_queue_size: int = 8192,
        max_batch_size: int = 128,
        schedule_delay: float = 5.0,
        export_trigger_ratio: float = 0.7,
    ):
        """
        Initialize the Keywords AI processor.

        Args:
            api_key: The API key for authentication.
            organization: The organization ID.
            project: The project ID.
            endpoint: The HTTP endpoint to which traces/spans are posted.
            max_retries: Maximum number of retries upon failures.
            base_delay: Base delay (in seconds) for the first backoff.
            max_delay: Maximum delay (in seconds) for backoff growth.
            max_queue_size: The maximum number of spans to store in the queue.
            max_batch_size: The maximum number of spans to export in a single batch.
            schedule_delay: The delay between checks for new spans to export.
            export_trigger_ratio: The ratio of the queue size at which we will trigger an export.
        """

        # Create the exporter
        exporter = KeywordsAISpanExporter(
            api_key=api_key,
            organization=organization,
            project=project,
            endpoint=endpoint,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )

        # Initialize the BatchTraceProcessor with our exporter
        super().__init__(
            exporter=exporter,
            max_queue_size=max_queue_size,
            max_batch_size=max_batch_size,
            schedule_delay=schedule_delay,
            export_trigger_ratio=export_trigger_ratio,
        )

        # Store the exporter for easy access
        self._keywords_exporter = exporter

    def set_endpoint(self, endpoint: str) -> None:
        """
        Dynamically change the endpoint URL.

        Args:
            endpoint: The new endpoint URL to use for exporting spans.
        """
        self._keywords_exporter.set_endpoint(endpoint)
