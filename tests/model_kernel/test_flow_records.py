"""FL-001 Slice A exact record, evidence, and semantic-boundary contracts."""

import pytest
from pydantic import TypeAdapter, ValidationError

import backend.model_kernel as kernel

from tests.model_kernel.fl001_slice_a_helpers import (
    AS_DESIGNED,
    AUTHORITY,
    FLOW_A,
    PORT_A,
    PORT_B,
    FLOW_DECLARATION_CLAIM,
    direction_pin,
    flow_declaration,
    flow_fixture,
    flow_kind,
    flow_registration,
    flow_withdrawal,
)


def complete_claims():
    _, registration, ports, pcn, source_pifs, sink_pifs = flow_fixture()
    declaration = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=source_pifs, sink_pifs=sink_pifs)
    return registration, declaration, flow_withdrawal(declaration)


def test_flow_kind_pin_and_records_have_exact_field_order():
    registration, declaration, withdrawal = complete_claims()
    assert tuple(kernel.FlowKindToken.model_fields) == (
        "token_kind", "system_id", "system_edition", "code")
    assert tuple(kernel.FlowDirectionDeclarationPin.model_fields) == (
        "port_anchor_id", "declaration_record_id")
    assert tuple(type(registration).model_fields) == (
        "record_kind", "schema_version", "record_id", "anchor",
        "source_port_anchor_ids", "sink_port_anchor_ids", "flow_kind",
        "evidence", "recorded_at", "authority", "note")
    assert tuple(type(declaration).model_fields) == (
        "record_kind", "schema_version", "record_id", "flow_anchor_id",
        "context", "connection_assertion_record_id",
        "source_direction_pins", "sink_direction_pins", "evidence",
        "supersedes", "recorded_at", "authority", "note")
    assert tuple(type(withdrawal).model_fields) == (
        "record_kind", "schema_version", "record_id", "withdraws",
        "recorded_at", "authority", "note")
    assert (registration.record_kind, declaration.record_kind,
            withdrawal.record_kind) == (
                "flow_registration", "flow_declaration",
                "flow_declaration_withdrawal")


def test_public_builder_direct_construction_and_model_union_have_parity():
    adapter = TypeAdapter(kernel.ModelRecord)
    for record in complete_claims():
        direct = type(record)(**record.model_dump(mode="python"))
        rebuilt = adapter.validate_python(record.model_dump(mode="python"))
        assert direct == record
        assert type(rebuilt) is type(record)


@pytest.mark.parametrize(("source", "sink"), [
    ((), (PORT_B,)),
    ((PORT_A,), ()),
    ((PORT_A, PORT_A), (PORT_B,)),
    ((PORT_A,), (PORT_B, PORT_B)),
    ((PORT_A,), (PORT_A,)),
    (("bad-port",), (PORT_B,)),
])
def test_registration_rejects_empty_duplicate_overlap_and_malformed_roles(
        source, sink):
    with pytest.raises(kernel.ModelIntegrityError) as error:
        flow_registration(
            source_ports=source, sink_ports=sink, port_records=())
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_registration_rejects_over_limit_union_and_canonicalizes_each_role():
    source = tuple("prt_" + f"{index:032x}" for index in range(1, 64))
    sink = ("prt_" + f"{64:032x}", "prt_" + f"{65:032x}")
    with pytest.raises(kernel.ModelIntegrityError):
        flow_registration(source_ports=source, sink_ports=sink)
    ordered = flow_registration(
        source_ports=(PORT_B, PORT_A),
        sink_ports=("prt_" + "4" * 32, "prt_" + "3" * 32))
    assert ordered.source_port_anchor_ids == (PORT_A, PORT_B)
    assert ordered.sink_port_anchor_ids == (
        "prt_" + "3" * 32, "prt_" + "4" * 32)


def test_direction_pins_and_parents_canonicalize_but_duplicates_reject():
    registration, declaration, _ = complete_claims()
    pin_a = direction_pin(PORT_A, "pif_" + "a" * 64)
    pin_b = direction_pin(PORT_B, "pif_" + "b" * 64)
    payload = declaration.model_dump(mode="python", exclude={"record_id"})
    payload["source_direction_pins"] = (pin_b, pin_a)
    payload["sink_direction_pins"] = (direction_pin(
        "prt_" + "3" * 32, "pif_" + "c" * 64),)
    candidate = kernel.build_record(kernel.FlowDeclaration, **payload)
    assert tuple(pin.port_anchor_id for pin in
                 candidate.source_direction_pins) == (PORT_A, PORT_B)
    for field, value in (
        ("source_direction_pins", (pin_a, pin_a)),
        ("supersedes", ("fld_" + "a" * 64, "fld_" + "a" * 64)),
    ):
        with pytest.raises(kernel.ModelIntegrityError):
            flow_declaration(
                registration,
                port_records=(), pcn=type("P", (), {"record_id":
                    declaration.connection_assertion_record_id})(),
                source_pifs=(), sink_pifs=(), **{field: value})


@pytest.mark.parametrize("parents", [
    ("frg_" + "a" * 64,),
    ("flw_" + "a" * 64,),
    ("fld_NOT_HEX",),
])
def test_declaration_parents_accept_only_fld_ids(parents):
    _, declaration, _ = complete_claims()
    with pytest.raises(ValidationError):
        kernel.FlowDeclaration(**{
            **declaration.model_dump(mode="python"), "supersedes": parents})


