from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from urllib.parse import urljoin, urlparse

from src.bitrix24_client.exceptions import Bitrix24InvalidBaseURLError
from src.bitrix24_client.utils import is_valid_url

class BaseBitrix24Client(ABC):
    def __init__(self, base_url: str, access_token: str, user_id: Optional[int] = None, timeout: int = 10):
        """
        Base class for Bitrix24 API clients.

        Args:
            base_url (str): Base URL of the Bitrix24 portal (e.g., 'https://yourdomain.bitrix24.ru').
            access_token (str): Bitrix24 access token or webhook key.
            user_id (Optional[int]): User ID for OAuth-based authentication (None for webhook).
            timeout (int): Request timeout in seconds.

        Raises:
            Bitrix24InvalidBaseURLError: If the provided base_url is not a valid HTTP or HTTPS URL.
        """
        if not is_valid_url(base_url):
            raise Bitrix24InvalidBaseURLError(f"Invalid base URL: '{base_url}'")

        self.base_url = base_url.rstrip('/') + '/'
        self.access_token = access_token
        self.user_id = user_id
        self.timeout = timeout

    def _build_url(self, method: str) -> str:
        """
        Constructs the full API endpoint URL for a given Bitrix24 method.

        Args:
            method (str): The API method name (e.g., 'crm.lead.get').

        Returns:
            str: The full URL to be used for the API call.
        """
        if self.user_id is not None:
            path = f"rest/{self.user_id}/{self.access_token}/{method}"
        else:
            path = f"rest/{self.access_token}/{method}"
        return urljoin(self.base_url, path)

    @abstractmethod
    def call_method(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Executes a call to the Bitrix24 REST API.

        Args:
            method (str): The API method name.
            params (Optional[Dict[str, Any]]): Parameters for the method call.

        Returns:
            Any: The result returned by the Bitrix24 API.
        """
        ...
