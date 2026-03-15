from __future__ import annotations

import flet as ft

from comiclog.services.highlight_service import HighlightService


class HighlightView(ft.Column):
    """명장면 아카이브 화면(작품별 그룹 + 카드 UI)."""

    def __init__(self, page: ft.Page, highlight_service: HighlightService) -> None:
        """페이지와 서비스 객체를 주입받아 명장면 목록 화면을 초기화합니다."""
        super().__init__(expand=True, spacing=12)
        self._page = page
        self._highlight_service = highlight_service

        self._list = ft.ListView(expand=True, spacing=10)

        self.controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("명장면 아카이브", size=24, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("새로고침", on_click=self._on_refresh),
                ],
            ),
            self._list,
        ]

        self.reload()

    def _on_refresh(self, _: ft.ControlEvent) -> None:
        """새로고침 버튼 이벤트: 데이터를 다시 조회합니다."""
        self.reload()

    def reload(self) -> None:
        """서비스에서 명장면 데이터를 가져와 카드 형태로 렌더링합니다."""
        grouped = self._highlight_service.get_highlights_grouped_by_work()

        if not grouped:
            self._list.controls = [
                ft.Card(
                    content=ft.Container(
                        padding=14,
                        content=ft.Text("아직 등록된 명장면이 없습니다."),
                    )
                )
            ]
            self.update()
            return

        cards: list[ft.Control] = []
        for work_title, highlights in grouped.items():
            # 작품별 섹션 카드
            section_items: list[ft.Control] = [
                ft.Text(work_title, size=18, weight=ft.FontWeight.W_600)
            ]

            for item in highlights:
                section_items.append(
                    ft.Card(
                        content=ft.Container(
                            padding=12,
                            content=ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(
                                        f"{item['episode_no']}화 - {item.get('episode_title') or '제목 없음'}",
                                        size=13,
                                        color=ft.Colors.BLUE_GREY_700,
                                    ),
                                    ft.Text(item["content"], size=15),
                                    ft.Text(
                                        f"평점: {item['rating'] if item['rating'] is not None else '-'} / 작성일: {item['created_at'] or '-'}",
                                        size=12,
                                        color=ft.Colors.BLUE_GREY_500,
                                    ),
                                ],
                            ),
                        )
                    )
                )

            cards.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        border_radius=18,
                        content=ft.Column(controls=section_items, spacing=8),
                    )
                )
            )

        self._list.controls = cards
        self.update()
