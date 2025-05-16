from math import log1p

from .interfaces import RetryStrategyI


class LogarithmicRetryStrategyI(RetryStrategyI):
    def __init__(self, base: float, max_delay: float):
        self.base = base
        self.max_delay = max_delay

    def calculate_delay(self, retries: int) -> float:
        delay = self.base * log1p(retries) if retries > 0 else self.base
        return min(delay, self.max_delay)
