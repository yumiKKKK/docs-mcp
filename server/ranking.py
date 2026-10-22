
from collections.abc import Iterable


def score_terms(content: str, terms: Iterable[str]) -> tuple[int, list[str], dict[str, int]]:
    normalized = content.casefold()
    counts = {term: normalized.count(term.casefold()) for term in terms}
    matched = [term for term, count in counts.items() if count > 0]
    return sum(counts.values()), matched, counts


def find_occurrences(content: str, terms: Iterable[str], snippet_before: int = 100, snippet_after: int = 500) -> list[dict]:
    normalized_chars = []
    index_map = []

    # casefold된 각 문자와 원본 문자열의 인덱스를 연결
    for original_index, char in enumerate(content):
        folded = char.casefold()
        normalized_chars.extend(folded)
        index_map.extend([original_index] * len(folded))

    normalized = "".join(normalized_chars)
    occurrences = {}

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

            # 겹치는 검색 결과도 찾음
            position += 1

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
    return sorted(
        results,
        key=lambda item: (
            -item["score"],
            item["filename"],
            item.get("_position", 0),
        ),
    )
