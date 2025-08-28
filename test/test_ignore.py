import pytest
from mdfile.updater.ignore import IgnoreBlocks  # replace with actual import path


def test_basic_extract_and_restore():
    content = """Keep
<!-- ignore -->
Stuff
<!-- ignore end -->
Keep"""

    ignores = IgnoreBlocks()
    extracted = ignores.extract(content)

    # token should be present
    assert ignores.token in extracted
    # ignore block should be removed from extracted
    assert "Stuff" not in extracted

    restored = ignores.restore(extracted)
    assert restored == content


def test_multiple_ignore_blocks():
    content = """A
<!-- ignore -->X<!-- ignore end -->
B
<!-- ignore -->Y<!-- ignore end -->
C"""

    ignores = IgnoreBlocks()
    extracted = ignores.extract(content)

    # two tokens must be present
    assert extracted.count(ignores.token) == 2
    assert "X" not in extracted
    assert "Y" not in extracted
    assert "C" in extracted
    assert "A" in extracted
    assert "B" in extracted

    restored = ignores.restore(extracted)
    assert restored == content


def test_reserved_token_in_input_raises():
    ignores = IgnoreBlocks()
    content = f"Some text with {ignores.token} already inside"

    with pytest.raises(ValueError, match="Reserved ignore token"):
        ignores.extract(content)


def test_restore_with_missing_token_raises():
    content = """Start
<!-- ignore -->Hidden<!-- ignore end -->
End"""

    ignores = IgnoreBlocks()
    extracted = ignores.extract(content)

    # Manually drop the token
    bad_content = extracted.replace(ignores.token, "")

    with pytest.raises(ValueError, match="Missing token"):
        ignores.restore(bad_content)


def test_restore_with_extra_token_unchanged():
    """If restore runs when no ignores exist, should just return unchanged."""
    ignores = IgnoreBlocks()
    content = "Plain text, no ignores here"

    extracted = ignores.extract(content)
    # No blocks, so extract == content
    assert extracted == content

    restored = ignores.restore(extracted)
    assert restored == content
