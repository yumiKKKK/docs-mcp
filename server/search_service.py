from pathlib import Path
from .document_repository import DocumentRepository
from .query_processor import process_query
from .ranking import score_terms, sort_results
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
        results: list[dict] = []
        if processed.terms:
            for path in self.repository.get_documents():
                try:
                    content = self.repository.read_document(path)
                except (OSError, UnicodeError, RuntimeError, ValueError):
                    continue
                score, matched, _ = score_terms(content, processed.terms)
                if not matched:
                    continue
                normalized = content.casefold()
                first_position = min(normalized.find(term) for term in matched)
                start = max(0, first_position - self.snippet_before)
                end = min(len(content), first_position + self.snippet_after)
                snippet = content[start:end].strip()
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet += "..."
                results.append({"filename": self.repository.relative_name(path), "score": score,
                                "matched_terms": matched, "snippet": snippet})
        results = sort_results(results)
        total = len(results)
        total_pages = (total + page_size - 1) // page_size
        start_index = (page - 1) * page_size
        page_results = results[start_index:start_index + page_size] if page <= total_pages else []
        return SearchResponse(query=processed.original_query, total=total, page=page, page_size=page_size,
                              total_pages=total_pages, has_next=page < total_pages,
                              has_previous=page > 1 and total > 0,
                              results=[SearchResult(**item) for item in page_results])
