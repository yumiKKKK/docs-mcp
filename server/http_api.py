import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .document_repository import DocumentRepository
from .search_service import SearchService
from .extractor import DocumentExtractor
from .chunker import DocumentChunker
from .indexer import DocumentIndexer

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = Path(os.getenv("DOCS_DIR", BASE_DIR / "docs")).resolve()
DB_PATH = BASE_DIR / "storage" / "document.db"

DOCS_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

repository = DocumentRepository(DOCS_DIR)
extractor = DocumentExtractor()

chunker = DocumentChunker(
    chunk_size=1000,
    overlap=150
)

indexer = DocumentIndexer(
    repository=repository,
    extractor=extractor,
    chunker=chunker,
    db_path=DB_PATH
)

search_service = SearchService(repository, indexer)


@asynccontextmanager
async def lifespan(app: FastAPI):
    stats = indexer.sync()
    yield


app = FastAPI(
    title="MCP Document Search API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173"
    ).split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)


@app.get("/api/search")
def search(
        query: str,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=50)
):
    try:
        result = search_service.search(
            query=query,
            page=page,
            page_size=page_size
        )

        return result.model_dump()

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        ) from exc


@app.get("/api/documents")
def list_documents():
    return {
        "documents": [
            repository.relative_name(path)
            for path in repository.get_documents()
        ]
    }


@app.post("/api/index/sync")
def sync_documents():
    return indexer.sync()


@app.get("/api/index/statistics")
def get_index_statistics():
    return indexer.get_statistics()
