import pytest
from mdfile.updater.validator import validate_blocks

@pytest.mark.parametrize(
    "content, msg",
    [
        # Unmatched end block
        ("A\n<!-- file end -->", "File block ended without a start"),
        # Repeated start block without end
        ("<!-- ignore -->X<!-- ignore -->", "Ignore block repeated without ending"),
        # Nested blocks of different types
        ("<!-- file -->X<!-- process end -->", "Nested blocks closed incorrectly"),
        # Multiple unmatched
        ("<!-- shell -->do<!-- shell -->again", "Shell block repeated without end"),
    ]
)
def test_validate_blocks_exceptions(content, msg):
    """Validator should raise exceptions for bad block structure"""
    with pytest.raises(ValueError) as excinfo:
        validate_blocks(content)
    # Custom readable message
    assert True, f"Validation failed as expected: {msg} | Exception: {excinfo.value}"


@pytest.mark.parametrize(
    "content",
    [
        # Proper matching blocks
        "A\n<!-- shell -->do something<!-- shell end -->\nB",
        "<!-- file -->X<!-- file end -->",
        "<!-- ignore -->ignored<!-- ignore end -->",
        """<!-- shell -->code<!-- shell end -->
           <!-- file -->data<!-- file end -->"""
    ]
)
def test_validate_blocks_success(content):
    """Validator should pass for correct blocks"""
    result = validate_blocks(content)
    assert result is True, "Validation should succeed for well-formed blocks"


import pytest
from mdfile.updater.validator import validate_blocks

@pytest.mark.parametrize(
    "content, msg",
    [

        # Mixed case: valid blocks first, then an unmatched end block
        (
            """Start
            <!-- shell -->do this<!-- shell end -->
            <!-- file -->data<!-- file end -->
            Oops <!-- process end -->""",
            "Unmatched end block after valid blocks"
        ),

        # Mixed case: unmatched start inside correct blocks
        (
            """<!-- shell -->valid<!-- shell end -->
               <!-- file -->start without end
               <!-- ignore -->ignored<!-- ignore end -->""",
            "Unclosed file block inside valid shell and ignore blocks"
        ),

        # Mixed case: repeated start inside valid blocks
        (
            """<!-- shell -->A<!-- shell end -->
               <!-- file -->B<!-- file -->C<!-- file end -->""",
            "Repeated file start inside valid shell block"
        ),


    ]
)
def test_validate_blocks_mixed(content, msg):
    """Validator should catch errors in mixed content correctly"""
    with pytest.raises(ValueError) as excinfo:
        validate_blocks(content)
    assert True, f"Mixed validation failed as expected: {msg} | Exception: {excinfo.value}"




# --- Mixed content that should raise errors ---
@pytest.mark.parametrize(
    "content, msg",
    [

        # Unmatched end after valid blocks
        (
            """Start
            <!-- shell -->do this<!-- shell end -->
            <!-- file -->data<!-- file end -->
            Oops <!-- process end -->""",
            "Unmatched end block after valid blocks"
        ),
        # Unclosed start inside correct blocks
        (
            """<!-- shell -->valid<!-- shell end -->
               <!-- file -->start without end
               <!-- ignore -->ignored<!-- ignore end -->""",
            "Unclosed file block inside valid shell and ignore blocks"
        ),
        # Repeated start inside valid blocks
        (
            """<!-- shell -->A<!-- shell end -->
               <!-- file -->B<!-- file -->C<!-- file end -->""",
            "Repeated file start inside valid shell block"
        ),
        # Mismatched end block type
        (
            """<!-- file -->X<!-- process end -->""",
            "Mismatched end block type"
        ),
    ]
)
def test_validate_blocks_mixed_errors(content, msg):
    """Validator should raise ValueError for invalid mixed-content blocks"""
    with pytest.raises(ValueError) as excinfo:
        validate_blocks(content)
    assert True, f"{msg} | Exception: {excinfo.value}"


# --- Mixed content that should pass ---
@pytest.mark.parametrize(
    "content, msg",
    [
        # Ignore block contains fake end, should pass
        (
            """<!-- ignore -->X <!-- shell end --> Y<!-- ignore end -->
               <!-- shell -->real<!-- shell end -->""",
            "Ignore block contains fake end, should not error"
        ),
        # Multiple valid blocks in mixed order
        (
            """A
               <!-- shell -->do this<!-- shell end -->
               B
               <!-- file -->data<!-- file end -->
               C""",
            "Multiple valid blocks, all closed"
        ),
        # Nested ignore inside file, all valid
        (
            """<!-- file -->X<!-- ignore -->ignored<!-- ignore end -->Y<!-- file end -->""",
            "Nested ignore inside file, all closed"
        ),
        # Mixed case tags (capitalization) should pass
        (
            """<!-- SHELL -->do it<!-- ShElL end -->
               <!-- FILE -->data<!-- file END -->""",
            "Mixed-case tags should validate correctly"
        ),
    ]
)
def test_validate_blocks_mixed_success(content, msg):
    """Validator should pass for valid mixed-content blocks"""
    assert validate_blocks(content) is True, msg
