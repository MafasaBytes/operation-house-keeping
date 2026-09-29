"""Versioned external-parent pytest reporter, revision 3; v2 is retained unchanged.

Only the parent opens and writes report files. The pytest child publishes
bounded events through an inherited anonymous shared-memory slot; hooks touch
memory only. The caller must reserve all report bytes/files before this runner
starts.

Differences from v2, and why (Slice 5 F-full, ledger record 3234):

* Identity is published once, in the collection stream. An identity whose
  event would not fit one slot is split into ordered base64 chunks of its
  UTF-8 bytes, each carrying the identity SHA-256, byte length and chunk
  position, so the parent reconstructs and verifies it exactly. Result events
  carry only the collection index and identity digest, so no event grows with
  identity length. (v2 repeated the identity per phase; a 40,111-byte identity
  produced a 160,727-byte event and crashed pytest.)
* Diagnostics are chunked the same way up to MAX_DIAGNOSTIC_BYTES per phase.
  A longer diagnostic keeps its first MAX_DIAGNOSTIC_BYTES and records
  ``diagnostic_truncated`` plus the full byte length and SHA-256; truncation is
  disclosed separately and never alters identity or outcome.
* Lifecycle uses ``pytest_runtest_logstart``, which pytest emits for every
  executed item including marker-skipped ones, and one terminal event after
  the teardown report. Completeness means every collected index has exactly
  one terminal outcome; setup-skipped items need no call phase. (v2 counted
  ``pytest_runtest_setup``, which the skipping plugin pre-empts.)
* Hooks never raise into pytest. A publication failure is counted, the reason
  retained, and ``session.shouldstop`` set so pytest stops between items;
  unreported items are then incomplete or never executed, never passes.
* The parent classifies every collected index as passed, failed, errored,
  skipped, incomplete (logstart without terminal) or never_executed, and
  cross-checks the child's own counts.
"""

import base64
import ctypes
import hashlib
import json
import mmap
import os
from pathlib import Path
import signal
import sys
import time

MAX_EVENT_BYTES = 65536
CHUNK_BYTES = 24576            # raw bytes per chunk; base64 is 32,768 ASCII bytes
MAX_DIAGNOSTIC_BYTES = 131072  # per phase, retained in chunks
MAX_REPORT_BYTES = 64 * 1024 * 1024
MAX_LISTED = 64                # bounded index lists in summaries
STOP_GRACE_SECONDS = 120
STATE = 0
LENGTH = 1
DATA = 5
TERMINAL_WHEN = 'teardown'


def wire(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True) + '\n').encode('ascii')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


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
            raise RuntimeError('external recorder stopped')
        self.memory[LENGTH:DATA] = len(payload).to_bytes(4, 'big')
        self.memory[DATA:DATA + len(payload)] = payload
        self.memory[STATE] = 1
        while self.memory[STATE] == 1:
            pass
        if self.memory[STATE] != 0:
            raise RuntimeError('external recorder stopped')


