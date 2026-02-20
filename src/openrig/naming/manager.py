"""Module for managing naming conventions in rigging.

This module provides the ``Manager`` class to validate, parse, and build
strings based on configurable naming rules and tokens.

The key design decisions that enable strict typing throughout:

- Token values flowing **in** (raw input from callers) are typed as
  ``TokenValue = Union[str, Enum]``, defined in ``schemas``.
- Token values flowing **internally** (after normalization) are always
  plain ``str``, represented as ``TokenData = Dict[str, str]``.
- Rules are ``ConcreteRule`` instances (``RegexRule``, ``ListRule``,
  ``CallableRule``) that expose a uniform ``validate`` / ``to_regex_pattern``
  interface, eliminating all ``isinstance`` branching over rule types.
- Global rules are stored as a typed ``GlobalRules`` dataclass instead of
  ``Dict[str, Any]``, so attribute access is fully type-safe.
- Serialization uses a ``ManagerConfig`` ``TypedDict`` so ``from_dict`` /
  ``to_dict`` round-trips are fully typed without ``Any``.
"""

from __future__ import annotations

import logging
import re
from enum import Enum
from typing import (
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    TypedDict,
    Union,
)

from openrig.schemas import (
    ConcreteRule,
    GlobalRules,
    TokenData,
    TokenValue,
)

from .normalizers import Normalizer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class NamingError(Exception):
    """Base exception for naming-related errors."""


class NamingConfigError(NamingError):
    """Raised when the Manager is configured with invalid parameters."""


class NamingValidationError(NamingError):
    """Raised when a name or token value fails validation."""


# ---------------------------------------------------------------------------
# Serialization contract
# ---------------------------------------------------------------------------


class ManagerConfig(TypedDict, total=False):
    """Typed dictionary representing the serializable state of a ``Manager``.

    Used by ``Manager.from_dict`` and ``Manager.to_dict`` to provide a
    fully typed round-trip without resorting to ``Dict[str, Any]``.

    Attributes:
        tokens: Ordered list of token name strings.
        separator: The separator character.
        rules: Mapping of token name to its ``ConcreteRule``.
        normalizers: Mapping of token name to its normalizer callable.
        global_rules: The global naming constraints.
    """

    tokens: List[str]
    separator: str
    rules: Dict[str, ConcreteRule]
    normalizers: Dict[str, Normalizer]
    global_rules: GlobalRules


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------


