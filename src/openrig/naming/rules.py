"""Configuration rules for the naming convention.

This module is responsible for two things:

1. **Building rules**: interpreting the raw ``RuleConfig`` entries from
   ``config.json`` and converting them into typed ``ConcreteRule`` instances
   (``RegexRule``, ``ListRule``, ``CallableRule``).

2. **Building normalizers**: resolving the normalizer function names declared
   in ``config.json`` into actual callables from ``normalizers.NORMALIZER_MAP``.

The module also validates the integrity of the assembled convention at import
time, so any configuration error is caught immediately rather than at the
first call to ``build_name``.

Exported constants (consumed by ``__init__.py`` and ``Manager``):
    - ``TOKENS``: ordered list of token names.
    - ``SEPARATOR``: the separator character.
    - ``TOKEN_RULES``: mapping of token name → ``ConcreteRule``.
    - ``NORMALIZERS``: mapping of token name → normalizer callable.
    - ``GLOBAL_RULES``: the validated ``GlobalRules`` instance.
"""

from __future__ import annotations

import importlib
import inspect
import re
from enum import Enum
from typing import Callable, Dict, FrozenSet, List, Mapping

from openrig import constants
from openrig.schemas import (
    CallableRule,
    ConcreteRule,
    GlobalRules,
    ListRule,
    RegexRule,
    RuleConfig,
)
from openrig.settings import SETTINGS

# ---------------------------------------------------------------------------
# Normalizer type alias
# ---------------------------------------------------------------------------

# All normalizer functions accept ``object`` (the widest safe type for
# input that is guaranteed to be converted to ``str`` internally) and
# return ``str``. Using ``object`` instead of ``Any`` is correct here:
# it is the honest supertype of everything without losing type safety.
Normalizer = Callable[[object], str]


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class RuleBuilderError(Exception):
    """Raised when the naming convention cannot be assembled from configuration."""


# ---------------------------------------------------------------------------
# Private providers — each converts a RuleConfig into a ConcreteRule
# ---------------------------------------------------------------------------


def _provider_regex(config: RuleConfig) -> RegexRule:
    """Converts a ``"regex"`` RuleConfig into a ``RegexRule``.

    Args:
        config: The raw rule configuration from ``config.json``.

    Returns:
        A ``RegexRule`` instance wrapping the pattern.

    Raises:
        RuleBuilderError: If ``config.value`` is not a string, or if the
            pattern is not a valid regular expression.
    """
    if not isinstance(config.value, str):
        raise RuleBuilderError(
            f"Regex rule requires a string 'value', got: {type(config.value).__name__!r}."
        )
    try:
        return RegexRule(pattern=config.value)
    except ValueError as exc:
        raise RuleBuilderError(str(exc)) from exc


def _provider_list(config: RuleConfig) -> ListRule:
    """Converts a ``"list"`` RuleConfig into a ``ListRule``.

    Args:
        config: The raw rule configuration from ``config.json``.

    Returns:
        A ``ListRule`` instance with the allowed values as a ``frozenset``.

    Raises:
        RuleBuilderError: If ``config.value`` is not a list.
    """
    if not isinstance(config.value, list):
        raise RuleBuilderError(
            f"List rule requires a list 'value', got: {type(config.value).__name__!r}."
        )
    return ListRule(allowed=frozenset(config.value))


def _provider_from_enums(config: RuleConfig) -> ListRule:
    """Aggregates enum member values into a ``ListRule``.

    Iterates over all enum classes named in ``config.sources`` within
    ``openrig.constants`` and collects their string values into a single
    ``ListRule``.

    Args:
        config: The raw rule configuration. ``config.sources`` must be a
            non-empty list of enum class names present in ``openrig.constants``.

    Returns:
        A ``ListRule`` whose allowed set is the union of all member values.

    Raises:
        RuleBuilderError: If ``config.sources`` is missing, empty, or
            references a name that is not a valid ``Enum`` subclass.
    """
    if not isinstance(config.sources, list) or not config.sources:
        raise RuleBuilderError(
            "'sources' for a 'from_enums' rule must be a non-empty list of enum names."
        )

    all_values: FrozenSet[str] = frozenset()
    for name in config.sources:
        enum_cls = getattr(constants, name, None)
        if (
            enum_cls is None
            or not inspect.isclass(enum_cls)
            or not issubclass(enum_cls, Enum)
        ):
            raise RuleBuilderError(
                f"'{name}' is not a valid Enum subclass in openrig.constants."
            )
        all_values = all_values | frozenset(str(member.value) for member in enum_cls)

    return ListRule(allowed=all_values)


