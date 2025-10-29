# # app/models.py

# from datetime import datetime
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
# from sqlalchemy import String, DateTime
# from app.models.comment import Post
# # Базовый класс для моделей
# class Base(DeclarativeBase):
#     pass

# class Image(Base):
#     __tablename__ = "images"

#     id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
#     filename: Mapped[str] = mapped_column(String, nullable=False)
#     path: Mapped[str] = mapped_column(String, nullable=False)
#     upload_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
#     posts: Mapped[list["Post"]] = relationship("Post", back_populates="image")


from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime

# Если Base общий, импортируй из base.py
from app.models.base import Base

class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    upload_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    url: Mapped[str] = mapped_column(String, nullable=True)

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="image")
