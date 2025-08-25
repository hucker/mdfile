import pytest
from mdfile.dotted_dict import DottedDict  # replace with the actual import

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
    d = DottedDict(data)
    with pytest.raises(KeyError):
        _ = d[key]
