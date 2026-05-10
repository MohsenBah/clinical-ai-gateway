from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class IngestDataRequest(BaseModel):
    data_path: str
    clear_existing: bool = False


class IngestDataResponse(BaseModel):
    success: bool
    records_ingested: int
    message: str


@router.post("/ingest", response_model=IngestDataResponse)
def ingest_data(request: IngestDataRequest, app_request: Request) -> IngestDataResponse:
    """Ingest clinical data into the vector database."""
    data_service = app_request.app.state.data_service

    try:
        if request.clear_existing:
            data_service.clear_collection()

        records_ingested = data_service.ingest_data(request.data_path)

        return IngestDataResponse(
            success=True,
            records_ingested=records_ingested,
            message=f"Successfully ingested {records_ingested} clinical records"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Data ingestion failed: {str(e)}"
        )


@router.delete("/clear")
def clear_data(app_request: Request):
    """Clear all data from the vector database."""
    data_service = app_request.app.state.data_service

    try:
        data_service.clear_collection()
        return {"message": "Vector database cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Clear operation failed: {str(e)}"
        )