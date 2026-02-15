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
  def get_model(self, model_name: str | None) -> Model:
      """Gets an instance of the specified model.

      If `model_name` is None, it returns the default model. This method
      lazily loads the OpenAI client to avoid errors if the API
      key is not configured.

      Args:
          model_name: The name of the model to get.

      Returns:
          A `Model` instance configured with the appropriate client.
      """
      if model_name is None:
          model_name = DEFAULT_MODEL

      client = self._get_client()

      return (
          OpenAIResponsesModel(model=model_name, openai_client=client)
          if self._use_responses
          else OpenAIChatCompletionsModel(model=model_name, openai_client=client)
      )
  ```

- **Example with `Raises`:**

  ```python
  def validate_code(cls, v):
      """Validates that the code contains a Diagram definition.

      Args:
          v: The code string to validate.

      Returns:
          The original code string if it is valid.

      Raises:
          ValueError: If the code does not contain a 'Diagram' definition.
      """
      if 'Diagram(' not in v:
          raise ValueError('Code must contain a Diagram definition')
      return v
  ```

### 3.3. Google Style for Classes

Class docstrings should contain:

1. A one-line summary.
2. A more detailed description of the class's purpose.
3. An `Attributes:` (or `Args:` in `__init__`) section to describe public attributes.
4. An optional `Example:` block showing basic usage.

- **Class Example:**

  ```python
  class OpenAIProvider(ModelProvider):
      """Creates a new OpenAI provider.

      This class manages the creation and access to an OpenAI client,
      allowing for the configuration of API keys, base URLs, and other parameters.
      It loads the client lazily to optimize performance.

      Attributes:
          use_responses: A boolean indicating whether to use the OpenAI responses API.
      """

      def __init__(
          self,
          *,
          api_key: str | None = None,
          base_url: str | None = None,
          # ...
      ) -> None:
          """Initializes the OpenAI provider.

          Args:
              api_key: The API key to use.
              base_url: The base URL for the client.
              openai_client: An optional, pre-existing OpenAI client.
              # ...
          """
          # ...
  ```

- **Example with `Example`:**

  ```python
  class OpenIdConfig(BaseModel):
    """Represents the OpenID Connect configuration.

    Attributes:
        client_id: The client ID.
        auth_uri: The authorization URI.
        token_uri: The token URI.
        client_secret: The client secret.
        redirect_uri: The optional redirect URI.

    Example:
        config = OpenIdConfig(
            client_id="your_client_id",
            auth_uri="https://accounts.google.com/o/oauth2/auth",
            token_uri="https://oauth2.googleapis.com/token",
            client_secret="your_client_secret",
        )
    """
    client_id: str
    auth_uri: str
    token_uri: str
    client_secret: str
    redirect_uri: Optional[str]
  ```

### 3.4. Module Docstrings

Module docstrings should be at the top of the file and summarize the module's content and purpose.

- **Example:**

  ```python
  """Defines the Coder agent for generating, executing, and debugging code.

  This module provides the `CoderAgent` class, which interacts with a
  language model to write code and with a code executor (local or Docker)
  to test it. The agent supports multiple rounds of debugging and user
  approval guards.
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

- **Formatter:** Black
- **Import Sorter:** isort
- **Type Checker:** mypy

### 6.1. Pre-commit

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
