import os
from pathlib import Path
from typing import List

from aiogram.types import BotCommand
from pytz import timezone

from . import ROOT_DIR


REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_NAME = os.getenv('POSTGRES_NAME')

TOKEN = os.getenv('TOKEN')

TIMEZONE = timezone('Europe/Moscow')

COMMON_USERS_COMMANDS: List[BotCommand] = [
    BotCommand('start', 'Перезапустить бота'),
    BotCommand('menu', 'Главное меню'),
]
ADMIN_COMMANDS: List[BotCommand] = [
    BotCommand('admin_menu', 'Панель модератора'),
]

MODERATION_STATUS = 'На модерации'
REQUEST_DENIED_STATUS = 'Анкета отклонена'

LOGS_DIR = Path(ROOT_DIR, 'logs')
TEMP_DIR = Path(ROOT_DIR, 'temp')
