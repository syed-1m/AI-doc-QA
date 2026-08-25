import uuid

from arq.connections import RedisSettings
from sqlalchemy import select

from app.core.config import settings
from app.db.database import async_session_factory
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.document_processor import chunk_text, extract_text


async def process_document(ctx, document_id: str) -> None:
    """
    ARQ task: extracts text from a document, chunks it, stores the chunks,
    and updates the document's status. No embeddings yet (that's a later step).
    """
    async with async_session_factory() as db:
        result = await db.execute(select(Document).where(Document.id == uuid.UUID(document_id)))
        document = result.scalar_one_or_none()

        if document is None:
            print(f"[worker] Document {document_id} not found, skipping.")
            return

        try:
            pages = extract_text(document.file_path, document.mime_type)

            total_chunks = 0
            for page_text, page_number in pages:
                chunks = chunk_text(page_text)
                for i, chunk_content in enumerate(chunks):
                    db_chunk = DocumentChunk(
                        document_id=document.id,
                        chunk_index=total_chunks,
                        content=chunk_content,
                        page_number=page_number,
                    )
                    db.add(db_chunk)
                    total_chunks += 1

            document.status = "completed"
            document.page_count = len(pages)
            await db.commit()

            print(f"[worker] Processed document {document_id}: {total_chunks} chunks created.")

        except Exception as e:
            document.status = "failed"
            await db.commit()
            print(f"[worker] Failed to process document {document_id}: {e}")


class WorkerSettings:
    functions = [process_document]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)