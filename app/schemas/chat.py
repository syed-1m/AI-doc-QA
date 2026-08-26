import uuid

from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class SourceChunk(BaseModel):
    document_id: uuid.UUID
    filename: str
    page_number: int | None
    chunk_index: int


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]