import sqlite3
from pathlib import Path

from .document_repository import DocumentRepository
from .extractor import DocumentExtractor
from .chunker import DocumentChunker


class DocumentIndexer:
    """
    문서 추출, 청킹 및 검색 인덱싱 관리하는 클래스

    tables:
    1. documents — 원본 문서 정보
    2. chunks — 분할된 문서 내용
    3. chunks_fts — 전문 검색을 위한 FTS5 가상 테이블

    검색 시 chunks_fts에서 검색하고 chunks, documents를 JOIN하여 원본 문서 정보 반환
    """

    def __init__(
            self,
            repository: DocumentRepository,
            extractor: DocumentExtractor,
            chunker: DocumentChunker,
            db_path: Path
    ):
        """인덱서 초기화 및 데이터베이스 생성"""

        self.repository = repository
        self.extractor = extractor
        self.chunker = chunker
        self.db_path = db_path

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._initialize()

    def _connect(self):
        """SQLite 데이터베이스 연결"""

        connection = sqlite3.connect(
            str(self.db_path),
            timeout=30
        )

        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 30000")

        return connection

    def _initialize(self):
        """문서, 청크 및 전문 검색 테이블 초기화"""

        with self._connect() as conn:
            conn.execute("""
                         CREATE TABLE IF NOT EXISTS documents
                         (
                             id          INTEGER PRIMARY KEY AUTOINCREMENT,
                             path        TEXT    NOT NULL UNIQUE,
                             extension   TEXT    NOT NULL,
                             file_size   INTEGER NOT NULL,
                             modified_at REAL    NOT NULL,
                             sha256      TEXT    NOT NULL,
                             indexed_at  TEXT DEFAULT CURRENT_TIMESTAMP
                         )
                         """)

            conn.execute("""
                         CREATE TABLE IF NOT EXISTS chunks
                         (
                             id          INTEGER PRIMARY KEY AUTOINCREMENT,
                             document_id INTEGER NOT NULL,
                             chunk_index INTEGER NOT NULL,
                             page_number INTEGER NOT NULL,
                             location    TEXT,
                             content     TEXT    NOT NULL,

                             FOREIGN KEY (document_id)
                                 REFERENCES documents (id)
                                 ON DELETE CASCADE
                         )
                         """)

            conn.execute("""
                        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
                        USING fts5(
                            content,
                            filename,
                            path,
                            location,
                            tokenize='unicode61'
                        )
            """)

            conn.execute("""
                         CREATE INDEX IF NOT EXISTS
                             idx_chunks_document
                             ON chunks (document_id)
                         """)

    def index_document(self, path: Path) -> bool:
        """
        문서가 신규이거나 변경된 경우에만 인덱싱
        변경이 없으면 False를 반환
        """

        info = self.repository.get_document_info(path)

        with self._connect() as conn:

            existing = conn.execute(
                """
                SELECT id, sha256
                FROM documents
                WHERE path = ?
                """,
                (info.relative_path,)
            ).fetchone()

            if existing and existing[1] == info.sha256:
                return False

            # 파일 추출 및 청킹
            pages = self.extractor.extract(info.path)

            chunks = self.chunker.split(pages)

            # 기존 문서 삭제
            if existing:

                document_id = existing[0]

                old_chunks = conn.execute(
                    """
                    SELECT id
                    FROM chunks
                    WHERE document_id = ?
                    """,
                    (document_id,)
                ).fetchall()

                for (chunk_id,) in old_chunks:
                    conn.execute(
                        """
                        DELETE
                        FROM chunks_fts
                        WHERE rowid = ?
                        """,
                        (chunk_id,)
                    )

                conn.execute(
                    "DELETE FROM chunks WHERE document_id = ?",
                    (document_id,)
                )

                conn.execute(
                    "DELETE FROM documents WHERE id = ?",
                    (document_id,)
                )

            cursor = conn.execute(
                """
                INSERT INTO documents (path,
                                       extension,
                                       file_size,
                                       modified_at,
                                       sha256)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    info.relative_path,
                    info.extension,
                    info.size,
                    info.modified_at,
                    info.sha256
                )
            )

            document_id = cursor.lastrowid

            for chunk in chunks:
                cursor = conn.execute(
                    """
                    INSERT INTO chunks (document_id,
                                        chunk_index,
                                        page_number,
                                        location,
                                        content)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        document_id,
                        chunk.chunk_index,
                        chunk.page_number,
                        chunk.location,
                        chunk.content
                    )
                )

                chunk_id = cursor.lastrowid

                conn.execute(
                    """
                    INSERT INTO chunks_fts (rowid,
                                            content,
                                            filename,
                                            path,
                                            location)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        chunk_id,
                        chunk.content,
                        info.path.name,
                        info.relative_path,
                        chunk.location
                    )
                )

        return True

    def sync(self) -> dict:
        """docs 디렉터리와 인덱스의 상태를 동기화"""

        documents = self.repository.get_documents()

        current_paths = {
            self.repository.relative_name(path)
            for path in documents
        }

        stats = {
            "total": len(documents),
            "indexed": 0,
            "unchanged": 0,
            "deleted": 0,
            "failed": []
        }

        for path in documents:

            try:

                changed = self.index_document(path)

                if changed:
                    stats["indexed"] += 1
                else:
                    stats["unchanged"] += 1

            except Exception as exc:

                stats["failed"].append({
                    "filename": path.name,
                    "error": str(exc)
                })

        # 삭제된 문서 정리
        with self._connect() as conn:

            rows = conn.execute(
                "SELECT id, path FROM documents"
            ).fetchall()

            for document_id, path in rows:

                if path not in current_paths:

                    chunk_ids = conn.execute(
                        """
                        SELECT id
                        FROM chunks
                        WHERE document_id = ?
                        """,
                        (document_id,)
                    ).fetchall()

                    for (chunk_id,) in chunk_ids:
                        conn.execute(
                            """
                            DELETE
                            FROM chunks_fts
                            WHERE rowid = ?
                            """,
                            (chunk_id,)
                        )

                    conn.execute(
                        "DELETE FROM documents WHERE id = ?",
                        (document_id,)
                    )

                    stats["deleted"] += 1

        return stats

    def search(
            self,
            query: str,
            limit: int = 5
    ) -> list[dict]:
        """전문 검색 기반 관련 문서 청크 조회"""

        if not query or not query.strip():
            return []

        if limit < 1:
            raise ValueError("limit must be positive")

        # 사용자 검색어를 FTS5 구문으로 변환
        terms = query.split()

        fts_query = " OR ".join(
            '"' + term.replace('"', '""') + '"'
            for term in terms
            if term.strip()
        )

        if not fts_query:
            return []

        with self._connect() as conn:

            rows = conn.execute(
                """
                SELECT d.path,
                       d.extension,
                       c.chunk_index,
                       c.page_number,
                       c.location,
                       c.content,
                       bm25(
                               chunks_fts,
                               1.0,
                               5.0,
                               2.0,
                               1.0
                       ) AS relevance

                FROM chunks_fts

                         JOIN chunks c
                              ON c.id = chunks_fts.rowid

                         JOIN documents d
                              ON d.id = c.document_id

                WHERE chunks_fts MATCH ?

                ORDER BY relevance ASC

                LIMIT ?
                """,
                (fts_query, limit)
            ).fetchall()

        results = [
            {
                "filename": Path(row[0]).name,
                "path": row[0],
                "extension": row[1],
                "chunk_index": row[2],
                "page": row[3],
                "location": row[4],
                "content": row[5],
                "score": round(-row[6], 6)
            }
            for row in rows
        ]
        return results

    def get_statistics(self) -> dict:
        """문서, 청크 및 확장자별 인덱싱 통계 조회"""

        with self._connect() as conn:
            document_count = conn.execute(
                "SELECT COUNT(*) FROM documents"
            ).fetchone()[0]

            chunk_count = conn.execute(
                "SELECT COUNT(*) FROM chunks"
            ).fetchone()[0]

            extension_counts = conn.execute(
                """
                SELECT extension, COUNT(*)
                FROM documents
                GROUP BY extension
                """
            ).fetchall()

        return {
            "documents": document_count,
            "chunks": chunk_count,
            "extensions": dict(extension_counts)
        }