def chunks(raw):
    count = max(1, -(-len(raw) // CHUNK_BYTES))
    for position in range(count):
        piece = raw[position * CHUNK_BYTES:(position + 1) * CHUNK_BYTES]
        yield position, count, base64.b64encode(piece).decode('ascii')


class MemoryOnlyPlugin:
    def __init__(self, slot):
        self.slot = slot
        self.index = {}
        self.open = {}
        self.logstarted = 0
        self.terminal = 0
        self.collection_errors = 0
        self.unknown_nodes = 0
        self.failures = []
        self.truncated = 0
        self.session = None

    # -- publication never raises into pytest --------------------------------
    def _publish(self, value):
        try:
            self.slot.publish(value)
            return True
        except Exception as exc:  # recorder stopped, cap reached, or defect
            if len(self.failures) < MAX_LISTED:
                self.failures.append('%s: %s' % (type(exc).__name__, exc))
            else:
                self.failures[-1] = 'further reporting failures suppressed'
            if self.session is not None:
                self.session.shouldstop = 'bounded reporter publication failure'
            return False

    def _identity(self, stream, event, index, text):
        raw = text.encode('utf-8', 'surrogatepass')
        base = {'stream': stream, 'index': index, 'node_sha256': digest(raw),
                'node_bytes': len(raw)}
        whole = dict(base, event=event, node=text)
        if len(wire(whole)) <= MAX_EVENT_BYTES:
            return self._publish(whole)
        ok = True
        for position, count, data in chunks(raw):
            ok = self._publish(dict(base, event=event + '_chunk', chunk=position,
                                    chunks=count, data_b64=data)) and ok
        return ok

    # -- collection ----------------------------------------------------------
    def pytest_sessionstart(self, session):
        self.session = session

    def pytest_collectreport(self, report):
        try:
            if report.failed:
                self.collection_errors += 1
                text = str(report.longrepr)
                self._identity('collection', 'collection_error', self.collection_errors - 1,
                               (report.nodeid or '<root>') + '\n' + text[:MAX_DIAGNOSTIC_BYTES])
        except Exception as exc:
            self.failures.append('collectreport: %r' % (exc,))

    def pytest_collection_finish(self, session):
        try:
            for position, item in enumerate(session.items):
                self.index[item.nodeid] = position
                self._identity('collection', 'collected', position, item.nodeid)
            self._publish({'stream': 'collection', 'event': 'collection_complete',
                           'collected': len(session.items), 'durable': True})
        except Exception as exc:
            self.failures.append('collection_finish: %r' % (exc,))

    # -- lifecycle -----------------------------------------------------------
    def _ref(self, nodeid):
        position = self.index.get(nodeid)
        raw = nodeid.encode('utf-8', 'surrogatepass')
        if position is None:
            self.unknown_nodes += 1
        return {'index': position, 'node_sha256': digest(raw)}

    def pytest_runtest_logstart(self, nodeid, location):
        try:
            ref = self._ref(nodeid)
            self.open[nodeid] = []
            self.logstarted += 1
            # Parent fsync/ack completes before setup proceeds.
            self._publish(dict(ref, stream='results', event='logstart', durable=True))
        except Exception as exc:
            self.failures.append('logstart: %r' % (exc,))

    def pytest_runtest_logreport(self, report):
        try:
            ref = self._ref(report.nodeid)
            phase = dict(ref, stream='results', event='phase', when=report.when,
                         outcome=report.outcome, duration=report.duration,
                         wasxfail=bool(getattr(report, 'wasxfail', False)))
            if report.failed or report.skipped:
                raw = str(report.longrepr).encode('utf-8', 'surrogatepass')
                kept = raw[:MAX_DIAGNOSTIC_BYTES]
                phase.update(diagnostic_bytes=len(raw), diagnostic_sha256=digest(raw),
                             diagnostic_truncated=len(kept) < len(raw))
                if len(kept) < len(raw):
                    self.truncated += 1
                self._publish(phase)
                for position, count, data in chunks(kept):
                    self._publish(dict(ref, stream='results', event='diagnostic_chunk',
                                       when=report.when, chunk=position, chunks=count,
                                       data_b64=data))
            else:
                self._publish(phase)
            self.open.setdefault(report.nodeid, []).append((report.when, report.outcome))
            if report.when == TERMINAL_WHEN:
                phases = self.open.pop(report.nodeid)
                self.terminal += 1
                self._publish(dict(ref, stream='results', event='terminal',
                                   outcome=classify(phases), durable=True))
        except Exception as exc:
            self.failures.append('logreport: %r' % (exc,))

    def finish(self, pytest_exit):
        pending = sorted(p for p in (self.index.get(n) for n in self.open) if p is not None)
        return self._publish({'stream': 'results', 'event': 'session_complete',
                              'pytest_exit': int(pytest_exit), 'collected': len(self.index),
                              'logstarted': self.logstarted, 'terminal': self.terminal,
                              'pending_count': len(pending), 'pending_indices': pending[:MAX_LISTED],
                              'collection_errors': self.collection_errors,
                              'unknown_nodes': self.unknown_nodes,
                              'reporting_failures': self.failures,
                              'diagnostic_truncations': self.truncated, 'durable': True})


def classify(phases):
    """Terminal outcome from (when, outcome) phase pairs; setup-skips need no call."""
    failed = [when for when, outcome in phases if outcome == 'failed']
    if failed:
        return 'failed' if failed[0] == 'call' else 'errored'
    if any(outcome == 'skipped' for _, outcome in phases):
        return 'skipped'
    return 'passed'


class ParentState:
    def __init__(self):
        self.identities = {}
        self.pieces = {}
        self.collected_declared = None
        self.collection_errors = 0
        self.logstart = set()
        self.terminal = {}
        self.defects = []
        self.truncations = 0
        self.summary = None

    def defect(self, text):
        if len(self.defects) < MAX_LISTED:
            self.defects.append(text)

    def accept(self, event):
        kind = event.get('event')
        if kind == 'collected':
            raw = event['node'].encode('utf-8', 'surrogatepass')
            if digest(raw) != event['node_sha256'] or len(raw) != event['node_bytes']:
                self.defect('identity digest mismatch at %s' % event['index'])
            self._identity(event['index'], event['node_sha256'])
        elif kind == 'collected_chunk':
            key = (event['index'], event['node_sha256'], event['node_bytes'], event['chunks'])
            part = self.pieces.setdefault(key, {})
            if event['chunk'] in part:
                self.defect('duplicate identity chunk at %s' % event['index'])
            part[event['chunk']] = base64.b64decode(event['data_b64'], validate=True)
            if len(part) == event['chunks']:
                raw = b''.join(part[i] for i in range(event['chunks']))
                del self.pieces[key]
                if digest(raw) != event['node_sha256'] or len(raw) != event['node_bytes']:
                    self.defect('reassembled identity mismatch at %s' % event['index'])
                self._identity(event['index'], event['node_sha256'])
        elif kind in ('collection_error', 'collection_error_chunk'):
            if kind == 'collection_error' or event['chunk'] == 0:
                self.collection_errors += 1
        elif kind == 'collection_complete':
            self.collected_declared = event['collected']
        elif kind == 'logstart':
            self._known(event)
            self.logstart.add(event['index'])
        elif kind == 'phase':
            self._known(event)
            if event.get('diagnostic_truncated'):
                self.truncations += 1
        elif kind == 'terminal':
            self._known(event)
            if event['index'] in self.terminal:
                self.defect('duplicate terminal outcome at %s' % event['index'])
            self.terminal[event['index']] = event['outcome']
        elif kind == 'session_complete':
            self.summary = event

    def _identity(self, index, sha):
        if index in self.identities:
            self.defect('duplicate collection index %s' % index)
        self.identities[index] = sha

    def _known(self, event):
        if event.get('index') is None or self.identities.get(event['index']) != event.get('node_sha256'):
            self.defect('result for unknown or mismatched identity: %s' % event.get('index'))

    def classification(self):
        counts = dict.fromkeys(('passed', 'failed', 'errored', 'skipped',
                                'incomplete', 'never_executed'), 0)
        incomplete, never = [], []
        for index in sorted(self.identities):
            if index in self.terminal:
                counts[self.terminal[index]] += 1
            elif index in self.logstart:
                counts['incomplete'] += 1; incomplete.append(index)
            else:
                counts['never_executed'] += 1; never.append(index)
        return counts, incomplete, never


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
            os._exit(0 if plugins[0].finish(status) else 93)
        except BaseException:
            os._exit(92)

    state = ParentState()
    total = 0
    recorder_error = None
    child_status = None
    stopped_at = None
    killed_after_stop = False
    try:
        while True:
            if slot.memory[STATE] == 1:
                size = int.from_bytes(slot.memory[LENGTH:DATA], 'big')
                if not 0 < size <= MAX_EVENT_BYTES or total + size > report_limit:
                    recorder_error = 'report_limit_exceeded' if 0 < size <= MAX_EVENT_BYTES \
                        else 'invalid_event_size'
                    slot.memory[STATE] = 2
                    stopped_at = time.monotonic()
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
                state.accept(event)
                slot.memory[STATE] = 0
            else:
                if child_status is not None:
                    break
                reaped, status = os.waitpid(pid, os.WNOHANG)
                if reaped == pid:
                    child_status = os.waitstatus_to_exitcode(status)
                    if slot.memory[STATE] != 1:
                        break
                    continue
                time.sleep(0.001)
    except BaseException as exc:
        recorder_error = recorder_error or repr(exc)
        slot.memory[STATE] = 2
        stopped_at = stopped_at or time.monotonic()
    finally:
        if child_status is None:
            # A stopped recorder makes every later publish fail fast; the child
            # stops between items. Bounded grace, then kill.
            while child_status is None:
                reaped, status = os.waitpid(pid, os.WNOHANG)
                if reaped == pid:
                    child_status = os.waitstatus_to_exitcode(status)
                elif stopped_at is not None and time.monotonic() - stopped_at > STOP_GRACE_SECONDS:
                    try: os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError: pass
                    killed_after_stop = True
                    _, status = os.waitpid(pid, 0)
                    child_status = os.waitstatus_to_exitcode(status)
                else:
                    time.sleep(0.01)
        for fd in (collection_fd, results_fd):
            try: os.fsync(fd)
            except OSError as exc: recorder_error = recorder_error or repr(exc)
            os.close(fd)

    counts, incomplete, never = state.classification()
    summary = state.summary
    reasons = []
    if recorder_error: reasons.append('recorder: ' + recorder_error)
    if killed_after_stop: reasons.append('child killed after recorder stop grace')
    if child_status != 0: reasons.append('child exit %s' % child_status)
    if summary is None: reasons.append('no session summary')
    else:
        if summary['pytest_exit'] not in (0, 1): reasons.append('pytest exit %s' % summary['pytest_exit'])
        if summary['reporting_failures']: reasons.append('child reporting failures')
        if summary['unknown_nodes']: reasons.append('results for uncollected nodes')
        if (summary['collected'], summary['terminal']) != (len(state.identities), len(state.terminal)):
            reasons.append('child and parent counts disagree')
    if state.collected_declared != len(state.identities): reasons.append('collection stream incomplete')
    if state.pieces: reasons.append('unreassembled identity chunks')
    if state.collection_errors: reasons.append('collection errors')
    if state.defects: reasons.append('protocol defects')
    if incomplete or never: reasons.append('collected nodes without terminal outcome')
    return {'child_exit': child_status, 'report_bytes': total, 'recorder_error': recorder_error,
            'summary': summary, 'counts': dict(counts, collected=len(state.identities)),
            'incomplete_indices': incomplete[:MAX_LISTED], 'never_executed_count': len(never),
            'first_never_executed': never[:MAX_LISTED], 'protocol_defects': state.defects,
            'diagnostic_truncations': state.truncations, 'incomplete_reasons': reasons,
            'incomplete_evidence': bool(reasons)}


def identities(collection_path):
    """Recover every collected identity (index -> text) from a retained stream."""
    found, pieces = {}, {}
    for line in Path(collection_path).read_bytes().splitlines():
        event = json.loads(line)
        if event['event'] == 'collected':
            found[event['index']] = event['node']
        elif event['event'] == 'collected_chunk':
            part = pieces.setdefault(event['index'], {})
            part[event['chunk']] = base64.b64decode(event['data_b64'], validate=True)
            if len(part) == event['chunks']:
                raw = b''.join(part[i] for i in range(event['chunks']))
                if digest(raw) != event['node_sha256']:
                    raise ValueError('identity digest mismatch at %s' % event['index'])
                found[event['index']] = raw.decode('utf-8', 'surrogatepass')
    return found


if __name__ == '__main__':
    raise SystemExit('Import run() from a separately reserved external controller')
