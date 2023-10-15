import logging
from datetime import datetime

from .config import (
    LOGS_DIR,
    TIMEZONE,
)


__all__ = (
    'logger',
)


class Formatter(logging.Formatter):
    @staticmethod
    def convert_to_datetime(timestamp):
        return datetime.fromtimestamp(timestamp).astimezone(TIMEZONE)

    def formatTime(self, record, date_format=None):
        if not date_format:
            date_format = '%d-%m-%Y %H:%M:%S'
        date_string = self.convert_to_datetime(record.created).strftime(date_format)

        return date_string


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOGS_DIR)
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

formatter = Formatter('%(asctime)s: %(filename)s: %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
