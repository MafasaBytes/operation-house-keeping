"""TS-001 temporal projector.

Reads the immutable data_sources evidence store (attempts, extractions,
quarantines) and projects it into the rebuildable temporal store: one
ledger row per fully-processed attempt, one occurrence per successful
attempt x observation, immutable clock-segment openings, exact change
chains keyed on all six identity dimensions.

Ground truth of processing is the attempt ledger; the checkpoint is an
optimization validated against it. Inconsistency, version mismatch, or a
late attempt behind the watermark halts with TEMPORAL_REBUILD_REQUIRED —
history chains are never rewritten in place and ambiguous state is never
silently repaired. Extraction incompleteness halts the source and
persists nothing.
"""

from datetime import datetime
from decimal import Decimal

from backend.data_sources.contracts import AcquisitionAttempt
from backend.data_sources.provenance import derive_entity_id
from backend.data_sources.raw_store import FilesystemRawStore
from backend.temporal_state.contracts import (
    AttemptOrderKey,
    ClockSegmentOpening,
    HaltInfo,
    ProjectionCheckpoint,
    ProjectionReport,
    SourcePropertyRef,
    SourceSubjectRef,
    TemporalAttemptEvent,
    TemporalOccurrence,
)
from backend.temporal_state.store import (
    PROJECTOR_VERSION,
    SCHEMA_VERSION,
    TemporalStore,
)


class _DeferIncomplete(Exception):
    """Internal control flow only — never escapes the projector's public
    methods."""

    def __init__(self, attempt_id: str) -> None:
        super().__init__(attempt_id)
        self.attempt_id = attempt_id


def order_key_of(attempt: AcquisitionAttempt) -> AttemptOrderKey:
    return AttemptOrderKey(
        attempt_started_at=attempt.started_at,
        ingestion_run_id=attempt.ingestion_run_id,
        sweep_position=attempt.sweep_position,
        attempt_id=attempt.attempt_id,
    )


