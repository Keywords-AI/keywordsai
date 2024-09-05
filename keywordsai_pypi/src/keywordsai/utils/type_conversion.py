from keywordsai.keywordsai_types.param_types import KeywordsAITextLogParams
from keywordsai.keywordsai_types._interal_types import OpenAIStyledInput, OpenAIStyledResponse
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

def openai_io_to_keywordsai_log(
    openai_input: OpenAIStyledInput, openai_output: OpenAIStyledResponse
):
    kai_params = KeywordsAITextLogParams(
        model = openai_input.get("model", ""),
        prompt_messages=openai_input.get("messages", []),
        completion_message=openai_output["choices"][0]["message"],
    )
    usage = openai_output.get("usage")
    
    if usage:
        kai_params.prompt_tokens = usage.get("prompt_tokens")
        kai_params.completion_tokens = usage.get("completion_tokens")
    
    
    return kai_params.model_dump()
    


