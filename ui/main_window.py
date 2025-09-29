import flet as ft
from ui.file_selector import FileSelector
from ui.progress_view import ProgressView
from ui.settings_panel import SettingsPanel
from converter.markitdown_wrapper import MarkItDownConverter
import asyncio


class MainWindow(ft.Container):
    def __init__(self, page: ft.Page):
        self.page = page
        self.converter = MarkItDownConverter()
        self.current_view = "selector"  # selector, progress, settings

        # Components
        self.file_selector = None
        self.progress_view = None
        self.settings_panel = None

        # State
        self.selected_files = []
        self.output_directory = ""
        self.conversion_settings = {
            "use_llm": False,
            "overwrite_policy": "skip",
            "add_timestamp": False,
            "preserve_structure": True
        }

        super().__init__(content=self._build())

    def _build(self):
        # Initialize components
        self.file_selector = FileSelector(self.on_files_selected, self.on_start_conversion, self.page)
        self.progress_view = ProgressView()
        self.settings_panel = SettingsPanel(self.on_settings_changed)

        # Add file pickers to page overlay
        if self.page and hasattr(self.file_selector, 'file_picker'):
            self.page.overlay.extend([
                self.file_selector.file_picker,
                self.file_selector.folder_picker,
                self.file_selector.output_folder_picker
            ])

        # Create modern glass-morphic container
        self.main_container = ft.Container(
            content=ft.Column(
                controls=[
                    self._create_header(),
                    ft.Divider(height=1, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                    self._create_content_area(),
                ],
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
            ),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[
                    ft.Colors.with_opacity(0.05, ft.Colors.BLUE),
                    ft.Colors.with_opacity(0.02, ft.Colors.PURPLE),
                ],
            ),
            border_radius=20,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            padding=0,
            expand=True,
            blur=ft.Blur(20, 20, ft.BlurTileMode.MIRROR),
        )

        # Wrap in a background container
        return ft.Container(
            content=self.main_container,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[
                    "#1a1a2e",
                    "#0f0f1e",
                ],
            ),
            expand=True,
            padding=20,
        )

    def _create_header(self):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.TRANSFORM_ROUNDED,
                                size=32,
                                color=ft.Colors.BLUE_ACCENT_400,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "MarkItDown Converter",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                    ),
                                    ft.Text(
                                        "Transform documents to Markdown",
                                        size=12,
                                        color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                                    ),
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=15,
                    ),
                    ft.Row(
                        controls=[
                            self._create_nav_button(
                                ft.Icons.FOLDER_OPEN_ROUNDED,
                                "Files",
                                "selector",
                            ),
                            self._create_nav_button(
                                ft.Icons.PENDING_ACTIONS_ROUNDED,
                                "Progress",
                                "progress",
                            ),
                            self._create_nav_button(
                                ft.Icons.SETTINGS_ROUNDED,
                                "Settings",
                                "settings",
                            ),
                            ft.Container(width=10),
                            ft.IconButton(
                                icon=ft.Icons.DARK_MODE_ROUNDED
                                if self.page.theme_mode == ft.ThemeMode.LIGHT
                                else ft.Icons.LIGHT_MODE_ROUNDED,
                                icon_color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                                on_click=self.toggle_theme,
                                tooltip="Toggle theme",
                            ),
                        ],
                        spacing=5,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.all(20),
        )

    def _create_nav_button(self, icon, label, view_name):
        is_active = self.current_view == view_name
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        icon,
                        size=20,
                        color=ft.Colors.BLUE_ACCENT_400 if is_active else ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                    ),
                    ft.Text(
                        label,
                        size=14,
                        color=ft.Colors.WHITE if is_active else ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                        weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                    ),
                ],
                spacing=8,
            ),
            padding=ft.padding.symmetric(horizontal=15, vertical=8),
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_ACCENT_400) if is_active else None,
            on_click=lambda e, v=view_name: self.switch_view(v),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )

    def _create_content_area(self):
        self.content_container = ft.AnimatedSwitcher(
            content=self.file_selector,
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=300,
            reverse_duration=200,
            switch_in_curve=ft.AnimationCurve.EASE_IN_OUT,
            switch_out_curve=ft.AnimationCurve.EASE_IN_OUT,
            expand=True,
        )

        return ft.Container(
            content=self.content_container,
            padding=20,
            expand=True,
        )

    def switch_view(self, view_name):
        self.current_view = view_name

        if view_name == "selector":
            self.content_container.content = self.file_selector
        elif view_name == "progress":
            self.content_container.content = self.progress_view
        elif view_name == "settings":
            self.content_container.content = self.settings_panel

        # Update navigation buttons
        self.update()

    def toggle_theme(self, e):
        self.page.theme_mode = (
            ft.ThemeMode.LIGHT
            if self.page.theme_mode == ft.ThemeMode.DARK
            else ft.ThemeMode.DARK
        )
        self.page.update()
        self.update()

    def on_files_selected(self, files):
        self.selected_files = files
        print(f"Files selected: {len(files)}")

    def on_start_conversion(self, files, output_dir):
        self.selected_files = files
        self.output_directory = output_dir

        # Switch to progress view
        self.switch_view("progress")

        # Start conversion in background using Flet's async handling
        self.page.run_task(self.start_conversion_async)

    async def start_conversion_async(self):
        await self.converter.batch_convert(
            self.selected_files,
            self.output_directory,
            self.conversion_settings,
            self.progress_view.update_progress,
        )

    def on_settings_changed(self, settings):
        self.conversion_settings.update(settings)
        print(f"Settings updated: {settings}")