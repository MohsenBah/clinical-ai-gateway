import time
import uuid

from fastapi import APIRouter, HTTPException, Request

from gateway.middleware.audit import audit_log
from gateway.middleware.input_validation import validate_input
from gateway.middleware.output_filter import filter_output
from gateway.middleware.rate_limit import check_rate_limit
from gateway.schemas import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query_model(request: QueryRequest, app_request: Request) -> QueryResponse:
    llm_client = app_request.app.state.llm_client

    start = time.perf_counter()
    request_id = str(uuid.uuid4())

    if not check_rate_limit(request.user_id):
        audit_log(
            event_type="query",
            request_id=request_id,
            user_id=request.user_id,
            session_id=request.session_id,
            decision="blocked",
            reason="rate_limit_exceeded",
            query_length=len(request.query),
        )
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "request_id": request_id,
            },
        )

    validation = validate_input(request.query)
    if not validation.allowed:
        audit_log(
            event_type="query",
            request_id=request_id,
            user_id=request.user_id,
            session_id=request.session_id,
            decision="blocked",
            reason=validation.reason,
            query_length=len(request.query),
            blocked_category=validation.category,
            matched_pattern=validation.matched_pattern,
        )
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Input failed safety validation",
                "request_id": request_id,
            },
        )

    raw_answer = llm_client.generate(request.query)
    filtered = filter_output(raw_answer)

    latency_ms = round((time.perf_counter() - start) * 1000, 2)

    audit_log(
        event_type="query",
        request_id=request_id,
        user_id=request.user_id,
        session_id=request.session_id,
        decision="allowed",
        reason=filtered.reason,
        query_length=len(request.query),
        response_length=len(filtered.safe_text),
        output_modified=filtered.modified,
        latency_ms=latency_ms,
    )

    return QueryResponse(answer=filtered.safe_text, request_id=request_id)
