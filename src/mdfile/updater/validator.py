import re

BLOCK_TYPES = ["ignore", "file", "shell", "process"]

def validate_blocks(content: str) -> bool:
    """
    Validate that all block start/end tags match in the content.

    Raises:
        ValueError: If any block is mismatched.
    """
    # Build combined regex for all blocks
    pattern = re.compile(
        r"<!--\s*(ignore|file|shell|process)\s*-->|<!--\s*(ignore|file|shell|process)\s*end\s*-->",
        re.IGNORECASE
    )

    stack = []
    pos = 0
    while True:
        match = pattern.search(content, pos)
        if not match:
            break

        start_tag, end_tag = match.groups()
        block_type = start_tag or end_tag
        token = match.group(0)

        # Ignore content inside ignore blocks
        if stack and stack[-1] == "ignore" and start_tag != "ignore" and end_tag != "ignore":
            pos = match.end()
            continue

        if start_tag:
            stack.append(block_type.lower())
        elif end_tag:
            if not stack:
                msg = f"Unexpected <!-- {block_type} end --> at position {match.start()}"
                raise ValueError(msg)
            last = stack.pop()
            if last != block_type.lower():
                msg = f"Mismatched block: opened {last}, closed {block_type} at position {match.start()}"
                raise ValueError(msg)
        pos = match.end()

    if stack:
        raise ValueError(f"Unclosed block(s): {stack}")

    return True