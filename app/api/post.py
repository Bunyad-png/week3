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

# @router.post("/auth/sign-up", response_model=LoginResponse, status_code=201)
# async def sign_up(user: UserCreate, db: AsyncSession = Depends(get_db)):
#     # Проверка: есть ли такой email уже
#     existing_user = await get_user_by_email(db, user.email)
#     if existing_user:
#         raise HTTPException(status_code=400, detail="User with this email already exists")
    
#     new_user = await create_user(db, user)

#     access_token = create_access_token({"sub": new_user.email})
#     refresh_token = create_refresh_token({"sub": new_user.email})

#     return {
#         "message": "User successfully created",
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer"
#     }



# @router.post("/auth/login", response_model=LoginResponse)
# async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
#     user = None

#     # если в identifier есть "@", предполагаем, что это email
#     if "@" in data.identifier:
#         user = await get_user_by_email(db, email=data.identifier)
#     else:
#         user = await get_user(db, username=data.identifier)

#     if not user or not verify_password(data.password, user.hashed_password):
#         raise HTTPException(status_code=401, detail="Неверный логин или пароль")

#     access_token = create_access_token(data={"sub": user.username})
#     refresh_token = create_refresh_token(data={"sub": user.username})

#     return {
#         "message": "Успешный вход",
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer",
#     }

# @router.get("/me", response_model=UserResponse)
# async def read_users_me(current_user = Depends(get_current_user)):
#     return current_user




# @router.get("/auth/refresh")
# async def refresh_token(
#     refresh_token: str = Depends(bearer_scheme),  # Берём токен из Authorization: Bearer
#     db: AsyncSession = Depends(get_db),
# ):
#     user = await verify_refresh_token(refresh_token, db)

#     # Генерируем новый access token
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username},
#         expires_delta=access_token_expires,
#     )

#     return {
#         "accessToken": access_token,
#         "token_type": "bearer",
#     }


# @router.post("/auth/authorize")
# async def authorize(
#     grant_type: str = Form(..., regex="password"),  # будет принимать только "password"
#     username: str = Form(...),
#     password: str = Form(...),
#     scope: str = Form(None),
#     client_id: str = Form(None),
#     client_secret: str = Form(None),
#     db: AsyncSession = Depends(get_db),
# ):
#     if grant_type != "password":
#         raise HTTPException(status_code=400, detail="Unsupported grant_type")

#     user = await get_user(db, username=username)
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid username or password")

#     if not verify_password(password, user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid username or password")

#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

#     access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
#     refresh_token = create_refresh_token(data={"sub": user.username}, expires_delta=refresh_token_expires)

#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer",
#         "scope": scope or "",
#     }




# @router.post("/auth/reset-pass")
# async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
#     user = await get_user(db, username=data.username)
#     if not user:
#         raise HTTPException(status_code=404, detail="Пользователь не найден")

#     # Здесь должна быть проверка кода подтверждения (например, из БД или кеша)
#     # Для примера сделаем заглушку, что код == 123456
#     if data.code != 123456:
#         raise HTTPException(status_code=400, detail="Неверный код подтверждения")

#     # Хешируем новый пароль
#     hashed_password = get_password_hash(data.new_pass)

#     # Обновляем пароль пользователя
#     user.hashed_password = hashed_password
#     db.add(user)
#     await db.commit()
#     await db.refresh(user)

#     return {"message": "Пароль успешно обновлен"}



# @router.get("/auth/me")
# async def get_myself(current_user: User = Depends(get_current_user)):
#     return {"attributes": dir(current_user)}

# @router.get("/auth/user", response_model=List[UserWithFollowResponse])
# async def get_user_by_username(
#     username: str = Query(..., description="Username пользователя"),
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(select(User).where(User.username == username))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail="Пользователь не найден")

#     # Проверка подписки
#     result_follow = await db.execute(
#         select(Follow).where(
#             (Follow.follower_id == current_user.id) & (Follow.following_id == user.id)
#         )
#     )
#     follow = result_follow.scalars().first()
#     has_followed = bool(follow)

#     # Подсчёт количества подписчиков
#     followers_count_result = await db.execute(
#         select(func.count(Follow.follower_id)).where(Follow.following_id == user.id)
#     )
#     followers_count = followers_count_result.scalar_one()

#     # Подсчёт количества подписок
#     followings_count_result = await db.execute(
#         select(func.count(Follow.following_id)).where(Follow.follower_id == user.id)
#     )
#     followings_count = followings_count_result.scalar_one()

#     response_data = UserWithFollowResponse(
#         first_name=user.first_name,
#         last_name=user.last_name,
#         email=user.email,
#         username=user.username,
#         followers=followers_count,
#         followings=followings_count,
#         user_img=user.user_image,
#         has_followed=has_followed
#     )

#     return [response_data]

