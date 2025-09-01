"""
File replacer module.

Provides classes for replacing file placeholders or blocks within markdown
content with the corresponding file contents rendered via a markdown factory.
Supports both inline placeholders (`{{file ...}}`) and block placeholders
(`<!--file ...--> ... <!--file end-->`).
"""

import pathlib
import re
from abc import ABC, abstractmethod
from typing import ClassVar
from to_md.md_factory import markdown_factory

class BaseReplacer(ABC):
    """
    Base class for replacing file placeholders or blocks with markdown content.

    Subclasses must define:
      * PLACEHOLDER_PATTERN: Regex pattern used to locate placeholders.
      * _format_success: Method to format output when files are found.
      * _format_failure: Method to format output when no files are found.
    """

    PLACEHOLDER_PATTERN: ClassVar[re.Pattern[str]]

    def __init__(self, bold: str | None = None, auto_break: bool = False,cfg:dict[str,str]=None) -> None:
        """
        Initialize a base file replacer.

        Args:
            bold (str | None): Comma-separated values that should be bolded.
            auto_break (bool): Whether to automatically wrap long lines.
        """
        self.cfg = {} or cfg
        self.bold_vals: list[str] = bold.split(",") if bold else []
        self.auto_break: bool = auto_break

    @abstractmethod
    def _format_success(self, pattern: str, output: str) -> str:
        """
        Format a block when matching files are found.

        Args:
            pattern (str): File glob pattern.
            output (str): Combined markdown content for all matching files.

        Returns:
            str: Formatted replacement block.
        """
        ...

    @abstractmethod
    def _format_failure(self, pattern: str) -> str:
        """
        Format a block when no matching files are found.

        Args:
            pattern (str): File glob pattern.

        Returns:
            str: Formatted replacement block indicating failure.
        """
        ...

    def validate(self,cfg:dict|None=None):
        """
        Validate the configuration for the updater.

        It is expected that more complex replacers will override this method.
        """
        if not cfg:
            return True
        return True

    def update(self, content: str) -> str:
        """
        Replace all file placeholders or blocks in the content.

        Args:
            content (str): Markdown content containing placeholders.

        Returns:
            str: Updated markdown content with placeholders replaced.
        """
        matches: list[re.Match[str]] = list(self.PLACEHOLDER_PATTERN.finditer(content))
        new_content: str = content

        for match in matches:
            file_pattern: str = match.group(1).strip()
            old_block: str = match.group(0)

            matching_files: list[pathlib.Path] = list(pathlib.Path().glob(file_pattern))

            if matching_files:
                # Generate markdown for all matched files using a comprehension
                markdown_parts: list[str] = [
                    markdown_factory(
                        str(file_path),
                        bold_vals=self.bold_vals,
                        auto_break=self.auto_break
                    ).to_full_markdown()
                    for file_path in matching_files
                ]

                replacement: str = self._format_success(
                    file_pattern, "\n\n".join(markdown_parts)
                )
            else:
                replacement = self._format_failure(file_pattern)

            new_content = new_content.replace(old_block, replacement, 1)

        return new_content


class FileReplacer(BaseReplacer):
    """
    Replace {{file ...}} placeholders with file contents.

    Example:
        Input: "Here is a file: {{file example.txt}}"
        Output: "Here is a file: <markdown for example.txt>"
    """

    PLACEHOLDER_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"\{\{file\s+(.+?)\}\}")

    def _format_success(self, pattern: str, output: str) -> str:
        """
        Format replacement when files are found.

        Args:
            pattern (str): File glob pattern.
            output (str): Markdown text for matched files.

        Returns:
            str: Markdown content without extra wrapping.
        """
        return output

    def _format_failure(self, pattern: str) -> str:
        """
        Format replacement when no files are found.

        Args:
            pattern (str): File glob pattern.

        Returns:
            str: Warning message in markdown.
        """
        return f"**Warning:** No files found matching the pattern '{pattern}'."


class FileBlockInsertReplacer(BaseReplacer):
    """
    Replace <!--file ...--> ... <!--file end--> blocks with file contents.

    Example:
        Input:
            <!--file example.txt-->
            old stuff
            <!--file end-->

        Output:
            <!--file example.txt-->
            <markdown for example.txt>
            <!--file end-->
    """

    PLACEHOLDER_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"<!--file\s+(.+?)-->(.*?)<!--file end-->",
        re.DOTALL,
    )

    def _format_success(self, pattern: str, output: str) -> str:
        """
        Format replacement when files are found.

        Args:
            pattern (str): File glob pattern.
            output (str): Markdown text for matched files.

        Returns:
            str: Wrapped block with file markers.
        """
        return f"<!--file {pattern}-->\n{output}\n<!--file end-->"

    def _format_failure(self, pattern: str) -> str:
        """
        Format replacement when no files are found.

        Args:
            pattern (str): File glob pattern.

        Returns:
            str: Block with a no-file-found comment.
        """
        return (
            f"<!--file {pattern}-->\n"
            f"<!-- No files found matching pattern '{pattern}' -->\n"
            f"<!--file end-->"
        )
