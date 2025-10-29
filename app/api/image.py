from sqlalchemy.orm import joinedload
import os, shutil
from fastapi import APIRouter, Depends, HTTPException,  UploadFile, File
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.auth import UPLOAD_DIR
from app.models.image import Image 
from datetime import datetime
from fastapi.responses import FileResponse
import urllib.parse
import uuid


router = APIRouter(prefix="/auth", tags=["AUTH"])
BASE_URL = "http://localhost:9000"

@router.post("/image/")
async def upload_image(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    try:
        # Убедимся, что папка существует
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Путь к файлу
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Формируем URL (с заменой \ на / для Windows)
        file_url = f"{BASE_URL}/{file_path.replace(os.sep, '/')}"

        # Создаём объект изображения
        image = Image(
            filename=file.filename,
            path=file_path,
            upload_time=datetime.utcnow(),
            url=file_url  # <--- добавлено поле url
        )

        db.add(image)
        await db.commit()
        await db.refresh(image)

        return {"image_id": image.id, "url": image.url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/image/{image_id}/file")
async def get_image_file(image_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Image).where(Image.id == image_id))
    image = result.scalars().first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    file_path = image.path.replace("\\", "/")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    # 👇 Вот здесь правильно
    encoded_filename = urllib.parse.quote(image.filename)

    return FileResponse(
        path=file_path,
        media_type="image/*",
        filename=image.filename,
        headers={
            "Content-Disposition": f"inline; filename*=UTF-8''{encoded_filename}"
        }
    )


@router.post("/image/user")
async def upload_user_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image.")
    
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Сохраняем файл (блокирующий вызов, можно заменить на aiofiles для асинхронности)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Сохраняем запись в БД
    new_image = Image(
        filename=filename,  # Сохраняем уникальное имя, чтобы потом по нему ориентироваться
        path=file_path,
        url="",
    )
    db.add(new_image)
    await db.commit()

    return {"user_image": filename}