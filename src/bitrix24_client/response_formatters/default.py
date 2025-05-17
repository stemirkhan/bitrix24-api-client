from typing import Any, Tuple
from ..interfaces import ResponseFormatterI

class DefaultResponseFormatter(ResponseFormatterI):
    def format(self, data: dict, fetch_all: bool) -> Tuple[list, Any, Any]:
        results = data.get("result", [])

        if isinstance(results, dict):
            key = list(results.keys())[0]
            results = results[key]

        if fetch_all:
            return results, data.get('next', None), data.get('total', None)
        return results, None, None
