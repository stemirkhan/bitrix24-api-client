class Bitrix24Error(Exception):
    """
    Base exception for Bitrix24 client errors.
    """
    pass


class Bitrix24ConnectionError(Bitrix24Error):
    """
    Raised when a connection to Bitrix24 fails.
    """
    pass


class Bitrix24TimeoutError(Bitrix24Error):
    """
    Raised when a request to Bitrix24 times out.
    """
    pass


class Bitrix24HTTPError(Bitrix24Error):
    """
    Raised when an HTTP error (4xx/5xx) occurs during a request to Bitrix24.

    Attributes:
        status_code (int): The HTTP status code returned by the server.
        response_text (str): The body of the HTTP response.
    """

    def __init__(self, status_code: int, response_text: str):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"HTTP {status_code}: {response_text}")


class Bitrix24APIError(Bitrix24Error):
    """
    Raised when the Bitrix24 API returns an error.

    Attributes:
        code (str): The error code returned by the API.
        description (str): The error description returned by the API.
    """

    def __init__(self, code: str, description: str):
        self.code = code
        self.description = description
        super().__init__(f"Bitrix24 API error [{code}]: {description}")


class Bitrix24InvalidResponseError(Bitrix24Error):
    """
    Raised when the response from Bitrix24 is not valid JSON.
    """
    pass


class Bitrix24InvalidBaseURLError(Bitrix24Error):
    """
    Raised when the provided base URL is invalid.
    """
    pass
