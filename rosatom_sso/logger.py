import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from rosatom_sso.config import (
    LOGS_DIR,
    TIMEZONE,
)


__all__ = (
    'setup_logger',
)


class _LocalTimeFormatter(logging.Formatter):
    @staticmethod
    def convert_to_datetime(timestamp):
        return datetime.fromtimestamp(timestamp).astimezone(TIMEZONE)

    def formatTime(self, record, date_format=None):
        if not date_format:
            date_format = '%d-%m-%Y %H:%M:%S'
        date_string = self.convert_to_datetime(record.created).strftime(date_format)

        return date_string


def _namer(_):
    return Path(LOGS_DIR, f'logfile.{datetime.now(tz=TIMEZONE).strftime("%d-%m-%Y_%H:%M:%S")}.log')


def setup_logger():
    if not os.path.exists(LOGS_DIR):
        os.mkdir(LOGS_DIR)

    root_logger = logging.getLogger('rosatom_sso')
    root_logger.setLevel(logging.DEBUG)

    handler = TimedRotatingFileHandler(filename=Path(LOGS_DIR, 'logfile.log'), when='d', interval=31, backupCount=31)
    handler.namer = _namer

    formatter = _LocalTimeFormatter('{asctime}: {filename}: {levelname} - {message}', style='{')
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)
