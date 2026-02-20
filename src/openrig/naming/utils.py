"""String manipulation utilities for the OpenRig naming system.

Provides validators, getters, converters, and incrementers for building
and transforming name strings used throughout the rigging pipeline.

Categories:
    Validators: ``is_string``, ``is_digit``, ``is_camel_case``, etc.
    Getters: ``get_digits``, ``get_version``, ``get_namespace``, etc.
    Converters: ``to_camel_case``, ``to_snake_case``, ``to_kebab_case``, etc.
    Incrementers: ``increment_digit``, ``increment_character``, etc.
    Decrementers: ``decrement_digit``, ``decrement_character``, etc.
"""

import re
from typing import Iterable

# Compiled Regex Patterns for performance
_CAMEL_CASE_RE = re.compile(r"^[a-z][a-z0-9]*([A-Z][a-z0-9]*)*$")
_PASCAL_CASE_RE = re.compile(r"^[A-Z][a-z0-9]*([A-Z][a-z0-9]*)*$")
_SNAKE_CASE_RE = re.compile(r"^[a-z]+(_[a-z0-9]+)*$")
_KEBAB_CASE_RE = re.compile(r"^[a-z]+(-[a-z0-9]+)*$")
_DIGITS_RE = re.compile(r"\d+")
_BRACKETS_DIGITS_RE = re.compile(r"\[([^\]]+)\]")
_UNDERSCORE_DATA_RE = re.compile(r"(?<=_)[^_]+(?=_)")
_NORMALIZE_RE = re.compile(r"[^a-zA-Z0-9]+")
_SPLIT_TEXT_DELIM_RE = re.compile(r"[_\-\s\.]+")
_SPLIT_TEXT_WORDS_RE = re.compile(
    r"[A-Z]+(?=[A-Z][a-z])|[A-Z][a-z0-9]+|[A-Z]+|[a-z]+|[0-9]+"
)
_CLEAN_TXT_INVALID_RE = re.compile(r"[^a-zA-Z0-9_]")
_INCREMENT_DIGIT_RE = re.compile(r"(\d+)$")
_VERSION_RE = re.compile(r"[vV](\d+)")
_SIDE_MAPPING = {
    "_L_": "_R_",
    "_R_": "_L_",
    "_l_": "_r_",
    "_r_": "_l_",
    "L_": "R_",
    "R_": "L_",
    "l_": "r_",
    "r_": "l_",
    "_L": "_R",
    "_R": "_L",
    "_l": "_r",
    "_r": "_l",
    "_C_": "_C_",
    "_c_": "_c_",
    "Left": "Right",
    "Right": "Left",
    "_Left": "_Right",
    "_Right": "_Left",
    "Center": "Center",
    "center": "center",
    "Middle": "Middle",
    "middle": "middle",
    "_M_": "_M_",
    "_m_": "_m_",
    "M_": "M_",
    "m_": "m_",
    "_M": "_M",
    "_m": "_m",
    "left": "right",
    "right": "left",
    "_left": "_right",
    "_right": "_left",
}


# VALIDATORS
def is_string(text: object) -> bool:
    """Validates whether a variable is a string.

    Args:
        text: The value to validate.

    Returns:
        True if ``text`` is a ``str`` instance, False otherwise.
    """
    return isinstance(text, str)


def is_digit(value: object) -> bool:
    """Validates whether a variable is a number.

    Args:
        value: The value to validate.

    Returns:
        True if ``value`` is an ``int`` or ``float`` instance, False otherwise.
    """
    return isinstance(value, (int, float))


def is_camel_case(text: str) -> bool:
    """Validates if a text is in camelCase style.

    Args:
        text: Text to validate.

    Returns:
        True if the text is in camelCase style, False otherwise.
    """
    return bool(_CAMEL_CASE_RE.fullmatch(text))


def is_pascal_case(text: str) -> bool:
    """Validates if a text is in PascalCase style.

    Args:
        text: String to validate.

    Returns:
        True if the text is in PascalCase style, False otherwise.
    """
    return bool(_PASCAL_CASE_RE.fullmatch(text))


def is_snake_case(text: str) -> bool:
    """Validates if a text is in snake_case style.

    Args:
        text: String to validate.

    Returns:
        True if the text is in snake_case style, False otherwise.
    """
    return bool(_SNAKE_CASE_RE.fullmatch(text))


