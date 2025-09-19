import copy
import pytest
from util.dotted_dict import DottedDict  # replace with the actual import

# Define commonly used test cases
NON_STRING_KEYS = [
    1,  # integer
    (1, 2),  # tuple
    True,  # boolean
    3.14,  # float
    None,  # None
    b"bytes",  # bytes
    object(),  # custom object
]


# Lookup and access tests
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
    ],
)
def test_dotteddict_lookup(data, key, expected):
    """Test dotted key lookups work correctly."""
    d = DottedDict(data)
    assert d[key] == expected
    assert d.get(key) == expected


@pytest.mark.parametrize(
    "data,key,default_value",
    [
        # top-level with get default
        ({"a": 1}, "missing", "default"),
        # nested with get default
        ({"foo": {"bar": {}}}, "foo.bar.missing", "default"),
        # deeply nested with get default
        ({"x": {"y": {}}}, "x.y.z.missing", "default"),
    ],
)
def test_get_with_default(data, key, default_value):
    """Test get() method with default values."""
    d = DottedDict(data)
    assert d.get(key, default_value) == default_value


@pytest.mark.parametrize(
    "data,key",
    [
        ({"a": 1}, "b"),  # missing top-level
        ({"foo": {"bar": 10}}, "foo.baz"),  # missing intermediate
        ({"x": {"y": {"z": "value"}}}, "x.y.q"),  # missing leaf
    ],
)
def test_missing_key_raises(data, key):
    """Test that accessing missing dotted keys raises KeyError."""
    d = DottedDict(data)
    with pytest.raises(KeyError):
        _ = d[key]


# Assignment tests
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
def test_setitem(initial, key, value, expected):
    """Test setting values with dotted notation."""
    d = DottedDict(initial)
    d[key] = value
    assert d[key] == value
    assert d == expected


@pytest.mark.parametrize(
    "initial,key,value",
    [
        # intermediate path component is a non-dict value
        ({"foo": 1}, "foo.bar", 42),
        # deep nesting where intermediate is a non-dict
        ({"foo": {"bar": 1}}, "foo.bar.baz", 42),
    ],
)
def test_setitem_through_non_dict(initial, key, value):
    """Test setting values through paths where an intermediate component is not a dict."""
    d = DottedDict(initial)
    d[key] = value
    assert d[key] == value


# Type rejection tests
@pytest.mark.parametrize("non_string_key", NON_STRING_KEYS)
def test_getitem_rejects_non_string_keys(non_string_key):
    """Test that __getitem__ properly rejects non-string keys."""
    d = DottedDict({"a": 1})
    with pytest.raises(TypeError) as excinfo:
        d[non_string_key]
    error_msg = str(excinfo.value).lower()
    assert any(term in error_msg for term in ["string", "str"])
    assert "key" in error_msg


@pytest.mark.parametrize("non_string_key", NON_STRING_KEYS)
def test_get_rejects_non_string_keys(non_string_key):
    """Test that get() properly rejects non-string keys."""
    d = DottedDict({"a": 1})
    with pytest.raises(TypeError) as excinfo:
        d.get(non_string_key)
    error_msg = str(excinfo.value).lower()
    assert any(term in error_msg for term in ["string", "str"])
    assert "key" in error_msg


@pytest.mark.parametrize("non_string_key", NON_STRING_KEYS)
def test_setitem_rejects_non_string_keys(non_string_key):
    """Test that __setitem__ properly rejects non-string keys."""
    d = DottedDict()
    with pytest.raises(TypeError) as excinfo:
        d[non_string_key] = "value"
    error_msg = str(excinfo.value).lower()
    assert any(term in error_msg for term in ["string", "str"])
    assert "key" in error_msg


@pytest.mark.parametrize("non_string_key", NON_STRING_KEYS)
def test_contains_rejects_non_string_keys(non_string_key):
    """Test that __contains__ (in operator) properly rejects non-string keys."""
    d = DottedDict({"a": 1})
    with pytest.raises(TypeError) as excinfo:
        non_string_key in d
    error_msg = str(excinfo.value).lower()
    assert any(term in error_msg for term in ["string", "str"])
    assert "key" in error_msg


# Dict with non-string keys tests
@pytest.mark.parametrize(
    "test_dict,key_type",
    [
        # Direct non-string keys
        ({1: "value"}, "int"),
        ({None: "value"}, "NoneType"),
        ({True: "value"}, "bool"),
        ({(1, 2): "value"}, "tuple"),
        ({3.14: "value"}, "float"),
        # Nested non-string keys
        ({"outer": {2: "value"}}, "int"),
        ({"outer": {None: "value"}}, "NoneType"),
        ({"a": {"b": {"c": {4: "value"}}}}, "int"),
    ],
)
def test_convert_dict_rejects_non_string_keys(test_dict, key_type):
    """Test that _convert_dict properly rejects dictionaries with non-string keys."""
    d = DottedDict()
    with pytest.raises(TypeError) as excinfo:
        d._convert_dict(test_dict)
    error_msg = str(excinfo.value)
    assert "string keys" in error_msg
    assert key_type in error_msg


