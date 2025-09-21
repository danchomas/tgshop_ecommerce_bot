# Тесты для сервисов категорий
import pytest
from unittest.mock import Mock, patch
from src.services.category_services import (
    CategoryAddService, CategoryGetService,
    CategoryEditService, CategoryDeleteService
)
from src.data.models import Category, MenuItem

class TestCategoryServices:
    """Тесты для сервисов категорий."""

    @patch('src.services.category_services.Category')
    def test_category_add_service_success(self, mock_category_class):
        """Тест успешного добавления категории."""
        # Подготовка
        mock_db = Mock()
        mock_category = Mock(spec=Category)
        mock_category.id = 1
        mock_category.key = "test_key"
        mock_category.name = "Test Category"

        mock_category_class.return_value = mock_category
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        mock_db.rollback = Mock()

        # Создание сервиса
        service = CategoryAddService(mock_db)

        # Тест
        result = service.add_category("test_key", "Test Category")

        # Проверки
        assert result == mock_category
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_category_add_service_exception(self):
        """Тест добавления категории с исключением."""
        # Подготовка
        mock_db = Mock()
        mock_db.add = Mock(side_effect=Exception("Database error"))
        mock_db.commit = Mock()
        mock_db.rollback = Mock()

        # Создание сервиса
        service = CategoryAddService(mock_db)

        # Тест
        result = service.add_category("test_key", "Test Category")

        # Проверки
        assert result is None
        mock_db.add.assert_called_once()
        mock_db.rollback.assert_called_once()

    def test_category_get_service(self):
        """Тест получения категории."""
        # Подготовка
        mock_db = Mock()
        mock_query = Mock()
        mock_category = Mock(spec=Category)

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_category

        # Создание сервиса
        service = CategoryGetService(mock_db)

        # Тест
        result = service.get_category(1)

        # Проверки
        assert result == mock_category
        mock_db.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.first.assert_called_once()

    def test_category_edit_service_success(self):
        """Тест успешного редактирования категории."""
        # Подготовка
        mock_db = Mock()
        mock_query = Mock()
        mock_category = Mock(spec=Category)
        mock_category.id = 1
        mock_category.key = "old_key"
        mock_category.name = "Old Name"

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_category
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        mock_db.rollback = Mock()

        # Создание сервиса
        service = CategoryEditService(mock_db)

        # Тест
        result = service.update_category(1, key="new_key", name="New Name")

        # Проверки
        assert result == mock_category
        assert mock_category.key == "new_key"
        assert mock_category.name == "New Name"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_category_delete_service_success(self):
        """Тест успешного удаления категории."""
        # Подготовка
        mock_db = Mock()
        mock_query = Mock()
        mock_category = Mock(spec=Category)
        mock_menu_item = Mock(spec=MenuItem)

        # Настраиваем моки для цепочки вызовов
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_category
        mock_query.delete.return_value = 1  # Удалено 1 элемент
        mock_db.delete = Mock()
        mock_db.commit = Mock()
        mock_db.rollback = Mock()

        # Создание сервиса
        service = CategoryDeleteService(mock_db)

        # Тест
        result = service.delete_category(1)

        # Проверки
        assert result is False
