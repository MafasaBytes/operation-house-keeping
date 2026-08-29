"""VP-001 Slice D read-only state and deterministic disclosure demo."""

from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path

from backend.identity_binding.facade import BoundTemporalQueries
from backend.identity_binding.resolver import BindingResolver
from backend.identity_binding.store import BindingStore
from backend.model_kernel import LifecycleViewContext, ModelQueries, ModelStore
from backend.model_state import ModelStateQueries
from tests.model_kernel.test_demo_model import (
    CURRENT_REVISION,
    DEMO_MODEL,
    FROZEN_CN001_MODEL_RECORDS,
    FROZEN_ES001_MODEL_RECORDS,
    FROZEN_MK001_RECORDS,
    FROZEN_PT001_MODEL_RECORDS,
    FROZEN_SN001_MODEL_RECORDS,
    FROZEN_VM001_RECORD,
    FROZEN_VS001_RECORD,
    PRE_VP001_REVISION,
    PT001_MEMBERSHIP,
    VP001_MEMBERSHIP,
)
from tests.model_kernel.test_demo_pt001 import (
    ARTIFACT_BYTES as PT_ARTIFACT_BYTES,
    ARTIFACT_SHA256 as PT_ARTIFACT_SHA256,
    _artifact_bytes as pt_artifact_bytes,
)
from tests.model_kernel.test_demo_vp001 import (
    AUTHORITY,
    CONTEXT,
    DISCLAIMER,
    EXTRUDER_PORT,
    HOTEND_VARIABLE,
    VPA_FILE_BYTES,
    VPA_FILE_SHA256,
    VPA_ID,
    WARNINGS,
)
from tests.model_state.helpers import PROP_TEMP, SUBJECT, full_timeline_stack
from tests.model_state.test_demo_join import (
    AS_OF,
    EXTRUDER,
    LATEST_ATTEMPT_ID,
    LATEST_CHECKSUM,
    LATEST_OBSERVATION_ID,
    LATEST_OCCURRENCE_ID,
    LATEST_RAW_RECORD_ID,
    LATEST_RECEIVED_AT,
    LATEST_VALUE,
)


BINDING_ROOT = Path("bindings/demo-printer")
BINDING_REVISION = (
    "rev_67af9095cb5a75fc9022b7666a9a68d1eed48f03750f8e26759b745240e60b93"
)
ARTIFACT_BYTES = 13951
ARTIFACT_SHA256 = (
    "601210171a6080802d034b9c6b796c8d88e76a681464a99bc233828eb12b784d"
)


def _canonical_json_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def _queries(tmp_path, *, membership=VP001_MEMBERSHIP,
             model_root=DEMO_MODEL):
    model = ModelStore(model_root).replay(membership)
    resolver = BindingResolver(BindingStore(BINDING_ROOT).load())
    temporal = full_timeline_stack(tmp_path)
    return model, resolver, temporal, ModelStateQueries(
        model, resolver, temporal)


def _composed(queries, *, context=CONTEXT):
    return queries.associated_port_variable_state(
        HOTEND_VARIABLE, EXTRUDER_PORT, context=context, as_of=AS_OF,
        entity_anchor_id=EXTRUDER)


