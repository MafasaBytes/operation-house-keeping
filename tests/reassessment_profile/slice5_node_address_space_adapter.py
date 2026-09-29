"""Test-only, node-specific address-space allowance for the pytest process (F2).

Owner-directed preparation (2026-09-29, retry result
32f9594b1aab2594f00c69e833f8c06bf4d6f9c351795a647deb097b81b5e2bd, finding F2):
``tests/transition_assessment/test_preflight.py::
test_t64_t69_exact_production_byte_node_and_depth_boundaries`` builds two
134,217,726/134,217,727-byte strings and admits them through the production
preflight; under the harness's 512 MiB soft RLIMIT_AS the full session's
accumulated baseline left no room and the test raised MemoryError. The test,
its assertion and the production limit are unchanged.

This plugin raises the pytest process's *soft* RLIMIT_AS only while an
explicitly named node runs, to an explicit finite value no greater than the
inherited hard ceiling, and restores the previous soft limit afterwards
(teardown is a pluggy wrapper so restoration always follows pytest's own
teardown). No other node, no application child and no production guard is
affected; children spawned during the named node inherit the raised soft
limit, which the evidence record discloses.

Configuration (environment, read once at session start):

* ``REL5_NODE_AS_LIMITS``: JSON object mapping exact node ids to soft-limit
  bytes. Each value must satisfy inherited_soft <= value <= inherited_hard,
  and the inherited hard limit must be finite. Unset: the plugin is inert.
* ``REL5_NODE_AS_EVIDENCE_DIR``: directory for one JSON record per named
  node (inherited limits, applied limit, VmPeak/VmHWM before and after the
  node, restoration status). Unset: no evidence is written.
"""
import json
import os
import resource
from pathlib import Path

import pytest

LIMITS_ENV = 'REL5_NODE_AS_LIMITS'
EVIDENCE_ENV = 'REL5_NODE_AS_EVIDENCE_DIR'
_STATE = {}


def _vm():
    fields = {}
    for line in Path('/proc/self/status').read_text().splitlines():
        key, _, value = line.partition(':')
        if key in ('VmPeak', 'VmSize', 'VmHWM', 'VmRSS'):
            fields[key] = int(value.split()[0]) * 1024
    return fields


def pytest_sessionstart(session):
    raw = os.environ.get(LIMITS_ENV)
    if raw is None:
        return
    limits = json.loads(raw)
    if not isinstance(limits, dict) or not all(
            type(v) is int and v > 0 for v in limits.values()):
        raise ValueError('REL5_NODE_AS_LIMITS must map node ids to positive integers')
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    if hard == resource.RLIM_INFINITY:
        raise ValueError('node address-space allowance requires a finite inherited hard limit')
    for node, value in limits.items():
        if not soft <= value <= hard:
            raise ValueError('allowance for %s outside inherited (soft, hard)' % node)
    _STATE['limits'] = limits
    _STATE['inherited'] = (soft, hard)
    _STATE['evidence'] = os.environ.get(EVIDENCE_ENV)
    _STATE['records'] = {}


def pytest_runtest_setup(item):
    limits = _STATE.get('limits') or {}
    if item.nodeid not in limits:
        return
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    record = dict(node=item.nodeid, inherited=[soft, hard], applied=limits[item.nodeid],
                  before=_vm(), restored=False)
    resource.setrlimit(resource.RLIMIT_AS, (limits[item.nodeid], hard))
    record['effective'] = list(resource.getrlimit(resource.RLIMIT_AS))
    _STATE['records'][item.nodeid] = record


@pytest.hookimpl(wrapper=True)
def pytest_runtest_teardown(item):
    record = (_STATE.get('records') or {}).get(item.nodeid)
    if record is None:
        return (yield)
    try:
        result = yield
    finally:
        record['after'] = _vm()
        try:
            resource.setrlimit(resource.RLIMIT_AS, (record['inherited'][0], record['inherited'][1]))
            record['restored'] = list(resource.getrlimit(resource.RLIMIT_AS)) == record['inherited']
        except Exception as exc:  # disclosed, never hidden
            record['restore_error'] = repr(exc)
        evidence = _STATE.get('evidence')
        if evidence:
            name = 'node-as-%02d.json' % (len(_STATE['records']))
            with (Path(evidence) / name).open('x') as stream:
                json.dump(record, stream, sort_keys=True)
    return result
