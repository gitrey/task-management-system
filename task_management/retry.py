from pydantic import BaseModel, Field


class RetryPolicy(BaseModel):
    """Configures exponential backoff retry strategy.

    Attributes:
        max_retries: Maximum number of retries for a task.
        base_delay: Initial delay in seconds.
        max_delay: Maximum possible delay in seconds.
    """

    max_retries: int = Field(default=3, ge=0)
    base_delay: float = Field(default=1.0, gt=0)
    max_delay: float = Field(default=60.0, gt=0)

    def get_delay(self, attempt: int) -> float:
        """Calculates delay for a given retry attempt using exponential backoff.

        Args:
            attempt: The current retry attempt number (1-based).

        Returns:
            The delay in seconds to wait before the next attempt.
        """
        delay = self.base_delay * (2 ** (attempt - 1))
        return min(delay, self.max_delay)
