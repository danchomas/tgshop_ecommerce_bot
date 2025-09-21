# Тесты для сервиса корзины
import pytest
from unittest.mock import Mock, patch
from src.services.cart_service import CartService

class TestCartService:
    """Тесты для CartService."""

    def setup_method(self):
        """Очистка синглтона перед каждым тестом."""
        CartService._instance = None

    def test_singleton_instance(self):
        """Тест синглтон паттерна."""
        cart1 = CartService()
        cart2 = CartService()

        assert cart1 is cart2

    def test_get_cart_new_user(self):
        """Тест получения корзины для нового пользователя."""
        cart_service = CartService()
        user_id = 123456789

        cart = cart_service.get_cart(user_id)

        assert isinstance(cart, dict)
        assert cart == {}
        assert user_id in cart_service.carts

    def test_get_cart_existing_user(self):
        """Тест получения корзины для существующего пользователя."""
        cart_service = CartService()
        user_id = 123456789
        expected_cart = {"test": "data"}
        cart_service.carts[user_id] = expected_cart

        cart = cart_service.get_cart(user_id)

        assert cart == expected_cart

    @patch('src.services.cart_service.get_db')
    @patch('src.services.cart_service.ItemGetService')
    def test_add_to_cart_success(self, mock_item_service_class, mock_get_db):
        """Тест успешного добавления товара в корзину."""
        # Подготовка моков
        mock_db_gen = Mock()
        mock_db = Mock()
        mock_get_db.return_value = mock_db_gen
        mock_db_gen.__next__ = Mock(return_value=mock_db)

        mock_item_service = Mock()
        mock_item_service_class.return_value = mock_item_service

        mock_item = Mock()
        mock_item.id = 1
        mock_item.name = "Test Item"
        mock_item.price = 99.99
        mock_item_service.get_item.return_value = mock_item

        # Тест
        cart_service = CartService()
        user_id = 123456789
        result = cart_service.add_to_cart(user_id, 1)

        # Проверки
        assert result is True
        cart = cart_service.get_cart(user_id)
        assert 1 in cart
        assert cart[1]["item"] == mock_item
        assert cart[1]["quantity"] == 1

    @patch('src.services.cart_service.get_db')
    @patch('src.services.cart_service.ItemGetService')
    def test_add_to_cart_item_not_found(self, mock_item_service_class, mock_get_db):
        """Тест добавления несуществующего товара в корзину."""
        # Подготовка моков
        mock_db_gen = Mock()
        mock_db = Mock()
        mock_get_db.return_value = mock_db_gen
        mock_db_gen.__next__ = Mock(return_value=mock_db)

        mock_item_service = Mock()
        mock_item_service_class.return_value = mock_item_service
        mock_item_service.get_item.return_value = None

        # Тест
        cart_service = CartService()
        user_id = 123456789
        result = cart_service.add_to_cart(user_id, 999)

        # Проверки
        assert result is False
        cart = cart_service.get_cart(user_id)
        assert cart == {}

    def test_remove_from_cart(self):
        """Тест удаления товара из корзины."""
        cart_service = CartService()
        user_id = 123456789

        # Добавляем товар в корзину
        mock_item = Mock()
        cart_service.carts[user_id] = {1: {"item": mock_item, "quantity": 2}}

        # Удаляем товар
        cart_service.remove_from_cart(user_id, 1)

        # Проверяем
        cart = cart_service.get_cart(user_id)
        assert 1 not in cart

    def test_clear_cart(self):
        """Тест очистки корзины."""
        cart_service = CartService()
        user_id = 123456789

        # Добавляем товары в корзину
        mock_item = Mock()
        cart_service.carts[user_id] = {
            1: {"item": mock_item, "quantity": 2},
            2: {"item": mock_item, "quantity": 1}
        }

        # Очищаем корзину
        cart_service.clear_cart(user_id)

        # Проверяем
        cart = cart_service.get_cart(user_id)
        assert cart == {}

    def test_get_cart_total(self):
        """Тест расчета общей суммы корзины."""
        cart_service = CartService()
        user_id = 123456789

        # Добавляем товары в корзину
        mock_item1 = Mock()
        mock_item1.price = 100.0
        mock_item2 = Mock()
        mock_item2.price = 50.0

        cart_service.carts[user_id] = {
            1: {"item": mock_item1, "quantity": 2},  # 200.0
            2: {"item": mock_item2, "quantity": 3}   # 150.0
        }

        # Тест
        total = cart_service.get_cart_total(user_id)

        # Проверяем
        assert total == 350.0

    def test_get_cart_items(self):
        """Тест получения всех товаров из корзины."""
        cart_service = CartService()
        user_id = 123456789

        # Добавляем товары в корзину
        mock_item1 = Mock()
        mock_item2 = Mock()

        cart_service.carts[user_id] = {
            1: {"item": mock_item1, "quantity": 2},
            2: {"item": mock_item2, "quantity": 1}
        }

        # Тест
        items = cart_service.get_cart_items(user_id)

        # Проверяем
        assert len(items) == 2
        assert items[0] == (mock_item1, 2)
        assert items[1] == (mock_item2, 1)
