from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # LLM
    gemini_api_key: str = ""
    llm_provider: str = "groq"          # "gemini" or "groq"
    gemini_model: str = "gemini-2.0-flash-lite"

    # Groq (free tier: 6000 RPM, 14400 RPD)
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"

    # Embedding
    embedding_model: str = "all-MiniLM-L6-v2"

    # Vector DB
    chroma_persist_dir: str = "./data/chroma_db"
    chroma_collection_name: str = "documents"

    # Search
    top_k_results: int = 5
    similarity_threshold: float = 0.2

    # Auth
    secret_key: str = "changeme"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Files
    upload_dir: str = "./data/uploads"
    max_file_size_mb: int = 50

    # App
    app_name: str = "DocSearch Engine"
    app_version: str = "1.0.0"
    debug: bool = True
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
