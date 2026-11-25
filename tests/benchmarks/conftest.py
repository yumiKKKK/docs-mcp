
from pathlib import Path

import pytest

from server.document_repository import DocumentRepository
from server.extractor import DocumentExtractor
from server.chunker import DocumentChunker
from server.indexer import DocumentIndexer


@pytest.fixture
def sample_text():
    return (
        "Python document search engine indexing. "
        "Search performance optimization. "
    ) * 100


@pytest.fixture
def sample_pages(sample_text):
    from server.extractor import ExtractedPage

    return [
        ExtractedPage(
            page_number=1,
            content=sample_text,
            location="document"
        )
    ]


@pytest.fixture
def benchmark_components(tmp_path):
    docs_dir = tmp_path / "docs"
    db_path = tmp_path / "storage" / "benchmark.db"

    docs_dir.mkdir(parents=True)

    repository = DocumentRepository(docs_dir)
    extractor = DocumentExtractor()
    chunker = DocumentChunker(
        chunk_size=1000,
        overlap=150
    )

    indexer = DocumentIndexer(
        repository=repository,
        extractor=extractor,
        chunker=chunker,
        db_path=db_path
    )

    return {
        "docs_dir": docs_dir,
        "db_path": db_path,
        "repository": repository,
        "extractor": extractor,
        "chunker": chunker,
        "indexer": indexer,
    }


@pytest.fixture
def create_text_files():
    def factory(directory: Path, count: int, size=1000):
        directory.mkdir(parents=True, exist_ok=True)

        content = (
            "Python search engine document indexing. "
        )
        content = (
                content * (size // len(content) + 1)
        )[:size]

        for i in range(count):
            path = directory / f"document_{i}.txt"
            path.write_text(content, encoding="utf-8")

        return directory

    return factory
