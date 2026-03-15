from __future__ import annotations

import flet as ft

from comiclog.db.database import DEFAULT_DB_PATH, connect_db
from comiclog.services.work_service import WorkService


class WorkDetailView(ft.Column):
    """작품 상세 정보를 보여주는 모바일 스타일 뷰."""

    def __init__(
        self,
        page: ft.Page,
        work_id: int,
        work_service: WorkService,
        db_path: str | None = None,
    ) -> None:
        """작품 ID 기준으로 상세 화면을 초기화합니다."""
        super().__init__(expand=True, spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
        self._page = page
        self._work_id = work_id
        self._work_service = work_service
        self._db_path = db_path or getattr(work_service, "_db_path", DEFAULT_DB_PATH)

        self._work = self._work_service.get_work_by_id(work_id)
        self._episodes = self._load_episodes()
        self._memos = self._load_memos()

        self.controls = self._build_layout()

    def _build_layout(self) -> list[ft.Control]:
        """모바일 카드 중심 레이아웃을 구성합니다."""
        if not self._work:
            return [
                ft.Container(
                    padding=16,
                    border_radius=16,
                    bgcolor=ft.Colors.RED_50,
                    content=ft.Column(
                        controls=[
                            ft.Text("작품을 찾을 수 없습니다.", size=18, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton("목록으로", on_click=lambda _: self._page.go("/works")),
                        ]
                    ),
                )
            ]

        return [
            ft.Container(
                padding=12,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.ElevatedButton("← 목록", on_click=lambda _: self._page.go("/works")),
                        ft.Text("작품 상세", size=20, weight=ft.FontWeight.BOLD),
                    ],
                ),
            ),
            self._build_work_info_card(),
            self._build_read_link_button(),
            self._build_episodes_section(),
            self._build_memos_section(),
            ft.Container(
                padding=ft.padding.only(top=6, bottom=16),
                content=ft.ElevatedButton(
                    "메모 작성",
                    on_click=lambda _: self._page.go(f"/works/{self._work_id}/memos/new"),
                    width=220,
                ),
                alignment=ft.alignment.center,
            ),
        ]

    def _build_work_info_card(self) -> ft.Control:
        """작품 기본 정보 카드를 생성합니다."""
        assert self._work is not None
        return ft.Card(
            content=ft.Container(
                padding=16,
                border_radius=20,
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text(self._work["title"], size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(f"작가: {self._work.get('author') or '-'}", size=14),
                        ft.Text(
                            f"설명: {self._work.get('description') or '-'}",
                            size=13,
                            color=ft.Colors.BLUE_GREY_700,
                        ),
                    ],
                ),
            )
        )

    def _build_read_link_button(self) -> ft.Control:
        """읽기 링크 버튼을 렌더링합니다."""
        url = self._extract_read_link(self._work.get("description") if self._work else None)
        return ft.Container(
            alignment=ft.alignment.center_left,
            content=ft.ElevatedButton(
                "읽기 링크 열기",
                on_click=lambda _: self._open_read_link(url),
                disabled=not bool(url),
            ),
            padding=ft.padding.only(left=6, right=6),
        )

    def _build_episodes_section(self) -> ft.Control:
        """읽은 화 목록 섹션을 구성합니다."""
        items: list[ft.Control] = [
            ft.Text("읽은 화 목록", size=18, weight=ft.FontWeight.W_600)
        ]
        if not self._episodes:
            items.append(ft.Text("아직 기록된 화가 없습니다."))
        else:
            for ep in self._episodes:
                items.append(
                    ft.Card(
                        content=ft.Container(
                            padding=12,
                            content=ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(f"{ep['episode_no']}화 - {ep.get('episode_title') or '제목 없음'}"),
                                    ft.Text(
                                        f"읽은 날짜: {ep.get('read_at') or '-'}",
                                        size=12,
                                        color=ft.Colors.BLUE_GREY_600,
                                    ),
                                ],
                            ),
                        )
                    )
                )

        return ft.Container(
            padding=12,
            border_radius=18,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            content=ft.Column(controls=items, spacing=8),
        )

    def _build_memos_section(self) -> ft.Control:
        """메모 목록 섹션을 구성합니다."""
        items: list[ft.Control] = [
            ft.Text("메모 목록", size=18, weight=ft.FontWeight.W_600)
        ]
        if not self._memos:
            items.append(ft.Text("작성된 메모가 없습니다."))
        else:
            for memo in self._memos:
                items.append(
                    ft.Card(
                        content=ft.Container(
                            padding=12,
                            content=ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(memo["memo_text"]),
                                    ft.Text(f"명장면: {memo.get('favorite_scene') or '-'}", size=12),
                                    ft.Text(
                                        f"작성일: {memo.get('created_at') or '-'}",
                                        size=12,
                                        color=ft.Colors.BLUE_GREY_600,
                                    ),
                                ],
                            ),
                        )
                    )
                )

        return ft.Container(
            padding=12,
            border_radius=18,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            content=ft.Column(controls=items, spacing=8),
        )

    def _load_episodes(self) -> list[dict]:
        """작품에 연결된 읽은 화 목록을 조회합니다."""
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
        """작품에 연결된 메모 목록을 조회합니다."""
        with connect_db(self._db_path) as conn:
            rows = conn.execute(
                """
                SELECT m.id, m.memo_text, m.favorite_scene, m.created_at
                FROM memos m
                JOIN episodes e ON e.id = m.episode_id
                WHERE e.work_id = ?
                ORDER BY m.id DESC
                """,
                (self._work_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def _open_read_link(self, url: str | None) -> None:
        """읽기 링크를 외부 브라우저로 엽니다."""
        if not url:
            self._page.snack_bar = ft.SnackBar(ft.Text("등록된 읽기 링크가 없습니다."))
            self._page.snack_bar.open = True
            self._page.update()
            return
        self._page.launch_url(url)

    @staticmethod
    def _extract_read_link(description: str | None) -> str | None:
        """description 필드에서 '읽기 링크:' 접두어 값을 파싱합니다."""
        if not description:
            return None
        for line in description.splitlines():
            if line.startswith("읽기 링크:"):
                value = line.replace("읽기 링크:", "", 1).strip()
                return value or None
        return None
