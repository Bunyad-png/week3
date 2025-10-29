# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import sessionmaker
# import os
# from sqlalchemy import create_engine
# from dotenv import load_dotenv

# # Загружаем переменные окружения из файла .env
# load_dotenv()

# # Получаем строку подключения из переменной окружения
# DATABASE_URL = os.getenv("DATABASE_URL")

# # Для отладки — выводим строку подключения (не делайте так в проде с реальным паролем!)
# print(f"Using DATABASE_URL: {DATABASE_URL}")

# # Создаём асинхронный движок SQLAlchemy
# engine = create_engine(DATABASE_URL, echo=True)

# # Создаём sessionmaker для асинхронных сессий
# async_session = sessionmaker(
#     engine, expire_on_commit=False, class_=AsyncSession
# )

# # Dependency для FastAPI, возвращает сессию для работы с БД
# async def get_db():
#     async with async_session() as session:
#         yield session



from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from app.models.base import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Using DATABASE_URL: {DATABASE_URL}")

# Создаём асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаём sessionmaker для асинхронных сессий
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Dependency для FastAPI, возвращает сессию для работы с БД
async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)