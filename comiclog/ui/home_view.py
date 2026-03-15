from __future__ import annotations

import flet as ft

from comiclog.services.stats_service import StatsService


class HomeView(ft.Column):
    """Home 탭: 앱 소개와 최근 활동 요약을 보여주는 화면."""

    def __init__(self, stats_service: StatsService) -> None:
        """통계 서비스를 주입받아 홈 화면을 초기화합니다."""
        super().__init__(expand=True, spacing=12, scroll=ft.ScrollMode.ADAPTIVE)
        self._stats_service = stats_service

        self._intro_card = ft.Card(
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text("ComicLog", size=28, weight=ft.FontWeight.BOLD),
                        ft.Text("읽은 만화를 기록하고 감상 메모/명장면을 아카이빙하세요."),
                    ],
                ),
            )
        )

        self._activity_card = ft.Card(content=ft.Container(padding=16))

        self.controls = [
            self._intro_card,
            ft.Text("최근 활동", size=20, weight=ft.FontWeight.W_600),
            self._activity_card,
        ]

        self.reload()

    def reload(self) -> None:
        """요약 통계를 다시 읽어 홈 화면 활동 영역을 갱신합니다."""
        summary = self._stats_service.get_summary()
        self._activity_card.content = ft.Container(
            padding=16,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(f"총 읽은 화: {summary['total_read_episodes']}"),
                    ft.Text(f"메모 수: {summary['memo_count']}"),
                    ft.Text(f"작품 수: {len(summary['records_by_work'])}"),
                ],
            ),
        )
