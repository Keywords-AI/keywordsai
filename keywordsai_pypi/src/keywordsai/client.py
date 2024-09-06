from .constants import *
from httpx import Client
from .utils.debug_print import print_info, debug_print
import os

class KeywordsAIClient(Client):
    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        path: str = None,
        extra_headers: dict = None,
    ):
        super().__init__()
        self.api_key = api_key or KEYWORDSAI_API_KEY
        self.base_url = base_url or KEYWORDSAI_BASE_URL
        self.path = path or KEYWORDSAI_LOGGING_PATH
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        print_info(
            f"KeywordsAI Client initialized with base_url: {self.base_url}",
            print_func=debug_print,
        )
        if extra_headers:
            self._headers.update(extra_headers)

    def post(self, data: dict):
        response = super().post(
            url=f"{self.base_url}{self.path}",
            json=data,
            headers=self.headers,
        )
        return response
