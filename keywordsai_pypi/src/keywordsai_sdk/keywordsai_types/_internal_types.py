from pydantic import BaseModel, model_validator, field_validator, ConfigDict
from typing import Any, List, Union, Dict, Optional, Literal
from typing import Literal
from .chat_completion_types import ProviderCredentialType
from pydantic import Field
from typing_extensions import Annotated, TypedDict
from datetime import datetime
from dateparser import parse
from functools import wraps


class KeywordsAIBaseModel(BaseModel):
    def __contains__(self, key):
        # Define custom behavior for the 'in' operator
        return hasattr(self, key)

    def get(self, key, default=None):
        # Custom .get() method to access attributes with a default value if the attribute doesn't exist
        return getattr(self, key, default)

    def __getitem__(self, key):
        # Allow dictionary-style access to attributes
        return getattr(self, key)

    def __setitem__(self, key, value):
        # Allow dictionary-style assignment to attributes
        setattr(self, key, value)

    def _assign_related_field(
        self, related_model_name: str, assign_to_name: str, data: dict
    ):
        related_model_value = data.get(related_model_name)
        if not isinstance(related_model_value, (int, str)):
            return
        data[assign_to_name] = related_model_value


class CacheControl(KeywordsAIBaseModel):
    type: str  # ephemeral


class OpenAIMessage(TypedDict):
    role: str
    content: str
    tool_calls: Optional[List[dict]] = None


