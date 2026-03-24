from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    gemini_api_key: str = ""
    groq_api_key: str = ""
    chat_model: str = "groq/llama3-8b-8192"
    summary_model: str = "gemini/gemini-2.0-flash"
    advanced_model: str = "groq/llama-3.3-70b-versatile"
    embedding_model: str = "all-MiniLM-L6-v2"
    similarity_threshold: float = 0.3
    top_k: int = 5
    data_dir: str = "./data"

    # Derived paths
    @property
    def upload_dir(self) -> str:
        path = os.path.join(self.data_dir, "uploads")
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def index_dir(self) -> str:
        path = os.path.join(self.data_dir, "indices")
        os.makedirs(path, exist_ok=True)
        return path

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
