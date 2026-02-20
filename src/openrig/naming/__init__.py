"""Naming package for OpenRig.

This package provides a configurable system for building, parsing, and
validating names according to a defined convention.

The main entry point is ``get_manager()``, which returns a singleton
``Manager`` instance pre-configured with the rules and normalizers
declared in ``config.json``.

Public API:
    - ``get_manager() -> Manager``: returns the singleton manager.
    - ``Manager``: the naming manager class.
    - ``Normalizer``: type alias for normalizer callables.

Example:
    >>> from openrig.naming import get_manager
    >>> manager = get_manager()
    >>> manager.build_name(descriptor="arm", side="l", usage="jnt")
    'arm_l_jnt'
"""

from __future__ import annotations

from typing import Optional

from .manager import Manager
from .normalizers import Normalizer
from .rules import GLOBAL_RULES, NORMALIZERS, SEPARATOR, TOKEN_RULES, TOKENS

__all__ = [
    "Manager",
    "Normalizer",
    "get_manager",
]

_manager_instance: Optional[Manager] = None


def get_manager() -> Manager:
    """Returns the pre-configured singleton ``Manager`` instance.

    Builds the instance on first call using the convention defined in
    ``config.json`` (via ``rules.py``). Subsequent calls return the
    same instance.

    Returns:
        The singleton ``Manager`` instance.
    """
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = Manager(
            tokens=TOKENS,
            separator=SEPARATOR,
            rules=TOKEN_RULES,
            normalizers=NORMALIZERS,
            global_rules=GLOBAL_RULES,
        )
    return _manager_instance
