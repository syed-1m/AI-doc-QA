# AI Document Q&A API

A FastAPI backend that lets users upload documents (PDF/DOCX/TXT), automatically processes them into searchable chunks with embeddings, and answers natural-language questions about their content using Retrieval-Augmented Generation (RAG) — with streamed responses, source citations, and a semantic cache.

## Features

- **Authentication** — JWT-based register/login, protected routes
- **Document management** — upload, list, retrieve, delete (owner-scoped)
- **Automatic background processing** — text extraction, chunking, and embedding generation via a dedicated ARQ worker
- **RAG-powered Q&A** — ask questions about your documents, get grounded answers with page-level citations
- **Streaming responses** — Server-Sent Events (SSE) showing live progress through the query pipeline
- **Semantic caching** — repeated or similarly-worded questions are served from cache instead of re-running the full pipeline
- **Rate limiting** — Redis-backed, per-user, per-endpoint
- **Consistent error handling** — every error returns `{ "error": { "code": ..., "message": ... } }`

## Tech Stack

- **API**: FastAPI, Pydantic v2
- **Database**: PostgreSQL + pgvector, SQLAlchemy (async), Alembic migrations
- **Cache / Queue**: Redis, ARQ (background worker)
- **AI**: Google Gemini (`gemini-embedding-001` for embeddings, `gemini-3.6-flash` for chat)
- **Auth**: JWT (PyJWT), bcrypt password hashing
- **Infra**: Docker, Docker Compose

## Prerequisites

- Docker Desktop installed and running
- A free [Google Gemini API key](https://aistudio.google.com) (no credit card required)

## Setup

1. Clone the repository:
```bash
   git clone https://github.com/syed-1m/AI-doc-QA.git
   cd AI-doc-QA
```

2. Copy the example environment file and fill in your values:
```bash
   cp .env.example .env
```
   At minimum, set:

   GEMINI_API_KEY=your-key-here
JWT_SECRET=some-long-random-string


3. Start the full stack:
```bash
   docker compose up -d --build
```
   This starts four containers: `api` (FastAPI), `worker` (ARQ background processor), `db` (PostgreSQL + pgvector), and `redis`.

4. Apply database migrations (first run only):
```bash
   docker compose exec api alembic upgrade head
```

5. Confirm it's running:

http://localhost:8000/health
   Should return `{"status": "ok", ...}`.

## API Documentation

Interactive Swagger UI is available at:

http://localhost:8000/docs

## Quick Start Walkthrough

1. **Register**: `POST /api/v1/auth/register` with `{"email": "...", "password": "..."}`
2. **Login**: `POST /api/v1/auth/login` — copy the returned `access_token`
3. **Authorize**: click "Authorize" in Swagger UI, paste the token
4. **Upload a document**: `POST /api/v1/documents/upload` with a PDF/DOCX/TXT file
5. **Wait a few seconds**, then check `GET /api/v1/documents/{id}` — `status` should change from `"pending"` to `"completed"`
6. **Ask a question**: `POST /api/v1/chat/query` with `{"question": "..."}` — returns a streamed answer with sources

## Project Structure

app/
├── api/v1/ # Route handlers (auth, documents, chat)
├── services/ # Business logic (document processing, semantic cache)
├── repositories/ # Database queries
├── ai/ # Embedding and chat generation (Gemini integration)
├── models/ # SQLAlchemy ORM models
├── schemas/ # Pydantic request/response schemas
├── db/ # Database engine and session setup
├── core/ # Config, security, rate limiting
└── workers/ # ARQ background task definitions
alembic/ # Database migrations


## Known Limitations

- DOCX and TXT files don't have real page boundaries, so `page_number` is always `1` for those formats (PDFs report accurate page numbers).
- Single-region deployment; no multi-tenant document sharing.
- Semantic cache correctness depends on cache entries being scoped per-user; cache does not currently invalidate automatically if a source document is edited or deleted (documents can still be deleted independently via the API).