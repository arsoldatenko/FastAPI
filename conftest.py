import pytest
import pytest_asyncio
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from httpx import ASGITransport, AsyncClient
from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "postgresql://postgres:qwerty123@localhost:5433/FastAPI_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# Фикстура для создания и удаления таблиц перед/после тестов
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# Фикстура для переопределения get_db в FastAPI
@pytest.fixture
def override_get_db(db):
    def _override():
        yield db

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.pop(get_db, None)


# Асинхронный клиент использующий тестовую базу
@pytest_asyncio.fixture
async def client(override_get_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
