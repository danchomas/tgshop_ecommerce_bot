# Админские обработчики
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

# Роутер для админских функций
admin_router = Router()

# Состояния для админских операций
class AdminStates(StatesGroup):
    waiting_for_category_name = State()
    waiting_for_category_key = State()
    waiting_for_item_name = State()
    waiting_for_item_description = State()
    waiting_for_item_price = State()
    waiting_for_item_category = State()
    waiting_for_edit_field = State()
    waiting_for_edit_value = State()


# Обработчик команды /admin
@admin_router.message(F.text == "/admin")
async def admin_start(message: types.Message):
    user = AuthService(message.from_user.id)
    if await user.isAdmin():
        await message.answer("Добро пожаловать в админ-панель!", reply_markup=get_admin_main_keyboard())
    else:
        await message.answer("У вас нет доступа к админ-панели.")


# Обработчик кнопки "Управление меню"
@admin_router.message(F.text == "🍽️ Управление меню")
async def menu_management(message: types.Message):
    user = AuthService(message.from_user.id)
    if await user.isAdmin():
        await message.answer("Управление меню:", reply_markup=get_menu_management_keyboard())
    else:
        await message.answer("У вас нет доступа.")


# Обработчик кнопки "Заказы"
@admin_router.message(F.text == "📦 Заказы")
async def orders_management(message: types.Message):
    user = AuthService(message.from_user.id)
    if await user.isAdmin():
        await message.answer("Управление заказами:", reply_markup=get_orders_management_keyboard())
    else:
        await message.answer("У вас нет доступа.")


# Начало добавления категории
@admin_router.callback_query(F.data == "add_category")
async def add_category_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите ключ категории (латинские буквы, без пробелов):")
    await state.set_state(AdminStates.waiting_for_category_key)


# Получение ключа категории
@admin_router.message(AdminStates.waiting_for_category_key)
async def add_category_key_received(message: types.Message, state: FSMContext):
    await state.update_data(category_key=message.text)
    await message.answer("Введите название категории:")
    await state.set_state(AdminStates.waiting_for_category_name)


# Получение названия категории и добавление в БД
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


# Начало добавления товара
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

    category_buttons = []
    for category in categories:
        category_buttons.append([types.InlineKeyboardButton(text=category.name, callback_data=f"select_category_{category.id}")])
    category_buttons.append([types.InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_management")])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=category_buttons)
    await callback.message.edit_text("Выберите категорию для товара:", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_item_category)


# Выбор категории для товара
@admin_router.callback_query(F.data.startswith("select_category_"))
async def category_selected(callback: types.CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[2])
    await state.update_data(item_category_id=category_id)
    await callback.message.edit_text("Введите название товара:")
    await state.set_state(AdminStates.waiting_for_item_name)


# Получение названия товара
@admin_router.message(AdminStates.waiting_for_item_name)
async def item_name_received(message: types.Message, state: FSMContext):
    await state.update_data(item_name=message.text)
    await message.answer("Введите описание товара:")
    await state.set_state(AdminStates.waiting_for_item_description)


# Получение описания товара
@admin_router.message(AdminStates.waiting_for_item_description)
async def item_description_received(message: types.Message, state: FSMContext):
    await state.update_data(item_description=message.text)
    await message.answer("Введите цену товара:")
    await state.set_state(AdminStates.waiting_for_item_price)


# Получение цены товара и добавление в БД
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


# Редактирование категорий — ВЫБОР КАТЕГОРИИ
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


# Редактирование товаров — ВЫБОР ТОВАРА
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
async def edit_category_start(callback: types.CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[2])
    await state.update_data(editing_category_id=category_id, editing_target="category")

    # Клавиатура выбора поля (пока только название)
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="✏️ Название", callback_data="edit_field_name")],
            [types.InlineKeyboardButton(text="❌ Отмена", callback_data="edit_categories")],
        ]
    )
    await callback.message.edit_text("Выберите поле для редактирования:", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_edit_field)


