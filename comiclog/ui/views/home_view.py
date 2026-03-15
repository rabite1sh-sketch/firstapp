from __future__ import annotations

from datetime import date

import flet as ft

from comiclog.services.comic_service import ComicService


class HomeView(ft.Container):
    def __init__(self, service: ComicService, page: ft.Page) -> None:
        super().__init__(expand=True, padding=20)
        self._service = service
        self._page = page

        self._title = ft.TextField(label="만화 제목", autofocus=True)
        self._episode = ft.TextField(label="권/에피소드")
        self._memo = ft.TextField(label="감상 메모", multiline=True, min_lines=2, max_lines=4)
        self._favorite_scene = ft.TextField(
            label="명장면 기록", multiline=True, min_lines=2, max_lines=4
        )
        self._read_date = ft.TextField(label="감상 날짜", value=str(date.today()))

        self._entry_list = ft.ListView(spacing=8, auto_scroll=False, expand=True)

        self.content = ft.Column(
            controls=[
                ft.Text("ComicLog", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("읽은 만화를 기록하고 감상을 남겨보세요."),
                self._build_form(),
                ft.Divider(),
                ft.Text("최근 기록", size=20, weight=ft.FontWeight.W_600),
                self._entry_list,
            ],
            expand=True,
            spacing=14,
        )

        self.reload_entries()

    def _build_form(self) -> ft.Card:
        return ft.Card(
            content=ft.Container(
                padding=16,
                content=ft.Column(
                    controls=[
                        self._title,
                        self._episode,
                        self._memo,
                        self._favorite_scene,
                        self._read_date,
                        ft.Row(
                            controls=[
                                ft.ElevatedButton("기록 저장", on_click=self._on_save),
                                ft.TextButton("입력 초기화", on_click=self._on_clear),
                            ]
                        ),
                    ],
                    spacing=8,
                ),
            )
        )

    def _on_save(self, _: ft.ControlEvent) -> None:
        if not self._title.value or not self._episode.value:
            self._page.snack_bar = ft.SnackBar(ft.Text("제목과 에피소드는 필수입니다."))
            self._page.snack_bar.open = True
            self._page.update()
            return

        self._service.add_entry(
            title=self._title.value.strip(),
            episode=self._episode.value.strip(),
            memo=(self._memo.value or "").strip(),
            favorite_scene=(self._favorite_scene.value or "").strip(),
            read_date=(self._read_date.value or "").strip(),
        )
        self.reload_entries()
        self._on_clear(_)

        self._page.snack_bar = ft.SnackBar(ft.Text("기록이 저장되었습니다."))
        self._page.snack_bar.open = True
        self._page.update()

    def _on_clear(self, _: ft.ControlEvent) -> None:
        self._title.value = ""
        self._episode.value = ""
        self._memo.value = ""
        self._favorite_scene.value = ""
        self._read_date.value = str(date.today())
        self._page.update()

    def reload_entries(self) -> None:
        entries = self._service.list_entries()
        if not entries:
            self._entry_list.controls = [
                ft.Text("아직 저장된 기록이 없습니다. 첫 번째 기록을 남겨보세요.")
            ]
            self._page.update()
            return

        cards: list[ft.Control] = []
        for entry in entries:
            cards.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    f"{entry.title} ({entry.episode})",
                                    size=16,
                                    weight=ft.FontWeight.W_600,
                                ),
                                ft.Text(f"감상 날짜: {entry.read_date}"),
                                ft.Text(f"메모: {entry.memo or '-'}"),
                                ft.Text(f"명장면: {entry.favorite_scene or '-'}"),
                            ],
                            spacing=4,
                        ),
                    )
                )
            )

        self._entry_list.controls = cards
        self._page.update()
