from typing import Optional

from typing import Optional

def unquote(command: Optional[str]) -> Optional[str]:
    """
    Remove quotes from a string if it's properly quoted.

    The string must be enclosed in matching quotes:
    - Single quotes: 'text'
    - Double quotes: "text"
    - Triple single quotes: '''text'''
    - Triple double quotes:

    Args:
        command: The potentially quoted string

    Returns:
        The string without the enclosing quotes

    Raises:
        ValueError: If the string is not properly quoted
    """
    if command is None:
        return None

    # Empty string is not a valid quoted string
    if not command:
        raise ValueError("Empty string is not properly quoted")

    # Check for triple quotes first (they take precedence)
    for quote in ['"""', "'''"]:
        if len(command) >= 2 * len(quote) and command.startswith(quote) and command.endswith(quote):
            content = command[len(quote):-len(quote)]
            # Check for unescaped quotes in the content
            if quote in content:
                raise ValueError(f"String has unescaped quotes within content: {command}")
            return content

    # Check for regular quotes
    for quote in  ['"', "'"]:
        if len(command) >= 2 and command.startswith(quote) and command.endswith(quote):
            content = command[1:-1]
            # Check for unescaped quotes in the content
            i = 0
            while i < len(content):
                if content[i] == quote[0] and (i == 0 or content[i - 1] != '\\'):
                    raise ValueError(f"String has unescaped quotes within content: {command}")
                i += 1
            return content

    # If we got here, it's not properly quoted
    raise ValueError(f"String is not properly quoted: {command}")
