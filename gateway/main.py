from fastapi import FastAPI

from gateway.logging_config import configure_logging
from gateway.routes.health import router as health_router
from gateway.routes.query import router as query_router
from gateway.routes.data import router as data_router
from gateway.services.llm_client import LLMClient
from gateway.services.data_ingestion import DataIngestionService

configure_logging()

# Initialize services
llm_client = LLMClient()
data_service = DataIngestionService()
llm_client.set_data_service(data_service)

app = FastAPI(
    title="Clinical AI Gateway",
    description="Security-first gateway for clinical AI inference with RAG.",
    version="0.1.0",
)

# Make services available to routes
app.state.llm_client = llm_client
app.state.data_service = data_service

app.include_router(health_router)
app.include_router(query_router)
app.include_router(data_router, prefix="/data", tags=["data"])
