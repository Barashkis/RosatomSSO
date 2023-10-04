import csv
import os
from datetime import datetime
from typing import Sequence

from openpyxl import Workbook

from rosatom_sso.config import temp_dir_path
from rosatom_sso.database import (
    CommonUser,
    Statistic,
)

from .interfaces import UsersFileBuilder


class CommonUsersFileBuilder(UsersFileBuilder):
    @staticmethod
    def build_xlsx(users: Sequence[CommonUser], statistics_: Sequence[Statistic]) -> str:
        fp = f'{temp_dir_path}/common-users-{int(datetime.now().timestamp() * 100)}'
        csv_path = f'{fp}.csv'
        xlsx_path = f'{fp}.xlsx'

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
                        column = int(column)
                    correct_row.append(column)
                worksheet.append(correct_row)
        workbook.save(xlsx_path)
        os.remove(csv_path)

        return xlsx_path
