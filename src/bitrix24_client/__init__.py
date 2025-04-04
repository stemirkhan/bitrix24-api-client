# my_package/__init__.py
from .sync_client import Bitrix24Client
from .async_client import AsyncBitrix24Client

__all__ = ["Bitrix24Client", "AsyncBitrix24Client"]