def test_committed_association_and_variable_state_are_direct_equal(tmp_path):
    model, resolver, temporal, queries = _queries(tmp_path)
    result = _composed(queries)
    direct_association = ModelQueries(model).variable_port_association(
        HOTEND_VARIABLE, EXTRUDER_PORT, context=CONTEXT)
    direct_state = queries.variable_state(
        HOTEND_VARIABLE, as_of=AS_OF, entity_anchor_id=EXTRUDER)
    direct_bound = BoundTemporalQueries(
        resolver, temporal).latest_observed(SUBJECT, PROP_TEMP, AS_OF)
    direct_observed = temporal.latest_observed(SUBJECT, PROP_TEMP, AS_OF)

    assert result.status == "associated"
    assert result.association == direct_association
    assert result.variable_state == direct_state
    assert (result.association.conclusion,
            result.association.lineage_summary) == ("asserted", "healthy")
    assert result.association.material.revision.revision_id == CURRENT_REVISION
    assert result.variable_state.model_revision.revision_id == CURRENT_REVISION
    assert result.variable_state.binding_revision.revision_id == BINDING_REVISION
    assert result.as_of == AS_OF

    assert result.variable_state.model_membership == "registered"
    assert result.variable_state.binding_discovery == "declared_candidates"
    assert result.variable_state.observation_availability == "observed"
    assert result.variable_state.selection == "single"
    [candidate] = result.variable_state.candidates
    assert candidate.attachment == "attached"
    assert candidate.bound == direct_bound
    assert candidate.bound.observed == direct_observed
    occurrence = candidate.bound.observed.occurrence
    assert occurrence.value_json == LATEST_VALUE
    assert occurrence.received_at == LATEST_RECEIVED_AT
    assert occurrence.occurrence_id == LATEST_OCCURRENCE_ID
    assert occurrence.attempt_id == LATEST_ATTEMPT_ID
    assert occurrence.observation_id == LATEST_OBSERVATION_ID
    assert occurrence.raw_record_id == LATEST_RAW_RECORD_ID
    assert occurrence.payload_checksum == LATEST_CHECKSUM
    provenance = temporal.provenance(occurrence.occurrence_id)
    assert (provenance.attempt_id, provenance.observation_id,
            provenance.raw_record_id, provenance.payload_checksum) == (
                LATEST_ATTEMPT_ID, LATEST_OBSERVATION_ID,
                LATEST_RAW_RECORD_ID, LATEST_CHECKSUM)


def test_history_and_context_change_association_not_variable_evidence(tmp_path):
    _, _, _, current_queries = _queries(tmp_path / "current")
    current = _composed(current_queries)

    historical_model, _, _, historical_queries = _queries(
        tmp_path / "historical", membership=PT001_MEMBERSHIP)
    historical = _composed(historical_queries)
    historical_direct = historical_queries.variable_state(
        HOTEND_VARIABLE, as_of=AS_OF, entity_anchor_id=EXTRUDER)
    assert historical_model.revision.revision_id == PRE_VP001_REVISION
    assert historical.status == "association_not_declared"
    assert historical.association.conclusion == "not_declared"
    assert historical.association.roots == ()
    assert historical.variable_state == historical_direct
    assert historical.variable_state.candidates[0].attachment == "attached"
    assert historical.variable_state.candidates[0].bound.observed.occurrence \
        .value_json == LATEST_VALUE

    as_built = LifecycleViewContext(
        kind="lifecycle_view", view="as_built")
    other_context = _composed(current_queries, context=as_built)
    assert other_context.status == "association_not_declared"
    assert other_context.association.conclusion == "not_declared"
    assert other_context.variable_state == current.variable_state
    assert other_context.variable_state.candidates[0].bound.observed == \
        current.variable_state.candidates[0].bound.observed


