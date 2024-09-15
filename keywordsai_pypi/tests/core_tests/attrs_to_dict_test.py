attributes = [
    {"key": "llm.request.type", "value": {"string_value": "chat"}},
    {"key": "traceloop.workflow.name", "value": {"string_value": "joke_creation"}},
    {"key": "gen_ai.system", "value": {"string_value": "OpenAI"}},
    {"key": "gen_ai.request.model", "value": {"string_value": "gpt-3.5-turbo"}},
    {"key": "llm.headers", "value": {"string_value": "None"}},
    {"key": "llm.is_streaming", "value": {"bool_value": False}},
    {"key": "gen_ai.openai.api_base", "value": {"string_value": "https://api.openai.com/v1/"}},
    {"key": "gen_ai.prompt.0.role", "value": {"string_value": "user"}},
    {"key": "gen_ai.prompt.0.content", "value": {"string_value": "Tell me a joke about opentelemetry"}},
    {"key": "gen_ai.response.model", "value": {"string_value": "gpt-3.5-turbo-0125"}},
    {"key": "llm.usage.total_tokens", "value": {"int_value": 40}},
    {"key": "gen_ai.usage.completion_tokens", "value": {"int_value": 25}},
    {"key": "gen_ai.usage.prompt_tokens", "value": {"int_value": 15}},
    {"key": "gen_ai.completion.0.finish_reason", "value": {"string_value": "stop"}},
    {"key": "gen_ai.completion.0.role", "value": {"string_value": "assistant"}},
    {"key": "gen_ai.completion.0.content", "value": {"string_value": "Why did the opentelemetry project break up with the logging library? \n\nBecause it couldn't handle all the debug logs!"}},
    {"key": "gen_ai.completion.1", "value": {"int_value": "None"}},
]

from keywordsai_sdk.utils.conversion import convert_attr_list_to_dict
def convert_to_dict_test():
    try:
        data = convert_attr_list_to_dict(attributes)
        assert data["llm"]["request"]["type"] == "chat", data
        print("data: ", data)
    except Exception as e:
        assert False, data

    
if __name__ == "__main__":
    convert_to_dict_test()
        