# MarkItDown UI Converter

A modern, sleek desktop GUI application that provides a user-friendly interface for batch converting documents to Markdown using Microsoft's MarkItDown library.

## Features

### ✨ Modern Glass-Morphic UI
- Sleek, cutting-edge interface with animations
- Dark/Light theme support
- Responsive design with smooth transitions
- Real-time visual feedback

### 📁 Comprehensive File Support
- **Documents**: PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx), EPub
- **Images**: JPEG, PNG, GIF, BMP (with OCR support)
- **Web**: HTML files, YouTube URLs
- **Text**: TXT, CSV, JSON, XML
- **Audio**: MP3, WAV, M4A (with speech transcription)
- **Archives**: ZIP files (processes contents)

### 🚀 Advanced Features
- Batch conversion with multi-threading
- Real-time progress tracking with animations
- Configurable settings and conversion profiles
- Error handling and detailed logging
- Output directory customization
- File overwrite policies (skip, overwrite, rename)

## Installation

### Quick Setup (Recommended)

**Windows:**
```batch
# Run the setup script
setup.bat

# Run the application
run.bat
```

**macOS/Linux:**
```bash
# Make scripts executable and run setup
chmod +x setup.sh run.sh
./setup.sh

# Run the application
./run.sh
```

### Manual Setup

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate Virtual Environment**:

   **Windows:**
   ```batch
   venv\Scripts\activate.bat
   ```

   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```

### Requirements
- Python 3.10 or higher
- Windows 10/11, macOS 10.14+, or Linux

## Usage

### File Selection
1. **Choose Mode**: Select between "Multiple Files" or "Entire Folder"
2. **Browse Files**: Click the drop zone to select files or folders
3. **Configure Output**: Set your desired output directory

### Settings Panel
- **File Handling**: Configure overwrite policies and timestamp options
- **Conversion Options**: Enable document structure preservation and AI enhancements
- **Performance**: Adjust parallel worker count for optimal speed

### Progress Tracking
- Real-time circular and linear progress indicators
- Live conversion log with success/failure status
- Completion statistics and error reporting

## Architecture

```
app.py                    # Main entry point
├── ui/
│   ├── main_window.py   # Main application window with glass-morphic design
│   ├── file_selector.py # File/folder selection with drag-and-drop
│   ├── progress_view.py # Animated progress tracking
│   └── settings_panel.py # Configuration options
├── converter/
│   └── markitdown_wrapper.py # MarkItDown integration with async processing
└── utils/               # Utility functions
```

## Sample Files

Test the application with the included sample files:
- `test_sample.html` - HTML file example
- `test_sample.txt` - Plain text file example

## Technical Details

### Framework
- **Flet**: Cross-platform GUI framework based on Flutter
- **MarkItDown**: Microsoft's document conversion library
- **Python 3.10+**: Required for compatibility

### Performance
- Multi-threaded batch processing
- Async operations for UI responsiveness
- Target: <2 seconds per typical PDF document

### Configuration
Settings are automatically saved to `~/.markitdown_converter/settings.json`

## Development

### Project Structure
The application follows a clean three-layer architecture:
1. **UI Layer**: Modern Flet-based interface
2. **Conversion Core**: MarkItDown wrapper with batch processing
3. **File Management**: I/O operations and configuration

### Extending Support
To add new file format support:
1. Update `get_supported_formats()` in `markitdown_wrapper.py`
2. Add format detection logic in `convert_single_file()`
3. Update UI file filters in `file_selector.py`

## Future Enhancements

- Drag-and-drop file support
- Watch folder mode for automatic conversions
- Cloud storage integration
- Conversion templates and presets
- OCR quality settings
- Batch processing queue management

## License

This project builds upon Microsoft's MarkItDown library and follows open-source principles for educational and development purposes.