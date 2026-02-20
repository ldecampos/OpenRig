# Naming Convention

## Introduction

Consistent naming is one of the most impactful decisions in a rigging pipeline. A well-formed name encodes enough information to be machine-readable (parseable, searchable, mirroring-friendly) without sacrificing human readability.

The OpenRig naming system is **config-driven**, **modular**, and **agnostic** to any specific convention. The default convention (`descriptor_side_usage`) ships with the project, but every aspect of it — tokens, separator, rules, and normalizers — is defined in `config.json` and can be changed without touching a single line of Python code.

---

## Core Design Principles

| Principle | What it means in practice |
|-----------|--------------------------|
| **Modular** | Each token (descriptor, side, usage) has its own independent rule and normalizer. Adding a new token is a one-line change in `config.json`. |
| **Scalable** | The same `Manager` class handles conventions with 1 token or 10 tokens without modification. |
| **Agnostic** | The library has no opinion on what your tokens mean. You define the tokens, the rules, and the normalizers. The engine enforces them. |
| **Config-driven** | `config.json` is the single source of truth. Rules, separators, token order, and normalizers are all declared there. |
| **Normalizer-first** | Inputs are normalized before validation. This means callers can pass `"left"`, `"Left"`, or `Side.LEFT` and always get a valid `"l"`. |

---

## Default Convention

The default convention shipped in `config.json` defines three ordered tokens separated by `_`:

```
upperArm  _  l   _  jnt
────────     ─      ───
descriptor   side   usage
```

**Full example:**

```
arm_l_jnt          → left arm joint
upperArm_r_ctr     → right upper arm control
spine_c_grp        → center spine group
lowerLegBend_l_jnt → left lower leg bend joint
```

### Tokens

| Token | Position | Required | Rule type | Example values |
|-------|----------|----------|-----------|----------------|
| `descriptor` | 1st | Yes | Regex (camelCase) | `arm`, `upperArm`, `spineIk` |
| `side` | 2nd | No | List | `l`, `r`, `c`, `m` |
| `usage` | 3rd | No | From enums | `jnt`, `ctr`, `grp`, `skin` |

Tokens are **optional**. Valid names with the default convention:

```
arm              → descriptor only
arm_l            → descriptor + side
arm_l_jnt        → full name
```

### Descriptor Rules

- Must be **camelCase**: starts with a lowercase letter, no separators.
- Automatically normalized from snake_case or PascalCase on input.

```python
# All of these produce the same result:
manager.build_name(descriptor="upper_arm", side="l", usage="jnt")  # "upperArm_l_jnt"
manager.build_name(descriptor="UpperArm",  side="l", usage="jnt")  # "upperArm_l_jnt"
manager.build_name(descriptor="upperArm",  side="l", usage="jnt")  # "upperArm_l_jnt"
```

### Side Rules

Accepted values: `l` (left), `r` (right), `c` (center), `m` (middle).

The normalizer accepts long forms and any case — they are all converted to the canonical abbreviation:

| Input | Normalized |
|-------|-----------|
| `"left"` | `"l"` |
| `"Left"` | `"l"` |
| `"LEFT"` | `"l"` |
| `"L"` | `"l"` |
| `Side.LEFT` | `"l"` |
| `"right"` | `"r"` |
| `"center"` | `"c"` |
| `"middle"` | `"m"` |

### Usage Rules

Usage values are aggregated from five enum classes defined in `constants.py`. The most commonly used values are:

**Structure & Hierarchy** (`Usage`)

| Value | Token | Description |
|-------|-------|-------------|
| `ctr` | control | Animatable control curve |
| `grp` | group | Transform group / organizer |
| `jnt` | joint | Skeleton joint |
| `loc` | locator | Scene locator |
| `offset` | offset | Offset transform above a control |
| `drv` | driver | Driver joint or transform |
| `pv` | pole vector | IK pole vector target |
| `ref` | reference | Reference / snap target |
| `guide` | guide | Build-time guide object |
| `ikh` | IK handle | IK handle node |

**Deformers** (`UsageDeformer`)

| Value | Token | Description |
|-------|-------|-------------|
| `skin` | skin cluster | Skin cluster deformer |
| `bs` | blend shape | Blend shape deformer |
| `dm` | delta mush | Delta Mush deformer |
| `ffd` | FFD | Lattice FFD deformer |

**Constraints** (`UsageConstraint`)

| Value | Token | Description |
|-------|-------|-------------|
| `pasns` | parent constraint | Parent constraint node |
| `posns` | point constraint | Point constraint node |
| `orsns` | orient constraint | Orient constraint node |
| `matcns` | matrix constraint | Matrix-based constraint |

