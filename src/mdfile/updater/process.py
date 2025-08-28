import io
import re
import shlex
import subprocess
from rich.console import Console
from rich.panel import Panel

class ProcessReplacer:
    """
    Replace {{process <command>}} placeholders with the output of the command.
    Uses Rich for formatting output. Handles timeouts gracefully.
    """

    # Regex pattern for process placeholders
    PLACEHOLDER_PATTERN: re.Pattern[str] = re.compile(
        r"\{\{process\s+(.+?)\}\}", re.DOTALL
    )

    def __init__(self, timeout_sec: int = 30) -> None:
        """
        Args:
            timeout_sec (int): Timeout in seconds for command execution.
        """
        self.timeout_sec = timeout_sec

    def update(self, content: str) -> str:
        """
        Replace all process placeholders in the content with command output.

        Args:
            content (str): Markdown content containing {{process <command>}}.

        Returns:
            str: Updated content with process output inserted.
        """
        matches = list(self.PLACEHOLDER_PATTERN.finditer(content))
        new_content = content

        for match in matches:
            command = match.group(1).strip()
            old_block = match.group(0)

            string_io = io.StringIO()
            console = Console(file=string_io, width=100, highlight=False)

            try:
                args = shlex.split(command)
                result = subprocess.run(
                    args,
                    capture_output=True,
                    shell=False,
                    text=True,
                    check=True,
                    timeout=self.timeout_sec
                )

                console.print(result.stdout.strip())
                output = string_io.getvalue()
                new_block = f"```text\n{output}```"

            except subprocess.TimeoutExpired:
                console.print(
                    Panel.fit(
                        f"Command execution timed out after {self.timeout_sec} seconds",
                        title="Timeout Error",
                        style="bold red"
                    )
                )
                output = string_io.getvalue()
                new_block = f"<!--process {command}-->\n{output}\n<!--process end-->"

            new_content = new_content.replace(old_block, new_block, 1)

        return new_content


class ProcessBlockReplacer:
    """
    Replace <!--process <command>--> ... <!--process end--> blocks
    with the output of the command, formatted with Rich.
    """

    # Regex pattern for process insert blocks
    PLACEHOLDER_PATTERN: re.Pattern[str] = re.compile(
        r'^<!--process\s+(.+?)-->(.*?)<!--process end-->', re.DOTALL | re.MULTILINE
    )

    def __init__(self, timeout_sec: int = 30) -> None:
        """
        Args:
            timeout_sec (int): Timeout in seconds for command execution.
        """
        self.timeout_sec = timeout_sec

    def update(self, content: str) -> str:
        """
        Replace all process insert blocks in the content with command output.

        Args:
            content (str): Markdown content containing process insert blocks.

        Returns:
            str: Updated content with command output inserted.
        """
        matches = list(self.PLACEHOLDER_PATTERN.finditer(content))
        new_content = content

        for match in matches:
            command = match.group(1).strip()
            old_block = match.group(0)

            string_io = io.StringIO()
            console = Console(file=string_io, width=100, highlight=False)

            try:
                args = shlex.split(command)
                result = subprocess.run(
                    args,
                    capture_output=True,
                    shell=False,
                    text=True,
                    check=True,
                    timeout=self.timeout_sec
                )

                console.print(result.stdout.strip())
                output = string_io.getvalue()
                new_block = f"<!--process {command}-->\n```text\n{output}\n```\n<!--process end-->"

            except subprocess.TimeoutExpired:
                console.print(
                    Panel.fit(
                        f"Command execution timed out after {self.timeout_sec} seconds",
                        title="Timeout Error",
                        style="bold red"
                    )
                )
                output = string_io.getvalue()
                new_block = f"<!--process {command}-->\n{output}\n<!--process end-->"

            new_content = new_content.replace(old_block, new_block, 1)

        return new_content
