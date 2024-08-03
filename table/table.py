from engine.engine import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class ImageModel(Base):
    __tablename__ = "imaging"
    __allow_unmapped__ = True  # Allow unmapped attributes

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    image_data: Mapped[str] = mapped_column(String, nullable=False)


class ResponseImage(Base):
    id: int
    image_data: str
