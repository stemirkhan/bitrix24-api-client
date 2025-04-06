from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    """
    Validates whether the given URL is a proper HTTP or HTTPS URL.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)
