"""Versioned external-parent pytest reporter; the previous runner is retained.

Only the parent opens and writes report files. The pytest child publishes bounded
events through an inherited anonymous shared-memory slot; hooks touch memory
only. The caller must reserve all report bytes/files before this runner starts.
"""

import ctypes
import json
import mmap
import os
from pathlib import Path
import signal
import sys
import time

MAX_EVENT_BYTES = 65536
MAX_DIAGNOSTIC_BYTES = 32768
MAX_REPORT_BYTES = 24 * 1024 * 1024
STATE = 0
LENGTH = 1
DATA = 5


def wire(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=False) + '\n').encode('utf-8')


class MemorySlot:
    def __init__(self):
        self.memory = mmap.mmap(-1, DATA + MAX_EVENT_BYTES,
                                flags=mmap.MAP_SHARED,
                                prot=mmap.PROT_READ | mmap.PROT_WRITE)
        self.memory[STATE] = 0

    def publish(self, value):
        payload = wire(value)
        if len(payload) > MAX_EVENT_BYTES:
            raise ValueError('report event exceeds memory slot')
        while self.memory[STATE] == 1:
            pass
        if self.memory[STATE] != 0:
            raise RuntimeError('external recorder failed')
        self.memory[LENGTH:DATA] = len(payload).to_bytes(4, 'big')
        self.memory[DATA:DATA + len(payload)] = payload
        self.memory[STATE] = 1
        while self.memory[STATE] == 1:
            pass
        if self.memory[STATE] != 0:
            raise RuntimeError('external recorder failed')


class MemoryOnlyPlugin:
    def __init__(self, slot):
        self.slot = slot
        self.pending = {}
        self.started = 0
        self.completed = 0
        self.truncated = 0

    def pytest_collection_finish(self, session):
        for item in session.items:
            self.slot.publish({'stream': 'collection', 'event': 'collected',
                               'node': item.nodeid})

    def pytest_runtest_setup(self, item):
        # Parent fsync/ack completes before fixture setup proceeds.
        self.slot.publish({'stream': 'results', 'event': 'started',
                           'node': item.nodeid, 'durable': True})
        self.started += 1

    def pytest_runtest_logreport(self, report):
        row = {'node': report.nodeid, 'when': report.when,
               'outcome': report.outcome, 'duration': report.duration}
        if report.failed or report.skipped:
            diagnostic = str(report.longrepr)
            row['longrepr'] = diagnostic[:MAX_DIAGNOSTIC_BYTES]
            if len(diagnostic) > MAX_DIAGNOSTIC_BYTES:
                row['diagnostic_truncated'] = True
                self.truncated += 1
        self.pending.setdefault(report.nodeid, []).append(row)
        if report.when == 'teardown':
            phases = self.pending.pop(report.nodeid)
            # Report files are written by the parent only after teardown.
            self.slot.publish({'stream': 'results', 'event': 'node_complete',
                               'node': report.nodeid, 'phases': phases,
                               'durable': True})
            self.completed += 1

    def finish(self, pytest_exit):
        self.slot.publish({'stream': 'results', 'event': 'session_complete',
                           'pytest_exit': int(pytest_exit),
                           'started': self.started, 'completed': self.completed,
                           'pending_nodes': sorted(self.pending),
                           'truncated_diagnostics': self.truncated,
                           'durable': True})


def run(argv, collection_path, results_path, *, report_limit=MAX_REPORT_BYTES,
        adapter_roots=None):
    """Run one separately authorized pytest invocation and retain its protocol."""
    if type(report_limit) is not int or not 0 < report_limit <= MAX_REPORT_BYTES:
        raise ValueError('invalid pre-reserved report limit')
    for name in (collection_path, results_path):
        path = Path(name)
        if not path.parent.is_dir() or path.exists() or path.is_symlink():
            raise ValueError('report path must be absent under an existing directory')
    slot = MemorySlot()
    collection_fd = os.open(collection_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    results_fd = os.open(results_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    pid = os.fork()
    if pid == 0:
        os.close(collection_fd)
        os.close(results_fd)
        try:
            # Linux parent-death signal prevents an orphan from spinning if the
            # external recorder process disappears during a hook handshake.
            libc = ctypes.CDLL(None, use_errno=True)
            if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:
                raise OSError(ctypes.get_errno(), 'parent-death signal setup failed')
            if os.getppid() == 1:
                os._exit(92)
            import pytest
            plugins = [MemoryOnlyPlugin(slot)]
            if adapter_roots is not None:
                from slice5_g_app_root_adapter import RootAdapter
                plugins.append(RootAdapter(*adapter_roots))
            status = pytest.main(argv, plugins=plugins)
            plugins[0].finish(status)
            os._exit(0)
        except BaseException:
            os._exit(92)

    total = 0
    summary = None
    recorder_error = None
    child_status = None
    try:
        while True:
            if slot.memory[STATE] == 1:
                size = int.from_bytes(slot.memory[LENGTH:DATA], 'big')
                if not 0 < size <= MAX_EVENT_BYTES or total + size > report_limit:
                    recorder_error = 'report limit exceeded before write'
                    slot.memory[STATE] = 2
                    try: os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError: pass
                    break
                payload = bytes(slot.memory[DATA:DATA + size])
                event = json.loads(payload)
                fd = collection_fd if event['stream'] == 'collection' else results_fd
                view = memoryview(payload)
                while view:
                    view = view[os.write(fd, view):]
                total += size
                if event.get('durable'):
                    os.fsync(fd)
                if event.get('event') == 'session_complete':
                    summary = event
                slot.memory[STATE] = 0
                if child_status is not None:
                    break
            else:
                if child_status is not None:
                    break
                reaped, status = os.waitpid(pid, os.WNOHANG)
                if reaped == pid:
                    child_status = os.waitstatus_to_exitcode(status)
                    if slot.memory[STATE] != 1:
                        break
                time.sleep(0.001)
    except BaseException as exc:
        recorder_error = repr(exc)
        slot.memory[STATE] = 2
        try: os.kill(pid, signal.SIGKILL)
        except ProcessLookupError: pass
    finally:
        if child_status is None:
            _, status = os.waitpid(pid, 0)
            child_status = os.waitstatus_to_exitcode(status)
        for fd in (collection_fd, results_fd):
            try: os.fsync(fd)
            except OSError as exc: recorder_error = repr(exc)
            os.close(fd)
    incomplete = bool(recorder_error or child_status != 0 or summary is None or
                      summary.get('pending_nodes') or
                      summary.get('truncated_diagnostics') or
                      summary.get('started') != summary.get('completed'))
    return {'child_exit': child_status, 'report_bytes': total,
            'recorder_error': recorder_error, 'summary': summary,
            'incomplete_evidence': incomplete}


if __name__ == '__main__':
    raise SystemExit('Import run() from a separately reserved external controller')
