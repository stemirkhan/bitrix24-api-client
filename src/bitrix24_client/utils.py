from urllib.parse import urlparse
from typing import List, Dict, Any


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


def chunk_batch_requests(commands: Dict[str, Any], chunk_size: int = 50) -> List[Dict[str, Any]]:
    chunked = [
        {k: commands[k] for k in list(commands.keys())[i:i + chunk_size]}
        for i in range(0, len(commands), chunk_size)
    ]
    return chunked