def _artifact_bytes(tmp_path, *, model_root=DEMO_MODEL):
    store = ModelStore(model_root)
    base = store.replay(PT001_MEMBERSHIP)
    final = store.replay(VP001_MEMBERSHIP)
    model_queries = ModelQueries(final)
    exact = model_queries.variable_port_association(
        HOTEND_VARIABLE, EXTRUDER_PORT, context=CONTEXT)
    by_variable = model_queries.ports_associated_with_variable(
        HOTEND_VARIABLE, context=CONTEXT)
    by_port = model_queries.variables_associated_with_port(
        EXTRUDER_PORT, context=CONTEXT)
    assertion = model_queries.variable_port_assertion(VPA_ID)
    historical = ModelQueries(base).variable_port_association(
        HOTEND_VARIABLE, EXTRUDER_PORT, context=CONTEXT)
    historical_by_variable = ModelQueries(base).ports_associated_with_variable(
        HOTEND_VARIABLE, context=CONTEXT)
    historical_by_port = ModelQueries(base).variables_associated_with_port(
        EXTRUDER_PORT, context=CONTEXT)
    historical_assertion = ModelQueries(base).variable_port_assertion(VPA_ID)

    resolver = BindingResolver(BindingStore(BINDING_ROOT).load())
    temporal = full_timeline_stack(tmp_path)
    state_queries = ModelStateQueries(final, resolver, temporal)
    composed = _composed(state_queries)
    direct_state = state_queries.variable_state(
        HOTEND_VARIABLE, as_of=AS_OF, entity_anchor_id=EXTRUDER)
    direct_association = model_queries.variable_port_association(
        HOTEND_VARIABLE, EXTRUDER_PORT, context=CONTEXT)
    [candidate] = composed.variable_state.candidates
    occurrence = candidate.bound.observed.occurrence
    provenance = temporal.provenance(occurrence.occurrence_id)

    predecessor_hashes = {
        **FROZEN_MK001_RECORDS,
        **FROZEN_VM001_RECORD,
        **FROZEN_VS001_RECORD,
        **FROZEN_SN001_MODEL_RECORDS,
        **FROZEN_ES001_MODEL_RECORDS,
        **FROZEN_CN001_MODEL_RECORDS,
        **FROZEN_PT001_MODEL_RECORDS,
    }
    vpa = final.records[VPA_ID]
    content = {
        "model": {
            "base_revision": base.revision.model_dump(mode="json"),
            "final_revision": final.revision.model_dump(mode="json"),
            "predecessor_sha256": dict(sorted(predecessor_hashes.items())),
            "predecessor_bytes_preserved": all(
                hashlib.sha256(
                    (model_root / "records" / filename).read_bytes()
                ).hexdigest() == digest
                for filename, digest in predecessor_hashes.items()),
            "appended_record": vpa.model_dump(mode="json"),
            "appended_file": {
                "bytes": VPA_FILE_BYTES,
                "sha256": VPA_FILE_SHA256,
            },
        },
        "authority": AUTHORITY.model_dump(mode="json"),
        "context": CONTEXT.model_dump(mode="json"),
        "queries": {
            "exact": {
                "endpoint_status": exact.endpoint_status,
                "owner_alignment": exact.owner_alignment,
                "conclusion": exact.conclusion,
                "lineage_summary": exact.lineage_summary,
                "root_record_ids": [row.root_record.record_id
                                    for row in exact.roots],
            },
            "ports_associated_with_variable": {
                "status": by_variable.status,
                "entries": [{
                    "entry_index": row.entry_index,
                    "port_anchor_id": row.port_anchor_id,
                    "conclusion": row.conclusion,
                    "lineage_summary": row.lineage_summary,
                } for row in by_variable.entries],
            },
            "variables_associated_with_port": {
                "status": by_port.status,
                "entries": [{
                    "entry_index": row.entry_index,
                    "variable_anchor_id": row.variable_anchor_id,
                    "conclusion": row.conclusion,
                    "lineage_summary": row.lineage_summary,
                } for row in by_port.entries],
            },
            "assertion": {
                "record_id": assertion.record_id,
                "lookup_status": assertion.lookup_status,
                "activity": assertion.activity,
                "containing_lineage_health": (
                    assertion.containing_lineage_health),
                "root_record_id": assertion.root_record.record_id,
                "successor_record_ids": [row.record_id
                                         for row in assertion.successors],
                "withdrawal_record_ids": [row.record_id
                                          for row in assertion.withdrawals],
            },
            "historical_28": {
                "endpoint_status": historical.endpoint_status,
                "owner_alignment": historical.owner_alignment,
                "conclusion": historical.conclusion,
                "lineage_summary": historical.lineage_summary,
                "root_count": len(historical.roots),
                "variable_collection_status": historical_by_variable.status,
                "variable_collection_entry_count": len(
                    historical_by_variable.entries),
                "port_collection_status": historical_by_port.status,
                "port_collection_entry_count": len(
                    historical_by_port.entries),
                "assertion_lookup_status": (
                    historical_assertion.lookup_status),
            },
        },
        "provenance_axes": {
            "statement": (
                "Model revision, binding revision, and temporal cutoff are "
                "separate provenance axes; no clock synchronization or "
                "shared validity interval is claimed."),
            "model_revision_id": (
                composed.variable_state.model_revision.revision_id),
            "binding_revision_id": (
                composed.variable_state.binding_revision.revision_id),
            "temporal_cutoff": composed.as_of.isoformat(),
        },
        "state_composition": {
            "observation_attachment_statement": (
                "The observation is attached to the registered variable "
                "only; the port contributes no temporal selector, locator, "
                "value, or occurrence."),
            "status": composed.status,
            "direct_association_equal": composed.association == (
                direct_association),
            "direct_variable_state_equal": composed.variable_state == (
                direct_state),
            "model_revision_id": (
                composed.variable_state.model_revision.revision_id),
            "binding_revision_id": (
                composed.variable_state.binding_revision.revision_id),
            "temporal_cutoff": composed.as_of.isoformat(),
            "candidate_index": 0,
            "attachment": candidate.attachment,
            "source_subject": candidate.subject.model_dump(mode="json"),
            "source_property": candidate.property.model_dump(mode="json"),
            "observed_value_json": occurrence.value_json,
            "occurrence": {
                "occurrence_id": occurrence.occurrence_id,
                "received_at": occurrence.received_at.isoformat(),
                "attempt_id": occurrence.attempt_id,
                "observation_id": occurrence.observation_id,
                "raw_record_id": occurrence.raw_record_id,
                "payload_checksum": occurrence.payload_checksum,
            },
            "provenance": {
                "attempt_id": provenance.attempt_id,
                "observation_id": provenance.observation_id,
                "raw_record_id": provenance.raw_record_id,
                "payload_checksum": provenance.payload_checksum,
            },
        },
    }
    content_bytes = _canonical_json_bytes(content)
    return _canonical_json_bytes({
        "artifact": "VP-001 demo-printer variable-to-port disclosure",
        "schema_version": "1",
        "disclaimer": DISCLAIMER,
        "warnings": list(WARNINGS),
        "artifact_checksum": {
            "algorithm": "sha256",
            "scope": "content",
            "value": hashlib.sha256(content_bytes).hexdigest(),
        },
        "content": content,
    })


