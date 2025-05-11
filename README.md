# Bitrix24 API Client

![License](https://img.shields.io/github/license/stemirkhan/bitrix24-api-client)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Build](https://img.shields.io/badge/status-active-brightgreen)

Библиотека для взаимодействия с [Bitrix24 REST API](https://training.bitrix24.com/rest_help/), поддерживающая как синхронный, так и асинхронный режим работы.

## 🔧 Возможности

* Синхронный клиент (`requests`)
* Асинхронный клиент (`httpx`)
* Поддержка стратегий повторов: `fixed`, `linear`, `exponential`, `logarithmic`, `exponential_jitter`
* Поддержка постраничной загрузки (`fetch_all=True`)
* Обработка ошибок API и HTTP
* Менеджер контекста и сессий

## 💻 Установка

```bash
pip install bitrix24-api-client
```

## 🚀 Быстрый старт

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

## 🔁 Стратегии повторных попыток

Поддерживаемые стратегии:

* `fixed` — фиксированная задержка
* `linear` — линейный рост
* `logarithmic` — логарифмический рост
* `exponential` — экспоненциальный рост
* `exponential_jitter` — экспоненциальный с джиттером (случайная задержка)

Пример:

```python
client = Bitrix24Client(
    base_url="https://yourdomain.bitrix24.ru",
    access_token="your_webhook_or_token",
    retry_strategy="exponential_jitter"
)
```

## ⚙️ Аргументы конструктора

| Параметр           | Описание                                  |
| ------------------ | ----------------------------------------- |
| `base_url`         | URL портала Bitrix24                      |
| `access_token`     | Токен или Webhook ключ                    |
| `user_id`          | ID пользователя                           |
| `timeout`          | Таймаут запроса                           |
| `rate_limit_pause` | Базовая задержка перед повтором           |
| `max_retries`      | Максимальное количество повторов          |
| `max_delay`        | Максимальная задержка между повторами     |
| `retry_strategy`   | Стратегия повтора (см. выше)              |


---

## 🤝 Участие

Если вы нашли ошибку, хотите предложить улучшение или добавить функциональность — буду рад вашей помощи. Можно создать issue или отправить pull request.

Любой вклад приветствуется: от кода и документации до примеров использования.

---

## 📄 Лицензия

Проект распространяется под лицензией MIT. См. файл [LICENSE](https://github.com/stemirkhan/bitrix24-api-client/blob/main/LICENSE) для подробностей.

