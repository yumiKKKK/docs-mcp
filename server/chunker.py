from dataclasses import dataclass
from .extractor import ExtractedPage


@dataclass
class DocumentChunk:
    chunk_index: int
    page_number: int
    location: str
    content: str


class DocumentChunker:
    """추출된 문서 페이지를 청크로 분할하는 클래스"""

    def __init__(
            self,
            chunk_size: int = 1000,
            overlap: int = 150
    ):
        """
        청크 크기와 청크 간 중복 길이를 초기화

        Args:
            chunk_size: 각 청크의 최대 문자 수
            overlap: 이전 청크와 다음 청크 사이의 중복 문자 수
        """

        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")

        if overlap < 0 or overlap >= chunk_size:
            raise ValueError(
                "overlap must be >= 0 and < chunk_size"
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(
            self,
            pages: list[ExtractedPage]
    ) -> list[DocumentChunk]:
        """
        페이지별로 분할하며,
        청크 사이에 overlap을 적용하여 문맥이 끊기는 것을 최소화

        Args:
            pages: 텍스트가 추출된 문서 페이지 목록

        Returns:
            페이지 정보와 텍스트 내용을 포함한 DocumentChunk 목록
        """

        results = []
        chunk_index = 0

        for page in pages:

            content = page.content.strip()

            if not content:
                continue

            start = 0

            while start < len(content):

                end = min(
                    start + self.chunk_size,
                    len(content)
                )

                text = content[start:end].strip()

                if text:
                    results.append(
                        DocumentChunk(
                            chunk_index=chunk_index,
                            page_number=page.page_number,
                            location=page.location,
                            content=text
                        )
                    )

                    chunk_index += 1

                if end >= len(content):
                    break

                start = end - self.overlap

        return results