class OpenAIStyledInput(TypedDict):
    messages: List[OpenAIMessage] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    n: Optional[int] = None
    timeout: Optional[float] = None
    stream: Optional[bool] = None
    logprobs: Optional[bool] = None
    echo: Optional[bool] = None
    stop: Optional[Union[List[str], str]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    logit_bias: Optional[Dict[str, float]] = None
    tools: Optional[List[dict]] = None
    parallel_tool_calls: Optional[bool] = None
    tool_choice: Optional[Union[Literal["auto", "none", "required"], dict]] = None


class OpenAIStyledResponse(TypedDict):
    id: str
    model: str

    class OpenAIUsage(TypedDict):
        total_tokens: int
        prompt_tokens: int
        completion_tokens: int

    usage: Optional[OpenAIUsage] = None
    object: str

    class OpenAIChoice(TypedDict):
        index: int
        message: OpenAIMessage
        finish_reason: str

    choices: List[OpenAIChoice]
    created: int


class FilterObject(KeywordsAIBaseModel):
    id: str = None
    metric: Union[str, List[str]]
    value: List[Any]
    operator: str = ""
    display_name: Optional[str] = ""
    value_field_type: Optional[str] = None
    from_url: Optional[str] = False

    def model_dump(self, exclude_none: bool = True, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = exclude_none
        return super().model_dump(args, kwargs)


class ImageURL(KeywordsAIBaseModel):
    url: str
    detail: Optional[str] = "auto"

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(args, kwargs)


class ImageContent(KeywordsAIBaseModel):
    type: Literal["image_url"] = "image_url"
    # text: Optional[str] = None
    image_url: Union[ImageURL, str]

    model_config = ConfigDict(extra="allow")


class TextContent(KeywordsAIBaseModel):
    type: Literal["text"] = "text"
    text: str
    cache_control: Optional[CacheControl] = None


class ToolCallFunction(KeywordsAIBaseModel):
    name: str
    arguments: str


class ToolCall(KeywordsAIBaseModel):
    id: str = None
    type: Literal["function"] = "function"
    function: ToolCallFunction


MessageContentType = Annotated[
    Union[ImageContent, TextContent], Field(discriminator="type")
]


class Message(KeywordsAIBaseModel):
    role: Literal["user", "assistant", "system", "tool", "none"]
    content: Union[str, List[Union[MessageContentType, str]], None] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None

    @field_validator("content")
    def validate_content(cls, v):
        if isinstance(v, list) and not v:
            raise ValueError("Empty list not allowed for content")
        return v

    @field_validator("role")
    def validate_role(cls, v):
        valid_values = ["user", "assistant", "system", "tool", "none"]
        if v not in valid_values:
            raise ValueError(f"Invalid role value, must be one of {valid_values}")
        return v

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class Messages(KeywordsAIBaseModel):
    messages: List[Message]

    @field_validator("messages")
    def validate_messages(cls, v):
        if not v:
            raise ValueError("messages cannot be empty")
        return v

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class Properties(KeywordsAIBaseModel):
    type: Union[str, list[str]] = None
    description: Optional[str] = None
    enum: Optional[List[str]] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)

    class Config:
        extra = "allow"


class FunctionParameters(KeywordsAIBaseModel):
    type: Union[str, list[str]] = "object"
    properties: Dict[str, Properties] = None  # Only need when you type is object
    required: List[str] = None

    model_config = ConfigDict(extra="allow")


class Function(KeywordsAIBaseModel):
    name: str
    description: Optional[str | None] = None  # Optional description
    parameters: Optional[dict] = {}  # Optional parameters
    strict: Optional[bool] = None  # Optional strict mode

    def model_dump(self, exclude_none: bool = True, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = exclude_none
        return super().model_dump(*args, **kwargs)


class FunctionTool(KeywordsAIBaseModel):
    type: Literal["function"] = "function"
    function: Function


class CodeInterpreterTool(KeywordsAIBaseModel):
    type: Literal["code_interpreter"] = "code_interpreter"


class FileSearchTool(KeywordsAIBaseModel):
    type: Literal["file_search"] = "file_search"

    class FileSearch(KeywordsAIBaseModel):
        max_num_results: Optional[int] = None

    file_search: FileSearch


class ToolChoiceFunction(KeywordsAIBaseModel):
    name: str

    model_config = ConfigDict(extra="allow")


class ToolChoice(KeywordsAIBaseModel):
    type: str
    function: Optional[ToolChoiceFunction] = None

    model_config = ConfigDict(extra="allow")


class BasicLLMParams(KeywordsAIBaseModel):
    echo: Optional[bool] = None
    frequency_penalty: Optional[float] = None
    logprobs: Optional[bool] = None
    logit_bias: Optional[Dict[str, float]] = None
    messages: List[Message] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    max_completion_tokens: Optional[int] = None
    n: Optional[int] = None
    parallel_tool_calls: Optional[bool] = None
    presence_penalty: Optional[float] = None
    stop: Optional[Union[List[str], str]] = None
    stream: Optional[bool] = None
    stream_options: Optional[dict] = None
    temperature: Optional[float] = None
    timeout: Optional[float] = None
    tools: Optional[List[FunctionTool]] = None
    tool_choice: Optional[Union[Literal["auto", "none", "required"], ToolChoice]] = None
    top_logprobs: Optional[int] = None
    top_p: Optional[float] = None

    def model_dump(self, exclude_none: bool = True, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = exclude_none
        return super().model_dump(*args, **kwargs)

    model_config = ConfigDict(protected_namespaces=())


class PromptParam(KeywordsAIBaseModel):
    prompt_id: Optional[str] = None
    version: Optional[int] = None
    variables: Optional[dict] = None
    echo: Optional[bool] = True
    override: Optional[bool] = False
    override_params: Optional[BasicLLMParams] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class StrictBasicLLMParams(BasicLLMParams):
    messages: List[Message]

    @field_validator("messages")
    def validate_messages(cls, v):
        if not v:
            raise ValueError("messages cannot be empty")
        return v

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class LoadBalanceModel(KeywordsAIBaseModel):
    model: str
    credentials: dict = None
    weight: int

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)

    @field_validator("weight")
    def validate_weight(cls, v):
        if v <= 0:
            raise ValueError("Weight has to be greater than 0")
        return v

    model_config = ConfigDict(protected_namespaces=())


class Span(KeywordsAIBaseModel):
    span_identifier: Union[str, int]
    parent_identifier: Optional[Union[str, int]] = None


class Trace(KeywordsAIBaseModel):
    trace_identifier: Union[str, int]
    span: Span


class LoadBalanceGroup(KeywordsAIBaseModel):
    group_id: str
    models: Optional[List[LoadBalanceModel]] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class PostHogIntegration(KeywordsAIBaseModel):
    posthog_api_key: str
    posthog_base_url: str


class Customer(KeywordsAIBaseModel):
    customer_identifier: Union[str, int, None] = None
    name: Optional[str | None] = None
    email: Optional[str | None] = None
    period_start: Optional[str | datetime] = (
        None  # ISO 8601 formatted date-string YYYY-MM-DD
    )
    period_end: Optional[str | datetime] = (
        None  # ISO 8601 formatted date-string YYYY-MM-DD
    )
    budget_duration: Optional[Literal["daily", "weekly", "monthly", "yearly"]] = None
    period_budget: Optional[float] = None
    markup_percentage: Optional[float] = None  # 20 -> original price * 1.2
    total_budget: Optional[float] = None
    metadata: Optional[dict] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)

    @staticmethod
    def _validate_timestamp(v):
        if isinstance(v, str):
            try:
                value = datetime.fromisoformat(v)
                return value
            except Exception as e:
                try:
                    value = parse(v)
                    return value
                except Exception as e:
                    raise ValueError(
                    "timestamp has to be a valid ISO 8601 formatted date-string YYYY-MM-DD"
                )
        return v

    @field_validator("period_start")
    def validate_period_start(cls, v):
        return cls._validate_timestamp(v)

    @field_validator("period_end")
    def validate_period_end(cls, v):
        return cls._validate_timestamp(v)


class TextModelResponseFormat(KeywordsAIBaseModel):
    type: str
    response_schema: Optional[dict] = None
    json_schema: Optional[dict] = None

    class Config:
        extra = "allow"

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class CacheOptions(KeywordsAIBaseModel):
    cache_by_customer: Optional[bool] = None  # Create cache for each customer_user

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class RetryParams(KeywordsAIBaseModel):
    num_retries: Optional[int] = 3
    retry_after: Optional[float] = 0.2
    retry_enabled: Optional[bool] = True

    @field_validator("retry_after")
    def validate_retry_after(cls, v):
        if v <= 0:
            raise ValueError("retry_after has to be greater than 0")
        return v

    @field_validator("num_retries")
    def validate_num_retries(cls, v):
        if v <= 0:
            raise ValueError("num_retries has to be greater than 0")
        return v

    model_config = ConfigDict(extra="forbid")


class EvaluationExtraParams(TypedDict, total=False):
    retrieved_contexts: Optional[List[str]] = None
    contexts: Optional[List[str]] = None
    ground_truth: Optional[str] = None
    ground_truth_answers: Optional[List[str]] = None
    summary: Optional[str] = None


class EvaluationParams(KeywordsAIBaseModel):
    evaluation_identifier: Union[str, int] = ""
    last_n_messages: Optional[int] = (
        1  # last n messages to consider for evaluation, 0 -> all messages
    )
    extra_params: Optional[EvaluationExtraParams] = (
        {}
    )  # extra params that are needed for the evaluation
    sample_percentage: Optional[float] = (
        None  # percentage of messages that trigger the evaluation, default is defined in organization settings, 0 is disabled, 100 is always.
    )

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class KeywordsAIAPIControlParams(KeywordsAIBaseModel):
    block: Optional[bool] = None

    def model_dump(self, *args, **kwargs):
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class Usage(KeywordsAIBaseModel):
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class KeywordsAIParams(KeywordsAIBaseModel):
    api_key: Optional[str] = None
    blurred: Optional[bool] = None
    cache_enabled: Optional[bool] = None
    cache_hit: Optional[bool] = None
    cache_options: Optional[CacheOptions] = None
    cache_ttl: Optional[int] = None
    cache_bit: Optional[int] = None
    cache_key: Optional[str] = None
    redis_cache_ttl: Optional[int] = None
    cache_request_content: Optional[str] = None
    completion_message: Optional[Message] = None
    completion_messages: Optional[List[Message]] = None
    completion_tokens: Optional[int] = None
    completion_unit_price: Optional[float] = None
    cost: Optional[float] = None
    covered_by: Optional[str] = None
    credential_override: Optional[Dict[str, dict]] = None
    custom_identifier: Optional[Union[str, int]] = None
    customer_credentials: Optional[Dict[str, ProviderCredentialType]] = None
    customer_email: Optional[str] = None
    customer_identifier: Optional[Union[str, int]] = None
    customer_params: Optional[Customer] = None
    delimiter: Optional[str] = "\n\n"
    disable_fallback: Optional[bool] = False
    disable_log: Optional[bool] = False
    environment: Optional[str] = None
    error_bit: Optional[int] = None
    error_message: Optional[str] = None
    evaluation_cost: Optional[float] = None
    evaluation_identifier: Optional[Union[str, int]] = None
    evaluation_params: Optional[EvaluationParams] = None
    exclude_models: Optional[List[str]] = None
    exclude_providers: Optional[List[str]] = None
    fallback_models: Optional[List[str]] = None
    field_name: Optional[str] = "data: "
    for_eval: Optional[bool] = None
    full_request: Optional[dict] = None
    full_response: Optional[dict] = None
    generation_time: Optional[float] = None
    has_tool_calls: Optional[bool] = None
    id: Optional[int] = None
    ip_address: Optional[str] = None
    is_test: Optional[bool] = None
    keywordsai_api_controls: Optional[KeywordsAIAPIControlParams] = None
    keywordsai_params: Optional[dict] = None
    latency: Optional[float] = None
    load_balance_group: Optional[LoadBalanceGroup] = None
    load_balance_models: Optional[List[LoadBalanceModel]] = None
    log_method: Optional[str] = None
    log_type: Optional[str] = None
    metadata: Optional[dict] = None
    mock_response: Optional[str] = None
    model_name_map: Optional[Dict[str, str]] = None
    models: Optional[List[str]] = None
    organization_id: Optional[int] = None  # Organization ID
    organization_key_id: Optional[str] = None  # Organization key ID
    posthog_integration: Optional[PostHogIntegration] = None
    prompt: Optional[PromptParam] = None
    prompt_messages: Optional[List[Message]] = None
    prompt_tokens: Optional[int] = None
    prompt_unit_price: Optional[float] = None
    recommendations: Optional[str] = None
    recommendations_dict: Optional[dict] = None
    request_breakdown: Optional[bool] = False
    response_format: Optional[TextModelResponseFormat] = None
    retry_params: Optional[RetryParams] = None
    status: Optional[str] = None
    status_code: Optional[int] = None
    thread_identifier: Optional[Union[str, int]] = None
    time_to_first_token: Optional[float] = None
    timestamp: Optional[str | datetime] = None
    tokens_per_second: Optional[float] = None
    total_request_tokens: Optional[int] = None
    trace_params: Optional[Trace] = None
    trace_id: Optional[int] = None
    ttft: Optional[float] = None
    unique_id: Optional[str] = None
    usage: Optional[Usage] = None
    used_custom_credential: Optional[bool] = None
    user_id: Optional[int] = None
    warnings: Optional[str] = None
    warnings_dict: Optional[dict] = None

    @model_validator(mode="before")
    @classmethod
    def _preprocess_data(cls, data):
        if isinstance(data, dict):
            pass
        elif hasattr(data, "__dict__"):
            data = data.__dict__
        else:
            raise ValueError("KeywordsAIParams can only be initialized with a dict or an object with a __dict__ attribute")

        _name_mapping = {"time_to_first_token": "ttft", "latency": "generation_time"}
        # Map field names
        for key, value in _name_mapping.items():
            if key in data:
                data[key] = data.pop(key)
            else:
                data[key] = data.get(value)

        # Handle related fields
        for field_name in cls.__annotations__:
            if field_name.endswith("_id"):
                related_model_name = field_name[:-3]  # Remove '_id' from the end
                cls._assign_related_field(related_model_name, field_name, data)

        return data

    @classmethod
    def _assign_related_field(
        cls, related_model_name: str, assign_to_name: str, data: dict
    ):
        related_model_value = data.get(related_model_name)
        if not isinstance(related_model_value, (int, str)):
            return
        data[assign_to_name] = related_model_value

    def model_dump(self, *args, **kwargs):
        # Set exclude_none to True if not explicitly provided
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)

    @field_validator("timestamp")
    def validate_timestamp(cls, v):
        if isinstance(v, str):
            try:
                value = datetime.fromisoformat(v)
                return value
            except Exception as e:
                try:
                    value = parse(v)
                    return value
                except Exception as e:
                    raise ValueError(
                        "timestamp has to be a valid ISO 8601 formatted date-string YYYY-MM-DD"
                )
        return v

    model_config = ConfigDict(protected_namespaces=())


