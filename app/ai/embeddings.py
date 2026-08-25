import google.generativeai as genai

from app.core.config import settings

genai.configure(api_key=settings.gemini_api_key)

EMBEDDING_DIMENSION = 1536


def _normalize(vector: list[float]) -> list[float]:
    """Gemini requires manual normalization when requesting fewer than 3072 dimensions."""
    magnitude = sum(x * x for x in vector) ** 0.5
    if magnitude == 0:
        return vector
    return [x / magnitude for x in vector]


def generate_embedding(text: str) -> list[float]:
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured")

    result = genai.embed_content(
        model=f"models/{settings.embedding_model}",
        content=text,
        task_type="retrieval_document",
        output_dimensionality=EMBEDDING_DIMENSION,
    )
    return _normalize(result["embedding"])