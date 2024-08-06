from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from engine.engine import Base


# SQLAlchemy models
class ImageModel(Base):
    __tablename__ = "imaging"

    id = Column(Integer, primary_key=True, index=True)
    image_data = Column(String, nullable=False)
    black_white_images = relationship("BlackWhiteImage", back_populates="original_image")


class BlackWhiteImage(Base):
    __tablename__ = "black_white_png"

    id = Column(Integer, primary_key=True, autoincrement=True)
    black_white_image = Column(Text, nullable=False)
    image_id = Column(Integer, ForeignKey("imaging.id"), nullable=False)
    original_image = relationship("ImageModel", back_populates="black_white_images")
