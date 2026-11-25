
from pathlib import Path

from .document_repository import DocumentRepository
from .query_processor import process_query
from .ranking import (
    score_terms,
    iter_occurrence_positions,
    select_page,
)
from .snippet import create_snippet
from .schemas import SearchResponse, SearchResult
from .indexer import DocumentIndexer

class SearchService:
    """문서 검색 및 검색 결과 응답을 담당하는 서비스"""

    def __init__(
            self,
            repository: DocumentRepository,
            indexer: DocumentIndexer,
            snippet_before: int = 100,
            snippet_after: int = 500,
    ):
        self.repository = repository
        self.indexer = indexer
        self.snippet_before = snippet_before
        self.snippet_after = snippet_after

    def search(
            self,
            query: str,
            page: int = 1,
            page_size: int = 10,
    ) -> SearchResponse:

        self._validate_pagination(query, page, page_size)

        processed = process_query(query)

        candidates = self._collect_candidates(
            processed.terms
        )

        total = len(candidates)

        start = (page - 1) * page_size

        page_candidates = select_page(
            candidates,
            start,
            page_size,
        )

        results = self._build_results(page_candidates)

        total_pages = (total + page_size - 1) // page_size

        return SearchResponse(
            query=processed.original_query,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1 and total > 0,
            results=results,
        )

    def _validate_pagination(
            self,
            query: str,
            page: int,
            page_size: int,
    ) -> None:

        if not isinstance(query, str):
            raise ValueError("query must be a string")

        if isinstance(page, bool) or not isinstance(page, int) or page < 1:
            raise ValueError(
                "page must be an integer greater than or equal to 1"
            )

        if (
                isinstance(page_size, bool)
                or not isinstance(page_size, int)
                or not 1 <= page_size <= 50
        ):
            raise ValueError(
                "page_size must be an integer between 1 and 50"
            )

    def _collect_candidates(
            self,
            terms: list[str],
    ) -> list[dict]:

        if not terms:
            return []

        chunks = self.indexer.search(
            query=" ".join(terms),
            limit=10000,
        )

        candidates = []

        for chunk in chunks:
            content = chunk["content"]

            score, matched, _ = score_terms(content, terms)

            if not matched:
                continue

            filename = self._get_filename(chunk)

            for occurrence in iter_occurrence_positions(
                    content,
                    matched,
            ):
                candidates.append({
                    "filename": filename,
                    "score": score,
                    "matched_terms": occurrence["matched_terms"],
                    "_position": (
                        chunk["chunk_index"],
                        occurrence["position"],
                    ),
                    "_snippet_data": (
                        content,
                        occurrence["position"],
                        occurrence["end"],
                    ),
                })

        return candidates

    def _get_filename(self, chunk: dict) -> str:

        path = chunk.get("path")

        if path is None:
            raise ValueError(
                "Indexer candidate must contain the original document path"
            )

        document_path = Path(path)

        if not document_path.is_absolute():
            document_path = self.repository.docs_dir / document_path

        return self.repository.relative_name(document_path)

    def _build_results(
            self,
            candidates: list[dict],
    ) -> list[SearchResult]:

        results = []

        for item in candidates:
            content, position, end_position = item["_snippet_data"]

            snippet = create_snippet(
                content,
                position,
                end_position,
                self.snippet_before,
                self.snippet_after,
            )

            results.append(
                SearchResult(
                    filename=item["filename"],
                    score=item["score"],
                    matched_terms=item["matched_terms"],
                    snippet=snippet,
                )
            )

        return results
