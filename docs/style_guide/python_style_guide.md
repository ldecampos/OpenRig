# Python Coding Style Guide

## Introduction

This style guide provides the coding conventions for Python projects at OpenRig. The goal is to improve code readability and maintain consistency across the entire codebase.

- PEP 8 -- Style Guide for Python Code for code style
- PEP 257 -- Docstring Conventions for documentation strings (docstrings).
- PEP 484 -- Type Hints for type annotations
- PEP 282 -- A Logging System for logging, and Google's conventions.

## 1. Code Layout & Imports (PEP 8)

### 1.1. Indentation

Use **4 spaces** per indentation level. Do not use tabs.

### 1.2. Maximum Line Length

Limit all lines to a maximum of **88 characters** (compatible with `black`) or 79 characters (strict PEP 8).

### 1.3. Blank Lines

- Surround top-level function and class definitions with **two blank lines**.
- Method definitions inside a class are surrounded by a **single blank line**.

### 1.4. Imports

Imports should be grouped in the following order:

1. Standard library imports.
2. Related third-party imports (e.g., `numpy`, `maya`).
3. Local application/library specific imports.

Put a blank line between each group of imports.

- **Yes:**

  ```python
  import os
  import sys

  import maya.cmds as cmds

  from openrig.core import base
  ```

- **No:**

  ```python
    import maya.cmds as cmds
    import os
    from openrig.core import base
    import sys
  ```

## 2. Naming (PEP 8)

Choosing sensible names is crucial. Follow these conventions to maintain clarity.

### 2.1. Variables

Variable names should be in `snake_case` (lowercase with underscores).

- **Yes:**

  ```python
  user_profile = get_user_profile()
  max_retries = 5
  ```

- **No:**

  ```python
  userProfile = get_user_profile() # Avoid camelCase
  MaxRetries = 5                   # Avoid PascalCase
  ```

### 2.2. Functions and Methods

Like variables, functions and methods should be in `snake_case`.

- **Yes:**

  ```python
  def calculate_total_value(quantity, value):
      # ...

  class User:
      def get_full_name(self):
          # ...
  ```

- **No:**

  ```python
  def CalculateTotalValue(quantity, value): # Avoid PascalCase
      # ...

  class User:
      def getFullName(self):                         # Avoid camelCase
          # ...
  ```

### 2.3. Classes

Class names should follow the `PascalCase` convention (also known as `CapWords`).

- **Yes:**

  ```python
  class OpenRigAgent:
      # ...

  class DiagramGenerateRequest(BaseModel):
      # ...
  ```

- **No:**

  ```python
  class open_rig_agent: # Avoid snake_case
      # ...
  ```

### 2.4. Modules

Python module names should be short, lowercase, and, if necessary, use underscores to improve readability.

- **Yes:**

  ``` python
  # File: src/openrig/utils/string_helpers.py
  import string_helpers
  ```

- **No:**

  ``` python
  # File: src/openrig/utils/StringHelpers.py
  import StringHelpers # Avoid PascalCase
  ```

### 2.5. Constants

Constants are declared at the module level and written in all capital letters with underscores separating words.

- **Yes:**

  ```python
  # In a module
  DEFAULT_MODEL = "gpt-4"
  MAX_WORKERS = 10
  ```

- **No:**

  ```python
  default_model = "gpt-4" # Avoid snake_case for constants
  ```

## 3. Docstrings (Google Style & PEP 257)

All public modules, functions, classes, and methods must have docstrings.

### 3.1. General Guidelines (PEP 257)

- The docstring is a string literal that appears as the first statement in the definition.
- Use `"""triple double quotes"""` for docstrings.
- The docstring should be concise and describe what the object does, not how it does it.
- The first line should be a short, imperative summary ending in a period.

### 3.2. Google Style for Functions and Methods

Function and method docstrings should contain:

1. A one-line summary ending in a period.
2. A more detailed description (optional, but recommended for complex functions). This section can explain behavior, algorithms, or side effects.
3. An `Args:` section to describe the arguments.
4. A `Returns:` section to describe the return value.
5. An optional `Raises:` section to describe any exceptions that are raised.

- **Complete Example:**

  ```python
  def build_name(self, **kwargs: object) -> str:
      """Builds a validated name from the given token values.

      Each keyword argument corresponds to a token defined in the active
      convention. Values are normalized before validation, so raw inputs
      such as ``"upper_arm"`` or ``Side.LEFT`` are accepted.

      Args:
          **kwargs: Token name/value pairs (e.g. ``descriptor="arm"``,
              ``side="l"``, ``usage="jnt"``).

      Returns:
          A fully validated name string built from the provided tokens.

      Raises:
          NamingValidationError: If any token value fails validation after
              normalization, or if the assembled name violates a global rule.
      """
      ...
  ```

