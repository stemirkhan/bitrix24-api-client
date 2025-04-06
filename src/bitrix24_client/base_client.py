from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from urllib.parse import urljoin

from src.bitrix24_client.exceptions import Bitrix24InvalidBaseURLError
from src.bitrix24_client.utils import is_valid_url


class BaseBitrix24Client(ABC):
    def __init__(self, base_url: str, access_token: str, user_id: Optional[int] = None, timeout: int = 10):
        """
        Initialize the base Bitrix24 API client.

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

        self._base_url = base_url.rstrip('/') + '/'
        self._access_token = access_token
        self._user_id = user_id
        self._timeout = timeout

    @property
    def base_url(self) -> str:
        """
        Get the base URL of the Bitrix24 portal.

        Returns:
            str: The base URL.
        """
        return self._base_url

    @property
    def access_token(self) -> str:
        """
        Get the access token or webhook key.

        Returns:
            str: The access token.
        """
        return self._access_token

    @property
    def user_id(self) -> Optional[int]:
        """
        Get the user ID if available.

        Returns:
            Optional[int]: The user ID or None if not set.
        """
        return self._user_id

    @property
    def timeout(self) -> int:
        """
        Get the timeout value for requests.

        Returns:
            int: The timeout in seconds.
        """
        return self._timeout

    def _build_url(self, method: str) -> str:
        """
        Construct the full API endpoint URL for a given Bitrix24 method.

        Args:
            method (str): The API method name (e.g., 'crm.lead.get').

        Returns:
            str: The full URL to be used for the API call.
        """
        if self._user_id is not None:
            path = f"rest/{self._user_id}/{self._access_token}/{method}"
        else:
            path = f"rest/{self._access_token}/{method}"
        return urljoin(self._base_url, path)

    @abstractmethod
    def call_method(self, method: str, params: Optional[Dict[str, Any]] = None, fetch_all: bool = False) -> Any:
        """
        Execute a call to the Bitrix24 REST API.

        Args:
            method (str): The API method to call (e.g., 'crm.lead.get').
            params (Optional[Dict[str, Any]]): Parameters to pass in the request body.
            fetch_all (bool): Whether to fetch all pages of data if the method is paginated.

        Returns:
            Any: The result returned by the Bitrix24 API.
        """
        ...
