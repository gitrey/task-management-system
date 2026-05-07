import json
import logging
import time
import sys
from typing import List, Dict, Any


class StructuredLogger:
    """Provides JSON-structured logging for observability.

    Attributes:
        logger: Internal logger instance.
        _buffer: Static list to store recent log records for API streaming.
    """

    _buffer: List[Dict[str, Any]] = []
    _max_buffer_size = 500

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
        """Logs a structured JSON message and updates the buffer.

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
        json_record = json.dumps(record)
        self.logger.log(level, json_record)

        # Update the static buffer for API access
        StructuredLogger._buffer.append(record)
        if len(StructuredLogger._buffer) > StructuredLogger._max_buffer_size:
            StructuredLogger._buffer.pop(0)

    @classmethod
    def get_buffer(cls) -> List[Dict[str, Any]]:
        """Returns the current log buffer."""
        return cls._buffer
