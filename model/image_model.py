from pydantic import BaseModel
from typing import List


class ResponseImage(BaseModel):
    id: int
    image_data: str

    class Config:
        orm_mode = True
