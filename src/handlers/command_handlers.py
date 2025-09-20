from aiogram import Router, F, types

command_router = Router()

@command_router.message(F.text == "/start")
async def start_command(message: types.Message):
    await message.reply('Hello! Welcome to the TGShop E-commerce Bot.')

@command_router.message(F.text == "/help")
async def help_command(message: types.Message):
    await message.answer("Help!")
