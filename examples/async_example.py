import asyncio
from src.bitrix24_client.async_client import AsyncBitrix24Client


async def main():
    client = AsyncBitrix24Client(base_url='https://yourdomain.bitrix24.ru',
                                 access_token='your_webhook_key',
                                 user_id=1,  # Optional user_id parameter
                                 max_concurrent_requests=10)

    try:
        result = await client.call_method(
            method='crm.contact.list',
            params={'select': ['ID', 'NAME']},
            fetch_all=True
        )
        print("Contacts:", result)
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
