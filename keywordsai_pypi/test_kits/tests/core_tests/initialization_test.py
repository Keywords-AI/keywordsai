from tests.test_env import *
from keywordsai.core import KeywordsAI

def test_init():
    kai = KeywordsAI()
    assert kai is not None
    return kai

import time
start = time.time()
kai = test_init()
end = time.time()
print(f"Time taken: {end - start}")
