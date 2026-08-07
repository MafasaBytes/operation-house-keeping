"""TS-001 read APIs over the temporal store.

Every time-relative query takes an explicit caller-supplied ``as_of``
cutoff and is historically closed at it: occurrence choice, staleness,
and every evidence-quality component are computed solely from rows whose
effective wall time is at or before the cutoff, tie-broken by the
AttemptOrderKey components. Results report "latest observed" evidence —
never actual system state.
"""

import json
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.temporal_state.contracts import (
    ClockSegmentOpening,
    SourcePropertyRef,
    SourceSubjectRef,
    TemporalAttemptEvent,
    TemporalOccurrence,
)
from backend.temporal_state.store import TemporalStore, _dt, _iso, marker_from_json


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True)


class EvidenceQuality(_Frozen):
    intervening_failed_attempts: int
    intervening_quarantined_attempts: int
    later_snapshots_without_property: int
    later_empty_snapshots: int
    latest_applicable_attempt_outcome: str | None
    source_time_basis: str
    clock_segment_id: str | None
    possible_source_clock_reset: bool


class LatestObservedState(_Frozen):
    occurrence: TemporalOccurrence
    as_of: datetime
    staleness_seconds: float
    evidence_quality: EvidenceQuality


class FreshnessEntry(_Frozen):
    subject: SourceSubjectRef
    property: SourcePropertyRef
    occurrence_id: str
    received_at: datetime
    staleness_seconds: float
    failed_attempts_since: int
    quarantined_attempts_since: int


class ProvenanceChain(_Frozen):
    occurrence_id: str
    attempt_id: str
    observation_id: str
    raw_record_id: str
    payload_checksum: str


_KEY_WHERE = (
    "source_id=? AND adapter_id=? AND subject_identifier=? AND "
    "extraction_route=? AND item_key=? AND json_pointer=?"
)
_ORDER_ASC = ("attempt_started_at, ingestion_run_id, sweep_position, "
              "attempt_id")
_ORDER_DESC = ("attempt_started_at DESC, ingestion_run_id DESC, "
               "sweep_position DESC, attempt_id DESC")


def _key_params(subject: SourceSubjectRef, prop: SourcePropertyRef) -> tuple:
    return (subject.source_id, subject.adapter_id, subject.subject_identifier,
            prop.extraction_route, prop.item_key, prop.json_pointer)


def _occurrence_from_row(row) -> TemporalOccurrence:
    return TemporalOccurrence(
        occurrence_id=row[0], attempt_id=row[1],
        subject=SourceSubjectRef(source_id=row[2], adapter_id=row[3],
                                 subject_identifier=row[4]),
        property=SourcePropertyRef(extraction_route=row[5], item_key=row[6],
                                   json_pointer=row[7]),
        observation_id=row[8], raw_record_id=row[9], payload_checksum=row[10],
        attempt_started_at=_dt(row[11]), ingestion_run_id=row[12],
        sweep_position=row[13], received_at=_dt(row[14]),
        finished_at=_dt(row[15]), source_time=marker_from_json(row[19]),
        clock_segment_id=row[20], value_json=row[21], json_type=row[22],
        declared_unit=row[23], change_class=row[24],
        previous_occurrence_id=row[25],
        quality_flags=json.loads(row[26]),
    )


def _attempt_from_row(row) -> TemporalAttemptEvent:
    return TemporalAttemptEvent(
        attempt_id=row[0], source_id=row[1], adapter_id=row[2],
        endpoint_id=row[3], item_key=row[4], sweep_position=row[5],
        ingestion_run_id=row[6], attempt_started_at=_dt(row[7]),
        received_at=_dt(row[8]), finished_at=_dt(row[9]),
        effective_wall_time=_dt(row[10]), effective_time_basis=row[11],
        outcome=row[12], raw_record_id=row[13], payload_checksum=row[14],
        observation_count=row[15], failure_or_quarantine_code=row[16],
        source_warning_count=row[17], projector_version=row[18],
    )


