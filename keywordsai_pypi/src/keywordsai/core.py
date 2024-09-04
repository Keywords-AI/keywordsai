from threading import Thread
from .utils.debug_print import *
from typing import List, Literal
from .constants import *
from queue import Queue
from threading import Lock
import logging
from os import getenv
from functools import wraps
from asyncio import iscoroutinefunction, get_event_loop
import time
from packaging.version import Version
import openai
import types

class UploadWorker(Thread):
    _queue = Queue()
    state: Literal["running", "paused", "stopped"] = "running"

    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        while self.state == "running":
            data = self._queue.get(block=True)
            if data:
                self._send_to_keywords(data)
                self._queue.task_done()
            
    def _send_to_keywords(self, data):
        print_info(f"Sending data to KeywordsAI: {data}", print_func=logging.info)

class SyncGenerator():
    def __init__(self, generator):
        self.generator = generator
        self.response_collector = []
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

def _openai_wrapper(func, *args, **kwargs):
        if iscoroutinefunction(func):
            @wraps(func)
            async def wrapped_openai(*args, **kwargs):
                loop = get_event_loop()
                start_time = loop.time()
                result =  await func(*args, **kwargs)
                end_time = loop.time()
                debug(print)(f"Function {func.__name__} took {end_time - start_time} seconds")
                return result
        else:    
            @wraps(func)
            def wrapped_openai(*args, **kwargs):
                start_time = time.time()
                result =  func(*args, **kwargs)
                end_time = time.time()
                is_stream = _is_streaming_response(func)
                ttft = None
                if is_stream:
                    print(f"Function {func.__name__} is a streaming response")
                    ttft = end_time - start_time
                    return 
                else:
                    latency = end_time - start_time 
                debug(print)(f"Function {func.__name__} took {end_time - start_time} seconds")
                return result
        
        return wrapped_openai

class KeywordsAI:
    _workers: List[UploadWorker] = []
    _lock = Lock()
    _singleton = getenv("KEYWORDS_AI_IS_SINGLETON", "True") == "True"

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
        print_info(f"Singleton model {cls._singleton}", logging.debug)
        if not hasattr(cls, "_instance"):
            with cls._lock:
                cls._instance = super(KeywordsAI, cls).__new__(cls)
        else:
            if cls._singleton and cls._instance:
                print_info("Singleton instance already exists", logging.debug)
                return cls._instance
            else:
                cls._instance = super(KeywordsAI, cls).__new__(cls)
        
        return cls._instance

    def __init__(self) -> None:
        for _ in range(KEYWORDSAI_NUM_THREADS):
            self._workers.append(UploadWorker())

        
    def initialize(self):
        for worker in self._workers:
            worker.start()

    def upload(self, data):
        for worker in self._workers:
            worker._queue.put(data)
            
    def keywordsai_log(self, func, type=LogType.TEXT_LLM, **wrapper_kwargs):
        
        if type == KeywordsAI.LogType.TEXT_LLM:
            def wrapper(*args, **kwargs):
                print_info(f"Calling {func.__name__} with args {args} and kwargs {kwargs}", logging.info)
                openai_func = _openai_wrapper(func)
                return openai_func(*args, **kwargs)
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

        return wrapper