from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Yser(Base):
    __tablename__ = "auhter"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    image_url: Mapped[str | None] = mapped_column(nullable=True)

    comments: Mapped[list["Comment"]] = relationship(back_populates="author")