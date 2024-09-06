from tests.test_env import *
from keywordsai.core import KeywordsAI
from keywordsai.client import KeywordsAIClient
import os

def test_init_kai_instance():
    try:
        kai = KeywordsAI()
        assert isinstance(kai, KeywordsAI)
    except Exception as e:
        assert False, e
        
def test_init_kai_client():
    try:
        kai_client = KeywordsAIClient()
        assert isinstance(kai_client, KeywordsAIClient)
    except Exception as e:
        assert False, e

if __name__ == "__main__":
    kai_client = KeywordsAIClient()
    os.environ["KEYWORDSAI_BASE_URL"] = "random_url"
    kai_client2 = KeywordsAIClient()