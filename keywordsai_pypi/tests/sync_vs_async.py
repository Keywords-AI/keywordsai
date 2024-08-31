from asyncio import get_event_loop, sleep as async_sleep, run
from time import sleep
from keywordsai.decorators import openai_wrapper

@openai_wrapper
def sync_func(seconds):
    sleep(seconds)
    return f"Sync sleep for {seconds} seconds"

@openai_wrapper
async def async_func(seconds):
    await async_sleep(seconds)
    return f"Async sleep for {seconds} seconds"

sync_func(1)
run(async_func(1))