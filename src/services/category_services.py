# Работа с категориями
from typing import Optional, List
from sqlalchemy.orm import Session
from data.models import Category

# Базовый класс для сервисов категорий
class CategoryServiceBase:
    def __init__(self, db: Session):
        self.db = db

# Сервис добавления категорий
class CategoryAddService(CategoryServiceBase):
    def add_category(self, key: str, name: str) -> Optional[Category]:
        try:
            category = Category(key=key, name=name)
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            return category
        except Exception:
            self.db.rollback()
            return None

# Сервис получения категорий
class CategoryGetService(CategoryServiceBase):
    def get_category(self, category_id: int) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_category_by_key(self, key: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.key == key).first()

    def get_all_categories(self) -> List[Category]:
        return self.db.query(Category).all()

# Сервис редактирования категорий
class CategoryEditService(CategoryServiceBase):
    def update_category(self, category_id: int, key: str = None, name: str = None) -> Optional[Category]:
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None

        if key is not None:
            category.key = key
        if name is not None:
            category.name = name

        try:
            self.db.commit()
            self.db.refresh(category)
            return category
        except Exception:
            self.db.rollback()
            return None

# Сервис удаления категорий
class CategoryDeleteService(CategoryServiceBase):
    def delete_category(self, category_id: int) -> bool:
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return False

        try:
            self.db.query(MenuItem).filter(MenuItem.category_id == category_id).delete()
            self.db.delete(category)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
