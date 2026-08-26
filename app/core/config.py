from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ai-document-qa"
    environment: str = "development"
    debug: bool = True

    database_url: str
    redis_url: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    max_file_size_mb: int = 20
    upload_dir: str = "uploads"
    allowed_file_types: str = "pdf,docx,txt"

    ai_provider: str = "gemini"
    gemini_api_key: str = ""
    embedding_model: str = "gemini-embedding-001"
    chat_model: str = "gemini-2.5-flash"

    rate_limit_per_minute: int = 30


settings = Settings()
