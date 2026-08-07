import importlib.util

import pytest

_EXTRAS = {
    "cad": (("OCP",), "CAD extra not installed — run: pip install "
            "--require-hashes -r requirements-cad.txt"),
    "pdf": (("pdfplumber", "pypdf", "pypdfium2"), "PDF extra not installed — "
            "run: pip install --require-hashes -r requirements-pdf.txt"),
}


def pytest_collection_modifyitems(config, items):
    missing_markers = {
        marker: pytest.mark.skip(reason=reason)
        for marker, (modules, reason) in _EXTRAS.items()
        if any(importlib.util.find_spec(m) is None for m in modules)
    }
    if not missing_markers:
        return
    for item in items:
        for marker, skip in missing_markers.items():
            if marker in item.keywords:
                item.add_marker(skip)
