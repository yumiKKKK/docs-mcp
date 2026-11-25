
import pytest

from server.search_service import SearchService


@pytest.mark.parametrize(
    "document_count",
    [100, 1000, 5000]
)
def test_search_service(
        benchmark,
        benchmark_components,
        create_text_files,
        document_count
):
    components = benchmark_components

    create_text_files(
        components["docs_dir"],
        document_count,
        size=1000
    )

    indexer = components["indexer"]

    # 검색 대상 문서 사전 인덱싱
    stats = indexer.sync()

    assert stats["indexed"] == document_count
    assert not stats["failed"]

    service = SearchService(
        repository=components["repository"],
        indexer=indexer
    )

    result = benchmark(
        service.search,
        "Python search",
        1,
        10
    )

    assert result.total >= 0
