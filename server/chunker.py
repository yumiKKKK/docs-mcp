
from dataclasses import dataclass

from .extractor import ExtractedPage


@dataclass(slots=True)
class DocumentChunk:
    chunk_index: int
    page_number: int
    location: str
    content: str


class DocumentChunker:
    """추출된 문서 페이지를 효율적으로 청크 분할하는 클래스"""

    def __init__(
            self,
            chunk_size: int = 1000,
            overlap: int = 150
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")

        if overlap < 0 or overlap >= chunk_size:
            raise ValueError(
                "overlap must be >= 0 and < chunk_size"
            )

        self.chunk_size = chunk_size
        self.overlap = overlap
        self.step = chunk_size - overlap

    def split(
            self,
            pages: list[ExtractedPage]
    ) -> list[DocumentChunk]:
        """
        페이지별 텍스트를 overlap을 적용하여 청크로 분할한다.
        """

        results = []
        chunk_index = 0

        chunk_size = self.chunk_size
        step = self.step

        for page in pages:
            content = page.content.strip()

            if not content:
                continue

            content_length = len(content)

            start = 0

            while start < content_length:
                end = min(start + chunk_size, content_length)

                # 필요한 경우에만 청크 문자열 생성
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

                if end == content_length:
                    break

                start += step

        return results
