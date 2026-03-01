import json
import logging
import time
import sys


class StructuredLogger:
    """Provides JSON-structured logging for observability.

    Attributes:
        logger: Internal logger instance.
    """

    def __init__(self, name: str = "TaskManager"):
        """Initializes the structured logger.

        Args:
            name: Name for the internal logger. Defaults to "TaskManager".
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log(self, level: int, event: str, **kwargs):
        """Logs a structured JSON message.

        Args:
            level: The logging level (e.g., logging.INFO).
            event: A string description of the event.
            **kwargs: Additional fields to include in the JSON record.
        """
        record = {
            "timestamp": time.time(),
            "level": logging.getLevelName(level),
            "event": event,
            **kwargs,
        }
        self.logger.log(level, json.dumps(record))
