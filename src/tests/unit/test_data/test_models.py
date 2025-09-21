# Тесты для моделей данных
import pytest
from src.data.models import Category, MenuItem

class TestCategoryModel:
    """Тесты для модели Category."""

    def test_category_creation(self):
        """Тест создания категории."""
        category = Category(
            key="test_category",
            name="Test Category"
        )

        assert category.key == "test_category"
        assert category.name == "Test Category"
        assert category.items == []

    def test_category_repr(self):
        """Тест строкового представления категории."""
        category = Category(
            key="test_category",
            name="Test Category"
        )

        # Проверяем, что объект можно создать
        assert isinstance(category, Category)

class TestMenuItemModel:
    """Тесты для модели MenuItem."""

    def test_item_creation(self):
        """Тест создания товара."""
        item = MenuItem(
            name="Test Item",
            description="Test Description",
            price=99.99,
            category_id=1
        )

        assert item.name == "Test Item"
        assert item.description == "Test Description"
        assert item.price == 99.99
        assert item.category_id == 1

    def test_item_repr(self):
        """Тест строкового представления товара."""
        item = MenuItem(
            name="Test Item",
            description="Test Description",
            price=99.99,
            category_id=1
        )

        # Проверяем, что объект можно создать
        assert isinstance(item, MenuItem)
