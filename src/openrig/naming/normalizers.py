"""Normalization functions for token values.

Each public function in this module conforms to the ``Normalizer`` signature::

    Callable[[object], str]

This means they accept any object (the raw token value before normalization,
which may be a ``str``, an ``Enum``, or any other type) and always return a
plain ``str``. Empty string signals "no value provided".

All functions are registered in ``NORMALIZER_MAP`` at the bottom of the module,
which is the single source of truth consumed by ``rules.build_normalizers()``.

Note on the ``if not value`` guard:
    These functions use ``if not value: return ""`` as a fast-exit for falsy
    inputs. This is intentional: the ``Manager`` never passes ``None`` to a
    normalizer (it returns ``""`` before calling them), and a falsy non-None
    value such as ``0`` or ``False`` is not a valid token value in this system.
    If that assumption changes, the guard should be replaced with an explicit
    ``if value is None: return ""``.
"""

from __future__ import annotations

from enum import Enum
from typing import Callable

from openrig.constants import Side
from openrig.naming import utils
from openrig.schemas import TokenValue

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _create_mapping(
    pairs: list[tuple[TokenValue, TokenValue]],
) -> dict[str, str]:
    """Builds a normalisation lookup table from (short, long) pairs.

    For each pair both the long form and the lowercase short form are mapped
    to the canonical short form. This allows case-insensitive lookups.

    Args:
        pairs: A list of ``(short_form, long_form)`` tuples. Each element may
            be a plain ``str`` or an ``Enum`` member whose ``.value`` is a
            ``str``.

    Returns:
        A ``dict`` mapping both long forms and lowercase short forms to the
        canonical short form string.

    Example:
        >>> _create_mapping([("l", "left"), ("r", "right")])
        {'left': 'l', 'l': 'l', 'right': 'r', 'r': 'r'}
    """
    mapping: dict[str, str] = {}
    for short, long in pairs:
        short_val = str(short.value) if isinstance(short, Enum) else str(short)
        long_val = str(long.value) if isinstance(long, Enum) else str(long)
        mapping[long_val] = short_val
        mapping[short_val.lower()] = short_val
    return mapping


_SIDE_MAPPING: dict[str, str] = _create_mapping(
    [
        (Side.LEFT, Side.LEFT_LONG),
        (Side.RIGHT, Side.RIGHT_LONG),
        (Side.CENTER, Side.CENTER_LONG),
        (Side.MIDDLE, Side.MIDDLE_LONG),
    ]
)


# ---------------------------------------------------------------------------
# Normalizer functions
# ---------------------------------------------------------------------------


def side(value: object) -> str:
    """Normalizes a side value to its standard abbreviation.

    Maps long-form or mixed-case side strings to their canonical short form
    (e.g. ``'Left'`` → ``'l'``). Values not found in the mapping are
    converted to camelCase as a fallback.

    Args:
        value: The raw side value to normalize.

    Returns:
        The normalized side string (e.g. ``'left'`` → ``'l'``),
        or ``""`` if the value is falsy.
    """
    if not value:
        return ""
    str_val = str(value)
    normalized = _SIDE_MAPPING.get(str_val.lower())
    return normalized if normalized else utils.to_camel_case(str_val)


def descriptor(value: object) -> str:
    """Normalizes a descriptor to camelCase.

    Converts any casing or separator style to camelCase to avoid conflicts
    with the naming separator (e.g. ``'upper_arm'`` → ``'upperArm'``).

    Args:
        value: The raw descriptor value to normalize.

    Returns:
        The camelCase descriptor string, or ``""`` if the value is falsy.
    """
    if not value:
        return ""
    return utils.to_camel_case(str(value))


def normalize_type(value: object) -> str:
    """Normalizes a type token to camelCase.

    Registered in ``NORMALIZER_MAP`` under the key ``"type"``. The function
    is named ``normalize_type`` to avoid shadowing the ``type`` builtin.

    Args:
        value: The raw type value to normalize.

    Returns:
        The camelCase type string, or ``""`` if the value is falsy.
    """
    if not value:
        return ""
    return utils.to_camel_case(str(value))


