# Тесты для сервиса аутентификации
import pytest
from unittest.mock import patch
from src.services.auth_service import AuthService
import asyncio

class TestAuthService:
    """Тесты для AuthService."""

    @patch('src.services.auth_service.os.getenv')
    def test_is_admin_true(self, mock_getenv):
        """Тест проверки администратора - положительный результат."""
        mock_getenv.return_value = "123456789"
        auth_service = AuthService(123456789)

        # Выполняем асинхронный метод
        async def run_test():
            return await auth_service.isAdmin()

        result = asyncio.run(run_test())

        assert result is True

    @patch('src.services.auth_service.os.getenv')
    def test_is_admin_false(self, mock_getenv):
        """Тест проверки администратора - отрицательный результат."""
        mock_getenv.return_value = "987654321"
        auth_service = AuthService(123456789)

        # Выполняем асинхронный метод
        async def run_test():
            return await auth_service.isAdmin()

        result = asyncio.run(run_test())

        assert result is False

    @patch('src.services.auth_service.os.getenv')
    def test_is_admin_no_env(self, mock_getenv):
        """Тест проверки администратора без переменной окружения."""
        mock_getenv.return_value = None
        auth_service = AuthService(123456789)

        # Выполняем асинхронный метод
        async def run_test():
            return await auth_service.isAdmin()

        result = asyncio.run(run_test())

        assert result is False
