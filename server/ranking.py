
from typing import Iterable
import heapq

from .text_search import _iter_matches
from .snippet import create_snippet

def score_terms(
        content: str,
        terms: Iterable[str],
) -> tuple[int, list[str], dict[str, int]]:
    """총 등장 횟수, 매칭 검색어, 검색어별 등장 횟수 반환"""

    normalized = content.casefold()

    counts = {}
    normalized_counts = {}

    for term in terms:
        if term in counts:
            continue

        normalized_term = term.casefold()

        if normalized_term not in normalized_counts:
            normalized_counts[normalized_term] = (
                normalized.count(normalized_term)
            )

        counts[term] = normalized_counts[normalized_term]

    matched = [
        term for term, count in counts.items()
        if count > 0
    ]

    return sum(counts.values()), matched, counts


def iter_occurrence_positions(
        content: str,
        terms: Iterable[str],
):
    """검색어의 등장 위치와 매칭 정보를 생성한다."""
    if not content:
        return

    terms = list(dict.fromkeys(term for term in terms if term))
    if not terms:
        return

    term_order = {term: i for i, term in enumerate(terms)}
    occurrences = {}

    for start, end, term in _iter_matches(content, terms):
        item = occurrences.get(start)

        if item is None:
            item = {
                "position": start,
                "end": end,
                "matched_terms": [term],
            }
            occurrences[start] = item

        else:
            if end > item["end"]:
                item["end"] = end

            if term not in item["matched_terms"]:
                item["matched_terms"].append(term)

    for item in sorted(occurrences.values(), key=lambda x: x["position"]):
        item["matched_terms"].sort(key=term_order.__getitem__)
        yield item

def find_occurrences(
        content: str,
        terms: Iterable[str],
        snippet_before: int = 100,
        snippet_after: int = 500,
) -> list[dict]:

    if not content or snippet_before < 0 or snippet_after < 0:
        return []

    results = []

    for item in iter_occurrence_positions(content, terms):
        results.append({
            "position": item["position"],
            "matched_terms": item["matched_terms"],
            "snippet": create_snippet(
                content,
                item["position"],
                item["end"],
                snippet_before,
                snippet_after,
            ),
        })

    return results

def sort_results(results: list[dict]) -> list[dict]:
    # 점수 내림차순, 파일명 및 위치 오름차순 정렬
    return sorted(
        results,
        key=lambda item: (
            -item["score"],
            item["filename"],
            item.get("_position", 0),
        ),
    )

def select_page(
        results: list[dict],
        start: int,
        page_size: int,
) -> list[dict]:
    """전체 정렬 없이 필요한 페이지의 결과만 선택한다."""

    if start < 0 or page_size < 1:
        raise ValueError("Invalid pagination parameters")

    end = start + page_size

    return heapq.nsmallest(
        end,
        results,
        key=lambda item: (
            -item["score"],
            item["filename"],
            item.get("_position", 0),
        ),
    )[start:]