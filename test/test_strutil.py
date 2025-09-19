import pytest
from typing import Optional

# Import the function to test
# Assuming it's in a module like str_utils
from mdfile.updater.str_utils import unquote


def test_unquote_none():
    """Test that None input returns None output."""
    assert unquote(None) is None


def test_unquote_double_quotes():
    """Test unquoting with double quotes."""
    assert unquote('"hello"') == "hello"
    assert unquote('"hello world"') == "hello world"
    assert unquote('"123"') == "123"
    assert unquote('""') == ""


def test_unquote_single_quotes():
    """Test unquoting with single quotes."""
    assert unquote("'hello'") == "hello"
    assert unquote("'hello world'") == "hello world"
    assert unquote("'123'") == "123"
    assert unquote("''") == ""


def test_unquote_triple_double_quotes():
    """Test unquoting with triple double quotes."""
    assert unquote('"""hello"""') == "hello"
    assert unquote('"""hello world"""') == "hello world"
    assert unquote('"""multiline\nstring"""') == "multiline\nstring"
    assert unquote('""""""') == ""


def test_unquote_triple_single_quotes():
    """Test unquoting with triple single quotes."""
    assert unquote("'''hello'''") == "hello"
    assert unquote("'''hello world'''") == "hello world"
    assert unquote("'''multiline\nstring'''") == "multiline\nstring"
    assert unquote("''''''") == ""


def test_unquote_nested_quotes():
    """Test unquoting with nested quotes."""
    assert unquote('"This has \'single\' quotes"') == "This has 'single' quotes"
    assert unquote("'This has \"double\" quotes'") == 'This has "double" quotes'
    assert unquote('"""This has "double" and \'single\' quotes"""') == 'This has "double" and \'single\' quotes'
    assert unquote("'''This has 'single' and \"double\" quotes'''") == "This has 'single' and \"double\" quotes"


def test_unquote_errors():
    """Test that improper quoting raises ValueError."""
    with pytest.raises(ValueError):
        unquote("unquoted string")

    with pytest.raises(ValueError):
        unquote('"mismatched quote')

    with pytest.raises(ValueError):
        unquote('mismatched quote"')

    with pytest.raises(ValueError):
        unquote('"""mismatched triple quote"')

    with pytest.raises(ValueError):
        unquote('"quoted string with extra"characters"')


def test_unquote_special_cases():
    """Test unquoting with special edge cases."""
    # Single character cases
    with pytest.raises(ValueError):
        unquote('"')

    with pytest.raises(ValueError):
        unquote("'")

    # Empty string (not quoted)
    with pytest.raises(ValueError):
        unquote("")

    # Quotes with only whitespace
    assert unquote('" "') == " "
    assert unquote("' '") == " "
    assert unquote('"""   """') == "   "
    assert unquote("'''   '''") == "   "


def test_unquote_with_escapes():
    """Test unquoting with escape sequences."""
    # The function doesn't handle escape sequences specially,
    # so these tests verify the expected behavior
    assert unquote(r'"escaped \"quotes\""') == r'escaped \"quotes\"'
    assert unquote(r"'escaped \'quotes\''") == r"escaped \'quotes\'"

def test_unquote_embedded_quotes():
    """Test that strings with embedded unescaped quotes raise ValueError."""
    # Double quotes with embedded double quote
    with pytest.raises(ValueError):
        unquote('"This has an "embedded" quote"')

    # Single quotes with embedded single quote
    with pytest.raises(ValueError):
        unquote("'This has an 'embedded' quote'")

    # Triple double quotes with embedded triple double quotes
    with pytest.raises(ValueError):
        unquote('"""This has an """embedded""" triple quote"""')

    # Triple single quotes with embedded triple single quotes
    with pytest.raises(ValueError):
        unquote("'''This has an '''embedded''' triple quote'''")