class Manager:
    """Manages naming conventions by validating and operating on strings.

    Builds, parses, and validates names according to a configurable token
    structure. All token values are normalized to plain strings before
    validation, so callers may pass raw ``str`` or ``Enum`` members.

    Attributes:
        tokens: Ordered list of token name strings.
        separator: Character used to join token values.
        rules: Mapping of token name to its ``ConcreteRule``.
        normalizers: Mapping of token name to its normalizer callable.
        global_rules: Global constraints applied to every built name.

    Example:
        >>> from openrig.schemas import RegexRule, ListRule, GlobalRules
        >>> manager = Manager(
        ...     tokens=["descriptor", "side", "usage"],
        ...     separator="_",
        ...     rules={
        ...         "descriptor": RegexRule(pattern=r"^[a-z][a-zA-Z0-9]*$"),
        ...         "side": ListRule(allowed=frozenset({"l", "r", "c"})),
        ...     },
        ...     global_rules=GlobalRules(max_length=80),
        ... )
        >>> manager.build_name(descriptor="arm", side="l", usage="jnt")
        'arm_l_jnt'
    """

    tokens: List[str]
    separator: str
    rules: Dict[str, ConcreteRule]
    normalizers: Dict[str, Normalizer]
    global_rules: GlobalRules

    def __init__(
        self,
        tokens: Optional[Sequence[str]] = None,
        separator: Optional[str] = None,
        rules: Optional[Dict[str, ConcreteRule]] = None,
        normalizers: Optional[Dict[str, Normalizer]] = None,
        global_rules: Optional[GlobalRules] = None,
    ) -> None:
        """Initializes the naming Manager.

        Args:
            tokens: Ordered sequence of token name strings.
            separator: Character used to join token values. Must not be empty.
            rules: Mapping of token name to its ``ConcreteRule``. Tokens
                without a rule accept any value.
            normalizers: Mapping of token name to its normalizer callable.
                Normalizers are applied before validation.
            global_rules: Global constraints (max length, forbidden patterns).
                Defaults to an unconstrained ``GlobalRules`` instance.

        Raises:
            NamingConfigError: If ``separator`` is ``None`` or empty.
        """
        self.tokens = list(tokens or [])
        if not separator:
            raise NamingConfigError("Separator must be a non-empty string.")
        self.separator = separator
        self.rules = dict(rules or {})
        self.normalizers = dict(normalizers or {})
        self.global_rules = global_rules or GlobalRules(max_length=0)
        self._regex_cache: Dict[Tuple[bool, bool, bool], str] = {}

    def __repr__(self) -> str:
        """Returns a developer-friendly string representation."""
        return (
            f"<{self.__class__.__name__} "
            f"tokens={self.tokens} separator={self.separator!r}>"
        )

    # -----------------------------------------------------------------------
    # Serialization
    # -----------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: ManagerConfig) -> Manager:
        """Creates a ``Manager`` instance from a ``ManagerConfig`` dictionary.

        Args:
            data: A ``ManagerConfig`` typed dict containing the configuration.

        Returns:
            A new ``Manager`` instance.
        """
        return cls(
            tokens=data.get("tokens"),
            separator=data.get("separator"),
            rules=data.get("rules"),
            normalizers=data.get("normalizers"),
            global_rules=data.get("global_rules"),
        )

    def to_dict(self) -> ManagerConfig:
        """Exports the current configuration as a ``ManagerConfig`` dictionary.

        Returns:
            A ``ManagerConfig`` typed dict representing the current state.
        """
        return ManagerConfig(
            tokens=self.tokens,
            separator=self.separator,
            rules=self.rules,
            normalizers=self.normalizers,
            global_rules=self.global_rules,
        )

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _join_tokens(self, data: TokenData) -> str:
        """Joins normalized token values into a name string.

        Skips tokens whose value is an empty string.

        Args:
            data: A ``TokenData`` mapping of token name → normalized value.

        Returns:
            The assembled name string.
        """
        parts = [data[token] for token in self.tokens if data.get(token)]
        return self.separator.join(parts)

    def _normalize_token_value(self, token: str, value: TokenValue) -> str:
        """Normalizes a raw token value to a plain string.

        Processing order:
        1. Extract ``.value`` from ``Enum`` members.
        2. Apply the token's registered normalizer (if any).
        3. Convert to ``str`` and strip surrounding whitespace.

        Args:
            token: The token name.
            value: The raw input value (``str`` or ``Enum``).

        Returns:
            The normalized string value. Returns ``""`` for empty inputs.
        """
        # Step 1: unwrap Enum — isinstance narrows the type so Pylance
        # knows value.value is str after this branch.
        raw: str = str(value.value) if isinstance(value, Enum) else value

        if not raw:
            return ""

        # Step 2: apply registered normalizer
        normalizer = self.normalizers.get(token)
        if normalizer is not None:
            raw = normalizer(raw)

        # Step 3: final string coercion + strip
        return str(raw).strip()

    # -----------------------------------------------------------------------
    # Validators
    # -----------------------------------------------------------------------

    def is_valid(self, name: str) -> bool:
        """Returns ``True`` if ``name`` is fully valid against all tokens.

        A name is fully valid when it contains a non-empty, rule-conforming
        value for every token defined in the convention. For partial
        validation use ``get_data`` and inspect individual token values.

        Args:
            name: The candidate name string.

        Returns:
            ``True`` if the name is strictly valid, ``False`` otherwise.
        """
        if not name:
            return False

        regex = self.get_matching_regex(full_match=True, strict=True)
        if not re.match(regex, name):
            return False

        # Second pass: callable rules cannot be fully represented as regex,
        # so we validate each extracted token value explicitly.
        try:
            data = self.get_data(name)
            return all(
                self.is_valid_token(token, value)
                for token, value in data.items()
                if value
            )
        except Exception:
            return False

    def is_valid_token(self, token: str, value: str) -> bool:
        """Returns ``True`` if ``value`` is valid for the given token.

        Checks that the value does not contain the separator, then delegates
        to the token's ``ConcreteRule.validate`` method.

        Args:
            token: The token name.
            value: The normalized (post-normalization) string value.

        Returns:
            ``True`` if valid, ``False`` otherwise.
        """
        if self.separator in value:
            return False

        rule = self.rules.get(token)
        if rule is None:
            return True

        return rule.validate(value)

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def get_data(self, name: str) -> TokenData:
        """Extracts token values from a name string using the matching regex.

        Args:
            name: The name string to parse.

        Returns:
            A ``TokenData`` dict mapping every token name to its extracted
            value, or ``""`` for tokens not present in the name.
        """
        data: TokenData = {token: "" for token in self.tokens}
        regex = self.get_matching_regex(capture_groups=True, full_match=True)
        match = re.match(regex, name)
        if match:
            data.update({k: v for k, v in match.groupdict().items() if v is not None})
        return data

    def parse(self, name: str) -> Union[TokenData, str]:
        """Attempts to parse a name into its constituent token values.

        Tries in order:
        1. Regex-based extraction (strict structural match).
        2. Split-based extraction (loose positional match).
        3. Returns the original string if both fail.

        Args:
            name: The name string to parse.

        Returns:
            A ``TokenData`` dict if parsing succeeds, or the original
            ``str`` if the name does not conform to the convention.
        """
        if not name:
            return name

        # 1. Regex extraction
        data = self.get_data(name)
        if any(data.values()):
            return data

        # 2. Split extraction
        parts = name.split(self.separator)
        if len(parts) <= len(self.tokens):
            temp_data: TokenData = {token: "" for token in self.tokens}
            for i, part in enumerate(parts):
                token = self.tokens[i]
                if self.is_valid_token(token, part):
                    temp_data[token] = part
                else:
                    return name
            return temp_data

        return name

    def get_token_value(self, name: str, token_name: str) -> str:
        """Returns the value of a specific token extracted from a name.

        Args:
            name: The name string to extract from.
            token_name: The name of the token to retrieve.

        Returns:
            The extracted token value, or ``""`` if not present.

        Raises:
            NamingValidationError: If ``token_name`` is not defined in this
                manager's token list.
        """
        if token_name not in self.tokens:
            raise NamingValidationError(
                f"Token '{token_name}' is not defined. Available tokens: {self.tokens}."
            )
        return self.get_data(name)[token_name]

    def get_errors(self, name: str) -> List[str]:
        """Returns a list of human-readable validation errors for a name.

        Args:
            name: The name string to validate.

        Returns:
            A list of error message strings. Empty if the name is valid.
        """
        errors: List[str] = []

        if not name:
            errors.append("Name must be a non-empty string.")
            return errors

        parts = name.split(self.separator)
        if len(parts) > len(self.tokens):
            errors.append(
                f"Name has too many parts: expected at most {len(self.tokens)}, "
                f"got {len(parts)}."
            )

        for i, part in enumerate(parts):
            if i >= len(self.tokens):
                break
            if not self.is_valid_token(self.tokens[i], part):
                errors.append(f"Invalid value '{part}' for token '{self.tokens[i]}'.")

        if not errors and not self.is_valid(name):
            errors.append("Name does not match the required naming pattern.")

        return errors

    def get_matching_regex(
        self,
        capture_groups: bool = False,
        full_match: bool = True,
        strict: bool = False,
    ) -> str:
        """Generates a regex pattern matching names against this convention.

        Tokens are optional from right to left: for tokens
        ``["descriptor", "side", "usage"]`` the pattern matches
        ``"arm"``, ``"arm_l"``, and ``"arm_l_jnt"``, but never
        ``"arm__jnt"``.

        The pattern for each token is derived from its ``ConcreteRule``
        via ``rule.to_regex_pattern()``. Tokens without a rule use a
        catch-all pattern that excludes the separator.

        Results are cached by ``(capture_groups, full_match, strict)``.

        Args:
            capture_groups: If ``True``, wraps each token in a named
                capture group ``(?P<token_name>...)``.
            full_match: If ``True``, anchors the pattern with ``^`` / ``$``.
            strict: If ``True``, all tokens are required (no optional groups).

        Returns:
            The assembled regex pattern string.
        """
        cache_key = (capture_groups, full_match, strict)
        if cache_key in self._regex_cache:
            return self._regex_cache[cache_key]

        if not self.tokens:
            result = "^$" if full_match else ""
            self._regex_cache[cache_key] = result
            return result

        # 1. Build raw pattern per token via ConcreteRule.to_regex_pattern()
        raw_patterns: Dict[str, str] = {}
        for token in self.tokens:
            rule = self.rules.get(token)
            if rule is not None:
                raw_patterns[token] = rule.to_regex_pattern()
            else:
                # No rule: match anything except the separator
                if len(self.tokens) == 1:
                    raw_patterns[token] = ".+"
                elif len(self.separator) > 1:
                    raw_patterns[token] = f"(?:(?!{re.escape(self.separator)}).)+"
                else:
                    raw_patterns[token] = f"[^{re.escape(self.separator)}]+"

        # 2. Wrap in optional named capture groups
        token_patterns: Dict[str, str] = {}
        for token in self.tokens:
            raw = raw_patterns[token]
            if capture_groups:
                token_patterns[token] = f"(?P<{token}>{raw})"
            else:
                token_patterns[token] = f"(?:{raw})"

        # 3. Assemble final regex
        sep = re.escape(self.separator)

        if strict:
            final_regex = sep.join(token_patterns[t] for t in self.tokens)
        else:
            if len(self.tokens) == 1:
                final_regex = token_patterns[self.tokens[0]]
            else:
                final_regex = f"(?:{sep}{token_patterns[self.tokens[-1]]})?"
                for i in range(len(self.tokens) - 2, 0, -1):
                    tok = self.tokens[i]
                    final_regex = f"(?:{sep}{token_patterns[tok]}{final_regex})?"
                final_regex = token_patterns[self.tokens[0]] + final_regex

        result = f"^{final_regex}$" if full_match else final_regex
        self._regex_cache[cache_key] = result
        return result

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def add_rule(self, token: str, rule: ConcreteRule) -> None:
        """Adds or replaces the validation rule for a token.

        Clears the regex cache because the pattern depends on all rules.

        Args:
            token: The token name.
            rule: The ``ConcreteRule`` instance to associate with the token.
        """
        self._regex_cache.clear()
        self.rules[token] = rule

    def remove_rule(self, token: str) -> None:
        """Removes the validation rule for a token, if present.

        Clears the regex cache because the pattern depends on all rules.

        Args:
            token: The token name whose rule should be removed.
        """
        self._regex_cache.clear()
        self.rules.pop(token, None)

    # -----------------------------------------------------------------------
    # Builders
    # -----------------------------------------------------------------------

    def build_name(self, **kwargs: TokenValue) -> str:
        """Builds a name string from token values.

        Normalizes each provided value, validates it against the token's
        rule, joins all non-empty values with the separator, and then
        checks the result against the global rules.

        Args:
            **kwargs: Token values keyed by token name. Values may be
                ``str`` or ``Enum`` members; they are normalized before
                validation.

        Returns:
            The assembled name string.

        Raises:
            NamingValidationError: If unknown tokens are provided, if a
                normalized value fails its rule, or if the assembled name
                violates a global constraint.
        """
        unknown = [key for key in kwargs if key not in self.tokens]
        if unknown:
            raise NamingValidationError(
                f"Unknown tokens: {unknown}. Expected one of: {self.tokens}."
            )

        data: TokenData = {token: "" for token in self.tokens}

        for token in self.tokens:
            raw_value = kwargs.get(token, "")
            normalized = self._normalize_token_value(token, raw_value)
            if normalized and not self.is_valid_token(token, normalized):
                raise NamingValidationError(
                    f"Invalid value '{normalized}' for token '{token}' "
                    f"(separator: '{self.separator}')."
                )
            data[token] = normalized

        final_name = self._join_tokens(data)
        self._validate_global_rules(final_name)
        return final_name

    def update_name(self, name: str, **kwargs: TokenValue) -> str:
        """Updates specific token values in an existing name.

        Parses ``name`` into its token values, applies ``kwargs`` as
        overrides, then rebuilds the name.

        If ``name`` cannot be parsed against the full convention, it is
        treated as a bare descriptor (first token) provided it passes the
        first token's rule.

        Args:
            name: The existing name string to update.
            **kwargs: Token values to override. Same rules as ``build_name``.

        Returns:
            The updated name string.

        Raises:
            NamingValidationError: If ``name`` cannot be interpreted and is
                not empty, or if the updated values are invalid.
        """
        data: TokenData = self.get_data(name)
        is_parsed = any(data.values())

        if not is_parsed:
            if not name:
                # Empty name: build from kwargs only
                return self.build_name(**kwargs)

            first_token = self.tokens[0]
            if self.is_valid_token(first_token, name):
                data[first_token] = name
            else:
                raise NamingValidationError(
                    f"Could not parse '{name}' against tokens {self.tokens}, "
                    f"and it is not a valid value for the first token "
                    f"'{first_token}'."
                )

        # Merge overrides: normalize kwargs to str before updating TokenData
        for token, raw_value in kwargs.items():
            data[token] = self._normalize_token_value(token, raw_value)

        return self.build_name(**data)

    def resolve_name(
        self,
        value: Union[str, TokenData, Sequence[TokenValue]],
        tokens: Optional[List[str]] = None,
        rules: Optional[Dict[str, ConcreteRule]] = None,
        normalizers: Optional[Dict[str, Normalizer]] = None,
    ) -> str:
        """Resolves a flexible input into a final name string.

        Provides a unified entry point for callers that may supply names as
        dicts, sequences, or plain strings. When ``tokens``, ``rules``, or
        ``normalizers`` overrides are provided, a temporary ``Manager`` is
        created with those overrides applied on top of the current config.

        Supported ``value`` types:
        - ``dict`` (``TokenData``): passed directly to ``build_name``.
        - ``list`` / ``tuple`` (``Sequence[TokenValue]``): values are
          mapped positionally to tokens, then passed to ``build_name``.
        - ``str``: returned as-is (no building or validation).

        Args:
            value: The input to resolve.
            tokens: Optional token list override.
            rules: Optional rules override.
            normalizers: Optional normalizers override.

        Returns:
            The resolved name string.

        Raises:
            NamingValidationError: If a sequence input has more items than
                there are tokens.
        """
        if tokens is not None or rules is not None or normalizers is not None:
            temp = Manager(
                tokens=tokens if tokens is not None else self.tokens,
                separator=self.separator,
                rules=rules if rules is not None else self.rules,
                normalizers=normalizers
                if normalizers is not None
                else self.normalizers,
                global_rules=self.global_rules,
            )
            return temp.resolve_name(value)

        if isinstance(value, dict):
            return self.build_name(**value)

        if isinstance(value, (list, tuple)):
            if len(value) > len(self.tokens):
                raise NamingValidationError(
                    f"Input sequence has {len(value)} items but only "
                    f"{len(self.tokens)} tokens are defined."
                )
            token_data: TokenData = {
                token: self._normalize_token_value(token, val)
                for token, val in zip(self.tokens, value)
            }
            return self.build_name(**token_data)

        # Plain string: return as-is
        return str(value)

    # -----------------------------------------------------------------------
    # Private validation helpers
    # -----------------------------------------------------------------------

    def _validate_global_rules(self, name: str) -> None:
        """Validates a fully assembled name against the global rules.

        Args:
            name: The assembled name string.

        Raises:
            NamingValidationError: If ``name`` exceeds the maximum length or
                contains a forbidden pattern.
        """
        max_length = self.global_rules.max_length
        if max_length and len(name) > max_length:
            raise NamingValidationError(
                f"Name '{name}' exceeds the maximum length of {max_length} "
                f"(got {len(name)})."
            )

        for pattern in self.global_rules.forbidden_patterns:
            if pattern in name:
                raise NamingValidationError(
                    f"Name '{name}' contains the forbidden pattern '{pattern}'."
                )
