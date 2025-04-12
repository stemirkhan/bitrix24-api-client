from src.bitrix24_client.sync_client import Bitrix24Client

client = Bitrix24Client(base_url='https://yourdomain.bitrix24.ru',
                        access_token='your_webhook_key',
                        user_id=1) # Optional user_id parameter

try:
    result = client.call_method(
        method='crm.lead.list',
        params={'select': ['ID', 'TITLE']},
        fetch_all=True
    )
    print("Leads:", result)
except Exception as e:
    print(f"Error occurred: {e}")
