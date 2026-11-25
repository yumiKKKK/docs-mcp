
import pytest

from server.chunker import DocumentChunker
from server.extractor import ExtractedPage


@pytest.mark.parametrize(
    "text_size",
    [10000, 100000, 1000000]
)
def test_chunker(
        benchmark,
        text_size
):
    content = (
            "Python search engine document indexing. "
            * (text_size // 45 + 1)
    )[:text_size]

    pages = [
        ExtractedPage(
            page_number=1,
            content=content,
            location="document"
        )
    ]

    chunker = DocumentChunker(
        chunk_size=1000,
        overlap=150
    )

    result = benchmark(
        chunker.split,
        pages
    )

    assert len(result) > 0


@pytest.mark.parametrize(
    "chunk_size",
    [256, 512, 1000, 2000]
)
def test_chunker_size(
        benchmark,
        chunk_size
):
    content = "Python search engine " * 10000

    pages = [
        ExtractedPage(
            page_number=1,
            content=content,
            location="document"
        )
    ]

    chunker = DocumentChunker(
        chunk_size=chunk_size,
        overlap=150
    )

    result = benchmark(
        chunker.split,
        pages
    )

    assert len(result) > 0
