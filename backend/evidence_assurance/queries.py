"""EA-001 read-only composition facade and store-independent validator."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import UTC, datetime
from typing import get_args

from pydantic import BaseModel

from backend.data_sources.contracts import (
    Ds004OperationalEvidenceMaterial,
    OperationalApiInventoryToken,
)
from backend.evidence_assurance.contracts import (
    FIXED_LIMITS,
    CapturedOperationalEvidenceSnapshot,
    CapturedViewFence,
    CoverageDisposition,
    EvidenceAssuranceConfigurationError,
    EvidenceAssuranceQueryError,
    OperationalCoverageSummary,
    OperationalEvidenceAssurance,
    OperationalEvidenceIssue,
    OperationalEvidenceSelectionPolicy,
    OperationalEvidenceSelectionRequest,
    OperationalEvidenceSelectionResult,
    OperationalProvenanceRoute,
    SelectedSourceObservation,
    _deep_plain,
    _ordered_issues,
)
from backend.temporal_state.contracts import (
    TemporalSelectionInventoryToken,
    TemporalSelectionMaterial,
    temporal_selection_digest,
)


class _DerivationError(Exception):
    def __init__(self, code: str, detail_code: str, detail: str) -> None:
        self.code = code
        self.detail_code = detail_code
        self.detail = detail


def _issue(code: str, detail_code: str, detail: str) -> OperationalEvidenceIssue:
    return OperationalEvidenceIssue(
        code=code, detail_code=detail_code, route_index=None, detail=detail)


def _append_issue(target: list[OperationalEvidenceIssue], issue) -> None:
    identity = (issue.code, issue.route_index, issue.detail_code)
    if all((row.code, row.route_index, row.detail_code) != identity for row in target):
        target.append(issue)


def _source_error_issue(error: BaseException) -> OperationalEvidenceIssue:
    code = getattr(error, "error_code", "")
    if code == "OPERATIONAL_EVIDENCE_UNSUPPORTED_ROUTE":
        return _issue(
            "unsupported_operational_evidence", "source_route_unsupported",
            "the requested operational evidence route is not supported")
    if code == "OPERATIONAL_EVIDENCE_LIMIT_EXCEEDED":
        return _issue(
            "excessive_bounded_material", "source_material_limit_exceeded",
            "source evidence exceeds the fixed bounded-material limits")
    if code in {
        "OPERATIONAL_EVIDENCE_UNAVAILABLE",
        "OPERATIONAL_EVIDENCE_NAMED_MATERIAL_UNAVAILABLE",
    }:
        return _issue(
            "source_evidence_unavailable", "source_material_unavailable",
            "source operational evidence is unavailable")
    if code == "OPERATIONAL_EVIDENCE_CHECKSUM_MISMATCH":
        return _issue(
            "checksum_mismatch", "source_payload_checksum_mismatch",
            "captured payload bytes do not match the stored checksum")
    if code == "OPERATIONAL_EVIDENCE_PROVENANCE_MISMATCH":
        return _issue(
            "provenance_closure_failure", "source_provenance_not_closed",
            "captured source provenance does not close")
    if code in {
        "OPERATIONAL_EVIDENCE_OBSERVATION_MISMATCH",
        "OPERATIONAL_EVIDENCE_PAYLOAD_INVALID",
    }:
        return _issue(
            "observation_content_mismatch", "source_observation_content_mismatch",
            "captured observation content does not match its raw evidence")
    if code == "OPERATIONAL_EVIDENCE_EXTRACTION_INCOMPLETE":
        return _issue(
            "extraction_incomplete", "source_extraction_incomplete",
            "required captured extraction material is incomplete")
    if code == "OPERATIONAL_EVIDENCE_SEED_PARITY_MISMATCH":
        return _issue(
            "source_temporal_parity_failure", "pre_horizon_seed_id_mismatch",
            "source and temporal pre-horizon seed attempts differ")
    return _issue(
        "invalid_bounded_material", "source_material_invalid",
        "source operational evidence is invalid")


def _temporal_error_issue(error: BaseException) -> OperationalEvidenceIssue:
    code = getattr(error, "error_code", "")
    if code == "TEMPORAL_SELECTION_LIMIT_EXCEEDED":
        return _issue(
            "excessive_bounded_material", "temporal_material_limit_exceeded",
            "temporal evidence exceeds the fixed bounded-material limits")
    if code in {"TEMPORAL_STORE_UNAVAILABLE", "TEMPORAL_SELECTION_UNAVAILABLE"}:
        return _issue(
            "temporal_evidence_unavailable", "temporal_material_unavailable",
            "temporal operational evidence is unavailable")
    return _issue(
        "invalid_bounded_material", "temporal_material_invalid",
        "temporal operational evidence is invalid")


def _strict_request(value) -> OperationalEvidenceSelectionRequest:
    try:
        plain = _deep_plain(value)
    except Exception as error:
        raise EvidenceAssuranceQueryError(
            "EA_REQUEST_INVALID", "selection request is invalid") from error
    if isinstance(plain, dict) and "policy" in plain:
        try:
            OperationalEvidenceSelectionPolicy.model_validate(plain["policy"])
        except Exception as error:
            raise EvidenceAssuranceQueryError(
                "EA_SELECTION_POLICY_INVALID",
                "selection policy is invalid") from error
    try:
        return OperationalEvidenceSelectionRequest.model_validate(plain)
    except Exception as error:
        raise EvidenceAssuranceQueryError(
            "EA_REQUEST_INVALID", "selection request is invalid") from error


def _source_token_from_material(request, material):
    keys = tuple(sorted(
        f"{item.kind}:{item.logical_id}:{item.byte_count}:"
        f"{item.captured_file_sha256}:{item.payload_checksum or '-'}"
        for item in material.artifacts
    ))
    return OperationalApiInventoryToken(
        schema_version="1", scope=request.scope,
        horizon_started_at=request.horizon_started_at, as_of=request.as_of,
        ordered_member_keys=keys,
        canonical_membership_sha256="sha256:" + hashlib.sha256(json.dumps(
            list(keys), ensure_ascii=False, separators=(",", ":"),
            allow_nan=False).encode("utf-8")).hexdigest(),
    )


def _temporal_token_from_material(material):
    return TemporalSelectionInventoryToken(
        schema_version=material.schema_version,
        projector_version=material.projector_version,
        scope=material.scope,
        horizon_started_at=material.horizon_started_at,
        as_of=material.as_of,
        occurrence_membership_sha256=temporal_selection_digest(
            material.occurrence_membership),
        attempt_coverage_membership_sha256=temporal_selection_digest(
            material.attempt_coverage_membership),
        clock_opening_membership_sha256=temporal_selection_digest(
            material.clock_segment_openings),
    )


def _attempt_order(row):
    started = getattr(row, "started_at", None) or row.attempt_started_at
    return (
        started.astimezone(UTC), row.ingestion_run_id,
        row.sweep_position, row.attempt_id,
    )


def _canonical_age(start: datetime, end: datetime) -> str:
    delta = end.astimezone(UTC) - start.astimezone(UTC)
    microseconds = (
        (delta.days * 86_400 + delta.seconds) * 1_000_000
        + delta.microseconds
    )
    if microseconds < 0:
        raise _DerivationError(
            "temporal_occurrence_inconsistent", "negative_observation_age",
            "selected occurrence is later than the explicit cutoff")
    whole, fraction = divmod(microseconds, 1_000_000)
    if not fraction:
        return str(whole)
    return f"{whole}.{fraction:06d}".rstrip("0")


def _source_attempt_outcome(material, attempt):
    if attempt.outcome == "failed":
        return "acquisition_failed", attempt.failure.error_code, 0, 0
    quarantine = next(
        (row for row in material.quarantines
         if row.record_id == attempt.raw_record_id), None)
    if quarantine is not None:
        return "quarantined", quarantine.error_code, 0, 0
    extraction = next(
        (row for row in material.extractions
         if row.raw_record_id == attempt.raw_record_id), None)
    if extraction is None:
        return "extraction_incomplete", None, 0, 0
    manifest = extraction.result.manifest
    exact = [
        row for row in material.observations
        if row.raw_record_id == attempt.raw_record_id
    ]
    if exact:
        disposition = "property_observed"
    elif manifest.observations:
        disposition = "snapshot_without_property"
    else:
        disposition = "empty_snapshot"
    return disposition, None, len(manifest.observations), len(manifest.warnings)


def _validate_temporal_event(source_attempt, temporal_event, material):
    disposition, failure_code, observation_count, warning_count = (
        _source_attempt_outcome(material, source_attempt))
    expected_outcome = {
        "property_observed": "observations_projected",
        "snapshot_without_property": "observations_projected",
        "empty_snapshot": "observations_projected",
        "acquisition_failed": "acquisition_failed",
        "quarantined": "quarantined",
        "extraction_incomplete": None,
    }[disposition]
    expected_effective = source_attempt.received_at or source_attempt.finished_at
    expected_basis = (
        "received_at" if source_attempt.received_at is not None
        else "finished_at_no_response")
    equal = (
        temporal_event.source_id == source_attempt.source_id
        and temporal_event.adapter_id == source_attempt.adapter_id
        and temporal_event.endpoint_id == source_attempt.endpoint_id
        and temporal_event.item_key == source_attempt.item_key
        and temporal_event.sweep_position == source_attempt.sweep_position
        and temporal_event.ingestion_run_id == source_attempt.ingestion_run_id
        and temporal_event.attempt_started_at == source_attempt.started_at
        and temporal_event.received_at == source_attempt.received_at
        and temporal_event.finished_at == source_attempt.finished_at
        and temporal_event.effective_wall_time == expected_effective
        and temporal_event.effective_time_basis == expected_basis
        and temporal_event.outcome == expected_outcome
        and temporal_event.raw_record_id == source_attempt.raw_record_id
        and temporal_event.payload_checksum == source_attempt.payload_checksum
        and temporal_event.observation_count == observation_count
        and temporal_event.failure_or_quarantine_code == failure_code
        and temporal_event.source_warning_count == warning_count
    )
    if not equal:
        raise _DerivationError(
            "source_temporal_parity_failure", "attempt_content_parity_failure",
            "source and temporal attempt content differ")


def _validate_occurrence(source_attempt, source_observation, occurrence):
    if not (
        occurrence.attempt_id == source_attempt.attempt_id
        and occurrence.observation_id == source_observation.observation_id
        and occurrence.raw_record_id == source_attempt.raw_record_id
        and occurrence.payload_checksum == source_attempt.payload_checksum
        and occurrence.attempt_started_at == source_attempt.started_at
        and occurrence.ingestion_run_id == source_attempt.ingestion_run_id
        and occurrence.sweep_position == source_attempt.sweep_position
        and occurrence.received_at == source_attempt.received_at
        and occurrence.finished_at == source_attempt.finished_at
        and occurrence.source_time == source_observation.source_time
        and occurrence.value_json == source_observation.value_json
        and occurrence.json_type == source_observation.json_type
        and occurrence.declared_unit == source_observation.declared_unit
        and set(source_observation.quality_flags) <= set(occurrence.quality_flags)
    ):
        raise _DerivationError(
            "source_temporal_parity_failure",
            "observation_content_parity_failure",
            "source and temporal observation content differ")


def _derive_routes_and_selection(request, source, temporal):
    if source.scope != request.scope or temporal.scope != request.scope:
        raise _DerivationError(
            "source_temporal_parity_failure", "material_scope_parity_failure",
            "captured material does not share the exact request scope")
    if (
        temporal.horizon_started_at != request.horizon_started_at
        or temporal.as_of != request.as_of
    ):
        raise _DerivationError(
            "temporal_occurrence_inconsistent", "temporal_interval_mismatch",
            "temporal material does not match the requested interval")

    source_attempts = {row.attempt_id: row for row in source.attempts}
    temporal_attempts = {
        row.attempt_id: row for row in temporal.attempt_coverage_membership}
    start, end = request.horizon_started_at, request.as_of
    source_in_horizon = {
        row.attempt_id for row in source.attempts
        if start <= (row.received_at or row.finished_at).astimezone(UTC) <= end
    }
    if source_in_horizon != set(temporal_attempts):
        raise _DerivationError(
            "source_temporal_parity_failure", "attempt_membership_parity_failure",
            "source and temporal attempt memberships differ")

    selected_occurrence = (
        temporal.occurrence_membership[temporal.selected_occurrence_index]
        if temporal.selected_occurrence_index is not None else None)
    seed_id = (
        selected_occurrence.attempt_id
        if temporal.selected_occurrence_is_pre_horizon_seed else None)
    allowed_source_ids = set(temporal_attempts)
    if seed_id is not None:
        allowed_source_ids.add(seed_id)
    if set(source_attempts) != allowed_source_ids:
        raise _DerivationError(
            "source_temporal_parity_failure", "retained_attempt_parity_failure",
            "source retained attempts do not match temporal membership and seed")

    source_observations = {
        (row.raw_record_id, row.observation_id): row
        for row in source.observations
    }
    occurrence_by_attempt = {}
    for index, occurrence in enumerate(temporal.occurrence_membership):
        if occurrence.attempt_id in occurrence_by_attempt:
            raise _DerivationError(
                "temporal_occurrence_inconsistent",
                "duplicate_property_occurrence_for_attempt",
                "one attempt carries duplicate exact-property occurrences")
        occurrence_by_attempt[occurrence.attempt_id] = (index, occurrence)
        source_attempt = source_attempts.get(occurrence.attempt_id)
        observation = source_observations.get(
            (occurrence.raw_record_id, occurrence.observation_id))
        if source_attempt is None or observation is None:
            raise _DerivationError(
                "temporal_occurrence_absent", "source_occurrence_not_closed",
                "temporal occurrence has no matching captured source observation")
        _validate_occurrence(source_attempt, observation, occurrence)

    expected_occurrence_attempts = {
        row.attempt_id for row in source.attempts
        if row.outcome == "succeeded"
        and any(obs.raw_record_id == row.raw_record_id
                for obs in source.observations)
        and row.received_at <= end
    }
    if set(occurrence_by_attempt) != expected_occurrence_attempts:
        raise _DerivationError(
            "source_temporal_parity_failure",
            "observation_membership_parity_failure",
            "source and temporal observation memberships differ")

    run_indices = {row.run_id: index for index, row in enumerate(source.runs)}
    envelope_indices = {
        row.record_id: index for index, row in enumerate(source.envelopes)}
    extraction_indices = {
        row.raw_record_id: index for index, row in enumerate(source.extractions)}
    quarantine_indices = {
        row.record_id: index for index, row in enumerate(source.quarantines)}
    observation_indices = {
        (row.raw_record_id, row.observation_id): index
        for index, row in enumerate(source.observations)
    }
    artifact_indices = {
        (row.kind, row.logical_id): index
        for index, row in enumerate(source.artifacts)
    }

    routes = []
    route_by_attempt = {}
    ordered_events = tuple(sorted(
        temporal.attempt_coverage_membership, key=_attempt_order))
    if ordered_events != temporal.attempt_coverage_membership:
        raise _DerivationError(
            "temporal_occurrence_inconsistent", "attempt_order_inconsistent",
            "temporal attempt membership is not in complete attempt order")
    for temporal_index, event in enumerate(ordered_events):
        attempt = source_attempts[event.attempt_id]
        _validate_temporal_event(attempt, event, source)
        disposition, _, _, _ = _source_attempt_outcome(source, attempt)
        if disposition == "extraction_incomplete":
            raise _DerivationError(
                "extraction_incomplete", "source_extraction_incomplete",
                "required captured extraction material is incomplete")
        source_index = source.attempts.index(attempt)
        envelope_index = (
            envelope_indices.get(attempt.raw_record_id)
            if attempt.raw_record_id is not None else None)
        extraction_index = (
            extraction_indices.get(attempt.raw_record_id)
            if attempt.raw_record_id is not None else None)
        quarantine_index = (
            quarantine_indices.get(attempt.raw_record_id)
            if attempt.raw_record_id is not None else None)
        occurrence_entry = occurrence_by_attempt.get(attempt.attempt_id)
        occurrence_index = occurrence_entry[0] if occurrence_entry else None
        observation_index = None
        if occurrence_entry:
            occurrence = occurrence_entry[1]
            observation_index = observation_indices[
                (occurrence.raw_record_id, occurrence.observation_id)]

        descriptor_keys = {
            ("acquisition_attempt", attempt.attempt_id),
            ("ingestion_run", attempt.ingestion_run_id),
        }
        if attempt.raw_record_id is not None:
            envelope = source.envelopes[envelope_index]
            descriptor_keys.update({
                ("raw_envelope", attempt.raw_record_id),
                ("raw_payload", attempt.payload_checksum),
                ("ingestion_run", envelope.ingestion_run_id),
            })
            if extraction_index is not None:
                descriptor_keys.add(("extraction_result", attempt.raw_record_id))
            if quarantine_index is not None:
                descriptor_keys.add(("quarantine_record", attempt.raw_record_id))
        try:
            descriptor_indices = tuple(sorted(
                artifact_indices[key] for key in descriptor_keys))
        except KeyError as error:
            raise _DerivationError(
                "provenance_closure_failure", "artifact_descriptor_absent",
                "required source artifact descriptor is absent") from error
        route = OperationalProvenanceRoute(
            attempt_index=source_index,
            run_index=run_indices[attempt.ingestion_run_id],
            temporal_attempt_index=temporal_index,
            envelope_index=envelope_index,
            payload_artifact_index=(
                artifact_indices.get(("raw_payload", attempt.payload_checksum))
                if attempt.payload_checksum is not None else None),
            extraction_index=extraction_index,
            quarantine_index=quarantine_index,
            observation_index=observation_index,
            temporal_occurrence_index=occurrence_index,
            artifact_descriptor_indices=descriptor_indices,
            coverage_disposition=disposition,
        )
        route_by_attempt[attempt.attempt_id] = len(routes)
        routes.append(route)

    if selected_occurrence is None:
        selected = SelectedSourceObservation(
            outcome="no_observation_at_or_before_as_of",
            temporal_occurrence_index=None, provenance_route_index=None,
            pre_horizon_seed=False, selected_received_at=None,
            observation_age_seconds=None, age_basis="not_applicable")
    else:
        selected = SelectedSourceObservation(
            outcome="selected_source_observation",
            temporal_occurrence_index=temporal.selected_occurrence_index,
            provenance_route_index=route_by_attempt.get(selected_occurrence.attempt_id),
            pre_horizon_seed=temporal.selected_occurrence_is_pre_horizon_seed,
            selected_received_at=selected_occurrence.received_at,
            observation_age_seconds=_canonical_age(
                selected_occurrence.received_at, request.as_of),
            age_basis="received_at")

    route_indices = tuple(range(len(routes)))
    by_disposition = {
        disposition: tuple(
            index for index, route in enumerate(routes)
            if route.coverage_disposition == disposition)
        for disposition in get_args(CoverageDisposition)
    }
    complete = bool(
        routes and selected_occurrence is not None
        and len(by_disposition["property_observed"]) == len(routes))
    completeness = (
        "complete_within_declared_horizon"
        if complete else "incomplete_within_declared_horizon")
    coverage = OperationalCoverageSummary(
        attempt_route_indices=route_indices,
        property_observed_route_indices=by_disposition["property_observed"],
        omitted_property_route_indices=by_disposition["snapshot_without_property"],
        empty_snapshot_route_indices=by_disposition["empty_snapshot"],
        failed_route_indices=by_disposition["acquisition_failed"],
        quarantined_route_indices=by_disposition["quarantined"],
        extraction_incomplete_route_indices=by_disposition["extraction_incomplete"],
        completeness=completeness,
    )
    issues = []
    if selected_occurrence is None:
        issues.append(_issue(
            "no_observation_at_or_before_as_of", "no_eligible_observation",
            "no exact-scope observation exists at or before the cutoff"))
    if not complete:
        issues.append(_issue(
            "incomplete_coverage_within_declared_horizon",
            "horizon_coverage_incomplete",
            "the declared horizon is not completely covered by property observations"))
    return tuple(routes), selected, coverage, _ordered_issues(tuple(issues))


def _canonical_value(value):
    if isinstance(value, BaseModel):
        return {
            name: _canonical_value(getattr(value, name))
            for name in value.__class__.model_fields
        }
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat()
    if isinstance(value, (tuple, list)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("canonical object keys must be strings")
        return {key: _canonical_value(item) for key, item in value.items()}
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("canonical numbers must be finite")
        return value
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise ValueError("canonical content contains an unsupported value")


def _canonical_snapshot_bytes(snapshot_without_fingerprint: dict) -> bytes:
    wrapped = {
        "algorithm": "sha256",
        "snapshot": _canonical_value(snapshot_without_fingerprint),
    }
    return json.dumps(
        wrapped, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _fingerprint(snapshot_without_fingerprint: dict) -> str:
    return "sha256:" + hashlib.sha256(
        _canonical_snapshot_bytes(snapshot_without_fingerprint)).hexdigest()


def _build_snapshot(request, source, temporal, initial_source, initial_temporal,
                    final_source, final_temporal):
    routes, selected, coverage, issues = _derive_routes_and_selection(
        request, source, temporal)
    base = {
        "schema_version": "1",
        "request": request,
        "fixed_limits": FIXED_LIMITS,
        "source_material": source,
        "temporal_material": temporal,
        "provenance_routes": routes,
        "selected": selected,
        "coverage": coverage,
        "capture_fence": CapturedViewFence(
            initial_source_token=initial_source,
            initial_temporal_token=initial_temporal,
            final_source_token=final_source,
            final_temporal_token=final_temporal,
            relation="equal_at_observed_fences"),
        "assurance": OperationalEvidenceAssurance(
            payload_byte_check=(
                "matched" if any(row.kind == "raw_payload" for row in source.artifacts)
                else "not_applicable"),
            metadata_same_read_check="matched",
            provenance_closure="closed",
            observation_content_relation=(
                "exact_value_and_type"
                if selected.outcome == "selected_source_observation"
                else "not_applicable"),
            occurrence_membership_relation="reconciled",
            attempt_coverage_membership_relation="reconciled",
            captured_view_relation="equal_at_observed_fences",
            semantic_compatibility="not_assessed",
            accountable_occurrence="not_assessed"),
        "issues": issues,
    }
    return CapturedOperationalEvidenceSnapshot(
        **base, content_fingerprint=_fingerprint(base))


class EvidenceAssuranceQueries:
    def __init__(self, *, source, temporal) -> None:
        source_methods = ("inventory_token", "read_material", "reread_named_material")
        temporal_methods = ("selection_inventory_token", "selection_material")
        if not all(callable(getattr(source, name, None)) for name in source_methods):
            raise EvidenceAssuranceConfigurationError(
                "EA_DEPENDENCY_INVALID", "source dependency is invalid")
        if not all(callable(getattr(temporal, name, None)) for name in temporal_methods):
            raise EvidenceAssuranceConfigurationError(
                "EA_DEPENDENCY_INVALID", "temporal dependency is invalid")
        self._source = source
        self._temporal = temporal

    def select_operational_evidence(self, request):
        request = _strict_request(request)
        call = {
            "scope": request.scope,
            "horizon_started_at": request.horizon_started_at,
            "as_of": request.as_of,
        }
        issues = []
        initial_source = initial_temporal = None
        temporal_material = source_material = None
        final_source = final_temporal = None

        try:
            initial_source = self._source.inventory_token(**call)
        except Exception as error:
            _append_issue(issues, _source_error_issue(error))
        try:
            initial_temporal = self._temporal.selection_inventory_token(**call)
        except Exception as error:
            _append_issue(issues, _temporal_error_issue(error))
        try:
            temporal_material = self._temporal.selection_material(**call)
            temporal_material = TemporalSelectionMaterial.model_validate(
                _deep_plain(temporal_material))
        except Exception as error:
            _append_issue(issues, _temporal_error_issue(error))
        if temporal_material is not None:
            seed_id = None
            if temporal_material.selected_occurrence_is_pre_horizon_seed:
                seed_id = temporal_material.occurrence_membership[
                    temporal_material.selected_occurrence_index].attempt_id
            try:
                source_material = self._source.read_material(
                    **call, selected_seed_attempt_id=seed_id)
                source_material = Ds004OperationalEvidenceMaterial.model_validate(
                    _deep_plain(source_material))
            except Exception as error:
                _append_issue(issues, _source_error_issue(error))
        try:
            final_source = self._source.inventory_token(**call)
        except Exception as error:
            _append_issue(issues, _source_error_issue(error))
        try:
            final_temporal = self._temporal.selection_inventory_token(**call)
        except Exception as error:
            _append_issue(issues, _temporal_error_issue(error))

        if initial_source is not None and final_source is not None:
            if initial_source != final_source:
                _append_issue(issues, _issue(
                    "source_store_changed_during_capture", "source_fence_changed",
                    "source membership changed between observed fences"))
            if source_material is not None:
                derived = _source_token_from_material(request, source_material)
                if derived not in (initial_source, final_source):
                    _append_issue(issues, _issue(
                        "source_store_changed_during_capture",
                        "source_material_fence_disagreement",
                        "captured source material disagrees with observed fences"))
        if initial_temporal is not None and final_temporal is not None:
            if initial_temporal != final_temporal:
                _append_issue(issues, _issue(
                    "temporal_store_changed_during_capture", "temporal_fence_changed",
                    "temporal membership changed between observed fences"))
            if temporal_material is not None:
                derived = _temporal_token_from_material(temporal_material)
                if derived not in (initial_temporal, final_temporal):
                    _append_issue(issues, _issue(
                        "temporal_store_changed_during_capture",
                        "temporal_material_fence_disagreement",
                        "captured temporal material disagrees with observed fences"))

        if source_material is not None and temporal_material is not None:
            try:
                _derive_routes_and_selection(request, source_material, temporal_material)
            except _DerivationError as error:
                _append_issue(issues, _issue(
                    error.code, error.detail_code, error.detail))
            except Exception:
                _append_issue(issues, _issue(
                    "invalid_bounded_material", "derived_material_invalid",
                    "captured bounded material cannot be derived consistently"))

        refusal = [issue for issue in issues if issue.code not in {
            "no_observation_at_or_before_as_of",
            "incomplete_coverage_within_declared_horizon",
        }]
        required = (
            initial_source, initial_temporal, source_material, temporal_material,
            final_source, final_temporal,
        )
        if refusal or any(value is None for value in required):
            if not refusal:
                refusal = [_issue(
                    "invalid_bounded_material", "captured_material_incomplete",
                    "the captured bounded view is incomplete")]
            return OperationalEvidenceSelectionResult(
                status="refused", request=request, snapshot=None,
                issues=_ordered_issues(tuple(refusal)))
        try:
            snapshot = _build_snapshot(
                request, source_material, temporal_material,
                initial_source, initial_temporal, final_source, final_temporal)
        except _DerivationError as error:
            return OperationalEvidenceSelectionResult(
                status="refused", request=request, snapshot=None,
                issues=(_issue(error.code, error.detail_code, error.detail),))
        return OperationalEvidenceSelectionResult(
            status=snapshot.coverage.completeness,
            request=request, snapshot=snapshot, issues=())

    def revalidate_operational_evidence(self, snapshot, *, membership_mode):
        raise NotImplementedError


def validate_operational_evidence_snapshot(snapshot, *, expected_fingerprint=None):
    raise NotImplementedError
