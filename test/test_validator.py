import pytest
from mdfile.updater.validator import BlockValidator

@pytest.mark.parametrize(
    "content",
    [
        # simple valid blocks
        "<!-- shell ls -->do it<!-- shell end -->",
        "<!-- file myfile.txt -->data<!-- file end -->",
        "<!-- process run.sh -->echo hi<!-- process end -->",
        "<!-- ignore -->skip this<!-- ignore end -->",

        # ignore blocks with valid blocks inside
        "<!-- ignore --><!-- shell ignored -->x<!-- shell end --><!-- ignore end -->",
        "<!-- ignore --><!-- file ignored -->y<!-- file end --><!-- ignore end -->",
        "<!-- ignore --><!-- process ignored -->z<!-- process end --><!-- ignore end -->",

        # ignore inside another block
        "<!-- shell ls -->cmd<!-- ignore -->ignored<!-- ignore end -->more cmd<!-- shell end -->",
        "<!-- file f.txt -->data<!-- ignore -->skip<!-- ignore end -->end<!-- file end -->",
        "<!-- process run.sh -->do<!-- ignore -->skip<!-- ignore end -->done<!-- process end -->",

        # multiple sequential blocks
        "<!-- shell ls -->a<!-- shell end --><!-- file f.txt -->b<!-- file end -->",
        "<!-- process p.sh -->x<!-- process end --><!-- shell ls -->y<!-- shell end -->",
    ]
)
def test_block_validator_pass(content):
    bv = BlockValidator()
    assert bv.validate(content) is True


@pytest.mark.parametrize(
    "content,error",
    [
        # end without start
        ("<!-- shell end -->", "Unexpected shell end"),
        ("<!-- file end -->", "Unexpected file end"),
        ("<!-- process end -->", "Unexpected process end"),

        # missing text in start (empty command)
        ("<!-- shell --> <!-- shell end -->", "shell block missing required command/text"),
        ("<!-- file --> <!-- file end -->", "file block missing required command/text"),
        ("<!-- process --> <!-- process end -->", "process block missing required command/text"),

        # unclosed block
        ("<!-- shell ls -->do it", "Unclosed shell block started"),
        ("<!-- file f.txt -->data", "Unclosed file block started"),

        # unexpected nested ignore
        ("<!-- ignore -->x<!-- ignore -->y<!-- ignore end -->", "Unexpected ignore tag"),
    ]
)
def test_block_validator_fail(content, error):
    bv = BlockValidator()
    with pytest.raises(ValueError) as exc:
        bv.validate(content)
    assert error in str(exc.value)
