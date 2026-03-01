class RetryPolicy:
    """Configures exponential backoff retry strategy."""

    def __init__(
        self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def get_delay(self, attempt: int) -> float:
        """Calculates delay for a given retry attempt."""
        delay = self.base_delay * (2 ** (attempt - 1))
        return min(delay, self.max_delay)