# @router.get("/auth/users", response_model=List[UserResponse])
# async def get_all_users(db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(User))
#     users = result.scalars().all()
#     return users



# @router.post("/image/")
# async def upload_image(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
#     try:
#         # Убедимся, что папка существует
#         os.makedirs(UPLOAD_DIR, exist_ok=True)

#         # Путь к файлу
#         file_path = os.path.join(UPLOAD_DIR, file.filename)

#         # Сохраняем файл
#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         # Формируем URL (с заменой \ на / для Windows)
#         file_url = f"{BASE_URL}/{file_path.replace(os.sep, '/')}"

#         # Создаём объект изображения
#         image = Image(
#             filename=file.filename,
#             path=file_path,
#             upload_time=datetime.utcnow(),
#             url=file_url  # <--- добавлено поле url
#         )

#         db.add(image)
#         await db.commit()
#         await db.refresh(image)

#         return {"image_id": image.id, "url": image.url}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.get("/image/{image_id}/file")
# async def get_image_file(image_id: int, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Image).where(Image.id == image_id))
#     image = result.scalars().first()

#     if not image:
#         raise HTTPException(status_code=404, detail="Image not found")

#     file_path = image.path.replace("\\", "/")

#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="File not found on disk")

#     # 👇 Вот здесь правильно
#     encoded_filename = urllib.parse.quote(image.filename)

#     return FileResponse(
#         path=file_path,
#         media_type="image/*",
#         filename=image.filename,
#         headers={
#             "Content-Disposition": f"inline; filename*=UTF-8''{encoded_filename}"
#         }
#     )


# @router.post("/image/user")
# async def upload_user_image(
#     file: UploadFile = File(...),
#     db: AsyncSession = Depends(get_db)
# ):
#     if not file.content_type.startswith("image/"):
#         raise HTTPException(status_code=400, detail="Uploaded file is not an image.")
    
#     filename = f"{uuid.uuid4().hex}_{file.filename}"
#     file_path = os.path.join(UPLOAD_DIR, filename)
    
#     # Сохраняем файл (блокирующий вызов, можно заменить на aiofiles для асинхронности)
#     with open(file_path, "wb") as f:
#         content = await file.read()
#         f.write(content)

#     # Сохраняем запись в БД
#     new_image = Image(
#         filename=filename,  # Сохраняем уникальное имя, чтобы потом по нему ориентироваться
#         path=file_path,
#         url="",
#     )
#     db.add(new_image)
#     await db.commit()

#     return {"user_image": filename}



# @router.post("/posts/upload")
# async def upload_post(
#     post_data: Postcreate,
#     db: AsyncSession = Depends(get_db),
#     current_user = Depends(get_current_user)  # <-- добавлено
# ):
#     # Проверка существования изображения
#     result = await db.execute(select(Image).where(Image.id == post_data.image_id))
#     image = result.scalars().first()

#     if not image:
#         raise HTTPException(status_code=404, detail="Image not found")

#     # Создание поста
#     new_post = Post(
#         text=post_data.text,
#         image_id=post_data.image_id,
#         created_at=datetime.utcnow(),
#         user_id=current_user.id  # <-- добавлено
#     )

#     db.add(new_post)
#     await db.commit()
#     await db.refresh(new_post)

#     return {"message": "Post successfully created", "post_id": new_post.id}

# @router.get("/posts", response_model=List[PostOut])
# async def get_posts(db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Post).order_by(Post.created_at.desc()))
#     post = result.scalars().all()
#     return post

# @router.post("/posts/like")
# async def like_post(data: LikeRequest, db: AsyncSession = Depends(get_db)):
#     # Проверяем, существует ли пост
#     result = await db.execute(select(Post).where(Post.id == data.post_id))
#     post = result.scalar_one_or_none()
#     if post is None:
#         raise HTTPException(status_code=404, detail="Post not found")

#     # Добавляем лайк
#     new_like = Like(post_id=data.post_id)
#     db.add(new_like)
#     await db.commit()

#     return {"message": "Post liked successfully"}
# async def get_current_user_id():
#     return 1  # или сделай Depends(get_current_user) с авторизацией

# @router.get("/posts/{id}", response_model=PostDetail)
# async def get_post_detail(id: int, db: AsyncSession = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):

#     # Получаем пост
#     result = await db.execute(
#         select(Post).where(Post.id == id)
#     )
#     post = result.scalar_one_or_none()

#     if not post:
#         raise HTTPException(status_code=404, detail="Post not found")

#     # Получаем автора
#     result = await db.execute(
#         select(User).where(User.id == post.user_id)
#     )
#     user = result.scalar_one_or_none()

#     # Получаем изображение
#     result = await db.execute(
#         select(Image).where(Image.id == post.image_id)
#     )
#     image = result.scalar_one_or_none()

