# Тесты для сервисов товаров
import pytest
from unittest.mock import Mock, patch
from src.services.item_services import (
    ItemAddService, ItemGetService,
    ItemEditService, ItemDeleteService
)
from src.data.models import MenuItem

class TestItemServices:
    """Тесты для сервисов товаров."""

    @patch('src.services.item_services.MenuItem')
    def test_item_add_service_success(self, mock_item_class):
        """Тест успешного добавления товара."""
        # Подготовка
        mock_db = Mock()
        mock_item = Mock(spec=MenuItem)
        mock_item.id = 1
        mock_item.name = "Test Item"
        mock_item.description = "Test Description"
        mock_item.price = 99.99
        mock_item.category_id = 1

        mock_item_class.return_value = mock_item
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        mock_db.rollback = Mock()

        # Создание сервиса
        service = ItemAddService(mock_db)

        # Тест
        result = service.add_item("Test Item", "Test Description", 99.99, 1)

        # Проверки
        assert result == mock_item
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_item_get_service(self):
        """Тест получения товара."""
        # Подготовка
        mock_db = Mock()
        mock_query = Mock()
        mock_item = Mock(spec=MenuItem)

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_item

        # Создание сервиса
        service = ItemGetService(mock_db)

        # Тест
        result = service.get_item(1)

        # Проверки
        assert result == mock_item
        mock_db.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.first.assert_called_once()

    def test_item_edit_service_success(self):
        """Тест успешного редактирования товара."""
        # Подготовка
        mock_db = Mock()
        mock_query = Mock()
        mock_item = Mock(spec=MenuItem)
        mock_item.id = 1
        mock_item.name = "Old Name"
        mock_item.description = "Old Description"
        mock_item.price = 50.0
        mock_item.category_id = 1

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_item
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        mock_db.rollback = Mock()

        # Создание сервиса
        service = ItemEditService(mock_db)

        # Тест
        result = service.update_item(1, name="New Name", price=99.99)

        # Проверки
        assert result == mock_item
        assert mock_item.name == "New Name"
        assert mock_item.price == 99.99
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_item_delete_service_success(self):
        """Тест успешного удаления товара."""
        # Подготовка
        mock_db = Mock()
        mock_query = Mock()
        mock_item = Mock(spec=MenuItem)

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_item
        mock_db.delete = Mock()
        mock_db.commit = Mock()
        mock_db.rollback = Mock()

        # Создание сервиса
        service = ItemDeleteService(mock_db)

        # Тест
        result = service.delete_item(1)

        # Проверки
        assert result is True
        mock_db.delete.assert_called_once()
        mock_db.commit.assert_called_once()
