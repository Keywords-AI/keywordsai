import inspect
from openai import AsyncOpenAI
def detector(func):
    return inspect.iscoroutinefunction(func)

# Test cases
async def some_func():
    return "ss"

def some_sync_func():
    return "ss"

client = AsyncOpenAI()
# Testing the detector function
print(detector(some_func))      # Output: True
print(detector(some_sync_func)) # Output: False
print(detector(client.chat.completions.create)) # Output: True
print(client.chat.completions.create.__name__) # Output: True