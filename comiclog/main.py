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
    """앱 시작점: DB 초기화 후 NavigationBar 기반 탭 화면을 구성합니다."""
    page.title = "ComicLog"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    db_path = "comiclog/database/comiclog.db"

    # 앱 시작 시 SQLite 파일/테이블을 준비합니다.
    database = Database(db_path)
    database.initialize()

    # 탭 화면에서 공유하는 서비스 객체를 준비합니다.
    work_service = WorkService(db_path)
    highlight_service = HighlightService(db_path)
    stats_service = StatsService(db_path)

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
        """Home 탭 화면을 렌더링합니다."""
        content.content = HomeView(stats_service=stats_service)

    def render_works(route: str) -> None:
        """Works 탭 하위 화면(목록/추가/상세)을 라우트에 따라 렌더링합니다."""
        parts = route.strip("/").split("/")

        # /works/new -> 작품 추가 화면
        if route == "/works/new":
            content.content = AddWorkView(page=page, work_service=work_service)
            return

        # /works/<id> -> 작품 상세 화면
        if len(parts) == 2 and parts[0] == "works" and parts[1].isdigit():
            content.content = WorkDetailView(
                page=page,
                work_id=int(parts[1]),
                work_service=work_service,
                db_path=db_path,
            )
            return

        # 기본: 작품 목록
        content.content = WorkListView(
            page=page,
            work_service=work_service,
            on_add_work=lambda: page.go("/works/new"),
        )

    def render_highlights() -> None:
        """Highlights 탭 화면을 렌더링합니다."""
        content.content = HighlightView(page=page, highlight_service=highlight_service)

    def render_stats() -> None:
        """Stats 탭 화면을 렌더링합니다."""
        content.content = StatsView(page=page, stats_service=stats_service)

    def render_from_state() -> None:
        """현재 탭/라우트 상태를 기준으로 본문 화면을 갱신합니다."""
        if navigation.selected_index == TAB_HOME:
            render_home()
        elif navigation.selected_index == TAB_WORKS:
            render_works(page.route or "/works")
        elif navigation.selected_index == TAB_HIGHLIGHTS:
            render_highlights()
        else:
            render_stats()
        page.update()

    def on_nav_change(_: ft.ControlEvent) -> None:
        """하단 탭 선택 변경을 처리합니다."""
        if navigation.selected_index == TAB_HOME:
            page.go("/")
        elif navigation.selected_index == TAB_WORKS:
            page.go("/works")
        elif navigation.selected_index == TAB_HIGHLIGHTS:
            page.go("/highlights")
        else:
            page.go("/stats")

    def on_route_change(_: ft.RouteChangeEvent) -> None:
        """라우트 변경 시 탭 선택 상태와 화면을 동기화합니다."""
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

    # 앱 시작 라우트
    page.go("/")


if __name__ == "__main__":
    ft.app(target=main)