- **Example with `Raises`:**

  ```python
  def _require_str(data: dict, key: str) -> str:
      """Extracts a required string value from a configuration dict.

      Args:
          data: The configuration dictionary to read from.
          key: The key whose value must be a non-empty string.

      Returns:
          The string value associated with *key*.

      Raises:
          NamingConfigError: If *key* is missing or its value is not a string.
      """
      value = data.get(key)
      if not isinstance(value, str):
          raise NamingConfigError(f"Expected string for '{key}', got {type(value)}")
      return value
  ```

### 3.3. Google Style for Classes

Class docstrings should contain:

1. A one-line summary.
2. A more detailed description of the class's purpose.
3. An `Attributes:` (or `Args:` in `__init__`) section to describe public attributes.
4. An optional `Example:` block showing basic usage.

- **Class Example:**

  ```python
  class Manager:
      """Validates, parses, and builds names according to a configurable convention.

      A ``Manager`` is built from a set of ordered tokens, a separator, per-token
      rules, and optional normalizers. It can validate raw names, extract token
      values, and assemble new names with automatic normalization.

      Attributes:
          tokens: Ordered list of token names that form a valid name.
          separator: The string used to join tokens (default ``"_"``).
      """

      def __init__(
          self,
          tokens: list[str],
          separator: str,
          rules: dict[str, RuleValidator],
          global_rules: GlobalRules | None = None,
      ) -> None:
          """Initializes the Manager with a naming convention.

          Args:
              tokens: Ordered token names (e.g. ``["descriptor", "side", "usage"]``).
              separator: Character(s) used to join tokens.
              rules: Mapping from token name to its validation rule.
              global_rules: Optional global constraints applied to the full name.
          """
          ...
  ```

- **Example with `Example`:**

  ```python
  class RegexRule:
      """Validates a token value against a regular expression.

      Attributes:
          pattern: The compiled regex pattern used for validation.

      Example:
          rule = RegexRule(pattern=r"^[a-z][a-zA-Z0-9]*$")
          rule.validate("upperArm")  # True
          rule.validate("UpperArm")  # False
      """
      pattern: re.Pattern
  ```

### 3.4. Module Docstrings

Module docstrings should be at the top of the file and summarize the module's content and purpose.

- **Example:**

  ```python
  """Normalizer functions for converting raw token values to their canonical form.

  Each function accepts any object as input and always returns a ``str``.
  Falsy inputs (``None``, ``""``, ``0``) return an empty string.
  Normalizers are assigned per-token in ``config.json`` and applied
  automatically by the ``Manager`` before validation.
  """

  # ... rest of the module's code ...
  ```

## 4. Type Hinting (PEP 484)

Type hints improve code readability and enable static analysis. We follow PEP 484 standards.

### 4.1. Function Signatures

All functions and methods must include type annotations for arguments and return values.

- **Yes:**

  ```python
  def calculate_offset(value: float, bias: float = 0.0) -> float:
      return value + bias
  ```

- **No:**

  ```python
  def calculate_offset(value, bias=0.0):
      return value + bias
  ```

### 4.2. Complex Types

Use generic types from the typing module (or built-ins in Python 3.9+) for complex structures.

- **Yes:**

  ```python
  def process_items(items: list[str]) -> dict[str, int]:
      # ...
  ```

## 5. Logging (PEP 282)

We follow [PEP 282](https://peps.python.org/pep-0282/) standards for logging.

### 5.1. Usage

Use the standard `logging` module instead of `print()` for tracking events, status, and errors.

- **Yes:**

  ```python
  import logging

  logger = logging.getLogger(__name__)
  logger.info("Operation started")
  ```

- **No:**

  ```python
  print("Operation started")
  ```

### 5.2. Log Levels

Select the appropriate level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`.

## 6. Tooling

To ensure consistency and automate compliance, use the following tools:

- **Linter + Formatter:** [Ruff](https://docs.astral.sh/ruff/) — handles code style, import sorting, and docstring conventions in a single tool. Configured in `pyproject.toml`.
- **Type Checker:** mypy

Ruff replaces Black and isort. Do not install or configure them separately.

### 6.1. Running Ruff

```bash
# Check for issues
ruff check .

# Fix automatically where possible
ruff check . --fix

# Format code
ruff format .
```

### 6.2. Pre-commit

We use pre-commit to automatically run these checks before every commit.

#### Installation & Setup

1. Install pre-commit:

    ```bash
    pip install pre-commit
    ```

2. Install the git hook scripts:

    ```bash
    pre-commit install
    ```

#### Usage

Once installed, pre-commit will run automatically on `git commit`. To run it manually on all files:

```bash
pre-commit run --all-files
```
