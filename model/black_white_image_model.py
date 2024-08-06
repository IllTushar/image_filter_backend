from pydantic import BaseModel


class CreateImageBlackWhite(BaseModel):
    image_id: int
    black_white_image: str


class ImageResponseImage(BaseModel):
    id: int
    image_id: int
    black_white_image: str

    class Config:
        orm_mode = True
