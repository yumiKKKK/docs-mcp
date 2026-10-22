
import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessedQuery:
    original_query: str
    terms: tuple[str, ...]
    expanded_terms: tuple[str, ...]


def process_query(query: str) -> ProcessedQuery:
    original = unicodedata.normalize("NFC", query).strip()
    terms = tuple(dict.fromkeys(
        re.findall(r"[가-힣]+|[a-zA-Z0-9_]+", original.casefold())
    ))

    return ProcessedQuery(
        original_query=original,
        terms=terms,
        expanded_terms=(),
    )
