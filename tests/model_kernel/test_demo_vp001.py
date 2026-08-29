"""VP-001 Slice D bounded demo-ledger and query contract.

The one association is synthetic, explicit, and context-specific.  These
tests deliberately replay the accepted 28-record PT membership when asking
what the model said before the VP append; current membership is never used to
invent historical state.
"""

from collections import Counter
from datetime import UTC, datetime
import hashlib
from pathlib import Path

from backend.model_kernel import (
    AuthorityRef,
    LifecycleViewContext,
    ModelQueries,
    ModelRecordEvidence,
    ModelStore,
    OwnerDeclarationEvidence,
    VariablePortAssociation,
    build_record,
)
from tests.model_kernel.test_demo_model import (
    CURRENT_REVISION,
    DEMO_MODEL,
    EXTRUDER,
    FROZEN_CN001_MODEL_RECORDS,
    FROZEN_ES001_MODEL_RECORDS,
    FROZEN_MK001_RECORDS,
    FROZEN_PT001_MODEL_RECORDS,
    FROZEN_SN001_MODEL_RECORDS,
    FROZEN_VM001_RECORD,
    FROZEN_VS001_RECORD,
    HOTEND_VARIABLE,
    PRE_VP001_REVISION,
    PT001_MEMBERSHIP,
    VP001_MEMBERSHIP,
    VP001_MODEL_RECORDS,
)
from tests.model_kernel.test_demo_pt001 import (
    ARTIFACT_BYTES as PT_ARTIFACT_BYTES,
    ARTIFACT_SHA256 as PT_ARTIFACT_SHA256,
    EXTRUDER_PORT,
    SUBSYSTEM_PORT,
    _artifact_bytes as pt_artifact_bytes,
)


VPA_ID = (
    "vpa_f6443787fc9665e24cae80a5ba0650d0bda8abefe87cb60427c8b39068932e49"
)
VPA_FILE_SHA256 = (
    "95f9390f784600b2f7a17e74a540d6874722039be5d093614c15a716ff08034e"
)
VPA_FILE_BYTES = 1184
VARIABLE_REGISTRATION_ID = (
    "vrg_40c8c6b984345af33de6913ca9025d60d22b0e627b110e974c78270eb941dca7"
)
PORT_REGISTRATION_ID = (
    "prg_c06e49bef910d073a6af206d884a1bb68c0b9baa1cdb1d698d0c35c61025e057"
)
CONTEXT = LifecycleViewContext(kind="lifecycle_view", view="as_designed")
AUTHORITY = AuthorityRef(
    kind="test_fixture", agent="vp001_demo_fixture",
    method="manual_declaration",
)
OWNER_STATEMENT = (
    "VP-001 fixture authority explicitly declares that the existing "
    "synthetic hotend-temperature variable and the existing synthetic "
    "extruder-unit interface are associated in the as-designed lifecycle "
    "view; illustrative fixture only."
)
NOTE = "VP-001 bounded synthetic demonstration."
DISCLAIMER = (
    "This is an illustrative synthetic VP-001 association fixture. It does "
    "not describe or claim any real printer wiring, signal routing, "
    "connector, protocol, sensing location, measurement location, data path, "
    "flow, command, control, influence, causality, behavior, compatibility, "
    "safety, correctness, activity, or operating condition."
)
WARNINGS = (
    "Shared ownership did not create the association.",
    "Names did not create the association.",
    "Moonraker data did not create the association.",
    "CAD or geometry did not create the association.",
    "PIF tokens did not create the association.",
    "PCN topology did not create the association.",
    "Existing observations did not create the association.",
    "Displaying variable state beside the port does not mean the value "
    "occurred at, originated at, travelled through, or describes the port.",
)


def expected_vpa():
    """Construct the golden record only through the accepted public builder."""
    return build_record(
        VariablePortAssociation,
        variable_anchor_id=HOTEND_VARIABLE,
        port_anchor_id=EXTRUDER_PORT,
        context=CONTEXT,
        evidence=(
            ModelRecordEvidence(
                kind="model_record", record_id=VARIABLE_REGISTRATION_ID),
            ModelRecordEvidence(
                kind="model_record", record_id=PORT_REGISTRATION_ID),
            OwnerDeclarationEvidence(
                kind="owner_declaration", statement=OWNER_STATEMENT),
        ),
        supersedes=(),
        recorded_at=datetime(2026, 8, 29, 12, 0, tzinfo=UTC),
        authority=AUTHORITY,
        note=NOTE,
    )