def _provider_callable(config: RuleConfig) -> CallableRule:
    """Imports a callable by dotted path and wraps it in a ``CallableRule``.

    The callable at the given path must accept a single ``str`` argument and
    return a value interpretable as ``bool``.

    Args:
        config: The raw rule configuration. ``config.value`` must be a
            dotted import path string (e.g. ``"mypackage.module.my_func"``).

    Returns:
        A ``CallableRule`` wrapping the imported function.

    Raises:
        RuleBuilderError: If ``config.value`` is not a string, if the module
            cannot be imported, or if the resolved attribute is not callable.
    """
    if not isinstance(config.value, str):
        raise RuleBuilderError(
            f"Callable rule requires a dotted-path string 'value', "
            f"got: {type(config.value).__name__!r}."
        )

    import_path = config.value
    try:
        module_path, func_name = import_path.rsplit(".", 1)
    except ValueError as exc:
        raise RuleBuilderError(
            f"Callable rule 'value' must be a dotted path (e.g. 'pkg.mod.func'), "
            f"got: {import_path!r}."
        ) from exc

    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise RuleBuilderError(
            f"Could not import module '{module_path}' for callable rule: {exc}"
        ) from exc

    func = getattr(module, func_name, None)
    if func is None:
        raise RuleBuilderError(
            f"Module '{module_path}' has no attribute '{func_name}'."
        )
    if not callable(func):
        raise RuleBuilderError(
            f"'{import_path}' resolves to a non-callable object: {func!r}."
        )

    return CallableRule(func=func, name=import_path)


# ---------------------------------------------------------------------------
# Provider dispatch table
# ---------------------------------------------------------------------------

# Maps the ``type`` string from ``config.json`` to the corresponding provider.
# Each provider accepts a ``RuleConfig`` and returns a ``ConcreteRule``.
_PROVIDER_MAP: Dict[str, Callable[[RuleConfig], ConcreteRule]] = {
    "regex": _provider_regex,
    "list": _provider_list,
    "from_enums": _provider_from_enums,
    "callable": _provider_callable,
}


# ---------------------------------------------------------------------------
# Public builders
# ---------------------------------------------------------------------------


def build_rules() -> tuple[Dict[str, ConcreteRule], GlobalRules]:
    """Builds the token rule mapping and the global rules from configuration.

    Reads ``SETTINGS.naming.rules``, extracts the mandatory ``__global__``
    entry as a ``GlobalRules`` instance, and converts every remaining entry
    from a ``RuleConfig`` into the appropriate ``ConcreteRule`` via the
    provider dispatch table.

    Returns:
        A tuple of ``(token_rules, global_rules)`` where ``token_rules`` maps
        each token name to its ``ConcreteRule`` and ``global_rules`` is the
        validated ``GlobalRules`` dataclass.

    Raises:
        RuleBuilderError: If ``__global__`` is missing or invalid, if an
            unknown rule type is encountered, or if a provider fails.
    """
    # --- Extract and validate global rules ---
    global_rules_config = SETTINGS.naming.rules.get("__global__")
    if not isinstance(global_rules_config, GlobalRules):
        raise RuleBuilderError(
            "Configuration is missing or invalid for '__global__' in 'naming_rules'. "
            "Expected a GlobalRules instance."
        )
    global_rules: GlobalRules = global_rules_config

    # --- Build per-token rules ---
    token_rules: Dict[str, ConcreteRule] = {}
    for token, config in SETTINGS.naming.rules.items():
        if token == "__global__":
            continue

        if not isinstance(config, RuleConfig):
            raise RuleBuilderError(
                f"Expected a RuleConfig for token '{token}', "
                f"got: {type(config).__name__!r}."
            )

        provider = _PROVIDER_MAP.get(config.type)
        if provider is None:
            raise RuleBuilderError(
                f"Unknown rule type '{config.type}' for token '{token}'. "
                f"Valid types are: {sorted(_PROVIDER_MAP.keys())!r}."
            )

        token_rules[token] = provider(config)

    return token_rules, global_rules


