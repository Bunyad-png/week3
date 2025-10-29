# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from sqlalchemy import Integer, Text, ForeignKey, DateTime
# from datetime import datetime
# from app.models.base import Base
# from app.models.image import Image

# class Post(Base):
#     __tablename__ = "posts"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
#     text: Mapped[str] = mapped_column(Text, nullable=False)
#     image_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("images.id"), nullable=True)
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

#     image: Mapped["Image"] = relationship("Image", backref="posts")


# from __future__ import annotations
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from sqlalchemy import Integer, Text, ForeignKey
# from typing import Optional
# from datetime import datetime
# from sqlalchemy import  DateTime
# # Импортируем общий Base (из base.py)
# from app.models.base import Base

# class Post(Base):
#     __tablename__ = "posts"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
#     text: Mapped[str] = mapped_column(Text, nullable=False)
#     image_id: Mapped[int | None] = mapped_column(ForeignKey("images.id"), nullable=True)
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

#     image: Mapped[Optional["Image"]] = relationship("Image", back_populates="posts")
#     user: Mapped[Optional[User]] = relationship("User", back_populates="posts")


from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Text, ForeignKey, DateTime
from typing import Optional
from datetime import datetime
from app.models.base import Base

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    image_id: Mapped[Optional[int]] = mapped_column(ForeignKey("images.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)  # Внешний ключ на users.id
    user: Mapped[Optional[User]] = relationship("User", back_populates="posts")

    image: Mapped[Optional["Image"]] = relationship("Image", back_populates="posts")
