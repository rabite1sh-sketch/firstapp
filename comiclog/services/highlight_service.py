from __future__ import annotations

from collections import defaultdict
from typing import Any

from comiclog.db.database import DEFAULT_DB_PATH, connect_db


class HighlightService:
    """명장면(하이라이트) 메모 조회 기능을 제공하는 서비스 클래스."""

    _HIGHLIGHT_MARKER = "__HIGHLIGHT__"

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        """서비스에서 사용할 SQLite DB 경로를 설정합니다."""
        self._db_path = db_path

    def get_highlights(self) -> list[dict[str, Any]]:
        """명장면 메모 목록을 조회합니다.

        Notes:
            요구사항의 `memos.is_highlight = 1` 조건을 만족하도록,
            현재 스키마에서는 아래 값을 모두 명장면으로 간주합니다.
            - `favorite_scene = '__HIGHLIGHT__'` (현재 서비스 저장 방식)
            - `favorite_scene = '1'` 또는 `favorite_scene = 1` (호환 처리)
        """
        with connect_db(self._db_path) as conn:
            rows = conn.execute(
                """
                SELECT
                    m.id AS memo_id,
                    m.memo_text AS content,
                    m.favorite_scene,
                    m.rating,
                    m.created_at,
                    e.id AS episode_id,
                    e.episode_no,
                    e.episode_title,
                    w.id AS work_id,
                    w.title AS work_title
                FROM memos m
                JOIN episodes e ON e.id = m.episode_id
                JOIN works w ON w.id = e.work_id
                WHERE m.favorite_scene = ?
                   OR m.favorite_scene = '1'
                   OR m.favorite_scene = 1
                ORDER BY w.title ASC, m.id DESC
                """,
                (self._HIGHLIGHT_MARKER,),
            ).fetchall()

        return [
            {
                "memo_id": row["memo_id"],
                "content": row["content"],
                "rating": row["rating"],
                "created_at": row["created_at"],
                "episode_id": row["episode_id"],
                "episode_no": row["episode_no"],
                "episode_title": row["episode_title"],
                "work_id": row["work_id"],
                "work_title": row["work_title"],
                "is_highlight": True,
            }
            for row in rows
        ]

    def get_highlights_grouped_by_work(self) -> dict[str, list[dict[str, Any]]]:
        """명장면 목록을 작품 단위로 그룹화해 반환합니다."""
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in self.get_highlights():
            grouped[item["work_title"]].append(item)
        return dict(grouped)