class BasicTextToSpeechParams(KeywordsAIBaseModel):
    model: str
    input: str
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    speed: Optional[float] = 1
    response_format: Optional[str] = "mp3"

    model_config = ConfigDict(protected_namespaces=())


class BasicEmbeddingParams(KeywordsAIBaseModel):
    input: str
    model: str
    encoding_format: Optional[Literal["float", "base64"]] = "float"
    dimensions: Optional[int] = None
    user: Optional[str] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class EmbeddingParams(BasicEmbeddingParams, KeywordsAIParams):
    pass


class TextToSpeechParams(BasicTextToSpeechParams, KeywordsAIParams):
    pass


# Assistant Params
class CodeInterpreterResource(KeywordsAIBaseModel):
    type: Literal["code_interpreter"] = "code_interpreter"
    code: str


class TextResponseChoice(KeywordsAIBaseModel):
    message: Message


class TextFullResponse(KeywordsAIBaseModel):
    choices: List[TextResponseChoice]

    @model_validator(mode="after")
    def validate_choices(cls, values):
        if not values.choices:
            raise ValueError("Choices cannot be empty")
        return values


AssistantToolTypes = Annotated[
    Union[CodeInterpreterTool, FunctionTool, FileSearchTool],
    Field(discriminator="type"),
]


