"""PT-001 Slice C golden fixture, replay, query, and integrity contract."""

from collections import Counter
import hashlib
import json
from pathlib import Path

import pytest

from backend.model_kernel import LifecycleViewContext, ModelQueries, ModelStore
from tests.model_kernel.test_demo_model import (
    CN001_MEMBERSHIP,
    EXTRUDER, FROZEN_CN001_MODEL_RECORDS, FROZEN_ES001_MODEL_RECORDS,
    FROZEN_MK001_RECORDS, FROZEN_SN001_MODEL_RECORDS,
    FROZEN_PT001_MODEL_RECORDS, FROZEN_VM001_RECORD, FROZEN_VS001_RECORD,
    PRE_CN001_MEMBERSHIP,
    PRE_CN001_REVISION, PRE_ES001_MEMBERSHIP, PRE_ES001_REVISION,
    PRE_PT001_REVISION,
    PRE_SPECIFICATION_MEMBERSHIP, PRE_SPECIFICATION_REVISION,
    PRE_VARIABLE_MEMBERSHIP, PRE_VARIABLE_REVISION, SUBSYSTEM,
    VS001_MEMBERSHIP, GOLDEN_REVISION, PT001_MEMBERSHIP,
    PT001_MODEL_RECORDS,
)


DEMO_MODEL = Path("models/demo-printer")
SUBSYSTEM_PORT = "prt_c1d68d104a73405a950556b55f6a4d34"
EXTRUDER_PORT = "prt_91a3d6db9df440e1a09dbdb185c7b182"
ENDPOINTS = tuple(sorted((SUBSYSTEM_PORT, EXTRUDER_PORT)))
FINAL_REVISION = "mrv_c6244b6dc41de599de9894b55f4064e41ba5260e7d00f50bffc1e1e63da560a2"
CONTEXT = LifecycleViewContext(kind="lifecycle_view", view="as_designed")
AUTHORITY = {
    "kind": "test_fixture", "agent": "pt001_demo_fixture",
    "method": "manual_declaration",
}
DISCLAIMER = (
    "This is an illustrative synthetic PT-001 fixture. It does not describe "
    "or claim any real printer wiring, connector, protocol, pinout, electrical "
    "design, behavior, operating activity, flow, influence, causality, safety "
    "property, correctness, or operating condition."
)
WARNINGS = (
    "Geometry does not create these ports.",
    "CAD does not establish this connection.",
    "Moonraker does not establish this connection.",
    "Token equality does not establish compatibility.",
    "Direction admissibility does not establish flow.",
    "Explicit compatibility remains a declared synthetic claim.",
    "Consistent means only that the explicit declaration does not contradict "
    "the bounded direction table; it does not prove real-world compatibility.",
)

PT001_FILE_SHA256 = {
    filename[:-5]: digest
    for filename, digest in FROZEN_PT001_MODEL_RECORDS.items()
}

# Filled from two byte-identical independent generations, then verified again
# in both clean-checkout columns.
ARTIFACT_BYTES = 33855
ARTIFACT_SHA256 = "53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8"


