#  Copyright (c) 2022.
#  Author: Lyapin Ilya <nestyreff@ya.ru>
#  yrPartner
import os
from asyncio import run
from datetime import datetime
from logging import basicConfig, DEBUG
from pathlib import Path

from aiogram import Dispatcher, Bot, types
from aiogram.filters.command import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import SendMessage
from aiogram.utils.i18n import I18n

# теперь в любой файл это импортим
from aiogram.utils.i18n import gettext as _

# Кастомный определятор языка (я подкрутил, чтобы пользователь мог менять язык в настройках)
# можно использовать SimpleI18nMiddleware вместо этого
from aiogram.utils.i18n import SimpleI18nMiddleware

from mocked_bot import MockedBot


async def test(message: types.Message):
    user = message.from_user
    text = _("C {date} прошло {days} дней и {secs} секунд")
    return await message.answer(
        # обязательно используем .format, не нужно использовать f-строки
        text.format(**{"days": 1, "secs": 2, "date": datetime.now()})
    )


async def main():
    basicConfig(
        level=DEBUG
    )

    LOCALES = Path(__file__).parent / 'locales'
    i18n = I18n(path=LOCALES, domain='messages', default_locale='ru')
    i18n_instance = SimpleI18nMiddleware(i18n)

    dp = Dispatcher(MemoryStorage())
    dp.message.register(test, CommandStart())

    i18n_instance.setup(dp)

    bot = MockedBot(
        token=os.getenv('token'),
        parse_mode='HTML'
    )
    result: SendMessage = await dp.feed_update(
        bot=bot,
        update=types.Update(
            update_id=1,
            message=types.Message(
                message_id=1,
                from_user=types.User(username='some', id=123, is_bot=False, first_name='Ok'),
                text='/start',
                date=datetime.now(),
                chat=types.Chat(id=123, type='private')
            )
        )
    )
    assert result.text == f'C {datetime.now()} прошло 1 дней и 2 секунд'


if __name__ == '__main__':
    run(main())
