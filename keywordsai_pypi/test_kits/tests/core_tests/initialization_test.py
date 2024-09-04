import os

os.environ["KEYWORDS_AI_IS_SINGLETON"] = "False"
from keywordsai.core import KeywordsAI
from tests.test_env import *

def test_init():
    kai = KeywordsAI()
    assert kai is not None




