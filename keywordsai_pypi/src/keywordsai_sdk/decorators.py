import time
from functools import wraps
from asyncio import iscoroutinefunction, get_event_loop
from packaging.version import Version
import openai
import types
from keywordsai_sdk.utils.debug_print import debug

def _is_openai_v1():
    return Version(openai.__version__) >= Version("1.0.0")

def _is_streaming_response(response):
    return (
        isinstance(response, types.GeneratorType)
        or isinstance(response, types.AsyncGeneratorType)
        or (_is_openai_v1() and isinstance(response, openai.Stream))
        or (_is_openai_v1() and isinstance(response, openai.AsyncStream))
    )



