"""Data schemas for OpenRig configuration.

Defines the core data contracts used throughout the system, split into
two groups:

**Naming system types** (used by ``rules.py``, ``manager.py``):
    - ``TokenValue``: accepted raw input for a token before normalization.
    - ``TokenData``: canonical post-normalization form (always ``str`` values).
    - ``RuleValidator``: ``Protocol`` that every rule type must satisfy.
    - ``RegexRule``, ``ListRule``, ``CallableRule``: concrete rule implementations.
    - ``ConcreteRule``: union of all concrete rule types.
    - ``RuleConfig``, ``GlobalRules``: intermediate config representations.

**Settings dataclasses** (populated by ``settings.py`` from ``config.json``):
    - ``RiggingSettings``: rigging conventions (side, rotate order, axes).
    - ``NamingSettings``: naming convention (separator, tokens, rules, normalizers).
    - ``ShapesSettings``: control curve shape defaults.
    - ``ColorsSettings``: color conventions per side/usage (reserved).
    - ``ExportSettings``: export paths and format defaults (reserved).
    - ``SkinSettings``: skinning configuration defaults (reserved).
    - ``Settings``: root dataclass aggregating all sections.

Each settings section corresponds directly to a top-level key in
``config.json``, making it trivial to locate any value's origin.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Dict,
    FrozenSet,
    List,
    Mapping,
    Optional,
    Protocol,
    Tuple,
    Union,
    runtime_checkable,
)

# ---------------------------------------------------------------------------
# Token value types
# ---------------------------------------------------------------------------

# TokenValue: accepted raw input for a token (before normalization).
# Enum members are accepted so callers can pass e.g. Side.LEFT directly.
TokenValue = Union[str, Enum]

# TokenData: canonical internal representation after normalization.
# Every value is a plain str; empty string means "token not provided".
TokenData = Dict[str, str]


# ---------------------------------------------------------------------------
# Rule Protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class RuleValidator(Protocol):
    """Protocol for all token-level validation rules.

    Any object that implements ``validate`` and ``to_regex_pattern``
    satisfies this protocol. This replaces the previous
    ``Union[List, str, Callable]`` type alias, eliminating the need for
    ``isinstance`` branching in the ``Manager``.

    Example:
        >>> class MyRule:
        ...     def validate(self, value: str) -> bool:
        ...         return value.isalpha()
        ...     def to_regex_pattern(self) -> str:
        ...         return r"[a-zA-Z]+"
    """

    def validate(self, value: str) -> bool:
        """Validates a normalized token value.

        Args:
            value: The normalized (post-normalization) string value to check.

        Returns:
            ``True`` if the value is acceptable, ``False`` otherwise.
        """
        ...

    def to_regex_pattern(self) -> str:
        """Returns a regex pattern representing the valid values for this rule.

        Used by the ``Manager`` to build the global matching regex without
        inspecting the rule's internal structure.

        Returns:
            A regex pattern string (without anchors ``^`` / ``$``).
        """
        ...


# ---------------------------------------------------------------------------
# Concrete rule implementations
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RegexRule:
    """A rule that validates a token value against a regular expression.

    Attributes:
        pattern: The regex pattern string. Anchors ``^`` / ``$`` are
            optional; ``validate`` always performs a full match.

    Example:
        >>> rule = RegexRule(pattern=r"^[a-z][a-zA-Z0-9]*$")
        >>> rule.validate("armUpper")
        True
        >>> rule.validate("Arm Upper")
        False
    """

    pattern: str

    def __post_init__(self) -> None:
        """Validates that the pattern compiles correctly on construction."""
        try:
            re.compile(self.pattern)
        except re.error as exc:
            raise ValueError(
                f"RegexRule received an invalid pattern '{self.pattern}': {exc}"
            ) from exc

    def validate(self, value: str) -> bool:
        """Validates the value against the compiled regex pattern.

        Args:
            value: The normalized token value.

        Returns:
            ``True`` if the value matches the full pattern.
        """
        return bool(re.fullmatch(self.pattern, value))

    def to_regex_pattern(self) -> str:
        """Returns the raw pattern, stripping leading/trailing anchors.

        Returns:
            The pattern string ready for embedding in a larger regex.
        """
        pattern = self.pattern
        if pattern.startswith("^"):
            pattern = pattern[1:]
        if pattern.endswith("$"):
            pattern = pattern[:-1]
        return pattern


@dataclass(frozen=True)
class ListRule:
    """A rule that validates a token value against a fixed set of allowed values.

    Attributes:
        allowed: A frozenset of accepted string values.

    Example:
        >>> rule = ListRule(allowed=frozenset({"l", "r", "c", "m"}))
        >>> rule.validate("l")
        True
        >>> rule.validate("left")
        False
    """

    allowed: FrozenSet[str]

    def validate(self, value: str) -> bool:
        """Checks membership in the allowed set.

        Args:
            value: The normalized token value.

        Returns:
            ``True`` if ``value`` is in the allowed set.
        """
        return value in self.allowed

    def to_regex_pattern(self) -> str:
        """Returns an alternation pattern of all allowed values, sorted by length.

        Sorting by length descending prevents shorter alternatives from
        shadowing longer ones in the regex engine.

        Returns:
            A non-capturing alternation group, e.g. ``(?:left|right|l|r)``.
        """
        options = sorted(self.allowed, key=len, reverse=True)
        escaped = [re.escape(opt) for opt in options if opt]
        if not escaped:
            return r"[^\s]+"
        return f"(?:{'|'.join(escaped)})"


@dataclass(frozen=True)
class CallableRule:
    """A rule that delegates validation to an arbitrary callable.

    The callable must accept a single ``str`` argument and return ``bool``.
    Because callable rules are opaque to the regex engine,
    ``to_regex_pattern`` returns a catch-all pattern; validation must be
    performed separately via ``validate``.

    Attributes:
        func: The validation callable. Typed as ``object`` to avoid
            hashability issues; narrowed at call site.
        name: A human-readable label used in error messages and ``__repr__``.

    Example:
        >>> rule = CallableRule(func=str.isalpha, name="alpha_only")
        >>> rule.validate("arm")
        True
        >>> rule.validate("arm1")
        False
    """

    func: object
    name: str

    def validate(self, value: str) -> bool:
        """Calls the wrapped function with the value.

        Args:
            value: The normalized token value.

        Returns:
            ``True`` if the function returns a truthy result.

        Raises:
            TypeError: If the stored ``func`` is not callable.
        """
        if not callable(self.func):
            raise TypeError(
                f"CallableRule '{self.name}' holds a non-callable: {self.func!r}"
            )
        return bool(self.func(value))

    def to_regex_pattern(self) -> str:
        """Returns a permissive catch-all pattern.

        Returns:
            A catch-all pattern ``[^\\s]+``.
        """
        return r"[^\s]+"


# Concrete union: the type stored in Manager.rules.
ConcreteRule = Union[RegexRule, ListRule, CallableRule]


# ---------------------------------------------------------------------------
# Intermediate naming config dataclasses
# ---------------------------------------------------------------------------


@dataclass
class RuleConfig:
    """Raw deserialized configuration for a single token rule.

    Intermediate representation populated from ``config.json``.
    ``rules.py`` converts each instance into a ``ConcreteRule``.

    Attributes:
        type: Rule type: ``"regex"``, ``"list"``, ``"from_enums"``,
            or ``"callable"``.
        value: Primary payload — pattern string, list of values, or
            dotted import path, depending on ``type``.
        sources: Enum class names to aggregate. Only for ``"from_enums"``.
    """

    type: str
    value: Union[str, List[str], None] = None
    sources: Optional[List[str]] = None


@dataclass
class GlobalRules:
    """Global constraints applied to every fully-built name.

    Attributes:
        max_length: Maximum allowed character length for any built name.
        forbidden_patterns: Substrings that must not appear in any built name.
        separator_rule: Optional ``RuleConfig`` constraining valid separators.
    """

    max_length: int
    forbidden_patterns: List[str] = field(default_factory=lambda: [])
    separator_rule: Optional[RuleConfig] = None


# ---------------------------------------------------------------------------
# Settings dataclasses — one per config.json top-level section
# ---------------------------------------------------------------------------


@dataclass
class RiggingSettings:
    """Rigging convention defaults from ``config.json["rigging"]``.

    These values drive the default class attributes on ``Side``,
    ``RotateOrder``, ``Axis``, and ``ShapeType`` in ``constants.py``.

    Attributes:
        side_default: Default side token (e.g. ``"c"``).
        rotate_order_default: Default rotate order string (e.g. ``"xyz"``).
        axis_aim: Default aim axis (e.g. ``"X"``).
        axis_up: Default up axis (e.g. ``"Y"``).
        axis_side: Default side axis (e.g. ``"Z"``).
    """

    side_default: str
    rotate_order_default: str
    axis_aim: str
    axis_up: str
    axis_side: str


@dataclass
class NamingSettings:
    """Naming convention configuration from ``config.json["naming"]``.

    Attributes:
        separator: Token separator character (e.g. ``"_"``).
        tokens: Ordered tuple of token names.
        rules: Mapping from token name (or ``"__global__"``) to its parsed
            rule configuration object.
        normalizers: Mapping from token name to normalizer function name.
    """

    separator: str
    tokens: Tuple[str, ...]
    rules: Mapping[str, Union[RuleConfig, GlobalRules]]
    normalizers: Mapping[str, str]


@dataclass
class ShapesSettings:
    """Control curve shape defaults from ``config.json["shapes"]``.

    Attributes:
        default: The default shape type string (e.g. ``"circle"``).
    """

    default: str = "circle"


@dataclass
class ColorsSettings:
    """Color convention defaults from ``config.json["colors"]``.

    Reserved for future use. Fields will be added as the color convention
    is defined (e.g. colors indexed by side or usage type).
    """


@dataclass
class ExportSettings:
    """Export defaults from ``config.json["export"]``.

    Reserved for future use. Fields will be added as export paths,
    formats, and options are defined.
    """


@dataclass
class SkinSettings:
    """Skinning configuration defaults from ``config.json["skin"]``.

    Reserved for future use. Fields will be added as skinning workflow
    defaults are defined.
    """


@dataclass
class Settings:
    """Root configuration dataclass for OpenRig.

    Aggregates all section-level settings. Each attribute corresponds
    directly to a top-level key in ``config.json``.

    Populated by ``settings.py`` on module load and consumed throughout
    the project via the module-level ``SETTINGS`` constant.

    Attributes:
        rigging: Rigging convention defaults.
        naming: Naming convention configuration.
        shapes: Control curve shape defaults.
        colors: Color convention defaults (reserved for future use).
        export: Export defaults (reserved for future use).
        skin: Skinning configuration defaults (reserved for future use).

    Example:
        >>> from openrig.settings import SETTINGS
        >>> SETTINGS.rigging.side_default
        'c'
        >>> SETTINGS.naming.separator
        '_'
        >>> SETTINGS.shapes.default
        'circle'
    """

    rigging: RiggingSettings
    naming: NamingSettings
    shapes: ShapesSettings
    colors: ColorsSettings = field(default_factory=ColorsSettings)
    export: ExportSettings = field(default_factory=ExportSettings)
    skin: SkinSettings = field(default_factory=SkinSettings)
