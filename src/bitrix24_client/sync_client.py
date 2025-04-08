import requests
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError
from typing import Any, Dict, Optional
from .base_client import BaseBitrix24Client
from .exceptions import (
    Bitrix24Error,
    Bitrix24ConnectionError,
    Bitrix24TimeoutError,
    Bitrix24HTTPError
)


class Bitrix24Client(BaseBitrix24Client):
    def call_method(self, method: str, params: Optional[Dict[str, Any]] = None, fetch_all: bool = False) -> Any:
        """
        Makes a POST request to the Bitrix24 API and handles errors, with support for paginated list methods.

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
            result = self._fetch_all_pages(url, params)
        else:
            result = self._fetch(url, params)

        return result

    def _make_request(self, url: str, params: Optional[Dict[str, Any]]) -> dict:
        """
        Makes a POST request to the Bitrix24 API and returns the response as a dictionary.

        Args:
            url (str): The URL for the API request.
            params (Optional[Dict[str, Any]]): Parameters to pass in the request body.

        Returns:
            dict: The parsed JSON response from Bitrix24 API.

        Raises:
            Bitrix24InvalidResponseError: If the response is not a valid JSON.
            Bitrix24APIError: If the Bitrix24 API returns an error.
        """
        try:
            response = requests.post(url, json=params or {}, timeout=self.timeout)
            response.raise_for_status()

            data = self._validate_response(response.text)
            return data

        except Timeout:
            raise Bitrix24TimeoutError(f"Request to Bitrix24 timed out: {url}")
        except ConnectionError:
            raise Bitrix24ConnectionError(f"Failed to connect to Bitrix24: {url}")
        except HTTPError as e:
            raise Bitrix24HTTPError(e.response.status_code, e.response.text)
        except RequestException as e:
            raise Bitrix24Error(f"Request error to Bitrix24: {str(e)}")

    def _fetch(self, url: str, params: Optional[Dict[str, Any]]) -> list:
        """
        Fetches a single page of data from the Bitrix24 API.

        Args:
            url (str): The URL for the API request.
            params (Optional[Dict[str, Any]]): Parameters to pass in the request body.

        Returns:
            list: The list of results from the single page of data.
        """
        data = self._make_request(url, params)
        results, _, _ = self._handle_response(data, fetch_all=False)
        return results

    def _fetch_all_pages(self, url: str, params: Optional[Dict[str, Any]]) -> list:
        """
        Fetches all pages of data if the method is paginated.

        Args:
            url (str): The URL for the API request.
            params (Optional[Dict[str, Any]]): Parameters to pass in the request body.

        Returns:
            list: The complete list of results from all pages.
        """
        all_results = []
        params = params.copy() if params else {}

        while True:
            data = self._make_request(url, params)

            results, next_page, _ = self._handle_response(data, fetch_all=True)

            all_results.extend(results)

            if next_page:
                params["start"] = next_page
            else:
                break

        return all_results
