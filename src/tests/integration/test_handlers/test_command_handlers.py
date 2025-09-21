# Интеграционные тесты для обработчиков команд
import pytest
from unittest.mock import Mock, patch
from src.handlers.command_handlers import *

@pytest.mark.asyncio
class TestCommandHandlers:
    """Интеграционные тесты для обработчиков команд."""

    async def test_start_command(self, mock_message):
        """Тест команды /start."""
        await start_command(mock_message)

        mock_message.answer.assert_called_once()
        args, kwargs = mock_message.answer.call_args
        assert "Добро пожаловать" in args[0]
        assert "reply_markup" in kwargs

    async def test_help_command(self, mock_message):
        """Тест команды /help."""
        await help_command(mock_message)

        mock_message.answer.assert_called_once()
        args, kwargs = mock_message.answer.call_args
        assert "Помощь" in args[0]
        assert "reply_markup" in kwargs

    @patch('src.handlers.command_handlers.AuthService')
    async def test_admin_command_admin(self, mock_auth_service_class, mock_message):
        """Тест команды /admin для администратора."""
        # Подготовка мока AuthService
        mock_auth_service = Mock()
        mock_auth_service.isAdmin = Mock(return_value=True)
        mock_auth_service_class.return_value = mock_auth_service

        await admin_command(mock_message)

        mock_message.answer.assert_called_once()
        args, kwargs = mock_message.answer.call_args
        assert "Админ-панель" in args[0]

    @patch('src.handlers.command_handlers.AuthService')
    async def test_admin_command_non_admin(self, mock_auth_service_class, mock_message):
        """Тест команды /admin для обычного пользователя."""
        # Подготовка мока AuthService
        mock_auth_service = Mock()
        mock_auth_service.isAdmin = Mock(return_value=False)
        mock_auth_service_class.return_value = mock_auth_service

        await admin_command(mock_message)

        mock_message.answer.assert_called_once()
        args, kwargs = mock_message.answer.call_args
        assert "нет доступа" in args[0]

    async def test_go_back(self, mock_message):
        """Тест кнопки 'Назад'."""
        await go_back(mock_message)

        mock_message.answer.assert_called_once()
        args, kwargs = mock_message.answer.call_args
        assert "Главное меню" in args[0]
        assert "reply_markup" in kwargs

    @patch('src.handlers.command_handlers.get_back_to_main_inline_keyboard')
    async def test_back_to_main(self, mock_get_keyboard, mock_callback):
        """Тест callback 'Назад в главное меню'."""
        # Подготовка мока клавиатуры
        mock_keyboard = Mock()
        mock_get_keyboard.return_value = mock_keyboard

        await back_to_main(mock_callback)

        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()
