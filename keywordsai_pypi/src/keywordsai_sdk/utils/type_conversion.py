from keywordsai_sdk.keywordsai_types.param_types import KeywordsAITextLogParams
from keywordsai_sdk.keywordsai_types._internal_types import (
    OpenAIStyledInput,
    OpenAIStyledResponse,
)
from openai.types.chat.chat_completion import ChatCompletion, Choice, ChatCompletionMessage
from openai.types.chat.chat_completion_message import FunctionCall
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from typing import List


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
