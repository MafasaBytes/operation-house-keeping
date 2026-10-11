"""Application-owned bounded adapter for the owning raw-store public protocol.

The fixed T1 sweep retains at most two records in memory. Owning backend models
and public runner/projector methods are unchanged; no test fixture is involved.
"""
from pathlib import Path
from .t1_contracts import refuse


class RawStore:
    def __init__(self, base_dir, publication=None):
        self.base_dir = Path(base_dir)
        self.publication = publication
        self.payloads, self.envelopes, self.attempts = {}, {}, {}
        self.extractions, self.runs, self.quarantines = {}, {}, {}

    def _put(self, pool, key, value):
        if key in pool:
            if pool[key] != value:
                refuse('SIM_DERIVATION_MISMATCH', 7, '/evidence/raw')
            return False
        if len(pool) >= 2:
            refuse('SIM_RESOURCE_LIMIT', 7, '/evidence/raw', 4)
        pool[key] = value
        if self.publication is not None:
            prefix = 'evidence/raw/' if pool is self.payloads else \
                'evidence/raw/envelope-' if pool is self.envelopes else \
                'evidence/attempts/' if pool is self.attempts else \
                'evidence/extraction/' if pool is self.extractions else None
            if prefix is not None:
                path = prefix + (key.removeprefix('sha256:') if pool is self.payloads else key + '.json')
                wire = value if isinstance(value, bytes) else value.model_dump_json(indent=2).encode('utf-8')
                self.publication.write(path, wire)
        return True

    def put_payload(self, data):
        from backend.data_sources.provenance import payload_checksum
        if len(data) > 16384:
            refuse('SIM_RESOURCE_LIMIT', 7, '/evidence/raw', 4)
        digest = payload_checksum(data)
        self._put(self.payloads, digest, data)
        return digest

    def get_payload(self, digest): return self.payloads[digest]
    def put_envelope(self, value): return self._put(self.envelopes, value.record_id, value)
    def has_envelope(self, key): return key in self.envelopes
    def get_envelope(self, key): return self.envelopes[key]
    def put_attempt(self, value): return self._put(self.attempts, value.attempt_id, value)
    def get_attempt(self, key): return self.attempts[key]
    def iter_attempts(self, source):
        return iter(sorted((a for a in self.attempts.values() if a.source_id == source),
                           key=lambda a: (a.started_at, a.attempt_id)))
    def put_extraction(self, value): return self._put(self.extractions, value.raw_record_id, value)
    def has_extraction(self, key): return key in self.extractions
    def get_extraction(self, key): return self.extractions[key]
    def put_run(self, value): return self._put(self.runs, value.run_id, value)
    def iter_runs(self, source): return iter(r for r in self.runs.values() if r.source_id == source)
    def put_quarantine(self, value): return self._put(self.quarantines, value.record_id, value)
    def has_quarantine(self, key): return key in self.quarantines
    def get_quarantine(self, key): return self.quarantines[key]
    def iter_accepted_envelopes(self, source):
        committed = {a.raw_record_id for a in self.attempts.values() if a.raw_record_id}
        return iter(e for key, e in sorted(self.envelopes.items())
                    if e.source_id == source and key in committed and key not in self.quarantines)

    def retained_files(self):
        files = {'evidence/raw/' + d.removeprefix('sha256:'): w for d, w in self.payloads.items()}
        for pool, prefix in ((self.envelopes, 'evidence/raw/envelope-'),
                             (self.attempts, 'evidence/attempts/'),
                             (self.extractions, 'evidence/extraction/')):
            files.update({prefix + key + '.json': value.model_dump_json(indent=2).encode('utf-8')
                          for key, value in pool.items()})
        return files
