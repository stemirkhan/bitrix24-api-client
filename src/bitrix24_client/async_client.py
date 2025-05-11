import httpx
from typing import Any, Dict, Optional
import asyncio
from .base_client import BaseBitrix24Client
from .exceptions import (
    Bitrix24Error,
    Bitrix24ConnectionError,
    Bitrix24TimeoutError,
    Bitrix24HTTPError
)


class AsyncBitrix24Client(BaseBitrix24Client):
    def __init__(self, *args, max_concurrent_requests: int = 10, **kwargs):
        """
        Initializes the AsyncBitrix24Client with an optional limit for concurrent requests.

        Args:
            base_url (str): Base URL of the Bitrix24 portal (e.g., 'https://yourdomain.bitrix24.ru').
            access_token (str): Bitrix24 access token or webhook key.
            user_id (Optional[int]): User ID for OAuth-based authentication (None for webhook).
            timeout (int): Request timeout in seconds.
            max_concurrent_requests (int): The maximum number of concurrent requests.

        Raises:
            Bitrix24InvalidBaseURLError: If the provided base_url is not a valid HTTP or HTTPS URL.
        """
        super().__init__(*args, **kwargs)
        self.max_concurrent_requests = max_concurrent_requests
        self.semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=self._timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()

    async def open_session(self):
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        else:
            raise Bitrix24Error("Client session is already open.")

    async def close_session(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        else:
            raise Bitrix24Error("Client session is not open.")

    async def call_method(self, method: str, params: Optional[Dict[str, Any]] = None, fetch_all: bool = False) -> Any:
        """
        Makes an asynchronous POST request to the Bitrix24 API and handles errors, with support for paginated list methods.

        Args:
            method (str): The API method to call (e.g., 'crm.lead.get').
            params (Optional[Dict[str, Any]]): Parameters to pass in the request body.
            fetch_all (bool): Whether to fetch all pages of data if the method is paginated.

        Returns:
            Any: The result returned by the Bitrix24 API (all pages if fetch_all is True).

        Raises:
            Bitrix24TimeoutError: If the request times out.
            Bitrix24ConnectionError: If there is a connection error.
            Bitrix24HTTPError: If there is an HTTP error.
            Bitrix24APIError: If the Bitrix24 API returns an error.
            Bitrix24InvalidResponseError: If the response is not a valid JSON.
            Bitrix24Error: For any other request-related issues.
        """
        url = self._build_url(method)

        if fetch_all:
            result = await self._fetch_all_pages(url, params)
        else:
            result = await self._fetch(url, params)

        return result

    async def _make_request(self, url: str, params: Optional[Dict[str, Any]]) -> dict:
        """
        Makes an async POST request to the Bitrix24 API and returns the response as a dictionary.

        Args:
            url (str): The URL for the API request.
            params (Optional[Dict[str, Any]]): Parameters to pass in the request body.

        Returns:
            dict: The parsed JSON response from Bitrix24 API.

        Raises:
            Bitrix24TimeoutError: If the request times out.
            Bitrix24ConnectionError: If the connection to Bitrix24 fails.
            Bitrix24HTTPError: If a non-503 HTTP error occurs.
            Bitrix24Error: If maximum retries are exceeded or another request error occurs.
        """
        retries = 0

        while retries <= self._max_retries:
            try:
                async with self.semaphore:
                    response = await self._client.post(url, json=params or {})
                    if response.status_code == 503:
                        if retries == self._max_retries:
                            raise Bitrix24Error(f"Max retries exceeded for 503 error: {url}")
                        delay = self._calculate_delay(retries)
                        await asyncio.sleep(delay)
                        retries += 1
                        continue

                    response.raise_for_status()
                    return self._validate_response(response.text)

            except httpx.TimeoutException:
                raise Bitrix24TimeoutError(f"Request to Bitrix24 timed out: {url}")
            except httpx.ConnectError:
                raise Bitrix24ConnectionError(f"Failed to connect to Bitrix24: {url}")
            except httpx.HTTPStatusError as e:
                raise Bitrix24HTTPError(e.response.status_code, e.response.text)
            except httpx.RequestError as e:
                raise Bitrix24Error(f"Request error to Bitrix24: {str(e)}")

        raise Bitrix24Error(f"Exceeded maximum retry attempts for {url}")

    async def _fetch(self, url: str, params: Optional[Dict[str, Any]]) -> list:
        """
        Fetches a single page of data from the Bitrix24 API.

        Args:
            url (str): The URL for the API request.
            params (Optional[Dict[str, Any]]): Parameters to pass in the request body.

        Returns:
            list: The list of results from the single page of data.
        """
        data = await self._make_request(url, params)
        results, _, _ = self._handle_response(data, fetch_all=False)
        return results

    async def _fetch_all_pages(self, url: str, params: Optional[Dict[str, Any]]) -> list:
        """
        Fetches all pages of data using parallel async requests with semaphore-based concurrency control.

        Args:
            url (str): The URL for the API request.
            params (Optional[Dict[str, Any]]): Parameters to pass in the request body.

        Returns:
            list: The complete list of results from all pages.
        """
        params = params.copy() if params else {}
        data = await self._make_request(url, params)
        results, next_item, total = self._handle_response(data, fetch_all=True)
        page_size = 50

        if not next_item:
            return results

        tasks = []
        all_results = results

        for start in range(page_size, total, page_size):
            new_params = params.copy()
            new_params["start"] = start
            tasks.append(asyncio.create_task(self._make_request(url, new_params)))

        pages = await asyncio.gather(*tasks)

        for page in pages:
            page_results, _, _ = self._handle_response(page, fetch_all=True)
            all_results.extend(page_results)

        return all_results