class BasicAssistantParams(KeywordsAIBaseModel):
    model: str
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    tools: Optional[List[AssistantToolTypes]] = None
    tool_resources: Optional[dict] = None  # To complete
    metadata: Optional[dict] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    response_format: Optional[Union[str, dict]] = None  # To complete

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class AssistantParams(BasicAssistantParams, KeywordsAIParams):
    pass


class ThreadMessage(Message):
    attachments: Optional[List[dict]] = None
    metadata: Optional[dict] = None


class BasicThreadParams(KeywordsAIBaseModel):
    messages: Optional[List[ThreadMessage]] = None
    tool_resources: Optional[dict] = None
    metadata: Optional[dict] = None


class ThreadParams(BasicThreadParams, KeywordsAIParams):
    pass


class TruncationStrategy(KeywordsAIBaseModel):
    type: str
    last_messages: Optional[int] = None


class BasicRunParams(KeywordsAIBaseModel):
    assistant_id: str
    model: Optional[str] = None
    instructions: Optional[str] = None
    additional_instructions: Optional[str] = None
    additional_messages: Optional[List[ThreadMessage]] = None
    tools: Optional[List[AssistantToolTypes]] = None
    metadata: Optional[dict] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    stream: Optional[bool] = None
    max_prompt_tokens: Optional[int] = None
    max_completion_tokens: Optional[int] = None
    truncation_strategy: Optional[TruncationStrategy] = None
    tool_choice: Optional[ToolChoice] = None
    parallel_tool_calls: Optional[bool] = None
    response_format: Optional[Union[str, dict]] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class RunParams(BasicRunParams, KeywordsAIParams):
    pass


