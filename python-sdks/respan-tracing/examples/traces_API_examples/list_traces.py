import requests
import os

from dotenv import load_dotenv

load_dotenv()

url = f"{os.getenv('RESPAN_BASE_URL')}/v1/traces"

response = requests.post(url)

print(response.json())
