
import pytest

from server.extractor import DocumentExtractor

# TO-DO : TXT 이외 확장자 테스트 추가

@pytest.mark.parametrize(
    "file_size",
    [
        1024,
        100 * 1024,
        1024 * 1024,
        10 * 1024 * 1024,
        ]
)
def test_extract_text(
        benchmark,
        tmp_path,
        file_size
):
    path = tmp_path / "sample.txt"

    content = (
            "Python search engine document indexing. "
            * (file_size // 45 + 1)
    )[:file_size]

    path.write_text(content, encoding="utf-8")

    extractor = DocumentExtractor()

    result = benchmark(
        extractor.extract,
        path
    )

    assert len(result) == 1
    assert result[0].content == content