def is_kebab_case(text: str) -> bool:
    """Validates if a text is in kebab-case style.

    Args:
        text: String to validate.

    Returns:
        True if the text is in kebab-case style, False otherwise.
    """
    return bool(_KEBAB_CASE_RE.fullmatch(text))


def is_character_in(text: str, character: str = "_") -> bool:
    """Validates if a character is in a text.

    Args:
        text: Text to look for.
        character: Character to validate. Defaults to '_'.

    Returns:
        True if the character is in the text, False otherwise.
    """
    return bool(character in text)


# GETTERS
def get_case_style(text: str) -> str:
    """Determines the naming style of a given text.

    Args:
        text: The text to determine style.

    Returns:
        The naming style of the text. Possible values are:
        "camelCase", "PascalCase", "snake_case", "kebab-case", or "unknown".
    """
    if is_camel_case(text):
        return "camelCase"
    if is_pascal_case(text):
        return "PascalCase"
    if is_snake_case(text):
        return "snake_case"
    if is_kebab_case(text):
        return "kebab-case"

    return "unknown"


def get_digits(text: str) -> list[str]:
    """Gets digits inside a text.

    Args:
        text: Text to extract digits.

    Returns:
        List of string digits from the original text.
    """
    return _DIGITS_RE.findall(text)


def get_digit_by_index(text: str, index: int = 0) -> str | None:
    """Gets the digit inside a text at a specific index.

    Args:
        text: Text to extract digits.
        index: Index of the digit to extract. Defaults to 0.

    Returns:
        Digit from the original text.
    """
    digit = get_digits(text)

    if digit and 0 <= index < len(digit):
        return digit[index]
    return None


def get_first_digit(text: str) -> str | None:
    """Gets the first digit inside a text.

    Args:
        text: Text to extract digits.

    Returns:
        First digit from the original string.
    """
    digit = get_digits(text)

    return digit[0] if digit else None


def get_last_digit(text: str) -> str | None:
    """Gets the last digit inside a string.

    Args:
        text: Text to extract digits.

    Returns:
        Last digit from the original text.
    """
    digit = get_digits(text=text)

    return digit[-1] if digit else None


def get_digits_between_brackets(text: str) -> list[str]:
    """Gets all digits between brackets inside a text.

    Args:
        text: The text to extract digits from.

    Returns:
        List of strings representing the numeric digits found between square brackets.
    """
    results: list[str] = _BRACKETS_DIGITS_RE.findall(text)

    numeric_results: list[str] = []
    for item in results:
        digits: list[str] = _DIGITS_RE.findall(item)
        numeric_results.extend(digits)

    return numeric_results if numeric_results else []


def get_data_between_underscores(text: str) -> list[str]:
    """Gets all data between underscores inside a text.

    Args:
        text: The text to extract data from.

    Returns:
        List of strings representing the data found between underscores.
    """
    # Use lookarounds to handle overlapping matches (e.g. 'a_b_c' -> 'b')
    return _UNDERSCORE_DATA_RE.findall(text)


def get_version(text: str) -> int | None:
    """Extracts the version number from a text (e.g., 'v001' -> 1).

    Args:
        text: Text to extract version from.

    Returns:
        The version number as an integer, or None if not found.
    """
    match = _VERSION_RE.search(text)
    if match:
        return int(match.group(1))
    return None


def get_namespace(text: str, separator: str = ":") -> str:
    """Extracts the namespace prefix from a string.

    Args:
        text: The string to process (e.g., 'namespace:item').
        separator: The separator character. Defaults to ':'.

    Returns:
        The namespace string, or empty string if none.
    """
    if separator in text:
        return text.rpartition(separator)[0]
    return ""


# CONVERTERS
def replace_spaces(text: str, replacement: str) -> str:
    """Replaces spaces in the given text with a specified character.

    Args:
        text: The input text.
        replacement: Specified character to replace with.

    Returns:
        The input text with spaces replaced by the given replacement.
    """
    return text.replace(" ", replacement)


def normalize_text(text: str) -> str:
    """Normalizes text by replacing non-alphanumeric characters with spaces.

    Args:
        text: Text to normalize.

    Returns:
        Normalized text.
    """
    return _NORMALIZE_RE.sub(" ", text)


def to_upper(text: str) -> str:
    """Converts a text to uppercase.

    Args:
        text: Text to convert.

    Returns:
        Uppercase text.
    """
    return text.upper()


def to_lower(text: str) -> str:
    """Converts a text to lowercase.

    Args:
        text: Text to convert.

    Returns:
        Lowercase text.
    """
    return text.lower()


