import time
from functools import wraps
from asyncio import iscoroutinefunction, get_event_loop

def openai_wrapper(func, *args, **kwargs):
    if iscoroutinefunction(func):
        @wraps(func)
        async def wrapped_openai(*args, **kwargs):
            loop = get_event_loop()
            start_time = loop.time()
            result =  await func(*args, **kwargs)
            end_time = loop.time()
            print(f"Function {func.__name__} took {end_time - start_time} seconds")
            return result
    else:    
        @wraps(func)
        def wrapped_openai(*args, **kwargs):
            start_time = time.time()
            result =  func(*args, **kwargs)
            end_time = time.time()
            print(f"Function {func.__name__} took {end_time - start_time} seconds")
            return result
    
    return wrapped_openai

