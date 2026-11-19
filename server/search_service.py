
from pathlib import Path

from .document_repository import DocumentRepository
from .query_processor import process_query
from .ranking import score_terms, find_occurrences, sort_results
from .schemas import SearchResponse, SearchResult
from .indexer import DocumentIndexer


class SearchService:
    """문서 검색, 결과 정렬 및 페이지네이션을 담당하는 서비스 클래스"""

    def __init__(
            self,
            repository: DocumentRepository,
            indexer: DocumentIndexer,
            snippet_before: int = 100,
            snippet_after: int = 500,
    ):
        self.repository = repository
        self.indexer = indexer

        # 검색 결과의 앞뒤 문맥 범위 설정
        self.snippet_before = snippet_before
        self.snippet_after = snippet_after

    def search(
            self,
            query: str,
            page: int = 1,
            page_size: int = 10
    ) -> SearchResponse:
        """검색어 처리, 문서 검색, 결과 정렬 및 페이지네이션을 수행하는 메서드"""

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

        # 검색어 정규화 및 검색어 추출
        processed = process_query(query)

        results = []

        # 검색 수행
        if processed.terms:

            # 검색 인덱스를 통한 후보 문서 청크 조회
            candidates = self.indexer.search(
                query=" ".join(processed.terms),
                limit=10000
            )

            for chunk in candidates:

                content = chunk["content"]

                # 검색어별 등장 횟수 및 매칭 결과 계산
                score, matched, _ = score_terms(
                    content,
                    processed.terms
                )

                if not matched:
                    continue

                # 검색어 등장 위치 및 주변 문맥 추출
                occurrences = find_occurrences(
                    content,
                    matched,
                    self.snippet_before,
                    self.snippet_after
                )

                # 검색 결과의 원본 문서 경로 추출
                if isinstance(chunk, dict):
                    path = chunk.get("path")
                else:
                    path = getattr(chunk, "path", None)

                if path is None:
                    raise ValueError(
                        "Indexer candidate must contain the original document path"
                    )

                document_path = Path(path)

                if not document_path.is_absolute():
                    document_path = self.repository.docs_dir / document_path

                filename = self.repository.relative_name(document_path)

                # 검색어 등장 위치별 결과 생성
                for occurrence in occurrences:
                    results.append({
                        "filename": filename,
                        "score": score,
                        "matched_terms": occurrence["matched_terms"],
                        "snippet": occurrence["snippet"],
                        "_position": (
                            chunk["chunk_index"],
                            occurrence["position"]
                        ),
                    })

        # 검색 점수 및 문서 위치 기준 결과 정렬
        results = sort_results(results)

        # 전체 검색 결과 수 및 전체 페이지 수 계산
        total = len(results)
        total_pages = (total + page_size - 1) // page_size

        # 페이지 시작 인덱스 계산
        start = (page - 1) * page_size

        # 요청 페이지에 해당하는 검색 결과 추출
        page_results = (
            results[start:start + page_size]
            if page <= total_pages
            else []
        )

        response_results = [
            SearchResult(
                filename=item["filename"],
                score=item["score"],
                matched_terms=item["matched_terms"],
                snippet=item["snippet"]
            )
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
