"""Rebuildable SQLite store for the TS-001 temporal projection.

Derived data only — the evidence store stays authoritative and untouched.
Logical rows are deterministic for the same evidence and projector
version; SQLite/WAL/SHM file bytes are explicitly NOT part of that claim.

Writer model (honest): one active write transaction at a time via
``BEGIN IMMEDIATE`` with busy_timeout=0; actual write contention raises
TemporalStoreBusyError — no lifetime lease is pretended. Readers operate
concurrently under WAL.
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from backend.data_sources.contracts import SourceTimeMarker
from backend.temporal_state.contracts import (
    ClockSegmentOpening,
    ProjectionCheckpoint,
    SourcePropertyRef,
    SourceSubjectRef,
    TemporalAttemptEvent,
    TemporalConfigurationError,
    TemporalOccurrence,
    TemporalStoreBusyError,
)

SCHEMA_VERSION = "1"
PROJECTOR_VERSION = "1.0.0"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS temporal_attempts(
  attempt_id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL, adapter_id TEXT NOT NULL,
  endpoint_id TEXT NOT NULL, item_key TEXT NOT NULL,
  sweep_position INTEGER NOT NULL, ingestion_run_id TEXT NOT NULL,
  attempt_started_at TEXT NOT NULL, received_at TEXT,
  finished_at TEXT NOT NULL,
  effective_wall_time TEXT NOT NULL, effective_time_basis TEXT NOT NULL,
  outcome TEXT NOT NULL, raw_record_id TEXT, payload_checksum TEXT,
  observation_count INTEGER NOT NULL,
  failure_or_quarantine_code TEXT, source_warning_count INTEGER NOT NULL,
  projector_version TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_attempts_order ON temporal_attempts(
  source_id, attempt_started_at, ingestion_run_id, sweep_position, attempt_id);
CREATE INDEX IF NOT EXISTS idx_attempts_scope ON temporal_attempts(
  source_id, adapter_id, item_key, effective_wall_time);

CREATE TABLE IF NOT EXISTS clock_segment_openings(
  segment_id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL, adapter_id TEXT NOT NULL, clock_id TEXT NOT NULL,
  boundary_reason TEXT NOT NULL,
  opened_by_attempt_id TEXT NOT NULL REFERENCES temporal_attempts(attempt_id),
  opened_at_effective_wall_time TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_segments_domain ON clock_segment_openings(
  source_id, adapter_id, clock_id);

CREATE TABLE IF NOT EXISTS temporal_occurrences(
  occurrence_id TEXT PRIMARY KEY,
  attempt_id TEXT NOT NULL REFERENCES temporal_attempts(attempt_id),
  source_id TEXT NOT NULL, adapter_id TEXT NOT NULL,
  subject_identifier TEXT NOT NULL,
  extraction_route TEXT NOT NULL, item_key TEXT NOT NULL,
  json_pointer TEXT NOT NULL,
  observation_id TEXT NOT NULL, raw_record_id TEXT NOT NULL,
  payload_checksum TEXT NOT NULL,
  attempt_started_at TEXT NOT NULL, ingestion_run_id TEXT NOT NULL,
  sweep_position INTEGER NOT NULL,
  received_at TEXT NOT NULL, finished_at TEXT NOT NULL,
  source_time_kind TEXT NOT NULL, source_clock_id TEXT,
  source_marker_value TEXT, source_time_json TEXT NOT NULL,
  clock_segment_id TEXT REFERENCES clock_segment_openings(segment_id),
  value_json TEXT NOT NULL, json_type TEXT NOT NULL, declared_unit TEXT,
  change_class TEXT NOT NULL, previous_occurrence_id TEXT,
  quality_flags_json TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_occ_key_order ON temporal_occurrences(
  source_id, adapter_id, subject_identifier, extraction_route, item_key,
  json_pointer, attempt_started_at, ingestion_run_id, sweep_position,
  attempt_id);
CREATE INDEX IF NOT EXISTS idx_occ_key_ewt ON temporal_occurrences(
  source_id, adapter_id, subject_identifier, extraction_route, item_key,
  json_pointer, received_at);
CREATE INDEX IF NOT EXISTS idx_occ_domain ON temporal_occurrences(
  source_id, adapter_id, source_clock_id, attempt_started_at,
  ingestion_run_id, sweep_position, attempt_id);

CREATE TABLE IF NOT EXISTS checkpoints(
  source_id TEXT PRIMARY KEY,
  last_attempt_started_at TEXT NOT NULL,
  last_ingestion_run_id TEXT NOT NULL,
  last_sweep_position INTEGER NOT NULL,
  last_attempt_id TEXT NOT NULL,
  projector_version TEXT NOT NULL, schema_version TEXT NOT NULL);
"""

_DUMP_TABLES = {
    "temporal_attempts": "attempt_id",
    "temporal_occurrences": "occurrence_id",
    "clock_segment_openings": "segment_id",
}


