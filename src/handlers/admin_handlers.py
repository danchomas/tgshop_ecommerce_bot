from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.admin_keyboards import *
from data.database import get_db
from services.auth_service import AuthService
from services.category_services import (
    CategoryGetService, CategoryAddService, CategoryEditService, CategoryDeleteService
)
from services.item_services import (
    ItemGetService, ItemAddService, ItemEditService, ItemDeleteService
)

admin_router = Router()

class AdminStates(StatesGroup):
    waiting_for_category_name = State()
    waiting_for_category_key = State()
    waiting_for_item_name = State()
    waiting_for_item_description = State()
    waiting_for_item_price = State()
    waiting_for_item_category = State()
    waiting_for_edit_category_name = State()
    waiting_for_edit_item_name = State()
    waiting_for_edit_item_description = State()
    waiting_for_edit_item_price = State()

@admin_router.message(F.text == "/admin")
async def admin_start(message: types.Message):
    user = AuthService(message.from_user.id)
    if await user.isAdmin():
        await message.answer("Добро пожаловать в админ-панель!", reply_markup=get_admin_main_keyboard())
    else:
        await message.answer("У вас нет доступа к админ-панели.")

@admin_router.message(F.text == "🍽️ Управление меню")
async def menu_management(message: types.Message):
    user = AuthService(message.from_user.id)
    if await user.isAdmin():
        await message.answer("Управление меню:", reply_markup=get_menu_management_keyboard())
    else:
        await message.answer("У вас нет доступа.")

@admin_router.message(F.text == "📦 Заказы")
async def orders_management(message: types.Message):
    user = AuthService(message.from_user.id)
    if await user.isAdmin():
        await message.answer("Управление заказами:", reply_markup=get_orders_management_keyboard())
    else:
        await message.answer("У вас нет доступа.")

@admin_router.callback_query(F.data == "add_category")
async def add_category_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите ключ категории (латинские буквы, без пробелов):")
    await state.set_state(AdminStates.waiting_for_category_key)

@admin_router.message(AdminStates.waiting_for_category_key)
async def add_category_key_received(message: types.Message, state: FSMContext):
    await state.update_data(category_key=message.text)
    await message.answer("Введите название категории:")
    await state.set_state(AdminStates.waiting_for_category_name)

