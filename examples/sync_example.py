from src.bitrix24_client.sync_client import Bitrix24Client

client = Bitrix24Client(base_url='https://example.bitrix24.ru',
                        access_token='token',
                        user_id=1)  # Optional user_id parameter

client.open_session()

result = client.call_method(
    method='crm.lead.list',
    params={'select': ['ID', 'TITLE']},
    fetch_all=True
)

client.close_session()
