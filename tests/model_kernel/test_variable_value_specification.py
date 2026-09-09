"""VS-001 Part A: the value-specification record contract, its canonical
identity, and the identifier grammar.

A specification states what the MODEL requires. It is an unauthenticated
authority claim about the model, never a claim about any source. Lineage
and store validation live in test_specification_lineage.py."""

import hashlib
import json

import pytest
from pydantic import ValidationError

from backend.model_kernel import (
    AuthorityRef,
    DeclaredUnit,
    ModelKernelError,
    OwnerDeclarationEvidence,
    UnitNotDeclared,
    UnitReference,
    VariableValueSpecification,
    build_record,
)
from backend.model_kernel.canonical import canonical_bytes, verify_record_id

from tests.model_kernel.builders import (
    AUTHORITY,
    T0,
    VAR_A,
    VAR_B,
    SPEC_EVIDENCE,
    declared_unit,
    specification,
)

# every value the owner's rejection matrix requires, plus non-ASCII
# lookalikes that a naive ASCII assumption would admit
FORBIDDEN_IDENTIFIERS = [
    pytest.param("", id="empty"),
    pytest.param("Degree_Celsius", id="uppercase"),
    pytest.param(" degree_celsius", id="leading_space"),
    pytest.param("degree_celsius ", id="trailing_space"),
    pytest.param("degree celsius", id="inner_space"),
    pytest.param("degree_celsius\n", id="trailing_lf"),
    pytest.param("degree_celsius\r", id="trailing_cr"),
    pytest.param("degree_celsius\t", id="trailing_tab"),
    pytest.param("degree_celsius\x00", id="trailing_nul"),
    pytest.param("\ndegree_celsius", id="leading_lf"),
    pytest.param("../x", id="path_traversal"),
    pytest.param("°C", id="degree_sign"),
    pytest.param("ｄegree", id="fullwidth_d"),
    pytest.param("dеgree", id="cyrillic_e"),
    pytest.param("degree_celsiuｓ", id="fullwidth_s"),
    pytest.param("ıd", id="dotless_i"),
    pytest.param("degree​celsius", id="zero_width_space"),
    pytest.param("degree celsius", id="line_separator"),
    pytest.param("degreecelsius", id="next_line"),
    pytest.param("_degree", id="leading_underscore"),
    pytest.param("-degree", id="leading_hyphen"),
    pytest.param(".degree", id="leading_dot"),
]

REQUIRED_IDENTIFIERS = ["degree_celsius", "ohk-units-1", "project_local",
                        "a", "1", "x.y.z", "unit-code_1.2"]


class TestIdentifierGrammar:
    """Behaviour is authoritative, not the regex text: the guarantee must
    not rest on which regex engine pydantic happens to default to."""

    @pytest.mark.parametrize("value", FORBIDDEN_IDENTIFIERS)
    def test_forbidden_code_rejected(self, value):
        with pytest.raises(ValidationError):
            UnitReference(system_id="project_local",
                          system_edition="ohk-units-1", code=value)

    @pytest.mark.parametrize("value", FORBIDDEN_IDENTIFIERS)
    def test_forbidden_system_edition_rejected(self, value):
        with pytest.raises(ValidationError):
            UnitReference(system_id="project_local", system_edition=value,
                          code="degree_celsius")

    @pytest.mark.parametrize("value", REQUIRED_IDENTIFIERS)
    def test_required_identifiers_accepted(self, value):
        reference = UnitReference(system_id="project_local",
                                  system_edition=value, code=value)
        assert (reference.system_edition, reference.code) == (value, value)

    def test_grammar_is_enforced_by_behaviour_not_only_by_pattern(self):
        """A trailing newline is the classic engine-dependent hole: it must
        be rejected however the field constraint is spelled."""
        with pytest.raises(ValidationError):
            UnitReference(system_id="project_local",
                          system_edition="ohk-units-1", code="degree\n")

    def test_unit_system_is_closed(self):
        with pytest.raises(ValidationError):
            UnitReference(system_id="ucum", system_edition="2024",
                          code="Cel")


