from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessedQuery:
    original_query: str
    terms: tuple[str, ...]
    expanded_terms: tuple[str, ...]


def process_query(query: str) -> ProcessedQuery:
    """Normalize a query. """
    original = query.strip()
    terms = tuple(dict.fromkeys(original.casefold().split()))
    return ProcessedQuery(original_query=original, terms=terms, expanded_terms=())
