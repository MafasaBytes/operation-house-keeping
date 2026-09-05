"""EA-001 Slice B captured-view selection acceptance tests."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta

import pytest

from backend.data_sources.contracts import (
    OperationalApiInventoryToken,
    OperationalEvidenceReadError,
)
from backend.data_sources.evidence import FilesystemDs004OperationalEvidenceReader
from backend.evidence_assurance import (
    EvidenceAssuranceQueries,
    EvidenceAssuranceQueryError,
    OperationalEvidenceSelectionPolicy,
    OperationalEvidenceSelectionRequest,
)
from backend.temporal_state.projector import TemporalProjector
from backend.temporal_state.queries import TemporalQueries
from backend.temporal_state.store import TemporalStore

from tests.data_sources.test_http_api_connector import ok_json
from tests.data_sources.test_ingestion_runner_api import happy_script, make_runner
from tests.data_sources.test_ea001_operational_evidence_reader import _scope


HORIZON = datetime(2026, 8, 7, 19, 0, tzinfo=UTC)
AS_OF = datetime(2026, 8, 7, 21, 0, tzinfo=UTC)


def _policy():
    return OperationalEvidenceSelectionPolicy(
        kind="independent_latest_at_or_before_as_of",
        version="ea001.operational_selection.v1",
        occurrence_axis="received_at",
        attempt_coverage_axis="effective_wall_time",
        source_time_use="disclosure_only",
    )


def _request(*, scope=None, start=HORIZON, end=AS_OF):
    return OperationalEvidenceSelectionRequest(
        schema_version="1", scope=scope or _scope(),
        horizon_started_at=start, as_of=end, policy=_policy(),
    )


def _world(tmp_path, script=None):
    runner, raw, transport = make_runner(tmp_path / "source", script or happy_script())
    temporal_store = TemporalStore(
        tmp_path / "temporal.db", evidence_root=raw.base_dir)
    projector = TemporalProjector(raw, temporal_store)
    source = FilesystemDs004OperationalEvidenceReader(raw)
    temporal = TemporalQueries(temporal_store)
    return runner, raw, transport, projector, source, temporal


def _captured_world(tmp_path, script=None):
    runner, raw, transport, projector, source, temporal = _world(tmp_path, script)
    runner.run("printer-1")
    projector.project("printer-1")
    return raw, transport, source, temporal


def _changed_source_token(token):
    keys = tuple(sorted((*token.ordered_member_keys, "raw_payload:synthetic:1:x:-")))
    encoded = json.dumps(
        list(keys), ensure_ascii=False, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return OperationalApiInventoryToken(
        **token.model_dump(
            mode="python",
            exclude={"ordered_member_keys", "canonical_membership_sha256"},
        ),
        ordered_member_keys=keys,
        canonical_membership_sha256="sha256:" + hashlib.sha256(encoded).hexdigest(),
    )


class _SourceProbe:
    def __init__(self, wrapped, log, *, mutate_final=False, fake_all=False,
                 read_error=None):
        self.wrapped = wrapped
        self.log = log
        self.mutate_final = mutate_final
        self.fake_all = fake_all
        self.read_error = read_error
        self.inventory_calls = 0

    def inventory_token(self, *args, **kwargs):
        self.log.append("source_inventory")
        self.inventory_calls += 1
        token = self.wrapped.inventory_token(*args, **kwargs)
        if self.fake_all or (self.mutate_final and self.inventory_calls == 2):
            return _changed_source_token(token)
        return token

    def read_material(self, *args, **kwargs):
        self.log.append("source_material")
        if self.read_error is not None:
            raise self.read_error
        return self.wrapped.read_material(*args, **kwargs)

    def reread_named_material(self, expected_material):
        return self.wrapped.reread_named_material(expected_material)


class _TemporalProbe:
    def __init__(self, wrapped, log, *, mutate_final=False):
        self.wrapped = wrapped
        self.log = log
        self.mutate_final = mutate_final
        self.inventory_calls = 0

    def selection_inventory_token(self, *args, **kwargs):
        self.log.append("temporal_inventory")
        self.inventory_calls += 1
        token = self.wrapped.selection_inventory_token(*args, **kwargs)
        if self.mutate_final and self.inventory_calls == 2:
            return token.model_copy(update={
                "occurrence_membership_sha256": "sha256:" + "0" * 64})
        return token

    def selection_material(self, *args, **kwargs):
        self.log.append("temporal_material")
        return self.wrapped.selection_material(*args, **kwargs)


def test_complete_capture_protocol_routes_age_and_assurance(tmp_path):
    _, _, source, temporal = _captured_world(tmp_path)
    log = []
    result = EvidenceAssuranceQueries(
        source=_SourceProbe(source, log), temporal=_TemporalProbe(temporal, log),
    ).select_operational_evidence(_request())

    assert log == [
        "source_inventory", "temporal_inventory", "temporal_material",
        "source_material", "source_inventory", "temporal_inventory",
    ]
    assert result.status == "complete_within_declared_horizon"
    assert result.issues == ()
    snapshot = result.snapshot
    assert snapshot is not None
    assert snapshot.fixed_limits.maximum_in_horizon_attempts == 4096
    assert len(snapshot.provenance_routes) == 1
    route = snapshot.provenance_routes[0]
    assert route.coverage_disposition == "property_observed"
    assert route.attempt_index == route.temporal_attempt_index == 0
    assert route.envelope_index == route.extraction_index == 0
    assert route.observation_index == route.temporal_occurrence_index == 0
    assert snapshot.coverage.property_observed_route_indices == (0,)
    assert snapshot.coverage.completeness == result.status
    assert snapshot.selected.outcome == "selected_source_observation"
    occurrence = snapshot.temporal_material.occurrence_membership[
        snapshot.selected.temporal_occurrence_index]
    assert snapshot.selected.selected_received_at == occurrence.received_at
    assert snapshot.selected.observation_age_seconds == str(
        int((AS_OF - occurrence.received_at).total_seconds()))
    assert snapshot.selected.age_basis == "received_at"
    assert snapshot.assurance.payload_byte_check == "matched"
    assert snapshot.assurance.observation_content_relation == "exact_value_and_type"
    assert snapshot.assurance.semantic_compatibility == "not_assessed"
    assert snapshot.assurance.accountable_occurrence == "not_assessed"
    assert snapshot.content_fingerprint.startswith("sha256:")


def test_no_observation_and_no_attempt_retains_both_incomplete_issues(tmp_path):
    _, _, source, temporal = _captured_world(tmp_path)
    early = datetime(2020, 1, 1, tzinfo=UTC)
    result = EvidenceAssuranceQueries(
        source=source, temporal=temporal,
    ).select_operational_evidence(_request(
        start=early - timedelta(hours=1), end=early))
    assert result.status == "incomplete_within_declared_horizon"
    assert result.issues == ()
    assert result.snapshot is not None
    assert tuple(issue.code for issue in result.snapshot.issues) == (
        "no_observation_at_or_before_as_of",
        "incomplete_coverage_within_declared_horizon",
    )
    assert result.snapshot.provenance_routes == ()
    assert result.snapshot.selected.outcome == "no_observation_at_or_before_as_of"


@pytest.mark.parametrize(
    ("scope_update", "script_update", "disposition"),
    [
        ({"subject_identifier": "not-present"}, None, "snapshot_without_property"),
        ({}, {"/printer/objects/query": ok_json({
            "result": {"eventtime": 1, "status": {}}})}, "empty_snapshot"),
    ],
)
def test_nonobserving_snapshot_dispositions(
    tmp_path, scope_update, script_update, disposition,
):
    script = happy_script()
    if script_update:
        script.update(script_update)
    _, _, source, temporal = _captured_world(tmp_path, script)
    result = EvidenceAssuranceQueries(
        source=source, temporal=temporal,
    ).select_operational_evidence(_request(scope=_scope(**scope_update)))
    assert result.status == "incomplete_within_declared_horizon"
    assert result.snapshot.provenance_routes[0].coverage_disposition == disposition
    assert tuple(issue.code for issue in result.snapshot.issues) == (
        "no_observation_at_or_before_as_of",
        "incomplete_coverage_within_declared_horizon",
    )


def test_pre_horizon_seed_is_selected_but_not_attempt_coverage(tmp_path):
    _, _, source, temporal = _captured_world(tmp_path)
    material = temporal.selection_material(
        _scope(), horizon_started_at=HORIZON, as_of=AS_OF)
    occurrence = material.occurrence_membership[material.selected_occurrence_index]
    start = occurrence.received_at + timedelta(minutes=1)
    result = EvidenceAssuranceQueries(
        source=source, temporal=temporal,
    ).select_operational_evidence(_request(start=start, end=start + timedelta(minutes=1)))
    assert result.status == "incomplete_within_declared_horizon"
    snapshot = result.snapshot
    assert snapshot.selected.pre_horizon_seed is True
    assert snapshot.temporal_material.attempt_coverage_membership == ()
    assert snapshot.coverage.attempt_route_indices == ()
    assert tuple(issue.code for issue in snapshot.issues) == (
        "incomplete_coverage_within_declared_horizon",
    )


def test_source_and_temporal_final_fence_changes_are_both_retained(tmp_path):
    _, _, source, temporal = _captured_world(tmp_path)
    log = []
    result = EvidenceAssuranceQueries(
        source=_SourceProbe(source, log, mutate_final=True),
        temporal=_TemporalProbe(temporal, log, mutate_final=True),
    ).select_operational_evidence(_request())
    assert result.status == "refused"
    assert result.snapshot is None
    assert tuple(issue.code for issue in result.issues) == (
        "source_store_changed_during_capture",
        "temporal_store_changed_during_capture",
    )
    assert all(issue.route_index is None for issue in result.issues)


def test_material_token_disagreement_refuses(tmp_path):
    _, _, source, temporal = _captured_world(tmp_path)
    result = EvidenceAssuranceQueries(
        source=_SourceProbe(source, [], fake_all=True), temporal=temporal,
    ).select_operational_evidence(_request())
    assert result.status == "refused"
    assert tuple(issue.code for issue in result.issues) == (
        "source_store_changed_during_capture",
    )


def test_seed_parity_lower_refusal_maps_to_structured_parity_issue(tmp_path):
    _, _, source, temporal = _captured_world(tmp_path)
    result = EvidenceAssuranceQueries(
        source=_SourceProbe(
            source, [], read_error=OperationalEvidenceReadError(
                "OPERATIONAL_EVIDENCE_SEED_PARITY_MISMATCH",
                "source-selected and supplied seed IDs differ")),
        temporal=temporal,
    ).select_operational_evidence(_request())
    assert result.status == "refused"
    assert tuple(issue.code for issue in result.issues) == (
        "source_temporal_parity_failure",
    )


def test_request_and_policy_misuse_fail_before_any_io():
    class NeverIo:
        def inventory_token(self, *args, **kwargs):
            raise AssertionError("I/O occurred")
        def read_material(self, *args, **kwargs):
            raise AssertionError("I/O occurred")
        def reread_named_material(self, *args, **kwargs):
            raise AssertionError("I/O occurred")
        def selection_inventory_token(self, *args, **kwargs):
            raise AssertionError("I/O occurred")
        def selection_material(self, *args, **kwargs):
            raise AssertionError("I/O occurred")

    queries = EvidenceAssuranceQueries(source=NeverIo(), temporal=NeverIo())
    payload = _request().model_dump(mode="python")
    payload["unexpected"] = "field"
    with pytest.raises(EvidenceAssuranceQueryError) as error:
        queries.select_operational_evidence(payload)
    assert error.value.error_code == "EA_REQUEST_INVALID"

    payload = _request().model_dump(mode="python")
    payload["policy"]["source_time_use"] = "selection"
    with pytest.raises(EvidenceAssuranceQueryError) as error:
        queries.select_operational_evidence(payload)
    assert error.value.error_code == "EA_SELECTION_POLICY_INVALID"
