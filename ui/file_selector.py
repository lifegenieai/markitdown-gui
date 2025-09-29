import flet as ft
import os
from pathlib import Path


class FileSelector(ft.Container):
    def __init__(self, on_files_selected, on_start_conversion, page=None):
        self.on_files_selected = on_files_selected
        self.on_start_conversion = on_start_conversion
        self.page = page
        self.selected_files = []
        self.output_directory = str(Path.home() / "Documents" / "MarkdownOutput")
        self.selection_mode = "files"  # files or folder
        super().__init__(content=self._build())

    def _build(self):
        # File picker dialogs
        self.file_picker = ft.FilePicker(
            on_result=self.on_file_picker_result,
        )
        self.folder_picker = ft.FilePicker(
            on_result=self.on_folder_picker_result,
        )
        self.output_folder_picker = ft.FilePicker(
            on_result=self.on_output_folder_result,
        )

        # Pickers will be added to page overlay from MainWindow

        # Stats display
        self.stats_text = ft.Text(
            "No files selected",
            size=14,
            color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
        )

        # File list container
        self.file_list = ft.ListView(
            height=300,  # Increased height for better visibility
            spacing=5,
            padding=ft.padding.all(10),
            auto_scroll=True,  # Auto-scroll to bottom when new items added
        )

        return ft.Column(
            controls=[
                self._create_mode_selector(),
                self._create_drop_zone(),
                self._create_file_stats(),
                self._create_output_selector(),
                self._create_action_buttons(),
            ],
            spacing=20,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )


    def _create_mode_selector(self):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("Selection Mode:", size=16, weight=ft.FontWeight.W_500),
                    ft.RadioGroup(
                        content=ft.Row([
                            ft.Radio(value="files", label="Multiple Files"),
                            ft.Radio(value="folder", label="Entire Folder"),
                        ]),
                        value="files",
                        on_change=self.on_mode_changed,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=10,
        )

    def _create_drop_zone(self):
        self.drop_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.CLOUD_UPLOAD_ROUNDED,
                        size=64,
                        color=ft.Colors.BLUE_ACCENT_400,
                    ),
                    ft.Text(
                        "Drop files here or click to browse",
                        size=18,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Text(
                        "Supports: PDF, Word, Excel, PowerPoint, Images, HTML, YouTube URLs",
                        size=12,
                        color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            width=float("inf"),
            height=200,
            border=ft.border.all(
                2,
                ft.Colors.with_opacity(0.3, ft.Colors.BLUE_ACCENT_400),
            ),
            border_radius=15,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE_ACCENT_400),
            on_click=self.on_browse_click,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )

        return self.drop_container

    def _create_file_stats(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.FOLDER_COPY_ROUNDED, size=20, color=ft.Colors.BLUE_ACCENT_400),
                            self.stats_text,
                        ],
                        spacing=10,
                    ),
                    ft.Container(
                        content=self.file_list,
                        border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                        border_radius=10,
                        bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE),
                        visible=False,  # Initially hidden
                    ),
                ],
                spacing=10,
            ),
        )

    def _create_output_selector(self):
        self.output_path_text = ft.Text(
            self.output_directory,
            size=14,
            color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Output Directory", size=16, weight=ft.FontWeight.W_500),
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.FOLDER_ROUNDED, size=20, color=ft.Colors.ORANGE_ACCENT_400),
                            ft.Container(
                                content=self.output_path_text,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DRIVE_FILE_MOVE_ROUNDED,
                                icon_color=ft.Colors.BLUE_ACCENT_400,
                                tooltip="Change output directory",
                                on_click=self.browse_output_folder,
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                spacing=10,
            ),
            padding=ft.padding.all(15),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE),
        )

    def _create_action_buttons(self):
        self.convert_button = ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.TRANSFORM_ROUNDED, size=20),
                    ft.Text("Start Conversion", size=16, weight=ft.FontWeight.W_500),
                ],
                spacing=10,
            ),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.BLUE_ACCENT_400,
                    ft.ControlState.HOVERED: ft.Colors.BLUE_ACCENT_700,
                },
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation={"pressed": 0, "": 2},
            ),
            disabled=True,
            on_click=self.start_conversion,
        )

        self.clear_button = ft.TextButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CLEAR_ROUNDED, size=18),
                    ft.Text("Clear Selection", size=14),
                ],
                spacing=5,
            ),
            style=ft.ButtonStyle(
                color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                padding=15,
            ),
            on_click=self.clear_selection,
        )

        return ft.Row(
            controls=[
                self.convert_button,
                self.clear_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

    def on_mode_changed(self, e):
        self.selection_mode = e.control.value
        self.clear_selection(None)

    def on_browse_click(self, e):
        if self.selection_mode == "files":
            self.file_picker.pick_files(
                dialog_title="Select files to convert",
                allow_multiple=True,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["pdf", "docx", "xlsx", "pptx", "html", "jpg", "jpeg", "png", "txt", "csv", "json", "xml"],
            )
        else:
            self.folder_picker.get_directory_path(
                dialog_title="Select folder to convert",
            )

    def browse_output_folder(self, e):
        self.output_folder_picker.get_directory_path(
            dialog_title="Select output directory",
        )

    def on_file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.selected_files = [(f.path, f.name) for f in e.files]
            self.update_file_display()

    def on_folder_picker_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            # Get all supported files in the folder
            folder_path = e.path
            supported_extensions = {'.pdf', '.docx', '.xlsx', '.pptx', '.html', '.jpg', '.jpeg', '.png', '.txt', '.csv', '.json', '.xml'}

            self.selected_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if Path(file).suffix.lower() in supported_extensions:
                        file_path = os.path.join(root, file)
                        self.selected_files.append((file_path, file))

            self.update_file_display()

    def on_output_folder_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.output_directory = e.path
            self.output_path_text.value = e.path
            self.update()

    def update_file_display(self):
        if self.selected_files:
            # Update stats
            total_size = 0
            file_types = {}

            for file_path, file_name in self.selected_files:
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
                    ext = Path(file_path).suffix.lower()
                    file_types[ext] = file_types.get(ext, 0) + 1

            # Update stats text
            size_mb = total_size / (1024 * 1024)
            self.stats_text.value = f"{len(self.selected_files)} files selected ({size_mb:.1f} MB)"

            # Update file list
            self.file_list.controls.clear()
            for file_path, file_name in self.selected_files[:10]:  # Show first 10 files
                self.file_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(self._get_file_icon(file_path), size=16, color=ft.Colors.BLUE_ACCENT_400),
                                ft.Text(file_name, size=12, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ],
                            spacing=10,
                        ),
                        padding=5,
                    )
                )

            if len(self.selected_files) > 10:
                self.file_list.controls.append(
                    ft.Text(f"... and {len(self.selected_files) - 10} more files", size=12, italic=True)
                )

            # Show file list container
            self.file_list.parent.visible = True

            # Enable convert button
            self.convert_button.disabled = False

            # Update drop zone appearance
            self.drop_container.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.GREEN_ACCENT_400)
            self.drop_container.border = ft.border.all(2, ft.Colors.with_opacity(0.5, ft.Colors.GREEN_ACCENT_400))

        self.on_files_selected(self.selected_files)
        self.update()

    def _get_file_icon(self, file_path):
        ext = Path(file_path).suffix.lower()
        icon_map = {
            '.pdf': ft.Icons.PICTURE_AS_PDF_ROUNDED,
            '.docx': ft.Icons.ARTICLE_ROUNDED,
            '.xlsx': ft.Icons.TABLE_CHART_ROUNDED,
            '.pptx': ft.Icons.SLIDESHOW_ROUNDED,
            '.html': ft.Icons.HTML_ROUNDED,
            '.jpg': ft.Icons.IMAGE_ROUNDED,
            '.jpeg': ft.Icons.IMAGE_ROUNDED,
            '.png': ft.Icons.IMAGE_ROUNDED,
            '.txt': ft.Icons.DESCRIPTION_ROUNDED,
            '.csv': ft.Icons.TABLE_ROWS_ROUNDED,
            '.json': ft.Icons.DATA_OBJECT_ROUNDED,
            '.xml': ft.Icons.CODE_ROUNDED,
        }
        return icon_map.get(ext, ft.Icons.INSERT_DRIVE_FILE_ROUNDED)

    def clear_selection(self, e):
        self.selected_files = []
        self.file_list.controls.clear()
        self.file_list.parent.visible = False
        self.stats_text.value = "No files selected"
        self.convert_button.disabled = True

        # Reset drop zone appearance
        self.drop_container.bgcolor = ft.Colors.with_opacity(0.05, ft.Colors.BLUE_ACCENT_400)
        self.drop_container.border = ft.border.all(2, ft.Colors.with_opacity(0.3, ft.Colors.BLUE_ACCENT_400))

        self.update()

    def start_conversion(self, e):
        if self.selected_files and self.output_directory:
            self.on_start_conversion(self.selected_files, self.output_directory)