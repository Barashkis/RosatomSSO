import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Sequence

from openpyxl import Workbook

from ......config import TEMP_DIR
from ......database import (
    CommonUser,
    Statistic,
)
from .interfaces import UsersFileBuilder


class CommonUsersFileBuilder(UsersFileBuilder):
    @staticmethod
    def build_xlsx(users: Sequence[CommonUser], statistics_: Sequence[Statistic]) -> str:  # type: ignore[override]
        filename = f'common-users-{int(datetime.now().timestamp() * 100)}'
        csv_path = Path(TEMP_DIR, f'{filename}.csv')
        xlsx_path = Path(TEMP_DIR, f'{filename}.xlsx')

        with open(csv_path, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(['Пользователей в системе', len(users)])
            writer.writerow(['Данные о пользователе'] + [None] * 5 + ['Активность пользователя'])
            writer.writerow(
                [
                    'Имя в Telegram',
                    'Фамилия и имя',
                    'Название отряда',
                    'Статус',
                    'Количество баллов',
                    'Дата регистрации',
                    'Количество нажатых кнопок',
                    'Название последней нажатой кнопки',
                    'Последний раз был активен',
                ],
            )
            for i, user in enumerate(users):
                statistic = statistics_[i]

                username = '@' + user.username if user.username else 'не установлен'
                last_pressed_button = (
                    last_pressed_button if (last_pressed_button := statistic.last_pressed_button)
                    else 'нажатий не было'
                )

                writer.writerow(
                    [
                        username,
                        user.wr_fullname,
                        user.squad_name,
                        user.status,
                        user.points,
                        f'{datetime.strftime(user.created_at, "%d.%m.%Y, %H:%M:%S")} по МСК',
                        statistic.presses,
                        last_pressed_button,
                        f'{datetime.strftime(statistic.last_activity_date, "%d.%m.%Y, %H:%M:%S")} по МСК'
                    ],
                )

        workbook = Workbook()
        worksheet = workbook.active
        with open(csv_path, 'r') as f:
            for row in csv.reader(f):
                correct_row = []
                for column in row:
                    if column.isdigit():
                        column = int(column)  # type: ignore[assignment]
                    correct_row.append(column)
                worksheet.append(correct_row)
        workbook.save(xlsx_path)
        os.remove(csv_path)

        return str(xlsx_path)
