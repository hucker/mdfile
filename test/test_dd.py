import pytest
from util.dotted_dict import DottedDict  # replace with the actual import

@pytest.mark.parametrize(
    "data,key,expected",
    [
        # top-level lookups
        ({"a": 1, "b": 2}, "a", 1),
        ({"a": 1, "b": 2}, "b", 2),
        # nested one level
        ({"foo": {"bar": 10}}, "foo.bar", 10),
        # nested two levels
        ({"foo": {"bar": {"baz": 42}}}, "foo.bar.baz", 42),
        # nested three levels
        ({"x": {"y": {"z": {"w": "deep"}}}}, "x.y.z.w", "deep"),
        # top-level with get default
        ({"a": 1}, "missing", "default"),
        # nested with get default
        ({"foo": {"bar": {}}}, "foo.bar.missing", "default"),
    ],
)
def test_dotteddict_lookup(data, key, expected):
    """Test dotted key lookups and get() with optional default."""
    d = DottedDict(data)
    if expected == "default":
        assert d.get(key, "default") == "default"
    else:
        assert d[key] == expected
        assert d.get(key) == expected

@pytest.mark.parametrize(
    "data,key",
    [
        ({"a": 1}, "b"),  # missing top-level
        ({"foo": {"bar": 10}}, "foo.baz"),  # missing intermediate
        ({"x": {"y": {"z": "value"}}}, "x.y.q"),  # missing leaf
    ],
)
def test_dotteddict_missing_key_raises(data, key):
    """Test that accessing missing dotted keys raises KeyError."""
    d = DottedDict(data)
    with pytest.raises(KeyError):
        _ = d[key]


@pytest.mark.parametrize(
    "initial,key,value,expected",
    [
        # top-level assignment
        ({}, "a", 1, {"a": 1}),
        # one-level nested assignment
        ({}, "foo.bar", 42, {"foo": {"bar": 42}}),
        # two-level nested assignment
        ({}, "foo.bar.baz", "deep", {"foo": {"bar": {"baz": "deep"}}}),
        # overwrite existing top-level key
        ({"a": 10}, "a", 99, {"a": 99}),
        # overwrite existing nested key
        ({"foo": {"bar": 1}}, "foo.bar", 2, {"foo": {"bar": 2}}),
        # create new nested key alongside existing
        ({"foo": {"bar": 1}}, "foo.baz", 3, {"foo": {"bar": 1, "baz": 3}}),
    ],
)
def test_dotteddict_setitem(initial, key, value, expected):
    """Test that accessing missing dotted keys raises KeyError."""
    d = DottedDict(initial)
    d[key] = value
    assert d[key] == value
    assert d == expected


@pytest.mark.parametrize(
    "initial,key",
    [
        # attempt to overwrite a leaf that is not a dict
        ({"foo": 1}, "foo.bar"),
        ({"foo": {"bar": 1}}, "foo.bar.baz.qux"),  # intermediate is a leaf
    ],
)
def test_dotteddict_setitem_creates_nested(initial, key):
    d = DottedDict(initial)
    # assignment should succeed and create nested dicts as needed
    d[key] = 123
    # check that we can read it back
    assert d[key] == 123