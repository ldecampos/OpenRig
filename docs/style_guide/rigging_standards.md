# Rigging Standards

## Introduction

This document defines the rigging conventions adopted by OpenRig. These decisions govern
how rigs are structured, oriented, and connected inside the DCC. Where possible,
conventions are declared in `config.json` so they can be changed without modifying code.

---

## 1. Coordinate System & Axes

All axis conventions are declared in `config.json` under the `rigging` key and read at
runtime via `openrig.constants`. Changing a value in the config is enough to apply it
across the entire library.

| Convention | Default | Config key |
|---|---|---|
| Aim axis | `X` | `axis_aim` |
| Up axis | `Y` | `axis_up` |
| Side axis | `Z` | `axis_side` |
| Rotate order | `xyz` | `rotate_order_default` |

**Rationale:** X-aim, Y-up, Z-side is the most common convention in Maya pipelines
and aligns with the default matrix layout for joints.

---

## 2. Side Convention

| Side | Token | Meaning |
|---|---|---|
| Left | `l` | Positive X side of the character |
| Right | `r` | Negative X side of the character |
| Center | `c` | On the character's symmetry plane |
| Middle | `m` | Intermediate position, not strictly on-axis |

Default side is declared in `config.json` as `side_default` (default: `"c"`).

**Rule:** Left is always the character's left (positive X), not the camera's left.

---

## 3. Joint Orientation

- Joints follow the axis convention defined in Section 1: aim along **X**, up along **Y**.
- The last joint in a chain (tip joint) inherits the orientation of its parent.
- World-oriented joints are acceptable only for root and global nodes.

---

## 4. Hierarchy & Node Organization

> **Status: open design decision — not yet adopted.**

The library does not mandate a specific node hierarchy. The following are the options
under consideration:

### Option A — Group + Offset nodes (traditional)

```text
<descriptor>_<side>_grp
  └── <descriptor>_<side>_offset
        └── <descriptor>_<side>_ctr
```

Explicit transform nodes absorb placement so the control starts at zero.
Simple and universally compatible, but adds nodes to the scene.

### Option B — offsetParentMatrix (Maya 2020+)

The initial placement is stored in the control's `offsetParentMatrix` attribute.
No extra nodes are needed; the control itself starts at zero in channel box.
Cleaner hierarchy, but Maya-specific and not supported in all DCCs.

### Option C — Other

Any other approach (e.g. driven by the solution's config) is valid as long as it
satisfies the core requirement: the animatable node must read zero on all channels
at bind pose.

The chosen approach will be documented here once the design decision is made.

---

## 5. Controls

OpenRig does not mandate a specific control representation. Valid options include:

- Curves with display shapes (most common)
- Transform nodes without shapes (lightweight setups)
- Direct geometry selection (no dedicated control object)

The control type for a given solution is declared in its configuration, not hardcoded
in the library. The default shape type is declared in `config.json` under `shapes.default`.

---

## 6. Naming

All node names must conform to the naming convention defined in `config.json`.
See [naming_convention.md](naming_convention.md) for the full reference.

Quick summary of the default convention:

```text
descriptor_side_usage
upperArm_l_jnt
spine_c_ctr
```

---

## 7. Connections & Data Flow

- Prefer **matrix-based connections** over constraint nodes where possible.
  They are cheaper to evaluate and easier to inspect.
- Constraints are acceptable for legacy compatibility or cases where matrix math
  would significantly increase complexity.
- Utility nodes must follow the naming convention (`mult`, `add`, `cond`, `dmat`, etc.).

---

## 8. Build vs Scene State

- A rig must be **fully reconstructable** from its description file.
  No manual edits to the built scene should be necessary.
- Guide objects (`guide` usage token) are build-time only and must be removed or
  hidden after the rig is built.
- Any metadata needed for API access after the build must be stored as
  custom attributes on a designated metadata node.
