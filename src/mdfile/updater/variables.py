import json
import os
import re
import datetime as dt
from importlib.metadata import version

class VariableReplacer:
    """
    Replace {{$var}} placeholders with values from a variables dictionary
    or environment. If a placeholder starts with ENV., it will read from
    os.environ. Sensitive API keys are blocked.
    """

    def __init__(self, vars_file: str | None = None) -> None:
        """
        Initialize the replacer with optional JSON file for variables.

        Args:
            vars_file (str | None): Path to JSON file with variables.
        """
        self.vars = self._load_vars(vars_file)

    def _load_vars(self, vars_file: str|None = None) -> dict[str, str]:

        """Load vars from JSON file or return empty dict."""
        base_vars: dict[str, str] = {
            "version": version("mdfile"),
            "name": "mdfile",
            "date": dt.datetime.now().strftime("%Y-%m-%d"),
            "time": dt.datetime.now().strftime("%H:%M:%S"),
        }

        if vars_file is None:
            return base_vars
        with open(vars_file, "r", encoding="utf-8") as f:
            json_vars = json.load(f)
            return base_vars | json_vars

    @property
    def PLACEHOLDER_PATTERN(self) -> re.Pattern[str]:
        """
        Matches {{$var}} placeholders in the content, allowing optional spaces.

        Details:
            \{\{\s*\$            : literal opening {{ with optional whitespace
            ([a-zA-Z][a-zA-Z0-9_.]*) : capture group for variable name
                                         - must start with a letter
                                         - can contain letters, digits, underscores, or dots
            \s*\}\}              : optional whitespace before closing }}

        Example matches:
            {{$USER}}          -> captures 'USER'
            {{ $USER }}        -> captures 'USER'
            {{   $ENV.PATH  }} -> captures 'ENV.PATH'

        This ensures we only capture well-formed variable placeholders
        while allowing human-friendly spacing.
        """
        return re.compile(r'\{\{\s*\$([a-zA-Z][a-zA-Z0-9_.]*)\s*\}\}')

    def update(self, content: str) -> str:
        """
        Replace all {{$var}} placeholders in content.

        Args:
            content (str): Text containing {{$var}} placeholders.

        Returns:
            str: Updated content with placeholders replaced.
        """
        def replacer(match: re.Match[str]) -> str:
            var_name: str = match.group(1)

            # Block potentially sensitive API keys
            if self._is_sensitive(var_name):
                return f"ERROR: Variable {var_name} blocked."

            # ENV lookup
            if var_name.startswith("ENV."):
                env_key = var_name[4:]
                return os.environ.get(env_key, f"(ERROR: Variable `{var_name}` not found)")

            # vars dict lookup
            if var_name in self.vars:
                return str(self.vars[var_name])

            # fallback
            return f"(ERROR: Variable `{var_name}` not found)"

        return self.PLACEHOLDER_PATTERN.sub(replacer, content)

    @staticmethod
    def _is_sensitive(var_name: str) -> bool:
        """
        Determine if an environment variable name is likely to contain
        an API key or secret, so it can be blocked from output.
        """
        var_name_upper = var_name.upper()
        # Block if starts with API_, contains _API_, ends with _API,
        # or contains common secret/key/token patterns
        patterns = [
            "API_", "_API_", "_API",
            "_SECRET", "SECRET_", "_TOKEN", "TOKEN_", "_KEY", "KEY_"
        ]
        return any(pat in var_name_upper for pat in patterns)
