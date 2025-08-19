
import logging


class HealthFilter(logging.Filter):
    """Class to handle log configuration"""
    def filter(self, record: logging.LogRecord) -> bool:
        return "/health" not in record.getMessage()
