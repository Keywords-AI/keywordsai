import requests
import os

from dotenv import load_dotenv

load_dotenv()

url = f"{os.getenv('KEYWORDSAI_BASE_URL')}/v1/traces"

response = requests.post(url)

print(response.json())
