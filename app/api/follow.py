from sqlalchemy.orm import joinedload
from app.schemas.user import  UnfollowRequest
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth import  get_current_user
from app.models.user import User
from sqlalchemy.future import select
from app.models.post import Follow

from app.schemas.user import  FollowRequest

router = APIRouter(prefix="/auth", tags=["AUTH"])
BASE_URL = "http://localhost:9000"

@router.post("/followings/follow")
async def follow_user(
    follow_request: FollowRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Найти пользователя, на которого хотим подписаться
    result = await db.execute(select(User).where(User.username == follow_request.username))
    user_to_follow = result.scalars().first()
    if not user_to_follow:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user_to_follow.id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя подписаться на самого себя")

    # Проверяем, есть ли уже подписка
    result = await db.execute(
        select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == user_to_follow.id
        )
    )
    existing_follow = result.scalars().first()
    if existing_follow:
        return {"message": "Вы уже подписаны на этого пользователя"}

    # Создаем подписку
    new_follow = Follow(
        follower_id=current_user.id,
        following_id=user_to_follow.id
    )
    db.add(new_follow)
    await db.commit()

    return {"message": f"Вы успешно подписались на {user_to_follow.username}"}


@router.get("/following/followers")
async def get_followers(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(User).join(Follow, User.id == Follow.follower_id)
        .where(Follow.following_id == current_user.id)
    )
    followers = result.scalars().all()

    return [
        {
            "id": follower.id,
            "username": follower.username,
            "user_image": follower.user_image  # убедись, что поле называется правильно
        }
        for follower in followers
    ]


@router.post("/followings/unfollow")
async def unfollow_user(
    unfollow_data: UnfollowRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Ищем пользователя, от которого хотим отписаться
    result = await db.execute(select(User).where(User.username == unfollow_data.username))
    target_user = result.scalars().first()

    if not target_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя отписаться от самого себя")

    # Ищем подписку
    result = await db.execute(
        select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == target_user.id
        )
    )
    follow = result.scalars().first()

    if not follow:
        raise HTTPException(status_code=400, detail="Вы не подписаны на этого пользователя")

    # Удаляем подписку
    await db.delete(follow)
    await db.commit()

    return {"message": f"Вы успешно отписались от {target_user.username}"}
