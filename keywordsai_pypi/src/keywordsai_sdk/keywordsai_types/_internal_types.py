from typing_extensions import Literal
from pydantic import BaseModel, model_validator, field_validator
from typing import Any, List, Union, Dict, Optional, Literal
from typing import Literal
from .chat_completion_types import ProviderCredentialType
from pydantic import Field
from typing_extensions import Annotated, TypedDict

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


class FilterObject(BaseModel):
    id: str = None
    metric: Union[str, List[str]]
    value: List[Any]
    operator: str = ""
    display_name: Optional[str] = ""
    value_field_type: Optional[str] = None
    from_url: Optional[str] = False

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(args, kwargs)


class ImageURL(BaseModel):
    url: str
    detail: Optional[str] = "auto"

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(args, kwargs)


class ImageContent(BaseModel):
    type: Literal["image_url"] = "image_url"
    # text: Optional[str] = None
    image_url: Union[ImageURL, str]
    
    class Config:
        extra = "allow"


class TextContent(BaseModel):
    type: Literal["text"] = "text"
    text: str


class ToolCallFunction(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    id: str = None
    type: Literal["function"] = "function"
    function: ToolCallFunction


MessageContetentType = Annotated[Union[ImageContent, TextContent], Field(discriminator="type")]
class Message(BaseModel):
    role: Literal["user", "assistant", "system", "tool", "none"]
    # content: Union[str, List[Union[ImageContent, TextContent, str]], None] = None
    content: Union[str, List[Union[MessageContetentType, str]], None] = None
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
            raise ValueError(
                f"Invalid role value, must be one of {valid_values}")
        return v

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class Messages(BaseModel):
    messages: List[Message]

    @field_validator("messages")
    def validate_messages(cls, v):
        if not v:
            raise ValueError("messages cannot be empty")
        return v

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class Properties(BaseModel):
    type: Literal["string", "number", "integer",
                  "boolean", "array", "object"] = None
    description: Optional[str] = None
    enum: Optional[List[str]] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)
    
    class Config:
        extra = "allow"


class FunctionParameters(BaseModel):
    type: Literal["object"] = "object"
    properties: Dict[str, Properties]
    required: List[str] = None
    
    class Config:
        extra = "allow"

class Function(BaseModel):
    name: str
    description: str = None # Optional description
    parameters: FunctionParameters
    strict: Optional[bool] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class FunctionTool(BaseModel):
    type: Literal["function"] = "function"
    function: Function

class CodeInterpreterTool(BaseModel):
    type: Literal["code_interpreter"] = "code_interpreter"


class FileSearchTool(BaseModel):
    type: Literal["file_search"] = "file_search"
    class FileSearch(BaseModel):
        max_num_results: Optional[int] = None
    
    file_search: FileSearch

class ToolChoiceFunction(BaseModel):
    name: str
    class Config:
        extra = "allow"

class ToolChoice(BaseModel):
    type: str
    function: Optional[ToolChoiceFunction] = None

    class Config:
        extra = "allow"
        
class PromptParam(BaseModel):
    prompt_id: Optional[str] = None
    version: Optional[int] = None
    variables: Optional[dict] = None
    echo: Optional[bool] = True

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)
    
class BasicLLMParams(BaseModel):
    messages: List[Message] = None
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
    tools: Optional[List[FunctionTool]] = None
    parallel_tool_calls: Optional[bool] = None
    tool_choice: Optional[Union[Literal["auto", "none", "required"], ToolChoice]] = None
    
    @model_validator(mode="after")
    def validate_messages(cls, values):
        if not values.messages and not values.prompt:
            raise ValueError("Either prompt or messages must be provided") 
        
    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)

    class Config:
        protected_namespaces = ()

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
  
class LoadBalanceModel(BaseModel):
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

    class Config:
        protected_namespaces = ()

class Span(BaseModel):
    span_identifier: str
    parent_identifier: Optional[str] = None

class Trace(BaseModel):
    trace_identifier: str
    span: Span

class LoadBalanceGroup(BaseModel):
    group_id: str
    models: Optional[List[LoadBalanceModel]] = None
    
    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)