def test_disclosure_artifact_is_deterministic_complete_and_path_free(tmp_path):
    first = _artifact_bytes(tmp_path / "first")
    second = _artifact_bytes(tmp_path / "second")
    assert first == second
    assert len(first) == ARTIFACT_BYTES
    assert hashlib.sha256(first).hexdigest() == ARTIFACT_SHA256
    payload = json.loads(first)
    assert payload["disclaimer"] == DISCLAIMER
    assert payload["warnings"] == list(WARNINGS)
    content_bytes = _canonical_json_bytes(payload["content"])
    assert payload["artifact_checksum"] == {
        "algorithm": "sha256",
        "scope": "content",
        "value": hashlib.sha256(content_bytes).hexdigest(),
    }
    assert payload["content"]["model"]["base_revision"][
        "revision_id"] == PRE_VP001_REVISION
    assert payload["content"]["model"]["final_revision"][
        "revision_id"] == CURRENT_REVISION
    assert len(payload["content"]["model"]["predecessor_sha256"]) == 28
    assert payload["content"]["model"]["predecessor_bytes_preserved"] is True
    assert payload["content"]["queries"]["exact"]["conclusion"] == "asserted"
    assert payload["content"]["queries"]["historical_28"][
        "conclusion"] == "not_declared"
    assert payload["content"]["queries"]["historical_28"][
        "variable_collection_entry_count"] == 0
    assert payload["content"]["queries"]["historical_28"][
        "port_collection_entry_count"] == 0
    assert payload["content"]["queries"]["historical_28"][
        "assertion_lookup_status"] == "not_found"
    assert "separate provenance axes" in payload["content"][
        "provenance_axes"]["statement"]
    assert "attached to the registered variable only" in payload[
        "content"]["state_composition"][
            "observation_attachment_statement"]
    assert payload["content"]["state_composition"]["status"] == "associated"
    assert payload["content"]["state_composition"][
        "observed_value_json"] == LATEST_VALUE
    assert first.count(b'"record_kind":"variable_port_association"') == 1
    for needle in (b"/mnt/", b"/home/", b"C:\\\\"):
        assert needle not in first

    # PT remains a separately generated artifact over explicit PT membership.
    pt = pt_artifact_bytes()
    assert len(pt) == PT_ARTIFACT_BYTES
    assert hashlib.sha256(pt).hexdigest() == PT_ARTIFACT_SHA256
