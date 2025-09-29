import flet as ft
import asyncio
from typing import Dict, List
import os


class ProgressView(ft.Container):
    def __init__(self):
        self.current_file = ""
        self.completed = 0
        self.total = 0
        self.successful = 0
        self.failed = 0
        self.results = []
        super().__init__(content=self._build())

    def _build(self):
        # Progress indicators
        self.circular_progress = ft.ProgressRing(
            value=0,
            width=120,
            height=120,
            stroke_width=8,
            color=ft.Colors.BLUE_ACCENT_400,
        )

        self.progress_percentage = ft.Text(
            "0%",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
        )

        self.linear_progress = ft.ProgressBar(
            value=0,
            height=4,
            color=ft.Colors.BLUE_ACCENT_400,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        )

        self.current_file_text = ft.Text(
            "Waiting to start...",
            size=16,
            weight=ft.FontWeight.W_500,
            color=ft.Colors.WHITE,
            text_align=ft.TextAlign.CENTER,
        )

        # Statistics cards
        self.stats_row = ft.Row(
            controls=[
                self._create_stat_card("Total", "0", ft.Colors.BLUE_ACCENT_400, ft.Icons.FOLDER_ROUNDED),
                self._create_stat_card("Completed", "0", ft.Colors.PURPLE_ACCENT_400, ft.Icons.CHECK_CIRCLE_ROUNDED),
                self._create_stat_card("Successful", "0", ft.Colors.GREEN_ACCENT_400, ft.Icons.DONE_ALL_ROUNDED),
                self._create_stat_card("Failed", "0", ft.Colors.RED_ACCENT_400, ft.Icons.ERROR_ROUNDED),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        # Results log
        self.results_list = ft.ListView(
            height=300,
            spacing=5,
            padding=ft.padding.all(10),
            auto_scroll=True,
        )

        # Action buttons
        self.open_folder_btn = ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.FOLDER_OPEN_ROUNDED, size=20),
                    ft.Text("Open Output Folder", size=14),
                ],
                spacing=10,
            ),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_ACCENT_400,
                padding=15,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            visible=False,
            on_click=self.open_output_folder,
        )

        self.cancel_btn = ft.TextButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CANCEL_ROUNDED, size=18),
                    ft.Text("Cancel", size=14),
                ],
                spacing=5,
            ),
            style=ft.ButtonStyle(
                color=ft.Colors.RED_ACCENT_400,
                padding=15,
            ),
            on_click=self.cancel_conversion,
        )

        return ft.Column(
            controls=[
                # Progress circle section
                ft.Container(
                    content=ft.Stack(
                        controls=[
                            ft.Container(
                                content=self.circular_progress,
                                alignment=ft.alignment.center,
                            ),
                            ft.Container(
                                content=self.progress_percentage,
                                alignment=ft.alignment.center,
                            ),
                        ],
                        width=120,
                        height=120,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=20),
                ),

                # Linear progress and current file
                ft.Container(
                    content=ft.Column(
                        controls=[
                            self.linear_progress,
                            self.current_file_text,
                        ],
                        spacing=10,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    width=float("inf"),
                    padding=20,
                ),

                # Statistics
                self.stats_row,

                # Results log
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Conversion Log", size=16, weight=ft.FontWeight.W_500),
                            ft.Container(
                                content=self.results_list,
                                border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                                border_radius=10,
                                bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE),
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=10,
                ),

                # Action buttons
                ft.Row(
                    controls=[
                        self.open_folder_btn,
                        self.cancel_btn,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
            ],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

    def _create_stat_card(self, label: str, value: str, color: str, icon: str):
        stat_value = ft.Text(
            value,
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
            key=f"stat_{label.lower()}",
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(icon, size=32, color=color),
                    stat_value,
                    ft.Text(
                        label,
                        size=12,
                        color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=15,
            border_radius=15,
            bgcolor=ft.Colors.with_opacity(0.1, color),
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, color)),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )

    async def update_progress(
        self,
        current_file: str = None,
        completed: int = 0,
        total: int = 0,
        successful: int = 0,
        failed: int = 0,
        status: str = None,
        last_result: Dict = None,
        results: List = None,
    ):
        """Update the progress display"""
        self.completed = completed
        self.total = total
        self.successful = successful
        self.failed = failed

        if current_file:
            self.current_file_text.value = current_file

        # Update progress indicators
        if total > 0:
            progress = completed / total
            self.circular_progress.value = progress
            self.linear_progress.value = progress
            self.progress_percentage.value = f"{int(progress * 100)}%"

        # Update statistics
        self._update_stat_card("stat_total", str(total))
        self._update_stat_card("stat_completed", str(completed))
        self._update_stat_card("stat_successful", str(successful))
        self._update_stat_card("stat_failed", str(failed))

        # Add result to log
        if last_result:
            self._add_result_to_log(last_result)

        # Handle completion
        if status == "complete":
            self.current_file_text.value = "✨ Conversion Complete!"
            self.open_folder_btn.visible = True
            self.cancel_btn.visible = False

            # Add completion animation
            self.circular_progress.color = ft.Colors.GREEN_ACCENT_400
            self.linear_progress.color = ft.Colors.GREEN_ACCENT_400

            if results:
                self.results = results

        self.update()

    def _update_stat_card(self, key: str, value: str):
        """Update a specific stat card value"""
        for row in self.stats_row.controls:
            for control in row.content.controls:
                if isinstance(control, ft.Text) and hasattr(control, 'key') and control.key == key:
                    control.value = value
                    # Add pulse animation
                    row.scale = 1.1
                    row.update()
                    row.scale = 1.0
                    row.update()
                    break

    def _add_result_to_log(self, result: Dict):
        """Add a conversion result to the log"""
        icon = ft.Icons.CHECK_CIRCLE_ROUNDED if result["success"] else ft.Icons.ERROR_ROUNDED
        color = ft.Colors.GREEN_ACCENT_400 if result["success"] else ft.Colors.RED_ACCENT_400

        log_entry = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=20, color=color),
                    ft.Text(
                        result["file"],
                        size=14,
                        expand=True,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        "✓" if result["success"] else f"✗ {result.get('error', 'Failed')}",
                        size=12,
                        color=color,
                    ),
                ],
                spacing=10,
            ),
            padding=10,
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.05, color),
            animate_opacity=300,
            opacity=0,
        )

        self.results_list.controls.append(log_entry)

        # Animate entry appearance
        log_entry.opacity = 1
        self.results_list.update()

    def cancel_conversion(self, e):
        """Cancel the current conversion process"""
        # This would need to be connected to the converter
        self.current_file_text.value = "Cancelling..."
        self.update()

    def open_output_folder(self, e):
        """Open the output folder in file explorer"""
        # This would need the output directory path
        pass

    def reset(self):
        """Reset the progress view for a new conversion"""
        self.completed = 0
        self.total = 0
        self.successful = 0
        self.failed = 0
        self.results = []

        self.circular_progress.value = 0
        self.circular_progress.color = ft.Colors.BLUE_ACCENT_400
        self.linear_progress.value = 0
        self.linear_progress.color = ft.Colors.BLUE_ACCENT_400
        self.progress_percentage.value = "0%"
        self.current_file_text.value = "Waiting to start..."

        self.results_list.controls.clear()
        self.open_folder_btn.visible = False
        self.cancel_btn.visible = True

        self._update_stat_card("stat_total", "0")
        self._update_stat_card("stat_completed", "0")
        self._update_stat_card("stat_successful", "0")
        self._update_stat_card("stat_failed", "0")

        self.update()