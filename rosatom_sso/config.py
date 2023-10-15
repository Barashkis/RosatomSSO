import os
from pathlib import Path

from aiogram import types
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

COMMON_USERS_COMMANDS = [
    types.BotCommand('start', 'Перезапустить бота'),
    types.BotCommand('menu', 'Главное меню'),
]
ADMIN_COMMANDS = [
    types.BotCommand('admin_menu', 'Панель модератора'),
]

MODERATION_STATUS = 'На модерации'
REQUEST_DENIED_STATUS = 'Анкета отклонена'

LOGS_DIR = Path(ROOT_DIR, 'logfile.log')
TEMP_DIR = Path(ROOT_DIR, 'temp')
