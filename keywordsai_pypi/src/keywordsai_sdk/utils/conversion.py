from typing import Any, List
import json


def set_value_by_path(d: dict, path: str, value: Any) -> dict:
    """
    Set a value in a nested dictionary using a dotted path.
    """
    path_keys = path.split(".")
    for i, key in enumerate(path_keys[:-1]):
        if key.isdigit():
            key = int(key)
            if not isinstance(d, list):
                d = []
            while len(d) <= key:
                d.append({})
            d = d[key]
        else:
            if key not in d:
                d[key] = {} if not path_keys[i + 1].isdigit() else []
            d = d[key]

    last_key = path_keys[-1]
    if last_key.isdigit():
        last_key = int(last_key)
        if not isinstance(d, list):
            d = []
        while len(d) <= last_key:
            d.append(None)
    d[last_key] = value


def get_value_by_path(data: dict, path: str) -> Any:
    """
    Get a value in a nested dictionary using a dotted path.
    """
    keys = path.split(".")
    for key in keys:
        if key.isdigit():
            key = int(key)
            if isinstance(data, list):
                while len(data) <= key:
                    data.append({})
                data = data[key]
        else:
            if key not in data:
                return None
            data = data[key]
    return data


def delete_value_by_path(data: dict, path: str) -> dict:
    """
    Delete a value in a nested dictionary using a dotted path.
    """
    keys = path.split(".")
    for key in keys[:-1]:
        if key.isdigit():
            key = int(key)
            if isinstance(data, list):
                while len(data) <= key:
                    data.append({})
                data = data[key]
        else:
            if key not in data:
                return data
            data = data[key]
    del data[keys[-1]]
    return data


def convert_attr_list_to_dict(attrs: list[dict]) -> dict:
    """
    OpenTelemetry attributes are stored as a list of dictionaries. This function converts the list to a nested dictionary.
    Input:
    [
        {"key": "a.0", "value": {"int_value": 1} },
        {"key": "b.c", "value": {"int_value": 2} },
        {"key": "d", "value": {"int_value": 3} },
    ]
    Output:
    {
        "a": [1],
        "b": {"c": 2},
        "d": 3,
    """
    result = {}
    try:
        for item in attrs:
            key = item["key"]
            value = next(iter(item["value"].values()))
            set_value_by_path(result, key, value)
        return result
    except Exception as e:
        raise Exception(f"Error converting attributes to dictionary: {e}")


# ===============================LLM types================================
from keywordsai_sdk.keywordsai_types._internal_types import (
    AnthropicMessage,
    AnthropicParams,
    AnthropicTool,
    AnthropicStreamChunk,
    Message,
    TextContent,
    ImageContent,
    ImageURL,
    ToolCall,
    ToolCallFunction,
    ToolChoice,
    ToolChoiceFunction,
    FunctionTool,
    FunctionParameters,
    Function,
    LLMParams,
    Properties,
    AnthropicResponse,
    AnthropicTextResponseContent,
    AnthropicToolResponseContent,
    AnthropicUsage,
    AnthropicStreamDelta,
    AnthropicStreamContentBlock,
)
from openai.types.chat.chat_completion import ChatCompletion as ModelResponse


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
                content_list.append(
                    ImageContent(
                        type="image_url", image_url=ImageURL(url=item.source.data)
                    )
                )
        return Message(role=message.role, content=content_list)
    return Message(role=message.role)


def anthropic_messages_to_llm_messages(
    messages: List[AnthropicMessage],
) -> List[Message]:
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
                    content_list.append(
                        ImageContent(
                            type="image_url", image_url=ImageURL(url=item.source.data)
                        )
                    )
                elif item.type == "tool_use":
                    tool_calls.append(
                        ToolCall(
                            id=item.id,
                            function=ToolCallFunction(
                                name=item.name, arguments=item.input
                            ),
                        )
                    )
                elif item.type == "tool_result":
                    messages_to_return.append(
                        Message(
                            role="tool",
                            content=item.content,
                            tool_call_id=item.tool_use_id,
                        )
                    )
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
        properties[key] = Properties(type=value.type, description=value.description)
        if key in tool.input_schema.required:
            required.append(key)
    function_parameters = FunctionParameters(
        type="object", properties=properties, required=required
    )
    function = Function(
        name=tool.name, description=tool.description, parameters=function_parameters
    )
    return FunctionTool(type="function", function=function)


