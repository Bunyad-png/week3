
from app.schemas.user import UserCreate
from typing import Union, Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging
import os
from app.core.database import get_db
from app.models.user import User

# Конфигурация токенов
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
SECRET_KEY = "your-secret-key"  # 🔒 Заменить на секрет из .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней


# Используем HTTPBearer вместо OAuth2PasswordBearer
bearer_scheme = HTTPBearer()



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



async def get_user(db: AsyncSession, username: str | int):
    """
    Ищет пользователя по username или по id (если передано число).
    """
    if isinstance(username, int) or str(username).isdigit():
        logging.info(f"Поиск пользователя по ID: {username}")
        stmt = select(User).where(User.id == int(username))
    else:
        logging.info(f"Поиск пользователя по username: {username}")
        stmt = select(User).where(User.username == username)

    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        logging.warning(f"Пользователь '{username}' не найден")
    return user



async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()



async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Проверяет JWT-токен, получает из него 'sub' (username или ID)
    и возвращает объект пользователя из БД.
    """
    token = credentials.credentials
    logging.info(f"Получен токен: {token}")

    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Недействительный или просроченный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logging.info(f"Payload токена: {payload}")

        user_identifier = payload.get("sub")
        if user_identifier is None:
            logging.warning("В токене отсутствует 'sub'")
            raise credentials_exception

    except JWTError as e:
        logging.warning(f"Ошибка при декодировании токена: {e}")
        raise credentials_exception

    # --- ищем пользователя по username или id ---
    user = await get_user(db, username=user_identifier)
    if user is None:
        logging.warning(f"Пользователь '{user_identifier}' не найден")
        raise credentials_exception

    return user


async def verify_refresh_token(token: Union[str, HTTPAuthorizationCredentials], db: AsyncSession):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Если передан объект, достаём строку токена
    if isinstance(token, HTTPAuthorizationCredentials):
        token = token.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user