#     # Проверка лайка
#     result = await db.execute(
#         select(Like).where(Like.post_id == post.id, Like.user_id == current_user_id)
#     )
#     has_liked = result.scalar_one_or_none() is not None

#     # Проверка подписки
#     result = await db.execute(
#         select(Follow).where(Follow.follower_id == current_user_id, Follow.following_id == post.user_id)
#     )
#     has_followed = result.scalar_one_or_none() is not None

#     # Счётчики
#     likes_result = await db.execute(
#         select(Like).where(Like.post_id == post.id)
#     )
#     likes_count = len(likes_result.scalars().all())

#     comments_result = await db.execute(
#         select(Comment).where(Comment.post_id == post.id)
#     )
#     comments_count = len(comments_result.scalars().all())

#     return PostDetail(
#         id=post.id,
#         image=image.url if image else "",
#         username=user.username if user else "Unknown",
#         user_image=user.user_image if user else "",
#         text=post.text,
#         has_liked=has_liked,
#         has_followed=has_followed,
#         likes=likes_count,
#         comments=comments_count
#     )


# @router.post("/followings/follow")
# async def follow_user(
#     follow_request: FollowRequest,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     # Найти пользователя, на которого хотим подписаться
#     result = await db.execute(select(User).where(User.username == follow_request.username))
#     user_to_follow = result.scalars().first()
#     if not user_to_follow:
#         raise HTTPException(status_code=404, detail="Пользователь не найден")

#     if user_to_follow.id == current_user.id:
#         raise HTTPException(status_code=400, detail="Нельзя подписаться на самого себя")

#     # Проверяем, есть ли уже подписка
#     result = await db.execute(
#         select(Follow).where(
#             Follow.follower_id == current_user.id,
#             Follow.following_id == user_to_follow.id
#         )
#     )
#     existing_follow = result.scalars().first()
#     if existing_follow:
#         return {"message": "Вы уже подписаны на этого пользователя"}

#     # Создаем подписку
#     new_follow = Follow(
#         follower_id=current_user.id,
#         following_id=user_to_follow.id
#     )
#     db.add(new_follow)
#     await db.commit()

#     return {"message": f"Вы успешно подписались на {user_to_follow.username}"}


# @router.get("/following/followers")
# async def get_followers(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
#     result = await db.execute(
#         select(User).join(Follow, User.id == Follow.follower_id)
#         .where(Follow.following_id == current_user.id)
#     )
#     followers = result.scalars().all()

#     return [
#         {
#             "id": follower.id,
#             "username": follower.username,
#             "user_image": follower.user_image  # убедись, что поле называется правильно
#         }
#         for follower in followers
#     ]


# @router.post("/followings/unfollow")
# async def unfollow_user(
#     unfollow_data: UnfollowRequest,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     # Ищем пользователя, от которого хотим отписаться
#     result = await db.execute(select(User).where(User.username == unfollow_data.username))
#     target_user = result.scalars().first()

#     if not target_user:
#         raise HTTPException(status_code=404, detail="Пользователь не найден")

#     if target_user.id == current_user.id:
#         raise HTTPException(status_code=400, detail="Нельзя отписаться от самого себя")

#     # Ищем подписку
#     result = await db.execute(
#         select(Follow).where(
#             Follow.follower_id == current_user.id,
#             Follow.following_id == target_user.id
#         )
#     )
#     follow = result.scalars().first()

#     if not follow:
#         raise HTTPException(status_code=400, detail="Вы не подписаны на этого пользователя")

#     # Удаляем подписку
#     await db.delete(follow)
#     await db.commit()

#     return {"message": f"Вы успешно отписались от {target_user.username}"}


# @router.post("/comments")
# async def create_comment(
#     post_id: int,
#     content: str,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     new_comment = Comments(
#         post_id=post_id,
#         user_id=current_user.id,  # <- обязательно!
#         content=content
#     )
#     db.add(new_comment)
#     await db.commit()
#     await db.refresh(new_comment)
#     return new_comment
    

# @router.get("/comments/{post_id}", response_model=list[CommentOut])
# async def get_comments(
#     post_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Получить список комментариев для поста с информацией об авторе и статусе подписки.
#     """

#     if not current_user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Необходима авторизация"
#         )

#     # Загружаем комментарии с информацией об авторе
#     stmt = (
#         select(Comments)
#         .options(joinedload(Comments.author))  # загружаем автора
#         .where(Comments.post_id == post_id)
#         .order_by(Comments.created_at.desc())
#     )

#     result = await db.execute(stmt)
#     comments = result.scalars().all()

#     response = []

#     for comment in comments:
#         # Проверка подписки
#         has_followed = False
#         if comment.author:
#             follow_stmt = select(Follow).where(
#                 Follow.follower_id == current_user.id,
#                 Follow.following_id == comment.author.id
#             )
#             follow_result = await db.execute(follow_stmt)
#             has_followed = follow_result.scalar_one_or_none() is not None

