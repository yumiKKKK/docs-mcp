
import pytest

from server.ranking import (
    score_terms,
    find_occurrences,
    sort_results,
)


@pytest.mark.parametrize(
    "term_count",
    [10, 100, 1000]
)
def test_score_terms(benchmark, term_count):
    content = (
            "Python search engine document indexing "
            * 100
    )

    terms = [
        f"term_{i % 100}"
        for i in range(term_count)
    ]

    result = benchmark(
        score_terms,
        content,
        terms
    )

    assert len(result) == 3


@pytest.mark.parametrize(
    "text_size",
    [1000, 10000, 100000]
)
def test_find_occurrences(benchmark, text_size):
    content = (
            "Python search engine document indexing "
            * (text_size // 45 + 1)
    )[:text_size]

    terms = ["python", "search", "document"]

    result = benchmark(
        find_occurrences,
        content,
        terms,
        100,
        500
    )

    assert isinstance(result, list)


def test_sort_results(benchmark):
    results = [
        {
            "score": i % 100,
            "filename": f"document_{i}.txt",
            "_position": (i, 0),
        }
        for i in range(10000)
    ]

    result = benchmark(sort_results, results)

    assert len(result) == 10000
