# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a desktop GUI application that provides a user-friendly interface for batch converting PDFs and other documents to Markdown using Microsoft's MarkItDown library. The project is currently in the planning/specification phase.

## Development Setup

### Virtual Environment (Required)
Always use a virtual environment for this project:
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate.bat

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Quick Setup
Use the provided setup scripts:
- **Windows**: Run `setup.bat`
- **macOS/Linux**: Run `./setup.sh`

### Dependencies
The project uses:
- **Flet**: Modern Python GUI framework based on Flutter
- **MarkItDown**: Microsoft's document conversion library with all format support

## Architecture

The application follows a three-layer architecture:
1. **GUI Layer**: File selection, configuration options, progress display
2. **Conversion Core**: MarkItDown wrapper with batch processing logic
3. **File Manager**: I/O operations and directory handling

## Key Implementation Patterns

### MarkItDown Integration
```python
from markitdown import MarkItDown

# Basic usage
md = MarkItDown()
result = md.convert("document.pdf")

# With LLM enhancement (optional)
md = MarkItDown(
    llm_client=client,
    llm_model="gpt-4o"
)
```

### Batch Processing
The application should process files asynchronously to maintain UI responsiveness. Use threading or async patterns to prevent UI blocking during conversion.

## Core Features to Implement

1. **File Selection**: Single file and folder batch mode support
2. **Progress Tracking**: Real-time progress bar and logging
3. **Error Handling**: Graceful handling of conversion failures with detailed error reporting
4. **Output Configuration**: Customizable output directory and naming conventions

## Supported File Formats

Primary focus: PDF, DOCX, XLSX, PPTX (as supported by MarkItDown)

## Performance Target

Processing time should be under 2 seconds per typical PDF document.