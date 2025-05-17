# Bitrix24 REST API Client

![License](https://img.shields.io/github/license/stemirkhan/bitrix24-api-client)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Build](https://img.shields.io/badge/status-active-brightgreen)

A Python client for interacting with the Bitrix24 REST API.  
Supports both synchronous (`requests`) and asynchronous (`httpx`) modes.  
Ideal for CRM automation, data synchronization, and Bitrix24 integrations.

## 🔧 Features

* Synchronous client (`requests`)
* Asynchronous client (`httpx`)
* Retry strategies: `fixed`, `linear`, `exponential`, `logarithmic`, `exponential_jitter`
* Support for pagination (`fetch_all=True`)
* API and HTTP error handling
* Context manager and session support

## 💻 Installation

```bash
pip install bitrix24-api-client
```

## 🚀 Quick Start

```python
from bitrix24_client import Bitrix24Client

with Bitrix24Client(
    base_url="https://yourdomain.bitrix24.ru",
    access_token="your_webhook_or_token"
) as client:
    result = client.call_method("crm.lead.list", {"select": ["ID", "TITLE"]}, fetch_all=True)
    print(result)
```

```python
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
```

## 🔁 Retry Strategies

Supported strategies:

* `fixed` — fixed delay
* `linear` — linear backoff
* `logarithmic` — logarithmic backoff
* `exponential` — exponential backoff
* `exponential_jitter` — exponential backoff with jitter (randomized delay)

Example:

```python
client = Bitrix24Client(
    base_url="https://yourdomain.bitrix24.ru",
    access_token="your_webhook_or_token",
    retry_strategy="exponential_jitter"
)
```
## ⚙️ Constructor Arguments

| Parameter            | Description                                                            |
| -------------------- | ---------------------------------------------------------------------- |
| `base_url`           | Base URL of the Bitrix24 portal.                                       |
| `access_token`       | Bitrix24 access token or webhook key.                                  |
| `user_id`            | User ID for OAuth-based authentication (optional, `None` for webhook). |
| `timeout`            | Request timeout in seconds.                                            |
| `max_retries`        | Maximum number of retries on 503 errors.                               |
| `retry_strategy`     | Optional retry delay strategy (implements `RetryStrategyI`).           |
| `response_formatter` | Optional API response formatter (implements `ResponseFormatterI`).     |
| `response_validator` | Optional API response validator (implements `ResponseValidatorI`).     |

**Note:**
If `retry_strategy`, `response_formatter`, or `response_validator` are not provided, default implementations will be used.

**Raises:**
`Bitrix24InvalidBaseURLError` — If the provided `base_url` is invalid.

---

## 🤝 Contributing

If you’ve found a bug, have a suggestion, or want to add a feature — your help is welcome! Feel free to open an issue or submit a pull request.

All contributions are appreciated: code, documentation, or usage examples.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/stemirkhan/bitrix24-api-client/blob/main/LICENSE) file for details.