def build_normalizers() -> Dict[str, Normalizer]:
    """Resolves normalizer function names into callable normalizers.

    Reads ``SETTINGS.naming.normalizers`` and maps each token name to the
    corresponding function in ``normalizers.NORMALIZER_MAP``.

    Returns:
        A mapping of token name → normalizer callable.

    Raises:
        RuleBuilderError: If a declared normalizer name is not found in
            ``NORMALIZER_MAP``.
    """
    from openrig.naming.normalizers import NORMALIZER_MAP

    final_normalizers: Dict[str, Normalizer] = {}
    for token, func_name in SETTINGS.naming.normalizers.items():
        normalizer_func = NORMALIZER_MAP.get(func_name)
        if normalizer_func is None:
            raise RuleBuilderError(
                f"Normalizer '{func_name}' for token '{token}' not found "
                f"in NORMALIZER_MAP. Available: {sorted(NORMALIZER_MAP.keys())!r}."
            )
        final_normalizers[token] = normalizer_func

    return final_normalizers


def validate_convention(
    tokens: List[str],
    separator: str,
    token_rules: Mapping[str, ConcreteRule],
    global_rules: GlobalRules,
) -> None:
    """Validates the structural integrity of the assembled naming convention.

    Performs checks that cannot be done at the individual rule level:
    - Token list must be non-empty and duplicate-free.
    - Separator must be non-empty and satisfy its own global rule (if any).
    - Token names must be valid Python identifiers (required for named
      regex capture groups).

    Note:
        Regex pattern validity is no longer checked here because
        ``RegexRule.__post_init__`` already validates the pattern at
        construction time.

    Args:
        tokens: The ordered list of token names.
        separator: The separator character.
        token_rules: The assembled token rule mapping.
        global_rules: The global rules dataclass.

    Raises:
        RuleBuilderError: If any structural constraint is violated.
    """
    if not tokens:
        raise RuleBuilderError("'naming_tokens' cannot be an empty list.")

    if len(set(tokens)) != len(tokens):
        duplicates = [t for t in tokens if tokens.count(t) > 1]
        raise RuleBuilderError(
            f"'naming_tokens' contains duplicate entries: {sorted(set(duplicates))!r}."
        )

    if not separator:
        raise RuleBuilderError("'naming_separator' cannot be empty.")

    # Validate separator against its own declared rule.
    sep_rule = global_rules.separator_rule
    if sep_rule is not None and sep_rule.type == "regex":
        if not isinstance(sep_rule.value, str):
            raise RuleBuilderError(
                "The separator_rule has type 'regex' but its 'value' is not a string."
            )
        if not re.fullmatch(sep_rule.value, separator):
            raise RuleBuilderError(
                f"Separator '{separator}' does not satisfy its own rule "
                f"(pattern: '{sep_rule.value}')."
            )

    # Token names must be valid Python identifiers because they are used
    # as named groups in the matching regex (e.g. ``(?P<descriptor>...)``).
    _IDENTIFIER_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    for token in tokens:
        if not _IDENTIFIER_RE.match(token):
            raise RuleBuilderError(
                f"Token name '{token}' is not a valid Python identifier. "
                "Token names are used as regex named groups and must match "
                r"'^[a-zA-Z_][a-zA-Z0-9_]*$'."
            )

    # Warn about tokens that have no rule — they accept any value.
    # This is intentional (the Manager falls back to a catch-all pattern),
    # but worth surfacing during validation for transparency.
    rule_less = [t for t in tokens if t not in token_rules]
    if rule_less:
        import logging

        logging.getLogger(__name__).warning(
            "The following tokens have no validation rule and will accept any value: %s",
            rule_less,
        )


# ---------------------------------------------------------------------------
# Module-level assembly — executed once at import time
# ---------------------------------------------------------------------------

TOKENS: List[str] = list(SETTINGS.naming.tokens)
SEPARATOR: str = SETTINGS.naming.separator
TOKEN_RULES, _GLOBAL_RULES_OBJ = build_rules()
NORMALIZERS: Dict[str, Normalizer] = build_normalizers()

validate_convention(TOKENS, SEPARATOR, TOKEN_RULES, _GLOBAL_RULES_OBJ)

GLOBAL_RULES: GlobalRules = _GLOBAL_RULES_OBJ
