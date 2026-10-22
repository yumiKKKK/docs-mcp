from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    filename: str
    score: int = Field(ge=1)
    matched_terms: list[str]
    snippet: str


class SearchResponse(BaseModel):
    query: str
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=50)
    total_pages: int = Field(ge=0)
    has_next: bool
    has_previous: bool
    results: list[SearchResult]
