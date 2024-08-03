import base64
from io import BytesIO
import tempfile
from sqlalchemy.orm import Session
from table.table import ImageModel
from engine.engine import Base, engine, SessionLocal
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from model.image_model import ResponseImage
from removebg import RemoveBg
from sqlalchemy import Column, Integer, String, create_engine

from PIL import Image as PILImage
from pydantic import BaseModel
import os

router = APIRouter(prefix="/image", tags=["Image"])

# Create the tables in the database
Base.metadata.create_all(bind=engine)


def connect_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Define remove_bg with your API key
remove_bg = RemoveBg("87a4tgufMMc7Cyb4WTxdGYwa", "error.log")


@router.post("/upload-image/", response_model=ResponseImage)
async def upload_image(file: UploadFile = File(...), db: Session = Depends(connect_db)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Read the file content
    file_content = await file.read()
    image = PILImage.open(BytesIO(file_content))

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    db_image = ImageModel(image_data=img_str)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    return {"id": db_image.id, "image_data": db_image.image_data}


@router.get("/remove-bg/{image_id}", response_model=ResponseImage)
async def remove_bg_endpoint(image_id: int, db: Session = Depends(connect_db)):
    db_image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")

    img_data = base64.b64decode(db_image.image_data)
    input_image = PILImage.open(BytesIO(img_data))

    # Use in-memory bytes buffer instead of a temporary file
    input_buffer = BytesIO()
    input_image.save(input_buffer, format="PNG")
    input_buffer.seek(0)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as output_temp:
        output_temp_path = output_temp.name

    try:
        # Save the input buffer to a temporary file
        with open(output_temp_path, "wb") as input_temp:
            input_temp.write(input_buffer.getvalue())

        # Use the existing remove_background_from_img_file method
        remove_bg.remove_background_from_img_file(output_temp_path)

        # Read the processed image from the temporary output file
        with open(output_temp_path, "rb") as output_image_file:
            output_img_data = output_image_file.read()

        output_img_str = base64.b64encode(output_img_data).decode("utf-8")

    finally:
        os.remove(output_temp_path)

    return {"id": image_id, "image_data": output_img_str}
