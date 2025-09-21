# Тесты для клавиатур пользователей
import pytest
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from src.keyboards.user_keyboards import *

class TestUserKeyboards:
    """Тесты для пользовательских клавиатур."""

    def test_get_main_menu_keyboard(self):
        """Тест клавиатуры главного меню."""
        keyboard = get_main_menu_keyboard()

        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert keyboard.resize_keyboard is True
        assert len(keyboard.keyboard) == 3  # 3 строки кнопок

    def test_get_cart_keyboard(self):
        """Тест клавиатуры корзины."""
        keyboard = get_cart_keyboard()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 3  # 3 строки кнопок

    def test_get_item_quantity_keyboard(self):
        """Тест клавиатуры изменения количества товара."""
        keyboard = get_item_quantity_keyboard(1, 5)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Проверяем, что кнопка с количеством содержит правильное значение
        assert keyboard.inline_keyboard[0][1].text == "5"
        assert keyboard.inline_keyboard[0][1].callback_data == "quantity_1"

    def test_get_checkout_keyboard(self):
        """Тест клавиатуры оформления заказа."""
        keyboard = get_checkout_keyboard()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2  # 2 строки кнопок

    def test_get_back_to_main_keyboard(self):
        """Тест клавиатуры возврата в главное меню (reply)."""
        keyboard = get_back_to_main_keyboard()

        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert keyboard.resize_keyboard is True

    def test_get_back_to_main_inline_keyboard(self):
        """Тест клавиатуры возврата в главное меню (inline)."""
        keyboard = get_back_to_main_inline_keyboard()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1  # 1 строка кнопок
        assert len(keyboard.inline_keyboard[0]) == 1  # 1 кнопка