# End of Assistant Params


import io


class BasicTranscriptionParams(KeywordsAIBaseModel):
    file: io.BytesIO
    model: str
    language: Optional[str] = None
    prompt: Optional[str] = None
    response_format: Optional[Literal["json", "text", "srt", "verbose_json", "vtt"]] = (
        "json"
    )
    temperature: Optional[float] = 0
    timestamp_granularities: Optional[List[Literal["word", "segment"]]] = None
    user: Optional[str] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)

    class Config:
        arbitrary_types_allowed = True


class LLMParams(BasicLLMParams, KeywordsAIParams):
    @model_validator(mode="after")
    @classmethod
    def validate_messages(cls, values):
        """
        Either prompt or messages must be provided
        Returns:
            [type]: [description]
        """
        if not values.prompt and not values.messages:
            raise ValueError("Either prompt or messages must be provided")
        return values


class EnvEnabled(KeywordsAIBaseModel):
    test: Optional[bool] = False
    staging: Optional[bool] = False
    prod: Optional[bool] = False


class AlertSettings(KeywordsAIBaseModel):
    system: Optional[Dict[str, bool]] = None
    api: Optional[Dict[str, EnvEnabled]] = None
    webhook: Optional[Dict[str, EnvEnabled]] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


# ===============anthropic==================


class AnthropicAutoToolChoice(KeywordsAIBaseModel):
    type: Literal["auto"] = "auto"


class AnthropicAnyToolChoice(KeywordsAIBaseModel):
    type: Literal["any"] = "any"


class AnthropicToolChoice(KeywordsAIBaseModel):
    type: Literal["tool"] = "tool"
    name: str