class TemporalQueries:
    def __init__(self, store: TemporalStore) -> None:
        self.store = store

    # -- histories --------------------------------------------------------

    def history(self, subject, prop, limit: int | None = None):
        sql = (f"SELECT * FROM temporal_occurrences WHERE {_KEY_WHERE} "
               f"ORDER BY {_ORDER_ASC}")
        params = _key_params(subject, prop)
        if limit is not None:
            sql += " LIMIT ?"
            params = (*params, limit)
        with self.store.reader() as conn:
            return [_occurrence_from_row(r) for r in conn.execute(sql, params)]

    def change_history(self, subject, prop):
        with self.store.reader() as conn:
            rows = conn.execute(
                f"SELECT * FROM temporal_occurrences WHERE {_KEY_WHERE} AND "
                f"change_class != 'unchanged' ORDER BY {_ORDER_ASC}",
                _key_params(subject, prop),
            ).fetchall()
        return [_occurrence_from_row(r) for r in rows]

    # -- latest observed (single query, required cutoff, closed) ----------

    def latest_observed(self, subject, prop, as_of: datetime):
        cutoff = _iso(as_of)
        with self.store.reader() as conn:
            row = conn.execute(
                f"SELECT * FROM temporal_occurrences WHERE {_KEY_WHERE} AND "
                f"received_at <= ? ORDER BY received_at DESC, {_ORDER_DESC} "
                "LIMIT 1",
                (*_key_params(subject, prop), cutoff),
            ).fetchone()
            if row is None:
                return None
            occurrence = _occurrence_from_row(row)
            occ_window = (_iso(occurrence.received_at),
                          _iso(occurrence.attempt_started_at),
                          occurrence.ingestion_run_id,
                          occurrence.sweep_position, occurrence.attempt_id)
            # "intervening/later" = effective time strictly after the
            # occurrence (row-value tie-break) and at or before the cutoff.
            window = (
                "source_id=? AND item_key=? AND effective_wall_time <= ? AND "
                "(effective_wall_time > ? OR (effective_wall_time = ? AND "
                "(attempt_started_at, ingestion_run_id, sweep_position, "
                "attempt_id) > (?,?,?,?)))"
            )
            window_params = (subject.source_id, prop.item_key, cutoff,
                             occ_window[0], occ_window[0], occ_window[1],
                             occ_window[2], occ_window[3], occ_window[4])

            def count(extra_sql: str, extra_params: tuple = ()) -> int:
                return conn.execute(
                    f"SELECT count(*) FROM temporal_attempts a WHERE {window} "
                    f"{extra_sql}", (*window_params, *extra_params),
                ).fetchone()[0]

            failed = count("AND outcome='acquisition_failed'")
            quarantined = count("AND outcome='quarantined'")
            empty_later = count(
                "AND outcome='observations_projected' AND observation_count=0")
            not_exists = (
                "o.source_id=? AND o.adapter_id=? AND o.subject_identifier=? "
                "AND o.extraction_route=? AND o.item_key=? AND o.json_pointer=?"
            )
            without_property = count(
                "AND outcome='observations_projected' AND observation_count>0 "
                "AND NOT EXISTS (SELECT 1 FROM temporal_occurrences o WHERE "
                f"o.attempt_id=a.attempt_id AND {not_exists})",
                _key_params(subject, prop),
            )
            latest_attempt = conn.execute(
                "SELECT outcome FROM temporal_attempts WHERE source_id=? AND "
                "item_key=? AND effective_wall_time <= ? ORDER BY "
                f"effective_wall_time DESC, {_ORDER_DESC} LIMIT 1",
                (subject.source_id, prop.item_key, cutoff),
            ).fetchone()

        quality = EvidenceQuality(
            intervening_failed_attempts=failed,
            intervening_quarantined_attempts=quarantined,
            later_snapshots_without_property=without_property,
            later_empty_snapshots=empty_later,
            latest_applicable_attempt_outcome=(
                latest_attempt[0] if latest_attempt else None),
            source_time_basis=occurrence.source_time.kind,
            clock_segment_id=occurrence.clock_segment_id,
            possible_source_clock_reset=(
                "possible_source_clock_reset" in occurrence.quality_flags),
        )
        return LatestObservedState(
            occurrence=occurrence, as_of=as_of,
            staleness_seconds=(as_of - occurrence.received_at).total_seconds(),
            evidence_quality=quality,
        )

    # -- coverage / freshness / provenance / segments ---------------------

    def attempt_coverage(self, source_id: str, item_key: str | None = None):
        sql = "SELECT * FROM temporal_attempts WHERE source_id=?"
        params: tuple = (source_id,)
        if item_key is not None:
            sql += " AND item_key=?"
            params = (*params, item_key)
        sql += f" ORDER BY {_ORDER_ASC}"
        with self.store.reader() as conn:
            return [_attempt_from_row(r) for r in conn.execute(sql, params)]

    def freshness(self, source_id: str, as_of: datetime):
        cutoff = _iso(as_of)
        entries = []
        with self.store.reader() as conn:
            keys = conn.execute(
                "SELECT DISTINCT source_id, adapter_id, subject_identifier, "
                "extraction_route, item_key, json_pointer FROM "
                "temporal_occurrences WHERE source_id=? ORDER BY 1,2,3,4,5,6",
                (source_id,),
            ).fetchall()
        for key in keys:
            subject = SourceSubjectRef(source_id=key[0], adapter_id=key[1],
                                       subject_identifier=key[2])
            prop = SourcePropertyRef(extraction_route=key[3], item_key=key[4],
                                     json_pointer=key[5])
            latest = self.latest_observed(subject, prop, as_of)
            if latest is None:
                continue
            entries.append(FreshnessEntry(
                subject=subject, property=prop,
                occurrence_id=latest.occurrence.occurrence_id,
                received_at=latest.occurrence.received_at,
                staleness_seconds=latest.staleness_seconds,
                failed_attempts_since=(
                    latest.evidence_quality.intervening_failed_attempts),
                quarantined_attempts_since=(
                    latest.evidence_quality.intervening_quarantined_attempts),
            ))
        return entries

    def provenance(self, occurrence_id: str) -> ProvenanceChain | None:
        with self.store.reader() as conn:
            row = conn.execute(
                "SELECT occurrence_id, attempt_id, observation_id, "
                "raw_record_id, payload_checksum FROM temporal_occurrences "
                "WHERE occurrence_id=?", (occurrence_id,),
            ).fetchone()
        if row is None:
            return None
        return ProvenanceChain(
            occurrence_id=row[0], attempt_id=row[1], observation_id=row[2],
            raw_record_id=row[3], payload_checksum=row[4],
        )

    def clock_segments(self, source_id: str):
        with self.store.reader() as conn:
            rows = conn.execute(
                "SELECT * FROM clock_segment_openings WHERE source_id=? "
                "ORDER BY opened_at_effective_wall_time, segment_id",
                (source_id,),
            ).fetchall()
        return [
            ClockSegmentOpening(
                segment_id=r[0], source_id=r[1], adapter_id=r[2],
                clock_id=r[3], boundary_reason=r[4],
                opened_by_attempt_id=r[5],
                opened_at_effective_wall_time=_dt(r[6]),
            )
            for r in rows
        ]
