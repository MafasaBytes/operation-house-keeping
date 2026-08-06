"""Write-once filesystem raw store.

Layout under the base directory:

    payloads/<sha256-hex>          original bytes, content-addressed
    envelopes/<record_id>.json     RawRecord
    runs/<run_id>.json             IngestionRun
    quarantine/<record_id>.json    QuarantineRecord
    extracted/<record_id>.json     ExtractedTable

Nothing is ever overwritten: identical re-writes are detected (duplicates),
conflicting re-writes raise StoreIntegrityError.
"""

from collections.abc import Iterator
from pathlib import Path

from pydantic import BaseModel

from backend.data_sources.contracts import (
    ExtractedTable,
    IngestionRun,
    QuarantineRecord,
    RawRecord,
    StoreIntegrityError,
)
from backend.data_sources.provenance import payload_checksum

_CHECKSUM_PREFIX = "sha256:"


class FilesystemRawStore:
    def __init__(self, base_dir: Path | str) -> None:
        self.base_dir = Path(base_dir)
        self._payloads = self.base_dir / "payloads"
        self._envelopes = self.base_dir / "envelopes"
        self._runs = self.base_dir / "runs"
        self._quarantine = self.base_dir / "quarantine"
        self._extracted = self.base_dir / "extracted"
        for directory in (
            self._payloads,
            self._envelopes,
            self._runs,
            self._quarantine,
            self._extracted,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    # -- payloads ---------------------------------------------------------

    def put_payload(self, data: bytes) -> str:
        reference = payload_checksum(data)
        target = self._payloads / reference.removeprefix(_CHECKSUM_PREFIX)
        if not target.exists():
            self._write_once(target, data)
        return reference

    def get_payload(self, reference: str) -> bytes:
        target = self._payloads / reference.removeprefix(_CHECKSUM_PREFIX)
        if not target.exists():
            raise StoreIntegrityError(
                "STORE_MISSING_PAYLOAD", f"no payload stored for {reference}"
            )
        data = target.read_bytes()
        if payload_checksum(data) != reference:
            raise StoreIntegrityError(
                "STORE_CHECKSUM_MISMATCH",
                f"stored payload no longer matches checksum {reference}",
            )
        return data

    # -- envelopes --------------------------------------------------------

    def put_envelope(self, record: RawRecord) -> bool:
        """Persist a raw record envelope.

        Returns True if newly stored, False if an identical envelope already
        exists (a detected duplicate). Raises StoreIntegrityError if a
        different envelope is already stored under the same record_id.
        """
        return self._put_json_once(
            self._envelopes / f"{record.record_id}.json", record, "envelope"
        )

    def has_envelope(self, record_id: str) -> bool:
        return (self._envelopes / f"{record_id}.json").exists()

    def iter_accepted_envelopes(self, source_id: str) -> Iterator[RawRecord]:
        """Yield stored envelopes for a source, excluding quarantined records,
        in deterministic (record_id) order."""
        for path in sorted(self._envelopes.glob("*.json")):
            record = RawRecord.model_validate_json(path.read_text("utf-8"))
            if record.source_id != source_id:
                continue
            if (self._quarantine / f"{record.record_id}.json").exists():
                continue
            yield record

    # -- runs, quarantine, extracted --------------------------------------

    def put_run(self, run: IngestionRun) -> bool:
        return self._put_json_once(self._runs / f"{run.run_id}.json", run, "run")

    def iter_runs(self, source_id: str) -> Iterator[IngestionRun]:
        for path in sorted(self._runs.glob("*.json")):
            run = IngestionRun.model_validate_json(path.read_text("utf-8"))
            if run.source_id == source_id:
                yield run

    def get_run(self, run_id: str) -> IngestionRun:
        return IngestionRun.model_validate_json(
            self._read_required(self._runs / f"{run_id}.json", f"run {run_id}")
        )

    def put_quarantine(self, record: QuarantineRecord) -> bool:
        return self._put_json_once(
            self._quarantine / f"{record.record_id}.json", record, "quarantine record"
        )

    def get_quarantine(self, record_id: str) -> QuarantineRecord:
        return QuarantineRecord.model_validate_json(
            self._read_required(
                self._quarantine / f"{record_id}.json", f"quarantine {record_id}"
            )
        )

    def put_extracted(self, table: ExtractedTable) -> bool:
        return self._put_json_once(
            self._extracted / f"{table.raw_record_id}.json", table, "extracted table"
        )

    def get_extracted(self, record_id: str) -> ExtractedTable:
        return ExtractedTable.model_validate_json(
            self._read_required(
                self._extracted / f"{record_id}.json", f"extraction {record_id}"
            )
        )

    # -- internals --------------------------------------------------------

    def _put_json_once(self, target: Path, model: BaseModel, kind: str) -> bool:
        serialized = model.model_dump_json(indent=2)
        if target.exists():
            if target.read_text("utf-8") == serialized:
                return False
            raise StoreIntegrityError(
                "STORE_CONFLICT",
                f"a different {kind} is already stored as {target.name}",
            )
        self._write_once(target, serialized.encode("utf-8"))
        return True

    @staticmethod
    def _write_once(target: Path, data: bytes) -> None:
        # Write via a temp file then atomic rename so a crash cannot leave a
        # half-written record; mark read-only as a guard against mutation.
        tmp = target.with_suffix(target.suffix + ".tmp")
        tmp.write_bytes(data)
        tmp.replace(target)
        target.chmod(0o444)

    def _read_required(self, target: Path, description: str) -> str:
        if not target.exists():
            raise StoreIntegrityError("STORE_MISSING", f"no {description} stored")
        return target.read_text("utf-8")
