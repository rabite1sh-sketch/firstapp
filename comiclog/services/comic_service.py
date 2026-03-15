from __future__ import annotations

from comiclog.models.comic_entry import ComicEntry
from comiclog.services.db import Database


class ComicService:
    def __init__(self, database: Database) -> None:
        self._database = database

    def add_entry(
        self,
        *,
        title: str,
        episode: str,
        memo: str,
        favorite_scene: str,
        read_date: str,
    ) -> int:
        with self._database.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO comic_entries (title, episode, memo, favorite_scene, read_date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, episode, memo, favorite_scene, read_date),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def list_entries(self) -> list[ComicEntry]:
        with self._database.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, title, episode, memo, favorite_scene, read_date
                FROM comic_entries
                ORDER BY id DESC
                """
            ).fetchall()
        return [
            ComicEntry.from_row(
                (
                    row["id"],
                    row["title"],
                    row["episode"],
                    row["memo"],
                    row["favorite_scene"],
                    row["read_date"],
                )
            )
            for row in rows
        ]