class AnthropicInputSchemaProperty(KeywordsAIBaseModel):
    type: str
    description: str = None

    class Config:
        extra = "allow"

    def model_dump(self, exclude_none=True, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = exclude_none
        return super().model_dump(*args, **kwargs)


class AnthropicInputSchema(KeywordsAIBaseModel):
    type: Literal["object"] = "object"
    properties: Dict[str, AnthropicInputSchemaProperty] = (
        None  # Only need when you type is object
    )
    required: List[str] = None

    class Config:
        extra = "allow"


class AnthropicToolUse(KeywordsAIBaseModel):
    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: dict


class AnthropicTool(KeywordsAIBaseModel):
    name: str
    description: Optional[str | None] = None
    input_schema: dict


class AnthropicToolResult(KeywordsAIBaseModel):
    type: Literal["tool_result"] = "tool_result"
    tool_use_id: str
    content: str


class AnthropicImageContentSrc(KeywordsAIBaseModel):
    type: str
    media_type: str
    data: str


class AnthropicImageContent(KeywordsAIBaseModel):
    type: Literal["image"] = "image"
    source: AnthropicImageContentSrc


class AnthropicTextContent(KeywordsAIBaseModel):
    type: Literal["text"] = "text"
    text: str


AnthropicContentTypes = Annotated[
    Union[
        AnthropicImageContent,
        AnthropicTextContent,
        AnthropicToolUse,
        AnthropicToolResult,
    ],
    Field(discriminator="type"),
]


class AnthropicMessage(KeywordsAIBaseModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: Union[List[AnthropicContentTypes], str, None] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class AnthropicSystemMessage(KeywordsAIBaseModel):
    cache_control: Optional[CacheControl] = None
    type: str  # text
    text: str


class AnthropicParams(KeywordsAIBaseModel):
    model: str
    messages: List[AnthropicMessage]
    max_tokens: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    stop_sequence: Optional[List[str]] = None
    stream: Optional[bool] = None
    system: Optional[Union[str, List[AnthropicSystemMessage]]] = None
    temperature: Optional[float] = None
    tool_choice: Optional[
        Union[AnthropicAutoToolChoice, AnthropicAnyToolChoice, AnthropicToolChoice]
    ] = None
    tools: Optional[List[AnthropicTool]] = None
    top_k: Optional[int] = None
    top_p: Optional[float] = None


class AnthropicTextResponseContent(KeywordsAIBaseModel):
    type: Literal["text"] = "text"
    text: str


class AnthropicToolResponseContent(KeywordsAIBaseModel):
    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: dict


class AnthropicUsage(KeywordsAIBaseModel):
    input_tokens: int = 0
    output_tokens: int = 1


class AnthropicResponse(KeywordsAIBaseModel):
    id: str
    type: Literal["message", "tool_use", "tool_result"]
    content: List[AnthropicTextResponseContent | AnthropicToolResponseContent] = []
    model: str
    stop_reason: Literal["end_turn ", "max_tokens", "stop_sequence", "tool_use"] = (
        "end_turn"
    )
    stop_sequence: Union[str, None] = None
    usage: AnthropicUsage


"""
event: message_start
data: {"type": "message_start", "message": {"id": "msg_id", "type": "message", "role": "assistant", "content": [], "model": "claude-3-opus-20240229", "stop_reason": null, "stop_sequence": null, "usage": {"input_tokens": 25, "output_tokens": 1}}}

event: content_block_start
data: {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}

event: ping
data: {"type": "ping"}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hello"}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "!"}}

event: content_block_stop
data: {"type": "content_block_stop", "index": 0}

event: message_delta
data: {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence":null}, "usage": {"output_tokens": 15}}

event: message_stop
data: {"type": "message_stop"}
"""


class AnthropicStreamDelta(KeywordsAIBaseModel):
    type: Literal["text_delta", "input_json_delta"] = "text_delta"
    text: str | None = None
    partial_json: str | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.partial_json:
            self.type = "input_json_delta"
        elif self.text:
            self.type = "text_delta"
        else:
            self.type = "text_delta"
            self.text = ""

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class AnthropicStreamContentBlock(KeywordsAIBaseModel):
    type: Literal["text"] = "text"
    text: str = ""  # Initialize with an empty string


class AnthropicStreamChunk(KeywordsAIBaseModel):
    """Example chunk:
    {
    "type": "content_block_delta",
    "index": 1,
    "delta": {
        "type": "input_json_delta",
        "partial_json": "{\"location\": \"San Fra"
    }
    }
    """

    type: Literal[
        "message_start",
        "content_block_start",
        "content_block_delta",
        "content_block_stop",
        "message_delta",
        "message_stop",
        "ping",
    ]
    index: Union[int, None] = None
    delta: Union[AnthropicStreamDelta, None] = None
    content_block: Union[AnthropicStreamContentBlock, None] = None
    message: Union[AnthropicResponse, None] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)