def to_camel_case(text: str, remove_digits: bool = False) -> str:
    """Converts a text to camelCase.

    Args:
        text: Text to convert to camelCase.
        remove_digits: Remove digits from the text. Defaults to False.

    Returns:
        camelCase string.
    """
    split_words = split_text(text)

    camel_case = split_words[0].lower()

    for word in split_words[1:]:
        camel_case += word.capitalize()

    if remove_digits:
        camel_case = strip_digits(camel_case)

    return camel_case


def to_pascal_case(text: str, remove_digits: bool = False) -> str:
    """Converts a text to PascalCase.

    Args:
        text: Text to convert to PascalCase.
        remove_digits: Remove digits from the text. Defaults to False.

    Returns:
        PascalCase string.
    """
    split_words = split_text(text)

    pascal_case = ""
    for word in split_words:
        pascal_case += word.capitalize()

    if remove_digits:
        pascal_case = strip_digits(pascal_case)

    return pascal_case


def to_snake_case(text: str, remove_digits: bool = False) -> str:
    """Converts a text to snake_case.

    Args:
        text: Text to convert to snake_case.
        remove_digits: Remove digits from the text. Defaults to False.

    Returns:
        snake_case string.
    """
    split_words = split_text(text)
    snake_case = "_".join(word.lower() for word in split_words)

    if remove_digits:
        snake_case = strip_digits(snake_case)
        # Re-split and join to handle multiple separators from stripping digits
        snake_case = "_".join(word.lower() for word in split_text(snake_case))

    return snake_case


def to_kebab_case(text: str, remove_digits: bool = False) -> str:
    """Converts a text to kebab-case.

    Args:
        text: Text to convert to kebab-case.
        remove_digits: Remove digits from the text. Defaults to False.

    Returns:
        kebab-case string.
    """
    split_words = split_text(text)
    kebab_case = "-".join(word.lower() for word in split_words)

    if remove_digits:
        kebab_case = strip_digits(kebab_case)
        # Re-split and join to handle multiple separators from stripping digits
        kebab_case = "-".join(word.lower() for word in split_text(kebab_case))

    return kebab_case


def value_to_str(value: float | int) -> str:
    """Converts a numeric value to a filesystem-safe string in ``MxDx`` format.

    The ``M`` prefix indicates a negative value; the decimal point is
    replaced by ``d`` (e.g. ``-1.5`` → ``"M1d5"``, ``2.0`` → ``"2d0"``).

    Args:
        value: The numeric value to encode.

    Returns:
        The encoded string representation.
    """
    sign = ""
    if value < 0:
        sign = "M"
        value = abs(value)  # Convert value to positive

    return f"{sign}{value}".replace(".", "d")


def str_to_value(text: str) -> float:
    """Converts a formatted ``MxDx`` string back into a numeric value.

    Reverses the encoding applied by ``value_to_str``: strips the ``M``
    sign prefix and replaces ``d`` with a decimal point.

    Args:
        text: Formatted text to convert into a digit.

    Returns:
        The corresponding numerical value.
    """
    sign = 1
    if text[0] == "M":
        sign = -1
        text = text[1:]

    return float(text.replace("d", ".")) * sign


def strip_digits(text: str) -> str:
    """Removes digits from a text.

    Args:
        text: Text to remove digits from.

    Returns:
        Text without digits.
    """
    return _DIGITS_RE.sub("", text)


def split_text(text: str) -> list[str]:
    """Splits text into individual words.

    Handles camelCase, PascalCase, and delimiters like ``_`` and ``-``.

    Args:
        text: The text to split.

    Returns:
        A list of words.
    """
    text = _SPLIT_TEXT_DELIM_RE.sub(" ", text)
    return _SPLIT_TEXT_WORDS_RE.findall(text)


def join_tokens(tokens: Iterable[str | None], separator: str = "_") -> str:
    """Joins a sequence of tokens, filtering out None or empty strings.

    Args:
        tokens: A sequence of tokens (strings or None).
        separator: The separator to use. Defaults to '_'.

    Returns:
        The joined string.
    """
    return separator.join(t for t in tokens if t)


def capitalize_first(text: str) -> str:
    """Capitalizes the first letter of a text.

    Args:
        text: Text to capitalize.

    Returns:
        Text with the first letter capitalized.
    """
    if len(text) == 1:
        return text.upper()

    return text[0].upper() + text[1:]