def test_flow_records_reject_hidden_nested_fields_at_direct_and_builder_edges():
    registration, declaration, withdrawal = complete_claims()
    cases = (
        (registration, "anchor", registration.anchor.model_copy(
            update={"physical_mechanism": "forged"})),
        (registration, "flow_kind", registration.flow_kind.model_copy(
            update={"commodity": "forged"})),
        (registration, "authority", registration.authority.model_copy(
            update={"priority": 1})),
        (registration, "evidence", (
            registration.evidence[0].model_copy(update={"flowing": True}),
            *registration.evidence[1:])),
        (declaration, "context", declaration.context.model_copy(
            update={"cutoff": "2026-09-02T12:00:00Z"})),
        (declaration, "source_direction_pins", (
            declaration.source_direction_pins[0].model_copy(
                update={"role": "source"}),)),
        (withdrawal, "authority", withdrawal.authority.model_copy(
            update={"stopped": True})),
    )
    for record, field, forged in cases:
        payload = record.model_dump(mode="python")
        payload[field] = forged
        with pytest.raises(ValidationError):
            type(record)(**payload)
        payload.pop("record_id")
        with pytest.raises(kernel.ModelIntegrityError) as error:
            kernel.build_record(type(record), **payload)
        assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_private_state_on_nested_anchor_is_rejected_by_flow_record_boundary():
    registration, _, _ = complete_claims()
    forged = registration.anchor.model_copy()
    object.__setattr__(forged, "__pydantic_private__", {"flowing": True})
    payload = registration.model_dump(mode="python", exclude={"record_id"})
    payload["anchor"] = forged
    with pytest.raises(kernel.ModelIntegrityError) as error:
        kernel.build_record(kernel.FlowRegistration, **payload)
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_evidence_grammar_adds_only_frg_and_fld():
    existing = (
        "reg", "rtd", "rel", "vrg", "vsp", "vsm", "crg", "vcn",
        "prg", "pif", "pcn", "pcm", "vpa", "brg", "bhd", "srg",
        "std", "trg", "trd",
    )
    for prefix in (*existing, "frg", "fld"):
        record_id = prefix + "_" + "a" * 64
        assert kernel.ModelRecordEvidence(
            kind="model_record", record_id=record_id).record_id == record_id
    for prefix in ("flw", "rwd", "ptw", "vpw", "bhw", "stw", "trw"):
        with pytest.raises(ValidationError):
            kernel.ModelRecordEvidence(
                kind="model_record", record_id=prefix + "_" + "a" * 64)


@pytest.mark.parametrize(("factory", "forbidden"), [
    (flow_registration, {
        "context": AS_DESIGNED, "connection_anchor_id": "cnn_" + "a" * 32,
        "mechanism": "pipe", "activity": "current", "rate": "1"}),
])
def test_registration_forbids_context_mechanism_activity_and_rate(
        factory, forbidden):
    for field, value in forbidden.items():
        with pytest.raises(kernel.ModelIntegrityError):
            factory(**{field: value})


def test_declaration_and_withdrawal_forbid_assessment_occurrence_and_effects():
    registration, declaration, _ = complete_claims()
    fixture = flow_fixture()
    _, _, ports, pcn, source_pifs, sink_pifs = fixture
    for field, value in {
        "source_selector": "latest", "cutoff": "2026-09-02T12:00:00Z",
        "observed": True, "commanded": True, "occurrence": True,
        "flow_rate": "1", "conserved": True, "cause": "forged",
        "safe": True, "recommended_action": "none",
    }.items():
        with pytest.raises(kernel.ModelIntegrityError):
            flow_declaration(
                registration, port_records=ports, pcn=pcn,
                source_pifs=source_pifs, sink_pifs=sink_pifs,
                **{field: value})
    for field, value in (
        ("evidence", (FLOW_DECLARATION_CLAIM,)),
        ("context", AS_DESIGNED),
        ("supersedes", ("fld_" + "a" * 64,)),
        ("stopped", True),
    ):
        with pytest.raises(kernel.ModelIntegrityError):
            flow_withdrawal(declaration, **{field: value})


def test_slice_a_exports_exactly_five_flow_kernel_contracts():
    expected = {
        "FlowKindToken", "FlowDirectionDeclarationPin",
        "FlowRegistration", "FlowDeclaration",
        "FlowDeclarationWithdrawal",
    }
    assert {name for name in kernel.__all__ if name.startswith("Flow")} == \
        expected
    for forbidden in (
        "FlowLookupResult", "FlowAssessment", "FlowOccurrence",
        "ConnectionAnchor",
    ):
        assert forbidden not in kernel.__all__
        assert not hasattr(kernel, forbidden)


def test_flow_kind_is_exact_nominal_and_has_no_decomposed_semantics():
    token = flow_kind()
    assert token.model_dump() == {
        "token_kind": "flow_kind",
        "system_id": "project_local",
        "system_edition": "ohk-flow-kinds-1",
        "code": "synthetic_transfer",
    }
    for forbidden in (
        "commodity", "carrier", "phase", "unit", "rate", "mechanism"):
        with pytest.raises(ValidationError):
            kernel.FlowKindToken(**{**token.model_dump(), forbidden: "x"})
