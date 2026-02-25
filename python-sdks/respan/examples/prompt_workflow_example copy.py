from respan_sdk.respan_types.prompt_types import Prompt
from respan.prompts import PromptAPI
import os

prompt_api = PromptAPI(
    api_key=os.getenv("RESPAN_API_KEY"), base_url=os.getenv("RESPAN_BASE_URL")
)

prompt_api.create(create_data=Prompt(name=23434))
