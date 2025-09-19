import datetime as dt
import importlib.metadata
import os
import re


class PackageAccessor:
    """Accessor for a specific package's metadata."""

    def __init__(self, package: str) -> None:
        self._package: str = package
        self._pkg_meta: dict[str, str] | None = None

    def _load_metadata(self) -> None:
        if self._pkg_meta is None:
            try:
                self._pkg_meta = dict(importlib.metadata.metadata(self._package))
            except importlib.metadata.PackageNotFoundError:
                self._pkg_meta = {}

    def __getattr__(self, field: str) -> str:
        self._load_metadata()
        key: str = field.replace("_", "-")
        if not self._pkg_meta:
            return ""
        all_vals = importlib.metadata.metadata(self._package).get_all(key)
        if all_vals:
            return ", ".join(all_vals)
        return self._pkg_meta.get(key, "")

    @property
    def table(self) -> str:
        """Return Markdown table of all non-empty metadata fields alphabetically."""
        self._load_metadata()
        if not self._pkg_meta:
            return "| Field | Value |\n|-------|-------|\n| (none) | |"

        rows: list[str] = []
        for key in sorted(self._pkg_meta.keys(), key=str.lower):
            field_name: str = key.replace("-", "_")
            value: str = getattr(self, field_name)
            if value:
                rows.append(f"| {field_name} | {value} |")

        header: str = "| Field | Value |\n|-------|-------|"
        return "\n".join([header] + rows)


class VariableReplacer:
    """Replace {{$var}} placeholders with vars, environment, or package metadata."""

    def __init__(self, extra_vars: dict[str, str] | None = None) -> None:
        """Initialize with default date/time vars and optional extra variables."""
        self.vars: dict[str, str] = {
            "date": dt.datetime.now().strftime("%Y-%m-%d"),
            "time": dt.datetime.now().strftime("%H:%M:%S"),
        }

        if extra_vars is not None:
            self.vars.update(extra_vars)

        # Dictionary of PackageAccessor objects for caching
        self._packages: dict[str, PackageAccessor] = {}

    def _get_package_accessor(self, package: str) -> PackageAccessor:
        """Return cached PackageAccessor for package, create if needed."""
        if package not in self._packages:
            self._packages[package] = PackageAccessor(package)
        return self._packages[package]

    @property
    def PLACEHOLDER_PATTERN(self) -> re.Pattern[str]:
        return re.compile(r'\{\{\s*\$([a-zA-Z][a-zA-Z0-9_.]*)\s*\}\}')

    def update(self, content: str) -> str:
        """
        Replace all {{$var}} placeholders in the content with their values.

        Supports multiple variable sources:
        1. Environment variables: {{$ENV.VARIABLE_NAME}}
        2. Meta information: {{$meta.package.field}} or {{$meta.field}} (defaults to 'mdfile' package)
        3. Variables in self.vars dictionary: {{$var_name}}

        Security:
        - Blocks sensitive variables via self._is_sensitive() check

        Error handling:
        - Returns formatted error messages in place of variables that cannot be resolved
        - Validates meta variable syntax

        Examples of meta variables:
            {{$meta.__version__}}          # Gets __version__ from default 'mdfile' package
            {{$meta.pathlib.__version__}}  # Gets __version__ from pathlib package
            {{$meta.pandas.__name__}}      # Gets __name__ from pandas package
            {{$meta.sys.path}}             # Gets path attribute from sys module

        Args:
            content: String containing {{$var}} placeholders to be replaced

        Returns:
            String with all placeholders replaced by their values or error messages
        """
        return self.PLACEHOLDER_PATTERN.sub(self._resolve_variable, content)

    def _resolve_variable(self, match: re.Match[str]) -> str:
        """
        Resolve a single variable placeholder match to its value.

        Args:
            match: Regular expression match object containing the variable name

        Returns:
            String representation of the variable value or error message
        """
        var_name: str = match.group(1)

        # Block sensitive keys
        if self._is_sensitive(var_name):
            return f"ERROR: Variable {var_name} blocked."

        # Dispatch to appropriate resolver based on variable prefix
        if var_name.startswith("ENV."):
            return self._resolve_env_variable(var_name)
        elif var_name.startswith("meta."):
            return self._resolve_meta_variable(var_name)
        elif var_name in self.vars:
            return str(self.vars[var_name])

        return f"(ERROR: Variable `{var_name}` not found)"

    def _resolve_env_variable(self, var_name: str) -> str:
        """
        Resolve an environment variable reference.

        Args:
            var_name: Variable name with "ENV." prefix

        Returns:
            Value from environment or error message
        """
        env_key: str = var_name[4:]
        return os.environ.get(env_key, f"(ERROR: Variable `{var_name}` not found)")

    def _resolve_meta_variable(self, var_name: str) -> str:
        """
        Resolve a meta variable reference to a package attribute.

        Args:
            var_name: Variable name with "meta." prefix

        Returns:
            String value of the package attribute or error message
        """
        parts: list[str] = var_name.split(".")

        if len(parts) == 2:
            package = 'mdfile'
            field = parts[1]
        elif len(parts) == 3:
            package, field = parts[1], parts[2]
        else:
            return f"(ERROR: Invalid meta syntax '{var_name}', must be meta.<package>.<field>)"

        accessor: PackageAccessor = self._get_package_accessor(package)
        return str(getattr(accessor, field))

    @staticmethod
    def _is_sensitive(var_name: str) -> bool:
        var_name_upper: str = var_name.upper()
        patterns: list[str] = [
            "API_", "_API_", "_API",
            "_SECRET", "SECRET_", "_TOKEN", "TOKEN_", "_KEY", "KEY_"
        ]
        return any(pat in var_name_upper for pat in patterns)
