import keywordsai_sdk.keywordsai_config as config
from httpx import Client
from .utils.debug_print import print_info, debug_print

class KeywordsAIClient(Client):
    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        path: str = None,
        extra_headers: dict = None,
    ):
        super().__init__()
        self.api_key = api_key or config.KEYWORDSAI_API_KEY
        self.base_url = base_url or config.KEYWORDSAI_BASE_URL
        self.path = path or config.KEYWORDSAI_LOGGING_PATH
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if extra_headers:
            self._headers.update(extra_headers)

    def post(self, data: dict):
        url = f"{self.base_url}{self.path}"
        print_info(f"Posting data to KeywordsAI: {url} ", print_func=debug_print)
        response = super().post(
            url=url,
            json=data,
            headers=self.headers,
        )
        return response
