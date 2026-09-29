"""Check-only pytest plugin: emulate the full session's address-space baseline (F2).

Not a harness component and never loaded in a qualification run. The
targeted F2 verification cannot reproduce the full-suite session in
isolation, so this plugin reserves ``REL5_SESSION_BALLAST_BYTES`` of address
space at session start (a touched ``bytearray`` held for the session) to
place the pytest process at a disclosed baseline before the boundary node
runs. RED: ballast + 512 MiB soft limit -> the node's MemoryError reproduces.
GREEN: same ballast + the node-specific allowance adapter -> the node passes.
The ballast size and the process's VmSize after allocation are written to
``REL5_SESSION_BALLAST_EVIDENCE`` (a file path) so the emulated baseline is
part of the retained evidence.
"""
import json
import os
from pathlib import Path

_HOLD = []


def _vm():
    fields = {}
    for line in Path('/proc/self/status').read_text().splitlines():
        key, _, value = line.partition(':')
        if key in ('VmPeak', 'VmSize', 'VmRSS'):
            fields[key] = int(value.split()[0]) * 1024
    return fields


def pytest_sessionstart(session):
    size = int(os.environ['REL5_SESSION_BALLAST_BYTES'])
    before = _vm()
    block = bytearray(size)
    for offset in range(0, size, 4096):   # touch pages so RSS reflects the baseline too
        block[offset] = 1
    _HOLD.append(block)
    evidence = os.environ.get('REL5_SESSION_BALLAST_EVIDENCE')
    if evidence:
        with Path(evidence).open('x') as stream:
            json.dump(dict(ballast_bytes=size, before=before, after=_vm()), stream, sort_keys=True)
