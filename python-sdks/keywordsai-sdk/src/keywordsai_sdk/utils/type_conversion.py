from keywordsai_sdk.keywordsai_types.param_types import KeywordsAITextLogParams
from keywordsai_sdk.keywordsai_types._internal_types import (
    OpenAIStyledInput,
)
from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from typing import List
from typing import List
import json
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
    Function,
    AnthropicResponse,
    AnthropicTextResponseContent,
    AnthropicToolResponseContent,
    AnthropicUsage,
    AnthropicStreamDelta,
    AnthropicStreamContentBlock,
)
from keywordsai_sdk.keywordsai_types.param_types import LLMParams
from openai.types.chat.chat_completion import ChatCompletion as ModelResponse


# region: ===============================LLM types================================
def openai_stream_chunks_to_openai_io(
    stream_chunks: List[ChatCompletionChunk],
) -> ChatCompletion:
    first_chunk = stream_chunks[0]
    response_content = ""
    tool_call_arg_string = ""
    model = first_chunk.model
    role = first_chunk.choices[0].delta.role
    last_chunk = stream_chunks[-1]
    finish_reason = ""
    for chunk in stream_chunks:
        if chunk.choices:
            choice = chunk.choices[0]
            if choice.delta.content:
                response_content += str(choice.delta.content)
            if choice.delta.tool_calls:
                tool_call_arg_string += str(
                    choice.delta.tool_calls[0].function.arguments
                )
            if choice.finish_reason:
               finish_reason = choice.finish_reason 

    constructed_choice = {
        "message": {
            "role": role,
            "content": response_content,
        },
        "finish_reason": finish_reason,
        "index": 0,
    }
    if tool_call_arg_string:
        constructed_choice["tool_calls"] = [{
            "function": {
                "arguments": tool_call_arg_string,
                "name": first_chunk.choices[0].delta.tool_calls[0].function.name,
            }
        }]

    data = {
        "id": first_chunk.id,
        "choices": [Choice(**constructed_choice)],
        "created": first_chunk.created,
        "model": model,
        "object": "chat.completion",
        "usage": last_chunk.usage
    }
    completion_obj = ChatCompletion(
        **data
    )
    return completion_obj


def openai_io_to_keywordsai_log(
    openai_input: OpenAIStyledInput, openai_output: ChatCompletion
):
    extra_body = openai_input.pop("extra_body", {}) or {}
    kai_params = KeywordsAITextLogParams(
        prompt_messages=openai_input.pop("messages", []),
        completion_message=openai_output.choices[0].message.model_dump(),
        full_request=openai_input,
        **openai_input,
        **extra_body
    )
    usage = openai_output.usage

    if usage:
        kai_params.prompt_tokens = usage.prompt_tokens
        kai_params.completion_tokens = usage.completion_tokens
    

    return kai_params.model_dump()


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
                    content_list.append(TextContent(**item.model_dump()))
                elif item.type == "image":
                    content_list.append(
                        ImageContent(
                            type="image_url",
                            image_url=ImageURL(
                                url=f"data:{item.source.media_type};{item.source.type},{item.source.data}"
                            ),
                        )
                    )
                elif item.type == "tool_use":
                    arguments = json.dumps(item.input)
                    tool_calls.append(
                        ToolCall(
                            id=item.id,
                            function=ToolCallFunction(
                                name=item.name, arguments=arguments
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
    if tool.input_schema:
        input_schema = tool.input_schema.copy()
    else:
        input_schema = {}
    extra_fields = tool.model_dump(
        exclude={"name", "description", "input_schema", "type"}, exclude_none=True
    )
    input_schema.update(extra_fields)
    function = Function(
        name=tool.name, description=tool.description, parameters=input_schema
    )
    return FunctionTool(type=tool.type, function=function)


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
        if isinstance(params.system, list):
            content_list = []
            for system_message in params.system:
                if system_message.cache_control:
                    content = TextContent(**system_message.model_dump())
                else:
                    content = TextContent(text=system_message.text)
                content_list.append(content)
            messages.insert(0, Message(role="system", content=content_list))
        else:
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

    anthropic_usage = None
    usage = response.usage
    usage_dict = usage.model_dump()
    if usage:
        anthropic_usage = AnthropicUsage(
            input_tokens=usage_dict.get("prompt_tokens", 0),
            output_tokens=usage_dict.get("completion_tokens", 0),
            cache_creation_input_tokens=usage_dict.get("cache_creation_input_tokens", 0),
            cache_read_input_tokens=usage_dict.get("prompt_tokens_details", {}).get("cached_tokens", 0),
        )
    else:
        anthropic_usage = AnthropicUsage(input_tokens=0, output_tokens=0, cache_creation_input_tokens=0, cache_creation_output_tokens=0)

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


# endregion: ===============================End of LLM types================================
