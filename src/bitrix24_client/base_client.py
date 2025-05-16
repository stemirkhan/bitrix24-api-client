import json
import math
import random
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from urllib.parse import urljoin

from .exceptions import Bitrix24InvalidBaseURLError, Bitrix24InvalidResponseError, Bitrix24APIError
from .retry_strategies import ExponentialRetryStrategyI
from .retry_strategies.interfaces import RetryStrategyI
from .utils import is_valid_url


class BaseBitrix24Client(ABC):
    def __init__(
            self,
            base_url: str,
            access_token: str,
            user_id: Optional[int] = None,
            timeout: int = 10,
            max_retries: int = 5,
            retry_strategy: Optional[RetryStrategyI] = None,
    ):
        """
        Initialize the base Bitrix24 API client.

        Args:
            base_url (str): Base URL of the Bitrix24 portal.
            access_token (str): Bitrix24 access token or webhook key.
            user_id (Optional[int]): User ID for OAuth-based authentication (None for webhook).
            timeout (int): Request timeout in seconds.
            max_retries (int): Maximum number of retries on 503 errors.
            retry_strategy (Optional[RetryStrategyI]): Retry delay strategy.

        Raises:
            Bitrix24InvalidBaseURLError: If the provided base_url is invalid.
        """
        if not is_valid_url(base_url):
            raise Bitrix24InvalidBaseURLError(f"Invalid base URL: '{base_url}'")

        self._base_url = base_url.rstrip('/') + '/'
        self._access_token = access_token
        self._user_id = user_id
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_strategy = retry_strategy or ExponentialRetryStrategyI(base=5, max_delay=20)

    @property
    def max_retries(self) -> int:
        """
        Get the maximum number of retries after a 503 error.

        Returns:
            int: max_retries
        """
        return self._max_retries

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

    @staticmethod
    def _handle_response(data: dict, fetch_all: bool) -> tuple[list, Any, Any]:
        """
        Handles the response from Bitrix24 API and manages pagination if needed.

        Args:
            data (dict): The response data from the API.
            fetch_all (bool): Whether to fetch all pages of data.

        Returns:
            tuple: A tuple of results and the next page token (if any).
        """
        results = data.get("result", [])

        if isinstance(results, dict):
            key = list(results.keys())[0]
            results = results[key]

        if fetch_all:
            return results, data.get('next', None), data.get('total', None)
        return results, None, None

    @staticmethod
    def _validate_response(response_text: str) -> dict:
        """
        Validates and parses the JSON response from Bitrix24 API.

        Args:
            response_text (str): The response text from the API.

        Returns:
            dict: Parsed JSON data.

        Raises:
            Bitrix24InvalidResponseError: If the response is not valid JSON.
            Bitrix24APIError: If the response contains an API error.
        """
        try:
            data = json.loads(response_text)
        except ValueError:
            raise Bitrix24InvalidResponseError(f"Invalid JSON from Bitrix24: {response_text}")

        if "error" in data:
            raise Bitrix24APIError(
                code=data.get("error"),
                description=data.get("error_description") or "No description"
            )

        return data

    @abstractmethod
    def call_method(self, method: str, params: Optional[Dict[str, Any]] = None, fetch_all: bool = False) -> Any:
        ...
