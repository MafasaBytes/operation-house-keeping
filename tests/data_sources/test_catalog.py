"""Tests for the in-memory source catalog."""

import pytest

from backend.data_sources.catalog import InMemorySourceCatalog, UnknownSourceError
from backend.data_sources.contracts import SourceDefinition


def make_source(source_id: str = "bom-local", enabled: bool = True) -> SourceDefinition:
    return SourceDefinition(
        source_id=source_id,
        display_name="Local BOM CSV",
        source_kind="tabular_file",
        connector_type="local_file",
        configuration={"path": "backend/data_sources/testing/fixtures/bom_valid.csv"},
        credential_reference=None,
        declared_content_types=["text/csv"],
        enabled=enabled,
    )


class TestCatalog:
    def test_register_and_get(self):
        catalog = InMemorySourceCatalog()
        source = make_source()
        catalog.register(source)
        assert catalog.get("bom-local") == source

    def test_unknown_source_raises(self):
        with pytest.raises(UnknownSourceError):
            InMemorySourceCatalog().get("missing")

    def test_re_register_identical_is_idempotent(self):
        catalog = InMemorySourceCatalog()
        catalog.register(make_source())
        catalog.register(make_source())  # no error
        assert len(catalog.list_sources()) == 1

    def test_re_register_different_definition_raises(self):
        catalog = InMemorySourceCatalog()
        catalog.register(make_source())
        with pytest.raises(ValueError):
            catalog.register(make_source(enabled=False))

    def test_list_enabled_only(self):
        catalog = InMemorySourceCatalog()
        catalog.register(make_source("a", enabled=True))
        catalog.register(make_source("b", enabled=False))
        assert [s.source_id for s in catalog.list_sources(enabled_only=True)] == ["a"]
