from fastapi import APIRouter, Depends, Query
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth import  get_current_user
from app.schemas.user import  UserSearchOut
from app.models.user import User
from sqlalchemy.future import select
from app.models.post import Follow


router = APIRouter(prefix="/auth", tags=["AUTH"])
BASE_URL = "http://localhost:9000"

@router.get("/search", response_model=list[UserSearchOut])
async def search_users(
    username: str = Query(..., description="Username to search for"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Поиск пользователей по username.
    Возвращает информацию о пользователе и статус подписки.
    """

    # Получаем всех пользователей, username которых содержит подстроку
    stmt = select(User).where(User.username.ilike(f"%{username}%"))
    result = await db.execute(stmt)
    users = result.scalars().all()

    response = []

    for user in users:
        # Проверяем, подписан ли current_user на этого пользователя
        follow_stmt = select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == user.id
        )
        follow_result = await db.execute(follow_stmt)
        has_followed = follow_result.scalar_one_or_none() is not None

        response.append(UserSearchOut(
            username=user.username,
            user_img=user.image_url if hasattr(user, "image_url") else None,
            has_followed=has_followed
        ))

    return response


