import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, Router, F

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
router = Router()

@router.message(F.text == "/start")
async def start_command(message: types.Message):
    await message.reply('Hello! Welcome to the TGShop E-commerce Bot.')

dp.include_router(router)

asyncio.run(dp.start_polling(bot))
