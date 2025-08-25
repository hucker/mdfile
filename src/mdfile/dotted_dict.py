from collections.abc import Mapping
from typing import Any

class DottedDict(dict):
    """
    Dictionary that supports dotted key lookup for nested dictionaries.

    Example:
        data = DottedDict({"foo": {"fum": 42}})
        assert data["foo.fum"] == 42
    """

    def __getitem__(self, key: str) -> Any:
        if "." not in key:
            return super().__getitem__(key)

        current: Any = self
        for part in key.split("."):
            if isinstance(current, Mapping) and part in current:
                current = current[part]
            else:
                raise KeyError(key)
        return current

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default
