from __future__ import annotations

import flet as ft

from comiclog.db.database import Database
from comiclog.services.highlight_service import HighlightService
from comiclog.services.stats_service import StatsService
from comiclog.services.work_service import WorkService
from comiclog.ui.highlight_view import HighlightView
from comiclog.ui.home_screen import HomeScreen
from comiclog.ui.stats_view import StatsView
from comiclog.ui.work_list_view import WorkListView


def main(page: ft.Page) -> None:
    """앱 시작점: DB를 초기화하고 BottomNavigation 기반 화면 전환을 구성합니다."""
    page.title = "ComicLog"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    # 앱 시작 시 SQLite 파일/테이블을 준비합니다.
    database = Database("comiclog/database/comiclog.db")
    database.initialize()

    # 각 화면에서 재사용할 서비스 객체를 준비합니다.
    work_service = WorkService("comiclog/database/comiclog.db")
    highlight_service = HighlightService("comiclog/database/comiclog.db")
    stats_service = StatsService("comiclog/database/comiclog.db")

    # 화면 본문이 교체될 컨테이너입니다.
    content = ft.Container(expand=True, padding=16)

    def render_tab(index: int) -> None:
        """선택된 하단 탭 인덱스에 맞는 화면을 렌더링합니다."""
        if index == 0:
            content.content = HomeScreen()
        elif index == 1:
            content.content = WorkListView(page=page, work_service=work_service)
        elif index == 2:
            content.content = HighlightView(page=page, highlight_service=highlight_service)
        else:
            content.content = StatsView(page=page, stats_service=stats_service)
        page.update()

    def on_nav_change(e: ft.ControlEvent) -> None:
        """BottomNavigationBar 선택 변경 이벤트를 처리합니다."""
        render_tab(int(e.control.selected_index))

    navigation = ft.BottomNavigationBar(
        selected_index=0,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.BOOK_OUTLINED, selected_icon=ft.Icons.BOOK, label="Works"),
            ft.NavigationBarDestination(
                icon=ft.Icons.AUTO_AWESOME_OUTLINED,
                selected_icon=ft.Icons.AUTO_AWESOME,
                label="Highlights",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.INSERT_CHART_OUTLINED,
                selected_icon=ft.Icons.INSERT_CHART,
                label="Stats",
            ),
        ],
    )

    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[
                content,
                navigation,
            ],
        )
    )

    # 첫 화면(Home) 렌더링
    render_tab(0)


if __name__ == "__main__":
    ft.app(target=main)