class TemporalProjector:
    def __init__(
        self,
        evidence: FilesystemRawStore,
        store: TemporalStore,
        projector_version: str = PROJECTOR_VERSION,
    ) -> None:
        self.evidence = evidence
        self.store = store
        self.projector_version = projector_version

    # -- public -----------------------------------------------------------

    def project(self, source_id: str) -> ProjectionReport:
        report = ProjectionReport(source_id=source_id)
        with self.store.writer() as conn:
            watermark = self._validate_state(conn, source_id, report)
            if report.halted:
                return report
            caches = {"mono": {}, "wall": {}, "open_ordinal": {}}
            for attempt in self._ordered_attempts(source_id):
                key = order_key_of(attempt).sort_tuple()
                if watermark is not None and key <= watermark:
                    if not self.store.has_attempt(conn, attempt.attempt_id):
                        report.halted = self._late_attempt_halt(
                            source_id, attempt.attempt_id)
                        return report
                    continue
                try:
                    with self.store.attempt_txn(conn):
                        # Authoritative state lives inside the write
                        # transaction: another projector may have advanced
                        # this source since our pre-loop validation.
                        checkpoint = self.store.load_checkpoint(
                            conn, source_id)
                        ledger_max = self.store.ledger_max_order_key(
                            conn, source_id)
                        checkpoint_key = (checkpoint.order_key().sort_tuple()
                                          if checkpoint is not None else None)
                        if checkpoint_key is not None and (
                                ledger_max is None
                                or tuple(ledger_max) != checkpoint_key):
                            report.halted = HaltInfo(
                                source_id=source_id,
                                reason="TEMPORAL_REBUILD_REQUIRED",
                                detail="checkpoint became inconsistent with "
                                "the attempt ledger inside the write "
                                "transaction",
                            )
                            return report
                        txn_watermark = (tuple(ledger_max)
                                         if ledger_max is not None else None)
                        if self.store.has_attempt(conn, attempt.attempt_id):
                            # Processed concurrently, or we hold a stale
                            # attempt snapshot: never move the checkpoint
                            # back to this attempt's older key — leave the
                            # consistent checkpoint alone, or reconcile a
                            # missing one to the verified ledger maximum.
                            if checkpoint_key is None:
                                self.store.upsert_checkpoint(
                                    conn, self._checkpoint_from_ledger_key(
                                        source_id, ledger_max))
                        elif (txn_watermark is not None
                                and key <= txn_watermark):
                            report.halted = self._late_attempt_halt(
                                source_id, attempt.attempt_id)
                            return report
                        else:
                            self._process_attempt(conn, attempt, report,
                                                  caches)
                            self.store.upsert_checkpoint(
                                conn, self._checkpoint_for(source_id, attempt)
                            )
                except _DeferIncomplete:
                    report.deferred_incomplete.append(attempt.attempt_id)
                    report.halted = HaltInfo(
                        source_id=source_id,
                        reason="extraction_incomplete",
                        at_attempt_id=attempt.attempt_id,
                        detail="committed acquisition whose extraction is not "
                        "yet complete; nothing persisted, checkpoint unchanged",
                    )
                    return report
                watermark = key
        return report

    def rebuild(self, source_id: str) -> ProjectionReport:
        """Per-source rebuild in ONE write transaction: readers see the old
        projection or the complete rebuilt one, never a partial source.
        Other sources are untouched.

        Source-local checkpoint/ledger inconsistency is exactly what this
        repairs; a GLOBAL schema/projector version mismatch is not — rows
        must never be stamped with a projector version the database
        metadata does not name, so that repair is offline ``rebuild_all``.
        Extraction incompleteness rolls the whole transaction back and
        returns a public report; counters from the discarded transaction
        are never published."""
        report = ProjectionReport(source_id=source_id)
        with self.store.writer() as conn:
            meta = dict(conn.execute("SELECT key, value FROM meta"))
            if (meta.get("schema_version") != SCHEMA_VERSION
                    or meta.get("projector_version") != self.projector_version):
                report.halted = HaltInfo(
                    source_id=source_id,
                    reason="TEMPORAL_REBUILD_REQUIRED",
                    detail="global schema/projector version mismatch; "
                    "per-source rebuild refused — run offline rebuild_all() "
                    "with the intended projector",
                )
                return report
            working = ProjectionReport(source_id=source_id)
            try:
                with self.store.attempt_txn(conn):
                    self.store.delete_source_rows(conn, source_id)
                    caches = {"mono": {}, "wall": {}, "open_ordinal": {}}
                    last_attempt = None
                    for attempt in self._ordered_attempts(source_id):
                        self._process_attempt(conn, attempt, working, caches)
                        last_attempt = attempt
                    if last_attempt is not None:
                        self.store.upsert_checkpoint(
                            conn, self._checkpoint_for(source_id, last_attempt)
                        )
            except _DeferIncomplete as defer:
                report.deferred_incomplete.append(defer.attempt_id)
                report.halted = HaltInfo(
                    source_id=source_id,
                    reason="extraction_incomplete",
                    at_attempt_id=defer.attempt_id,
                    detail="rebuild halted at incomplete extraction; "
                    "transaction rolled back, previous projection preserved",
                )
                return report
        return working

    def rebuild_all(self, source_ids: list[str]) -> dict[str, ProjectionReport]:
        """Explicit OFFLINE maintenance: requires closed readers/writers.
        Deletes exactly the database file and its exact sidecars, recreates
        the schema, and replays every given source. No whole-file byte
        determinism or online replacement is claimed."""
        db_path = self.store.db_path
        evidence_root = self.store.evidence_root
        self.store.remove_database_files()
        self.store = TemporalStore(db_path, evidence_root=evidence_root)
        return {source_id: self.rebuild(source_id) for source_id in source_ids}

    # -- internals --------------------------------------------------------

    def _ordered_attempts(self, source_id: str) -> list[AcquisitionAttempt]:
        attempts = list(self.evidence.iter_attempts(source_id))
        attempts.sort(key=lambda a: order_key_of(a).sort_tuple())
        return attempts

    def _late_attempt_halt(self, source_id: str, attempt_id: str) -> HaltInfo:
        return HaltInfo(
            source_id=source_id,
            reason="TEMPORAL_REBUILD_REQUIRED",
            at_attempt_id=attempt_id,
            detail="unprocessed attempt orders at or before the processed "
            "watermark; inserting it would rewrite existing change chains",
        )

    def _checkpoint_from_ledger_key(self, source_id, key) -> ProjectionCheckpoint:
        return ProjectionCheckpoint(
            source_id=source_id,
            last_attempt_started_at=datetime.fromisoformat(key[0]),
            last_ingestion_run_id=key[1],
            last_sweep_position=key[2],
            last_attempt_id=key[3],
            projector_version=self.projector_version,
            schema_version=SCHEMA_VERSION,
        )

    def _checkpoint_for(self, source_id, attempt) -> ProjectionCheckpoint:
        return ProjectionCheckpoint(
            source_id=source_id,
            last_attempt_started_at=attempt.started_at,
            last_ingestion_run_id=attempt.ingestion_run_id,
            last_sweep_position=attempt.sweep_position,
            last_attempt_id=attempt.attempt_id,
            projector_version=self.projector_version,
            schema_version=SCHEMA_VERSION,
        )

    def _validate_state(self, conn, source_id, report):
        """Checkpoint is an optimization; the ledger is proof. Any
        inconsistency or version mismatch requires rebuild — never silent
        repair."""
        def halt(detail: str) -> None:
            report.halted = HaltInfo(
                source_id=source_id, reason="TEMPORAL_REBUILD_REQUIRED",
                detail=detail,
            )

        meta = dict(conn.execute("SELECT key, value FROM meta"))
        if (meta.get("schema_version") != SCHEMA_VERSION
                or meta.get("projector_version") != self.projector_version):
            halt("temporal store schema/projector version mismatch")
            return None
        checkpoint = self.store.load_checkpoint(conn, source_id)
        ledger_max = self.store.ledger_max_order_key(conn, source_id)
        if checkpoint is None:
            if ledger_max is None:
                return None  # fresh source
            # Safe reconstruction: no segment or chain state lives outside
            # the immutable rows, so the watermark is simply the ledger max.
            row = conn.execute(
                "SELECT attempt_started_at, ingestion_run_id, sweep_position, "
                "attempt_id FROM temporal_attempts WHERE source_id=? ORDER BY "
                "attempt_started_at DESC, ingestion_run_id DESC, "
                "sweep_position DESC, attempt_id DESC LIMIT 1", (source_id,),
            ).fetchone()
            with self.store.attempt_txn(conn):
                conn.execute(
                    "INSERT INTO checkpoints VALUES (?,?,?,?,?,?,?)",
                    (source_id, row[0], row[1], row[2], row[3],
                     self.projector_version, SCHEMA_VERSION),
                )
            return tuple(row)
        if (checkpoint.projector_version != self.projector_version
                or checkpoint.schema_version != SCHEMA_VERSION):
            halt("checkpoint recorded under a different projector/schema version")
            return None
        checkpoint_tuple = checkpoint.order_key().sort_tuple()
        if ledger_max is None or tuple(ledger_max) != checkpoint_tuple:
            halt("checkpoint is inconsistent with the attempt ledger "
                 "(ahead, behind, or ledger empty)")
            return None
        return checkpoint_tuple

    def _process_attempt(self, conn, attempt, report, caches) -> None:
        effective = attempt.received_at or attempt.finished_at
        basis = "received_at" if attempt.received_at else "finished_at_no_response"

        def ledger_row(outcome, code, count, warnings):
            return TemporalAttemptEvent(
                attempt_id=attempt.attempt_id, source_id=attempt.source_id,
                adapter_id=attempt.adapter_id, endpoint_id=attempt.endpoint_id,
                item_key=attempt.item_key, sweep_position=attempt.sweep_position,
                ingestion_run_id=attempt.ingestion_run_id,
                attempt_started_at=attempt.started_at,
                received_at=attempt.received_at, finished_at=attempt.finished_at,
                effective_wall_time=effective, effective_time_basis=basis,
                outcome=outcome, raw_record_id=attempt.raw_record_id,
                payload_checksum=attempt.payload_checksum,
                observation_count=count, failure_or_quarantine_code=code,
                source_warning_count=warnings,
                projector_version=self.projector_version,
            )

        if attempt.outcome == "failed":
            self.store.insert_attempt_event(conn, ledger_row(
                "acquisition_failed", attempt.failure.error_code, 0, 0))
            report.attempts_by_outcome["acquisition_failed"] = (
                report.attempts_by_outcome.get("acquisition_failed", 0) + 1)
            report.attempts_processed += 1
            return
        if self.evidence.has_quarantine(attempt.raw_record_id):
            quarantine = self.evidence.get_quarantine(attempt.raw_record_id)
            self.store.insert_attempt_event(conn, ledger_row(
                "quarantined", quarantine.error_code, 0, 0))
            report.attempts_by_outcome["quarantined"] = (
                report.attempts_by_outcome.get("quarantined", 0) + 1)
            report.attempts_processed += 1
            return
        if not self.evidence.has_extraction(attempt.raw_record_id):
            raise _DeferIncomplete(attempt.attempt_id)

        manifest = self.evidence.get_extraction(attempt.raw_record_id).manifest_view()
        observations = sorted(manifest.observations, key=lambda o: o.json_pointer)

        # pre-scan: distinct monotonic markers per clock domain in this attempt
        domain_values: dict[tuple, set] = {}
        for obs in observations:
            if obs.source_time.kind == "monotonic":
                domain = (attempt.source_id, attempt.adapter_id,
                          obs.source_time.clock_id)
                domain_values.setdefault(domain, set()).add(obs.source_time.value)
        mixed_domains = {d for d, values in domain_values.items() if len(values) > 1}

        self.store.insert_attempt_event(conn, ledger_row(
            "observations_projected", None, len(observations),
            len(manifest.warnings)))
        report.attempts_by_outcome["observations_projected"] = (
            report.attempts_by_outcome.get("observations_projected", 0) + 1)
        report.attempts_processed += 1

        route = self._route_of(attempt)
        for obs in observations:
            segment_id, extra_flags = self._resolve_segment(
                conn, attempt, obs, caches, mixed_domains)
            subject = SourceSubjectRef(
                source_id=attempt.source_id, adapter_id=attempt.adapter_id,
                subject_identifier=obs.subject_identifier)
            prop = SourcePropertyRef(
                extraction_route=route, item_key=attempt.item_key,
                json_pointer=obs.json_pointer)
            previous = self.store.latest_occurrence_for_key(conn, subject, prop)
            if previous is None:
                change, prev_id = "first_seen", None
            elif (previous[1], previous[2]) == (obs.json_type, obs.value_json):
                change, prev_id = "unchanged", previous[0]
            else:
                change, prev_id = "changed", previous[0]
            occurrence = TemporalOccurrence(
                occurrence_id=derive_entity_id(
                    attempt.attempt_id, "temporal", obs.observation_id),
                attempt_id=attempt.attempt_id,
                subject=subject, property=prop,
                observation_id=obs.observation_id,
                raw_record_id=attempt.raw_record_id,
                payload_checksum=attempt.payload_checksum,
                attempt_started_at=attempt.started_at,
                ingestion_run_id=attempt.ingestion_run_id,
                sweep_position=attempt.sweep_position,
                received_at=attempt.received_at, finished_at=attempt.finished_at,
                source_time=obs.source_time, clock_segment_id=segment_id,
                value_json=obs.value_json, json_type=obs.json_type,
                declared_unit=obs.declared_unit, change_class=change,
                previous_occurrence_id=prev_id,
                quality_flags=sorted({*obs.quality_flags, *extra_flags}),
            )
            self.store.insert_occurrence(conn, occurrence)
            report.occurrences_created += 1

    def _route_of(self, attempt) -> str:
        envelope = self.evidence.get_envelope(attempt.raw_record_id)
        if envelope.api_locator is not None:
            return envelope.api_locator.extraction_route
        return envelope.content_type

    def _resolve_segment(self, conn, attempt, obs, caches, mixed_domains):
        marker = obs.source_time
        if marker.kind == "unavailable":
            return None, ["ordered_by_acquisition_time_only"]
        effective = attempt.received_at

        if marker.kind == "wall_clock":
            clock_id = f"wall_clock:{marker.basis}"
            domain = (attempt.source_id, attempt.adapter_id, clock_id)
            if domain not in caches["wall"]:
                existing = self.store.wall_clock_segment_in_domain(conn, *domain)
                if existing is None:
                    existing = self._open_segment(
                        conn, attempt, domain, "initial", caches, effective)
                caches["wall"][domain] = existing
            return caches["wall"][domain], []

        domain = (attempt.source_id, attempt.adapter_id, marker.clock_id)
        flags = ["mixed_source_time_snapshot"] if domain in mixed_domains else []
        cache = caches["mono"]
        if domain not in cache:
            row = self.store.latest_marker_in_domain(conn, *domain)
            cache[domain] = (Decimal(row[0]), row[1]) if row else None
        state = cache[domain]
        value = Decimal(marker.value)
        decrease_marks = caches.setdefault("decrease_marks", {})
        if state is None:
            segment_id = self._open_segment(
                conn, attempt, domain, "initial", caches, effective)
        elif value < state[0]:
            segment_id = self._open_segment(
                conn, attempt, domain, "monotonic_decrease_observed",
                caches, effective)
            flags.append("possible_source_clock_reset")
            # every observation in this attempt carrying the decreased
            # marker is at the observed boundary and gets the flag
            decrease_marks[(domain, attempt.attempt_id, marker.value)] = True
        else:
            segment_id = state[1]
            if decrease_marks.get((domain, attempt.attempt_id, marker.value)):
                flags.append("possible_source_clock_reset")
        cache[domain] = (value, segment_id)  # last observed, processing order
        return segment_id, flags

    def _open_segment(self, conn, attempt, domain, reason, caches, effective):
        ordinal_key = (domain, attempt.attempt_id)
        ordinal = caches["open_ordinal"].get(ordinal_key, 0)
        caches["open_ordinal"][ordinal_key] = ordinal + 1
        segment = ClockSegmentOpening(
            segment_id=derive_entity_id(
                domain[0], "segment",
                f"{domain[1]}:{domain[2]}:{attempt.attempt_id}:{ordinal}"),
            source_id=domain[0], adapter_id=domain[1], clock_id=domain[2],
            boundary_reason=reason, opened_by_attempt_id=attempt.attempt_id,
            opened_at_effective_wall_time=effective,
        )
        self.store.insert_segment(conn, segment)
        return segment.segment_id
