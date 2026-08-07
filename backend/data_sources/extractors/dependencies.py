"""Extraction dependency declarations per content type.

The connector `available` status rung uses this to report honestly whether
the toolchain needed to extract a source's declared content type is
actually importable — a profile entry or catalog declaration never implies
capability.
"""

import importlib.util

EXTRACTION_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "text/csv": (),  # stdlib only
    "model/step": ("OCP",),
    "application/pdf": ("pdfplumber", "pypdf", "pypdfium2"),
}


def check_extraction_dependencies(content_type: str) -> tuple[bool, str]:
    required = EXTRACTION_DEPENDENCIES.get(content_type, ())
    if not required:
        return True, (
            f"no extraction dependencies required for {content_type!r} "
            "beyond the standard library"
        )
    missing = [name for name in required if importlib.util.find_spec(name) is None]
    if missing:
        return False, (
            f"extraction dependencies missing for {content_type!r}: "
            f"{', '.join(missing)}"
        )
    return True, (
        f"extraction dependencies importable for {content_type!r}: "
        f"{', '.join(required)}"
    )