def remove_prefix(text: str, prefix: str) -> str:
    """Removes a prefix from a text.

    Args:
        text: Text to remove prefix from.
        prefix: Prefix to remove.

    Returns:
        Text without prefix.
    """
    return text.removeprefix(prefix)


def remove_suffix(text: str, suffix: str) -> str:
    """Removes a suffix from a text.

    Args:
        text: Text to remove suffix from.
        suffix: Suffix to remove.

    Returns:
        Text without suffix.
    """
    return text.removesuffix(suffix)


def clean_txt(text: str, replace_with: str = "_") -> str:
    """Cleans a string by replacing illegal characters.

    Ensures the result does not start with a digit by prepending
    ``replace_with`` if necessary.

    Args:
        text: Text to clean.
        replace_with: Character to replace illegal characters with. Defaults to '_'.

    Returns:
        Cleaned text.
    """
    text = _CLEAN_TXT_INVALID_RE.sub(replace_with, text)
    if replace_with:
        text = re.sub(f"{re.escape(replace_with)}+", replace_with, text)
    if text and text[0].isdigit():
        text = f"{replace_with}{text}"
    return text


def strip_namespace(text: str, separator: str = ":") -> str:
    """Removes the namespace prefix from a string.

    Args:
        text: The string to process.
        separator: The separator character. Defaults to ':'.

    Returns:
        The string without the namespace prefix.
    """
    if separator in text:
        return text.rpartition(separator)[2]
    return text


def get_base_name(text: str, separator: str = "|") -> str:
    """Returns the last component of a path-like string.

    Args:
        text: The path string (e.g. 'path/to/item').
        separator: The path separator. Defaults to '|'.

    Returns:
        The base name (leaf node).
    """
    return text.split(separator)[-1]


def truncate(text: str, max_length: int, ellipsis: str = "...") -> str:
    """Truncates a string to a maximum length.

    Args:
        text: The text to truncate.
        max_length: The maximum length including the ellipsis.
        ellipsis: The string to append to truncated text. Defaults to "...".

    Returns:
        The truncated string.
    """
    if len(text) <= max_length:
        return text
    return text[: max(0, max_length - len(ellipsis))] + ellipsis


def split_name_number(text: str) -> tuple[str, str | None]:
    """Splits a string into its name and trailing number components.

    Args:
        text: The text to split (e.g., 'arm01').

    Returns:
        A tuple containing the name and the number string (or None).
    """
    match = _INCREMENT_DIGIT_RE.search(text)
    if match:
        number = match.group(1)
        name = text[: match.start()]
        return name, number
    return text, None


def get_unique_name(name: str, existing_names: Iterable[str]) -> str:
    """Returns a unique name by incrementing the digit if it exists in the list.

    Args:
        name: The desired name.
        existing_names: Iterable of names that already exist.

    Returns:
        A unique name.
    """
    existing_set = set(existing_names)
    while name in existing_set:
        name = increment_digit(name)
    return name


# INCREMENTERS
def increment_character(text: str) -> str:
    """Increments a letter sequence in a manner similar to Excel column naming.

    - Works for both uppercase and lowercase sequences
    - Handles cases like 'ZZ' → 'AAA' and 'zz' → 'aaa'

    Args:
        text: A text containing only letters ('A'-'Z' or 'a'-'z').

    Returns:
        The incremented letter sequence.
    """
    # Convert string to list for mutability
    chars = list(text)
    # Check if the input is uppercase or lowercase
    is_upper = chars[0].isupper()
    start_char = "A" if is_upper else "a"
    end_char = "Z" if is_upper else "z"
    # Start from the last character
    i = len(chars) - 1
    while i >= 0:
        if chars[i] != end_char:
            chars[i] = chr(ord(chars[i]) + 1)  # Increment character
            return "".join(chars)
        else:
            chars[i] = start_char  # Reset current position to start character
            i -= 1
    # Prepend 'A' or 'a' if all characters were 'Z' or 'z'
    return start_char + "".join(chars)


def increment_digit(text: str, pads: int | None = None) -> str:
    """Increments the last digit in a text.

    Args:
        text: Text to increment.
        pads: Number of digits for padding.
              If None, uses existing padding or defaults to 2.

    Returns:
        Text with the last digit incremented, or a digit appended if none existed.
    """
    match = _INCREMENT_DIGIT_RE.search(text)
    if match:
        current_digit = match.group(1)
        padding = pads if pads is not None else len(current_digit)
        new_digit = int(current_digit) + 1
        incremented_digit = str(new_digit).zfill(padding)
        return text[: match.start()] + incremented_digit

    padding = pads if pads is not None else 2
    return f"{text}{'1'.zfill(padding)}"


