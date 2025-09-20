# Работа с товарами
from typing import Optional, List
from sqlalchemy.orm import Session
from data.models import MenuItem

# Базовый класс для сервисов товаров
class ItemServiceBase:
    def __init__(self, db: Session):
        self.db = db

# Сервис добавления товаров
class ItemAddService(ItemServiceBase):
    def add_item(self, name: str, description: str, price: float, category_id: int) -> Optional[MenuItem]:
        try:
            item = MenuItem(
                name=name,
                description=description,
                price=price,
                category_id=category_id
            )
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item
        except Exception:
            self.db.rollback()
            return None

# Сервис получения товаров
class ItemGetService(ItemServiceBase):
    def get_item(self, item_id: int) -> Optional[MenuItem]:
        return self.db.query(MenuItem).filter(MenuItem.id == item_id).first()

    def get_all_items(self) -> List[MenuItem]:
        return self.db.query(MenuItem).all()

    def get_items_by_category(self, category_id: int) -> List[MenuItem]:
        return self.db.query(MenuItem).filter(MenuItem.category_id == category_id).all()

# Сервис редактирования товаров
class ItemEditService(ItemServiceBase):
    def update_item(self, item_id: int, name: str = None, description: str = None,
                   price: float = None, category_id: int = None) -> Optional[MenuItem]:
        item = self.db.query(MenuItem).filter(MenuItem.id == item_id).first()
        if not item:
            return None

        if name is not None:
            item.name = name
        if description is not None:
            item.description = description
        if price is not None:
            item.price = price
        if category_id is not None:
            item.category_id = category_id

        try:
            self.db.commit()
            self.db.refresh(item)
            return item
        except Exception:
            self.db.rollback()
            return None

    def update_item_name(self, item_id: int, name: str) -> Optional[MenuItem]:
        return self.update_item(item_id, name=name)

    def update_item_description(self, item_id: int, description: str) -> Optional[MenuItem]:
        return self.update_item(item_id, description=description)

    def update_item_price(self, item_id: int, price: float) -> Optional[MenuItem]:
        return self.update_item(item_id, price=price)

    def update_item_category(self, item_id: int, category_id: int) -> Optional[MenuItem]:
        return self.update_item(item_id, category_id=category_id)

# Сервис удаления товаров
class ItemDeleteService:
    def __init__(self, db: Session):
        self.db = db

    def delete_item(self, item_id: int) -> bool:
        item = self.db.query(MenuItem).filter(MenuItem.id == item_id).first()
        if not item:
            return False

        try:
            self.db.delete(item)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def delete_items_by_category(self, category_id: int) -> int:
        try:
            deleted_count = self.db.query(MenuItem).filter(
                MenuItem.category_id == category_id
            ).delete()
            self.db.commit()
            return deleted_count
        except Exception:
            self.db.rollback()
            return 0