class PostHogIntegration(BaseModel):
    posthog_api_key: str
    posthog_base_url: str

class Customer(BaseModel):
    customer_identifier: str
    name: Optional[str] = None
    email: Optional[str] = None
    
    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)

class TextModelResponseFormat(BaseModel):
    type: str
    response_schema: Optional[dict] = None
    json_schema: Optional[dict] = None
    
    class Config:
        extra = "allow"

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)

class CacheOptions(BaseModel):
    cache_by_customer: Optional[bool] = None # Create cache for each customer_user
    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)

class KeywordsAIParams(BaseModel):
    mock_response: Optional[str] = None
    cache_hit: Optional[bool] = None
    cache_enabled: Optional[bool] = None
    cache_ttl: Optional[int] = None
    cache_options: Optional[CacheOptions] = None
    credential_override: Optional[Dict[str, dict]] = None
    customer_params: Optional[Customer] = None
    customer_email: Optional[str] = None
    customer_credentials: Optional[Dict[str, ProviderCredentialType]] = None
    customer_identifier: Optional[Union[str, int]] = None
    delimiter: Optional[str] = "---"
    disable_fallback: Optional[bool] = False
    disable_log: Optional[bool] = False
    exclude_models: Optional[List[str]] = None
    exclude_providers: Optional[List[str]] = None
    evaluation_identifier: Optional[str] = None
    fallback_models: Optional[List[str]] = None
    load_balance_models: Optional[List[LoadBalanceModel]] = None
    load_balance_group: Optional[LoadBalanceGroup] = None
    metadata: Optional[dict] = None
    models: Optional[List[str]] = None
    model_name_map: Optional[Dict[str, str]] = None
    posthog_integration: Optional[PostHogIntegration] = None
    prompt: Optional[PromptParam] = None
    request_breakdown: Optional[bool] = False
    thread_identifier: Optional[Union[str, int]] = None
    fieldname: Optional[str] = ""
    for_eval: Optional[bool] = None
    response_format: Optional[TextModelResponseFormat] = None
    trace_params: Optional[Trace] = None
    # Add any additional validators if required

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)

    class Config:
        protected_namespaces = ()

class KeywordsAIParamsValidation(KeywordsAIParams):
    class Config(KeywordsAIParams.Config):
        extra = "allow"
        
class BasicTextToSpeechParams(BaseModel):
    model: str
    input: str
    voice: Literal["alloy","echo", "fable", "onyx","nova", "shimmer"] 
    speed: Optional[float] = 1
    response_format: Optional[str]="mp3"
    
    class Config:
        protected_namespaces = ()
class BasicEmbeddingParams(BaseModel):
    input: str
    model: str
    encoding_format: Optional[Literal["float","base64"]] = "float"
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
class CodeInterpreterResource(BaseModel):
    type: Literal["code_interpreter"] = "code_interpreter"
    code: str

class TextResponseChoice(BaseModel):
    message: Message
class TextFullResponse(BaseModel):
    choices: List[TextResponseChoice]
    
    @model_validator(mode="after")
    def validate_choices(cls, values):
        if not values.choices:
            raise ValueError("Choices cannot be empty")
        return values
    
    
AssistantToolTypes = Annotated[Union[CodeInterpreterTool, FunctionTool, FileSearchTool], Field(discriminator="type")]
class BasicAssistantParams(BaseModel):
    model: str
    name: Optional[str] = None
    desciprtion: Optional[str] = None
    instructions: Optional[str] = None
    tools: Optional[List[AssistantToolTypes]] = None
    tool_resources: Optional[dict] = None # To complete
    metadata: Optional[dict] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    response_format: Optional[Union[str, dict]] = None # To complete
    
    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)
class AssistantParams(BasicAssistantParams, KeywordsAIParams):
    pass


class ThreadMessage(Message):
    attachments: Optional[List[dict]] = None
    metadata: Optional[dict] = None
class BasicThreadParams(BaseModel):
    messages: Optional[List[ThreadMessage]] = None
    tool_resources: Optional[dict] = None
    metadata: Optional[dict] = None

class ThreadParams(BasicThreadParams, KeywordsAIParams):
    pass

class TruncationStrategy(BaseModel):
    type: str  
    last_messages: Optional[int] = None
