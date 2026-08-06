import importlib.util

import pytest


def pytest_collection_modifyitems(config, items):
    if importlib.util.find_spec("OCP") is not None:
        return
    skip_cad = pytest.mark.skip(
        reason="CAD extra not installed — run: pip install --require-hashes "
        "-r requirements-cad.txt"
    )
    for item in items:
        if "cad" in item.keywords:
            item.add_marker(skip_cad)
