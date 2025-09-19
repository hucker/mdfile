import pytest
from mdfile.updater.validator import Tokenizer, Token, Validator

@pytest.mark.parametrize(
    "text, expected",
    [
        # --- Simple text line
        ("hello world", [Token("TEXT", "text", "hello world", 1)]),

        # --- Empty line
        ("", [Token("TEXT", "text", "", 1)]),

        # --- Whitespace line
        ("   ", [Token("TEXT", "text", "   ", 1)]),

        # --- Start shell block with command
        ('<!-- shell "ls -l" -->', [Token("START", "shell", '"ls -l"', 1)]),

        # --- End shell block
        ('<!-- shell end -->', [Token("END", "shell", None, 1)]),

        # --- Ignore start/end
        ('<!-- ignore -->', [Token("START", "ignore", None, 1)]),
        ('<!-- ignore end -->', [Token("END", "ignore", None, 1)]),

        # --- File start, command with spaces
        ('<!-- file "my file.txt" -->', [Token("START", "file", '"my file.txt"', 1)]),

        # --- Process start
        ('<!-- process "run this" -->', [Token("START", "process", '"run this"', 1)]),

        # --- Multiple lines mixed
        (
            '\n'.join([
                '<!-- shell "echo hi" -->',
                "echo hi",
                '<!-- shell end -->',
            ]),
            [
                Token("START", "shell", '"echo hi"', 1),
                Token("TEXT", "text", 'echo hi', 2),
                Token("END", "shell", None, 3),
            ],
        ),

        # --- Consecutive different blocks
        (
            '\n'.join([
                '<!-- shell "a" -->',
                '<!-- file "b.txt" -->',
                '<!-- shell end -->',
                '<!-- file end -->',
            ]),
            [
                Token("START", "shell", '"a"', 1),
                Token("START", "file", '"b.txt"', 2),
                Token("END", "shell", None, 3),
                Token("END", "file", None, 4),
            ],
        ),

        # --- Malformed tags (should be TEXT)
        ('<!-- shell -->', [Token("TEXT", "text", '<!-- shell -->', 1)]),
        ('<!-- unknown "x" -->', [Token("TEXT", "text", '<!-- unknown "x" -->', 1)]),

        # --- Ignore mixed with text
        (
            '\n'.join([
                '<!-- ignore -->',
                'pass through this',
                '<!-- ignore end -->',
                'normal text',
            ]),
            [
                Token("START", "ignore", None, 1),
                Token("TEXT", "text", 'pass through this', 2),
                Token("END", "ignore", None, 3),
                Token("TEXT", "text", 'normal text', 4),
            ],
        ),
    ],
)
def test_tokenizer_edge_cases(text, expected):
    tokenizer = Tokenizer()
    tokens = list(tokenizer.tokenize(text))
    assert tokens == expected



@pytest.mark.parametrize(
    "doc",
    [
        "plain text line",
        '<!-- shell "ls -l" -->\noutput\n<!-- shell end -->',
        '<!-- ignore -->\nanything goes\n<!-- ignore end -->',
        '<!-- file "file.txt" -->\ndata\n<!-- file end -->',
        '\n'.join([
            '<!-- shell "echo hi" -->',
            "output line",
            '<!-- shell end -->',
            '<!-- file "b.txt" -->',
            "more output",
            '<!-- file end -->',
        ]),

    ],
)
def test_validator_valid(doc):
    tokens = list(Tokenizer().tokenize(doc))
    assert Validator().validate(tokens) is True


@pytest.mark.parametrize(
    "doc, errmsg, desc",
    [
        # --- Missing command
        ('<!-- shell "" -->', "'shell' block missing command at line 1", "shell start with empty command"),

        # --- Unclosed start
        ('<!-- shell "a" -->', "Unclosed 'shell' block started at line 1", "single shell start unclosed"),

        # --- Unexpected end
        ('<!-- shell end -->', "Unexpected 'shell' end", "end without start"),

        # --- Nested blocks: file inside shell
        (
            '\n'.join([
                '<!-- shell "a" -->',
                '<!-- file "b.txt" -->',
                '<!-- shell end -->',
                '<!-- file end -->',
            ]),
            "Unexpected 'file' start at line 2",
            "nested file inside shell"
        ),

        # --- Ignore nested inside ignore
        (
            '\n'.join([
                '<!-- ignore -->',
                '<!-- ignore -->',
                'text',
                '<!-- ignore end -->',
                '<!-- ignore end -->',
            ]),
            "Unexpected 'ignore' start at line 2",
            "nested ignore blocks"
        ),

        # --- Multiple nested shell blocks
        (
            '\n'.join([
                '<!-- shell "outer" -->',
                '<!-- shell "inner" -->',
                'echo hi',
                '<!-- shell end -->',
                '<!-- shell end -->',
            ]),
            "Unexpected 'shell' start at line 2",
            "nested shell blocks"
        ),

        # --- File end without start
        ('<!-- file end -->', "Unexpected 'file' end", "file end without start"),

        # --- Mixed shell and process nested incorrectly
        (
            '\n'.join([
                '<!-- shell "x" -->',
                '<!-- process "y" -->',
                '<!-- shell end -->',
                '<!-- process end -->',
            ]),
            "Unexpected 'process' start at line 2",
            "process inside shell without proper nesting"
        ),
    ],
)
def test_validator_invalid(doc, errmsg, desc):
    """Test invalid Markdown block structures and nesting issues."""
    tokens = list(Tokenizer().tokenize(doc))
    validator = Validator()
    with pytest.raises(ValueError) as exc:
        validator.validate(tokens)
    assert errmsg in str(exc.value.args[0]), f"Failed: {desc}"

