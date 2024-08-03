from pydantic import BaseModel


class ResponseImage(BaseModel):
    id: int
    image_data: str

    class Config:
        orm_mode = True
