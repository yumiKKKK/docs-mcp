from collections.abc import Iterable


def score_terms(content: str, terms: Iterable[str]) -> tuple[int, list[str], dict[str, int]]:
    normalized = content.casefold()
    counts = {term: normalized.count(term) for term in terms}
    matched = [term for term, count in counts.items() if count > 0]
    return sum(counts.values()), matched, counts


def sort_results(results: list[dict]) -> list[dict]:
    return sorted(results, key=lambda item: (-item["score"], item["filename"]))
