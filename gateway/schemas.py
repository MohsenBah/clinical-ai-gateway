from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    user_id: str = Field(default="demo-user", min_length=1, max_length=128)
    session_id: str = Field(default="demo-session", min_length=1, max_length=128)


class QueryResponse(BaseModel):
    answer: str
    request_id: str
