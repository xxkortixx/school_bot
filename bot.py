import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook

import questions as questions
import teacher_panel as teacher_panel
from config import bot_token

logging.basicConfig(level=logging.INFO)

bot = Bot(token=bot_token)

dp = Dispatcher()

dp.include_router(questions.router)
dp.include_router(teacher_panel.router)

async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



#█▄▄ █▄█   █▀█ █▀█ █░█ █░░ █▀▀ █▄░█ ▀█▀ █▀▄ ▄▀█ █▀█ █▄▀
#█▄█ ░█░   █▄█ █▀▀ █▄█ █▄▄ ██▄ █░▀█ ░█░ █▄▀ █▀█ █▀▄ █░█