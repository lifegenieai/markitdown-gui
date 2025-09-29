import flet as ft
from ui.main_window import MainWindow
import asyncio


def main(page: ft.Page):
    page.title = "MarkItDown Converter"
    page.window_width = 1200
    page.window_height = 800
    page.window_min_width = 900
    page.window_min_height = 600

    # Modern theme configuration
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        use_material3=True,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )

    # Set window properties for modern look
    page.window_bgcolor = ft.Colors.TRANSPARENT
    page.bgcolor = ft.Colors.TRANSPARENT

    # Create and add main window
    main_window = MainWindow(page)
    page.add(main_window)

    page.update()


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")