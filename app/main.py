# from fastapi import FastAPI
# from app.api import post
# from app.core.database import engine
# from app.models.base import Base
# from app.api.post import router as post_router  # импорт из post.py
# import asyncio


# app = FastAPI()

# app.include_router(post.router)
# app.include_router(post_router)
# app.include_router(post.router, prefix="/api")

# @app.on_event("startup")
# async def on_startup():
#     # Создаем таблицы
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

from app.models.base import Base
from app.core.database import engine
from fastapi import FastAPI
from app.api.untls import router as auth_router
from app.api.post import router as posts_router
from app.api.image import router as images_router
from app.api.comment import router as comment_router
from app.api.follow import router as follow_router
from app.api.search import router as search_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(posts_router, prefix="/posts")
app.include_router(images_router, prefix="/images")
app.include_router(comment_router, prefix="/comment")
app.include_router(follow_router, prefix="/follow")
app.include_router(search_router, prefix="/search")

@app.on_event("startup")
async def on_startup():
    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

