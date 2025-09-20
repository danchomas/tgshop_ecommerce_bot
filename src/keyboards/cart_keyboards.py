from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_cart_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Оформить заказ", callback_data="checkout")],
            [InlineKeyboardButton(text="🗑️ Очистить корзину", callback_data="clear_cart")],
            [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")]
        ]
    )
    return keyboard

def get_item_quantity_keyboard(item_id, quantity):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➖", callback_data=f"decrease_{item_id}"),
             InlineKeyboardButton(text=str(quantity), callback_data=f"quantity_{item_id}"),
             InlineKeyboardButton(text="➕", callback_data=f"increase_{item_id}")],
            [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"remove_{item_id}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="view_cart")]
        ]
    )
    return keyboard

def get_checkout_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить заказ", callback_data="confirm_order")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_order_process")]
        ]
    )
    return keyboard
