
from .document_repository import DocumentRepository
from .query_processor import process_query
from .ranking import score_terms, find_occurrences, sort_results
from .schemas import SearchResponse, SearchResult


class SearchService:
    def __init__(self, repository: DocumentRepository, snippet_before: int = 100, snippet_after: int = 500):
        self.repository = repository
        self.snippet_before = snippet_before
        self.snippet_after = snippet_after

    def search(self, query: str, page: int = 1, page_size: int = 10) -> SearchResponse:
        if not isinstance(query, str):
            raise ValueError("query must be a string")
        if isinstance(page, bool) or not isinstance(page, int) or page < 1:
            raise ValueError("page must be an integer greater than or equal to 1")
        if isinstance(page_size, bool) or not isinstance(page_size, int) or not 1 <= page_size <= 50:
            raise ValueError("page_size must be an integer between 1 and 50")

        processed = process_query(query)
        results = []

        for path in self.repository.get_documents() if processed.terms else []:
            try:
                content = self.repository.read_document(path)
            except (OSError, UnicodeError, RuntimeError, ValueError):
                continue

            score, matched, _ = score_terms(content, processed.terms)
            if not matched:
                continue

            occurrences = find_occurrences(content, matched, self.snippet_before, self.snippet_after)
            for occurrence in occurrences:
                results.append({
                    "filename": self.repository.relative_name(path),
                    "score": score,
                    "matched_terms": occurrence["matched_terms"],
                    "snippet": occurrence["snippet"],
                    "_position": occurrence["position"],
                })

        results = sort_results(results)
        total = len(results)
        total_pages = (total + page_size - 1) // page_size
        start = (page - 1) * page_size
        page_results = results[start:start + page_size] if page <= total_pages else []

        response_results = [
            SearchResult(filename=item["filename"], score=item["score"], matched_terms=item["matched_terms"], snippet=item["snippet"])
            for item in page_results
        ]

        return SearchResponse(
            query=processed.original_query,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1 and total > 0,
            results=response_results,
        )