**Utility Nodes** (`UsageUtility`)

| Value | Token | Description |
|-------|-------|-------------|
| `mult` | multiply | Multiply node |
| `add` | add | Addition node |
| `cond` | condition | Condition node |
| `blendmat` | blend matrix | Blend matrix node |
| `dmat` | decompose matrix | Decompose matrix node |

> See `constants.py` for the full list of values across all `Usage*` enums.

---

## Global Rules

Applied to every fully-assembled name regardless of token rules:

| Rule | Value | Effect |
|------|-------|--------|
| `max_length` | `80` | Names longer than 80 characters raise `NamingValidationError`. |
| `forbidden_patterns` | `["__", "--", ".."]` | Names containing these substrings raise `NamingValidationError`. |

---

## Using the Naming Library

### Getting the Manager

The library exposes a pre-configured singleton via `get_manager()`. This is the recommended entry point for all day-to-day usage.

```python
from openrig.naming import get_manager

manager = get_manager()
```

The singleton is built once from `config.json` on first call. All subsequent calls return the same instance.

---

### Building Names

```python
manager = get_manager()

# Basic
manager.build_name(descriptor="arm", side="l", usage="jnt")
# → "arm_l_jnt"

# camelCase descriptor from snake_case input
manager.build_name(descriptor="upper_arm", side="r", usage="ctr")
# → "upperArm_r_ctr"

# Using enums directly
from openrig.constants import Side, Usage
manager.build_name(descriptor="spine", side=Side.CENTER, usage=Usage.GROUP)
# → "spine_c_grp"

# Optional tokens — omit side and/or usage
manager.build_name(descriptor="spine", usage="jnt")   # → "spine_jnt"
manager.build_name(descriptor="rig")                  # → "rig"
```

**What happens internally:**

```
input value
    │
    ▼
[normalizer]  e.g. "upper_arm" → "upperArm", "Left" → "l"
    │
    ▼
[rule.validate()]  rejects invalid values and raises NamingValidationError
    │
    ▼
[join with separator]  "upperArm" + "_" + "l" + "_" + "jnt"
    │
    ▼
[global rules check]  max_length, forbidden_patterns
    │
    ▼
final name: "upperArm_l_jnt"
```

---

### Validating Names

```python
# Full name validation — returns True only if all tokens are present and valid
manager.is_valid("arm_l_jnt")        # True
manager.is_valid("upperArm_r_ctr")   # True
manager.is_valid("Arm_l_jnt")        # False — descriptor starts with uppercase
manager.is_valid("arm_x_jnt")        # False — "x" is not a valid side
manager.is_valid("arm_left_jnt")     # False — long form is not stored, only "l"
manager.is_valid("")                 # False

# Single token validation
manager.is_valid_token("side", "l")      # True
manager.is_valid_token("side", "left")   # False
manager.is_valid_token("usage", "jnt")   # True

# Human-readable error list
manager.get_errors("arm_x_jnt")
# → ["Invalid value 'x' for token 'side'."]

manager.get_errors("")
# → ["Name must be a non-empty string."]
```

> **Important:** `is_valid()` does **not** apply normalizers. It checks the name as-is.
> Use `build_name()` when you want automatic normalization before validation.

---

### Parsing Names

```python
# Extract all token values
data = manager.get_data("arm_l_jnt")
# → {"descriptor": "arm", "side": "l", "usage": "jnt"}

# Partial names return empty strings for missing tokens
data = manager.get_data("arm_l")
# → {"descriptor": "arm", "side": "l", "usage": ""}

# Extract a single token
manager.get_token_value("upperArm_r_ctr", "descriptor")  # → "upperArm"
manager.get_token_value("upperArm_r_ctr", "side")        # → "r"
manager.get_token_value("arm_l", "usage")                # → ""
```

---

### Updating Names

Update one or more tokens in an existing name without rewriting the whole string:

```python
manager.update_name("arm_l_jnt", side="r")
# → "arm_r_jnt"

manager.update_name("arm_l_jnt", side=Side.RIGHT)
# → "arm_r_jnt"

manager.update_name("arm_l_jnt", descriptor="leg")
# → "leg_l_jnt"

manager.update_name("arm_l_jnt", usage="ctr")
# → "arm_l_ctr"

# Normalization is applied to overrides too
manager.update_name("arm_l_jnt", descriptor="upper_arm")
# → "upperArm_l_jnt"

manager.update_name("arm_l_jnt", side="Right")
# → "arm_r_jnt"
```

---

### Resolving Names (Flexible Input)

`resolve_name()` accepts multiple input formats and always returns a string:

