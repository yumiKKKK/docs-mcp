from dataclasses import dataclass
from pathlib import Path

@dataclass
class ExtractedPage:
    page_number: int
    content: str
    location: str = ""

class DocumentExtractor:
    """다양한 문서 형식에서 텍스트를 추출하는 클래스"""

    def extract(self, path: Path) -> list[ExtractedPage]:
        """
        파일 확장자에 따라 적절한 추출 메서드를 실행

        Args:
            path: 텍스트를 추출할 문서 파일 경로

        Returns:
            추출된 페이지별 텍스트 목록

        Raises:
            ValueError: 지원하지 않는 파일 형식인 경우
        """

        extension = path.suffix.lower()

        extractors = {
            ".txt": self._extract_text,
            ".md": self._extract_text,
            ".pdf": self._extract_pdf,
            ".pptx": self._extract_pptx,
            ".docx": self._extract_docx,
            ".xlsx": self._extract_xlsx
        }

        extractor = extractors.get(extension)

        if extractor is None:
            raise ValueError(
                f"Unsupported extension: {extension}"
            )

        return extractor(path)

    @staticmethod
    def _extract_text(path: Path) -> list[ExtractedPage]:
        """TXT 및 Markdown 파일에서 텍스트를 추출"""

        content = path.read_text(
            encoding="utf-8-sig",
            errors="replace"
        )

        return [
            ExtractedPage(
                page_number=1,
                content=content,
                location="document"
            )
        ]

    @staticmethod
    def _extract_pdf(path: Path) -> list[ExtractedPage]:
        """PDF 파일에서 페이지별 텍스트를 추출"""

        import pymupdf

        results = []

        with pymupdf.open(path) as pdf:

            for index, page in enumerate(pdf, start=1):

                content = page.get_text("text").strip()

                if content:
                    results.append(
                        ExtractedPage(
                            page_number=index,
                            content=content,
                            location=f"page:{index}"
                        )
                    )

        return results

    @staticmethod
    def _extract_pptx(path: Path) -> list[ExtractedPage]:
        """PowerPoint 파일에서 슬라이드별 텍스트를 추출"""

        from pptx import Presentation

        presentation = Presentation(str(path))
        results = []

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

                        cells = [
                            cell.text.strip()
                            for cell in row.cells
                        ]

                        if any(cells):
                            contents.append(" | ".join(cells))

            if contents:
                results.append(
                    ExtractedPage(
                        page_number=slide_number,
                        content="\n".join(contents),
                        location=f"slide:{slide_number}"
                    )
                )

        return results

    @staticmethod
    def _extract_docx(path: Path) -> list[ExtractedPage]:
        """Word 파일에서 문서 텍스트를 추출"""

        from docx import Document

        document = Document(str(path))
        contents = []

        for paragraph in document.paragraphs:

            text = paragraph.text.strip()

            if text:
                contents.append(text)

        for table in document.tables:

            for row in table.rows:

                cells = [
                    cell.text.strip()
                    for cell in row.cells
                ]

                if any(cells):
                    contents.append(" | ".join(cells))

        return [
            ExtractedPage(
                page_number=1,
                content="\n".join(contents),
                location="document"
            )
        ]

    @staticmethod
    def _extract_xlsx(path: Path) -> list[ExtractedPage]:
        """Excel 파일에서 시트별 텍스트를 추출"""
        from openpyxl import load_workbook

        workbook = load_workbook(
            filename=path,
            read_only=True,
            data_only=True
        )

        results = []

        try:
            for sheet in workbook.worksheets:

                rows = []

                for row_index, row in enumerate(
                        sheet.iter_rows(),
                        start=1
                ):

                    values = []

                    for cell in row:

                        if cell.value is not None:
                            values.append(
                                f"{cell.coordinate}: {cell.value}"
                            )

                    if values:
                        rows.append(
                            " | ".join(values)
                        )

                if rows:
                    results.append(
                        ExtractedPage(
                            page_number=1,
                            content="\n".join(rows),
                            location=f"sheet:{sheet.title}"
                        )
                    )

        finally:
            workbook.close()

        return results