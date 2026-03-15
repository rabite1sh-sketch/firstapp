from __future__ import annotations

from typing import Callable

import flet as ft

from comiclog.services.work_service import WorkService


class AddWorkView(ft.Column):
    """작품 추가 화면 UI를 담당하는 뷰 클래스."""

    def __init__(
        self,
        page: ft.Page,
        work_service: WorkService,
        on_work_added: Callable[[], None] | None = None,
    ) -> None:
        """페이지/서비스를 주입받아 입력 폼을 초기화합니다."""
        super().__init__(expand=True, spacing=12)
        self._page = page
        self._work_service = work_service
        self._on_work_added = on_work_added

        self._title = ft.TextField(label="제목", autofocus=True)
        self._author = ft.TextField(label="작가")
        self._platform = ft.TextField(label="플랫폼")
        self._read_link = ft.TextField(label="읽기 링크")

        self.controls = [
            ft.Text("작품 추가", size=24, weight=ft.FontWeight.BOLD),
            self._title,
            self._author,
            self._platform,
            self._read_link,
            ft.Row(controls=[ft.ElevatedButton("작품 추가", on_click=self._on_add_work_click)]),
        ]

    def _on_add_work_click(self, _: ft.ControlEvent) -> None:
        """버튼 클릭 시 work_service.add_work()를 호출하고 Works 목록으로 이동합니다."""
        title = (self._title.value or "").strip()
        author = (self._author.value or "").strip() or None
        platform = (self._platform.value or "").strip()
        read_link = (self._read_link.value or "").strip()

        if not title:
            self._page.snack_bar = ft.SnackBar(ft.Text("제목은 필수 입력입니다."))
            self._page.snack_bar.open = True
            self._page.update()
            return

        extra_lines: list[str] = []
        if platform:
            extra_lines.append(f"플랫폼: {platform}")
        if read_link:
            extra_lines.append(f"읽기 링크: {read_link}")
        description = "\n".join(extra_lines) if extra_lines else None

        self._work_service.add_work(title=title, author=author, description=description)

        if self._on_work_added is not None:
            self._on_work_added()

        # 요구사항: 작품 추가 직후 Works 목록으로 이동
        self._page.go("/works")
