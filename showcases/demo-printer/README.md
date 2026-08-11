# showcases/demo-printer — synthetic showcase evidence; represents no real machine

This directory holds the SN-001 coherent demonstration source set. Every
file is synthetic showcase evidence, generated or hand-authored once and
frozen; nothing here describes, measures, or represents any real printer,
and nothing here is engineering truth or runtime authority. Committed
showcase derivatives are test artifacts.

Contents:

- `SOURCES.md` — the designed structure in prose. This is the oracle
  INPUT: the hand-authored golden expectations in
  `tests/structural_evidence/golden_showcase.py` are written from this
  prose, never from the generator and never from the implementation.
- `sources/printer_bom.csv` — hand-authored synthetic BOM, frozen.
- `sources/printer_assembly.step` — generated once by `tools/generate.py`
  (CAD extra required) and frozen. Regenerated output is byte-different
  (STEP embeds a FILE_NAME timestamp) and must never silently replace the
  frozen file.
- `MANIFEST.json` — source checksums, pinned ingestion identities,
  extractor identity (config + toolchain fingerprints), frozen-extraction
  checksums, and the regeneration command.
- `extractions/<raw_record_id>.json` — frozen canonical
  `ExtractionResult` derivatives so the SN-001 suite runs base-only. They
  are test artifacts, NOT authoritative ledger records; the `cad`-marked
  drift guard proves the live extractor still produces the STEP one.
- `tools/generate.py` — the one-time generator. Never imported by a test.