class TestSpecificationShape:
    def test_valid_specification_round_trips(self):
        record = specification()
        assert record.record_id.startswith("vsp_")
        assert verify_record_id(record)
        assert record.variable_anchor_id == VAR_A
        assert record.value_shape == "number"
        assert record.nullable is False
        assert record.unit.kind == "declared"
        assert record.unit.unit.code == "degree_celsius"
        assert record.supersedes == ()

    def test_unit_not_declared_arm(self):
        record = specification(unit=UnitNotDeclared(kind="not_declared"))
        assert record.unit.kind == "not_declared"
        assert not hasattr(record.unit, "unit")

    def test_unit_union_is_discriminated(self):
        with pytest.raises(ValidationError):
            VariableValueSpecification(
                record_id="vsp_" + "0" * 64, variable_anchor_id=VAR_A,
                value_shape="number", unit={"kind": "invented"},
                evidence=SPEC_EVIDENCE, recorded_at=T0, authority=AUTHORITY)

    def test_shape_vocabulary_is_closed(self):
        for shape in ("boolean", "number", "string"):
            assert specification(value_shape=shape).value_shape == shape
        for rejected in ("integer", "Number", "object", "array", "null", ""):
            with pytest.raises(ModelKernelError):
                specification(value_shape=rejected)

    def test_extra_fields_forbidden(self):
        with pytest.raises(ModelKernelError):
            specification(quantity_kind="temperature")
        with pytest.raises(ModelKernelError):
            specification(display_symbol="degC")

    def test_no_display_symbol_field_exists(self):
        assert "display_symbol" not in UnitReference.model_fields

    def test_anchor_is_referenced_not_embedded(self):
        """A specification references the anchor; it never embeds a second
        copy, which is why the cross-layer seam is untouched."""
        assert "anchor" not in VariableValueSpecification.model_fields
        assert isinstance(specification().variable_anchor_id, str)

    @pytest.mark.parametrize("bad", [
        pytest.param("ent_" + "a" * 32, id="entity_anchor"),
        pytest.param("var_" + "a" * 31, id="short"),
        pytest.param("var_" + "G" * 32, id="nonhex"),
        pytest.param("", id="empty"),
    ])
    def test_variable_anchor_id_pattern(self, bad):
        with pytest.raises(ModelKernelError):
            specification(variable_anchor_id=bad)

    @pytest.mark.parametrize("bad_id", [
        pytest.param("vrg_" + "a" * 64, id="wrong_prefix"),
        pytest.param("vsp_" + "a" * 63, id="short_tail"),
        pytest.param("vsp_" + "A" * 64, id="uppercase_tail"),
    ])
    def test_record_id_pattern(self, bad_id):
        record = specification()
        with pytest.raises(ValidationError):
            VariableValueSpecification(
                **{**record.model_dump(), "record_id": bad_id})


class TestEvidenceRequirement:
    def test_empty_evidence_rejected_at_direct_construction(self):
        with pytest.raises(ValidationError):
            VariableValueSpecification(
                record_id="vsp_" + "0" * 64, variable_anchor_id=VAR_A,
                value_shape="number", unit=declared_unit(), evidence=(),
                recorded_at=T0, authority=AUTHORITY)

    def test_empty_evidence_rejected_through_build_record(self):
        with pytest.raises(ModelKernelError) as excinfo:
            specification(evidence=())
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"

    def test_empty_evidence_forgery_rejected_at_revalidation(self):
        from backend.model_kernel.store import revalidate

        forged = VariableValueSpecification.model_construct(
            **{**specification().model_dump(), "evidence": ()})
        with pytest.raises(ModelKernelError) as excinfo:
            revalidate(forged)
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"

    def test_evidence_is_canonically_ordered_and_deduped(self):
        one = OwnerDeclarationEvidence(kind="owner_declaration",
                                       statement="alpha")
        two = OwnerDeclarationEvidence(kind="owner_declaration",
                                       statement="beta")
        forward = specification(evidence=(one, two))
        reversed_ = specification(evidence=(two, one))
        duplicated = specification(evidence=(two, one, two))
        assert forward.record_id == reversed_.record_id == duplicated.record_id
        assert [e.statement for e in forward.evidence] == ["alpha", "beta"]


