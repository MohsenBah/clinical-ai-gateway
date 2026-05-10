from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "clinical-ai-gateway"
    ollama_base_url: str = "http://localhost:11435"
    ollama_model: str = "llama3.2:1b"
    max_query_chars: int = 4000

    # Vector database settings
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    collection_name: str = "clinical_records"

    # RAG settings
    max_context_docs: int = 3
    embedding_model: str = "all-MiniLM-L6-v2"

    class Config:
        env_prefix = "GATEWAY_"


settings = Settings()
