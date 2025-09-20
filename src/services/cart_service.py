# Работа с корзиной
from data.database import get_db
from services.item_services import ItemGetService

# Сервис корзины покупок (Singleton)
class CartService:
    _instance = None

    # Реализация паттерна Singleton
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.carts = {}
        return cls._instance

    # Получение корзины пользователя
    def get_cart(self, user_id: int) -> dict:
        if user_id not in self.carts:
            self.carts[user_id] = {}
        return self.carts[user_id]

    # Добавление товара в корзину
    def add_to_cart(self, user_id: int, item_id: int) -> bool:
        cart = self.get_cart(user_id)

        db_gen = get_db()
        db = next(db_gen)
        item_get_service = ItemGetService(db)
        item = item_get_service.get_item(item_id)
        db.close()

        if not item:
            return False

        if item_id in cart:
            cart[item_id]["quantity"] += 1
        else:
            cart[item_id] = {
                "item": item,
                "quantity": 1
            }
        return True

    # Удаление товара из корзины
    def remove_from_cart(self, user_id: int, item_id: int):
        cart = self.get_cart(user_id)
        if item_id in cart:
            del cart[item_id]

    # Очистка корзины
    def clear_cart(self, user_id: int):
        if user_id in self.carts:
            self.carts[user_id] = {}

    # Получение общей суммы корзины
    def get_cart_total(self, user_id: int) -> float:
        cart = self.get_cart(user_id)
        return sum(item_data["item"].price * item_data["quantity"] for item_data in cart.values())

    # Получение всех товаров в корзине
    def get_cart_items(self, user_id: int) -> list:
        cart = self.get_cart(user_id)
        return [(item_data["item"], item_data["quantity"]) for item_data in cart.values()]

    # Получение количества товаров в корзине
    def get_cart_count(self, user_id: int) -> int:
        cart = self.get_cart(user_id)
        return sum(item_data["quantity"] for item_data in cart.values())

    # Обновление количества товара в корзине
    def update_item_quantity(self, user_id: int, item_id: int, quantity: int) -> bool:
        if quantity <= 0:
            self.remove_from_cart(user_id, item_id)
            return True

        cart = self.get_cart(user_id)

        db_gen = get_db()
        db = next(db_gen)
        item_get_service = ItemGetService(db)
        item = item_get_service.get_item(item_id)
        db.close()

        if not item or item_id not in cart:
            return False

        cart[item_id]["quantity"] = quantity
        return True
