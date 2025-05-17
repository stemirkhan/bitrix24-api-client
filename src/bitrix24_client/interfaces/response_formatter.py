from abc import ABC, abstractmethod
from typing import Any, Tuple


class ResponseFormatterI(ABC):
    @abstractmethod
    def format(self, data: dict, fetch_all: bool) -> Tuple[list, Any, Any]:
        """
        Format the response from the Bitrix24 API.

        Args:
            data (dict): Raw response data from the API.
            fetch_all (bool): Flag indicating whether to return paginated data.

        Returns:
            tuple: A tuple containing the result list, next page token (if any), and total count (if any).
        """
        raise NotImplementedError
