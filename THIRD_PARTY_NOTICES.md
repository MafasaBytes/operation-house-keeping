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

## pydantic (core runtime dependency)

MIT License. Copyright the pydantic contributors.
https://github.com/pydantic/pydantic
