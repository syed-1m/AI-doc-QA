from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import generate_answer, generate_embedding
from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.repositories.document_repository import get_document_by_id, search_similar_chunks
from app.schemas.chat import QueryRequest, QueryResponse, SourceChunk

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    payload: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    question_embedding = generate_embedding(payload.question)

    chunks = await search_similar_chunks(db, current_user.id, question_embedding, limit=5)

    if not chunks:
        return QueryResponse(
            answer="I don't have any documents to search yet. Please upload a document first.",
            sources=[],
        )

    context_texts = [chunk.content for chunk in chunks]
    answer = generate_answer(payload.question, context_texts)

    sources = []
    for chunk in chunks:
        document = await get_document_by_id(db, chunk.document_id)
        sources.append(
            SourceChunk(
                document_id=chunk.document_id,
                filename=document.filename if document else "unknown",
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
            )
        )

    return QueryResponse(answer=answer, sources=sources)