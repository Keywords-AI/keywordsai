from tests.test_env import *
from keywordsai.core import KeywordsAI, SyncGenerator

def test_generation():
    kai = KeywordsAI()
    wrapped_creation = kai.logging_wrapper(kai_local_client.chat.completions.create)
    response = wrapped_creation(model=test_model, messages=test_messages, stream=True)
    assert response is not None
    return response
    
if __name__ == "__main__":
    print("Running test_generation()...")   
    generator: SyncGenerator = test_generation()
    for chunk in generator:
        content = chunk.choices[0].delta.content
        print(content, end="")