def anthropic_params_to_llm_params(params: AnthropicParams) -> LLMParams:
    messages = anthropic_messages_to_llm_messages(
        params.messages
    )  # They have same structure
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
                function=ToolChoiceFunction(
                    name=getattr(params.tool_choice, "name", "")
                ),
            )
    if params.system:
        messages.insert(0, Message(role="system", content=params.system))
    if params.metadata:
        keywordsai_params: dict = params.metadata.pop("keywordsai_params", {})
        metadata_in_keywordsai_params = keywordsai_params.pop(
            "metadata", {}
        )  # To avoid conflict of kwargs
        params.metadata.update(metadata_in_keywordsai_params)
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
        **keywordsai_params,
    )
    return llm_params


def openai_response_to_anthropic_response(response: ModelResponse) -> AnthropicResponse:
    """example response
    {
      "id": "chatcmpl-123",
      "object": "chat.completion",
      "created": 1677652288,
      "model": "gpt-3.5-turbo-0125",
      "system_fingerprint": "fp_44709d6fcb",
      "choices": [{
        "index": 0,
        "message": {
          "role": "assistant",
          "content": "\n\nHello there, how may I assist you today?",
        },
        "logprobs": null,
        "finish_reason": "stop"
      }],
      "usage": {
        "prompt_tokens": 9,
        "completion_tokens": 12,
        "total_tokens": 21
      }
    }
    """
    anthropic_content = []
    for choice in response.choices:
        content = choice.message.content
        tool_calls: List[ToolCall] = getattr(choice.message, "tool_calls", None)
        if isinstance(content, str):
            if content:
                anthropic_content.append(
                    AnthropicTextResponseContent(type="text", text=content)
                )
        else:
            anthropic_content.append(AnthropicTextResponseContent(text=str(content)))

        if tool_calls:
            for tool_call in tool_calls:
                function = tool_call.function
                input_json = {}
                try:
                    input_json = json.loads(function.arguments)
                except Exception as e:
                    pass
                anthropic_content.append(
                    AnthropicToolResponseContent(
                        id=tool_call.id, name=function.name, input=input_json
                    )
                )

    usage = response.usage
    anthropic_usage = None
    if usage:
        anthropic_usage = AnthropicUsage(
            input_tokens=usage.prompt_tokens, output_tokens=usage.completion_tokens
        )
    else:
        anthropic_usage = AnthropicUsage(input_tokens=0, output_tokens=0)

    finish_reason_dict = {
        "stop": "stop_sequence",
        "length": "max_tokens",
        "tool_calls": "tool_use",
    }
    stop_reason = finish_reason_dict.get(
        str(response.choices[0].finish_reason), "end_turn"
    )
    return AnthropicResponse(
        id=response.id,
        type="message",
        role="assistant",
        content=anthropic_content,
        model=response.model,
        stop_reason=stop_reason,
        stop_sequence=None,
        usage=anthropic_usage,
    )


def openai_stream_chunk_to_anthropic_stream_chunk(
    chunk: ModelResponse, type="content_block_delta"
) -> AnthropicStreamChunk:
    """example openai chunk
    {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1694268190,"model":"gpt-3.5-turbo-0125", "system_fingerprint": "fp_44709d6fcb", "choices":[{"index":0,"delta":{"role":"assistant","content":""},"logprobs":null,"finish_reason":null}]}
    """
    if type == "content_block_delta":
        tool_calls: List[ToolCall] = chunk.choices[0].delta.tool_calls
        partial_json = None
        if tool_calls:
            partial_json = tool_calls[0].function.arguments
        return AnthropicStreamChunk(
            type="content_block_delta",
            index=chunk.choices[0].index,
            delta=AnthropicStreamDelta(
                text=chunk.choices[0].delta.content, partial_json=partial_json
            ),
        )
    elif type == "content_block_start":
        return AnthropicStreamChunk(
            type="content_block_start", content_block=AnthropicStreamContentBlock()
        )
    elif type == "content_block_stop":
        return AnthropicStreamChunk(
            type="content_block_stop", index=chunk.choices[0].index
        )
    elif type == "message_delta":
        return AnthropicStreamChunk(
            type="message_delta", message=openai_response_to_anthropic_response(chunk)
        )
    elif type == "message_stop":
        return AnthropicStreamChunk(type="message_stop")
    elif type == "message_start":
        return AnthropicStreamChunk(
            type="message_start", message=openai_response_to_anthropic_response(chunk)
        )
    elif type == "ping":
        return AnthropicStreamChunk(type="ping")
    return AnthropicStreamChunk()


def anthropic_stream_chunk_to_sse(chunk: AnthropicStreamChunk) -> str:
    first_line = f"event: {chunk.type}\n"
    second_line = f"data: {json.dumps(chunk.model_dump())}\n\n"
    return first_line + second_line


# ===============================End of LLM types================================
