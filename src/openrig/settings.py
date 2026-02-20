"""Settings module for OpenRig.

Loads ``config.json`` and exposes the result as the module-level ``SETTINGS``
constant. Environment variables can override any simple string field.

Architecture
------------
``json.load()`` unavoidably returns ``object`` (typed as ``Any`` in typeshed).
Rather than letting that ``Any`` propagate through the whole module, this
file absorbs it at the boundary with a small set of typed extractor helpers
(``_require_str``, ``_require_list``, ``_require_dict``) that convert
``object`` to concrete types immediately, raising ``ConfigError`` with a
clear human-readable message if the shape does not match.

Each top-level section of ``config.json`` is parsed by its own private
function (``_parse_rigging``, ``_parse_naming``, etc.), which receive and
return fully typed dataclasses. No ``Any`` escapes those functions.

Environment variable overrides
-------------------------------
Simple string fields can be overridden at runtime via environment variables
named ``OPENRIG_<SECTION>_<FIELD>`` (all upper-case). For example::

    OPENRIG_RIGGING_SIDE_DEFAULT=l
    OPENRIG_NAMING_SEPARATOR=-
    OPENRIG_SHAPES_DEFAULT=square

Token overrides use a comma-separated list::

    OPENRIG_NAMING_TOKENS=descriptor,side,usage
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Mapping, Tuple, Union

from openrig.schemas import (
    GlobalRules,
    NamingSettings,
    RiggingSettings,
    RuleConfig,
    Settings,
    ShapesSettings,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ConfigError(Exception):
    """Raised when ``config.json`` is missing, malformed, or structurally invalid."""


# ---------------------------------------------------------------------------
# Typed extractor helpers
# ---------------------------------------------------------------------------
# These functions are the single point where ``object`` (the type returned by
# json.load) is narrowed to a concrete type. All downstream code works with
# fully typed values.


def _require_str(value: object, path: str) -> str:
    """Extracts a ``str`` from an ``object``, raising ``ConfigError`` if it fails.

    Args:
        value: The raw value from the JSON payload.
        path: A dotted path string used in error messages (e.g. ``"rigging.axis_aim"``).

    Returns:
        The value cast to ``str``.

    Raises:
        ConfigError: If ``value`` is not a ``str``.
    """
    if not isinstance(value, str):
        raise ConfigError(
            f"Expected a string at '{path}', got {type(value).__name__!r}: {value!r}."
        )
    return value


def _require_list_of_str(value: object, path: str) -> List[str]:
    """Extracts a ``list`` of strings from an ``object``.

    Validates that ``value`` is a ``list`` and that every element is a
    ``str``. Uses index-based access to avoid ``list[Unknown]`` inference
    that Pylance produces when iterating directly over a bare
    ``isinstance``-narrowed list.

    Args:
        value: The raw value from the JSON payload.
        path: A dotted path string used in error messages.

    Returns:
        The value as a ``List[str]``.

    Raises:
        ConfigError: If ``value`` is not a list or contains non-string items.
    """
    if not isinstance(value, list):
        raise ConfigError(
            f"Expected a list at '{path}', got {type(value).__name__!r}: {value!r}."
        )
    # Cast to list[object] via explicit reconstruction so every element
    # is typed as object — required because isinstance narrows to
    # list[Unknown] and index access on that returns Unknown.
    items: List[object] = [*value]
    result: List[str] = []
    for i, item in enumerate(items):
        result.append(_require_str(item, f"{path}[{i}]"))
    return result


def _require_dict(value: object, path: str) -> Dict[str, object]:
    """Extracts a ``dict[str, object]`` from an ``object``.

    Validates that ``value`` is a ``dict`` and that every key is a ``str``.
    Uses ``list(value.keys())`` and index-based access to avoid
    ``dict[Unknown, Unknown]`` inference from bare ``isinstance`` narrowing.

    Args:
        value: The raw value from the JSON payload.
        path: A dotted path string used in error messages.

    Returns:
        The value as a ``Dict[str, object]``.

    Raises:
        ConfigError: If ``value`` is not a ``dict`` or contains non-string keys.
    """
    if not isinstance(value, dict):
        raise ConfigError(
            f"Expected a dict at '{path}', got {type(value).__name__!r}: {value!r}."
        )
    # Reconstruct as Dict[object, object] via spread so Pylance resolves
    # both keys and values as object instead of Unknown.
    raw: Dict[object, object] = {**value}
    result: Dict[str, object] = {}
    for k, v in raw.items():
        result[_require_str(k, f"{path}[key]")] = v
    return result


# ---------------------------------------------------------------------------
# Section parsers
# ---------------------------------------------------------------------------


def _parse_rule_config(data: Dict[str, object], path: str) -> RuleConfig:
    """Parses a single token rule dict into a ``RuleConfig``.

    Args:
        data: The raw dict from ``config.json``.
        path: Dotted path for error messages.

    Returns:
        A populated ``RuleConfig`` instance.

    Raises:
        ConfigError: If required fields are missing or have wrong types.
    """
    rule_type = _require_str(data.get("type"), f"{path}.type")

    raw_value = data.get("value")
    value: Union[str, List[str], None]
    if raw_value is None:
        value = None
    elif isinstance(raw_value, str):
        value = raw_value
    elif isinstance(raw_value, list):
        value = _require_list_of_str(data.get("value"), f"{path}.value")
    else:
        raise ConfigError(
            f"Expected a string or list at '{path}.value', "
            f"got {type(raw_value).__name__!r}."
        )

    raw_sources = data.get("sources")
    sources: Union[List[str], None] = None
    if raw_sources is not None:
        sources = _require_list_of_str(raw_sources, f"{path}.sources")

    return RuleConfig(type=rule_type, value=value, sources=sources)


def _parse_global_rules(data: Dict[str, object], path: str) -> GlobalRules:
    """Parses the ``__global__`` rule section into a ``GlobalRules`` instance.

    Args:
        data: The raw dict from ``config.json``.
        path: Dotted path for error messages.

    Returns:
        A populated ``GlobalRules`` instance.

    Raises:
        ConfigError: If required fields are missing or have wrong types.
    """
    raw_max = data.get("max_length")
    if not isinstance(raw_max, int):
        raise ConfigError(
            f"Expected an int at '{path}.max_length', got {type(raw_max).__name__!r}."
        )

    forbidden = _require_list_of_str(
        data.get("forbidden_patterns", []), f"{path}.forbidden_patterns"
    )

    separator_rule: Union[RuleConfig, None] = None
    raw_sep_rule = data.get("separator_rule")
    if raw_sep_rule is not None:
        sep_dict = _require_dict(raw_sep_rule, f"{path}.separator_rule")
        separator_rule = _parse_rule_config(sep_dict, f"{path}.separator_rule")

    return GlobalRules(
        max_length=raw_max,
        forbidden_patterns=forbidden,
        separator_rule=separator_rule,
    )


def _parse_naming_rules(
    raw_rules: Dict[str, object], path: str
) -> Mapping[str, Union[RuleConfig, GlobalRules]]:
    """Parses all token rules into a typed mapping.

    Args:
        raw_rules: The raw ``rules`` dict from ``config.json["naming"]``.
        path: Dotted path for error messages.

    Returns:
        A mapping of token name → ``RuleConfig`` or ``GlobalRules``.

    Raises:
        ConfigError: If any rule entry is malformed.
    """
    parsed: Dict[str, Union[RuleConfig, GlobalRules]] = {}
    for key, raw_value in raw_rules.items():
        entry_path = f"{path}.{key}"
        entry = _require_dict(raw_value, entry_path)
        if key == "__global__":
            parsed[key] = _parse_global_rules(entry, entry_path)
        else:
            parsed[key] = _parse_rule_config(entry, entry_path)
    return parsed


def _parse_rigging(section: Dict[str, object]) -> RiggingSettings:
    """Parses ``config.json["rigging"]`` into a ``RiggingSettings`` instance.

    Args:
        section: The raw ``rigging`` dict from ``config.json``.

    Returns:
        A populated ``RiggingSettings`` instance.

    Raises:
        ConfigError: If any required field is missing or has the wrong type.
    """
    return RiggingSettings(
        side_default=_require_str(section.get("side_default"), "rigging.side_default"),
        rotate_order_default=_require_str(
            section.get("rotate_order_default"), "rigging.rotate_order_default"
        ),
        axis_aim=_require_str(section.get("axis_aim"), "rigging.axis_aim"),
        axis_up=_require_str(section.get("axis_up"), "rigging.axis_up"),
        axis_side=_require_str(section.get("axis_side"), "rigging.axis_side"),
    )


def _parse_naming(section: Dict[str, object]) -> NamingSettings:
    """Parses ``config.json["naming"]`` into a ``NamingSettings`` instance.

    Args:
        section: The raw ``naming`` dict from ``config.json``.

    Returns:
        A populated ``NamingSettings`` instance.

    Raises:
        ConfigError: If any required field is missing or has the wrong type.
    """
    separator = _require_str(section.get("separator"), "naming.separator")
    tokens: Tuple[str, ...] = tuple(
        _require_list_of_str(section.get("tokens", []), "naming.tokens")
    )
    raw_rules = _require_dict(section.get("rules", {}), "naming.rules")
    rules = _parse_naming_rules(raw_rules, "naming.rules")

    raw_normalizers = _require_dict(
        section.get("normalizers", {}), "naming.normalizers"
    )
    normalizers: Dict[str, str] = {
        k: _require_str(v, f"naming.normalizers.{k}")
        for k, v in raw_normalizers.items()
    }

    return NamingSettings(
        separator=separator,
        tokens=tokens,
        rules=rules,
        normalizers=normalizers,
    )


def _parse_shapes(section: Dict[str, object]) -> ShapesSettings:
    """Parses ``config.json["shapes"]`` into a ``ShapesSettings`` instance.

    Args:
        section: The raw ``shapes`` dict from ``config.json``.

    Returns:
        A populated ``ShapesSettings`` instance, using defaults for absent fields.
    """
    raw_default = section.get("default")
    if raw_default is None:
        return ShapesSettings()
    return ShapesSettings(
        default=_require_str(raw_default, "shapes.default"),
    )


# ---------------------------------------------------------------------------
# Environment variable overrides
# ---------------------------------------------------------------------------


def _apply_env_overrides(settings: Settings) -> Settings:
    """Applies environment variable overrides to a ``Settings`` instance.

    Checks for ``OPENRIG_<SECTION>_<FIELD>`` variables and overwrites the
    corresponding dataclass fields. Only simple ``str`` fields and
    ``naming.tokens`` (comma-separated) are supported.

    Args:
        settings: The fully parsed ``Settings`` instance.

    Returns:
        The same ``Settings`` instance with any overrides applied in-place.
    """
    _str_overrides: List[Tuple[str, str, str]] = [
        # (env_var_suffix, section_attr, field_attr)
        ("RIGGING_SIDE_DEFAULT", "rigging", "side_default"),
        ("RIGGING_ROTATE_ORDER_DEFAULT", "rigging", "rotate_order_default"),
        ("RIGGING_AXIS_AIM", "rigging", "axis_aim"),
        ("RIGGING_AXIS_UP", "rigging", "axis_up"),
        ("RIGGING_AXIS_SIDE", "rigging", "axis_side"),
        ("NAMING_SEPARATOR", "naming", "separator"),
        ("SHAPES_DEFAULT", "shapes", "default"),
    ]

    for suffix, section_attr, field_attr in _str_overrides:
        env_key = f"OPENRIG_{suffix}"
        env_val = os.environ.get(env_key)
        if env_val is not None:
            section = getattr(settings, section_attr)
            setattr(section, field_attr, env_val)
            logger.debug("Override applied: %s=%r", env_key, env_val)

    tokens_env = os.environ.get("OPENRIG_NAMING_TOKENS")
    if tokens_env is not None:
        settings.naming.tokens = tuple(
            t.strip() for t in tokens_env.split(",") if t.strip()
        )
        logger.debug("Override applied: OPENRIG_NAMING_TOKENS=%r", tokens_env)

    return settings


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def get_settings() -> Settings:
    """Loads and returns the OpenRig configuration.

    Reads ``config.json`` from the same directory as this module, parses
    each section into its typed dataclass, and applies any environment
    variable overrides.

    Returns:
        A fully populated ``Settings`` instance.

    Raises:
        ConfigError: If ``config.json`` is missing, cannot be parsed as JSON,
            or has a structural mismatch with the expected schema.
    """
    config_path = Path(__file__).parent / "config.json"

    if not config_path.exists():
        raise ConfigError(
            f"Configuration file not found: '{config_path}'. "
            "Ensure 'config.json' exists in the openrig package directory."
        )

    try:
        with open(config_path, "r", encoding="utf-8") as fh:
            raw: object = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Failed to parse '{config_path}' as JSON: {exc}") from exc
    except OSError as exc:
        raise ConfigError(f"Could not read '{config_path}': {exc}") from exc

    # Narrow the top-level object to a typed dict immediately.
    root = _require_dict(raw, "<config.json>")

    try:
        settings = Settings(
            rigging=_parse_rigging(_require_dict(root.get("rigging", {}), "rigging")),
            naming=_parse_naming(_require_dict(root.get("naming", {}), "naming")),
            shapes=_parse_shapes(_require_dict(root.get("shapes", {}), "shapes")),
        )
    except ConfigError:
        raise
    except Exception as exc:
        raise ConfigError(
            f"Unexpected error while parsing '{config_path}': {exc}"
        ) from exc

    return _apply_env_overrides(settings)


SETTINGS: Settings = get_settings()
