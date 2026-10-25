from pydantic import BaseModel, Field
from typing import Any

class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)

class Evidence(BaseModel):
    source_id: str
    source_type: str
    text: str
    score: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)

class QueryResponse(BaseModel):
    question: str
    answer: str
    route: str
    citations: list[Evidence] = Field(default_factory=list)
    retrieval_attempts: int = 0
    correction_used: bool = False
    self_rag: dict[str, Any] = Field(default_factory=dict)
    abstained: bool = False

class HealthResponse(BaseModel):
    status: str
    database_ready: bool
    dataset_rows: int
