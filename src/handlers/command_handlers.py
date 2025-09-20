# Обработчики команд
from aiogram import Router, F, types
from services.auth_service import AuthService
from keyboards.user_keyboards import get_main_menu_keyboard, get_back_to_main_inline_keyboard

# Роутер для команд
command_router = Router()

# Обработчик команды /start
@command_router.message(F.text == "/start")
async def start_command(message: types.Message):
    welcome_text = """
🤖 <b>Добро пожаловать в TGShop!</b>

Здесь вы можете:
• 📋 Просмотреть меню
• 🛒 Сделать заказ
• ❓ Получить помощь

Используйте кнопки внизу экрана для навигации.
    """
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")

# Обработчик команды /help и кнопки помощи
@command_router.message(F.text == "/help")
@command_router.message(F.text == "❓ Помощь")
async def help_command(message: types.Message):
    help_text = """
🤖 <b>Помощь по боту TGShop</b>

<b>Основные команды:</b>
/start - Начать работу с ботом
/help - Показать помощь
/menu - Просмотреть меню
/cart - Просмотреть корзину

<b>Как сделать заказ:</b>
1. Нажмите "📋 Меню"
2. Выберите категорию
3. Добавьте товары в корзину
4. Перейдите в корзину и оформите заказ

<b>Для администраторов:</b>
/admin - Админ-панель
    """
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())

# Обработчик команды /admin
@command_router.message(F.text == "/admin")
async def admin_command(message: types.Message):
    user = AuthService(message.from_user.id)
    is_admin = await user.isAdmin()

    print(f"User ID: {message.from_user.id}")
    print(f"Is admin: {is_admin}")

    if is_admin:
        from keyboards.admin_keyboards import get_admin_main_keyboard
        await message.answer("👑 <b>Админ-панель</b>", reply_markup=get_admin_main_keyboard(), parse_mode="HTML")
    else:
        await message.answer("🚫 У вас нет доступа к админ-панели.", reply_markup=get_main_menu_keyboard())

# Обработчик кнопки "Назад"
@command_router.message(F.text == "⬅️ Назад")
async def go_back(message: types.Message):
    await message.answer("🏠 <b>Главное меню</b>", reply_markup=get_main_menu_keyboard(), parse_mode="HTML")

# Обработчик callback "Назад в главное меню"
@command_router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text("🏠 <b>Главное меню</b>", reply_markup=get_back_to_main_inline_keyboard(), parse_mode="HTML")
    await callback.answer()
