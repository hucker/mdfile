"""
Provides the DottedDict class for convenient nested dictionary access.

DottedDict is a specialized dictionary that allows accessing and setting nested values
using dot notation in string keys. It automatically converts nested dictionaries
to DottedDict instances and maintains type consistency throughout operations.

This module is useful for working with hierarchical configuration data,
complex nested structures, or any scenario where dot notation access is preferable
to multiple bracket notation.

NOTE: This module ENFORCES string keys for all operations.
"""


from collections.abc import Mapping
from typing import Any


class DottedDict(dict):
    """
    Dictionary that supports dotted key lookup and assignment
    for nested dictionaries.

    DottedDict can be initialized in multiple ways:
    - Empty: DottedDict()
    - From keyword arguments: DottedDict(a=1, b=2)
    - From a dictionary: DottedDict({"a": 1, "b": 2})
    - From a list of key-value pairs: DottedDict([("a", 1), ("b", 2)])

    All keys must be strings.

    Example:
        # Create a DottedDict
        data = DottedDict({"foo": {"bar": 1}})

        # Access nested values with dot notation
        assert data["foo.bar"] == 1
        assert data["foo"]["bar"] == 1

        # Set nested values with dot notation
        data["foo.baz"] = 42
        assert data["foo"]["baz"] == 42

        # Automatically creates nested structures
        data["a.b.c.d"] = "nested"
        assert data["a"]["b"]["c"]["d"] == "nested"
    """

    def __init__(self, mapping=None, **kwargs):
        """Initialize a new DottedDict with the given values.

        Args:
            mapping: An optional dictionary or iterable of key-value pairs to initialize from
            **kwargs: Key-value pairs to add to the dictionary
        """
        # Initialize as an empty dict
        super().__init__()

        # Use update to handle both dict and iterable of pairs
        if mapping is not None:
            self.update(mapping)

        # Add items from kwargs
        if kwargs:
            self.update(kwargs)

    def _convert_dict(self, d: dict) -> 'DottedDict':
        """Convert a regular dict to DottedDict, including nested dicts."""
        result = DottedDict()
        for k, v in d.items():
            if not isinstance(k, str):
                raise TypeError(f"DottedDict only accepts string keys, got {type(k)}")
            if isinstance(v, dict) and not isinstance(v, DottedDict):
                result[k] = self._convert_dict(v)
            else:
                result[k] = v
        return result

    def __setitem__(self, key: str, value: Any) -> None:
        # Validate key is a string
        if not isinstance(key, str):
            raise TypeError(f"DottedDict only accepts string keys, got {type(key)}")

        # Convert dict values to DottedDict
        if isinstance(value, dict) and not isinstance(value, DottedDict):
            value = self._convert_dict(value)

        if "." not in key:
            super().__setitem__(key, value)
            return

        parts = key.split(".")
        current: Any = self
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = DottedDict()
            current = current[part]

        current[parts[-1]] = value

    def __contains__(self, key: str) -> bool:
        """Support containment check with dotted notation."""
        if not isinstance(key, str):
            raise TypeError(f"DottedDict only accepts string keys, got {type(key)}")

        if "." not in key:
            return super().__contains__(key)

        try:
            self[key]  # Try to access the item using __getitem__
            return True
        except (KeyError, TypeError):
            return False

    def __getitem__(self, key: str) -> Any:
        # Validate key is a string
        if not isinstance(key, str):
            raise TypeError(f"DottedDict only accepts string keys, got {type(key)}")

        if "." not in key:
            return super().__getitem__(key)

        current: Any = self
        for part in key.split("."):
            if isinstance(current, Mapping) and part in current:
                current = current[part]
            else:
                raise KeyError(key)
        return current

    def get(self, key, default=None):
        """Get an item using the given key, with an optional default value.

        Args:
            key: The key to look up (must be a string)
            default: Value to return if the key is not found

        Returns:
            The value for key if key is in the dictionary, else default

        Raises:
            TypeError: If key is not a string
        """
        # Validate key is a string first
        if not isinstance(key, str):
            raise TypeError(f"DottedDict only accepts string keys, got {type(key)}")

        try:
            return self[key]
        except KeyError:
            return default

    def update(self, *args, **kwargs):
        d = dict()
        d.update(*args, **kwargs)
        for k, v in d.items():
            if not isinstance(k, str):
                raise TypeError(f"DottedDict only accepts string keys, got {type(k)}")
            self[k] = v  # Use __setitem__ to handle conversion