def _canonical_json_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def _artifact_bytes():
    store = ModelStore(DEMO_MODEL)
    loaded = store.replay(PT001_MEMBERSHIP)
    queries = ModelQueries(loaded)
    ports = tuple(sorted((SUBSYSTEM_PORT, EXTRUDER_PORT)))
    owners = (SUBSYSTEM, EXTRUDER)

    port_results = {port_id: queries.port(port_id) for port_id in ports}
    owner_results = {owner_id: queries.ports_of_entity(owner_id)
                     for owner_id in owners}
    interface_results = {
        port_id: queries.port_interface(port_id, context=CONTEXT)
        for port_id in ports
    }
    exact = queries.connections_exact(ports, context=CONTEXT)
    incidents = {port_id: queries.connections_of_port(
        port_id, context=CONTEXT) for port_id in ports}
    shared = queries.connections_containing(ports, context=CONTEXT)
    assertion_results = {
        record_id: queries.port_assertion(record_id)
        for record_id in PT001_MODEL_RECORDS
    }
    compatibility = queries.interface_compatibility(
        SUBSYSTEM_PORT, EXTRUDER_PORT, context=CONTEXT)

    histories = (
        (PRE_VARIABLE_MEMBERSHIP, PRE_VARIABLE_REVISION),
        (PRE_SPECIFICATION_MEMBERSHIP, PRE_SPECIFICATION_REVISION),
        (VS001_MEMBERSHIP, GOLDEN_REVISION),
        (PRE_ES001_MEMBERSHIP, PRE_ES001_REVISION),
        (PRE_CN001_MEMBERSHIP, PRE_CN001_REVISION),
        (CN001_MEMBERSHIP, PRE_PT001_REVISION),
    )
    replay = []
    for membership, revision_id in histories:
        historical = store.replay(membership)
        historical_queries = ModelQueries(historical)
        historical_exact = historical_queries.connections_exact(
            ports, context=CONTEXT)
        historical_compatibility = historical_queries.interface_compatibility(
            SUBSYSTEM_PORT, EXTRUDER_PORT, context=CONTEXT)
        replay.append({
            "membership": list(membership),
            "record_count": len(membership),
            "revision_id": revision_id,
            "port_statuses": [historical_queries.port(port_id).status
                              for port_id in ports],
            "topology_admission": historical_exact.admission_status,
            "topology_conclusion": historical_exact.conclusion,
            "explicit_compatibility": historical_compatibility.explicit_status,
            "compatibility_endpoints": (
                historical_compatibility.endpoint_registration_status),
        })

    prior_hashes = {
        **FROZEN_MK001_RECORDS, **FROZEN_VM001_RECORD,
        **FROZEN_VS001_RECORD, **FROZEN_SN001_MODEL_RECORDS,
        **FROZEN_ES001_MODEL_RECORDS, **FROZEN_CN001_MODEL_RECORDS,
    }
    content = {
        "model": {
            "model_id": "demo-printer",
            "accepted_base_revision": {
                "revision_id": PRE_PT001_REVISION,
                "record_count": 18,
                "record_ids": list(CN001_MEMBERSHIP),
            },
            "final_revision": loaded.revision.model_dump(mode="json"),
            "prior_record_sha256": dict(sorted(prior_hashes.items())),
            "appended_record_sha256": dict(sorted(
                FROZEN_PT001_MODEL_RECORDS.items())),
            "prior_bytes_preserved": all(
                hashlib.sha256((DEMO_MODEL / "records" / name).read_bytes(
                )).hexdigest() == digest
                for name, digest in prior_hashes.items()),
        },
        "authority": AUTHORITY,
        "context": CONTEXT.model_dump(mode="json"),
        "owners": [{
            "entity_anchor_id": owner_id,
            "entity_registration_id": result.entity_registration.record_id,
            "owned_port_anchor_ids": [record.anchor.anchor_id
                                      for record in result.ports],
        } for owner_id, result in sorted(owner_results.items())],
        "ports": [{
            "anchor": result.registration.anchor.model_dump(mode="json"),
            "registration_record_id": result.registration.record_id,
            "owner_entity_anchor_id": (
                result.registration.owner_entity_anchor_id),
            "owner_registration_record_id": (
                result.owner_registration.record_id),
            "status": result.status,
        } for _, result in sorted(port_results.items())],
        "appended_records": [
            assertion_results[record_id].record.model_dump(mode="json")
            for record_id in PT001_MODEL_RECORDS
        ],
        "interface_queries": [{
            "port_anchor_id": port_id,
            "status": result.status,
            "dimensions": [{
                "dimension": row.dimension,
                "status": row.status,
                "lineage_health": row.lineage_health,
                "declaration_record_id": row.declaration.record_id,
            } for row in result.dimensions],
        } for port_id, result in sorted(interface_results.items())],
        "topology_queries": {
            "exact": {
                "requested_port_anchor_ids": list(
                    exact.requested_port_anchor_ids),
                "admission_status": exact.admission_status,
                "conclusion": exact.conclusion,
                "roots": [{
                    "record_id": root.root.record_id,
                    "lineage_health": root.lineage_health,
                    "exact_endpoint_set": root.exact_endpoint_set,
                } for root in exact.roots],
            },
            "incident": [{
                "port_anchor_id": port_id,
                "status": result.status,
                "conclusion": result.conclusion,
                "root_record_ids": [root.root.record_id
                                    for root in result.roots],
            } for port_id, result in sorted(incidents.items())],
            "shared": {
                "requested_port_anchor_ids": list(
                    shared.requested_port_anchor_ids),
                "admission_status": shared.admission_status,
                "conclusion": shared.conclusion,
                "subjects": [{
                    "endpoint_port_anchor_ids": list(
                        subject.endpoint_port_anchor_ids),
                    "conclusion": subject.conclusion,
                    "exact_endpoint_set": all(
                        shared.roots[index].exact_endpoint_set
                        for index in subject.root_indices),
                } for subject in shared.subjects],
            },
        },
        "assertion_queries": [{
            "record_id": record_id,
            "status": result.status,
            "activity": result.activity,
            "containing_lineage_health": result.lineage_health,
        } for record_id, result in assertion_results.items()],
        "compatibility_query": {
            "requested_left_port_anchor_id": (
                compatibility.requested_left_port_anchor_id),
            "requested_right_port_anchor_id": (
                compatibility.requested_right_port_anchor_id),
            "endpoint_registration_status": (
                compatibility.endpoint_registration_status),
            "interface_domain_relation": compatibility.domain_relation,
            "interface_type_relation": compatibility.interface_type_relation,
            "direction_relation": compatibility.direction_relation,
            "explicit_status": compatibility.explicit_status,
            "explicit_declaration_record_id": compatibility.material.record_at(
                compatibility.explicit_declaration_index).record_id,
            "stale_citation_record_ids": [
                compatibility.material.record_at(index).record_id
                for index in compatibility.stale_citation_indices
            ],
            "cross_finding_consistency": compatibility.consistency,
        },
        "historical_replay": replay,
    }
    content_bytes = _canonical_json_bytes(content)
    payload = {
        "artifact": "PT-001 demo-printer port and connectivity disclosure",
        "schema_version": "1",
        "disclaimer": DISCLAIMER,
        "warnings": list(WARNINGS),
        "artifact_checksum": {
            "algorithm": "sha256",
            "scope": "content",
            "value": hashlib.sha256(content_bytes).hexdigest(),
        },
        "content": content,
    }
    return _canonical_json_bytes(payload)


