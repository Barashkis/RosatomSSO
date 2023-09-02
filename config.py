import os
from pathlib import Path

from pytz import timezone


token = os.getenv('TOKEN')

redis_host = os.getenv('REDIS_HOST')
redis_password = os.getenv('REDIS_PASSWORD')

postgres_user = os.getenv('POSTGRES_USER')
postgres_password = os.getenv('POSTGRES_PASSWORD')
postgres_host = os.getenv('POSTGRES_HOST')
postgres_name = os.getenv('POSTGRES_NAME')

tz = timezone('Europe/Moscow')


root_path = os.path.dirname(__file__)
logs_path = Path(root_path, 'logfile.log')
temp_dir_path = Path(root_path, 'temp')

migrations_dir = 'versions'

moderation_status = 'На модерации'
request_denied_status = 'Анкета отклонена'
