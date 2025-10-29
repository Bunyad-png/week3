from sqlalchemy.orm import joinedload
from app.models.комент import Comment
from app.schemas.user import PostDetail, UnfollowRequest, PostOut, UserCreate, UserResponse, CommentResponse
import os, shutil
from app.api.auth import create_access_token, create_refresh_token
from fastapi import APIRouter, Depends, HTTPException, Form, Query, UploadFile, File, status
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import get_user, create_user, verify_password, get_password_hash
from app.api.auth import create_access_token, get_current_user
from app.schemas.user import LoginRequest, LoginResponse,  UserWithFollowResponse, UserSearchOut, CommentOut
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
from app.api.auth import UPLOAD_DIR
from app.models.image import Image 
from datetime import datetime
from fastapi.responses import FileResponse
import urllib.parse
import uuid
from app.models.like import Like
from app.models.comment import Post
from app.schemas.user import Postcreate, LikeRequest, FollowRequest
from app.models.models import Comments

router = APIRouter(prefix="/auth", tags=["AUTH"])
BASE_URL = "http://localhost:9000"

@router.post("/comments")
async def create_comment(
    post_id: int,
    content: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_comment = Comments(
        post_id=post_id,
        user_id=current_user.id,  # <- обязательно!
        content=content
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment
    

@router.get("/comments/{post_id}", response_model=list[CommentOut])
async def get_comments(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список комментариев для поста с информацией об авторе и статусе подписки.
    """

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация"
        )

    # Загружаем комментарии с информацией об авторе
    stmt = (
        select(Comments)
        .options(joinedload(Comments.author))  # загружаем автора
        .where(Comments.post_id == post_id)
        .order_by(Comments.created_at.desc())
    )

    result = await db.execute(stmt)
    comments = result.scalars().all()

    response = []

    for comment in comments:
        # Проверка подписки
        has_followed = False
        if comment.author:
            follow_stmt = select(Follow).where(
                Follow.follower_id == current_user.id,
                Follow.following_id == comment.author.id
            )
            follow_result = await db.execute(follow_stmt)
            has_followed = follow_result.scalar_one_or_none() is not None

        response.append(CommentOut(
            id=comment.id,
            content=comment.content,
            this_user=(comment.user_id == current_user.id),
            created_at=comment.created_at,
            username=comment.author.username if comment.author else "Аноним",
            user_img=getattr(comment.author, "image_url", None),  # безопасно, если поля нет
            has_followed=has_followed
        ))

    return response




@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удаляет комментарий по id.
    Только автор комментария может его удалить.
    """

    # Получаем комментарий
    result = await db.execute(
        select(Comments).where(Comments.id == comment_id)
    )
    comment = result.scalar_one_or_none()

    if comment is None:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    # Проверка автора
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав на удаление этого комментария")

    # Удаляем комментарий
    await db.execute(delete(Comments).where(Comments.id == comment_id))
    await db.commit()

