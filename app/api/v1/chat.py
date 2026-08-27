import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import generate_answer, generate_embedding
from app.core.security import get_current_user
from app.core.rate_limit import rate_limiter
from app.db.database import get_db
from app.models.user import User
from app.repositories.document_repository import get_document_by_id, search_similar_chunks
from app.schemas.chat import QueryRequest
from app.services.semantic_cache import get_cached_answer, store_answer

router = APIRouter(prefix="/chat", tags=["chat"])


def _sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/query")
async def query_documents(
    payload: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limiter),
):
    async def event_stream():
        yield _sse_event("request_accepted", {"question": payload.question})

        question_embedding = generate_embedding(payload.question)

        cached = await get_cached_answer(str(current_user.id), question_embedding)
        if cached is not None:
            yield _sse_event("cache_hit", {"similarity": cached["similarity"]})
            yield _sse_event(
                "complete", {"answer": cached["answer"], "sources": cached["sources"]}
            )
            return

        yield _sse_event("cache_miss", {})
        yield _sse_event("document_search", {"status": "searching"})

        chunks = await search_similar_chunks(db, current_user.id, question_embedding, limit=5)

        if not chunks:
            yield _sse_event(
                "complete",
                {
                    "answer": "I don't have any documents to search yet. Please upload a document first.",
                    "sources": [],
                },
            )
            return

        yield _sse_event("chunks_retrieved", {"count": len(chunks)})

        context_texts = [chunk.content for chunk in chunks]
        yield _sse_event("context_created", {"chunk_count": len(context_texts)})

        answer = generate_answer(payload.question, context_texts)
        yield _sse_event("answer_generation", {"answer": answer})

        sources = []
        for chunk in chunks:
            document = await get_document_by_id(db, chunk.document_id)
            sources.append(
                {
                    "document_id": str(chunk.document_id),
                    "filename": document.filename if document else "unknown",
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                }
            )
        yield _sse_event("sources_found", {"sources": sources})

        await store_answer(str(current_user.id), question_embedding, answer, sources)

        yield _sse_event("complete", {"answer": answer, "sources": sources})

    return StreamingResponse(event_stream(), media_type="text/event-stream")