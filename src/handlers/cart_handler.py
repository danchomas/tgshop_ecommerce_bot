from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from services.cart_service import CartService
from keyboards.cart_keyboards import *
from keyboards.user_keyboards import get_main_menu_keyboard, get_back_to_main_inline_keyboard, get_cart_keyboard
from data.database import get_db
from services.item_services import ItemGetService
import logging

cart_router = Router()
cart_service = CartService()

class CartStates(StatesGroup):
    waiting_for_order_confirmation = State()

@cart_router.message(F.text == "🛒 Корзина")
@cart_router.message(F.text == "/cart")
async def show_cart(message: types.Message):
    user_id = message.from_user.id
    cart_items = cart_service.get_cart_items(user_id)

    if not cart_items:
        await message.answer("🛒 <b>Ваша корзина пуста!</b>\n\nДобавьте товары из меню.",
                           reply_markup=get_main_menu_keyboard(), parse_mode="HTML")
        return

    cart_text = "🛒 <b>Ваша корзина:</b>\n\n"
    total = 0

    for item, quantity in cart_items:
        item_total = item.price * quantity
        total += item_total
        cart_text += f"🍽️ <b>{item.name}</b>\n"
        cart_text += f"   {quantity} x {item.price:.2f} руб. = {item_total:.2f} руб.\n\n"

    cart_text += f"<b>Итого: {total:.2f} руб.</b>"

    await message.answer(cart_text, reply_markup=get_cart_keyboard(), parse_mode="HTML")

@cart_router.callback_query(F.data == "view_cart")
async def view_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    cart_items = cart_service.get_cart_items(user_id)

    if not cart_items:
        await callback.message.edit_text("🛒 <b>Ваша корзина пуста!</b>\n\nДобавьте товары из меню.",
                                       reply_markup=get_back_to_main_inline_keyboard(), parse_mode="HTML")
        return

    cart_text = "🛒 <b>Ваша корзина:</b>\n\n"
    total = 0

    for item, quantity in cart_items:
        item_total = item.price * quantity
        total += item_total
        cart_text += f"🍽️ <b>{item.name}</b>\n"
        cart_text += f"   {quantity} x {item.price:.2f} руб. = {item_total:.2f} руб.\n\n"

    cart_text += f"<b>Итого: {total:.2f} руб.</b>"

    await callback.message.edit_text(cart_text, reply_markup=get_cart_keyboard(), parse_mode="HTML")
    await callback.answer()

