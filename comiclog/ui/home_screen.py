from __future__ import annotations

import flet as ft


class HomeScreen(ft.Container):
    """ComicLog 기본 시작 화면."""

    def __init__(self) -> None:
        super().__init__(
            expand=True,
            alignment=ft.alignment.center,
            content=ft.Text(
                "ComicLog",
                size=36,
                weight=ft.FontWeight.BOLD,
            ),
        )
