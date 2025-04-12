from src.bitrix24_client.sync_client import Bitrix24Client
from src.bitrix24_client.exceptions import (
    Bitrix24TimeoutError,
    Bitrix24ConnectionError,
    Bitrix24HTTPError,
)


client = Bitrix24Client(base_url='https://yourdomain.bitrix24.ru',
                        access_token='your_webhook_key',
                        user_id=1) # Optional user_id parameter

try:
    result = client.call_method('crm.lead.get', params={'id': '123'})
    print("Lead:", result)
except Bitrix24TimeoutError:
    print("Request timed out.")
except Bitrix24ConnectionError:
    print("Could not connect to Bitrix24.")
except Bitrix24HTTPError as e:
    print(f"HTTP error: {e.status_code} - {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
