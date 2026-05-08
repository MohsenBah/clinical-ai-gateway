import httpx

from gateway.config import settings


class LLMClient:
    def generate(self, prompt: str) -> str:
        try:
            response = httpx.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except Exception:
            return "Model response placeholder. Ollama is not available."
