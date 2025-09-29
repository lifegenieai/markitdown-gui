import re
from typing import Dict, List, Optional
from pathlib import Path


class MarkdownEnhancer:
    """
    Post-processor for enhancing MarkItDown output with proper Markdown formatting.
    Converts basic text output into well-structured, human-readable Markdown.
    """

    def __init__(self, enhancement_level: str = "standard"):
        """
        Initialize the enhancer with specified enhancement level.

        Args:
            enhancement_level: "basic", "standard", or "advanced"
        """
        self.enhancement_level = enhancement_level

    def enhance(self, content: str, file_extension: str = "", preserve_structure: bool = True) -> str:
        """
        Main enhancement method that applies all formatting improvements.

        Args:
            content: Raw text content from MarkItDown
            file_extension: Original file extension for format-specific processing
            preserve_structure: Whether to preserve existing structure

        Returns:
            Enhanced Markdown content
        """
        if not content or not content.strip():
            return content

        # Handle .md files specially
        if file_extension.lower() == '.md' and preserve_structure:
            return self._enhance_existing_markdown(content)

        # Apply progressive enhancement based on level
        enhanced = content

        # Basic enhancements (always applied)
        enhanced = self._fix_line_endings(enhanced)
        enhanced = self._enhance_headings(enhanced)
        enhanced = self._enhance_lists(enhanced)
        enhanced = self._clean_spacing(enhanced)

        if self.enhancement_level in ["standard", "advanced"]:
            enhanced = self._enhance_tables(enhanced)
            enhanced = self._enhance_links(enhanced)
            enhanced = self._enhance_emphasis(enhanced)
            enhanced = self._enhance_code_blocks(enhanced)

        if self.enhancement_level == "advanced":
            enhanced = self._enhance_structure(enhanced)
            enhanced = self._add_table_of_contents(enhanced)
            enhanced = self._optimize_readability(enhanced)

        return enhanced

    def _enhance_existing_markdown(self, content: str) -> str:
        """Enhanced processing for files that are already in Markdown format."""
        # Clean up and standardize existing Markdown
        enhanced = self._standardize_headings(content)
        enhanced = self._standardize_lists(enhanced)
        enhanced = self._clean_spacing(enhanced)
        return enhanced

    def _fix_line_endings(self, content: str) -> str:
        """Normalize line endings and remove excessive whitespace."""
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in content.split('\n')]
        return '\n'.join(lines)

    def _enhance_headings(self, content: str) -> str:
        """Convert common heading patterns to proper Markdown headings."""
        lines = content.split('\n')
        enhanced_lines = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                enhanced_lines.append('')
                continue

            # Detect heading patterns
            heading_level = self._detect_heading_level(line, i, lines)

            if heading_level > 0:
                # Clean the line and make it a proper heading
                clean_line = re.sub(r'^[#\s\-=_*]+|[#\s\-=_*]+$', '', line).strip()
                if clean_line:
                    enhanced_lines.append('#' * heading_level + ' ' + clean_line)
                else:
                    enhanced_lines.append(line)
            else:
                enhanced_lines.append(line)

        return '\n'.join(enhanced_lines)

    def _detect_heading_level(self, line: str, index: int, lines: List[str]) -> int:
        """Detect if a line should be treated as a heading and determine its level."""
        if not line.strip():
            return 0

        # Already a markdown heading
        if re.match(r'^#{1,6}\s', line):
            return 0  # Don't modify existing headings

        # ALL CAPS lines (likely headings)
        if len(line) > 3 and line.isupper() and not re.search(r'[.!?]$', line):
            return 1

        # Lines with underlines (= or -)
        if index + 1 < len(lines):
            next_line = lines[index + 1].strip()
            if re.match(r'^=+$', next_line):
                return 1
            elif re.match(r'^-+$', next_line):
                return 2

        # Lines that end with colons and are short
        if line.endswith(':') and len(line) < 60 and not line.count(':') > 2:
            return 3

        # Standalone lines that look like section headers (short, no punctuation, followed by content)
        if (len(line) < 60 and
            not re.search(r'[.!?]$', line) and
            not line.startswith(('-', '*', '+')) and
            not re.match(r'^\d+[.)]', line) and  # Don't convert numbered list items
            len(line.split()) <= 4 and  # Short phrases only
            index + 1 < len(lines)):

            # Look ahead to see what follows
            next_line = lines[index + 1].strip()

            # If directly followed by a list or content, it's likely a heading
            if (next_line and (
                next_line.startswith(('-', '*', '+')) or
                re.match(r'^\d+[.)]', next_line) or
                (len(next_line) > 15 and next_line.endswith('.')) or
                next_line.startswith('#'))):
                return 2

            # Also check if there's a blank line then a list (common pattern)
            if (index + 2 < len(lines) and
                not next_line and  # blank line
                lines[index + 2].strip() and
                lines[index + 2].strip().startswith(('-', '*', '+'))):
                return 2

        # First significant line of document
        if index == 0 or (index < 5 and all(not l.strip() for l in lines[:index])):
            if len(line) < 80 and not line.endswith('.'):
                return 1

        return 0

    def _standardize_headings(self, content: str) -> str:
        """Standardize existing Markdown headings."""
        lines = content.split('\n')
        enhanced_lines = []

        for line in lines:
            # Fix heading formatting
            heading_match = re.match(r'^(#{1,6})\s*(.*)', line)
            if heading_match:
                level = heading_match.group(1)
                text = heading_match.group(2).strip()
                if text:
                    enhanced_lines.append(f"{level} {text}")
                else:
                    enhanced_lines.append(line)
            else:
                enhanced_lines.append(line)

        return '\n'.join(enhanced_lines)

    def _enhance_lists(self, content: str) -> str:
        """Convert text patterns to proper Markdown lists."""
        lines = content.split('\n')
        enhanced_lines = []

        for line in lines:
            original_line = line
            line = line.strip()

            if not line:
                enhanced_lines.append('')
                continue

            # Detect list patterns
            list_item = self._detect_list_item(line)
            if list_item:
                enhanced_lines.append(list_item)
            else:
                enhanced_lines.append(original_line)

        return '\n'.join(enhanced_lines)

    def _detect_list_item(self, line: str) -> Optional[str]:
        """Detect and format list items."""
        # Already proper Markdown list
        if re.match(r'^[\s]*[-*+]\s', line) or re.match(r'^[\s]*\d+\.\s', line):
            return None

        # Numbered list patterns
        numbered_match = re.match(r'^(\d+)[.)]\s*(.*)', line)
        if numbered_match:
            return f"{numbered_match.group(1)}. {numbered_match.group(2)}"

        # Bullet list patterns
        bullet_patterns = [
            r'^[•·▪▫‣⁃]\s*(.*)',  # Various bullet characters
            r'^[-–—]\s*(.*)',      # Dashes
            r'^\*\s*(.*)',         # Asterisks (not already formatted)
        ]

        for pattern in bullet_patterns:
            match = re.match(pattern, line)
            if match:
                return f"- {match.group(1)}"

        return None

    def _standardize_lists(self, content: str) -> str:
        """Standardize existing Markdown lists."""
        lines = content.split('\n')
        enhanced_lines = []

        for line in lines:
            # Standardize list formatting
            if re.match(r'^[\s]*[*+]\s', line):
                # Convert + and * to -
                enhanced_lines.append(re.sub(r'^([\s]*)[*+](\s)', r'\1-\2', line))
            else:
                enhanced_lines.append(line)

        return '\n'.join(enhanced_lines)

    def _enhance_tables(self, content: str) -> str:
        """Detect and enhance table formatting."""
        lines = content.split('\n')
        enhanced_lines = []
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Detect potential table by looking for patterns with | or multiple tabs/spaces
            if self._looks_like_table_row(line):
                table_lines = []
                j = i

                # Collect consecutive table-like lines
                while j < len(lines) and self._looks_like_table_row(lines[j].strip()):
                    table_lines.append(lines[j].strip())
                    j += 1

                if len(table_lines) >= 2:  # Need at least header + one row
                    formatted_table = self._format_table(table_lines)
                    enhanced_lines.extend(formatted_table)
                    i = j
                else:
                    enhanced_lines.append(lines[i])
                    i += 1
            else:
                enhanced_lines.append(lines[i])
                i += 1

        return '\n'.join(enhanced_lines)

    def _looks_like_table_row(self, line: str) -> bool:
        """Check if a line looks like it could be part of a table."""
        if not line or line.startswith('#'):
            return False

        # Has multiple | characters
        if line.count('|') >= 2:
            return True

        # Has multiple tab-separated values
        if '\t' in line and len(line.split('\t')) >= 3:
            return True

        # Has multiple values separated by 2+ spaces
        if len(re.split(r'\s{2,}', line)) >= 3:
            return True

        return False

    def _format_table(self, table_lines: List[str]) -> List[str]:
        """Format detected table lines into proper Markdown table."""
        if not table_lines:
            return []

        # Parse table data
        rows = []
        for line in table_lines:
            if '|' in line:
                # Split by | and clean up
                cells = [cell.strip() for cell in line.split('|')]
                # Remove empty cells at start/end
                if cells and not cells[0]:
                    cells = cells[1:]
                if cells and not cells[-1]:
                    cells = cells[:-1]
                rows.append(cells)
            elif '\t' in line:
                # Split by tabs
                rows.append([cell.strip() for cell in line.split('\t')])
            else:
                # Split by multiple spaces
                rows.append([cell.strip() for cell in re.split(r'\s{2,}', line)])

        if not rows:
            return table_lines

        # Ensure all rows have the same number of columns
        max_cols = max(len(row) for row in rows)
        for row in rows:
            while len(row) < max_cols:
                row.append('')

        # Format as Markdown table
        formatted = []

        # Header row
        if rows:
            header = '| ' + ' | '.join(rows[0]) + ' |'
            formatted.append(header)

            # Separator row
            separator = '|' + '---|' * max_cols
            formatted.append(separator)

            # Data rows
            for row in rows[1:]:
                data_row = '| ' + ' | '.join(row) + ' |'
                formatted.append(data_row)

        return formatted

    def _enhance_links(self, content: str) -> str:
        """Enhance link formatting."""
        # Convert bare URLs to proper Markdown links
        url_pattern = r'\b(https?://[^\s<>"{}|\\^`\[\]]+)'
        content = re.sub(url_pattern, r'[\1](\1)', content)

        # Fix malformed links
        content = re.sub(r'\[([^\]]+)\]\s*\(([^)]+)\)', r'[\1](\2)', content)

        return content

    def _enhance_emphasis(self, content: str) -> str:
        """Enhance bold and italic formatting."""
        # Convert **text** patterns that might be malformed
        content = re.sub(r'\*{3,}([^*]+)\*{3,}', r'**\1**', content)  # Multiple asterisks to bold
        content = re.sub(r'_{3,}([^_]+)_{3,}', r'**\1**', content)    # Multiple underscores to bold

        # Ensure proper spacing around emphasis
        content = re.sub(r'([^\s])\*\*([^*])', r'\1 **\2', content)
        content = re.sub(r'([^*])\*\*([^\s])', r'\1** \2', content)

        return content

    def _enhance_code_blocks(self, content: str) -> str:
        """Enhance code block formatting."""
        lines = content.split('\n')
        enhanced_lines = []
        in_code_block = False

        for line in lines:
            # Detect code blocks by indentation or backticks
            if line.strip().startswith('```'):
                enhanced_lines.append(line)
                in_code_block = not in_code_block
            elif not in_code_block and (line.startswith('    ') or line.startswith('\t')):
                # Convert indented code to fenced code blocks if multiple lines
                enhanced_lines.append(line)
            else:
                # Convert inline code patterns
                enhanced_line = re.sub(r'`([^`]+)`', r'`\1`', line)  # Ensure proper backticks
                enhanced_lines.append(enhanced_line)

        return '\n'.join(enhanced_lines)

    def _clean_spacing(self, content: str) -> str:
        """Clean up spacing and line breaks."""
        # Remove excessive blank lines (more than 2 consecutive)
        content = re.sub(r'\n{3,}', '\n\n', content)

        # Ensure proper spacing around headings and sections
        lines = content.split('\n')
        enhanced_lines = []

        for i, line in enumerate(lines):
            current_line = line.strip()

            # Add blank line before headings (except at start)
            if current_line.startswith('#') and i > 0:
                if enhanced_lines and enhanced_lines[-1].strip():
                    enhanced_lines.append('')

            enhanced_lines.append(line)

            # Add blank line after headings if not present
            if current_line.startswith('#') and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith('#'):
                    enhanced_lines.append('')

            # Add spacing after paragraphs that end with periods
            elif (current_line.endswith('.') and
                  i + 1 < len(lines) and
                  lines[i + 1].strip() and
                  not lines[i + 1].strip().startswith(('#', '-', '*', '+')) and
                  not re.match(r'^\d+\.', lines[i + 1].strip())):
                # Check if next line starts a new paragraph/section
                next_line = lines[i + 1].strip()
                if len(next_line) > 20 or next_line[0].isupper():
                    enhanced_lines.append('')

        return '\n'.join(enhanced_lines)

    def _enhance_structure(self, content: str) -> str:
        """Advanced structural enhancements."""
        # Add proper document structure
        lines = content.split('\n')

        # Find the main title (first heading)
        title_found = False
        for i, line in enumerate(lines):
            if line.strip().startswith('# ') and not title_found:
                title_found = True
                # Ensure title is followed by a blank line
                if i + 1 < len(lines) and lines[i + 1].strip():
                    lines.insert(i + 1, '')
                break

        return '\n'.join(lines)

    def _add_table_of_contents(self, content: str) -> str:
        """Add a table of contents for documents with multiple headings."""
        lines = content.split('\n')
        headings = []

        # Extract headings
        for line in lines:
            if re.match(r'^#{1,6}\s', line):
                level = len(line) - len(line.lstrip('#'))
                title = line.strip('#').strip()
                headings.append((level, title))

        # Only add TOC if there are multiple headings
        if len(headings) >= 3:
            toc_lines = ['## Table of Contents', '']
            for level, title in headings:
                if level == 1:
                    continue  # Skip main title
                indent = '  ' * (level - 2)
                anchor = title.lower().replace(' ', '-').replace(':', '')
                toc_lines.append(f"{indent}- [{title}](#{anchor})")

            toc_lines.extend(['', '---', ''])

            # Insert TOC after first heading
            for i, line in enumerate(lines):
                if line.strip().startswith('# '):
                    # Find next blank line or heading
                    insert_pos = i + 1
                    while insert_pos < len(lines) and lines[insert_pos].strip() and not lines[insert_pos].startswith('#'):
                        insert_pos += 1
                    insert_pos += 1  # Add one more line for spacing

                    lines[insert_pos:insert_pos] = toc_lines
                    break

        return '\n'.join(lines)

    def _optimize_readability(self, content: str) -> str:
        """Final readability optimizations."""
        # Ensure consistent paragraph spacing
        content = re.sub(r'([.!?])\n([A-Z])', r'\1\n\n\2', content)

        # Clean up any remaining formatting issues
        content = re.sub(r'\n{4,}', '\n\n\n', content)  # Max 3 consecutive newlines

        return content.strip() + '\n'  # Ensure file ends with newline