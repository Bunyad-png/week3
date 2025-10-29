from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, String, func
from sqlalchemy.orm import relationship
from app.models.base import Base  # твой declarative base

class Comments(Base):
    __tablename__ = "comment"  # имя таблицы в БД

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    author = relationship("User", back_populates="comments")  # здесь "comments" должен существовать в User
