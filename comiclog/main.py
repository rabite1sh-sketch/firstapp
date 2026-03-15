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

    # 탭/화면에서 재사용할 서비스
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
        """Home 탭 화면 렌더링."""
        home_view = HomeView(stats_service=stats_service)
        home_view.reload()
        content.content = home_view

    def render_works(route: str) -> None:
        """Works 탭의 목록/추가/상세 화면 렌더링."""
        parts = route.strip("/").split("/")

        if route == "/works/new":
            content.content = AddWorkView(
                page=page,
                work_service=work_service,
                on_work_added=lambda: None,
            )
            return

        if len(parts) == 2 and parts[0] == "works" and parts[1].isdigit():
            content.content = WorkDetailView(
                page=page,
                work_id=int(parts[1]),
                work_service=work_service,
                db_path=db_path,
            )
            return

        work_list = WorkListView(
            page=page,
            work_service=work_service,
            on_add_work=lambda: page.go("/works/new"),
        )
        content.content = work_list

        # 요구사항: WorkListView 생성 후 reload_works() 호출 + page.update()
        work_list.reload_works()
        page.update()

    def render_highlights() -> None:
        """Highlights 탭 화면 렌더링."""
        highlight_view = HighlightView(page=page, highlight_service=highlight_service)
        highlight_view.reload()
        content.content = highlight_view

    def render_stats() -> None:
        """Stats 탭 화면 렌더링."""
        stats_view = StatsView(page=page, stats_service=stats_service)
        stats_view.reload()
        content.content = stats_view

    def render_from_state() -> None:
        """현재 탭/라우트 상태 기준으로 본문 화면 갱신."""
        if navigation.selected_index == TAB_HOME:
            render_home()
        elif navigation.selected_index == TAB_WORKS:
            render_works(page.route or "/works")
            return
        elif navigation.selected_index == TAB_HIGHLIGHTS:
            render_highlights()
        else:
            render_stats()

        # 탭 컨트롤 구성 후 업데이트는 한 번만 호출
        page.update()

    def on_nav_change(_: ft.ControlEvent) -> None:
        """하단 탭 선택 변경 처리."""
        if navigation.selected_index == TAB_HOME:
            page.go("/")
        elif navigation.selected_index == TAB_WORKS:
            page.go("/works")
        elif navigation.selected_index == TAB_HIGHLIGHTS:
            page.go("/highlights")
        else:
            page.go("/stats")

    def on_route_change(_: ft.RouteChangeEvent) -> None:
        """라우트 변경 시 탭 선택값과 렌더링 상태 동기화."""
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
