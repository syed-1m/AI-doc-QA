from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

ALLOWED_EXTENSIONS = {ext.strip().lower() for ext in settings.allowed_file_types.split(",")}
ALLOWED_MIME_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "txt": "text/plain",
}
MAX_FILE_SIZE_BYTES = settings.max_file_size_mb * 1024 * 1024


def validate_upload(file: UploadFile, file_size: int) -> str:
    extension = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '.{extension}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.max_file_size_mb}MB",
        )

    return ALLOWED_MIME_TYPES.get(extension, "application/octet-stream")