@cart_router.callback_query(F.data == "checkout")
async def checkout_start(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    cart_items = cart_service.get_cart_items(user_id)

    if not cart_items:
        await callback.message.edit_text("🛒 <b>Ваша корзина пуста!</b>",
                                       reply_markup=get_main_menu_keyboard(), parse_mode="HTML")
        return

    order_text = "📦 <b>Подтверждение заказа:</b>\n\n"
    total = 0

    for item, quantity in cart_items:
        item_total = item.price * quantity
        total += item_total
        order_text += f"🍽️ <b>{item.name}</b>\n"
        order_text += f"   {quantity} x {item.price:.2f} руб. = {item_total:.2f} руб.\n\n"

    order_text += f"<b>Итого к оплате: {total:.2f} руб.</b>"
    order_text += "\n\nПодтвердить заказ?"

    await callback.message.edit_text(order_text, reply_markup=get_checkout_keyboard(), parse_mode="HTML")
    await state.set_state(CartStates.waiting_for_order_confirmation)
    await callback.answer()

@cart_router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_name = callback.from_user.full_name
    cart_items = cart_service.get_cart_items(user_id)
    total = cart_service.get_cart_total(user_id)

    if not cart_items:
        await callback.message.edit_text("🛒 <b>Ваша корзина пуста!</b>",
                                       reply_markup=get_back_to_main_inline_keyboard(), parse_mode="HTML")
        await state.clear()
        return

    order_text = f"📦 <b>НОВЫЙ ЗАКАЗ!</b>\n\n"
    order_text += f"👤 Пользователь: {user_name} (ID: {user_id})\n"
    order_text += f"🕒 Время: {callback.message.date.strftime('%d.%m.%Y %H:%M')}\n\n"
    order_text += "<b>Состав заказа:</b>\n"

    for item, quantity in cart_items:
        item_total = item.price * quantity
        order_text += f"🍽️ {item.name}\n"
        order_text += f"   {quantity} x {item.price:.2f} руб. = {item_total:.2f} руб.\n"

    order_text += f"\n<b>Итого: {total:.2f} руб.</b>"

    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        admin_id = os.getenv("ADMIN_ID")
        if admin_id:
            await callback.bot.send_message(chat_id=admin_id, text=order_text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Ошибка при отправке уведомления админу: {e}")

    cart_service.clear_cart(user_id)

    await callback.message.edit_text("✅ <b>Заказ успешно оформлен!</b>\n\nСпасибо за покупку! Администратор свяжется с вами для подтверждения.",
                                   reply_markup=get_back_to_main_inline_keyboard(), parse_mode="HTML")
    await state.clear()
    await callback.answer()

@cart_router.callback_query(F.data == "cancel_order_process")
async def cancel_order_process(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🛒 <b>Ваша корзина:</b>", reply_markup=get_cart_keyboard(), parse_mode="HTML")
    await state.clear()
    await callback.answer()

@cart_router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    cart_service.clear_cart(user_id)
    await callback.message.edit_text("🛒 <b>Корзина очищена!</b>",
                                   reply_markup=get_back_to_main_inline_keyboard(), parse_mode="HTML")
    await callback.answer()

@cart_router.callback_query(F.data.startswith("add_to_cart_"))
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

        success = cart_service.add_to_cart(user_id, item_id)

        if success:
            await callback.answer(f"✅ Товар '{item.name}' добавлен в корзину!")
        else:
            await callback.answer("❌ Ошибка при добавлении товара!")

    except Exception as e:
        logging.error(f"Ошибка при добавлении в корзину: {e}")
        await callback.answer("Произошла ошибка!")

@cart_router.callback_query(F.data.startswith("increase_"))
async def increase_quantity(callback: types.CallbackQuery):
    try:
        item_id = int(callback.data.split("_")[1])
        user_id = callback.from_user.id

        cart = cart_service.get_cart(user_id)
        if item_id in cart:
            cart[item_id]["quantity"] += 1
            quantity = cart[item_id]["quantity"]
            await callback.message.edit_reply_markup(reply_markup=get_item_quantity_keyboard(item_id, quantity))
        await callback.answer()
    except Exception as e:
        logging.error(f"Ошибка при увеличении количества: {e}")
        await callback.answer("Ошибка!")

@cart_router.callback_query(F.data.startswith("decrease_"))
async def decrease_quantity(callback: types.CallbackQuery):
    try:
        item_id = int(callback.data.split("_")[1])
        user_id = callback.from_user.id

        cart = cart_service.get_cart(user_id)
        if item_id in cart and cart[item_id]["quantity"] > 1:
            cart[item_id]["quantity"] -= 1
            quantity = cart[item_id]["quantity"]
            await callback.message.edit_reply_markup(reply_markup=get_item_quantity_keyboard(item_id, quantity))
        await callback.answer()
    except Exception as e:
        logging.error(f"Ошибка при уменьшении количества: {e}")
        await callback.answer("Ошибка!")

@cart_router.callback_query(F.data.startswith("remove_"))
async def remove_from_cart(callback: types.CallbackQuery):
    try:
        item_id = int(callback.data.split("_")[1])
        user_id = callback.from_user.id

        cart_service.remove_from_cart(user_id, item_id)
        await callback.message.edit_text("🛒 <b>Ваша корзина:</b>", reply_markup=get_cart_keyboard(), parse_mode="HTML")
        await callback.answer("Товар удален из корзины!")
    except Exception as e:
        logging.error(f"Ошибка при удалении из корзины: {e}")
        await callback.answer("Ошибка!")
