import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext

from database import CommonUser
from keyboards import (
    custom_cd,
    mailing_kb,
)
from loader import (
    PostgresSession,
    bot,
    dp,
)
from logger import logger


@dp.callback_query_handler(custom_cd('mailing_all_common_users').filter(), state='*')
async def mailing_all_common_users(call: types.CallbackQuery, state: FSMContext):
    logger.debug(f'Admin {call.from_user.id} enters mailing_all_common_users handler')

    await call.message.edit_reply_markup()
    await call.message.answer(
        'Напишите сообщение, которые хотите разослать всем бойцам ССО. '
        'Если Вы хотите выйти из режима рассылки, пришлите боту '
        'сообщение "Назад" (без кавычек)'
    )
    await state.set_state('send_message_to_all_common_users')


@dp.message_handler(state='send_message_to_all_common_users')
async def receive_message_to_all_common_users(message: types.Message, state: FSMContext):
    logger.debug(f'Admin {message.from_user.id} enters receive_message_to_all_common_users handler')

    message_text = message.text
    if message_text.lower() == 'назад':
        await message.answer('Процесс рассылки бойцам ССО был отменен', reply_markup=mailing_kb())
    else:
        with PostgresSession.begin() as session:
            for common_user in session.query(CommonUser).all():
                await bot.send_message(common_user.id, text=message_text)
                await asyncio.sleep(.05)

        await message.answer(
            f'Ваше сообщение было успешно разослано всем активным бойцам ССО',
            reply_markup=mailing_kb(),
        )

    await state.finish()
