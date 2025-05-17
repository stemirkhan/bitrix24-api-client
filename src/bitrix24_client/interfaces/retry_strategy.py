from abc import ABC, abstractmethod

class RetryStrategyI(ABC):
    @abstractmethod
    def calculate_delay(self, retries: int) -> float:
        """
        Calculate delay in seconds before the next retry.

        Args:
            retries (int): The current retry attempt number (starting from 1).

        Returns:
            float: Delay in seconds.
        """
        raise NotImplementedError
