from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class ImageModel(Base):
    __tablename__ = "imaging"
    __allow_unmapped__ = True  # Allow unmapped attributes

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    image_data: Mapped[str] = mapped_column(String, nullable=False)
