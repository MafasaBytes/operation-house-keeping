# Third-Party Notices

This project depends on third-party software. This file records license
layers and redistribution obligations for dependencies that carry
obligations beyond permissive attribution.

## cadquery-ocp (optional CAD extra, `requirements-cad.txt`)

`cadquery-ocp` provides Python bindings (OCP) to Open CASCADE Technology.
Two license layers apply:

1. **OCP bindings — Apache License 2.0.**
   Copyright the CadQuery/OCP contributors.
   https://github.com/CadQuery/OCP

2. **Open CASCADE Technology (OCCT) runtime libraries — GNU LGPL v2.1
   with the Open CASCADE additional exception.**
   Copyright Open Cascade SAS.
   https://dev.opencascade.org/

   The wheel bundles OCCT as dynamically linked shared libraries. Our
   code uses OCCT only through these libraries and does not modify OCCT.

### Redistribution obligations (OCCT / LGPL-2.1 + exception)

Installing via pip for internal use imposes no additional obligations.
If this project ever **redistributes** the OCCT libraries (for example by
shipping the wheel inside an installer, container image offered to third
parties, or vendored artifact), the distributor must:

- include the OCCT LGPL-2.1 license text and the Open CASCADE exception
  notice;
- preserve copyright notices;
- state modifications if OCCT itself is modified (we make none);
- keep OCCT replaceable by the recipient — satisfied here by dynamic
  linking; do not switch to static linking without revisiting this
  notice.

## PDF extraction closure (optional, `requirements-pdf.txt`)

All permissive; obligations are notice preservation on redistribution.

- **pdfplumber** — MIT. https://github.com/jsvine/pdfplumber
- **pdfminer.six** — MIT. https://github.com/pdfminer/pdfminer.six
- **pypdf** — BSD-3-Clause. https://github.com/py-pdf/pypdf
- **pypdfium2** — bindings BSD-3-Clause OR Apache-2.0. The wheel bundles
  the compiled PDFium library and ships its license inventory in-wheel at
  `pypdfium2-*.dist-info/licenses/`: `LICENSES/` (Apache-2.0,
  BSD-3-Clause, CC-BY-4.0) and per-platform `BUILD_LICENSES/` for PDFium's
  bundled components (verified for the pinned 5.12.1 linux_x64 wheel:
  abseil, agg23, fast_float, freetype, icu, and further entries in that
  directory). If the wheel is ever redistributed, preserve that directory.
  https://github.com/pypdfium2-team/pypdfium2
- **Pillow** — MIT-CMU. Bundles native imaging libraries; license file
  shipped in-wheel. https://python-pillow.github.io/
- **cryptography** — Apache-2.0 OR BSD-3-Clause (ships both texts
  in-wheel). https://github.com/pyca/cryptography
- **charset-normalizer** — MIT. **typing_extensions** — PSF-2.0.

Note: PDFium, Pillow, and cryptography contain native compiled
components; the PDF toolchain is not pure Python and runs only inside the
isolated extraction worker.

## pydantic (core runtime dependency)

MIT License. Copyright the pydantic contributors.
https://github.com/pydantic/pydantic
