
import pytest

from server.document_repository import DocumentRepository


@pytest.mark.parametrize(
    "file_size",
    [
        1024,
        100 * 1024,
        1024 * 1024,
        10 * 1024 * 1024,
        ]
)
def test_get_document_info(
        benchmark,
        tmp_path,
        file_size
):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    path = docs_dir / "sample.txt"

    path.write_bytes(b"A" * file_size)

    repository = DocumentRepository(docs_dir)

    result = benchmark(
        repository.get_document_info,
        path
    )

    assert result.size == file_size
    assert len(result.sha256) == 64