@admin_router.callback_query(F.data.startswith("edit_item_"))
async def edit_item_start(callback: types.CallbackQuery, state: FSMContext):
    item_id = int(callback.data.split("_")[2])
    await state.update_data(editing_item_id=item_id, editing_target="item")

    # Клавиатура выбора поля
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="✏️ Название", callback_data="edit_field_name")],
            [types.InlineKeyboardButton(text="📝 Описание", callback_data="edit_field_description")],
            [types.InlineKeyboardButton(text="💰 Цена", callback_data="edit_field_price")],
            [types.InlineKeyboardButton(text="❌ Отмена", callback_data="edit_items")],
        ]
    )
    await callback.message.edit_text("Выберите поле для редактирования:", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_edit_field)


# Обработка выбора поля для редактирования (и категории, и товара)
@admin_router.callback_query(AdminStates.waiting_for_edit_field)
async def edit_field_selected(callback: types.CallbackQuery, state: FSMContext):
    field_map = {
        "edit_field_name": ("Введите новое название:", AdminStates.waiting_for_edit_value, "name"),
        "edit_field_description": ("Введите новое описание:", AdminStates.waiting_for_edit_value, "description"),
        "edit_field_price": ("Введите новую цену:", AdminStates.waiting_for_edit_value, "price"),
    }

    if callback.data not in field_map:
        await callback.answer("Неизвестное действие")
        return

    prompt, next_state, field_name = field_map[callback.data]
    await state.update_data(editing_field=field_name)
    await callback.message.edit_text(prompt)
    await state.set_state(next_state)


# Получение нового значения и обновление в БД (универсальный обработчик)
@admin_router.message(AdminStates.waiting_for_edit_value)
async def edit_value_received(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    target = user_data.get('editing_target')
    field = user_data['editing_field']
    new_value = message.text

    # Валидация цены
    if field == "price":
        try:
            new_value = float(new_value.replace(',', '.'))
            if new_value <= 0:
                raise ValueError
        except ValueError:
            await message.answer("Пожалуйста, введите корректную цену (например, 100.50):")
            return

    db_gen = get_db()
    db = next(db_gen)

    try:
        if target == "category":
            category_id = user_data['editing_category_id']
            category_edit_service = CategoryEditService(db)
            if field == "name":
                obj = category_edit_service.update_category(category_id, name=new_value)
            else:
                await message.answer("Недопустимое поле для категории")
                return

        elif target == "item":
            item_id = user_data['editing_item_id']
            item_edit_service = ItemEditService(db)
            if field == "name":
                obj = item_edit_service.update_item_name(item_id, new_value)
            elif field == "description":
                obj = item_edit_service.update_item_description(item_id, new_value)
            elif field == "price":
                obj = item_edit_service.update_item_price(item_id, new_value)
            else:
                await message.answer("Недопустимое поле для товара")
                return

        if obj:
            if field == "price":
                await message.answer(f"Цена изменена на {new_value:.2f}")
            else:
                await message.answer(f"Поле '{field}' успешно обновлено!")
        else:
            await message.answer(f"Ошибка при обновлении {target}")

    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
    finally:
        db.close()

    await state.clear()

    # Возврат в соответствующее меню
    if target == "category":
        await message.answer("Управление меню:", reply_markup=get_menu_management_keyboard())
    else:
        await message.answer("Управление меню:", reply_markup=get_menu_management_keyboard())


# Подтверждение удаления категории
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


# Удаление категории из БД
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


# Подтверждение удаления товара
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


# Удаление товара из БД
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


# Возврат в админ-панель
@admin_router.callback_query(F.data == "admin_back")
async def admin_back(callback: types.CallbackQuery):
    from keyboards.admin_keyboards import get_admin_back_inline_keyboard
    await callback.message.edit_text("Добро пожаловать в админ-панель!", reply_markup=get_admin_back_inline_keyboard())
    await callback.answer()