```python
# From a dict
manager.resolve_name({"descriptor": "arm", "side": "l", "usage": "jnt"})
# → "arm_l_jnt"

# From a positional list (maps to tokens in order)
manager.resolve_name(["arm", "l", "jnt"])
# → "arm_l_jnt"

# From a tuple
manager.resolve_name(("arm", "l", "jnt"))
# → "arm_l_jnt"

# Plain string — returned as-is (no building or validation)
manager.resolve_name("already_valid_name")
# → "already_valid_name"
```

This is useful when writing functions that accept names in any format.

---

## Available Normalizers

Normalizers convert raw input into a canonical string before validation. They are assigned per-token in `config.json` and are also available as standalone functions.

```python
from openrig.naming import normalizers

normalizers.descriptor("upper_arm")   # → "upperArm"
normalizers.descriptor("UpperArm")    # → "upperArm"
normalizers.side("Left")              # → "l"
normalizers.side("RIGHT")             # → "r"
normalizers.version("v3")             # → "v003"
normalizers.version(1)                # → "v001"
normalizers.snake_case("upperArm")    # → "upper_arm"
normalizers.pascal_case("upper_arm")  # → "UpperArm"
```

| Key | Function | Description |
|-----|----------|-------------|
| `descriptor` | `descriptor()` | Converts to camelCase. |
| `side` | `side()` | Maps long forms and any case to the canonical abbreviation. |
| `type` | `normalize_type()` | Converts to camelCase (alias, avoids shadowing built-in). |
| `pascal_case` | `pascal_case()` | Converts to PascalCase. |
| `snake_case` | `snake_case()` | Converts to snake_case. |
| `kebab_case` | `kebab_case()` | Converts to kebab-case. |
| `upper` | `upper()` | Converts to UPPERCASE. |
| `lower` | `lower()` | Converts to lowercase. |
| `capitalize` | `capitalize()` | Capitalizes the first letter only. |
| `version` | `version()` | Normalizes to `vNNN` format (e.g. `v001`). |
| `strip_digits` | `strip_digits()` | Removes all digit characters. |
| `strip_namespace` | `strip_namespace()` | Strips the `namespace:` prefix. |
| `base_name` | `base_name()` | Returns the last `|`-separated segment (Maya DAG path). |
| `clean` | `clean()` | Replaces illegal characters with `_`. |

All normalizers accept any object as input and always return a `str`. Falsy inputs (`None`, `""`, `0`) always return `""`.

---

## Extending the Convention

### Changing the Convention via `config.json`

The entire naming convention is defined in `config.json`. To use a different set of tokens, separator, or rules, edit that file — no Python changes required.

**Example: adding a `variant` token**

```json
{
  "naming": {
    "separator": "_",
    "tokens": ["descriptor", "side", "usage", "variant"],
    "rules": {
      "descriptor": { "type": "regex", "value": "^[a-z][a-zA-Z0-9]*$" },
      "side":       { "type": "list",  "value": ["l", "r", "c", "m"] },
      "usage":      { "type": "from_enums", "sources": ["Usage", "UsageDeformer"] },
      "variant":    { "type": "regex", "value": "^[a-z][a-zA-Z0-9]*$" }
    },
    "normalizers": {
      "descriptor": "descriptor",
      "side": "side",
      "variant": "descriptor"
    }
  }
}
```

After restarting (or calling `get_manager()` for the first time in the session):

```python
manager.build_name(descriptor="arm", side="l", usage="jnt", variant="fk")
# → "arm_l_jnt_fk"
```

---

### Using a Custom Manager

For one-off workflows or tools that need a different convention, create a `Manager` directly without touching `config.json`:

```python
from openrig.naming.manager import Manager
from openrig.schemas import RegexRule, ListRule, GlobalRules

custom_manager = Manager(
    tokens=["asset", "department", "version"],
    separator="-",
    rules={
        "asset":      RegexRule(pattern=r"^[a-z][a-zA-Z0-9]+$"),
        "department": ListRule(allowed=frozenset({"rig", "anim", "fx", "lgt"})),
        "version":    RegexRule(pattern=r"^v\d{3}$"),
    },
    global_rules=GlobalRules(max_length=60),
)

custom_manager.build_name(asset="heroChar", department="rig", version="v001")
# → "heroChar-rig-v001"
```

---

### Adding or Removing Rules at Runtime

```python
from openrig.schemas import RegexRule

manager = get_manager()

# Add a rule to an existing token (replaces if already present)
manager.add_rule("descriptor", RegexRule(pattern=r"^[a-z][a-zA-Z0-9_]*$"))

# Remove a rule — the token will then accept any value
manager.remove_rule("usage")
```

