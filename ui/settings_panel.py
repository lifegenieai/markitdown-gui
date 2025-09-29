import flet as ft
import json
import os
from pathlib import Path


class SettingsPanel(ft.Container):
    def __init__(self, on_settings_changed):
        self.on_settings_changed = on_settings_changed
        self.settings_file = Path.home() / ".markitdown_converter" / "settings.json"
        self.settings = self.load_settings()
        super().__init__(content=self._build())

    def _build(self):
        # Settings controls
        self.overwrite_policy = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="skip", label="Skip existing files"),
                ft.Radio(value="overwrite", label="Overwrite existing files"),
                ft.Radio(value="rename", label="Rename with number suffix"),
            ]),
            value=self.settings.get("overwrite_policy", "skip"),
            on_change=self.on_setting_change,
        )

        self.add_timestamp = ft.Switch(
            label="Add timestamp to output files",
            value=self.settings.get("add_timestamp", False),
            active_color=ft.Colors.BLUE_ACCENT_400,
            on_change=self.on_setting_change,
        )

        self.preserve_structure = ft.Switch(
            label="Preserve document structure",
            value=self.settings.get("preserve_structure", True),
            active_color=ft.Colors.BLUE_ACCENT_400,
            on_change=self.on_setting_change,
        )

        self.use_llm = ft.Switch(
            label="Use AI for enhanced image descriptions (requires API key)",
            value=self.settings.get("use_llm", False),
            active_color=ft.Colors.PURPLE_ACCENT_400,
            on_change=self.on_setting_change,
        )

        self.parallel_workers = ft.Slider(
            min=1,
            max=8,
            divisions=7,
            value=self.settings.get("parallel_workers", 4),
            label="{value}",
            active_color=ft.Colors.ORANGE_ACCENT_400,
            on_change=self.on_setting_change,
        )

        # Markdown formatting options
        self.enhancement_level = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="basic", label="Basic - Essential formatting only"),
                ft.Radio(value="standard", label="Standard - Headings, lists, tables"),
                ft.Radio(value="advanced", label="Advanced - Full structure optimization"),
            ]),
            value=self.settings.get("enhancement_level", "standard"),
            on_change=self.on_setting_change,
        )

        self.preserve_structure = ft.Switch(
            label="Preserve existing document structure",
            value=self.settings.get("preserve_structure", True),
            active_color=ft.Colors.TEAL_ACCENT_400,
            on_change=self.on_setting_change,
        )

        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.SETTINGS_ROUNDED, size=28, color=ft.Colors.BLUE_ACCENT_400),
                                    ft.Text("Conversion Settings", size=20, weight=ft.FontWeight.BOLD),
                                ],
                                spacing=10,
                            ),
                            ft.Divider(height=20, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                        ],
                    ),
                    padding=ft.padding.only(bottom=10),
                ),

                # File Handling Section
                self._create_section(
                    "File Handling",
                    ft.Icons.FOLDER_SPECIAL_ROUNDED,
                    ft.Colors.BLUE_ACCENT_400,
                    [
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("When output file exists:", size=14, weight=ft.FontWeight.W_500),
                                    self.overwrite_policy,
                                ],
                                spacing=10,
                            ),
                        ),
                        self.add_timestamp,
                    ],
                ),

                # Conversion Options Section
                self._create_section(
                    "Conversion Options",
                    ft.Icons.TRANSFORM_ROUNDED,
                    ft.Colors.GREEN_ACCENT_400,
                    [
                        self.use_llm,
                    ],
                ),

                # Markdown Formatting Section
                self._create_section(
                    "Markdown Formatting",
                    ft.Icons.FORMAT_ALIGN_LEFT_ROUNDED,
                    ft.Colors.TEAL_ACCENT_400,
                    [
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Enhancement level:", size=14, weight=ft.FontWeight.W_500),
                                    self.enhancement_level,
                                ],
                                spacing=10,
                            ),
                        ),
                        self.preserve_structure,
                    ],
                ),

                # Performance Section
                self._create_section(
                    "Performance",
                    ft.Icons.SPEED_ROUNDED,
                    ft.Colors.ORANGE_ACCENT_400,
                    [
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Parallel conversion workers:", size=14, weight=ft.FontWeight.W_500),
                                    self.parallel_workers,
                                    ft.Text(
                                        "More workers = faster conversion but higher CPU usage",
                                        size=12,
                                        color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                                        italic=True,
                                    ),
                                ],
                                spacing=10,
                            ),
                        ),
                    ],
                ),

                # Supported Formats Info
                self._create_info_section(),

                # Action Buttons
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.SAVE_ROUNDED, size=18),
                                        ft.Text("Save Settings", size=14),
                                    ],
                                    spacing=8,
                                ),
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor=ft.Colors.BLUE_ACCENT_400,
                                    padding=15,
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                                on_click=self.save_settings_to_file,
                            ),
                            ft.TextButton(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.RESTORE_ROUNDED, size=18),
                                        ft.Text("Reset to Defaults", size=14),
                                    ],
                                    spacing=8,
                                ),
                                style=ft.ButtonStyle(
                                    color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                                    padding=15,
                                ),
                                on_click=self.reset_settings,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    margin=ft.margin.only(top=20),
                ),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _create_section(self, title: str, icon: str, color: str, controls: list):
        """Create a settings section with consistent styling"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icon, size=24, color=color),
                            ft.Text(title, size=16, weight=ft.FontWeight.W_600),
                        ],
                        spacing=10,
                    ),
                    ft.Container(
                        content=ft.Column(controls=controls, spacing=15),
                        padding=ft.padding.only(left=34, top=10),
                    ),
                ],
                spacing=10,
            ),
            padding=20,
            border_radius=15,
            bgcolor=ft.Colors.with_opacity(0.05, color),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, color)),
        )

    def _create_info_section(self):
        """Create the supported formats information section"""
        formats = {
            "Documents": ["PDF", "Word (.docx)", "PowerPoint (.pptx)", "Excel (.xlsx)", "EPub"],
            "Images": ["JPEG", "PNG", "GIF", "BMP (with OCR support)"],
            "Web": ["HTML", "YouTube URLs"],
            "Text": ["TXT", "CSV", "JSON", "XML"],
            "Audio": ["MP3", "WAV", "M4A (with transcription)"],
            "Archives": ["ZIP (processes contents)"],
        }

        format_chips = []
        for category, items in formats.items():
            format_chips.append(
                ft.Container(
                    content=ft.Text(category, size=12, weight=ft.FontWeight.BOLD),
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    border_radius=20,
                    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_ACCENT_400),
                )
            )
            for item in items:
                format_chips.append(
                    ft.Container(
                        content=ft.Text(item, size=11),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        border_radius=15,
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_ACCENT_400),
                    )
                )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.INFO_ROUNDED, size=24, color=ft.Colors.PURPLE_ACCENT_400),
                            ft.Text("Supported Formats", size=16, weight=ft.FontWeight.W_600),
                        ],
                        spacing=10,
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=format_chips,
                            wrap=True,
                            spacing=8,
                            run_spacing=8,
                        ),
                        padding=ft.padding.only(left=34, top=10),
                    ),
                ],
                spacing=10,
            ),
            padding=20,
            border_radius=15,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PURPLE_ACCENT_400),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.PURPLE_ACCENT_400)),
        )

    def on_setting_change(self, e):
        """Handle setting changes"""
        # Update settings dictionary
        self.settings["overwrite_policy"] = self.overwrite_policy.value
        self.settings["add_timestamp"] = self.add_timestamp.value
        self.settings["preserve_structure"] = self.preserve_structure.value
        self.settings["use_llm"] = self.use_llm.value
        self.settings["parallel_workers"] = int(self.parallel_workers.value)
        self.settings["enhancement_level"] = self.enhancement_level.value

        # Notify parent
        self.on_settings_changed(self.settings)

    def save_settings_to_file(self, e):
        """Save settings to JSON file"""
        try:
            os.makedirs(self.settings_file.parent, exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)

            # Show success message
            if self.page:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("Settings saved successfully!"),
                        bgcolor=ft.Colors.GREEN_ACCENT_400,
                    )
                )
        except Exception as ex:
            print(f"Error saving settings: {ex}")
            if self.page:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Error saving settings: {ex}"),
                        bgcolor=ft.Colors.RED_ACCENT_400,
                    )
                )

    def load_settings(self):
        """Load settings from JSON file"""
        default_settings = {
            "overwrite_policy": "skip",
            "add_timestamp": False,
            "preserve_structure": True,
            "use_llm": False,
            "parallel_workers": 4,
            "enhancement_level": "standard",
        }

        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    default_settings.update(loaded_settings)
            except Exception as ex:
                print(f"Error loading settings: {ex}")

        return default_settings

    def reset_settings(self, e):
        """Reset settings to defaults"""
        self.settings = {
            "overwrite_policy": "skip",
            "add_timestamp": False,
            "preserve_structure": True,
            "use_llm": False,
            "parallel_workers": 4,
            "enhancement_level": "standard",
        }

        # Update UI controls
        self.overwrite_policy.value = "skip"
        self.add_timestamp.value = False
        self.preserve_structure.value = True
        self.use_llm.value = False
        self.parallel_workers.value = 4
        self.enhancement_level.value = "standard"

        self.update()
        self.on_settings_changed(self.settings)

        # Show message
        if self.page:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Settings reset to defaults"),
                    bgcolor=ft.Colors.ORANGE_ACCENT_400,
                )
            )