def test_convert_dict_accepts_valid_dicts():
    """Test that _convert_dict correctly handles valid dictionaries."""
    d = DottedDict()

    # Simple valid dict
    simple_dict = {"a": 1, "b": 2}
    result = d._convert_dict(simple_dict)
    assert isinstance(result, DottedDict)
    assert result["a"] == 1
    assert result["b"] == 2

    # Nested valid dict
    nested_dict = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
    result = d._convert_dict(nested_dict)
    assert isinstance(result, DottedDict)
    assert result["a"] == 1
    assert result["b.c"] == 2
    assert result["b.d.e"] == 3

    # Dict with non-dict values
    mixed_dict = {"a": 1, "b": [1, 2, 3], "c": {"d": None}}
    result = d._convert_dict(mixed_dict)
    assert isinstance(result, DottedDict)
    assert result["a"] == 1
    assert result["b"] == [1, 2, 3]
    assert result["c.d"] is None

    # Empty dict
    empty_dict = {}
    result = d._convert_dict(empty_dict)
    assert isinstance(result, DottedDict)
    assert len(result) == 0


# Initialization tests
def test_initialization_methods():
    """Test initialization with different methods."""
    # From keyword arguments
    d1 = DottedDict(a=1, b=2)
    assert d1["a"] == 1
    assert d1["b"] == 2

    # From list of tuples
    d2 = DottedDict([("a", 1), ("b", 2)])
    assert d2["a"] == 1
    assert d2["b"] == 2

    # From another DottedDict
    d3 = DottedDict(d2)
    assert d3["a"] == 1
    assert d3["b"] == 2

    # From a regular dict
    d4 = DottedDict({"a": 1, "b": {"c": 2}})
    assert d4["a"] == 1
    assert d4["b.c"] == 2


def test_nested_dict_conversion():
    """Test that nested dictionaries are converted to DottedDict instances."""
    data = {"a": {"b": {"c": 1}}}
    d = DottedDict(data)
    assert isinstance(d["a"], DottedDict)
    assert isinstance(d["a"]["b"], DottedDict)


def test_deep_copy():
    """Test deep copying of DottedDict."""
    d1 = DottedDict({"a": 1, "b": {"c": [1, 2, 3]}})
    d2 = copy.deepcopy(d1)

    # Modify d1 and check that d2 is unaffected
    d1["a"] = 99
    d1["b.c"].append(4)

    assert d2["a"] == 1
    assert d2["b.c"] == [1, 2, 3]


# Container behavior tests
def test_iteration():
    """Test iteration over keys."""
    d = DottedDict({"a": 1, "b": {"c": 2}})
    assert set(d) == {"a", "b"}


def test_contains():
    """Test containment checks with dotted notation."""
    d = DottedDict({"a": 1, "b": {"c": 2}})
    assert "a" in d
    assert "b.c" in d
    assert "b.d" not in d
    assert "missing" not in d


# Update method tests
def test_update_with_dict():
    """Test update with a dictionary."""
    d = DottedDict({"existing": "value"})
    d.update({"a": 1, "b": 2})
    assert d["a"] == 1
    assert d["b"] == 2
    assert d["existing"] == "value"


def test_update_with_kwargs():
    """Test update with keyword arguments."""
    d = DottedDict({"existing": "value"})
    d.update(c=3, d=4)
    assert d["c"] == 3
    assert d["d"] == 4
    assert d["existing"] == "value"


def test_update_with_pairs():
    """Test update with list of pairs."""
    d = DottedDict({"existing": "value"})
    d.update([("e", 5), ("f", 6)])
    assert d["e"] == 5
    assert d["f"] == 6
    assert d["existing"] == "value"


def test_update_with_nested_dict():
    """Test update with nested dictionary."""
    d = DottedDict({"existing": "value"})
    d.update({"nested.key": "value"})
    assert d["nested.key"] == "value"
    assert d["nested"]["key"] == "value"
    assert d["existing"] == "value"


def test_update_with_another_dotteddict():
    """Test update with another DottedDict."""
    d = DottedDict({"existing": "value"})
    other = DottedDict({"other.nested": "other_value"})
    d.update(other)
    assert d["other"]["nested"] == "other_value"
    assert d["other.nested"] == "other_value"
    assert d["existing"] == "value"


def test_update_converts_regular_dicts():
    """Test that update converts regular dicts to DottedDict."""
    d = DottedDict()
    d.update({"regular": {"dict": "value"}})
    assert isinstance(d["regular"], DottedDict)
    assert d["regular.dict"] == "value"


@pytest.mark.parametrize("non_string_key", NON_STRING_KEYS[:3])  # Use a subset for brevity
def test_update_rejects_non_string_keys(non_string_key):
    """Test that update rejects non-string keys."""
    d = DottedDict({"valid": "value"})
    with pytest.raises(TypeError):
        d.update({non_string_key: "value"})


# Edge case tests
def test_get_with_none_values():
    """Test get method with None values."""
    d = DottedDict({"a": {"b": None}})
    assert d.get("a.b") is None
    assert d.get("a.b", "default") is None


def test_get_with_complex_default_values():
    """Test get method with complex default values."""
    d = DottedDict()
    complex_default = {"complex": "default"}
    assert d.get("missing", complex_default) is complex_default


def test_empty_string_keys():
    """Test handling of empty string keys."""
    d = DottedDict()
    d[""] = "empty"
    assert d.get("") == "empty"
    assert d[""] == "empty"


def test_keys_with_multiple_dots():
    """Test keys with multiple dots."""
    d = DottedDict()
    d["x.y.z"] = "multi-dots"
    assert d.get("x.y.z") == "multi-dots"
    assert d["x"]["y"]["z"] == "multi-dots"
