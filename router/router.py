import base64
from io import BytesIO
import tempfile
from sqlalchemy.orm import Session
from table.table import ImageModel, BlackWhiteImage
from engine.engine import Base, engine, SessionLocal
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from model.image_model import ResponseImage
from typing import List
from removebg import RemoveBg
from model.black_white_image_model import ImageResponseImage

from PIL import Image as PILImage

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


# Define the endpoint to get all images
@router.get("/get-all-image", response_model=List[ResponseImage])
async def get_all_image(db: Session = Depends(connect_db)):
    db_images = db.query(ImageModel).all()
    if not db_images:
        raise HTTPException(status_code=404, detail="Not Found!!")

    return db_images


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


@router.post("/filter/black-white/{image_id}", response_model=ImageResponseImage)
async def black_white(image_id: int, db: Session = Depends(connect_db)):
    db_image_data = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    if not db_image_data:
        raise HTTPException(status_code=404, detail="Details not found!")

    image_data = base64.b64decode(db_image_data.image_data)
    image = PILImage.open(BytesIO(image_data))

    bw_image = image.convert('L')

    buffered = BytesIO()
    bw_image.save(buffered, format="PNG")

    bw_base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

    db_bw_image = BlackWhiteImage(black_white_image=bw_base64_image, image_id=image_id)
    db.add(db_bw_image)
    db.commit()
    db.refresh(db_bw_image)

    return db_bw_image


@router.get("/get-all-black-white-image", response_model=List[ImageResponseImage])
async def get_all_black_white_image(db: Session = Depends(connect_db)):
    all_image_data = db.query(BlackWhiteImage).all()
    if not all_image_data:
        return HTTPException(status_code=404, detail="Data is not found!!")
    else:
        return all_image_data
