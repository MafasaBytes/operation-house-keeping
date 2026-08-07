"""IB-001 anchor value contracts: opaque IDs, non-identifying names,
purity of the system_identity package."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.system_identity import EntityAnchor, VariableAnchor

ENT = "ent_" + "a" * 32
VAR = "var_" + "b" * 32


def entity(**overrides):
    fields = dict(
        anchor_id=ENT, namespace="demo-printer",
        display_name="Extruder unit", role_name="extruder-unit",
        referent_kind="physical_instance",
    )
    fields.update(overrides)
    return EntityAnchor(**fields)


def variable(**overrides):
    fields = dict(
        anchor_id=VAR, entity_anchor_id=ENT, namespace="demo-printer",
        display_name="Hotend temperature", role_name="hotend-temperature",
    )
    fields.update(overrides)
    return VariableAnchor(**fields)


class TestEntityAnchor:
    def test_valid_anchor_constructs(self):
        anchor = entity()
        assert anchor.anchor_id == ENT
        assert anchor.referent_kind == "physical_instance"

    @pytest.mark.parametrize("bad_id", [
        "ent-" + "a" * 32,          # wrong separator
        "ent_" + "A" * 32,          # uppercase hex forbidden (path safety)
        "ent_" + "a" * 31,          # too short
        "ent_" + "a" * 33,          # too long
        "var_" + "a" * 32,          # variable prefix on an entity
        "a" * 36,                   # no prefix
    ])
    def test_id_pattern_enforced(self, bad_id):
        with pytest.raises(ValidationError):
            entity(anchor_id=bad_id)

    @pytest.mark.parametrize("field,value", [
        ("namespace", "Demo Printer"), ("namespace", "demo_printer"),
        ("namespace", ""), ("role_name", "Extruder Unit"),
        ("display_name", ""),
    ])
    def test_non_identifying_fields_validated(self, field, value):
        with pytest.raises(ValidationError):
            entity(**{field: value})

    def test_role_name_is_optional(self):
        assert entity(role_name=None).role_name is None

    @pytest.mark.parametrize("kind", [
        "physical_instance", "logical_instance", "type_definition", "unknown",
    ])
    def test_all_four_referent_kinds_accepted(self, kind):
        assert entity(referent_kind=kind).referent_kind == kind

    def test_richer_classification_rejected(self):
        with pytest.raises(ValidationError):
            entity(referent_kind="subsystem")

    def test_frozen_and_extra_forbid(self):
        anchor = entity()
        with pytest.raises(ValidationError):
            anchor.display_name = "renamed"
        with pytest.raises(ValidationError):
            entity(parent_id="x")  # no hierarchy fields, ever


class TestVariableAnchor:
    def test_valid_variable_constructs(self):
        assert variable().entity_anchor_id == ENT

    def test_owner_must_be_entity_id(self):
        with pytest.raises(ValidationError):
            variable(entity_anchor_id=VAR)

    def test_variable_id_pattern(self):
        with pytest.raises(ValidationError):
            variable(anchor_id=ENT)

    def test_no_semantic_fields(self):
        # a variable anchor names a variable; it never carries units/meaning
        with pytest.raises(ValidationError):
            variable(unit="celsius")


class TestPackagePurity:
    def test_system_identity_imports_nothing_from_backend(self):
        """system_identity is the future kernel's shared namespace: it must
        not depend on data_sources, temporal_state, or identity_binding."""
        pkg = Path("backend/system_identity")
        for source in pkg.rglob("*.py"):
            text = source.read_text(encoding="utf-8")
            for forbidden in ("backend.data_sources", "backend.temporal_state",
                              "backend.identity_binding"):
                assert forbidden not in text, f"{source} imports {forbidden}"
