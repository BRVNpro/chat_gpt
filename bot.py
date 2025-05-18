import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from handlers import (
    start,
    random_fact,
    gpt_interface,
    talk,
    quiz,
    translator,
    recommendations,
)
from utils.config import TELEGRAM_TOKEN
from utils.logger import setup_logger


async def main():
    setup_logger()

    bot = Bot(
        token=TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )

    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        start.router,
        random_fact.router,
        gpt_interface.router,
        talk.router,
        quiz.router,
        translator.router,
        recommendations.router,
    )

    await bot.set_my_commands([
        BotCommand(command="start", description="Запуск"),
        BotCommand(command="random", description="Рандомный факт"),
        BotCommand(command="gpt", description="Свободный вопрос к ChatGPT"),
        BotCommand(command="talk", description="Поговорить с личностью"),
        BotCommand(command="quiz", description="Квиз по теме"),
        BotCommand(command="translate", description="Переводчик"),
        BotCommand(command="recommend", description="Рекомендации"),
    ])

    print("✅ Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
