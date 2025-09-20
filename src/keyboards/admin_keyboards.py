from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_admin_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="🍽️ Управление меню")],
            [KeyboardButton(text="📦 Заказы")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_menu_management_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить категорию", callback_data="add_category")],
            [InlineKeyboardButton(text="➕ Добавить товар", callback_data="add_item")],
            [InlineKeyboardButton(text="✏️ Редактировать категории", callback_data="edit_categories")],
            [InlineKeyboardButton(text="✏️ Редактировать товары", callback_data="edit_items")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
        ]
    )
    return keyboard

def get_orders_management_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Все заказы", callback_data="all_orders")],
            [InlineKeyboardButton(text="✅ Выполнить заказ", callback_data="complete_order")],
            [InlineKeyboardButton(text="❌ Отменить заказ", callback_data="cancel_order")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
        ]
    )
    return keyboard

def get_categories_keyboard(categories):
    buttons = []
    for category in categories:
        buttons.append([InlineKeyboardButton(text=category.name, callback_data=f"edit_category_{category.id}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_management")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_items_keyboard(items):
    buttons = []
    for item in items:
        buttons.append([InlineKeyboardButton(text=f"{item.name} - {item.price} руб.", callback_data=f"edit_item_{item.id}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_management")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_category_edit_keyboard(category_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Изменить название", callback_data=f"edit_category_name_{category_id}")],
            [InlineKeyboardButton(text="🗑️ Удалить категорию", callback_data=f"delete_category_{category_id}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="edit_categories")]
        ]
    )
    return keyboard

def get_item_edit_keyboard(item_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Изменить название", callback_data=f"edit_item_name_{item_id}")],
            [InlineKeyboardButton(text="✏️ Изменить описание", callback_data=f"edit_item_desc_{item_id}")],
            [InlineKeyboardButton(text="✏️ Изменить цену", callback_data=f"edit_item_price_{item_id}")],
            [InlineKeyboardButton(text="🗑️ Удалить товар", callback_data=f"delete_item_{item_id}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="edit_items")]
        ]
    )
    return keyboard

def get_admin_back_inline_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
        ]
    )
    return keyboard
