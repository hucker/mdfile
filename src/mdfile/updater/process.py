import io
import re
import shlex
import subprocess
from typing import ClassVar
from rich.console import Console
from rich.panel import Panel


class BaseProcessReplacer:
    """
    Base class for replacing process placeholders with command output.
    Subclasses define the regex pattern and block formatting.
    """

    PLACEHOLDER_PATTERN: ClassVar[re.Pattern[str]]

    def __init__(self, timeout_sec: int = 30) -> None:
        self.timeout_sec = timeout_sec

    def _format_success(self, command: str, output: str) -> str:
        """
        Format replacement block on successful command execution.
        Subclasses override this.
        """
        raise NotImplementedError

    def _format_timeout(self, command: str, output: str) -> str:
        """
        Format replacement block when command times out.
        Subclasses override this.
        """
        raise NotImplementedError

    def update(self, content: str) -> str:
        """
        Replace all process placeholders in content with command output.
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
                    timeout=self.timeout_sec,
                )
                console.print(result.stdout.strip())
                output = string_io.getvalue()
                new_block = self._format_success(command, output)

            except subprocess.TimeoutExpired:
                console.print(
                    Panel.fit(
                        f"Command execution timed out after "
                        f"{self.timeout_sec} seconds",
                        title="Timeout Error",
                        style="bold red",
                    )
                )
                output = string_io.getvalue()
                new_block = self._format_timeout(command, output)

            new_content = new_content.replace(old_block, new_block, 1)

        return new_content


class ProcessReplacer(BaseProcessReplacer):
    """Replace {{process <command>}} placeholders with command output."""

    PLACEHOLDER_PATTERN = re.compile(r"\{\{process\s+(.+?)\}\}", re.DOTALL)

    def _format_success(self, command: str, output: str) -> str:
        return f"```text\n{output}```"

    def _format_timeout(self, command: str, output: str) -> str:
        return f"<!--process {command}-->\n{output}\n<!--process end-->"


class ProcessBlockReplacer(BaseProcessReplacer):
    """Replace <!--process ...--> blocks with command output."""

    PLACEHOLDER_PATTERN = re.compile(
        r"^<!--process\s+(.+?)-->(.*?)<!--process end-->",
        re.DOTALL | re.MULTILINE,
    )

    def _format_success(self, command: str, output: str) -> str:
        return (
            f"<!--process {command}-->\n```text\n{output}\n```\n<!--process end-->"
        )

    def _format_timeout(self, command: str, output: str) -> str:
        return f"<!--process {command}-->\n{output}\n<!--process end-->"
