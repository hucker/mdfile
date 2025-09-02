import re

class BlockValidator:
    """
    Validate shell, file, process, and ignore blocks in markdown content.
    """

    BLOCK_TYPES = ("shell", "file", "process")
    IGNORE = "ignore"

    START_PATTERN = re.compile(r"<!--\s*(shell|file|process)\s*(.*?)\s*-->")
    END_PATTERN = re.compile(r"<!--\s*(shell|file|process)\s*end\s*-->")
    IGNORE_PATTERN = re.compile(r"<!--\s*ignore\s*-->.*?<!--\s*ignore\s*end\s*-->", re.DOTALL)

    def preprocess_ignore(self, content: str) -> str:
        """
        Replace ignore blocks with the same number of newlines to preserve line numbers.
        Raise error for nested ignores.
        """
        def repl(match: re.Match) -> str:
            inner = match.group(0)
            if re.search(r"<!--\s*ignore\s*-->", inner[1:-1]):
                raise ValueError("Unexpected ignore tag")
            return "\n" * inner.count("\n")
        return re.sub(self.IGNORE_PATTERN, repl, content)

    def validate(self, content: str) -> bool:
        """
        Validate shell, file, and process blocks in the given content.
        Raises ValueError for any malformed or unexpected blocks.
        """
        content = self.preprocess_ignore(content)
        lines = content.splitlines()
        current_block = None
        start_lineno = None

        for idx, line in enumerate(lines, start=1):
            # check start tag first
            start_match = self.START_PATTERN.search(line)
            if start_match:
                block_type, command = start_match.groups()
                if current_block:
                    raise ValueError(f"Repeated {block_type} start at line {idx}")
                if not command.strip():  # catch missing command/text immediately
                    raise ValueError(f"{block_type} block missing required command/text")
                current_block = block_type
                start_lineno = idx
                continue

            # check end tag
            end_match = self.END_PATTERN.search(line)
            if end_match:
                block_type = end_match.group(1)
                if current_block != block_type:
                    # end tag without a matching start
                    raise ValueError(f"Unexpected {block_type} end")
                current_block = None
                start_lineno = None
                continue

        if current_block:
            raise ValueError(f"Unclosed {current_block} block started at line {start_lineno}")

        return True


