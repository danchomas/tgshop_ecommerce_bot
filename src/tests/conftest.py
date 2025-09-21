# Конфигурация pytest и общие фикстуры
import sys
import os
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

# Добавляем src в путь поиска модулей
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
src_path = os.path.join(project_root, 'src')

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.data.models import Base

# Используем in-memory SQLite для тестов
@pytest.fixture(scope="session")
def event_loop():
    """Создает экземпляр event loop для каждого теста."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_db():
    """Создает тестовую базу данных."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    def get_test_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    return get_test_db

@pytest.fixture
def mock_message():
    """Мок для сообщения Telegram."""
    message = Mock()
    message.from_user = Mock()
    message.from_user.id = 123456789
    message.from_user.full_name = "Test User"
    message.answer = AsyncMock()
    message.edit_text = AsyncMock()
    message.edit_reply_markup = AsyncMock()
    return message

@pytest.fixture
def mock_callback():
    """Мок для callback query."""
    callback = Mock()
    callback.from_user = Mock()
    callback.from_user.id = 123456789
    callback.from_user.full_name = "Test User"
    callback.message = Mock()
    callback.message.edit_text = AsyncMock()
    callback.message.edit_reply_markup = AsyncMock()
    callback.answer = AsyncMock()
    callback.bot = Mock()
    callback.bot.send_message = AsyncMock()
    return callback

@pytest.fixture
def mock_bot():
    """Мок для бота."""
    bot = Mock()
    bot.send_message = AsyncMock()
    return bot
