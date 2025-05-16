from .interfaces import RetryStrategyI


class FixedRetryStrategyI(RetryStrategyI):
    def __init__(self, base: float, max_delay: float):
        self.base = base
        self.max_delay = max_delay

    def calculate_delay(self, retries: int) -> float:
        return min(self.base, self.max_delay)