> **Note:** `add_rule()` and `remove_rule()` modify the shared singleton.
> Prefer creating a separate `Manager` instance when you need an isolated convention.

---

## Real-World Use Cases

### 1. Rigging — Building joint and control names

```python
from openrig.naming import get_manager
from openrig.constants import Side, Usage

mgr = get_manager()

# Arm joints
arm_jnt   = mgr.build_name(descriptor="arm",      side=Side.LEFT, usage=Usage.JOINT)
elbow_jnt = mgr.build_name(descriptor="forearm",  side=Side.LEFT, usage=Usage.JOINT)
wrist_jnt = mgr.build_name(descriptor="wrist",    side=Side.LEFT, usage=Usage.JOINT)
# → "arm_l_jnt", "forearm_l_jnt", "wrist_l_jnt"

# Controls
arm_ctr = mgr.build_name(descriptor="arm", side=Side.LEFT, usage=Usage.CONTROL)
arm_grp = mgr.build_name(descriptor="arm", side=Side.LEFT, usage=Usage.GROUP)
arm_off = mgr.build_name(descriptor="arm", side=Side.LEFT, usage=Usage.OFFSET)
# → "arm_l_ctr", "arm_l_grp", "arm_l_offset"
```

### 2. Mirroring — Swapping sides

```python
name = "arm_l_jnt"
data = mgr.get_data(name)
mirrored = mgr.update_name(name, side="r")
# → "arm_r_jnt"

# Or using the Side enum mirror helper
from openrig.constants import Side
side_val  = mgr.get_token_value(name, "side")   # → "l"
side_enum = Side(side_val)                        # → Side.LEFT
mirrored  = mgr.update_name(name, side=side_enum.mirror())
# → "arm_r_jnt"
```

### 3. Validation — Checking existing scene names

```python
scene_nodes = ["arm_l_jnt", "Arm_l_jnt", "arm_x_jnt", "upperArm_r_ctr"]

valid   = [n for n in scene_nodes if mgr.is_valid(n)]
invalid = [n for n in scene_nodes if not mgr.is_valid(n)]

print(valid)    # ["arm_l_jnt", "upperArm_r_ctr"]
print(invalid)  # ["Arm_l_jnt", "arm_x_jnt"]

# Get the exact error for each invalid name
for name in invalid:
    print(name, "→", mgr.get_errors(name))
# Arm_l_jnt  → ["Name does not match the required naming pattern."]
# arm_x_jnt  → ["Invalid value 'x' for token 'side'."]
```

### 4. Rename tool — Accepting flexible input from artists

```python
def rename_node(node_name: str, **overrides) -> str:
    """Builds a validated name from the given node, applying any overrides."""
    mgr = get_manager()
    return mgr.update_name(node_name, **overrides)

rename_node("arm_l_jnt", side="r")            # → "arm_r_jnt"
rename_node("arm_l_jnt", descriptor="leg")    # → "leg_l_jnt"
rename_node("arm_l_jnt", side="Right")        # → "arm_r_jnt"  (normalized)
```

### 5. Unique names — Avoiding duplicates in scene

```python
from openrig.naming.utils import get_unique_name

existing = {"arm_l_jnt", "arm_l_jnt01", "arm_l_jnt02"}
desired  = mgr.build_name(descriptor="arm", side="l", usage="jnt")
# → "arm_l_jnt"

unique = get_unique_name(desired, existing)
# → "arm_l_jnt03"
```

### 6. Deformer naming

```python
from openrig.constants import UsageDeformer

skin = mgr.build_name(descriptor="body", side="c", usage=UsageDeformer.SKIN_CLUSTER)
bs   = mgr.build_name(descriptor="body", side="c", usage=UsageDeformer.BLEND_SHAPE)
# → "body_c_skin", "body_c_bs"
```

---

## Quick Reference — Valid vs Invalid Names

| Name | Valid | Reason if invalid |
|------|-------|-------------------|
| `arm_l_jnt` | ✅ | — |
| `upperArm_r_ctr` | ✅ | — |
| `spine_c_grp` | ✅ | — |
| `arm_l` | ✅ | usage is optional |
| `rig` | ✅ | side and usage are optional |
| `Arm_l_jnt` | ❌ | descriptor starts with uppercase |
| `arm_left_jnt` | ❌ | `"left"` is not in the allowed side list |
| `arm_x_jnt` | ❌ | `"x"` is not a valid side value |
| `arm_l_notValid` | ❌ | `"notValid"` is not a recognised usage token |
| `arm__jnt` | ❌ | contains forbidden pattern `__` |
| `""` | ❌ | empty string |
