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

def generate_answer(question: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    prompt = (
        "You are a helpful assistant that answers questions using only the provided context. "
        "If the answer is not contained in the context, say so clearly instead of guessing.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )
    model = genai.GenerativeModel(settings.chat_model)
    response = model.generate_content(prompt)
    return response.text