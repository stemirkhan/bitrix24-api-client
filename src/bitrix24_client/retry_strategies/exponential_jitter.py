from random import uniform

from ..interfaces import RetryStrategyI


class ExponentialJitterRetryStrategyI(RetryStrategyI):
    def __init__(self, base: float, max_delay: float):
        self.base = base
        self.max_delay = max_delay

    def calculate_delay(self, retries: int) -> float:
        exp_delay = self.base * (2 ** (retries - 1))
        delay = uniform(0, exp_delay)
        return min(delay, self.max_delay)
