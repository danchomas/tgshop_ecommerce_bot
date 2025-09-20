from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from services.cart_service import CartService
from keyboards.cart_keyboards import *
from data.database import get_db
from services.item_services import ItemGetService

cart_router = Router()
cart_service = CartService()

class CartStates(StatesGroup):
    waiting_for_order_confirmation = State()

@cart_router.callback_query(F.data == "view_cart")
async def view_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    cart_items = cart_service.get_cart_items(user_id)
    total = cart_service.get_cart_total(user_id)

    if not cart_items:
        await callback.message.edit_text("Ваша корзина пуста!")
        return

    cart_text = "🛒 <b>Ваша корзина:</b>\n\n"
    for item, quantity in cart_items:
        cart_text += f"• {item.name} x{quantity} - {item.price * quantity:.2f} руб.\n"

    cart_text += f"\n<b>Итого: {total:.2f} руб.</b>"

    await callback.message.edit_text(cart_text, reply_markup=get_cart_keyboard(), parse_mode="HTML")

@cart_router.callback_query(F.data == "checkout")
async def checkout_start(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    cart_items = cart_service.get_cart_items(user_id)
    total = cart_service.get_cart_total(user_id)

    if not cart_items:
        await callback.message.edit_text("Ваша корзина пуста!")
        return

    order_text = "📦 <b>Подтверждение заказа:</b>\n\n"
    for item, quantity in cart_items:
        order_text += f"• {item.name} x{quantity} - {item.price * quantity:.2f} руб.\n"

    order_text += f"\n<b>Итого к оплате: {total:.2f} руб.</b>"
    order_text += "\n\nПодтвердите заказ?"

    await callback.message.edit_text(order_text, reply_markup=get_checkout_keyboard(), parse_mode="HTML")
    await state.set_state(CartStates.waiting_for_order_confirmation)

@cart_router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    cart_items = cart_service.get_cart_items(user_id)
    total = cart_service.get_cart_total(user_id)

    if not cart_items:
        await callback.message.edit_text("Ваша корзина пуста!")
        return

    # Здесь можно добавить логику обработки заказа
    # Например, сохранение в базу данных, отправка уведомления админу и т.д.

    # Очищаем корзину
    cart_service.clear_cart(user_id)

    # Отправляем уведомление админу (если нужно)
    # await notify_admin_about_order(callback.from_user, cart_items, total)

    await callback.message.edit_text("✅ Заказ успешно оформлен! Спасибо за покупку!")
    await state.clear()

@cart_router.callback_query(F.data == "cancel_order_process")
async def cancel_order_process(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🛒 <b>Ваша корзина:</b>", reply_markup=get_cart_keyboard(), parse_mode="HTML")
    await state.clear()

@cart_router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    cart_service.clear_cart(user_id)
    await callback.message.edit_text("Корзина очищена!")

@cart_router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: types.CallbackQuery):
    item_id = int(callback.data.split("_")[3])
    user_id = callback.from_user.id

    # Проверяем существование товара через ваш сервис
    db_gen = get_db()
    db = next(db_gen)
    item_get_service = ItemGetService(db)
    item = item_get_service.get_item(item_id)
    db.close()

    if not item:
        await callback.answer("Товар не найден!")
        return

    success = cart_service.add_to_cart(user_id, item_id)

    if success:
        await callback.answer("Товар добавлен в корзину!")
    else:
        await callback.answer("Ошибка при добавлении товара!")

@cart_router.callback_query(F.data.startswith("increase_"))
async def increase_quantity(callback: types.CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    cart = cart_service.get_cart(user_id)
    if item_id in cart:
        cart[item_id]["quantity"] += 1
        quantity = cart[item_id]["quantity"]
        await callback.message.edit_reply_markup(reply_markup=get_item_quantity_keyboard(item_id, quantity))
    await callback.answer()

@cart_router.callback_query(F.data.startswith("decrease_"))
async def decrease_quantity(callback: types.CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    cart = cart_service.get_cart(user_id)
    if item_id in cart and cart[item_id]["quantity"] > 1:
        cart[item_id]["quantity"] -= 1
        quantity = cart[item_id]["quantity"]
        await callback.message.edit_reply_markup(reply_markup=get_item_quantity_keyboard(item_id, quantity))
    await callback.answer()

@cart_router.callback_query(F.data.startswith("remove_"))
async def remove_from_cart(callback: types.CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    cart_service.remove_from_cart(user_id, item_id)
    await callback.message.edit_text("🛒 <b>Ваша корзина:</b>", reply_markup=get_cart_keyboard(), parse_mode="HTML")
    await callback.answer("Товар удален из корзины!")