#         response.append(CommentOut(
#             id=comment.id,
#             content=comment.content,
#             this_user=(comment.user_id == current_user.id),
#             created_at=comment.created_at,
#             username=comment.author.username if comment.author else "Аноним",
#             user_img=getattr(comment.author, "image_url", None),  # безопасно, если поля нет
#             has_followed=has_followed
#         ))

#     return response




# @router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_comment(
#     comment_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Удаляет комментарий по id.
#     Только автор комментария может его удалить.
#     """

#     # Получаем комментарий
#     result = await db.execute(
#         select(Comments).where(Comments.id == comment_id)
#     )
#     comment = result.scalar_one_or_none()

#     if comment is None:
#         raise HTTPException(status_code=404, detail="Комментарий не найден")

#     # Проверка автора
#     if comment.user_id != current_user.id:
#         raise HTTPException(status_code=403, detail="Нет прав на удаление этого комментария")

#     # Удаляем комментарий
#     await db.execute(delete(Comments).where(Comments.id == comment_id))
#     await db.commit()



# @router.get("/search", response_model=list[UserSearchOut])
# async def search_users(
#     username: str = Query(..., description="Username to search for"),
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Поиск пользователей по username.
#     Возвращает информацию о пользователе и статус подписки.
#     """

#     # Получаем всех пользователей, username которых содержит подстроку
#     stmt = select(User).where(User.username.ilike(f"%{username}%"))
#     result = await db.execute(stmt)
#     users = result.scalars().all()

#     response = []

#     for user in users:
#         # Проверяем, подписан ли current_user на этого пользователя
#         follow_stmt = select(Follow).where(
#             Follow.follower_id == current_user.id,
#             Follow.following_id == user.id
#         )
#         follow_result = await db.execute(follow_stmt)
#         has_followed = follow_result.scalar_one_or_none() is not None

#         response.append(UserSearchOut(
#             username=user.username,
#             user_img=user.image_url if hasattr(user, "image_url") else None,
#             has_followed=has_followed
#         ))

#     return response




@router.post("/posts/upload")
async def upload_post(
    post_data: Postcreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)  # <-- добавлено
):
    # Проверка существования изображения
    result = await db.execute(select(Image).where(Image.id == post_data.image_id))
    image = result.scalars().first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Создание поста
    new_post = Post(
        text=post_data.text,
        image_id=post_data.image_id,
        created_at=datetime.utcnow(),
        user_id=current_user.id  # <-- добавлено
    )

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    return {"message": "Post successfully created", "post_id": new_post.id}

@router.get("/posts", response_model=List[PostOut])
async def get_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).order_by(Post.created_at.desc()))
    post = result.scalars().all()
    return post

@router.post("/posts/like")
async def like_post(data: LikeRequest, db: AsyncSession = Depends(get_db)):
    # Проверяем, существует ли пост
    result = await db.execute(select(Post).where(Post.id == data.post_id))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # Добавляем лайк
    new_like = Like(post_id=data.post_id)
    db.add(new_like)
    await db.commit()

    return {"message": "Post liked successfully"}
async def get_current_user_id():
    return 1  # или сделай Depends(get_current_user) с авторизацией

@router.get("/posts/{id}", response_model=PostDetail)
async def get_post_detail(id: int, db: AsyncSession = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):

    # Получаем пост
    result = await db.execute(
        select(Post).where(Post.id == id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Получаем автора
    result = await db.execute(
        select(User).where(User.id == post.user_id)
    )
    user = result.scalar_one_or_none()

    # Получаем изображение
    result = await db.execute(
        select(Image).where(Image.id == post.image_id)
    )
    image = result.scalar_one_or_none()

    # Проверка лайка
    result = await db.execute(
        select(Like).where(Like.post_id == post.id, Like.user_id == current_user_id)
    )
    has_liked = result.scalar_one_or_none() is not None

    # Проверка подписки
    result = await db.execute(
        select(Follow).where(Follow.follower_id == current_user_id, Follow.following_id == post.user_id)
    )
    has_followed = result.scalar_one_or_none() is not None

    # Счётчики
    likes_result = await db.execute(
        select(Like).where(Like.post_id == post.id)
    )
    likes_count = len(likes_result.scalars().all())

    comments_result = await db.execute(
        select(Comment).where(Comment.post_id == post.id)
    )
    comments_count = len(comments_result.scalars().all())

    return PostDetail(
        id=post.id,
        image=image.url if image else "",
        username=user.username if user else "Unknown",
        user_image=user.user_image if user else "",
        text=post.text,
        has_liked=has_liked,
        has_followed=has_followed,
        likes=likes_count,
        comments=comments_count
    )
