import pathlib
import re
from .md_factory import markdown_factory

import pathlib
import re
from typing import Optional

class FileReplacer:
    """
    Handle {{file ...}} placeholders and replace them with file contents
    converted to markdown.
    """

    PLACEHOLDER_PATTERN = r"\{\{file\s+(.+?)\}\}"

    def __init__(self, bold: Optional[str] = None, auto_break: bool = False):
        """
        Args:
            bold (Optional[str]): Comma-separated values to bold.
            auto_break (bool): Whether to auto-wrap content.
        """
        self.bold = bold
        self.auto_break = auto_break

    def update(self, content: str) -> str:
        """
        Replace {{file ...}} placeholders with file contents or warnings.

        Args:
            content (str): Markdown content containing file placeholders.

        Returns:
            str: Updated content with placeholders replaced.
        """
        placeholders = re.finditer(self.PLACEHOLDER_PATTERN, content)
        new_content = content

        for placeholder in placeholders:
            file_pattern = placeholder.group(1).strip()
            full_placeholder = placeholder.group(0)

            kwargs = {
                "bold_vals": self.bold.split(",") if self.bold else [],
                "auto_break": self.auto_break,
            }

            matching_files = list(pathlib.Path().glob(file_pattern))

            if matching_files:
                markdown_parts = []
                for file_path in matching_files:
                    file_name = str(file_path)
                    md_gen = markdown_factory(file_name, **kwargs)
                    markdown_text = md_gen.to_full_markdown()
                    markdown_parts.append(markdown_text)

                all_markdown = "\n\n".join(markdown_parts)
            else:
                all_markdown = (
                    f"**Warning:** No files found matching the pattern "
                    f"'{file_pattern}'."
                )

            new_content = new_content.replace(full_placeholder, all_markdown, 1)

        return new_content


class FileBlockInsertReplacer:
    """
    Replace <!--file <glob_pattern>--> ... <!--file end--> blocks
    with file contents converted to Markdown using a markdown factory function.
    """

    # Regex pattern for file insert blocks
    PLACEHOLDER_PATTERN: re.Pattern[str] = re.compile(
        r'<!--file\s+(.+?)-->(.*?)<!--file end-->', re.DOTALL
    )

    def __init__(self, bold: str = "", auto_break: bool = False) -> None:
        """
        Args:
            bold (str): Comma-separated values to bold.
            auto_break (bool): Whether to auto-wrap content.
        """
        self.bold_vals = bold.split(",") if bold else []
        self.auto_break = auto_break

    def update(self, content: str) -> str:
        """
        Replace all file insertion blocks in the content with Markdown content from files.

        Args:
            content (str): Markdown content containing file insert blocks.

        Returns:
            str: Updated content with file insertions.
        """
        matches = list(self.PLACEHOLDER_PATTERN.finditer(content))
        new_content = content

        for match in matches:
            glob_pattern = match.group(1).strip()
            old_block = match.group(0)

            matching_files = list(pathlib.Path().glob(glob_pattern))

            if matching_files:
                markdown_parts = []
                for file_path in matching_files:
                    file_name = str(file_path)
                    md_gen = markdown_factory(file_name, bold_vals=self.bold_vals, auto_break=self.auto_break)
                    markdown_text = md_gen.to_full_markdown()
                    markdown_parts.append(markdown_text)

                all_markdown = "\n\n".join(markdown_parts)
                new_block = f"<!--file {glob_pattern}-->\n{all_markdown}\n<!--file end-->"
            else:
                new_block = (
                    f"<!--file {glob_pattern}-->\n"
                    f"<!-- No files found matching pattern '{glob_pattern}' -->\n"
                    f"<!--file end-->"
                )

            new_content = new_content.replace(old_block, new_block, 1)

        return new_content
