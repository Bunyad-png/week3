# from sqlalchemy.orm import Mapped, mapped_column
# from sqlalchemy import String, Integer, Boolean
# from app.models.base import Base  # или откуда у тебя Base
# from typing import List
# from sqlalchemy.orm import  relationship

# class User(Base):
#     __tablename__ = "users"

#     id: Mapped[int] = mapped_column(primary_key=True, index=True)
#     email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
#     hashed_password: Mapped[str] = mapped_column(String, nullable=False)
#     username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=True)  # разрешаем NULL
#     is_active: Mapped[bool] = mapped_column(Boolean, default=True)

#     posts: Mapped[List["Post"]] = relationship("Post", back_populates="user")

#     @property
#     def first_name(self):
#         return "DefaultFirstName"  # Можешь заменить на self.username.split("_")[0] если хочешь

#     @property
#     def last_name(self):
#         return "DefaultLastName"

#     @property
#     def followers(self):
#         return 0  # Временно, пока нет реального поля

#     @property
#     def followings(self):
#         return 0

#     @property
#     def user_img(self):
#         return "default.png"



from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, Text

from app.models.base import Base  # Импорт твоего базового класса


from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    posts: Mapped[List[Post]] = relationship("Post", back_populates="user")  # Обратная связь на Post

    comments: Mapped[List["Comments"]] = relationship("Comments", back_populates="author", cascade="all, delete-orphan")
    @property
    def first_name(self):
        return "DefaultFirstName"

    @property
    def last_name(self):
        return "DefaultLastName"

    @property
    def followers(self):
        return 0

    @property
    def followings(self):
        return 0

    @property
    def user_image(self):
        return "default.png"
