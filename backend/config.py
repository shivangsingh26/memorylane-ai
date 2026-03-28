from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # LLM / OpenAI Configuration
    openai_api_key: str = ""
    model_name: str = "gpt-5.1"          # latest OpenAI model
    embedding_model: str = "text-embedding-3-small"

    # Data
    data_dir: str = "./data"
    chroma_persist_dir: str = "./data/chroma"
    analytics_file: str = "./data/analytics.json"

    # App
    user1_name: str = "Shivang"
    user2_name: str = "Krishna"
    chunk_size: int = 7
    rag_top_k: int = 5

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

# Ensure data dirs exist on import
Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