def test_exact_ten_record_append_and_golden_identity_pins():
    loaded = ModelStore(DEMO_MODEL).replay(PT001_MEMBERSHIP)
    assert loaded.revision.revision_id == FINAL_REVISION
    assert loaded.revision.record_count == 28
    assert loaded.revision.record_ids == PT001_MEMBERSHIP
    assert Counter(record.record_kind for record in loaded.records.values()
                   if record.record_id in PT001_MODEL_RECORDS) == {
        "port_registration": 2,
        "port_interface_declaration": 6,
        "port_connection_assertion": 1,
        "port_compatibility_declaration": 1,
    }
    for record_id, digest in PT001_FILE_SHA256.items():
        path = DEMO_MODEL / "records" / f"{record_id}.json"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest


def test_all_eighteen_pre_pt_records_remain_byte_frozen():
    frozen = {
        **FROZEN_MK001_RECORDS, **FROZEN_VM001_RECORD,
        **FROZEN_VS001_RECORD, **FROZEN_SN001_MODEL_RECORDS,
        **FROZEN_ES001_MODEL_RECORDS, **FROZEN_CN001_MODEL_RECORDS,
    }
    assert len(frozen) == 18
    for filename, digest in frozen.items():
        assert hashlib.sha256((DEMO_MODEL / "records" / filename).read_bytes(
        )).hexdigest() == digest


