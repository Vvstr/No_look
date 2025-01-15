from pydantic import BaseModel, Field
from typing import Optional, List


class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = Field(2)
    scenario: str
    url: Optional[str] = None
    selector: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    context: List[str]
    scenario_used: str


class ScrapeRequest(BaseModel):
    url: str
    selector: str


class ScrapeResponse(BaseModel):
    data: List[str]


class ContextItem(BaseModel):
    content: str
