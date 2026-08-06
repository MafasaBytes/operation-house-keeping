# ADR-0002: OCP (cadquery-ocp) as the STEP extraction toolchain, isolated in a worker subprocess

Date: 2026-08-06
Status: Accepted (project owner, 2026-08-06, with amendments)

## Context

DS-002 requires reading STEP assemblies (structure, definitions vs
instances, transforms, units, properties) and producing a traceable glTF
visualization derivative — CAD extraction Levels 0–3 — from a pip
clean checkout on WSL/Linux and Windows, Python 3.13.

## Options considered

1. **OCP / `cadquery-ocp` (pip)** — OCCT bindings; XCAF assembly model,
   `STEPCAFControl_Reader`, `RWGltf_CafWriter`; wheels cp310–cp314 for
   win/linux/mac (46–68 MB); no sdist.
2. **pythonocc-core (conda-forge)** — same OCCT capability; conda-only
   distribution breaks the pip clean-checkout flow.
3. **Pure-Python Part 21 parser** (steputils 0.1 is dormant; would be
   largely bespoke) — safest and smallest, but caps at Levels 0–2 with no
   honest tessellated derivative, and reimplements AP214/AP242 assembly
   semantics at high risk.
4. **External CLI (FreeCAD headless / gmsh)** — heavyweight, weakly
   controllable; gmsh is GPL, which we do not want as a linked dependency.

## Decision

Option 1: `cadquery-ocp==7.9.3.1.1`, exactly pinned and hash-pinned in
`requirements-cad.txt` (`pip install --require-hashes -r
requirements-cad.txt`), used **only inside the extraction worker
subprocess**, never imported by the core service path.

- The worker subprocess is a **crash-isolation boundary, not a complete
  security sandbox** (see spec §Worker isolation for the exact controls).
- No source distribution exists. On platforms/Python versions without a
  wheel, installation fails; the connector's `available` status rung then
  fails honestly with evidence. No degraded fake implementation is
  provided.
- CAD-capable installs are an optional extra so the core module stays at
  one runtime dependency (pydantic).

## Licensing (two layers, both recorded)

- **`cadquery-ocp` bindings: Apache-2.0.**
- **OCCT runtime (bundled shared libraries in the wheel): LGPL-2.1 with
  the Open CASCADE exception.**

Obligations documented in `THIRD_PARTY_NOTICES.md`: retain notices; if we
ever redistribute the OCCT libraries (e.g. ship the wheel inside our own
artifact or installer), we must preserve the OCCT license text and the
exception notice, state changes if we modify OCCT, and keep OCCT
replaceable (dynamic linking via the wheel satisfies this). Internal use
and pip-resolved installation impose no additional obligations.

## Consequences

- Levels 0–3 achievable honestly, including a real tessellated glTF
  derivative with recorded tessellation parameters and environment.
- ~68 MB dependency confined to `requirements-cad.txt`; CI and clean
  checkouts that skip it still run the entire non-`cad` suite, and the
  `cad`-marked tests skip loudly with the reason.
- Byte-level GLB reproducibility is bounded to the pinned platform +
  toolchain; cross-platform comparison is semantic (spec §Determinism).
- Upgrading OCP changes extractor identity (`toolchain` field), which
  correctly invalidates determinism expectations recorded against the old
  version.
