import requests
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError
from typing import Any, Dict, Optional
from .base_client import BaseBitrix24Client
from .exceptions import (
    Bitrix24Error,
    Bitrix24ConnectionError,
    Bitrix24TimeoutError,
    Bitrix24HTTPError,
    Bitrix24APIError,
    Bitrix24InvalidResponseError,
)


class Bitrix24Client(BaseBitrix24Client):
    def call_method(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Makes a POST request to the Bitrix24 API and handles errors.

        Args:
            method (str): The API method to call (e.g., 'crm.lead.get').
            params (Optional[Dict[str, Any]]): Parameters to pass in the request body.

        Returns:
            Any: The result returned by the Bitrix24 API.

        Raises:
            Bitrix24TimeoutError: If the request times out.
            Bitrix24ConnectionError: If there is a connection error.
            Bitrix24HTTPError: If there is an HTTP error.
            Bitrix24APIError: If the Bitrix24 API returns an error.
            Bitrix24InvalidResponseError: If the response is not a valid JSON.
            Bitrix24Error: For any other request-related issues.
        """
        url = self._build_url(method)

        try:
            response = requests.post(url, json=params or {}, timeout=self.timeout)
            response.raise_for_status()

            try:
                data = response.json()
            except ValueError:
                raise Bitrix24InvalidResponseError(f"Invalid JSON from Bitrix24: {response.text}")

            if "error" in data:
                raise Bitrix24APIError(
                    code=data.get("error"),
                    description=data.get("error_description") or "No description"
                )

            return data.get("result")

        except Timeout:
            raise Bitrix24TimeoutError(f"Request to Bitrix24 timed out: {url}")
        except ConnectionError:
            raise Bitrix24ConnectionError(f"Failed to connect to Bitrix24: {url}")
        except HTTPError as e:
            raise Bitrix24HTTPError(e.response.status_code, e.response.text)
        except RequestException as e:
            raise Bitrix24Error(f"Request error to Bitrix24: {str(e)}")
