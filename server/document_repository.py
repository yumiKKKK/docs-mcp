from pathlib import Path
from typing import List
import hashlib
from dataclasses import dataclass

SUPPORTED_EXTENSIONS = {
    ".md", ".txt", ".pdf",
    ".pptx", ".docx", ".xlsx"
}


@dataclass
class DocumentInfo:
    path: Path
    relative_path: str
    extension: str
    size: int
    modified_at: float
    sha256: str


class DocumentRepository:
    """문서 디렉터리의 파일 탐색 및 문서 정보 관리를 담당하는 클래스"""

    def __init__(
            self,
            docs_dir: Path,
            supported_extensions: set[str] | None = None,
    ):
        """
        문서 저장 디렉터리와 지원하는 파일 확장자를 초기화

        Args:
            docs_dir: 문서 파일이 저장된 기본 디렉터리
            supported_extensions: 탐색할 파일 확장자 목록
        """

        self.docs_dir = Path(docs_dir).resolve()

        self.supported_extensions = (
            SUPPORTED_EXTENSIONS
            if supported_extensions is None
            else supported_extensions
        )

    def get_documents(self) -> List[Path]:
        """
        문서 디렉터리와 하위 디렉터리에서 지원하는 파일을 탐색

        Returns:
            지원하는 확장자를 가진 문서 파일 경로 목록
        """

        self.docs_dir.mkdir(parents=True, exist_ok=True)

        documents = []

        for path in self.docs_dir.rglob("*"):
            if not path.is_file():
                continue

            try:
                resolved = path.resolve(strict=True)
                resolved.relative_to(self.docs_dir)
            except (ValueError, OSError):
                continue

            if resolved.suffix.lower() in self.supported_extensions:
                documents.append(resolved)

        return sorted(
            documents,
            key=lambda p: p.relative_to(self.docs_dir).as_posix()
        )

    def get_document_info(self, path: Path) -> DocumentInfo:
        """
        문서 파일의 메타데이터와 SHA-256 해시 정보를 조회

        Args:
            path: 정보를 조회할 문서 파일 경로

        Returns:
            문서 경로, 확장자, 크기, 수정 시간 및 해시 정보

        Raises:
            ValueError: 문서 경로가 저장 디렉터리 외부에 있는 경우
        """

        resolved = path.resolve(strict=True)

        try:
            resolved.relative_to(self.docs_dir)
        except ValueError:
            raise ValueError(
                "Document path is outside docs directory"
            )

        stat = resolved.stat()

        return DocumentInfo(
            path=resolved,
            relative_path=self.relative_name(resolved),
            extension=resolved.suffix.lower(),
            size=stat.st_size,
            modified_at=stat.st_mtime,
            sha256=self.calculate_hash(resolved)
        )

    @staticmethod
    def calculate_hash(path: Path) -> str:
        """
        파일의 SHA-256 해시값을 계산

        Args:
            path: 해시를 계산할 파일 경로

        Returns:
            파일의 SHA-256 해시 문자열
        """

        sha256 = hashlib.sha256()

        with path.open("rb") as file:
            for block in iter(
                    lambda: file.read(1024 * 1024),
                    b""
            ):
                sha256.update(block)

        return sha256.hexdigest()

    def relative_name(self, path: Path) -> str:
        """
        문서 경로를 저장 디렉터리 기준 상대 경로로 변환

        Args:
            path: 상대 경로로 변환할 문서 파일 경로

        Returns:
            POSIX 형식의 상대 경로

        Raises:
            ValueError: 문서 경로가 저장 디렉터리 외부에 있는 경우
        """

        resolved = path.resolve()

        try:
            return resolved.relative_to(
                self.docs_dir.resolve()
            ).as_posix()
        except ValueError:
            raise ValueError(
                "Document path is outside docs directory"
            )
