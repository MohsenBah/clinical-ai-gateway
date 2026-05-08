from fastapi import FastAPI

from gateway.logging_config import configure_logging
from gateway.routes.health import router as health_router
from gateway.routes.query import router as query_router

configure_logging()

app = FastAPI(
    title="Clinical AI Gateway",
    description="Security-first gateway for clinical AI inference.",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(query_router)