def test_every_historical_membership_replays_without_port_artifacts():
    store = ModelStore(DEMO_MODEL)
    histories = (
        (PRE_VARIABLE_MEMBERSHIP, PRE_VARIABLE_REVISION),
        (PRE_SPECIFICATION_MEMBERSHIP, PRE_SPECIFICATION_REVISION),
        (VS001_MEMBERSHIP, GOLDEN_REVISION),
        (PRE_ES001_MEMBERSHIP, PRE_ES001_REVISION),
        (PRE_CN001_MEMBERSHIP, PRE_CN001_REVISION),
        (CN001_MEMBERSHIP, PRE_PT001_REVISION),
    )
    for membership, revision in histories:
        loaded = store.replay(membership)
        assert loaded.revision.revision_id == revision
        assert not loaded.port_registrations_by_anchor
        assert not loaded.port_interface_declarations
        assert not loaded.port_connections
        assert not loaded.port_compatibility_declarations
        queries = ModelQueries(loaded)
        for owner_id in (SUBSYSTEM, EXTRUDER):
            owned = queries.ports_of_entity(owner_id)
            assert owned.status == "registered"
            assert owned.ports == ()
        assert queries.port(SUBSYSTEM_PORT).status == "not_registered"
        assert queries.port(EXTRUDER_PORT).status == "not_registered"
        for port_id in ENDPOINTS:
            interface = queries.port_interface(port_id, context=CONTEXT)
            assert interface.status == "not_registered"
            assert tuple(row.status for row in interface.dimensions) == (
                "port_not_registered",) * 3
        exact = queries.connections_exact(ENDPOINTS, context=CONTEXT)
        assert (exact.admission_status, exact.conclusion) == (
            "endpoint_not_registered", "unknown")
        compatibility = queries.interface_compatibility(
            SUBSYSTEM_PORT, EXTRUDER_PORT, context=CONTEXT)
        assert compatibility.endpoint_registration_status == \
            "both_not_registered"
        assert compatibility.explicit_status == "not_declared"
    assert store.replay(PT001_MEMBERSHIP).revision.revision_id == FINAL_REVISION


def test_fixture_records_have_exact_owners_authority_context_and_declarations():
    loaded = ModelStore(DEMO_MODEL).load()
    subsystem = loaded.port_registrations_by_anchor[SUBSYSTEM_PORT]
    extruder = loaded.port_registrations_by_anchor[EXTRUDER_PORT]
    assert subsystem.owner_entity_anchor_id == SUBSYSTEM
    assert extruder.owner_entity_anchor_id == EXTRUDER
    assert subsystem.anchor.anchor_id == SUBSYSTEM_PORT
    assert extruder.anchor.anchor_id == EXTRUDER_PORT
    for record_id in PT001_MODEL_RECORDS:
        record = loaded.records[record_id]
        assert record.authority.model_dump() == AUTHORITY
        assert record.recorded_at.isoformat() == "2026-08-27T12:00:00+00:00"
        if hasattr(record, "supersedes"):
            assert record.supersedes == ()

    expected = {
        SUBSYSTEM_PORT: {
            "interface_domain": ("interface_domain", "project_local",
                                 "pt001-demo-1", "synthetic-exchange"),
            "direction_role": "output",
            "interface_type": ("interface_type", "project_local",
                               "pt001-demo-1", "synthetic-interface"),
        },
        EXTRUDER_PORT: {
            "interface_domain": ("interface_domain", "project_local",
                                 "pt001-demo-1", "synthetic-exchange"),
            "direction_role": "input",
            "interface_type": ("interface_type", "project_local",
                               "pt001-demo-1", "synthetic-interface"),
        },
    }
    queries = ModelQueries(loaded)
    for port_id, dimensions in expected.items():
        result = queries.port_interface(port_id, context=CONTEXT)
        assert result.status == "registered"
        assert tuple(row.status for row in result.dimensions) == (
            "declared", "declared", "declared")
        for row in result.dimensions:
            value = row.declaration.declaration.value
            actual = value if isinstance(value, str) else (
                value.token_kind, value.system_id, value.system_edition,
                value.code)
            assert actual == dimensions[row.dimension]


