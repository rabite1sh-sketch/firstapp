from __future__ import annotations

import flet as ft

from comiclog.db.database import Database
from comiclog.services.highlight_service import HighlightService
from comiclog.services.stats_service import StatsService
from comiclog.services.work_service import WorkService
from comiclog.ui.add_work_view import AddWorkView
from comiclog.ui.highlight_view import HighlightView
from comiclog.ui.home_view import HomeView
from comiclog.ui.stats_view import StatsView
from comiclog.ui.work_detail_view import WorkDetailView
from comiclog.ui.work_list_view import WorkListView

TAB_HOME = 0
TAB_WORKS = 1
TAB_HIGHLIGHTS = 2
TAB_STATS = 3


def main(page: ft.Page) -> None:
    """앱 시작점: DB 초기화 후 NavigationBar 기반 탭/라우트를 구성합니다."""
    page.title = "ComicLog"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    db_path = "comiclog/database/comiclog.db"
    database = Database(db_path)
    database.initialize()

    work_service = WorkService(db_path)
    highlight_service = HighlightService(db_path)
    stats_service = StatsService(db_path)

    # 앱 첫 실행 체험을 위한 샘플 작품 데이터
    if not work_service.get_works():
        work_service.add_work(title="샘플 작품 A", author="작가 미정", description="플랫폼: Sample")
        work_service.add_work(title="샘플 작품 B", author="작가 미정", description="플랫폼: Sample")

    content = ft.Container(expand=True, padding=16)

    navigation = ft.NavigationBar(
        selected_index=TAB_HOME,
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

    def render_home() -> None:
        home_view = HomeView(stats_service=stats_service)
        home_view.reload()
        content.content = home_view
        page.update()

    def render_works(route: str) -> None:
        parts = route.strip("/").split("/")

        if route == "/works/new":
            content.content = AddWorkView(page=page, work_service=work_service)
            page.update()
            return

        if len(parts) == 2 and parts[0] == "works" and parts[1].isdigit():
            content.content = WorkDetailView(
                page=page,
                work_id=int(parts[1]),
                work_service=work_service,
                db_path=db_path,
            )
            page.update()
            return

        work_list = WorkListView(
            page=page,
            work_service=work_service,
            on_add_work=lambda: page.go("/works/new"),
        )
        content.content = work_list
        # 요구사항: 컨트롤 추가 이후 목록 로드
        work_list.reload_works()
        page.update()

    def render_highlights() -> None:
        highlight_view = HighlightView(page=page, highlight_service=highlight_service)
        content.content = highlight_view
        highlight_view.reload()
        page.update()

    def render_stats() -> None:
        stats_view = StatsView(page=page, stats_service=stats_service)
        content.content = stats_view
        stats_view.reload()
        page.update()

    def render_from_state() -> None:
        if navigation.selected_index == TAB_HOME:
            render_home()
        elif navigation.selected_index == TAB_WORKS:
            render_works(page.route or "/works")
        elif navigation.selected_index == TAB_HIGHLIGHTS:
            render_highlights()
        else:
            render_stats()

    def on_nav_change(_: ft.ControlEvent) -> None:
        if navigation.selected_index == TAB_HOME:
            page.go("/")
        elif navigation.selected_index == TAB_WORKS:
            page.go("/works")
        elif navigation.selected_index == TAB_HIGHLIGHTS:
            page.go("/highlights")
        else:
            page.go("/stats")

    def on_route_change(_: ft.RouteChangeEvent) -> None:
        route = page.route or "/"
        if route.startswith("/works"):
            navigation.selected_index = TAB_WORKS
        elif route.startswith("/highlights"):
            navigation.selected_index = TAB_HIGHLIGHTS
        elif route.startswith("/stats"):
            navigation.selected_index = TAB_STATS
        else:
            navigation.selected_index = TAB_HOME

        render_from_state()

    navigation.on_change = on_nav_change
    page.on_route_change = on_route_change

    page.add(ft.Column(expand=True, spacing=0, controls=[content, navigation]))
    page.go("/")


if __name__ == "__main__":
    ft.app(target=main)
