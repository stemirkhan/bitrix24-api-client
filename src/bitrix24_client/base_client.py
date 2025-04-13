import json
import math
import random
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from urllib.parse import urljoin

from src.bitrix24_client.exceptions import Bitrix24InvalidBaseURLError, Bitrix24InvalidResponseError, Bitrix24APIError
from src.bitrix24_client.utils import is_valid_url


class BaseBitrix24Client(ABC):
    def __init__(
            self,
            base_url: str,
            access_token: str,
            user_id: Optional[int] = None,
            timeout: int = 10,
            rate_limit_pause: float = 1.0,
            max_retries: int = 5,
            max_delay: float = 20.0,
            retry_strategy: str = "exponential"
    ):
        """
        Initialize the base Bitrix24 API client.

        Args:
            base_url (str): Base URL of the Bitrix24 portal.
            access_token (str): Bitrix24 access token or webhook key.
            user_id (Optional[int]): User ID for OAuth-based authentication (None for webhook).
            timeout (int): Request timeout in seconds.
            rate_limit_pause (float): Initial pause in seconds before retry.
            max_retries (int): Maximum number of retries on 503 errors.
            max_delay (float): Maximum delay between retries in seconds.
            retry_strategy (str): Retry delay strategy. One of: 'fixed', 'linear', 'exponential', 'logarithmic', 'exponential_jitter'.

        Raises:
            Bitrix24InvalidBaseURLError: If the provided base_url is invalid.
        """
        if not is_valid_url(base_url):
            raise Bitrix24InvalidBaseURLError(f"Invalid base URL: '{base_url}'")

        self._base_url = base_url.rstrip('/') + '/'
        self._access_token = access_token
        self._user_id = user_id
        self._timeout = timeout
        self._rate_limit_pause = rate_limit_pause
        self._max_retries = max_retries
        self._max_delay = max_delay
        self._retry_strategy = retry_strategy

    @property
    def rate_limit_pause(self) -> float:
        """Getter for the rate limit pause duration."""
        return self._rate_limit_pause

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

    def _calculate_delay(self, retries: int) -> float:
        """
        Calculates the delay before the next retry based on the selected strategy.

        Args:
            retries (int): The current retry attempt number (starting from 1).

        Returns:
            float: Delay in seconds before the next retry.
        """
        base = self._rate_limit_pause
        strategy = self._retry_strategy.lower()

        if strategy == "fixed":
            delay = base
        elif strategy == "linear":
            delay = (base * retries) if retries > 0 else base
        elif strategy == "logarithmic":
            delay = (base * math.log1p(retries)) if retries > 0 else base
        elif strategy == "exponential":
            delay = base * (2 ** (retries - 1))
        elif strategy == "exponential_jitter":
            delay = base * (2 ** (retries - 1))
            delay = random.uniform(0, delay)
        else:
            raise ValueError(f"Unknown retry strategy: '{self._retry_strategy}'")

        return min(delay, self._max_delay)

    @abstractmethod
    def call_method(self, method: str, params: Optional[Dict[str, Any]] = None, fetch_all: bool = False) -> Any:
        ...
