from keywordsai_sdk.keywordsai_types.prompt_types import Prompt
from keywordsai.prompts import PromptAPI
import os

prompt_api = PromptAPI(
    api_key=os.getenv("KEYWORDSAI_API_KEY"), base_url=os.getenv("KEYWORDSAI_BASE_URL")
)

prompt_api.create(create_data=Prompt(name=23434))
