
from collections.abc import Iterable


def score_terms(content: str, terms: Iterable[str]) -> tuple[int, list[str], dict[str, int]]:
    """총 등장 횟수, 매칭 검색어, 검색어별 등장 횟수 반환"""

    # 대소문자 구분 없는 검색을 위한 정규화
    normalized = content.casefold()

    # 검색어별 등장 횟수 계산
    counts = {term: normalized.count(term.casefold()) for term in terms}

    # # 검색어별 등장 횟수 계산
    # counts = {}
    # for term in terms:
    #     # 검색어 미리 정규화
    #     normalized_term = term.casefold()
    #     counts[term] = normalized.count(normalized_term)

    # 실제 매칭된 검색어 추출
    matched = [term for term, count in counts.items() if count > 0]

    return sum(counts.values()), matched, counts


def find_occurrences(content: str, terms: Iterable[str], snippet_before: int = 100, snippet_after: int = 500) -> list[dict]:
    normalized_chars = []
    index_map = []

    for original_index, char in enumerate(content):
        folded = char.casefold()
        normalized_chars.extend(folded)
        index_map.extend([original_index] * len(folded))

    normalized = "".join(normalized_chars)
    occurrences = {}

    # 검색어별 등장 위치 탐색
    for term in terms:
        folded_term = term.casefold()
        if not folded_term:
            continue

        position = 0
        while True:
            position = normalized.find(folded_term, position)
            if position == -1:
                break

            end_position = position + len(folded_term)
            original_start = index_map[position]
            original_end = index_map[end_position - 1] + 1

            # 같은 원본 위치에 여러 검색어가 매칭되면 하나로 합침
            item = occurrences.setdefault(original_start, {
                "position": original_start,
                "end": original_end,
                "matched_terms": [],
            })
            item["end"] = max(item["end"], original_end)
            if term not in item["matched_terms"]:
                item["matched_terms"].append(term)

            position += 1

    # 검색 위치를 기준으로 앞뒤 문맥 추출
    results = []
    for item in occurrences.values():
        start = max(0, item["position"] - snippet_before)
        end = min(len(content), item["end"] + snippet_after)
        snippet = content[start:end].strip()
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet += "..."

        results.append({
            "position": item["position"],
            "matched_terms": item["matched_terms"],
            "snippet": snippet,
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
