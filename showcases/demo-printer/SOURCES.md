# Designed structure — the oracle input

Synthetic showcase evidence; represents no real machine. The golden
expectations in `tests/structural_evidence/golden_showcase.py` are
hand-authored FROM THIS PROSE (independent-oracle rule): never from the
generator, never from the extractor, never from the reconciler.

## BOM — `sources/printer_bom.csv`

Columns: `item_no,name,quantity,unit,parent`. Header row 0; six data rows
(physical rows 1-6). The structural reading declares: quantity = column 2,
parent = column 4, parent-matches = column 0 (all by index).

| row | item_no | name            | quantity | unit  | parent  | design intent |
|-----|---------|-----------------|----------|-------|---------|---|
| 1   | PRN-000 | Printer assembly| 1        | piece | (empty) | root row: no parent claim |
| 2   | EXT-100 | Extruder unit   | 4        | piece | PRN-000 | joins the committed extruder anchor; quantity "4" is the DELIBERATE mismatch (model registers one instance; STEP has no quantity column) |
| 3   | CBL-300 | Wiring harness  | 1        | piece | PRN-000 | BOM-only item, deliberately unmapped -> `source_subject_unmapped` |
| 4   | BRK-400 | Corner bracket  | 1        | piece | PRN-000 | duplicate label pair, unmapped |
| 5   | BRK-401 | Corner bracket  | 1        | piece | PRN-000 | same `name`, different `item_no` -> `duplicate_source_label_not_identity`, two distinct subjects |
| 6   | FAS-500 | Idler wheel     | 2        | piece | EXT-100 | quantity lexeme "2"; unmapped |

Containment claims (within-source, by unique `item_no` lookup):
rows 2,3,4,5 -> row 1; row 6 -> row 2. No unresolved parent references.

## STEP — `sources/printer_assembly.step`

AP214IS, millimetres, no view metadata anywhere (the engineering context
must be declared by an authority; the source declares none). Design:

```
printer-assembly (root assembly)
  extruder-1    -> extruder-unit   box 40 x 30 x 45 mm   at (120, 40, 20)
  gantry-left   -> gantry-sub      subassembly            at (0, 0, 200)
  gantry-right  -> gantry-sub      subassembly            at (300, 0, 200)
    idler-front -> idler-wheel     cylinder r8 x 6 mm     at (10, 5, 0)
    idler-rear  -> idler-wheel     cylinder r8 x 6 mm     at (90, 5, 0)
  fan-1         -> hotend-fan      box 30 x 30 x 10 mm    at (125, 35, 70)
```

5 part definitions (2 assemblies: printer-assembly, gantry-sub; 3 parts:
extruder-unit, idler-wheel, hotend-fan) and 6 usage occurrences plus the
synthesized root. Deliberate design facts:

- `gantry-sub` is used TWICE (gantry-left, gantry-right), so the
  idler-wheel usages inside it have a parent definition used by two
  usages: their derived usage paths are `multiple_parent_uses` — SN-001
  reports, never picks. Expected derived-path ambiguity count: 2 (the two
  idler usages).
- `idler-wheel` is one definition with two usages inside one sub-assembly
  (definition/usage discipline: 1 definition claim, 2 usage claims).
- `hotend-fan` is STEP-only and deliberately unmapped ->
  `source_subject_unmapped`.
- `extruder-unit` (the DEFINITION) is mapped by a hand-authored
  `BindingAssertion` to the committed extruder physical-instance anchor —
  a layer-2 representation claim, never a registration.
- The root `printer-assembly` definition is mapped to the new
  hand-authored assembly-type anchor -> `supported_by_step_only` for that
  anchor (no BOM subject maps to it).

## Expected reconciliation shape (golden multiset input)

With the two committed binding sets (after the SN-001c appends), the
committed model at 14 records, and the readings above:

- extruder anchor: `corroborated_by_all_mapped_sources` (BOM EXT-100 +
  STEP extruder-unit definition), `claims_not_comparable` (BOM quantity
  vs no STEP quantity column), and
  `quantity_not_reconcilable_with_registered_instances` (lexeme "4"
  against the one registered instance the join binds).
- assembly-type anchor: `supported_by_step_only`.
- CBL-300, BRK-400, BRK-401, FAS-500, hotend-fan, gantry-sub,
  idler-wheel, and every unmapped usage subject:
  `source_subject_unmapped` (per subject x applicable rule).
- BRK-400/BRK-401: `duplicate_source_label_not_identity` with TWO
  distinct subjects disclosed.
- the two idler usages: `derived_usage_path_ambiguous`.
- the STEP claim set's subjects, being mapped from a view-less source:
  `context_unknown` where a mapping exists but no authority declared a
  context for the source reading.
