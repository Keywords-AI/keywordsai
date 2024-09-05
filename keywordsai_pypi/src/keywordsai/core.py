from .utils.debug_print import *
from .constants import *
from threading import Lock
import logging
from os import getenv
from functools import wraps
from asyncio import iscoroutinefunction, get_event_loop
import time
from packaging.version import Version
import openai
import types
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai.types.chat.chat_completion import ChatCompletion
from collections.abc import Generator
from .task_queue import KeywordsAITaskQueue



class SyncGenerator:

    _keywordsai = None
    def __init__(self, generator: Generator[ChatCompletionChunk, None, None], keywordsai: "KeywordsAI" = None, extra_data={}):
        self.generator = generator
        self.response_collector = []
        self._keywordsai = keywordsai
        self.extra_data = extra_data

    def __iter__(self):
        try:
            for chunk in self.generator:
                self.response_collector.append(chunk)
                yield chunk
        finally:
            self._on_finish()

    def __enter__(self):
        return self.__iter__()

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def _on_finish(self):
        data = {"collecion": self.response_collector}
        data.update(self.extra_data)
        if self._keywordsai:
            self._keywordsai._log(data)
        return self.response_collector


def _is_openai_v1():
    return Version(openai.__version__) >= Version("1.0.0")


def _is_streaming_response(response):
    return (
        isinstance(response, types.GeneratorType)
        or isinstance(response, types.AsyncGeneratorType)
        or (_is_openai_v1() and isinstance(response, openai.Stream))
        or (_is_openai_v1() and isinstance(response, openai.AsyncStream))
    )




class KeywordsAI:
    _lock = Lock()
    _singleton = getenv("KEYWORDS_AI_IS_SINGLETON", "True") == "True"
    _instance = None

    class LogType:
        """
        Log types for KeywordsAI
        TEXT_LLM: Text-based language model (chat endpoint, text endpoint)
        AUDIO_LLM: Audio-based language model (audio endpoint)
        EMBEDDING_LLM: Embedding-based language model (embedding endpoint)
        GENERAL_FUNCTION: General function, any input (in json serailizable format), any output (in json serializable format)
        """

        TEXT_LLM = "TEXT_LLM"
        AUDIO_LLM = "AUDIO_LLM"
        EMBEDDING_LLM = "EMBEDDING_LLM"
        GENERAL_FUNCTION = "GENERAL_FUNCTION"

    @classmethod
    def set_singleton(cls, value: bool):
        cls._singleton = value

    def __new__(cls):
        print_info(f"Singleton model {cls._singleton}", debug_print)
        if cls._singleton:
            if not cls._instance:
                with cls._lock:
                    cls._instance = super(KeywordsAI, cls).__new__(cls)
            return cls._instance
        else:
            return super(KeywordsAI, cls).__new__(cls)
        

    def __init__(self) -> None:
        self._task_queue = KeywordsAITaskQueue() 
        self._task_queue.initialize()
            
    def _log(self, data):
        self._task_queue.add_task(data)
        
    def _openai_wrapper(self, func, *args, **kwargs):
        if iscoroutinefunction(func):

            @wraps(func)
            async def wrapped_openai(*args, **kwargs):
                loop = get_event_loop()
                start_time = loop.time()
                result = await func(*args, **kwargs)
                end_time = loop.time()
                return result
        else:
            @wraps(func)
            def wrapped_openai(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                is_stream = _is_streaming_response(result)
                ttft = None
                if is_stream:
                    ttft = end_time - start_time
                    result: Generator[ChatCompletionChunk, None, None]
                    return SyncGenerator(result, self, extra_data={"ttft": ttft})
                else:
                    latency = end_time - start_time
                    result: ChatCompletion
                    data = { **result.model_dump(), "latency": latency }
                    self._log(data=data)
                return result

        return wrapped_openai

    def logging_wrapper(self, func, type=LogType.TEXT_LLM, **wrapper_kwargs):
        if type == KeywordsAI.LogType.TEXT_LLM and func:
            def wrapper(*args, **kwargs):
                openai_func = self._openai_wrapper(func)
                result = openai_func(*args, **kwargs)
                return result
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

        return wrapper
