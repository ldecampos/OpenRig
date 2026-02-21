# OpenRig — Architecture Overview

## What is a rig?

A system that translates animator **inputs** into deformation **outputs** through a **process**.

OpenRig never assumes what inputs, outputs, or processes look like. There is no single
mandatory structure. A rig can use controls transforms,
direct geometry selection, or anything else, (It is probably a matrix representing a point in space). The library provides the tools; the rigger
decides what to build.

---

## Core Principles

- **Modular** — the fundamental unit is a *solution*, not a full rig.
  A full rig is just a composition of solutions.
- **Flexible** — solutions can be used standalone or composed freely.
- **Reconstructable** — a rig can always be rebuilt from its description (pipeline-style).
- **Agnostic** — the core logic is decoupled from any specific DCC.
- **Config-driven** — conventions and behaviours are declared in configuration, not hardcoded. It should have one by default, in an external file.

---

## Rig Lifecycle

```text
DESCRIPTION  →  BUILD  →  SCENE
(data/file)     (DCC)     (accessible via API)
```

1. **Description** — the rig is defined as data (JSON or similar), outside DCC.
2. **Build** — the description is materialized in the DCC.
3. **Scene** — the built rig leaves metadata in the scene;
   the API can recover its data at any point without keeping Python objects in memory.

---

## Three-Layer Architecture

```text
┌─────────────────────────────────────────┐
│           AGNOSTIC LAYER                │
│  Contracts, data models, solution logic │
│  knows nothing about any DCC            │
└─────────────────┬───────────────────────┘
                  │ implemented by
┌─────────────────▼───────────────────────┐
│           DCC LAYER                     │
│  DCC-specific: nodes, commands,         │
│  atomic operations (currently Maya)     │
└─────────────────┬───────────────────────┘
                  │ builds
┌─────────────────▼───────────────────────┐
│           SCENE                         │
│  Materialized rig, accessible via API   │
└─────────────────────────────────────────┘
```

Adding support for a future DCC (Blender, Houdini…) means adding a new DCC layer
implementation. The agnostic layer and all solutions remain untouched.

---

## Package Structure

```text
openrig/
├── naming/       ← agnostic — naming system (complete)
├── core/         ← agnostic — contracts and data models (ABCs, Protocols, dataclasses)
├── solutions/    ← agnostic — solution catalogue, implemented against core/ contracts
├── io/           ← agnostic — serialization: rig description ↔ JSON/file
├── utils/        ← agnostic — shared utilities (math, transforms…)
│
├── maya/         ← DCC-specific — everything Maya
│   ├── ops/      ← atomic operations (create joint, constraint, connect attrs…)
│   └── build/    ← materialize and read rigs in scene
│
└── ui/           ← independent project, joins later
```

### Responsibility of each module

| Module | Layer | Responsibility |
|---|---|---|
| `naming/` | Agnostic | Name validation, construction and parsing |
| `core/` | Agnostic | Contracts that every solution and component must fulfil |
| `solutions/` | Agnostic | Concrete solutions (arm, spine, twist…) built on `core/` |
| `io/` | Agnostic | Read/write rig descriptions to disk |
| `utils/` | Agnostic | Math, matrix helpers, shared utilities |
| `maya/ops/` | DCC | Low-level Maya operations (building blocks) |
| `maya/build/` | DCC | Build pipeline and scene introspection |
| `ui/` | — | Authoring tools, independent of the core library |

---

## What this design buys

- `solutions/` can be used and tested without Maya.
- A rigger works mainly with `solutions/` and `maya/build/`.
- Future DCC support = add `blender/Houdini/..` alongside `maya/`, nothing else changes.
- A rig description (in `io/`) is DCC-portable by design.
- The config-driven approach means conventions can change without touching the code.

---

## Open Questions (next steps)

- What does a **solution contract** look like in `core/`?
  What must every solution expose? (inputs, outputs, a build method?)
- How does a solution declare what it needs vs what it produces?
- How are solutions composed into a full rig?
- What format does the rig description use in `io/`?
- How does the rig leave retrievable metadata in the Maya scene?
