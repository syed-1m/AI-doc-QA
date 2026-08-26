import uuid

from app.models.document_chunk import DocumentChunk
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


async def create_document(
    db: AsyncSession,
    user_id: uuid.UUID,
    filename: str,
    file_path: str,
    file_size: int,
    mime_type: str,
) -> Document:
    document = Document(
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=mime_type,
        status="pending",
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def get_document_by_id(db: AsyncSession, document_id: uuid.UUID) -> Document | None:
    result = await db.execute(select(Document).where(Document.id == document_id))
    return result.scalar_one_or_none()

async def get_documents_by_user(db: AsyncSession, user_id: uuid.UUID) -> list[Document]:
    result = await db.execute(select(Document).where(Document.user_id == user_id))
    return list(result.scalars().all())


async def delete_document(db: AsyncSession, document: Document) -> None:
    db.delete(document)
    await db.commit()


async def search_similar_chunks(
    db: AsyncSession, user_id: uuid.UUID, query_embedding: list[float], limit: int = 5
) -> list[DocumentChunk]:
    result = await db.execute(
        select(DocumentChunk)
        .join(Document, DocumentChunk.document_id == Document.id)
        .where(Document.user_id == user_id)
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    return list(result.scalars().all())