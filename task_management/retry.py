class RetryPolicy:
    """Configures exponential backoff retry strategy.

    Attributes:
        max_retries: Maximum number of retries for a task.
        base_delay: Initial delay in seconds.
        max_delay: Maximum possible delay in seconds.
    """

    def __init__(
        self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0
    ):
        """Initializes the retry policy.

        Args:
            max_retries: Maximum number of retries. Defaults to 3.
            base_delay: Initial delay in seconds. Defaults to 1.0.
            max_delay: Maximum delay in seconds. Defaults to 60.0.
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def get_delay(self, attempt: int) -> float:
        """Calculates delay for a given retry attempt using exponential backoff.

        Args:
            attempt: The current retry attempt number (1-based).

        Returns:
            The delay in seconds to wait before the next attempt.
        """
        delay = self.base_delay * (2 ** (attempt - 1))
        return min(delay, self.max_delay)
