import copy

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


def test_nested_dict_conversion():
    """Test that nested dictionaries are converted to DottedDict instances."""
    data = {"a": {"b": {"c": 1}}}
    d = DottedDict(data)

    # Check that nested dictionaries are DottedDict instances
    assert isinstance(d["a"], DottedDict)
    assert isinstance(d["a"]["b"], DottedDict)

def test_initialization():
    """Test initialization with different arguments."""
    # From keyword arguments
    d1 = DottedDict(a=1, b=2)
    assert d1["a"] == 1

    # From list of tuples
    d2 = DottedDict([("a", 1), ("b", 2)])
    assert d2["a"] == 1

    # From another DottedDict
    d3 = DottedDict(d2)
    assert d3["a"] == 1

def test_deep_copy():
    """Test deep copying of DottedDict."""
    d1 = DottedDict({"a": 1, "b": {"c": [1, 2, 3]}})
    d2 = copy.deepcopy(d1)

    # Modify d1 and check that d2 is unaffected
    d1["a"] = 99
    d1["b.c"].append(4)

    assert d2["a"] == 1
    assert d2["b.c"] == [1, 2, 3]

def test_iteration_and_containment():
    """Test iteration and containment checks."""
    d = DottedDict({"a": 1, "b": {"c": 2}})

    # Basic iteration
    assert set(d) == {"a", "b"}

    # Containment checks with dotted notation
    assert "a" in d
    assert "b.c" in d
    assert "b.d" not in d

@pytest.mark.parametrize("non_string_key", [
    1,  # integer
    (1, 2),  # tuple
    True,  # boolean
    3.14,  # float
    None,  # None
    b"bytes",  # bytes
    object(),  # custom object
])
def test_rejects_non_string_keys(non_string_key):
    """Test that DottedDict raises TypeError for non-string keys."""
    d = DottedDict()

    # Test assignment with non-string key
    with pytest.raises(TypeError):
        d[non_string_key] = "value"

    # Test initialization with non-string key
    with pytest.raises(TypeError):
        DottedDict({non_string_key: "value"})

    # Test update with non-string key
    d = DottedDict({"valid": "value"})
    with pytest.raises(TypeError):
        d.update({non_string_key: "value"})

    # Test getitem with non-string key
    with pytest.raises(TypeError):
        value = d[non_string_key]

    # Test get with non-string key (should raise TypeError)
    with pytest.raises(TypeError):
        value = d.get(non_string_key, "default")

def test_update_method():
    """Test the update method with various input types."""
    # Base DottedDict to update
    d = DottedDict({"existing": "value"})

    # Update with dictionary
    d.update({"a": 1, "b": 2})
    assert d["a"] == 1
    assert d["b"] == 2
    assert d["existing"] == "value"

    # Update with kwargs
    d.update(c=3, d=4)
    assert d["c"] == 3
    assert d["d"] == 4

    # Update with list of pairs
    d.update([("e", 5), ("f", 6)])
    assert d["e"] == 5
    assert d["f"] == 6

    # Update with nested dict
    d.update({"nested.key": "value"})
    assert d["nested"]["key"] == "value"
    assert d["nested.key"] == "value"

    # Update with another DottedDict
    other = DottedDict({"other.nested": "other_value"})
    d.update(other)
    assert d["other"]["nested"] == "other_value"

    # Update should convert regular dicts to DottedDict
    d.update({"regular": {"dict": "value"}})
    assert isinstance(d["regular"], DottedDict)
    assert d["regular.dict"] == "value"


def test_get_method_edge_cases():
    """Test edge cases for the get method."""
    d = DottedDict({"a": {"b": None}})

    # Basic get functionality
    assert d.get("a.b") is None
    assert d.get("a.b", "default") is None

    # Default value for missing keys
    assert d.get("missing") is None
    assert d.get("missing", "default") == "default"
    assert d.get("a.missing", "default") == "default"
    assert d.get("missing.deeper", "default") == "default"

    # Complex default values
    complex_default = {"complex": "default"}
    assert d.get("missing", complex_default) is complex_default

    # Edge case: empty string key
    d[""] = "empty"
    assert d.get("") == "empty"
    assert d.get("", "default") == "empty"

    # Edge case: keys with multiple dots
    d["x.y.z"] = "multi-dots"
    assert d.get("x.y.z") == "multi-dots"

    # Edge case: None as default
    assert d.get("missing", None) is None

def test_get_with_non_string_keys():
    """Test that get rejects non-string keys."""
    d = DottedDict({"a": 1})

    # Should raise TypeError
    with pytest.raises(TypeError):
        d.get(1)

    # Should raise TypeError even with default
    with pytest.raises(TypeError):
        d.get(1, "default")

@pytest.mark.parametrize("non_string_key", [
    1,
    None,
    True,
    {"dict": "as_key"},
    ["list", "as", "key"],
    (1, 2),
    3.14,
    set([1, 2]),
    object(),
])
def test_contains_rejects_non_string_keys(non_string_key):
    """Test that __contains__ (in operator) properly rejects various non-string keys."""
    d = DottedDict({"a": 1, "b": {"c": 2}})

    # Test that the non-string key raises TypeError
    with pytest.raises(TypeError) as excinfo:
        non_string_key in d

    # Verify the error message is descriptive
    error_msg = str(excinfo.value).lower()
    assert "string" in error_msg or "str" in error_msg
    assert "key" in error_msg


def test_contains_accepts_string_keys():
    """Test that __contains__ works correctly with valid string keys."""
    d = DottedDict({"a": 1, "b": {"c": 2}})

    # Make sure string keys work as expected
    assert "a" in d
    assert "b" in d
    assert "b.c" in d
    assert "missing" not in d
    assert "b.missing" not in d


@pytest.mark.parametrize("test_dict, key_type", [
    # Direct non-string keys
    ({1: "value"}, "int"),
    ({None: "value"}, "NoneType"),
    ({True: "value"}, "bool"),
    ({(1, 2): "value"}, "tuple"),
    ({3.14: "value"}, "float"),
    ({object(): "value"}, "object"),

    # Nested non-string keys
    ({"outer": {2: "value"}}, "int"),
    ({"outer": {None: "value"}}, "NoneType"),
    ({"outer": {True: "value"}}, "bool"),
    ({"a": {"b": {"c": {4: "value"}}}}, "int"),
])
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
