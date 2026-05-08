from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "clinical-ai-gateway"
    ollama_base_url: str = "http://localhost:11435"
    ollama_model: str = "llama3.2:1b"
    max_query_chars: int = 4000

    class Config:
        env_prefix = "GATEWAY_"


settings = Settings()
