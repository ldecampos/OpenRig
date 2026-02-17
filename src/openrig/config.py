"""Configuration module for OpenRig."""

import os
from typing import Any

# Default configuration values
# These serve as the fallback if no external configuration is provided.
DEFAULTS: dict[str, Any] = {
    "side_default": "c",
    "rotate_order_default": "xyz",
    "axis_aim": "X",
    "axis_up": "Y",
    "axis_side": "Z",
    "shape_type_default": "circle",
    # Naming Convention Defaults
    # Defines the order of tokens to build a name (matches constants.Tokens)
    "naming_structure": ("descriptor", "side", "usage"),
    "naming_separator": "_",
    "naming_case": "snake_case",  # Options: snake_case, camelCase, PascalCase
}


def get_settings() -> dict[str, Any]:
    """Retrieves the configuration settings.

    Currently loads from defaults and allows environment variable overrides.
    Future implementations could load from a JSON/YAML file.
    """
    settings = DEFAULTS.copy()

    # Simple environment variable override mechanism
    # e.g. OPENRIG_SIDE_DEFAULT="l"
    for key, default_value in DEFAULTS.items():
        env_key = f"OPENRIG_{key.upper()}"
        if env_key in os.environ:
            env_value = os.environ[env_key]
            if isinstance(default_value, tuple):
                settings[key] = tuple(item.strip() for item in env_value.split(","))
            else:
                settings[key] = env_value

    return settings


SETTINGS = get_settings()
