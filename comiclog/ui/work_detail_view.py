from __future__ import annotations

from datetime import date

import flet as ft

from comiclog.db.database import DEFAULT_DB_PATH, connect_db
from comiclog.services.memo_service import MemoService
from comiclog.services.work_service import WorkService


class WorkDetailView(ft.Column):
    """작품 상세 화면: 작품 정보, 읽은 화 기록, 메모 작성/조회 기능 제공."""

    def __init__(
        self,
        page: ft.Page,
        work_id: int,
        work_service: WorkService,
        db_path: str | None = None,
    ) -> None:
        super().__init__(expand=True, spacing=12, scroll=ft.ScrollMode.ADAPTIVE)
        self._page = page
        self._work_id = work_id
        self._work_service = work_service
        self._db_path = db_path or getattr(work_service, "_db_path", DEFAULT_DB_PATH)
        self._memo_service = MemoService(self._db_path)

        self._work = self._work_service.get_work_by_id(work_id)

        self._episode_no = ft.TextField(label="읽은 화 번호", hint_text="예: 12")
        self._episode_title = ft.TextField(label="화 제목")
        self._episode_read_at = ft.TextField(label="읽은 날짜", value=str(date.today()))

        self._memo_episode = ft.Dropdown(label="메모 대상 화")
        self._memo_content = ft.TextField(label="감상 메모", multiline=True, min_lines=2, max_lines=4)
        self._memo_rating = ft.TextField(label="평점(1~5)")
        self._memo_highlight = ft.Checkbox(label="명장면으로 저장")

        self._episodes_list = ft.ListView(expand=False, spacing=8)
        self._memos_list = ft.ListView(expand=False, spacing=8)

        self.controls = self._build_layout()
        self._refresh_data()

    def _build_layout(self) -> list[ft.Control]:
        if not self._work:
            return [
                ft.Text("작품을 찾을 수 없습니다.", size=18, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("목록으로", on_click=lambda _: self._page.go("/works")),
            ]

        return [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.ElevatedButton("← 목록", on_click=lambda _: self._page.go("/works")),
                    ft.Text("작품 상세", size=22, weight=ft.FontWeight.BOLD),
                ],
            ),
            ft.Card(
                content=ft.Container(
                    padding=14,
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(self._work["title"], size=22, weight=ft.FontWeight.BOLD),
                            ft.Text(f"작가: {self._work.get('author') or '-'}"),
                            ft.Text(f"설명: {self._work.get('description') or '-'}"),
                        ],
                    ),
                )
            ),
            ft.Card(
                content=ft.Container(
                    padding=14,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text("읽은 화 기록", size=18, weight=ft.FontWeight.W_600),
                            self._episode_no,
                            self._episode_title,
                            self._episode_read_at,
                            ft.ElevatedButton("읽은 화 추가", on_click=self._on_add_episode),
                        ],
                    ),
                )
            ),
            ft.Card(
                content=ft.Container(
                    padding=14,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text("메모 작성", size=18, weight=ft.FontWeight.W_600),
                            self._memo_episode,
                            self._memo_content,
                            self._memo_rating,
                            self._memo_highlight,
                            ft.ElevatedButton("메모 저장", on_click=self._on_add_memo),
                        ],
                    ),
                )
            ),
            ft.Text("읽은 화 목록", size=18, weight=ft.FontWeight.W_600),
            self._episodes_list,
            ft.Text("메모 목록", size=18, weight=ft.FontWeight.W_600),
            self._memos_list,
        ]

    def _on_add_episode(self, _: ft.ControlEvent) -> None:
        """읽은 화를 DB에 저장합니다."""
        episode_no = (self._episode_no.value or "").strip()
        if not episode_no:
            return

        with connect_db(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO episodes (work_id, episode_no, episode_title, read_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    self._work_id,
                    episode_no,
                    (self._episode_title.value or "").strip() or None,
                    (self._episode_read_at.value or "").strip() or None,
                ),
            )
            conn.commit()

        self._episode_no.value = ""
        self._episode_title.value = ""
        self._episode_read_at.value = str(date.today())

        self._refresh_data()
        self._page.update()

    def _on_add_memo(self, _: ft.ControlEvent) -> None:
        """선택한 에피소드에 메모를 저장합니다."""
        if not self._memo_episode.value:
            return
        content = (self._memo_content.value or "").strip()
        if not content:
            return

        rating_value = (self._memo_rating.value or "").strip()
        rating = int(rating_value) if rating_value.isdigit() else None

        self._memo_service.add_memo(
            episode_id=int(self._memo_episode.value),
            content=content,
            rating=rating,
            is_highlight=bool(self._memo_highlight.value),
        )

        self._memo_content.value = ""
        self._memo_rating.value = ""
        self._memo_highlight.value = False

        self._refresh_data()
        self._page.update()

    def _refresh_data(self) -> None:
        """에피소드/메모 목록과 메모 대상 Dropdown을 재구성합니다."""
        episodes = self._load_episodes()
        memos = self._load_memos()

        self._memo_episode.options = [
            ft.dropdown.Option(str(ep["id"]), f"{ep['episode_no']}화 - {ep.get('episode_title') or '제목 없음'}")
            for ep in episodes
        ]
        if episodes and not self._memo_episode.value:
            self._memo_episode.value = str(episodes[0]["id"])

        if not episodes:
            self._episodes_list.controls = [ft.Text("아직 기록된 화가 없습니다.")]
        else:
            self._episodes_list.controls = [
                ft.Card(
                    content=ft.Container(
                        padding=10,
                        content=ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text(f"{ep['episode_no']}화 - {ep.get('episode_title') or '제목 없음'}"),
                                ft.Text(f"읽은 날짜: {ep.get('read_at') or '-'}", size=12),
                            ],
                        ),
                    )
                )
                for ep in episodes
            ]

        if not memos:
            self._memos_list.controls = [ft.Text("작성된 메모가 없습니다.")]
        else:
            self._memos_list.controls = [
                ft.Card(
                    content=ft.Container(
                        padding=10,
                        content=ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text(memo["memo_text"]),
                                ft.Text(f"평점: {memo.get('rating') if memo.get('rating') is not None else '-'}", size=12),
                                ft.Text(
                                    f"명장면: {'예' if memo.get('favorite_scene') else '아니오'} / 작성일: {memo.get('created_at') or '-'}",
                                    size=12,
                                ),
                            ],
                        ),
                    )
                )
                for memo in memos
            ]

    def _load_episodes(self) -> list[dict]:
        with connect_db(self._db_path) as conn:
            rows = conn.execute(
                """
                SELECT id, episode_no, episode_title, read_at
                FROM episodes
                WHERE work_id = ?
                ORDER BY id DESC
                """,
                (self._work_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def _load_memos(self) -> list[dict]:
        with connect_db(self._db_path) as conn:
            rows = conn.execute(
                """
                SELECT m.id, m.memo_text, m.favorite_scene, m.rating, m.created_at
                FROM memos m
                JOIN episodes e ON e.id = m.episode_id
                WHERE e.work_id = ?
                ORDER BY m.id DESC
                """,
                (self._work_id,),
            ).fetchall()
        return [dict(row) for row in rows]
