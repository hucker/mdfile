import re
import secrets


class IgnoreBlocks:
    """
    Manage <!-- ignore --> ... <!-- ignore end --> blocks in markdown text.

    Extracts blocks and replaces them with tokens like {{IGNORE_ab12cd34}}.
    Later restores them in place.

    This allows for markdown to have blocks that are ignored by the markdown
    tool.  This is very useful for times when you are trying to explaing how
    the markdown tool itself works, so you will want to display markdown
    that would be processed.

    """

    # Matches <!-- ignore --> ... <!-- ignore end --> blocks in markdown.
    #
    # Details:
    #   <!--\s*ignore\s*-->      : opening tag, allows extra whitespace
    #   (.*?)                    : lazily capture everything inside the block
    #   <!--\s*ignore\s*end\s*-->: closing tag, also whitespace-tolerant
    #
    # Flags:
    #   re.DOTALL     : let '.' match across multiple lines
    #   re.IGNORECASE : accept "IGNORE", "Ignore", "ignore", etc.
    #
    # This ensures whole ignore blocks (including the tags) are captured
    # as match.group(0), with the inner text alone in match.group(1).
    BLOCK_PATTERN: re.Pattern[str] = re.compile(
        r"<!--\s*ignore\s*-->(.*?)<!--\s*ignore\s*end\s*-->",
        re.DOTALL | re.IGNORECASE,
    )


    def __init__(self) -> None:
        self._ignores: list[str] = []
        # Create one unique token for this run
        self._token: str = f"IGNORE_{secrets.token_hex(8)}"

    @property
    def token(self) -> str:
        """Return the full {{IGNORE_xxx}} token string."""
        return f"{{{{{self._token}}}}}"

    def extract(self, content: str) -> str:
        """
        Replace ignore blocks with the token and store them internally.

        Args:
            content (str): Markdown input text.

        Returns:
            str: Markdown with ignore blocks replaced by token.

        Raises:
            ValueError: If the token already appears in content.
        """
        if self.token in content:
            raise ValueError("Reserved ignore token already present in input markdown")

        def _replacer(match: re.Match[str]) -> str:
            self._ignores.append(match.group(0))
            return self.token

        return self.BLOCK_PATTERN.sub(_replacer, content)

    def restore(self, content: str) -> str:
        """
        Replace tokens with their original ignore blocks.

        Args:
            content (str): Markdown text with ignore tokens.

        Returns:
            str: Markdown text with original ignore blocks restored.

        Raises:
            ValueError: If tokens are missing during restore.
        """
        for block in self._ignores:
            if self.token not in content:
                raise ValueError("Missing token in content during restore")
            content = content.replace(self.token, block, 1)
        return content
