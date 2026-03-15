from __future__ import annotations

import flet as ft
from typing import Callable

from comiclog.services.work_service import WorkService


class WorkListView(ft.Column):
    """작품 목록 화면 UI를 구성하는 뷰 클래스."""

    def __init__(
        self,
        page: ft.Page,
        work_service: WorkService,
        on_add_work: Callable[[], None] | None = None,
    ) -> None:
        """페이지 인스턴스와 작품 서비스 객체를 받아 목록 화면을 초기화합니다."""
        super().__init__(expand=True, spacing=12)
        self._page = page
        self._work_service = work_service
        self._on_add_work = on_add_work

        # 작품 목록이 렌더링될 리스트 영역입니다.
        self._work_list = ft.ListView(expand=True, spacing=10)

        self.controls = [
            ft.Row(
                controls=[
                    ft.Text("작품 목록", size=24, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("작품 추가", on_click=self._on_add_work_click),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            self._work_list,
        ]

        self.reload_works()

    def reload_works(self) -> None:
        """DB의 작품 데이터를 조회해 카드 리스트를 다시 그립니다."""
        works = self._work_service.get_works()

        if not works:
            self._work_list.controls = [
                ft.Card(
                    content=ft.Row(
                        controls=[
                            ft.Text("등록된 작품이 없습니다. '작품 추가' 버튼으로 시작하세요."),
                        ]
                    )
                )
            ]
            self.update()
            return

        cards: list[ft.Control] = []
        for work in works:
            cards.append(
                ft.Card(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        work["title"],
                                        size=18,
                                        weight=ft.FontWeight.W_600,
                                    )
                                ]
                            ),
                            ft.Text(f"작가: {work.get('author') or '-'}"),
                            ft.Text(f"설명: {work.get('description') or '-'}"),
                            ft.Row(
                                controls=[
                                    ft.ElevatedButton(
                                        "상세 보기",
                                        on_click=lambda _, work_id=work["id"]: self._go_to_detail(work_id),
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.END,
                            ),
                        ],
                        spacing=6,
                    )
                )
            )

        self._work_list.controls = cards
        self.update()

    def _on_add_work_click(self, _: ft.ControlEvent) -> None:
        """작품 추가 버튼 클릭 이벤트를 처리합니다."""
        if self._on_add_work is not None:
            self._on_add_work()
            return

        # 콜백이 없으면 기본 동작으로 샘플 작품을 생성합니다.
        count = len(self._work_service.get_works()) + 1
        self._work_service.add_work(
            title=f"새 작품 {count}",
            author="미정",
            description="작품 설명을 입력하세요.",
        )
        self.reload_works()

    def _go_to_detail(self, work_id: int) -> None:
        """작품 상세 화면 경로로 이동합니다."""
        self._page.go(f"/works/{work_id}")
