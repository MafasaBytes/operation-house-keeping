"""Fresh logical backend reconstruction via public connection-context seams.

No backend schema/constants are copied: the owning constructor initializes its
schema through overridden public writer/reader methods. The ephemeral database
has no physical-byte oracle and does not replace retained diagnostic DBs.
"""
from contextlib import contextmanager
import sqlite3
from backend.temporal_state.store import TemporalStore


class MemoryTemporalStore(TemporalStore):
    def __init__(self, db_path, evidence_root):
        self.connection = sqlite3.connect(':memory:', timeout=0, isolation_level=None)
        self.connection.execute('PRAGMA foreign_keys=ON')
        try:
            super().__init__(db_path, evidence_root)
        except BaseException:
            self.connection.close()
            raise

    @contextmanager
    def writer(self):
        yield self.connection

    @contextmanager
    def reader(self):
        self.connection.execute('PRAGMA query_only=ON')
        try:
            yield self.connection
        finally:
            self.connection.execute('PRAGMA query_only=OFF')

    def close(self):
        self.connection.close()