def pascal_case(value: object) -> str:
    """Normalizes a token value to PascalCase.

    Args:
        value: The raw value to normalize.

    Returns:
        The PascalCase string, or ``""`` if the value is falsy.
    """
    if not value:
        return ""
    return utils.to_pascal_case(str(value))


def snake_case(value: object) -> str:
    """Normalizes a token value to snake_case.

    Args:
        value: The raw value to normalize.

    Returns:
        The snake_case string, or ``""`` if the value is falsy.
    """
    if not value:
        return ""
    return utils.to_snake_case(str(value))


def kebab_case(value: object) -> str:
    """Normalizes a token value to kebab-case.

    Args:
        value: The raw value to normalize.

    Returns:
        The kebab-case string, or ``""`` if the value is falsy.
    """
    if not value:
        return ""
    return utils.to_kebab_case(str(value))


def clean(value: object) -> str:
    """Cleans a token value by replacing invalid characters.

    Args:
        value: The raw value to normalize.

    Returns:
        The cleaned string, or ``""`` if the value is falsy.
    """
    if not value:
        return ""
    return utils.clean_txt(str(value))


def version(value: object) -> str:
    """Normalizes a version number to the ``vNNN`` format.

    Accepts both raw integers (``1`` → ``'v001'``) and already-formatted
    strings (``'v3'`` → ``'v003'``).

    Args:
        value: The raw version value to normalize (``int`` or ``str``).

    Returns:
        The normalized version string (e.g. ``'v001'``), or ``""`` if falsy.
    """
    if not value:
        return ""
    str_val = str(value)
    ver_num = utils.get_version(str_val)
    if ver_num is not None:
        return f"v{str(ver_num).zfill(3)}"
    if str_val.isdigit():
        return f"v{str_val.zfill(3)}"
    return str_val


def upper(value: object) -> str:
    """Normalizes a token value to uppercase.

    Args:
        value: The raw value to normalize.

    Returns:
        The uppercase string, or ``""`` if the value is falsy.
    """
    if not value:
        return ""
    return utils.to_upper(str(value))


def lower(value: object) -> str:
    """Normalizes a token value to lowercase.

    Args:
        value: The raw value to normalize.

    Returns:
        The lowercase string, or ``""`` if the value is falsy.
    """
    if not value:
        return ""
    return utils.to_lower(str(value))


def capitalize(value: object) -> str:
    """Normalizes a token value by capitalizing its first letter.

    Args:
        value: The raw value to normalize.

    Returns:
        The capitalized string, or ``""`` if the value is falsy.
    """
    if not value:
        return ""
    return utils.capitalize_first(str(value))


def strip_digits(value: object) -> str:
    """Removes all digit characters from a token value.

    Args:
        value: The raw value to normalize.

    Returns:
        The string with all digits removed, or ``""`` if the value is falsy.
    """
    if not value:
        return ""
    return utils.strip_digits(str(value))


def strip_namespace(value: object) -> str:
    """Removes the namespace prefix from a token value.

    Strips everything up to and including the last ``:`` separator.

    Args:
        value: The raw value to normalize (e.g. ``'ns:nodeName'``).

    Returns:
        The string without its namespace prefix, or ``""`` if the value is falsy.
    """
    if not value:
        return ""
    return utils.strip_namespace(str(value))


def base_name(value: object) -> str:
    """Returns the leaf component of a path-like token value.

    Splits on ``|`` and returns the last segment.

    Args:
        value: The raw value to normalize (e.g. ``'|group|node'``).

    Returns:
        The base name string, or ``""`` if the value is falsy.
    """
    if not value:
        return ""
    return utils.get_base_name(str(value))


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

# ``Normalizer`` is re-exported here so callers can import it from this module
# without creating a circular dependency through ``rules``.
Normalizer = Callable[[object], str]

NORMALIZER_MAP: dict[str, Normalizer] = {
    "side": side,
    "descriptor": descriptor,
    "type": normalize_type,
    "pascal_case": pascal_case,
    "snake_case": snake_case,
    "kebab_case": kebab_case,
    "clean": clean,
    "version": version,
    "upper": upper,
    "lower": lower,
    "capitalize": capitalize,
    "strip_digits": strip_digits,
    "strip_namespace": strip_namespace,
    "base_name": base_name,
}
