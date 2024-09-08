from tests.test_env import *
from keywordsai_sdk import KeywordsAI
from keywordsai_sdk.client import KeywordsAIClient
import keywordsai_sdk.keywordsai_config as config

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
    config.KEYWORDSAI_BASE_URL = "some_url"
    kai_client2 = KeywordsAIClient()