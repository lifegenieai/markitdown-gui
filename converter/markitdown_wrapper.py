import os
import asyncio
from pathlib import Path
from typing import List, Tuple, Dict, Callable, Optional
from markitdown import MarkItDown
import threading
from concurrent.futures import ThreadPoolExecutor
import time
from .markdown_enhancer import MarkdownEnhancer


class MarkItDownConverter:
    def __init__(self):
        self._initialize_converter()
        self.enhancer = MarkdownEnhancer(enhancement_level="standard")
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.current_file = ""
        self.is_converting = False
        self.cancel_requested = False

    def _initialize_converter(self):
        """Initialize the MarkItDown converter with optimal settings."""
        try:
            # Try to initialize with LLM client for enhanced processing
            self.md_converter = MarkItDown(
                enable_plugins=True,
                # Note: LLM client would be configured here if API key is available
                # llm_client=client,
                # llm_model="gpt-4o",
                # llm_prompt="Convert to well-structured Markdown with proper headings, lists, and formatting"
            )
        except Exception as e:
            # Fallback to basic configuration
            print(f"Warning: Could not initialize with advanced features: {e}")
            self.md_converter = MarkItDown(enable_plugins=False)

    def configure_enhancement(self, enhancement_level: str = "standard",
                            preserve_structure: bool = True):
        """
        Configure the markdown enhancement settings.

        Args:
            enhancement_level: "basic", "standard", or "advanced"
            preserve_structure: Whether to preserve document structure
        """
        self.enhancer = MarkdownEnhancer(enhancement_level=enhancement_level)
        self.preserve_structure = preserve_structure

    def convert_single_file(self, file_path: str, output_dir: str, settings: Dict) -> Tuple[bool, str, str]:
        """
        Convert a single file to markdown
        Returns: (success, output_path, error_message)
        """
        try:
            # Check if it's a YouTube URL (in a text file or direct)
            if self._is_youtube_url(file_path):
                result = self._convert_youtube_url(file_path)
            else:
                # Regular file conversion
                result = self.md_converter.convert(file_path)

            if result and result.text_content:
                # Apply markdown enhancement
                file_extension = Path(file_path).suffix
                enhancement_level = settings.get("enhancement_level", "standard")
                preserve_structure = settings.get("preserve_structure", True)

                # Configure enhancer if settings changed
                if hasattr(self, 'enhancer'):
                    if self.enhancer.enhancement_level != enhancement_level:
                        self.enhancer = MarkdownEnhancer(enhancement_level=enhancement_level)

                # Enhance the markdown content
                enhanced_content = self.enhancer.enhance(
                    result.text_content,
                    file_extension=file_extension,
                    preserve_structure=preserve_structure
                )

                # Generate output filename
                input_filename = Path(file_path).stem
                timestamp = ""
                if settings.get("add_timestamp", False):
                    timestamp = f"_{int(time.time())}"

                output_filename = f"{input_filename}{timestamp}.md"
                output_path = os.path.join(output_dir, output_filename)

                # Check overwrite policy
                if os.path.exists(output_path):
                    if settings.get("overwrite_policy", "skip") == "skip":
                        return (False, output_path, "File exists (skipped)")
                    elif settings.get("overwrite_policy", "rename"):
                        counter = 1
                        base_path = output_path[:-3]  # Remove .md
                        while os.path.exists(output_path):
                            output_path = f"{base_path}_{counter}.md"
                            counter += 1

                # Ensure output directory exists
                os.makedirs(output_dir, exist_ok=True)

                # Write the enhanced markdown content
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(enhanced_content)

                return (True, output_path, None)
            else:
                return (False, None, "No content extracted")

        except Exception as e:
            return (False, None, str(e))

    def _is_youtube_url(self, file_path: str) -> bool:
        """Check if the file contains or is a YouTube URL"""
        if file_path.startswith("http") and "youtube.com" in file_path or "youtu.be" in file_path:
            return True

        # Check if it's a text file containing a YouTube URL
        if Path(file_path).suffix.lower() in ['.txt', '.url']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if "youtube.com" in content or "youtu.be" in content:
                        return True
            except:
                pass
        return False

    def _convert_youtube_url(self, url_or_file: str) -> object:
        """Convert YouTube URL to markdown"""
        try:
            # Extract URL if it's from a file
            if os.path.isfile(url_or_file):
                with open(url_or_file, 'r', encoding='utf-8') as f:
                    url = f.read().strip()
                    # Extract URL from common formats
                    if "URL=" in url:  # Windows .url file
                        for line in url.split('\n'):
                            if line.startswith("URL="):
                                url = line[4:]
                                break
            else:
                url = url_or_file

            # Use MarkItDown to convert YouTube URL
            return self.md_converter.convert(url)
        except Exception as e:
            # Return error as a result object
            class Result:
                def __init__(self, error):
                    self.text_content = f"# Error Converting YouTube URL\n\n{error}"

            return Result(str(e))

    async def batch_convert(
        self,
        files: List[Tuple[str, str]],
        output_dir: str,
        settings: Dict,
        progress_callback: Callable
    ):
        """
        Convert multiple files in batch with progress updates
        """
        self.is_converting = True
        self.cancel_requested = False

        total_files = len(files)
        completed = 0
        successful = 0
        failed = 0
        results = []

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        for file_path, file_name in files:
            if self.cancel_requested:
                break

            self.current_file = file_name

            # Update progress
            await progress_callback(
                current_file=file_name,
                completed=completed,
                total=total_files,
                successful=successful,
                failed=failed,
                status="converting"
            )

            # Convert file in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            success, output_path, error = await loop.run_in_executor(
                self.executor,
                self.convert_single_file,
                file_path,
                output_dir,
                settings
            )

            # Track results
            if success:
                successful += 1
                status = "success"
            else:
                failed += 1
                status = "failed"

            results.append({
                "file": file_name,
                "success": success,
                "output": output_path,
                "error": error,
                "status": status
            })

            completed += 1

            # Update progress with result
            await progress_callback(
                current_file=file_name,
                completed=completed,
                total=total_files,
                successful=successful,
                failed=failed,
                status=status,
                last_result=results[-1]
            )

            # Small delay to allow UI updates
            await asyncio.sleep(0.1)

        self.is_converting = False

        # Final update
        await progress_callback(
            current_file="Conversion complete",
            completed=completed,
            total=total_files,
            successful=successful,
            failed=failed,
            status="complete",
            results=results
        )

    def cancel_conversion(self):
        """Cancel the current batch conversion"""
        self.cancel_requested = True

    def get_supported_formats(self) -> List[str]:
        """Return list of supported file formats"""
        return [
            "pdf", "docx", "xlsx", "pptx",  # Office documents
            "jpg", "jpeg", "png", "gif", "bmp",  # Images
            "html", "htm",  # Web
            "txt", "csv", "json", "xml",  # Text formats
            "epub",  # E-books
            "mp3", "wav", "m4a",  # Audio (with transcription)
            "zip",  # Archives
            "url"  # YouTube URLs in .url files
        ]