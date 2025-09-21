# Тесты для клавиатур администраторов
import pytest
from unittest.mock import Mock
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from src.keyboards.admin_keyboards import *

class TestAdminKeyboards:
    """Тесты для админских клавиатур."""

    def test_get_admin_main_keyboard(self):
        """Тест главной клавиатуры администратора."""
        keyboard = get_admin_main_keyboard()

        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert keyboard.resize_keyboard is True
        assert len(keyboard.keyboard) == 2  # 4 строки кнопок

    def test_get_menu_management_keyboard(self):
        """Тест клавиатуры управления меню."""
        keyboard = get_menu_management_keyboard()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 5  # 5 строк кнопок

    def test_get_categories_keyboard(self):
        """Тест клавиатуры категорий."""
        # Создаем моки категорий
        mock_category1 = Mock()
        mock_category1.id = 1
        mock_category1.name = "Category 1"

        mock_category2 = Mock()
        mock_category2.id = 2
        mock_category2.name = "Category 2"

        categories = [mock_category1, mock_category2]
        keyboard = get_categories_keyboard(categories)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Должно быть 2 категории + кнопка "Назад"
        assert len(keyboard.inline_keyboard) == 3

    def test_get_items_keyboard(self):
        """Тест клавиатуры товаров."""
        # Создаем моки товаров
        mock_item1 = Mock()
        mock_item1.id = 1
        mock_item1.name = "Item 1"
        mock_item1.price = 100.0

        mock_item2 = Mock()
        mock_item2.id = 2
        mock_item2.name = "Item 2"
        mock_item2.price = 200.0

        items = [mock_item1, mock_item2]
        keyboard = get_items_keyboard(items)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Должно быть 2 товара + кнопка "Назад"
        assert len(keyboard.inline_keyboard) == 3

    def test_get_category_edit_keyboard(self):
        """Тест клавиатуры редактирования категории."""
        keyboard = get_category_edit_keyboard(1)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 3  # 3 строки кнопок

    def test_get_item_edit_keyboard(self):
        """Тест клавиатуры редактирования товара."""
        keyboard = get_item_edit_keyboard(1)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 5  # 5 строк кнопок

    def test_get_admin_back_inline_keyboard(self):
        """Тест клавиатуры возврата в админку."""
        keyboard = get_admin_back_inline_keyboard()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1  # 1 строка кнопок
        assert len(keyboard.inline_keyboard[0]) == 1  # 1 кнопка