class BasicRunParams(BaseModel):
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
class BasicTranscriptionParams(BaseModel):
    file: io.BytesIO
    model: str
    languange: Optional[str] = None
    prompt: Optional[str] = None
    response_format: Optional[Literal["json", "text", "srt", "verbose_json", "vtt"]] = "json"
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

class EanableForEnv(BaseModel):
    test: Optional[bool] = False
    staging: Optional[bool] = False
    prod: Optional[bool] = False


class AlertSettings(BaseModel):
    system: Optional[Dict[str, bool]] = None
    api: Optional[Dict[str, EanableForEnv]] = None
    webhook: Optional[Dict[str, EanableForEnv]] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)






#===============anthropic==================

class AnthropicAutoToolChoice(BaseModel):
    type: Literal["auto"] = "auto"
class AnthropicAnyToolChoie(BaseModel):
    type: Literal["any"] = "any"

class AnthropicToolChoice(BaseModel):
    type: Literal["tool"] = "tool"
    name: str

class AnthropicInputSchemaProperty(BaseModel):
    type: Literal["string", "number", "integer", "boolean", "array", "object"]
    description: str
    
    class Config:
        extra = "allow"


class AnthropicInputSchema(BaseModel):
    type: Literal["object"] = "object"
    properties: Dict[str, AnthropicInputSchemaProperty]
    required: List[str]


class AnthropicToolUse(BaseModel):
    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: Union[str, Dict]


class AnthropicTool(BaseModel):
    name: str
    description: str
    input_schema: AnthropicInputSchema


class AnthropicToolResult(BaseModel):
    type: Literal["tool_result"] = "tool_result"
    tool_use_id: str
    content: str


class AnthropicImageContentSrc(BaseModel):
    type: str
    media_type: str
    data: str


class AnthropicImageContent(BaseModel):
    type: Literal["image"] = "image"
    source: AnthropicImageContentSrc


class AnthropicTextContent(BaseModel):
    type: Literal["text"] = "text"
    text: str



