from __future__ import annotations

import sqlite3
from pathlib import Path

# 기본 DB 파일 위치: 프로젝트 요구사항의 `comiclog/database/` 폴더를 사용합니다.
DEFAULT_DB_PATH = "comiclog/database/comiclog.db"


def connect_db(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """SQLite DB 연결을 생성하고 Foreign Key 제약을 활성화합니다."""
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    """ComicLog 핵심 테이블(works, episodes, memos, tags, memo_tags)을 생성합니다."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS works (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            description TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_id INTEGER NOT NULL,
            episode_no TEXT NOT NULL,
            episode_title TEXT,
            read_at TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE,
            UNIQUE (work_id, episode_no)
        );

        CREATE TABLE IF NOT EXISTS memos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            episode_id INTEGER NOT NULL,
            memo_text TEXT NOT NULL,
            favorite_scene TEXT,
            rating INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS memo_tags (
            memo_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (memo_id, tag_id),
            FOREIGN KEY (memo_id) REFERENCES memos(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_episodes_work_id ON episodes(work_id);
        CREATE INDEX IF NOT EXISTS idx_memos_episode_id ON memos(episode_id);
        CREATE INDEX IF NOT EXISTS idx_memo_tags_tag_id ON memo_tags(tag_id);
        """
    )


def initialize_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """DB 연결 + 테이블 생성 + 커밋까지 한 번에 수행합니다."""
    with connect_db(db_path) as conn:
        create_tables(conn)
        conn.commit()


class Database:
    """기존 코드와의 호환을 위한 래퍼 클래스.

    - `connect()`는 DB 연결을 반환합니다.
    - `initialize()`는 초기화 함수를 호출합니다.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self._db_path = db_path

    def connect(self) -> sqlite3.Connection:
        return connect_db(self._db_path)

    def initialize(self) -> None:
        initialize_db(self._db_path)
