import asyncio
from typing import List

from src.bitrix24_client import AsyncBitrix24Client
from src.bitrix24_client import chunk_batch_requests


async def run_batch_example():
    client = AsyncBitrix24Client(
        base_url="https://example.bitrix24.ru",
        access_token="token",
        max_concurrent_requests=35,
        user_id=1
    )
    await client.open_session()

    lead_ids: List[dict] = await client.call_method(
        'crm.lead.list',
        params={
            'select': ['ID']
        },
        fetch_all=True
    )

    commands = {
        f"get_lead_{lead_id['ID']}": f"crm.lead.get?id={lead_id['ID']}"
        for lead_id in lead_ids
    }

    chunks = chunk_batch_requests(commands)

    get_lead_tasks = [
        asyncio.create_task(client.call_method(
            'batch',
            params={"halt": 1, "cmd": chunk}
        )) for chunk in chunks
    ]

    results = await asyncio.gather(*get_lead_tasks)

    await client.close_session()


if __name__ == "__main__":
    asyncio.run(run_batch_example())
