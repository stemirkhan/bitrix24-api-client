import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from urllib.parse import urljoin

from .exceptions import Bitrix24InvalidBaseURLError, Bitrix24InvalidResponseError, Bitrix24APIError
from .response_formatters import DefaultResponseFormatter
from .validators import DefaultResponseValidator
from .validators.interfaces import ResponseValidatorI
from .response_formatters.interfaces import ResponseFormatterI
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
            response_formatter: Optional[ResponseFormatterI] = None,
            response_validator: Optional[ResponseValidatorI] = None
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
            response_formatter (Optional[ResponseFormatterI]): Formatter for processing the API response.
            response_validator (Optional[ResponseValidatorI]): Validator for checking the correctness of the API response.

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
        self._response_formatter = response_formatter or DefaultResponseFormatter()
        self._response_validator = response_validator or DefaultResponseValidator()

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

    @abstractmethod
    def call_method(self, method: str, params: Optional[Dict[str, Any]] = None, fetch_all: bool = False) -> Any:
        ...
