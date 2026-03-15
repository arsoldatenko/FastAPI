from fastapi import FastAPI
from app.database import engine, Base
from app.api import links
from app.cache import test_redis
from contextlib import asynccontextmanager

# Создае таблицы если их нет
Base.metadata.create_all(bind=engine)


async def root():
    return {"message:" "Hello World!"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    await test_redis()  # проверка Redis
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(links.router, prefix="/api")
