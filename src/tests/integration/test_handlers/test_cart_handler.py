# Интеграционные тесты для обработчиков корзины
import pytest
from unittest.mock import Mock, patch
from src.handlers.cart_handler import *
from src.services.cart_service import CartService

@pytest.mark.asyncio
class TestCartHandler:
    """Интеграционные тесты для обработчиков корзины."""

    def setup_method(self):
        """Очистка синглтона корзины перед каждым тестом."""
        CartService._instance = None

    async def test_show_cart_empty(self, mock_message):
        """Тест показа пустой корзины."""
        await show_cart(mock_message)

        mock_message.answer.assert_called_once()
        args, kwargs = mock_message.answer.call_args
        assert "корзина пуста" in args[0]
        assert "reply_markup" in kwargs

    async def test_view_cart_empty(self, mock_callback):
        """Тест просмотра пустой корзины через callback."""
        # Подготовка мока клавиатуры
        with patch('src.handlers.cart_handler.get_back_to_main_inline_keyboard') as mock_get_keyboard:
            mock_keyboard = Mock()
            mock_get_keyboard.return_value = mock_keyboard

            await view_cart(mock_callback)

            mock_callback.message.edit_text.assert_called_once()
            args, kwargs = mock_callback.message.edit_text.call_args
            assert "корзина пуста" in args[0]
            assert "reply_markup" in kwargs
            mock_callback.answer.assert_called_once()

    async def test_checkout_start_empty(self, mock_callback):
        """Тест начала оформления заказа с пустой корзиной."""
        # Подготовка мока клавиатуры
        with patch('src.handlers.cart_handler.get_checkout_keyboard') as mock_get_keyboard:
            mock_keyboard = Mock()
            mock_get_keyboard.return_value = mock_keyboard

            mock_state = Mock()
            mock_state.set_state = Mock()

            await checkout_start(mock_callback, mock_state)

            mock_callback.message.edit_text.assert_called_once()
            args, kwargs = mock_callback.message.edit_text.call_args
            assert "корзина пуста" in args[0]
            mock_callback.answer.assert_called_once()

    async def test_confirm_order_empty(self, mock_callback):
        """Тест подтверждения заказа с пустой корзиной."""
        # Подготовка мока клавиатуры
        with patch('src.handlers.cart_handler.get_back_to_main_inline_keyboard') as mock_get_keyboard:
            mock_keyboard = Mock()
            mock_get_keyboard.return_value = mock_keyboard

            mock_state = Mock()
            mock_state.clear = Mock()

            await confirm_order(mock_callback, mock_state)

            mock_callback.message.edit_text.assert_called_once()
            args, kwargs = mock_callback.message.edit_text.call_args
            assert "корзина пуста" in args[0]
            mock_state.clear.assert_called_once()
            mock_callback.answer.assert_called_once()

    async def test_clear_cart(self, mock_callback):
        """Тест очистки корзины."""
        # Подготовка мока клавиатуры
        with patch('src.handlers.cart_handler.get_back_to_main_inline_keyboard') as mock_get_keyboard:
            mock_keyboard = Mock()
            mock_get_keyboard.return_value = mock_keyboard

            # Добавляем товар в корзину
            cart_service = CartService()
            user_id = mock_callback.from_user.id
            mock_item = Mock()
            mock_item.id = 1
            mock_item.name = "Test Item"
            mock_item.price = 99.99
            cart_service.carts[user_id] = {1: {"item": mock_item, "quantity": 1}}

            await clear_cart(mock_callback)

            # Проверяем, что корзина очищена
            cart = cart_service.get_cart(user_id)
            assert cart == {}
            mock_callback.message.edit_text.assert_called_once()
            mock_callback.answer.assert_called_once()