def test_connection_compatibility_and_all_public_lookups_agree():
    loaded = ModelStore(DEMO_MODEL).load()
    queries = ModelQueries(loaded)
    for port_id in ENDPOINTS:
        assert queries.port(port_id).status == "registered"
    assert [record.anchor.anchor_id for record in
            queries.ports_of_entity(SUBSYSTEM).ports] == [SUBSYSTEM_PORT]
    assert [record.anchor.anchor_id for record in
            queries.ports_of_entity(EXTRUDER).ports] == [EXTRUDER_PORT]
    exact = queries.connections_exact(ENDPOINTS, context=CONTEXT)
    incident_left = queries.connections_of_port(SUBSYSTEM_PORT, context=CONTEXT)
    incident_right = queries.connections_of_port(EXTRUDER_PORT, context=CONTEXT)
    shared = queries.connections_containing(ENDPOINTS, context=CONTEXT)
    assert (exact.admission_status, exact.conclusion) == ("admitted", "asserted")
    assert (incident_left.status, incident_left.conclusion) == (
        "registered", "asserted")
    assert (incident_right.status, incident_right.conclusion) == (
        "registered", "asserted")
    assert (shared.admission_status, shared.conclusion) == (
        "admitted", "asserted")
    roots = [result.material.records[result.roots[0].root_record_index].record_id
             for result in (exact, incident_left, incident_right, shared)]
    assert roots == [PT001_MODEL_RECORDS[-2]] * 4
    assert all(result.roots[0].lineage_health == "healthy"
               for result in (exact, incident_left, incident_right, shared))
    assert exact.roots[0].exact_endpoint_set is True
    assert shared.roots[0].exact_endpoint_set is True
    assert tuple(subject.endpoint_port_anchor_ids
                 for subject in shared.subjects) == (ENDPOINTS,)
    connection = loaded.records[PT001_MODEL_RECORDS[-2]]
    assert connection.endpoint_port_anchor_ids == ENDPOINTS

    compatibility = queries.interface_compatibility(
        SUBSYSTEM_PORT, EXTRUDER_PORT, context=CONTEXT)
    assert compatibility.endpoint_registration_status == "both_registered"
    assert compatibility.domain_relation == "token_identical"
    assert compatibility.interface_type_relation == "token_identical"
    assert compatibility.direction_relation == "admissible"
    assert compatibility.explicit_status == "declared_compatible"
    assert compatibility.consistency == "consistent"
    assert compatibility.stale_citation_indices == ()
    assert compatibility.material.records[
        compatibility.explicit_declaration_index].record_id == \
        PT001_MODEL_RECORDS[-1]
    for index, record_id in enumerate(PT001_MODEL_RECORDS):
        disclosure = queries.port_assertion(record_id)
        assert disclosure.status == "found"
        if index < 2:
            assert disclosure.activity is None
            assert disclosure.lineage_health is None
        else:
            assert disclosure.activity == "current"
            assert disclosure.lineage_health == "healthy"


def test_pcm_basis_is_complete_ordered_current_and_evidence_backed():
    loaded = ModelStore(DEMO_MODEL).load()
    pcm = loaded.records[PT001_MODEL_RECORDS[-1]]
    assert pcm.endpoint_port_anchor_ids == ENDPOINTS
    assert pcm.context == CONTEXT
    assert pcm.outcome == "declared_compatible"
    assert tuple(item.dimension for item in pcm.basis.dimensions) == (
        "interface_domain", "direction_role", "interface_type")
    citations = tuple(citation for dimension in pcm.basis.dimensions
                      for citation in dimension.citations)
    assert len(citations) == 6
    assert tuple(citation.port_anchor_id for citation in citations) == \
        ENDPOINTS * 3
    assert {citation.declaration_record_id for citation in citations} == set(
        PT001_MODEL_RECORDS[2:8])
    assert {ref.record_id for ref in pcm.evidence
            if ref.kind == "model_record"} == set(PT001_MODEL_RECORDS[2:8])


def test_disclaimers_are_explicit_and_forbidden_records_were_not_committed():
    loaded = ModelStore(DEMO_MODEL).load()
    text = "\n".join(
        str(loaded.records[record_id].model_dump(mode="json"))
        for record_id in PT001_MODEL_RECORDS)
    for required in (
        "illustrative fixture only",
        "not a real printer wiring",
        "proves no flow, activity, influence, causality, or control",
        "not inferred from token identity or direction",
        "proves no real-world compatibility, operation, correctness, or safety",
    ):
        assert required in text
    assert not any(record.record_kind == "port_claim_withdrawal"
                   for record in loaded.records.values())
    committed_roots = tuple(Path(name) for name in (
        "models", "bindings", "interpretations", "showcases", "var"))
    assert not [path for root in committed_roots
                for path in root.rglob("spj_*.json")]
    assert len(list(Path("interpretations/demo-printer/records").glob(
        "*.json"))) == 3
    assert len(list(Path("bindings/demo-printer/records").glob("*.json"))) == 6
    assert len(list(Path("bindings/demo-printer-model/records").glob(
        "*.json"))) == 5


