from dotenv import load_dotenv

load_dotenv(override=True)
from respan.logs.api import LogAPI
import os


def main():
    api_key = os.getenv("RESPAN_API_KEY")
    base_url = os.getenv("RESPAN_BASE_URL")

    log_api_client = LogAPI(api_key=api_key, base_url=base_url)

    log_list = log_api_client.list()
    print(log_list)


if __name__ == "__main__":
    main()
