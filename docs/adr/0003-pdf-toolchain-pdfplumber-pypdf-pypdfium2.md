# ADR-0003: pdfplumber + pypdf (+ bundled pdfminer.six/pypdfium2/Pillow) for PDF extraction, worker-isolated

Date: 2026-08-07
Status: Accepted (project owner, 2026-08-07, with amendments)

## Context

DS-003 needs positioned text, layout structure, table candidates,
annotations/links, image and vector inventory, page rendering, encryption
handling, and honest behavior on malformed/hostile PDFs — extraction
Levels 0–3 — from a pip clean checkout on WSL/Linux and Windows,
Python 3.13, avoiding AGPL dependencies.

## Options (PyPI-verified 2026-08-07)

1. **pdfplumber 0.11.10 (MIT)** — positioned chars/words/lines, table
   finder with explicit strategies, rects/curves/images/annots/hyperlinks.
   Depends on `pdfminer.six==20260107` (MIT), `pypdfium2>=5.9` (BSD-3 +
   Apache-2.0; PDFium itself BSD-3), `Pillow>=12.2` (MIT-CMU).
2. **pypdf 6.15.0 (BSD-3-Clause)** — pure Python, 0.4 MB: page labels,
   declared metadata, encryption state, safe catalog inspection
   (JavaScript/actions/embedded files/OCG names).
3. **PyMuPDF 1.28.2** — technically strongest, but PyPI license field:
   "Dual Licensed - GNU AFFERO GPL 3.0 or Artifex Commercial License".
   **Rejected on AGPL/commercial licensing** per owner rule.
4. **camelot / tabula-py** — MIT wrappers over Ghostscript (AGPL) / Java.
   Rejected: licensing and runtime burden; pdfplumber's method-declared
   table candidates satisfy DS-003 honesty requirements.

## Decision

Options 1 + 2, exactly hash-pinned as a closure in `requirements-pdf.txt`
(includes cryptography — required by pdfminer.six for encrypted PDFs —
plus cffi/pycparser/charset-normalizer). Total closure ≈ 20 MB.

**Not pure Python:** PDFium (compiled Chromium PDF runtime via ctypes),
Pillow, cryptography, and cffi ship native components. All PDF libraries
are therefore imported only inside the extraction worker subprocess (the
DS-002 crash-isolation harness, reused unchanged). The subprocess is a
crash-isolation boundary, not a complete sandbox.

Rendering: pypdfium2 rasterization + Pillow PNG encoding with pinned
encoder settings; both versions recorded in every derivative's
environment block.

## Licensing layers (see THIRD_PARTY_NOTICES.md)

- pdfplumber MIT; pdfminer.six MIT; pypdf BSD-3-Clause.
- pypdfium2: bindings BSD-3-Clause OR Apache-2.0; bundled PDFium library
  BSD-3-Clause with additional bundled third-party notices shipped in the
  wheel — the actual license inventory shipped with the pinned wheel is
  recorded in THIRD_PARTY_NOTICES.md at spike time.
- Pillow MIT-CMU; cryptography Apache-2.0 OR BSD-3-Clause.
- No copyleft obligations for internal use; redistribution obligations are
  notice-preservation only.

## Consequences

- Levels 0–3 honestly reachable including page renders; OCR (L4) can
  attach later per page without a toolchain change (it would be a separate
  approved dependency).
- Upgrading any closure member changes `component_versions` and the
  extractor toolchain string, correctly invalidating recorded determinism
  expectations.
- On platforms without a pypdfium2/Pillow/cryptography wheel, the
  hash-pinned install fails and the connector `available` rung fails
  honestly; no degraded fake path exists.
