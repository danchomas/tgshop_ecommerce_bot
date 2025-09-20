from aiogram import Router, F, types
from services.auth_service import AuthService

command_router = Router()

@command_router.message(F.text == "/start")
async def start_command(message: types.Message):
    await message.reply('Hello! Welcome to the TGShop E-commerce Bot.')

@command_router.message(F.text == "/help")
async def help_command(message: types.Message):
    await message.answer("Help!")

@command_router.message(F.text == "/admin")
async def admin_command(message: types.Message):
    user = AuthService(message.from_user.id)
    if await user.isAdmin():
        await message.answer("Admin!")
    else:
        await message.answer("You are not authorized to use this command.")
