import json
import logging
import time
import sys


class StructuredLogger:
    """Provides JSON-structured logging for observability."""

    def __init__(self, name: str = "TaskManager"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log(self, level: int, event: str, **kwargs):
        """Logs a structured JSON message."""
        record = {
            "timestamp": time.time(),
            "level": logging.getLevelName(level),
            "event": event,
            **kwargs,
        }
        self.logger.log(level, json.dumps(record))