def _iso(value: datetime | None) -> str | None:
    return value.astimezone(UTC).isoformat() if value is not None else None


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value is not None else None


class TemporalStore:
    def __init__(self, db_path: Path | str, evidence_root: Path | str) -> None:
        candidate = Path(db_path).resolve()
        root = Path(evidence_root).resolve()
        if candidate == root or root in candidate.parents:
            raise TemporalConfigurationError(
                "TEMPORAL_PATH_INSIDE_EVIDENCE_STORE",
                "the temporal database may not live at or inside the "
                "immutable evidence-store root",
            )
        self.db_path = candidate
        self.evidence_root = root
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.writer() as conn:
            conn.executescript(_SCHEMA)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                "INSERT OR IGNORE INTO meta VALUES ('schema_version', ?)",
                (SCHEMA_VERSION,),
            )
            conn.execute(
                "INSERT OR IGNORE INTO meta VALUES ('projector_version', ?)",
                (PROJECTOR_VERSION,),
            )

    # -- connections ------------------------------------------------------

    @contextmanager
    def writer(self):
        conn = sqlite3.connect(str(self.db_path), timeout=0, isolation_level=None)
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def reader(self):
        conn = sqlite3.connect(
            f"file:{self.db_path}?mode=ro", uri=True, timeout=0,
            isolation_level=None,
        )
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def attempt_txn(self, conn: sqlite3.Connection):
        """One write transaction (the per-attempt atomicity boundary).
        Actual write contention raises the typed busy error."""
        try:
            conn.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as error:
            if "locked" in str(error) or "busy" in str(error):
                raise TemporalStoreBusyError(
                    "TEMPORAL_STORE_BUSY",
                    "another write transaction is active on the temporal store",
                ) from error
            raise
        try:
            yield
        except BaseException:
            conn.execute("ROLLBACK")
            raise
        else:
            conn.execute("COMMIT")

    # -- meta -------------------------------------------------------------

    def meta_versions(self) -> tuple[str, str]:
        with self.reader() as conn:
            rows = dict(conn.execute("SELECT key, value FROM meta"))
        return rows.get("schema_version", ""), rows.get("projector_version", "")

    # -- inserts ----------------------------------------------------------

    def insert_attempt_event(self, conn, event: TemporalAttemptEvent) -> None:
        conn.execute(
            "INSERT INTO temporal_attempts VALUES "
            "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (event.attempt_id, event.source_id, event.adapter_id,
             event.endpoint_id, event.item_key, event.sweep_position,
             event.ingestion_run_id, _iso(event.attempt_started_at),
             _iso(event.received_at), _iso(event.finished_at),
             _iso(event.effective_wall_time), event.effective_time_basis,
             event.outcome, event.raw_record_id, event.payload_checksum,
             event.observation_count, event.failure_or_quarantine_code,
             event.source_warning_count, event.projector_version),
        )

    def insert_segment(self, conn, opening: ClockSegmentOpening) -> None:
        conn.execute(
            "INSERT INTO clock_segment_openings VALUES (?,?,?,?,?,?,?)",
            (opening.segment_id, opening.source_id, opening.adapter_id,
             opening.clock_id, opening.boundary_reason,
             opening.opened_by_attempt_id,
             _iso(opening.opened_at_effective_wall_time)),
        )

    def insert_occurrence(self, conn, occ: TemporalOccurrence) -> None:
        marker = occ.source_time
        conn.execute(
            "INSERT INTO temporal_occurrences VALUES "
            "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (occ.occurrence_id, occ.attempt_id,
             occ.subject.source_id, occ.subject.adapter_id,
             occ.subject.subject_identifier,
             occ.property.extraction_route, occ.property.item_key,
             occ.property.json_pointer,
             occ.observation_id, occ.raw_record_id, occ.payload_checksum,
             _iso(occ.attempt_started_at), occ.ingestion_run_id,
             occ.sweep_position, _iso(occ.received_at), _iso(occ.finished_at),
             marker.kind,
             getattr(marker, "clock_id", None),
             getattr(marker, "value", None) if marker.kind == "monotonic" else None,
             marker.model_dump_json(),
             occ.clock_segment_id, occ.value_json, occ.json_type,
             occ.declared_unit, occ.change_class, occ.previous_occurrence_id,
             json.dumps(sorted(occ.quality_flags))),
        )

    # -- lookups ----------------------------------------------------------

    def has_attempt(self, conn, attempt_id: str) -> bool:
        return conn.execute(
            "SELECT 1 FROM temporal_attempts WHERE attempt_id=?", (attempt_id,)
        ).fetchone() is not None

    def ledger_max_order_key(self, conn, source_id: str):
        row = conn.execute(
            "SELECT attempt_started_at, ingestion_run_id, sweep_position, "
            "attempt_id FROM temporal_attempts WHERE source_id=? "
            "ORDER BY attempt_started_at DESC, ingestion_run_id DESC, "
            "sweep_position DESC, attempt_id DESC LIMIT 1",
            (source_id,),
        ).fetchone()
        if row is None:
            return None
        return (row[0], row[1], row[2], row[3])

    def latest_occurrence_for_key(
        self, conn, subject: SourceSubjectRef, prop: SourcePropertyRef
    ):
        """Latest occurrence for the COMPLETE six-dimension key, by the
        deterministic attempt order."""
        return conn.execute(
            "SELECT occurrence_id, json_type, value_json FROM "
            "temporal_occurrences WHERE source_id=? AND adapter_id=? AND "
            "subject_identifier=? AND extraction_route=? AND item_key=? AND "
            "json_pointer=? ORDER BY attempt_started_at DESC, "
            "ingestion_run_id DESC, sweep_position DESC, attempt_id DESC "
            "LIMIT 1",
            (subject.source_id, subject.adapter_id, subject.subject_identifier,
             prop.extraction_route, prop.item_key, prop.json_pointer),
        ).fetchone()

    def latest_marker_in_domain(
        self, conn, source_id: str, adapter_id: str, clock_id: str
    ):
        """Latest monotonic marker observed in a clock domain, derived from
        occurrence rows (never from checkpoints)."""
        return conn.execute(
            "SELECT source_marker_value, clock_segment_id FROM "
            "temporal_occurrences WHERE source_id=? AND adapter_id=? AND "
            "source_clock_id=? AND source_time_kind='monotonic' "
            "ORDER BY attempt_started_at DESC, ingestion_run_id DESC, "
            "sweep_position DESC, attempt_id DESC LIMIT 1",
            (source_id, adapter_id, clock_id),
        ).fetchone()

    def wall_clock_segment_in_domain(
        self, conn, source_id: str, adapter_id: str, clock_id: str
    ):
        row = conn.execute(
            "SELECT segment_id FROM clock_segment_openings WHERE source_id=? "
            "AND adapter_id=? AND clock_id=? ORDER BY segment_id LIMIT 1",
            (source_id, adapter_id, clock_id),
        ).fetchone()
        return row[0] if row else None

    # -- checkpoints ------------------------------------------------------

    def upsert_checkpoint(self, conn, checkpoint: ProjectionCheckpoint) -> None:
        conn.execute(
            "INSERT INTO checkpoints VALUES (?,?,?,?,?,?,?) "
            "ON CONFLICT(source_id) DO UPDATE SET "
            "last_attempt_started_at=excluded.last_attempt_started_at, "
            "last_ingestion_run_id=excluded.last_ingestion_run_id, "
            "last_sweep_position=excluded.last_sweep_position, "
            "last_attempt_id=excluded.last_attempt_id, "
            "projector_version=excluded.projector_version, "
            "schema_version=excluded.schema_version",
            (checkpoint.source_id, _iso(checkpoint.last_attempt_started_at),
             checkpoint.last_ingestion_run_id, checkpoint.last_sweep_position,
             checkpoint.last_attempt_id, checkpoint.projector_version,
             checkpoint.schema_version),
        )

    def load_checkpoint(self, conn, source_id: str) -> ProjectionCheckpoint | None:
        row = conn.execute(
            "SELECT * FROM checkpoints WHERE source_id=?", (source_id,)
        ).fetchone()
        if row is None:
            return None
        return ProjectionCheckpoint(
            source_id=row[0], last_attempt_started_at=_dt(row[1]),
            last_ingestion_run_id=row[2], last_sweep_position=row[3],
            last_attempt_id=row[4], projector_version=row[5],
            schema_version=row[6],
        )

    # -- dump / rebuild helpers ------------------------------------------

    def ordered_logical_dump(self) -> dict[str, list[tuple]]:
        """Deterministic logical content; checkpoints excluded (they are an
        optimization, not part of the determinism claim)."""
        dump: dict[str, list[tuple]] = {}
        with self.reader() as conn:
            for table, pk in _DUMP_TABLES.items():
                dump[table] = conn.execute(
                    f"SELECT * FROM {table} ORDER BY {pk}"
                ).fetchall()
        return dump

    def delete_source_rows(self, conn, source_id: str) -> None:
        conn.execute("DELETE FROM temporal_occurrences WHERE source_id=?",
                     (source_id,))
        conn.execute("DELETE FROM clock_segment_openings WHERE source_id=?",
                     (source_id,))
        conn.execute("DELETE FROM temporal_attempts WHERE source_id=?",
                     (source_id,))
        conn.execute("DELETE FROM checkpoints WHERE source_id=?", (source_id,))

    def remove_database_files(self) -> None:
        """Offline maintenance: deletes exactly the configured database
        file and its exact SQLite sidecars — never a directory."""
        for suffix in ("", "-wal", "-shm"):
            target = Path(str(self.db_path) + suffix)
            if target.exists():
                target.unlink()


def marker_from_json(payload: str) -> SourceTimeMarker:
    from pydantic import TypeAdapter

    return TypeAdapter(SourceTimeMarker).validate_json(payload)
