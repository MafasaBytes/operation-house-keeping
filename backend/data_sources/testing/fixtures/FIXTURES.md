# Fixture provenance

All fixtures are committed byte-frozen (`.gitattributes` marks them binary;
raw-store checksums depend on exact bytes). License: authored in-repo,
project license. No secrets, no absolute paths.

## CSV (DS-001)

- `bom_valid.csv` — hand-authored 6-row BOM-like table (quoting + empty
  cell cases).
- `bom_malformed.bin` — hand-authored bytes that are not valid UTF-8.

## STEP (DS-002)

Generated **once** on 2026-08-06 by
`generators/generate_step_fixtures.py` (WSL2 Ubuntu x86_64, CPython
3.13.11, `cadquery-ocp==7.9.3.1.1`, AP214IS writer, millimetre units) and
frozen. Regenerated output is byte-different (STEP embeds a FILE_NAME
timestamp) and must never silently replace these files. The golden test
expectations are hand-authored in
`tests/data_sources/golden_step_assembly.py` from the design intent below
— deliberately independent of the generator (independent-oracle rule).

sha256 checksums at freeze time:

```
672bb32c2f0bbc5133238ac4ab318dd6ba8805239f8dfa63359555f206b850c2  step_assembly.step
05686a6960a96c4ee2a48ac05c3e9dd81870589a045f60310cc2b4350b057180  step_part_only.step
d49e57fea971514a9bf13f5c243111e712b76ec1cf9cb7f83933bf4da6759bc2  step_corrupted.step
a899fb4496afa7230c378d5be03cf3461990994993110fd2dad3257111081275  native_cad_masquerade.step
```

### `step_assembly.step` — intended semantics

```
demo-unit (root assembly)
  base-1     -> base-plate    (box 80x60x6 mm)   at (0, 0, 0)
  bracket-A  -> bracket-sub   (subassembly)      at (20, 15, 6), +30 deg about Z
    plate-1    -> bracket-plate (box 30x20x4 mm) at (0, 0, 0)
    bolt-front -> bolt-m6     (cyl r3 x 12 mm)   at (5, 5, 4)
    bolt-rear  -> bolt-m6     (cyl r3 x 12 mm)   at (25, 15, 4)
```

5 product definitions (2 assemblies, 3 parts; `bolt-m6` shared by two
occurrences), 5 usage occurrences + 1 root, explicit `SI_UNIT(.MILLI.,
.METRE.)` length unit, `FILE_SCHEMA 'AUTOMOTIVE_DESIGN { 1 0 10303 214 1
1 1 1 }'`.

Manual Part 21 inspection at freeze time confirmed the intended structure:

```
#7   PRODUCT('demo-unit', ...)
#33  PRODUCT('base-plate', ...)
#382 PRODUCT('bracket-sub', ...)
#413 PRODUCT('bracket-plate', ...)
#762 PRODUCT('bolt-m6', ...)
#376 NAUO('1','base-1',    demo-unit  -> base-plate)
#407 NAUO('5','bracket-A', demo-unit  -> bracket-sub)
#756 NAUO('2','plate-1',   bracket-sub -> bracket-plate)
#873 NAUO('3','bolt-front',bracket-sub -> bolt-m6)
#879 NAUO('4','bolt-rear', bracket-sub -> bolt-m6)
```

### Other STEP fixtures

- `step_part_only.step` — one product `lone-cube` (box 10x10x10 mm), no
  assembly structure.
- `step_corrupted.step` — the assembly fixture truncated at byte 24148
  (60%): valid ISO-10303-21 header, DATA section cut mid-entity. Expected:
  `EXTRACT_STEP_PARSE_FAILED` quarantine.
- `native_cad_masquerade.step` — 8-byte OLE compound-file signature plus
  zero padding under a `.step` name. Expected: conservative rejection as
  `ole_compound_container` (no vendor guess), `format_detection` quarantine.
