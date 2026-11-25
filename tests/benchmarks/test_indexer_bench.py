
import pytest

from server.document_repository import DocumentRepository
from server.extractor import DocumentExtractor
from server.chunker import DocumentChunker
from server.indexer import DocumentIndexer


def make_indexer(root):
    docs = root / "docs"
    docs.mkdir(parents=True, exist_ok=True)

    repository = DocumentRepository(docs)
    extractor = DocumentExtractor()
    chunker = DocumentChunker()

    indexer = DocumentIndexer(
        repository=repository,
        extractor=extractor,
        chunker=chunker,
        db_path=root / "storage" / "test.db"
    )

    return docs, indexer


def test_index_document(benchmark, tmp_path):
    counter = iter(range(100000))
    state = {}

    def setup():
        root = tmp_path / str(next(counter))
        docs, indexer = make_indexer(root)

        path = docs / "sample.txt"
        path.write_text(
            "Python search engine indexing. " * 100,
            encoding="utf-8"
        )

        state["indexer"] = indexer
        state["path"] = path

    def run_index():
        return state["indexer"].index_document(
            state["path"]
        )

    benchmark.pedantic(
        run_index,
        setup=setup,
        iterations=1,
        rounds=10
    )

@pytest.mark.parametrize(
    "document_count",
    [100, 1000, 5000]
)
def test_sync(benchmark, tmp_path, document_count):
    counter = iter(range(100000))
    state = {}

    def setup():
        root = tmp_path / str(next(counter))
        docs, indexer = make_indexer(root)

        for i in range(document_count):
            path = docs / f"doc_{i}.txt"
            path.write_text(
                "Python search engine indexing. " * 30,
                encoding="utf-8"
            )

        state["indexer"] = indexer

    def run_sync():
        return state["indexer"].sync()

    benchmark.pedantic(
        run_sync,
        setup=setup,
        iterations=1,
        rounds=5
    )