def predecessor_hashes():
    return {
        **FROZEN_MK001_RECORDS,
        **FROZEN_VM001_RECORD,
        **FROZEN_VS001_RECORD,
        **FROZEN_SN001_MODEL_RECORDS,
        **FROZEN_ES001_MODEL_RECORDS,
        **FROZEN_CN001_MODEL_RECORDS,
        **FROZEN_PT001_MODEL_RECORDS,
    }


def test_public_builder_produces_the_frozen_fixture_identity_and_contract():
    record = expected_vpa()
    assert record.record_id == VPA_ID
    assert record.record_kind == "variable_port_association"
    assert record.schema_version == "1"
    assert record.variable_anchor_id == HOTEND_VARIABLE
    assert record.port_anchor_id == EXTRUDER_PORT
    assert record.context == CONTEXT
    assert record.supersedes == ()
    assert record.recorded_at == datetime(2026, 8, 29, 12, 0, tzinfo=UTC)
    assert record.authority == AUTHORITY
    assert record.note == NOTE
    assert tuple((item.kind, getattr(item, "record_id", None))
                 for item in record.evidence) == (
        ("model_record", PORT_REGISTRATION_ID),
        ("model_record", VARIABLE_REGISTRATION_ID),
        ("owner_declaration", None),
    )
    assert record.evidence[-1].statement == OWNER_STATEMENT


def test_authoritative_append_is_exactly_one_vpa_and_preserves_28_bytes():
    path = DEMO_MODEL / "records" / f"{VPA_ID}.json"
    assert path.is_file() and not path.is_symlink()
    assert len(path.read_bytes()) == VPA_FILE_BYTES
    assert hashlib.sha256(path.read_bytes()).hexdigest() == VPA_FILE_SHA256

    loaded = ModelStore(DEMO_MODEL).load()
    assert loaded.revision.revision_id == CURRENT_REVISION
    assert loaded.revision.record_ids == VP001_MEMBERSHIP
    assert loaded.revision.record_count == 29
    assert VP001_MODEL_RECORDS == (VPA_ID,)
    assert loaded.records[VPA_ID] == expected_vpa()
    assert Counter(record.record_kind for record in loaded.records.values())[
        "variable_port_association"] == 1
    assert not loaded.variable_port_association_withdrawals

    frozen = predecessor_hashes()
    assert len(frozen) == 28
    for filename, digest in frozen.items():
        predecessor = DEMO_MODEL / "records" / filename
        assert hashlib.sha256(predecessor.read_bytes()).hexdigest() == digest


def test_current_exact_reverse_and_assertion_queries_are_one_healthy_root():
    queries = ModelQueries(ModelStore(DEMO_MODEL).load())
    exact = queries.variable_port_association(
        HOTEND_VARIABLE, EXTRUDER_PORT, context=CONTEXT)
    by_variable = queries.ports_associated_with_variable(
        HOTEND_VARIABLE, context=CONTEXT)
    by_port = queries.variables_associated_with_port(
        EXTRUDER_PORT, context=CONTEXT)
    disclosure = queries.variable_port_assertion(VPA_ID)

    assert (exact.endpoint_status, exact.owner_alignment, exact.conclusion,
            exact.lineage_summary) == (
                "both_registered", "same_owner", "asserted", "healthy")
    assert len(exact.roots) == 1
    [root] = exact.roots
    assert root.root_record == expected_vpa()
    assert root.lineage_records == (expected_vpa(),)
    assert root.current_tips == (expected_vpa(),)
    assert root.withdrawals == ()
    assert root.lineage_health == "healthy"

    assert by_variable.status == "registered"
    assert by_port.status == "registered"
    assert len(by_variable.entries) == len(by_port.entries) == 1
    left, right = by_variable.entries[0], by_port.entries[0]
    for entry in (left, right):
        assert entry.entry_index == 0
        assert entry.variable_anchor_id == HOTEND_VARIABLE
        assert entry.port_anchor_id == EXTRUDER_PORT
        assert entry.conclusion == exact.conclusion
        assert entry.lineage_summary == exact.lineage_summary
        assert entry.roots == exact.roots

    assert disclosure.lookup_status == "found"
    assert disclosure.record == expected_vpa()
    assert disclosure.activity == "current"
    assert disclosure.containing_lineage_health == "healthy"
    assert disclosure.root_record == expected_vpa()
    assert disclosure.successors == ()
    assert disclosure.withdrawals == ()


