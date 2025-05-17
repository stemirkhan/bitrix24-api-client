from abc import ABC, abstractmethod


class ResponseValidatorI(ABC):
    @abstractmethod
    def validate(self, response_text: str) -> dict:
        """
        Validate and parse the API response.

        Args:
            response_text (str): Raw response from the API as a string.

        Returns:
            dict: Parsed and validated response data.

        Raises:
            Exception: If validation or parsing fails.
        """
        raise NotImplementedError