AnthropicContentTypes = Annotated[Union[AnthropicImageContent, AnthropicTextContent, AnthropicToolUse, AnthropicToolResult], Field(discriminator="type")]
class AnthropicMessage(BaseModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: Union[List[AnthropicContentTypes], str, None] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class AnthropicParams(BaseModel):
    model: str
    messages: List[AnthropicMessage]
    max_tokens: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    stop_sequence: Optional[List[str]] = None
    stream: Optional[bool] = None
    system: Optional[str] = None
    temperature: Optional[float] = None
    tool_choice: Optional[Union[AnthropicAutoToolChoice, AnthropicAnyToolChoie, AnthropicToolChoice]] = None
    tools: Optional[List[AnthropicTool]] = None
    top_k: Optional[int] = None
    top_p: Optional[float] = None


class AnthropicTextResponseContent(BaseModel):
    type: Literal["text"] = "text"
    text: str


class AnthropicToolResponseContent(BaseModel):
    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: str


class AnthropicUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 1


class AnthropicResponse(BaseModel):
    id: str
    type: Literal["message", "tool_use", "tool_result"]
    content: List[AnthropicTextResponseContent | AnthropicToolResponseContent] = []
    model: str
    stop_reason: Literal["end_turn ", "max_tokens",
                         "stop_sequence", "tool_use"] = "end_turn"
    stop_sequence: Union[str, None] = None
    usage: AnthropicUsage


"""
event: message_start
data: {"type": "message_start", "message": {"id": "msg_1nZdL29xx5MUA1yADyHTEsnR8uuvGzszyY", "type": "message", "role": "assistant", "content": [], "model": "claude-3-opus-20240229", "stop_reason": null, "stop_sequence": null, "usage": {"input_tokens": 25, "output_tokens": 1}}}

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

class AnthropicStreamDelta(BaseModel):
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

class AnthropicStreamContentBlock(BaseModel):
    type: Literal["text"] = "text"
    text: str = ""  # Initialize with an empty string

class AnthropicStreamChunk(BaseModel):
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
    type: Literal["message_start", "content_block_start", "content_block_delta", "content_block_stop", "message_delta", "message_stop", "ping"]
    index: Union[int, None] = None
    delta: Union[AnthropicStreamDelta, None] = None
    content_block: Union[AnthropicStreamContentBlock, None] = None
    message: Union[AnthropicResponse, None] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


def anthropic_message_to_llm_message(message: AnthropicMessage) -> Message:
    content = message.content
    if isinstance(content, str):
        return Message(role=message.role, content=content)
    elif isinstance(content, list):
        content_list = []
        for item in content:
            if item.type == "text":
                content_list.append(TextContent(type="text", text=item.text))
            elif item.type == "image":
                content_list.append(ImageContent(
                    type="image_url", image_url=ImageURL(url=item.source.data)))
        return Message(role=message.role, content=content_list)
    return Message(role=message.role)

def antropic_messages_to_llm_messages(messages: List[AnthropicMessage]) -> List[Message]:
    messages_to_return = []
    for message in messages:
        content = message.content
        if isinstance(content, str):
            messages_to_return.append(Message(role=message.role, content=content))
        elif isinstance(content, list):
            content_list = []
            tool_calls = []
            for item in content:
                if item.type == "text":
                    content_list.append(TextContent(type="text", text=item.text))
                elif item.type == "image":
                    content_list.append(ImageContent(
                        type="image_url", image_url=ImageURL(url=item.source.data)))
                elif item.type == "tool_use":
                    tool_calls.append(ToolCall(
                        id=item.id, function=ToolCallFunction(name=item.name, arguments=item.input)))
                elif item.type == "tool_result":
                    messages_to_return.append(Message(role="tool", content=item.content, tool_call_id=item.tool_use_id))
            if content_list:
                message = Message(role=message.role, content=content_list)
                if tool_calls:
                    message.tool_calls = tool_calls
                messages_to_return.append(message)
    return messages_to_return


def anthropic_tool_to_llm_tool(tool: AnthropicTool) -> FunctionTool:
    properties = {}
    required = []
    for key, value in tool.input_schema.properties.items():
        properties[key] = Properties(
            type=value.type, description=value.description)
        if key in tool.input_schema.required:
            required.append(key)
    function_parameters = FunctionParameters(
        type="object", properties=properties, required=required)
    function = Function(
        name=tool.name, description=tool.description, parameters=function_parameters)
    return FunctionTool(type="function", function=function)


def anthropic_params_to_llm_params(params: AnthropicParams) -> LLMParams:
    messages = antropic_messages_to_llm_messages(params.messages)  # They have same structure
    tools = None
    tool_choice = None
    keywordsai_params = {}
    if params.tools:
        tools = [anthropic_tool_to_llm_tool(tool) for tool in params.tools]
    if params.tool_choice:
        anthropic_tool_choice = params.tool_choice
        if anthropic_tool_choice.type == "auto":
            tool_choice = "auto"
        elif anthropic_tool_choice.type == "any":
            tool_choice = "required"
        else:   
            tool_choice = ToolChoice(
                type=params.tool_choice.type,
                function=ToolChoiceFunction(name=getattr(params.tool_choice, "name", ""))
            )
    if params.system:
        messages.insert(0, Message(role="system", content=params.system))
    if params.metadata:
        keywordsai_params: dict = params.metadata.pop("keywordsai_params", {})
        metadat_in_keywordsai_params = keywordsai_params.pop(
            "metadata", {})  # To avoid confilc of kwargs
        params.metadata.update(metadat_in_keywordsai_params)
        print(params.metadata)

    llm_params = LLMParams(
        messages=messages,
        model=params.model,
        max_tokens=params.max_tokens,
        temperature=params.temperature,
        stop=params.stop_sequence,
        stream=params.stream,
        tools=tools,
        tool_choice=tool_choice,
        top_k=params.top_k,
        top_p=params.top_p,
        metadata=params.metadata,
        **keywordsai_params
    )
    return llm_params

import json
def anthropic_stream_chunk_to_sse(chunk: AnthropicStreamChunk) -> str:
    first_line = f"event: {chunk.type}\n"
    second_line = f"data: {json.dumps(chunk.model_dump())}\n\n"
    return first_line + second_line