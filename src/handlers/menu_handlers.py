# Обработчики меню
from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from data.database import get_db
from services.category_services import CategoryGetService
from services.item_services import ItemGetService
from keyboards.user_keyboards import get_back_to_main_keyboard, get_back_to_main_inline_keyboard
import logging

# Роутер для меню
menu_router = Router()

# Состояния для просмотра меню
class MenuStates(StatesGroup):
    viewing_category = State()

# Показ меню по кнопке и команде
@menu_router.message(F.text == "📋 Меню")
@menu_router.message(F.text == "/menu")
async def show_menu(message: types.Message):
    db_gen = get_db()
    db = next(db_gen)
    category_get_service = CategoryGetService(db)
    categories = category_get_service.get_all_categories()
    db.close()

    if not categories:
        await message.answer("📋 Меню пока пустое.", reply_markup=get_back_to_main_keyboard())
        return

    category_buttons = []
    for category in categories:
        category_buttons.append([types.KeyboardButton(text=category.name)])

    category_buttons.append([types.KeyboardButton(text="⬅️ Назад")])

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=category_buttons,
        resize_keyboard=True
    )

    await message.answer("📋 <b>Выберите категорию:</b>", reply_markup=keyboard, parse_mode="HTML")

# Показ товаров в выбранной категории
@menu_router.message(F.text.regexp(r'^[A-Za-zА-Яа-яЁё0-9\s\-_]+$'))
async def show_category_items(message: types.Message):
    category_name = message.text

    if category_name in ["⬅️ Назад", "📋 Меню", "🛒 Корзина", "❓ Помощь", "📊 Статистика", "🍽️ Управление меню", "📦 Заказы"]:
        return

    db_gen = get_db()
    db = next(db_gen)
    category_get_service = CategoryGetService(db)
    item_get_service = ItemGetService(db)

    categories = category_get_service.get_all_categories()
    category = None
    for cat in categories:
        if cat.name == category_name:
            category = cat
            break

    if not category:
        db.close()
        await message.answer("Категория не найдена.", reply_markup=get_back_to_main_keyboard())
        return

    items = item_get_service.get_items_by_category(category.id)
    db.close()

    if not items:
        await message.answer(f"В категории <b>{category_name}</b> пока нет товаров.", reply_markup=get_back_to_main_keyboard(), parse_mode="HTML")
        return

    items_text = f"🍽️ <b>{category_name}</b>\n\n"
    item_buttons = []

    for item in items:
        items_text += f"<b>{item.name}</b> - {item.price:.2f} руб.\n"
        items_text += f"{item.description}\n\n"
        item_buttons.append([types.InlineKeyboardButton(
            text=f"🛒 {item.name} - {item.price:.2f} руб.",
            callback_data=f"add_to_cart_{item.id}"
        )])

    item_buttons.append([types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories")])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=item_buttons)

    await message.answer(items_text, reply_markup=keyboard, parse_mode="HTML")

# Добавление товара в корзину
@menu_router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: types.CallbackQuery):
    try:
        item_id = int(callback.data.split("_")[3])
        user_id = callback.from_user.id

        db_gen = get_db()
        db = next(db_gen)
        item_get_service = ItemGetService(db)
        item = item_get_service.get_item(item_id)
        db.close()

        if not item:
            await callback.answer("Товар не найден!")
            return

        from services.cart_service import CartService
        cart_service = CartService()
        success = cart_service.add_to_cart(user_id, item_id)

        if success:
            await callback.answer(f"Товар '{item.name}' добавлен в корзину!")
        else:
            await callback.answer("Ошибка при добавлении товара!")

    except Exception as e:
        logging.error(f"Ошибка при добавлении в корзину: {e}")
        await callback.answer("Произошла ошибка!")

# Возврат к категориям
@menu_router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: types.CallbackQuery):
    await callback.message.edit_text("📋 <b>Выберите категорию:</b>", reply_markup=get_back_to_main_inline_keyboard(), parse_mode="HTML")
    await callback.answer()
