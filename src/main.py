import asyncio
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handlers.command_handlers import command_router
from handlers.admin_handlers import admin_router
from handlers.cart_handler import cart_router
from handlers.menu_handlers import menu_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)

load_dotenv()

# Проверка наличия токена
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")

ADMIN_ID = os.getenv("ADMIN_ID")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID не найден в .env файле")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Подключаем все роутеры
dp.include_router(command_router)
dp.include_router(admin_router)
dp.include_router(cart_router)
dp.include_router(menu_router)

async def main():
    logging.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