def replace_padding(text: str, padding: int = 2) -> str:
    """Replaces the padding of the last number in the text.

    Args:
        text: Text to modify.
        padding: New padding size. Defaults to 2.

    Returns:
        Text with updated padding.
    """
    match = _INCREMENT_DIGIT_RE.search(text)
    if match:
        digit = match.group(1)
        new_digit = str(int(digit)).zfill(padding)
        return text[: match.start()] + new_digit
    return text


def add_suffix(text: str, suffix: str, separator: str = "_") -> str:
    """Adds a suffix to a text using a separator.

    Args:
        text: Text to add the suffix to.
        suffix: The suffix to add.
        separator: The separator to use. Defaults to '_'.

    Returns:
        Text with the suffix added.
    """
    text = to_camel_case(text=text)
    if not suffix.isupper():
        suffix = to_camel_case(text=suffix)

    return f"{text}{separator}{suffix}"


def add_prefix(text: str, prefix: str, separator: str = "_") -> str:
    """Adds a prefix to a text using a separator.

    Args:
        text: Text to add the prefix to.
        prefix: The prefix to add.
        separator: The separator to use. Defaults to '_'.

    Returns:
        Text with the prefix added.
    """
    text = to_camel_case(text=text)
    if not prefix.isupper():
        prefix = to_camel_case(text=prefix)

    return f"{prefix}{separator}{text}"


def add_text(text: str, text_to_add: str = "") -> str:
    """Adds a text to another text in PascalCase.

    Args:
        text: The text to add to.
        text_to_add: The text to add. Defaults to ''.

    Returns:
        The text with the text_to_add added.
    """
    if text_to_add:
        text_to_add = to_pascal_case(text=text_to_add)

    return f"{text}{text_to_add}"


def swap_substrings(text: str, mapping: dict[str, str] | None = None) -> str:
    """Swaps substrings in a text based on a mapping dictionary.

    Performs a simultaneous replacement of all keys found in the mapping.
    This prevents double-swapping (e.g. L->R then R->L) and ensures robustness.

    Args:
        text: The text to process.
        mapping: Dictionary mapping substrings (e.g., {'_L_': '_R_'}).
                 If None, defaults to a standard side mapping (L/R, Left/Right).

    Returns:
        The text with substrings swapped if matches are found.
    """
    mapping = mapping or _SIDE_MAPPING

    # Create a regex pattern that matches any of the keys
    # Sort keys by length descending to match longest keys first (e.g. 'Left' - 'L')
    pattern = re.compile(
        "|".join(re.escape(k) for k in sorted(mapping, key=len, reverse=True))
    )

    return pattern.sub(lambda m: mapping[m.group(0)], text)


# DECREMENTERS
def decrement_character(text: str) -> str:
    """Decrements a letter sequence in a manner similar to Excel column naming.

    - Works for both uppercase and lowercase sequences
    - Handles cases like 'AAA' → 'ZZ' and 'aaa' → 'zz'

    Args:
        text: A text containing only letters ('A'-'Z' or 'a'-'z').

    Returns:
        The decremented letter sequence.
    """
    chars = list(text)
    is_upper = chars[0].isupper()
    start_char = "A" if is_upper else "a"
    end_char = "Z" if is_upper else "z"
    i = len(chars) - 1
    while i >= 0:
        if chars[i] != start_char:
            chars[i] = chr(ord(chars[i]) - 1)
            return "".join(chars)
        else:
            chars[i] = end_char
            i -= 1
    return "".join(chars[1:])


def decrement_digit(text: str, remove_if_one: bool = True) -> str:
    """Decrements the last digit in a text.

    Args:
        text: Text to decrement.
        remove_if_one: If True, removes the digit if it becomes 0 or 1.
                       Defaults to True.

    Returns:
        Text with the decremented digit, or the original text if no digit is found.
    """
    match = _INCREMENT_DIGIT_RE.search(text)
    if match:
        current_digit = match.group(1)
        current_value = int(current_digit)
        if remove_if_one and current_value <= 1:
            return text[: match.start()]
        if current_value <= 0:
            return text
        digits = len(current_digit)
        decremented_digit = str(current_value - 1).zfill(digits)
        return text[: match.start()] + decremented_digit

    return text
