from ..interfaces import RetryStrategyI


class ExponentialRetryStrategyI(RetryStrategyI):
    def __init__(self, base: float, max_delay: float):
        self.base = base
        self.max_delay = max_delay

    def calculate_delay(self, retries: int) -> float:
        delay = self.base * (2 ** (retries - 1))
        return min(delay, self.max_delay)