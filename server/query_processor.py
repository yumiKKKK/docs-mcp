
import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessedQuery:
    original_query: str
    terms: tuple[str, ...]
    expanded_terms: tuple[str, ...]


def process_query(query: str) -> ProcessedQuery:

    # 유니코드 정규화 및 공백 제거
    original = unicodedata.normalize("NFC", query).strip()

    # 검색어 추출 및 중복 제거
    terms = tuple(dict.fromkeys(
        re.findall(r"[가-힣]+|[a-zA-Z0-9_]+", original.casefold())
    ))

    return ProcessedQuery(
        original_query=original,
        terms=terms,
        expanded_terms=(),
    )
