import json
from .interfaces import ResponseValidatorI
from ..exceptions import Bitrix24InvalidResponseError, Bitrix24APIError


class DefaultResponseValidator(ResponseValidatorI):
    def validate(self, response_text: str) -> dict:
        """
        Validate and parse the API response.

        Args:
            response_text (str): Raw response from the API.

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
