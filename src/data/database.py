# Подключение к базе данных
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Создание движка и таблиц
engine = create_engine('sqlite:///bot.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

# Генератор сессий базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
