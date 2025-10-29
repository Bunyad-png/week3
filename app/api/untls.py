from sqlalchemy.orm import joinedload
from app.schemas.user import UserCreate, UserResponse
from app.api.auth import create_access_token, create_refresh_token
from fastapi import APIRouter, Depends, HTTPException, Form, Query,  File
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import get_user, create_user, verify_password, get_password_hash
from app.api.auth import create_access_token, get_current_user
from app.schemas.user import LoginRequest, LoginResponse,  UserWithFollowResponse
from app.api.auth import get_user_by_email
from app.api.auth import verify_refresh_token
from datetime import  timedelta
from app.api.auth import ACCESS_TOKEN_EXPIRE_MINUTES, bearer_scheme, REFRESH_TOKEN_EXPIRE_MINUTES
from app.schemas.user import ResetPasswordRequest
from app.models.user import User
from typing import List
from sqlalchemy.future import select
from app.models.post import Follow
from sqlalchemy import func, delete


router = APIRouter(prefix="/auth", tags=["AUTH"])
BASE_URL = "http://localhost:9000"

@router.post("/auth/sign-up", response_model=LoginResponse, status_code=201)
async def sign_up(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверка: есть ли такой email уже
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    new_user = await create_user(db, user)

    access_token = create_access_token({"sub": new_user.email})
    refresh_token = create_refresh_token({"sub": new_user.email})

    return {
        "message": "User successfully created",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }



@router.post("/auth/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = None

    # если в identifier есть "@", предполагаем, что это email
    if "@" in data.identifier:
        user = await get_user_by_email(db, email=data.identifier)
    else:
        user = await get_user(db, username=data.identifier)

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return {
        "message": "Успешный вход",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user = Depends(get_current_user)):
    return current_user




@router.get("/auth/refresh")
async def refresh_token(
    refresh_token: str = Depends(bearer_scheme),  # Берём токен из Authorization: Bearer
    db: AsyncSession = Depends(get_db),
):
    user = await verify_refresh_token(refresh_token, db)

    # Генерируем новый access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    return {
        "accessToken": access_token,
        "token_type": "bearer",
    }


@router.post("/auth/authorize")
async def authorize(
    grant_type: str = Form(..., regex="password"),  # будет принимать только "password"
    username: str = Form(...),
    password: str = Form(...),
    scope: str = Form(None),
    client_id: str = Form(None),
    client_secret: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    if grant_type != "password":
        raise HTTPException(status_code=400, detail="Unsupported grant_type")

    user = await get_user(db, username=username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": user.username}, expires_delta=refresh_token_expires)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "scope": scope or "",
    }




@router.post("/auth/reset-pass")
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user(db, username=data.username)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Здесь должна быть проверка кода подтверждения (например, из БД или кеша)
    # Для примера сделаем заглушку, что код == 123456
    if data.code != 123456:
        raise HTTPException(status_code=400, detail="Неверный код подтверждения")

    # Хешируем новый пароль
    hashed_password = get_password_hash(data.new_pass)

    # Обновляем пароль пользователя
    user.hashed_password = hashed_password
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"message": "Пароль успешно обновлен"}



@router.get("/auth/me")
async def get_myself(current_user: User = Depends(get_current_user)):
    return {"attributes": dir(current_user)}

@router.get("/auth/user", response_model=List[UserWithFollowResponse])
async def get_user_by_username(
    username: str = Query(..., description="Username пользователя"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверка подписки
    result_follow = await db.execute(
        select(Follow).where(
            (Follow.follower_id == current_user.id) & (Follow.following_id == user.id)
        )
    )
    follow = result_follow.scalars().first()
    has_followed = bool(follow)

    # Подсчёт количества подписчиков
    followers_count_result = await db.execute(
        select(func.count(Follow.follower_id)).where(Follow.following_id == user.id)
    )
    followers_count = followers_count_result.scalar_one()

    # Подсчёт количества подписок
    followings_count_result = await db.execute(
        select(func.count(Follow.following_id)).where(Follow.follower_id == user.id)
    )
    followings_count = followings_count_result.scalar_one()

    response_data = UserWithFollowResponse(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        username=user.username,
        followers=followers_count,
        followings=followings_count,
        user_img=user.user_image,
        has_followed=has_followed
    )

    return [response_data]

@router.get("/auth/users", response_model=List[UserResponse])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
