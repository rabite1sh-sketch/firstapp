from __future__ import annotations

from typing import Any

from comiclog.db.database import DEFAULT_DB_PATH, connect_db


class MemoService:
    """에피소드 감상 메모 CRUD를 제공하는 서비스 클래스."""

    _HIGHLIGHT_MARKER = "__HIGHLIGHT__"

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        """서비스에서 사용할 SQLite DB 경로를 설정합니다."""
        self._db_path = db_path

    def add_memo(self, episode_id: int, content: str, rating: int | None = None, is_highlight: bool = False) -> int:
        """새 감상 메모를 생성하고 생성된 메모 ID를 반환합니다.

        Args:
            episode_id: 메모가 속한 에피소드 ID
            content: 감상 메모 본문
            rating: 감상 점수(선택)
            is_highlight: 명장면 여부
        """
        with connect_db(self._db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO memos (episode_id, memo_text, favorite_scene, rating)
                VALUES (?, ?, ?, ?)
                """,
                (
                    episode_id,
                    content,
                    self._HIGHLIGHT_MARKER if is_highlight else None,
                    rating,
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def get_memos_by_episode(self, episode_id: int) -> list[dict[str, Any]]:
        """특정 에피소드의 메모 목록을 조회합니다."""
        with connect_db(self._db_path) as conn:
            rows = conn.execute(
                """
                SELECT id, episode_id, memo_text, rating, favorite_scene, created_at
                FROM memos
                WHERE episode_id = ?
                ORDER BY id DESC
                """,
                (episode_id,),
            ).fetchall()

        return [
            {
                "id": row["id"],
                "episode_id": row["episode_id"],
                "content": row["memo_text"],
                "rating": row["rating"],
                "is_highlight": row["favorite_scene"] == self._HIGHLIGHT_MARKER,
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def update_memo(
        self,
        memo_id: int,
        *,
        content: str,
        rating: int | None = None,
        is_highlight: bool = False,
    ) -> bool:
        """메모 내용을 수정하고 성공 여부를 반환합니다."""
        with connect_db(self._db_path) as conn:
            cursor = conn.execute(
                """
                UPDATE memos
                SET memo_text = ?,
                    rating = ?,
                    favorite_scene = ?,
                    updated_at = datetime('now')
                WHERE id = ?
                """,
                (
                    content,
                    rating,
                    self._HIGHLIGHT_MARKER if is_highlight else None,
                    memo_id,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_memo(self, memo_id: int) -> bool:
        """메모를 삭제하고 성공 여부를 반환합니다."""
        with connect_db(self._db_path) as conn:
            cursor = conn.execute("DELETE FROM memos WHERE id = ?", (memo_id,))
            conn.commit()
            return cursor.rowcount > 0
