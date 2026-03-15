from __future__ import annotations

from typing import Any

from comiclog.db.database import DEFAULT_DB_PATH, connect_db


class WorkService:
    """`works` 테이블에 대한 CRUD 기능을 제공하는 서비스 클래스."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        """서비스에서 사용할 SQLite DB 경로를 설정합니다."""
        self._db_path = db_path

    def add_work(self, title: str, author: str | None = None, description: str | None = None) -> int:
        """새 작품을 등록하고 생성된 작품 ID를 반환합니다."""
        with connect_db(self._db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO works (title, author, description)
                VALUES (?, ?, ?)
                """,
                (title, author, description),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def get_works(self) -> list[dict[str, Any]]:
        """등록된 모든 작품 목록을 최신 수정 순으로 조회합니다."""
        with connect_db(self._db_path) as conn:
            rows = conn.execute(
                """
                SELECT id, title, author, description, created_at, updated_at
                FROM works
                ORDER BY updated_at DESC, id DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_work_by_id(self, work_id: int) -> dict[str, Any] | None:
        """작품 ID로 단건 작품 정보를 조회하고, 없으면 `None`을 반환합니다."""
        with connect_db(self._db_path) as conn:
            row = conn.execute(
                """
                SELECT id, title, author, description, created_at, updated_at
                FROM works
                WHERE id = ?
                """,
                (work_id,),
            ).fetchone()
        return dict(row) if row else None

    def update_work(
        self,
        work_id: int,
        *,
        title: str,
        author: str | None = None,
        description: str | None = None,
    ) -> bool:
        """작품 정보를 수정하고, 수정 성공 여부(`True/False`)를 반환합니다."""
        with connect_db(self._db_path) as conn:
            cursor = conn.execute(
                """
                UPDATE works
                SET title = ?,
                    author = ?,
                    description = ?,
                    updated_at = datetime('now')
                WHERE id = ?
                """,
                (title, author, description, work_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_work(self, work_id: int) -> bool:
        """작품을 삭제하고, 삭제 성공 여부(`True/False`)를 반환합니다."""
        with connect_db(self._db_path) as conn:
            cursor = conn.execute("DELETE FROM works WHERE id = ?", (work_id,))
            conn.commit()
            return cursor.rowcount > 0
