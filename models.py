from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., example="English or Spanish?")
    top_k: Optional[int] = Field(2, example=2, description="Number of context items to retrieve.")
    scenario: str = Field("classic", example="classic", description="RAG scenario to use: classic, scraping, combined.")


class QueryResponse(BaseModel):
    answer: str
    context: List[str]
    scenario_used: str


class ScrapeRequest(BaseModel):
    url: str = Field(..., example="")
    selector: str = Field(..., example=".policy-text")


class ScrapeResponse(BaseModel):
    data: List[str]


class ContextItem(BaseModel):
    content: str = Field(..., example="")