import uuid
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.repositories.document_repository import (
    create_document,
    delete_document,
    get_document_by_id,
    get_documents_by_user,
)
from app.schemas.document import DocumentResponse
from app.utils.file_validation import validate_upload

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    contents = await file.read()
    file_size = len(contents)

    mime_type = validate_upload(file, file_size)

    extension = file.filename.rsplit(".", 1)[-1].lower()
    stored_filename = f"{uuid.uuid4()}.{extension}"
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / stored_filename

    with open(file_path, "wb") as f:
        f.write(contents)

    document = await create_document(
        db,
        user_id=current_user.id,
        filename=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        mime_type=mime_type,
    )
    return document


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    document = await get_document_by_id(db, document_id)
    if document is None or document.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_documents_by_user(db, current_user.id)



@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    document = await get_document_by_id(db, document_id)
    if document is None or document.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    file_path = document.file_path
    await delete_document(db, document)

    if os.path.exists(file_path):
        os.remove(file_path)