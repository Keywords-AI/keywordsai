from functools import wraps
from keywordsai_sdk.keywordsai_types.param_types import KeywordsAILogDict
import time
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai.types.chat.chat_completion import ChatCompletion
from packaging.version import Version
import types
from keywordsai_sdk.utils.debug_print import *
from keywordsai_sdk.utils.type_conversion import (
    openai_io_to_keywordsai_log,
    openai_stream_chunks_to_openai_io,
)
import openai
from typing import Generator, AsyncGenerator as AsyncGeneratorType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from keywordsai_sdk.core import KeywordsAILogger


class SyncGenerator:

    _keywordsai = None

    def __init__(
        self,
        generator: Generator[ChatCompletionChunk, None, None],
        keywordsai: "KeywordsAILogger" = None,
        data: dict = {},
        keywordsai_data={},
    ):
        self.generator = generator
        self.response_collector = []
        self._keywordsai = keywordsai
        data.update({"stream": True})
        self.data = data
        self.keywordsai_data = keywordsai_data

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
        constructed_response = openai_stream_chunks_to_openai_io(
            self.response_collector
        )
        data = openai_io_to_keywordsai_log(
            openai_input=self.data, openai_output=constructed_response
        )
        data.update(self.keywordsai_data)
        if self._keywordsai:
            self._keywordsai._log(data)
        return data


class AsyncGenerator:

    _keywordsai = None

    def __init__(
        self,
        generator: AsyncGeneratorType[ChatCompletionChunk, None],
        keywordsai: "KeywordsAILogger" = None,
        data: dict = {},
        keywordsai_data={},
    ):
        self.generator = generator
        self.response_collector = []
        self._keywordsai = keywordsai
        data.update({"stream": True})
        self.data = data
        self.keywordsai_data = keywordsai_data

    async def __aiter__(self):
        try:
            async for chunk in self.generator:
                self.response_collector.append(chunk)
                yield chunk
        finally:
            await self._on_finish()

    async def _on_finish(self):
        constructed_response = openai_stream_chunks_to_openai_io(
            self.response_collector
        )
        data = openai_io_to_keywordsai_log(
            openai_input=self.data, openai_output=constructed_response
        )
        data.update(self.keywordsai_data)
        print_info(data, debug_print)
        if self._keywordsai:
            self._keywordsai._log(data)
        return data


def _is_openai_v1():
    return Version(openai.__version__) >= Version("1.0.0")


def _is_streaming_response(response):
    return (
        isinstance(response, types.GeneratorType)
        or isinstance(response, types.AsyncGeneratorType)
        or (_is_openai_v1() and isinstance(response, openai.Stream))
        or (_is_openai_v1() and isinstance(response, openai.AsyncStream))
    )


def sync_openai_wrapper(
    func, keywordsai, keywordsai_params=KeywordsAILogDict, *args, **kwargs
):

    @wraps(func)
    def wrapped_openai(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            is_stream = _is_streaming_response(result)
            ttft = None
            if is_stream:
                ttft = end_time - start_time
                result: Generator[ChatCompletionChunk, None, None]
                return SyncGenerator(
                    result,
                    keywordsai,
                    data=kwargs,
                    keywordsai_data={**keywordsai_params, "ttft": ttft},
                )
            else:
                latency = end_time - start_time
                result: ChatCompletion
                log_data = openai_io_to_keywordsai_log(
                    openai_input=kwargs, openai_output=result
                )
                data = {**log_data, **keywordsai_params, "latency": latency}
                keywordsai._log(data=data)
            return result
        except Exception as e:
            print_error(e, print_func=debug_print)
            keywordsai._log(data={"error": str(e)})
            raise e

    return wrapped_openai


def async_openai_wrapper(
    func, keywordsai, keywordsai_params=KeywordsAILogDict, *args, **kwargs
):
    @wraps(func)
    async def wrapped_openai(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            end_time = time.time()
            is_stream = _is_streaming_response(result)
            ttft = None
            if is_stream:
                ttft = end_time - start_time
                result: AsyncGeneratorType[ChatCompletionChunk, None]
                return AsyncGenerator(
                    result,
                    keywordsai,
                    data=kwargs,
                    keywordsai_data={**keywordsai_params, "ttft": ttft},
                )
            else:
                latency = end_time - start_time
                result: ChatCompletion
                log_data = openai_io_to_keywordsai_log(
                    openai_input=kwargs, openai_output=result
                )
                data = {**log_data, **keywordsai_params, "latency": latency}
                keywordsai._log(data=data)
            return result
        except Exception as e:
            print_error(e, print_func=debug_print)
            keywordsai._log(data={"error": str(e)})
            raise e

    return wrapped_openai
