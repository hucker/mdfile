"""
Process replacer module.

Provides classes for replacing process placeholders or blocks in Markdown
content with the output of shell commands. Supports both inline placeholders
(`{{process ...}}`) and block placeholders (`<!--process ...--> ... <!--process end-->`).
Handles timeouts gracefully using Rich formatting.
"""

import io
import re
import shlex
import subprocess
from abc import ABC, abstractmethod
from typing import ClassVar

from rich.console import Console
from rich.panel import Panel

from updater.str_utils import unquote


class BaseProcessReplacer(ABC):
    """
    Base class for replacing process placeholders with command output.

    Subclasses must define:
      * PLACEHOLDER_PATTERN: Regex pattern to locate placeholders.
      * _format_success: Method to format output on successful execution.
      * _format_timeout: Method to format output on timeout.
    """

    PLACEHOLDER_PATTERN: ClassVar[re.Pattern[str]]

    def __init__(self, timeout_sec: int = 30) -> None:
        """
        Initialize a base process replacer.

        Args:
            timeout_sec (int): Maximum seconds to wait for command execution.
        """
        self.timeout_sec: int = timeout_sec

    @abstractmethod
    def _format_success(self, command: str, output: str) -> str:
        """
        Format a replacement block for successful command execution.

        Args:
            command (str): Command that was executed.
            output (str): Captured standard output of the command.

        Returns:
            str: Formatted replacement block.
        """
        ...

    @abstractmethod
    def _format_timeout(self, command: str, output: str) -> str:
        """
        Format a replacement block for commands that timed out.

        Args:
            command (str): Command that timed out.
            output (str): Partial captured output before timeout.

        Returns:
            str: Formatted replacement block.
        """
        ...

    def update(self, content: str) -> str:
        """
        Replace all process placeholders in the content with command output.

        Args:
            content (str): Markdown content containing placeholders.

        Returns:
            str: Updated content with command outputs inserted.
        """
        matches: list[re.Match[str]] = list(self.PLACEHOLDER_PATTERN.finditer(content))
        new_content: str = content

        for match in matches:
            command: str = match.group(1).strip()
            command = unquote(command)
            old_block: str = match.group(0)

            string_io = io.StringIO()
            console = Console(file=string_io, width=100, highlight=False)

            try:
                args: list[str] = shlex.split(command)
                result = subprocess.run(
                    args,
                    capture_output=True,
                    shell=False,
                    text=True,
                    check=True,
                    timeout=self.timeout_sec,
                )
                console.print(result.stdout.strip())
                output: str = string_io.getvalue()
                new_block: str = self._format_success(command, output)

            except subprocess.TimeoutExpired:
                console.print(
                    Panel.fit(
                        f"Command execution timed out after {self.timeout_sec} seconds",
                        title="Timeout Error",
                        style="bold red",
                    )
                )
                output = string_io.getvalue()
                new_block = self._format_timeout(command, output)

            new_content = new_content.replace(old_block, new_block, 1)

        return new_content


class ProcessReplacer(BaseProcessReplacer):
    """
    Replace {{process <command>}} placeholders with command output.

    Example:
        Input: "Run a command: {{process echo hello}}"
        Output: "Run a command: ```text\nhello```"
    """

    PLACEHOLDER_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"\{\{process\s+(.+?)\}\}", re.DOTALL
    )

    def _format_success(self, command: str, output: str) -> str:
        """Format successful command output as inline Markdown code block."""
        return f"```text\n{output}```"

    def _format_timeout(self, command: str, output: str) -> str:
        """Format timed-out command with comment markers."""
        return f'<!--process "{command}"-->\n{output}\n<!--process end-->'


class ProcessBlockReplacer(BaseProcessReplacer):
    """
    Replace <!--process ...--> blocks with command output.

    Example:
        Input:
            <!--process echo hello-->
            old content
            <!--process end-->

        Output:
            <!--process echo hello-->
            ```text
            hello
            ```
            <!--process end-->
    """

    PLACEHOLDER_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^<!--process\s+(.+?)-->(.*?)<!--process end-->",
        re.DOTALL | re.MULTILINE,
    )

    def _format_success(self, command: str, output: str) -> str:
        """Format successful command output as a full block with markers."""
        return f'<!--process "{command}"-->\n```text\n{output}\n```\n<!--process end-->'

    def _format_timeout(self, command: str, output: str) -> str:
        """Format timed-out command as a block with comment markers."""
        return f'<!--process "{command}"-->\n{output}\n<!--process end-->'


class ShellReplacer(BaseProcessReplacer):
    """Replace {{shell <command>}} placeholders with shell-style output."""

    PLACEHOLDER_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"\{\{shell\s+(.+?)\}\}", re.DOTALL
    )

    def __init__(self, timeout_sec: int = 30, lang: str = "bash") -> None:
        """
        Args:
            timeout_sec (int): Maximum seconds to wait for command execution.
            lang (str): Markdown identifier for the code block (default 'bash').
        """
        super().__init__(timeout_sec)
        self.lang: str = lang

    def _format_success(self, command: str, output: str) -> str:
        return f"```{self.lang}\n>> {command}\n{output}\n```"

    def _format_timeout(self, command: str, output: str) -> str:
        return f'<!--shell "{command}"-->\n{output}\n<!--shell end-->'


class ShellBlockReplacer(BaseProcessReplacer):
    """Replace <!--shell ...--> blocks with shell-style output."""

    PLACEHOLDER_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^<!--shell\s+(.+?)-->(.*?)<!--shell end-->",
        re.DOTALL | re.MULTILINE,
    )

    def __init__(self, timeout_sec: int = 30, lang: str = "bash") -> None:
        """
        Args:
            timeout_sec (int): Maximum seconds to wait for command execution.
            lang (str): Markdown identifier for the code block (default 'bash').
        """
        super().__init__(timeout_sec)
        self.lang: str = lang

    def _format_success(self, command: str, output: str) -> str:
        return f'<!--shell "{command}"-->\n```{self.lang}\n>> {command}\n{output}\n```\n<!--shell end-->'

    def _format_timeout(self, command: str, output: str) -> str:
        return f'<!--shell "{command}"-->\n{output}\n<!--shell end-->'
