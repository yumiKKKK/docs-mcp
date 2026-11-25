
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass(slots=True)
class ExtractedPage:
    page_number: int
    content: str
    location: str = ""


class DocumentExtractor:
    """다양한 문서 형식에서 메모리 효율적으로 텍스트를 추출하는 클래스"""

    def extract(self, path: Path) -> list[ExtractedPage]:
        return list(self.iter_extract(path))

    def iter_extract(
            self,
            path: Path
    ) -> Iterator[ExtractedPage]:
        """
        페이지 단위로 추출 결과를 반환하는 Generator.
        """
        extension = path.suffix.lower()

        extractors = {
            ".txt": self._extract_text,
            ".md": self._extract_text,
            ".pdf": self._extract_pdf,
            ".pptx": self._extract_pptx,
            ".docx": self._extract_docx,
            ".xlsx": self._extract_xlsx,
        }

        extractor = extractors.get(extension)

        if extractor is None:
            raise ValueError(
                f"Unsupported extension: {extension}"
            )

        yield from extractor(path)

    @staticmethod
    def _extract_text(
            path: Path
    ) -> Iterator[ExtractedPage]:
        """TXT 및 Markdown 파일 추출"""

        # 텍스트 파일은 기존의 단일 페이지 구조 유지
        with path.open(
                "r",
                encoding="utf-8-sig",
                errors="replace"
        ) as file:
            content = file.read()

        if content:
            yield ExtractedPage(
                page_number=1,
                content=content,
                location="document"
            )

    @staticmethod
    def _extract_pdf(
            path: Path
    ) -> Iterator[ExtractedPage]:
        """PDF 페이지별 텍스트 추출"""

        import pymupdf

        with pymupdf.open(path) as pdf:

            for index, page in enumerate(pdf, start=1):

                content = page.get_text("text").strip()

                if content:
                    yield ExtractedPage(
                        page_number=index,
                        content=content,
                        location=f"page:{index}"
                    )

    @staticmethod
    def _extract_pptx(
            path: Path
    ) -> Iterator[ExtractedPage]:
        """PowerPoint 슬라이드별 텍스트 추출"""

        from pptx import Presentation

        presentation = Presentation(str(path))

        for slide_number, slide in enumerate(
                presentation.slides,
                start=1
        ):
            contents = []

            for shape in slide.shapes:

                if shape.has_text_frame:
                    text = shape.text.strip()

                    if text:
                        contents.append(text)

                if shape.has_table:
                    for row in shape.table.rows:
                        cells = (
                            cell.text.strip()
                            for cell in row.cells
                        )

                        row_text = " | ".join(cells)

                        if row_text:
                            contents.append(row_text)

            if contents:
                yield ExtractedPage(
                    page_number=slide_number,
                    content="\n".join(contents),
                    location=f"slide:{slide_number}"
                )

    @staticmethod
    def _extract_docx(
            path: Path
    ) -> Iterator[ExtractedPage]:
        """Word 문서 텍스트 추출"""

        from docx import Document

        document = Document(str(path))

        contents = []

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                contents.append(text)

        for table in document.tables:
            for row in table.rows:
                cells = (
                    cell.text.strip()
                    for cell in row.cells
                )

                row_text = " | ".join(cells)

                if row_text:
                    contents.append(row_text)

        if contents:
            yield ExtractedPage(
                page_number=1,
                content="\n".join(contents),
                location="document"
            )

    @staticmethod
    def _extract_xlsx(
            path: Path
    ) -> Iterator[ExtractedPage]:
        """Excel 시트별 텍스트 추출"""

        from openpyxl import load_workbook
        from openpyxl.utils import get_column_letter

        workbook = load_workbook(
            filename=path,
            read_only=True,
            data_only=True
        )

        try:
            for sheet in workbook.worksheets:

                rows = []

                for row_index, row in enumerate(
                        sheet.iter_rows(values_only=True),
                        start=1
                ):
                    values = []

                    for column_index, value in enumerate(
                            row,
                            start=1
                    ):
                        if value is not None:
                            coordinate = (
                                f"{get_column_letter(column_index)}"
                                f"{row_index}"
                            )

                            values.append(
                                f"{coordinate}: {value}"
                            )

                    if values:
                        rows.append(" | ".join(values))

                if rows:
                    yield ExtractedPage(
                        page_number=1,
                        content="\n".join(rows),
                        location=f"sheet:{sheet.title}"
                    )

        finally:
            workbook.close()
