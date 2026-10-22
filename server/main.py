import os
from typing import Any
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from .document_repository import DocumentRepository
from .search_service import SearchService

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = Path(os.getenv("DOCS_DIR", BASE_DIR / "docs")).resolve()
repository = DocumentRepository(DOCS_DIR)
search_service = SearchService(repository)
mcp = FastMCP("document-search")


@mcp.tool()
def list_documents() -> list[str]:
    return [repository.relative_name(path) for path in repository.get_documents()]


@mcp.tool()
def search_documents(query: str, page: int = 1, page_size: int = 10) -> dict[str, Any]:
    return search_service.search(query, page, page_size).model_dump()


if __name__ == "__main__":
    mcp.run(transport="stdio")
