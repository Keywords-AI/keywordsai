from .keywordsai_config import *
from functools import wraps
from os import getenv
from .task_queue import KeywordsAITaskQueue
from threading import Lock
from .utils.debug_print import *
from keywordsai_sdk.integrations.openai import (
    sync_openai_wrapper,
    async_openai_wrapper,
)
from traceloop.sdk import Traceloop


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
        GENERAL_FUNCTION: General function, any input (in json serializable format), any output (in json serializable format)
        """

        TEXT_LLM = "TEXT_LLM"
        AUDIO_LLM = "AUDIO_LLM"
        EMBEDDING_LLM = "EMBEDDING_LLM"
        GENERAL_FUNCTION = "GENERAL_FUNCTION"

    @classmethod
    def flush(cls):
        if cls._instance:
            cls._instance._task_queue.flush()

    @classmethod
    def set_singleton(cls, value: bool):
        cls._singleton = value

    def __new__(cls):
        print_info(f"Singleton mode: {cls._singleton}", debug_print)
        if cls._singleton:
            if not cls._instance:
                with cls._lock:
                    cls._instance = super(KeywordsAI, cls).__new__(cls)
            return cls._instance
        else:
            return super(KeywordsAI, cls).__new__(cls)

    def __init__(self) -> None:
        Traceloop.init(
            app_name="keywordsai",
            api_endpoint=KEYWORDSAI_BASE_URL,
            api_key=KEYWORDSAI_API_KEY,
            
        )
        self._task_queue = KeywordsAITaskQueue()
    

    def _log(self, data):
        self._task_queue.add_task(data)

    def _openai_wrapper(
        self, func, keywordsai_params, *args, **kwargs
    ):
        return sync_openai_wrapper(
            func=func, keywordsai=self, keywordsai_params=keywordsai_params
        )

    def _async_openai_wrapper(
        self, func, keywordsai_params, *args, **kwargs
    ):
        return async_openai_wrapper(
            func=func, keywordsai=self, keywordsai_params=keywordsai_params
        )

    def logging_wrapper(
        self,
        func,
        type=LogType.TEXT_LLM,
        keywordsai_params = {},
        **wrapper_kwargs,
    ):
        if type == KeywordsAI.LogType.TEXT_LLM and func:

            def wrapper(*args, **kwargs):
                openai_func = self._openai_wrapper(
                    func, keywordsai_params=keywordsai_params
                )
                result = openai_func(*args, **kwargs)
                return result

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

        return wrapper

    def async_logging_wrapper(
        self,
        func,
        type=LogType.TEXT_LLM,
        keywordsai_params = {},
        **wrapper_kwargs,
    ):
        if type == KeywordsAI.LogType.TEXT_LLM and func:

            async def wrapper(*args, **kwargs):
                openai_func = self._async_openai_wrapper(
                    func, keywordsai_params=keywordsai_params
                )
                result = await openai_func(*args, **kwargs)
                return result

        else:

            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

        return wrapper
