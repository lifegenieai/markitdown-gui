# MarkItDown UI Wrapper - MVP Specification

## Overview
A simple desktop GUI application that provides a user-friendly interface for batch converting PDFs and other documents to Markdown using Microsoft's MarkItDown library.

## Core Features

### File Selection
- **Single File Mode**: File picker dialog for individual document conversion
- **Batch Mode**: Folder picker dialog for bulk conversion
- **Supported Formats**: PDF, DOCX, XLSX, PPTX (extensible)
- **Preview**: Show selected file/folder path and file count

### Configuration Options
- **Output Directory**: Choose where converted Markdown files are saved
- **Naming Convention**:
  - Keep original filename (default)
  - Add timestamp prefix
  - Custom prefix/suffix
- **LLM Integration**: Toggle for enhanced image descriptions (optional)
- **Overwrite Policy**: Skip existing, overwrite, or rename duplicates

### Conversion Process
- **Convert Button**: Start conversion process
- **Progress Bar**: Show current file being processed and overall progress
- **Real-time Log**: Display conversion status, errors, and completion messages
- **Cancel Option**: Stop conversion mid-process

### Results
- **Summary Display**: Files converted successfully vs. failed
- **Open Output**: Button to open output directory in file explorer
- **Error Report**: List of failed files with error reasons

## Technical Requirements

### Framework
- **Python + Tkinter** (built-in, no extra dependencies) or **PyQt/PySide** (more polished)
- **Alternative**: Electron-based for web tech stack

### Dependencies
- `markitdown[all]` - Core conversion functionality
- File dialog libraries (built into framework)
- Threading for non-blocking UI during conversion

### Architecture
```
┌─────────────────┐
│   GUI Layer    │ (File selection, configuration, progress)
├─────────────────┤
│ Conversion Core │ (MarkItDown wrapper, batch processing)
├─────────────────┤
│  File Manager   │ (I/O operations, directory handling)
└─────────────────┘
```

## User Interface Mockup

```
┌──────────────────────────────────────────────────────┐
│ MarkItDown Converter                            [ X ] │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Source Selection:                                    │
│ ○ Single File  ○ Folder                             │
│ [Browse...] C:\Documents\MyPDFs                     │
│ Files found: 127 PDFs                               │
│                                                      │
│ Output Settings:                                     │
│ Output Dir: [Browse...] C:\Output\Markdown          │
│ ☐ Add timestamp  ☐ Use LLM enhancement             │
│ Overwrite: [Skip existing ▼]                        │
│                                                      │
│ ┌────────────────────────────────────────────────┐   │
│ │ [Convert] [Cancel] [Open Output] [Clear Log]   │   │
│ ├────────────────────────────────────────────────┤   │
│ │ Progress: ████████░░ 67% (84/127)              │   │
│ │ Current: processing_report_2024.pdf            │   │
│ ├────────────────────────────────────────────────┤   │
│ │ Log:                                           │   │
│ │ ✓ document1.pdf → document1.md                 │   │
│ │ ✓ report.pdf → report.md                       │   │
│ │ ✗ corrupted.pdf (conversion failed)            │   │
│ │ ✓ presentation.pdf → presentation.md           │   │
│ └────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1 (MVP)
- Basic file/folder selection
- Simple conversion with default settings
- Progress tracking and basic logging
- Output directory selection

### Phase 2 (Enhanced)
- Configuration options (LLM, naming, overwrite policy)
- Better error handling and reporting
- Drag-and-drop support
- Settings persistence

### Phase 3 (Advanced)
- Watch folder mode for ongoing conversions
- Conversion templates/presets
- Integration with cloud storage
- Conversion quality metrics

## Success Criteria
- Convert hundreds of PDFs in one batch operation
- Clear progress indication and error reporting
- Intuitive interface requiring no technical knowledge
- Reliable handling of various PDF types and sizes
- Processing time under 2 seconds per typical PDF

## Implementation Notes

### MarkItDown Integration
Based on research of the Microsoft MarkItDown repository:

- **Installation**: `pip install 'markitdown[pdf]'`
- **Basic Usage**:
  ```python
  from markitdown import MarkItDown
  md = MarkItDown()
  result = md.convert("document.pdf")
  ```
- **Configuration Options**:
  ```python
  md = MarkItDown(
      enable_plugins=False,
      llm_client=client,
      llm_model="gpt-4o",
      llm_prompt="custom prompt"
  )
  ```

### Batch Processing Pattern
```python
import os
from markitdown import MarkItDown

def batch_convert(input_folder, output_folder, progress_callback=None):
    md = MarkItDown()
    files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]

    for i, filename in enumerate(files):
        try:
            result = md.convert(os.path.join(input_folder, filename))
            output_path = os.path.join(output_folder, f"{filename[:-4]}.md")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.text_content)
            if progress_callback:
                progress_callback(i + 1, len(files), filename, True)
        except Exception as e:
            if progress_callback:
                progress_callback(i + 1, len(files), filename, False, str(e))
```