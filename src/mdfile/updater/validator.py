import re
from dataclasses import dataclass
from typing import Optional, Iterator,Iterable


@dataclass
class Token:
    """Represents a parsed tag or text line from Markdown-like input."""
    kind: str             # "START", "END", "TEXT"
    block_type: str       # "shell", "file", "process", "ignore", "text"
    command: Optional[str]
    line: int


class Tokenizer:
    """Convert markdown-like tags into a stream of Token objects."""

    TAG_RE = r"""
        ^\s*<!--\s*                                      # HTML opener
        (?:
            (?P<start>(shell|file|process))\s+(?P<cmd>(?:"[^"]*"|'[^']*'))\s*  # start with command (quotes included)
          | (?P<ignore_start>ignore)\s*                                         # ignore start
          | (?P<end>(shell|file|process))\s+end\s*                             # end
          | (?P<ignore_end>ignore)\s+end\s*                                    # ignore end
        )
        -->\s*$                                          # HTML closer
        """

    def __init__(self,grammar:str|None=None) -> None:
        self.grammar=re.compile(self.TAG_RE or grammar,re.VERBOSE)

    def tokenize(self, text: str) -> Iterator[Token]:
        """
        Yield Token objects for each recognized tag or text line.
        """
        for lineno, line in enumerate(text.splitlines() or [""], start=1):
            m = self.grammar.match(line)
            if m:
                if m.group("start"):
                    yield Token("START", m.group("start"), m.group("cmd"), lineno)
                elif m.group("ignore_start"):
                    yield Token("START", "ignore", None, lineno)
                elif m.group("end"):
                    yield Token("END", m.group("end"), None, lineno)
                elif m.group("ignore_end"):
                    yield Token("END", "ignore", None, lineno)
            else:
                yield Token("TEXT", "text", line, lineno)






class Validator:
    """Validate token streams for markdown-like blocks."""

    def __init__(self) -> None:
        self.current_block: str | None = None
        self.start_line: int = 0
        self.last_error: str = ""
        self.last_error_line: int = 0

    def raise_error(self, msg: str, lineno: int) -> None:
        """Record and raise a validation error."""
        self.last_error = msg
        self.last_error_line = lineno
        raise ValueError(msg)

    def validate(self, tokens: Iterable[Token]) -> bool:
        """Validate the token stream, raising ValueError on first structural error."""
        for token in tokens:
            if token.kind == "START":
                if self.current_block:
                    self.raise_error(
                        f"Unexpected '{token.block_type}' start at line {token.line}, "
                        f"'{self.current_block}' not closed",
                        token.line,
                    )
                if token.block_type in ("shell", "file", "process"):
                    if not token.command or not token.command.strip(' \'"'):
                        self.raise_error(
                            f"'{token.block_type}' block missing command at line {token.line}",
                            token.line,
                        )

                self.current_block = token.block_type
                self.start_line = token.line

            elif token.kind == "END":
                if not self.current_block:
                    self.raise_error(
                        f"Unexpected '{token.block_type}' end at line {token.line}",
                        token.line,
                    )
                if token.block_type != self.current_block:
                    self.raise_error(
                        f"Mismatched end: '{token.block_type}' at line {token.line}, "
                        f"expected '{self.current_block}' end",
                        token.line,
                    )
                self.current_block = None
                self.start_line = 0

        if self.current_block:
            self.raise_error(
                f"Unclosed '{self.current_block}' block started at line {self.start_line}",
                self.start_line,
            )

        return True