def test_mandatory_disclaimer_and_warnings_are_exact_in_all_three_surfaces():
    specification = Path(
        "docs/superpowers/specs/2026-08-20-pt001-explicit-ports-and-connectivity-design.md"
    ).read_text(encoding="utf-8")
    fixture_documentation = Path("models/demo-printer/README.md").read_text(
        encoding="utf-8")
    artifact = _artifact_bytes().decode("ascii")
    for text in (specification, fixture_documentation, artifact):
        assert DISCLAIMER in text
    for warning in WARNINGS[:6]:
        assert warning in artifact


def test_pt001_final_owner_acceptance_status_is_exact():
    status_paths = (
        Path("CLAUDE.md"),
        Path("backend/model_kernel/README.md"),
        Path("docs/adr/0013-explicit-ports-and-typed-interface-connectivity.md"),
        Path(
            "docs/superpowers/specs/"
            "2026-08-20-pt001-explicit-ports-and-connectivity-design.md"),
        Path(
            "docs/superpowers/plans/"
            "2026-08-20-pt001-slice-a-implementation-plan.md"),
        Path(
            "docs/superpowers/plans/"
            "2026-08-20-pt001-adversarial-acceptance-matrix.md"),
    )
    required = (
        "PT-001 complete, owner accepted, adversarially reviewed, and "
        "dual-clean-checkout verified.",
        "Slice A is owner accepted.",
        "The qualified-token repair is owner accepted.",
        "Slice B is owner accepted.",
        "The public-contract repair is owner accepted.",
        "Slice C is owner accepted.",
        "The model ledger contains exactly 28 records.",
        FINAL_REVISION,
        ARTIFACT_SHA256,
    )
    for path in status_paths:
        text = " ".join(path.read_text(encoding="utf-8").split())
        for statement in required:
            assert statement in text, (path, statement)
        pt_status = text[text.index(required[0]):]
        for vp_boundary in (
                "VP-001 Slices A and B are owner accepted",
                "VP-001 Slice A is owner accepted"):
            if vp_boundary in pt_status:
                pt_status = pt_status.split(vp_boundary, 1)[0]
                break
        assert "awaiting owner acceptance" not in pt_status


def test_current_results_reject_fixture_specific_forgery_and_reordering():
    queries = ModelQueries(ModelStore(DEMO_MODEL).load())
    exact = queries.connections_exact(ENDPOINTS, context=CONTEXT)
    with pytest.raises(ValueError):
        type(exact).model_validate(exact.model_copy(update={
            "admission_status": "endpoint_not_registered"}))
    with pytest.raises(ValueError):
        type(exact).model_validate(exact.model_copy(update={
            "conclusion": "inactive"}))
    compatibility = queries.interface_compatibility(
        SUBSYSTEM_PORT, EXTRUDER_PORT, context=CONTEXT)
    with pytest.raises(ValueError):
        type(compatibility).model_validate(compatibility.model_copy(update={
            "explicit_status": "stale"}))
    with pytest.raises(ValueError):
        type(compatibility).model_validate(compatibility.model_copy(update={
            "requested_left_port_anchor_id": EXTRUDER_PORT}))


def test_deterministic_artifact_bytes_and_sha256():
    left = _artifact_bytes()
    right = _artifact_bytes()
    assert left == right
    assert len(left) == ARTIFACT_BYTES
    assert hashlib.sha256(left).hexdigest() == ARTIFACT_SHA256
    assert DISCLAIMER.encode("ascii") in left
    for warning in WARNINGS:
        assert warning.encode("ascii") in left
    payload = json.loads(left)
    content_bytes = _canonical_json_bytes(payload["content"])
    assert payload["artifact_checksum"] == {
        "algorithm": "sha256",
        "scope": "content",
        "value": hashlib.sha256(content_bytes).hexdigest(),
    }
    assert "/mnt/" not in left.decode("ascii")
    assert "/home/" not in left.decode("ascii")
