from __future__ import annotations

import flet as ft

from comiclog.services.stats_service import StatsService


class StatsView(ft.Column):
    """ComicLog 통계 화면(UI)."""

    def __init__(self, page: ft.Page, stats_service: StatsService) -> None:
        """컨트롤만 구성하고 데이터 로딩은 외부(main.py)에서 호출합니다."""
        super().__init__(expand=True, spacing=12, scroll=ft.ScrollMode.ADAPTIVE)
        self._page = page
        self._stats_service = stats_service

        self._summary_col = ft.Column(spacing=8)
        self._record_list = ft.ListView(expand=False, spacing=8)

        # Flet 0.82.2 호환: src 필수, fit은 문자열 사용
        self._chart_image = ft.Image(src="", visible=False, fit="contain", height=260)
        self._wordcloud_image = ft.Image(src="", visible=False, fit="contain", height=260)

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

    def _on_refresh(self, _: ft.ControlEvent) -> None:
        """버튼 클릭 시 통계를 다시 계산해 화면에 반영합니다."""
        self.reload()
        self._page.update()

    def reload(self) -> None:
        """통계 데이터/이미지 파일을 로드하여 UI에 반영합니다(내부 update 호출 없음)."""
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
                        content=ft.Text(f"{item['work_title']}: {item['episode_count']}화"),
                    )
                )
                for item in summary["records_by_work"]
            ]
        else:
            self._record_list.controls = [ft.Text("기록된 작품 데이터가 없습니다.")]

        chart_path = self._stats_service.generate_episode_bar_chart()
        self._chart_image.src = chart_path or ""
        self._chart_image.visible = bool(chart_path)

        wordcloud_path = self._stats_service.generate_memo_wordcloud()
        self._wordcloud_image.src = wordcloud_path or ""
        self._wordcloud_image.visible = bool(wordcloud_path)
