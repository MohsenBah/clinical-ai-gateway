import httpx
import logging
from typing import List, Dict, Any, Optional

from gateway.config import settings
from gateway.services.data_ingestion import DataIngestionService

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.data_service: Optional[DataIngestionService] = None

    def set_data_service(self, data_service: DataIngestionService):
        """Set the data ingestion service for RAG functionality."""
        self.data_service = data_service

    def retrieve_context(self, query: str) -> str:
        """Retrieve relevant clinical context for the query."""
        if not self.data_service:
            logger.warning("Data service not configured, skipping RAG")
            return ""

        try:
            results = self.data_service.search_similar(query)
            if not results:
                return ""

            # Format context from retrieved documents
            context_parts = []
            for i, result in enumerate(results, 1):
                doc = result['document']
                metadata = result['metadata']
                distance = result['distance']

                context_parts.append(
                    f"Document {i} (relevance: {1-distance:.3f}):\n{doc}\n"
                )

            context = "\n".join(context_parts)
            logger.info(f"Retrieved {len(results)} context documents")
            return context

        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return ""

    def build_rag_prompt(self, query: str, context: str) -> str:
        """Build a RAG-enhanced prompt."""
        if not context:
            return query

        system_prompt = """You are a clinical AI assistant helping healthcare professionals.
Use the provided clinical context to inform your responses, but prioritize patient safety and privacy.
If the context is insufficient, clearly state your limitations.
Always maintain HIPAA compliance and avoid disclosing protected health information.

Clinical Context:
{context}

User Query: {query}

Response:"""

        return system_prompt.format(context=context, query=query)

    def generate(self, prompt: str, use_rag: bool = True) -> str:
        """Generate response from LLM, optionally using RAG."""
        # Retrieve context if RAG is enabled
        context = ""
        if use_rag:
            context = self.retrieve_context(prompt)

        # Build enhanced prompt
        enhanced_prompt = self.build_rag_prompt(prompt, context) if context else prompt

        try:
            response = httpx.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": enhanced_prompt,
                    "stream": False,
                },
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "Model response placeholder. Ollama is not available."