def test_explicit_28_record_replay_is_not_declared_and_registered_empty():
    store = ModelStore(DEMO_MODEL)
    loaded = store.replay(PT001_MEMBERSHIP)
    assert loaded.revision.revision_id == PRE_VP001_REVISION
    assert loaded.revision.record_count == 28
    assert loaded.revision.record_ids == PT001_MEMBERSHIP
    assert not loaded.variable_port_associations
    assert not loaded.variable_port_association_withdrawals

    queries = ModelQueries(loaded)
    exact = queries.variable_port_association(
        HOTEND_VARIABLE, EXTRUDER_PORT, context=CONTEXT)
    assert (exact.endpoint_status, exact.owner_alignment, exact.conclusion,
            exact.lineage_summary, exact.roots) == (
                "both_registered", "same_owner", "not_declared",
                "not_applicable", ())
    assert queries.ports_associated_with_variable(
        HOTEND_VARIABLE, context=CONTEXT).entries == ()
    assert queries.variables_associated_with_port(
        EXTRUDER_PORT, context=CONTEXT).entries == ()
    assert queries.variable_port_assertion(VPA_ID).lookup_status == "not_found"


def test_other_registered_port_remains_empty_and_no_claim_is_inferred():
    queries = ModelQueries(ModelStore(DEMO_MODEL).load())
    other = queries.variables_associated_with_port(
        SUBSYSTEM_PORT, context=CONTEXT)
    assert other.status == "registered"
    assert other.entries == ()
    different_owner = queries.variable_port_association(
        HOTEND_VARIABLE, SUBSYSTEM_PORT, context=CONTEXT)
    assert (different_owner.endpoint_status, different_owner.owner_alignment,
            different_owner.conclusion, different_owner.lineage_summary) == (
                "both_registered", "different_owners", "not_evaluated",
                "not_applicable")
    assert different_owner.roots == ()


def test_fixture_scope_and_accepted_pt_artifact_are_unchanged():
    model_paths = sorted((DEMO_MODEL / "records").glob("*.json"))
    assert len(model_paths) == 29
    assert [path.stem for path in model_paths
            if path.name.startswith("vpa_")] == [VPA_ID]
    assert not any(path.name.startswith("vpw_") for path in model_paths)
    assert not any(path.name.startswith("spj_") for path in model_paths)
    assert len(tuple(Path("interpretations/demo-printer/records").glob(
        "*.json"))) == 3
    assert len(tuple(Path("bindings/demo-printer/records").glob("*.json"))) == 6
    assert len(tuple(Path("bindings/demo-printer-model/records").glob(
        "*.json"))) == 5

    artifact = pt_artifact_bytes()
    assert len(artifact) == PT_ARTIFACT_BYTES
    assert hashlib.sha256(artifact).hexdigest() == PT_ARTIFACT_SHA256


def test_disclaimer_and_non_inference_warnings_are_exact_and_complete():
    assert DISCLAIMER == (
        "This is an illustrative synthetic VP-001 association fixture. It "
        "does not describe or claim any real printer wiring, signal routing, "
        "connector, protocol, sensing location, measurement location, data "
        "path, flow, command, control, influence, causality, behavior, "
        "compatibility, safety, correctness, activity, or operating "
        "condition."
    )
    assert WARNINGS == (
        "Shared ownership did not create the association.",
        "Names did not create the association.",
        "Moonraker data did not create the association.",
        "CAD or geometry did not create the association.",
        "PIF tokens did not create the association.",
        "PCN topology did not create the association.",
        "Existing observations did not create the association.",
        "Displaying variable state beside the port does not mean the value "
        "occurred at, originated at, travelled through, or describes the port.",
    )
    assert EXTRUDER == "ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50"
