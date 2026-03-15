from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ComicEntry:
    id: int | None
    title: str
    episode: str
    memo: str
    favorite_scene: str
    read_date: str

    @classmethod
    def from_row(cls, row: tuple[int, str, str, str, str, str]) -> "ComicEntry":
        return cls(
            id=row[0],
            title=row[1],
            episode=row[2],
            memo=row[3],
            favorite_scene=row[4],
            read_date=row[5],
        )
