import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from handlers.command_handlers import command_router

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

dp.include_router(command_router)

asyncio.run(dp.start_polling(bot))