class TestParentCanonicalization:
    """Accept any input order, reject duplicates, sort canonically — and
    the canonical tuple is what the digest sees."""

    def test_permuted_parents_produce_the_same_record_id(self):
        parents = tuple(f"vsp_{c * 64}" for c in "123")
        forward = specification(supersedes=parents)
        reversed_ = specification(supersedes=tuple(reversed(parents)))
        assert forward.record_id == reversed_.record_id
        assert forward.supersedes == parents  # stored sorted

    def test_duplicate_parents_rejected(self):
        parent = "vsp_" + "1" * 64
        with pytest.raises(ModelKernelError) as excinfo:
            specification(supersedes=(parent, parent))
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"
        with pytest.raises(ValidationError):
            VariableValueSpecification(
                **{**specification().model_dump(),
                   "supersedes": (parent, parent)})

    def test_parent_set_participates_in_the_digest(self):
        one = specification(supersedes=("vsp_" + "1" * 64,))
        two = specification(supersedes=("vsp_" + "2" * 64,))
        assert one.record_id != two.record_id
        assert one.record_id != specification().record_id

    @pytest.mark.parametrize("bad", [
        pytest.param(("vrg_" + "1" * 64,), id="wrong_prefix"),
        pytest.param(("vsp_" + "1" * 63,), id="short"),
        pytest.param(("",), id="empty"),
    ])
    def test_parent_id_pattern(self, bad):
        with pytest.raises(ModelKernelError):
            specification(supersedes=bad)


class TestCanonicalIdentity:
    def test_golden_canonical_vector(self):
        record = specification(evidence=SPEC_EVIDENCE)
        expected = (
            '{"authority":{"agent":"mk001_demo_fixture","kind":"test_fixture",'
            '"method":"manual_declaration"},'
            '"evidence":[{"kind":"owner_declaration",'
            '"statement":"synthetic model-side value specification"}],'
            '"note":"","nullable":false,'
            '"record_kind":"variable_value_specification",'
            '"recorded_at":"2026-08-08T12:00:00+00:00","schema_version":"1",'
            '"supersedes":[],'
            '"unit":{"kind":"declared","unit":{"code":"degree_celsius",'
            '"system_edition":"ohk-units-1","system_id":"project_local"}},'
            '"value_shape":"number",'
            '"variable_anchor_id":"var_11111111111111111111111111111111"}'
        ).encode("utf-8")
        assert canonical_bytes(record) == expected
        assert record.record_id == "vsp_" + hashlib.sha256(
            expected).hexdigest()

    def test_record_id_excluded_from_its_own_digest(self):
        record = specification()
        payload = json.loads(canonical_bytes(record))
        assert "record_id" not in payload

    def test_offset_normalization(self):
        from datetime import timedelta, timezone

        shifted = specification(recorded_at=T0.astimezone(
            timezone(timedelta(hours=2))))
        assert shifted.record_id == specification().record_id

    def test_prefix_table_and_patterns_complete(self):
        import re
        import typing

        from backend.model_kernel.canonical import _PREFIX_BY_KIND
        from backend.model_kernel.contracts import (
            MODEL_RECORD_ID_PATTERN,
            ModelRecord,
        )
        from backend.model_kernel.store import _FILENAME

        members = typing.get_args(ModelRecord)
        assert VariableValueSpecification in members
        # 22 pre-ST-002, three ST-002, three FL-001, two FM-001, two FC-001.
        assert len(_PREFIX_BY_KIND) == len(members) == 32
        assert tuple(_PREFIX_BY_KIND.items())[-2:] == (
            ("flow_operating_criterion_declaration", "fcd"),
            ("flow_operating_criterion_withdrawal", "fcw"))
        assert tuple(cls.__name__ for cls in members[-2:]) == (
            "FlowOperatingCriterionDeclaration", "FlowOperatingCriterionWithdrawal")
        assert {cls.model_fields["record_kind"].default for cls in members} == set(_PREFIX_BY_KIND)
        for prefix in _PREFIX_BY_KIND.values():
            sample = f"{prefix}_{'0' * 64}"
            assert re.fullmatch(MODEL_RECORD_ID_PATTERN, sample)
            assert _FILENAME.fullmatch(sample + ".json")

    def test_identity_binding_canonicalizer_parity(self):
        from backend.identity_binding import canonical as ib_canonical

        record = specification()
        assert ib_canonical.canonical_bytes(record) == canonical_bytes(record)

    def test_specifications_are_citable_as_model_record_evidence(self):
        from backend.model_kernel import ModelRecordEvidence

        cited = ModelRecordEvidence(kind="model_record",
                                    record_id=specification().record_id)
        assert cited.record_id.startswith("vsp_")

    def test_withdrawals_remain_uncitable(self):
        from backend.model_kernel import ModelRecordEvidence

        with pytest.raises(ValidationError):
            ModelRecordEvidence(kind="model_record",
                                record_id="rwd_" + "0" * 64)

    def test_distinct_variables_produce_distinct_records(self):
        assert (specification(variable_anchor_id=VAR_A).record_id
                != specification(variable_anchor_id=VAR_B).record_id)
