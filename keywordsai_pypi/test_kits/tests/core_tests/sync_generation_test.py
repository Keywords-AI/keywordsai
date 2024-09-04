from tests.test_env import *
from keywordsai.core import KeywordsAI

def test_generation():
    kai = KeywordsAI()
    wrapped_creation = kai.keywordsai_log(kai_local_client.chat.completions.create)
    response = wrapped_creation(model=test_model, messages=test_messages)
    assert response is not None

    
if __name__ == "__main__":
    print("Running test_generation()...")   
    test_generation()