@admin_router.message(AdminStates.waiting_for_category_name)
async def add_category_name_received(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    category_key = user_data['category_key']
    category_name = message.text

    db_gen = get_db()
    db = next(db_gen)

    try:
        category_add_service = CategoryAddService(db)
        category = category_add_service.add_category(category_key, category_name)
        if category:
            await message.answer(f"Категория '{category_name}' успешно добавлена!")
        else:
            await message.answer("Ошибка при добавлении категории")
    except Exception as e:
        await message.answer(f"Ошибка при добавлении категории: {str(e)}")
    finally:
        db.close()

    await state.clear()
    await message.answer("Управление меню:", reply_markup=get_menu_management_keyboard())

@admin_router.callback_query(F.data == "add_item")
async def add_item_start(callback: types.CallbackQuery, state: FSMContext):
    db_gen = get_db()
    db = next(db_gen)
    category_get_service = CategoryGetService(db)
    categories = category_get_service.get_all_categories()
    db.close()

    if not categories:
        await callback.message.edit_text("Сначала создайте хотя бы одну категорию!")
        return

    # Создаем клавиатуру с категориями
    category_buttons = []
    for category in categories:
        category_buttons.append([types.InlineKeyboardButton(text=category.name, callback_data=f"select_category_{category.id}")])
    category_buttons.append([types.InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_management")])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=category_buttons)
    await callback.message.edit_text("Выберите категорию для товара:", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_item_category)

@admin_router.callback_query(F.data.startswith("select_category_"))
async def category_selected(callback: types.CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[2])
    await state.update_data(item_category_id=category_id)
    await callback.message.edit_text("Введите название товара:")
    await state.set_state(AdminStates.waiting_for_item_name)

@admin_router.message(AdminStates.waiting_for_item_name)
async def item_name_received(message: types.Message, state: FSMContext):
    await state.update_data(item_name=message.text)
    await message.answer("Введите описание товара:")
    await state.set_state(AdminStates.waiting_for_item_description)

@admin_router.message(AdminStates.waiting_for_item_description)
async def item_description_received(message: types.Message, state: FSMContext):
    await state.update_data(item_description=message.text)
    await message.answer("Введите цену товара:")
    await state.set_state(AdminStates.waiting_for_item_price)

@admin_router.message(AdminStates.waiting_for_item_price)
async def item_price_received(message: types.Message, state: FSMContext):
    try:
        price = float(message.text.replace(',', '.'))
        if price <= 0:
            raise ValueError("Цена должна быть положительной")
    except ValueError:
        await message.answer("Пожалуйста, введите корректную цену (например, 100.50):")
        return

    user_data = await state.get_data()
    category_id = user_data['item_category_id']
    name = user_data['item_name']
    description = user_data['item_description']

    db_gen = get_db()
    db = next(db_gen)

    try:
        item_add_service = ItemAddService(db)
        item = item_add_service.add_item(name, description, price, category_id)
        if item:
            await message.answer(f"Товар '{name}' успешно добавлен!")
        else:
            await message.answer("Ошибка при добавлении товара")
    except Exception as e:
        await message.answer(f"Ошибка при добавлении товара: {str(e)}")
    finally:
        db.close()

    await state.clear()
    await message.answer("Управление меню:", reply_markup=get_menu_management_keyboard())

@admin_router.callback_query(F.data == "edit_categories")
async def edit_categories(callback: types.CallbackQuery):
    db_gen = get_db()
    db = next(db_gen)
    category_get_service = CategoryGetService(db)
    categories = category_get_service.get_all_categories()
    db.close()

    if not categories:
        await callback.message.edit_text("Категории не найдены!")
        return

    keyboard = get_categories_keyboard(categories)
    await callback.message.edit_text("Выберите категорию для редактирования:", reply_markup=keyboard)

@admin_router.callback_query(F.data == "edit_items")
async def edit_items(callback: types.CallbackQuery):
    db_gen = get_db()
    db = next(db_gen)
    item_get_service = ItemGetService(db)
    items = item_get_service.get_all_items()
    db.close()

    if not items:
        await callback.message.edit_text("Товары не найдены!")
        return

    keyboard = get_items_keyboard(items)
    await callback.message.edit_text("Выберите товар для редактирования:", reply_markup=keyboard)

@admin_router.callback_query(F.data.startswith("edit_category_"))
async def edit_category(callback: types.CallbackQuery):
    category_id = int(callback.data.split("_")[2])
    keyboard = get_category_edit_keyboard(category_id)
    await callback.message.edit_text("Выберите действие:", reply_markup=keyboard)

@admin_router.callback_query(F.data.startswith("edit_category_name_"))
async def edit_category_name_start(callback: types.CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[3])
    await state.update_data(editing_category_id=category_id)
    await callback.message.edit_text("Введите новое название категории:")
    await state.set_state(AdminStates.waiting_for_edit_category_name)

@admin_router.message(AdminStates.waiting_for_edit_category_name)
async def edit_category_name_received(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    category_id = user_data['editing_category_id']
    new_name = message.text

    db_gen = get_db()
    db = next(db_gen)

    try:
        category_edit_service = CategoryEditService(db)
        category = category_edit_service.update_category(category_id, name=new_name)
        if category:
            await message.answer(f"Название категории изменено на '{new_name}'")
        else:
            await message.answer("Ошибка при изменении категории")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
    finally:
        db.close()

    await state.clear()
    await message.answer("Управление меню:", reply_markup=get_menu_management_keyboard())

@admin_router.callback_query(F.data.startswith("delete_category_"))
async def delete_category_confirm(callback: types.CallbackQuery):
    category_id = int(callback.data.split("_")[2])
    db_gen = get_db()
    db = next(db_gen)
    category_get_service = CategoryGetService(db)
    category = category_get_service.get_category(category_id)
    db.close()

    if category:
        confirm_keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_category_{category_id}")],
                [types.InlineKeyboardButton(text="❌ Отмена", callback_data="edit_categories")]
            ]
        )
        await callback.message.edit_text(f"Вы уверены, что хотите удалить категорию '{category.name}'? Все товары в этой категории также будут удалены.", reply_markup=confirm_keyboard)
    else:
        await callback.message.edit_text("Категория не найдена!")

@admin_router.callback_query(F.data.startswith("confirm_delete_category_"))
async def delete_category_confirmed(callback: types.CallbackQuery):
    category_id = int(callback.data.split("_")[3])

    db_gen = get_db()
    db = next(db_gen)

    try:
        category_delete_service = CategoryDeleteService(db)
        success = category_delete_service.delete_category(category_id)
        if success:
            await callback.message.edit_text("Категория успешно удалена!")
        else:
            await callback.message.edit_text("Ошибка при удалении категории")
    except Exception as e:
        await callback.message.edit_text(f"Ошибка: {str(e)}")
    finally:
        db.close()

    await callback.message.answer("Управление меню:", reply_markup=get_menu_management_keyboard())

@admin_router.callback_query(F.data.startswith("edit_item_"))
async def edit_item(callback: types.CallbackQuery):
    item_id = int(callback.data.split("_")[2])
    keyboard = get_item_edit_keyboard(item_id)
    await callback.message.edit_text("Выберите действие:", reply_markup=keyboard)

@admin_router.callback_query(F.data.startswith("edit_item_name_"))
async def edit_item_name_start(callback: types.CallbackQuery, state: FSMContext):
    item_id = int(callback.data.split("_")[3])
    await state.update_data(editing_item_id=item_id)
    await callback.message.edit_text("Введите новое название товара:")
    await state.set_state(AdminStates.waiting_for_edit_item_name)

@admin_router.message(AdminStates.waiting_for_edit_item_name)
async def edit_item_name_received(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    item_id = user_data['editing_item_id']
    new_name = message.text

    db_gen = get_db()
    db = next(db_gen)

    try:
        item_edit_service = ItemEditService(db)
        item = item_edit_service.update_item_name(item_id, new_name)
        if item:
            await message.answer(f"Название товара изменено на '{new_name}'")
        else:
            await message.answer("Ошибка при изменении товара")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
    finally:
        db.close()

    await state.clear()
    await message.answer("Управление меню:", reply_markup=get_menu_management_keyboard())

@admin_router.callback_query(F.data.startswith("edit_item_desc_"))
async def edit_item_desc_start(callback: types.CallbackQuery, state: FSMContext):
    item_id = int(callback.data.split("_")[3])
    await state.update_data(editing_item_id=item_id)
    await callback.message.edit_text("Введите новое описание товара:")
    await state.set_state(AdminStates.waiting_for_edit_item_description)

@admin_router.message(AdminStates.waiting_for_edit_item_description)
async def edit_item_desc_received(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    item_id = user_data['editing_item_id']
    new_description = message.text

    db_gen = get_db()
    db = next(db_gen)

    try:
        item_edit_service = ItemEditService(db)
        item = item_edit_service.update_item_description(item_id, new_description)
        if item:
            await message.answer("Описание товара успешно изменено")
        else:
            await message.answer("Ошибка при изменении описания")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
    finally:
        db.close()

    await state.clear()
    await message.answer("Управление меню:", reply_markup=get_menu_management_keyboard())

@admin_router.callback_query(F.data.startswith("edit_item_price_"))
async def edit_item_price_start(callback: types.CallbackQuery, state: FSMContext):
    item_id = int(callback.data.split("_")[3])
    await state.update_data(editing_item_id=item_id)
    await callback.message.edit_text("Введите новую цену товара:")
    await state.set_state(AdminStates.waiting_for_edit_item_price)

@admin_router.message(AdminStates.waiting_for_edit_item_price)
async def edit_item_price_received(message: types.Message, state: FSMContext):
    try:
        new_price = float(message.text.replace(',', '.'))
        if new_price <= 0:
            raise ValueError("Цена должна быть положительной")
    except ValueError:
        await message.answer("Пожалуйста, введите корректную цену (например, 100.50):")
        return

    user_data = await state.get_data()
    item_id = user_data['editing_item_id']

    db_gen = get_db()
    db = next(db_gen)

    try:
        item_edit_service = ItemEditService(db)
        item = item_edit_service.update_item_price(item_id, new_price)
        if item:
            await message.answer(f"Цена товара изменена на {new_price:.2f}")
        else:
            await message.answer("Ошибка при изменении цены")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
    finally:
        db.close()

    await state.clear()
    await message.answer("Управление меню:", reply_markup=get_menu_management_keyboard())

@admin_router.callback_query(F.data.startswith("delete_item_"))
async def delete_item_confirm(callback: types.CallbackQuery):
    item_id = int(callback.data.split("_")[2])
    db_gen = get_db()
    db = next(db_gen)
    item_get_service = ItemGetService(db)
    item = item_get_service.get_item(item_id)
    db.close()

    if item:
        confirm_keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_item_{item_id}")],
                [types.InlineKeyboardButton(text="❌ Отмена", callback_data="edit_items")]
            ]
        )
        await callback.message.edit_text(f"Вы уверены, что хотите удалить товар '{item.name}'?", reply_markup=confirm_keyboard)
    else:
        await callback.message.edit_text("Товар не найден!")

@admin_router.callback_query(F.data.startswith("confirm_delete_item_"))
async def delete_item_confirmed(callback: types.CallbackQuery):
    item_id = int(callback.data.split("_")[3])

    db_gen = get_db()
    db = next(db_gen)

    try:
        item_delete_service = ItemDeleteService(db)
        success = item_delete_service.delete_item(item_id)
        if success:
            await callback.message.edit_text("Товар успешно удален!")
        else:
            await callback.message.edit_text("Ошибка при удалении товара")
    except Exception as e:
        await callback.message.edit_text(f"Ошибка: {str(e)}")
    finally:
        db.close()

    await callback.message.answer("Управление меню:", reply_markup=get_menu_management_keyboard())

@admin_router.callback_query(F.data == "admin_back")
async def admin_back(callback: types.CallbackQuery):
    await callback.message.edit_text("Добро пожаловать в админ-панель!", reply_markup=get_admin_main_keyboard())
