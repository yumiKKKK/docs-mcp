import os
from typing import Any
from pathlib import Path
from mcp.server.fastmcp import FastMCP
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
mcp = FastMCP("document-search")

# 전체 문서 목록
@mcp.tool()
def list_documents() -> list[str]:
    return [repository.relative_name(path) for path in repository.get_documents()]

# 문서 검색
@mcp.tool()
def search_documents(query: str, page: int = 1, page_size: int = 10) -> dict[str, Any]:
    return search_service.search(query, page, page_size).model_dump()

if __name__ == "__main__":
    mcp.run(transport="stdio")
