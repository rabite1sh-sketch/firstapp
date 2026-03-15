from __future__ import annotations

import flet as ft

from comiclog.services.stats_service import StatsService


class StatsView(ft.Column):
    """ComicLog 통계 화면(UI)."""

    def __init__(self, page: ft.Page, stats_service: StatsService) -> None:
        """페이지와 통계 서비스를 주입받아 화면을 초기화합니다."""
        super().__init__(expand=True, spacing=12, scroll=ft.ScrollMode.ADAPTIVE)
        self._page = page
        self._stats_service = stats_service

        self._summary_col = ft.Column(spacing=8)
        self._record_list = ft.ListView(expand=False, spacing=8)
        self._chart_image = ft.Image(visible=False, fit=ft.ImageFit.CONTAIN, height=260)
        self._wordcloud_image = ft.Image(visible=False, fit=ft.ImageFit.CONTAIN, height=260)

        self.controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("통계", size=24, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("새로고침", on_click=self._on_refresh),
                ],
            ),
            self._summary_col,
            ft.Text("작품별 기록", size=18, weight=ft.FontWeight.W_600),
            self._record_list,
            ft.Text("차트", size=18, weight=ft.FontWeight.W_600),
            self._chart_image,
            ft.Text("워드클라우드", size=18, weight=ft.FontWeight.W_600),
            self._wordcloud_image,
        ]

        self.reload()

    def _on_refresh(self, _: ft.ControlEvent) -> None:
        """버튼 클릭 시 통계를 다시 계산해 화면에 반영합니다."""
        self.reload()

    def reload(self) -> None:
        """통계 데이터/이미지 파일을 로드하여 UI에 표시합니다."""
        summary = self._stats_service.get_summary()

        self._summary_col.controls = [
            ft.Card(
                content=ft.Container(
                    padding=12,
                    content=ft.Column(
                        controls=[
                            ft.Text(f"총 읽은 화: {summary['total_read_episodes']}"),
                            ft.Text(f"메모 수: {summary['memo_count']}"),
                        ]
                    ),
                )
            )
        ]

        if summary["records_by_work"]:
            self._record_list.controls = [
                ft.Card(
                    content=ft.Container(
                        padding=10,
                        content=ft.Text(
                            f"{item['work_title']}: {item['episode_count']}화",
                        ),
                    )
                )
                for item in summary["records_by_work"]
            ]
        else:
            self._record_list.controls = [ft.Text("기록된 작품 데이터가 없습니다.")]

        chart_path = self._stats_service.generate_episode_bar_chart()
        if chart_path:
            self._chart_image.src = chart_path
            self._chart_image.visible = True
        else:
            self._chart_image.visible = False

        wordcloud_path = self._stats_service.generate_memo_wordcloud()
        if wordcloud_path:
            self._wordcloud_image.src = wordcloud_path
            self._wordcloud_image.visible = True
        else:
            self._wordcloud_image.visible = False

        self.update()
