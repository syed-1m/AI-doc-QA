from fastapi import FastAPI

app = FastAPI(title="AI Document Q&A API")


@app.get("/health")
async def health_check():
    return {"status": "ok"}