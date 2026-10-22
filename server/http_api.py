"""Optional HTTP adapter; shares the exact SearchService used by MCP."""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from .document_repository import DocumentRepository
from .search_service import SearchService

BASE_DIR = Path(__file__).resolve().parent.parent
repository = DocumentRepository(Path(os.getenv("DOCS_DIR", BASE_DIR / "docs")))
search_service = SearchService(repository)
app = FastAPI(title="MCP Document Search API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
                   allow_credentials=False, allow_methods=["GET"], allow_headers=["*"])


@app.get("/api/search")
def search(query: str, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=50)):
    try:
        return search_service.search(query, page, page_size).model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/documents")
def list_documents():
    return {"documents": [repository.relative_name(path) for path in repository.get_documents()]}
