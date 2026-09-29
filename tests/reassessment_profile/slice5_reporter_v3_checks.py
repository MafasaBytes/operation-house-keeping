"""Prepared targeted checks for the v3 external reporter (not collected by pytest).

Each case writes a small synthetic suite into a fresh case directory, runs it
through ``bounded_pytest_runner_v3.run`` (GREEN) and, where it demonstrates a
v2 defect, through the retained ``bounded_pytest_runner_v2.run`` (RED), and
compares the retained reports with the fixed expectations below. The observed
F-full identity check runs the real c321 node selection instead of a synthetic
suite. The caller owns the reservation, the capture controller and the ledger;
this module only writes below the case directory it is given.

Nothing here has been executed at preparation time.
"""
import json
from pathlib import Path

OBSERVED_SELECTION = ('tests/semantic_compatibility/test_remaining_matrix.py::'
                      'test_huge_and_deep_evidence_are_gated_without_crashing')
# From the F-full reconciliation (collection indices 4581 and 4582).
OBSERVED_IDENTITIES = {
    '92c269680e0f2808b1929adb3a9f21f5c10ce8b183a47daab82aa509edd1e412': 5111,
    '632b533fc487d070dee8ad6239ccdd5e7c7f720f82c5baaf29d80b6b44c59463': 40111,
}

OVERSIZED = '''
import pytest
@pytest.mark.parametrize("value", ["[" * 40000, "x" * 200000, "short"])
def test_identity(value):
    assert value
'''

SKIPS = '''
import pytest
@pytest.mark.skip(reason="marker skip")
def test_marker_skip(): pass
@pytest.mark.skipif(True, reason="conditional skip")
def test_conditional_skip(): pass
def test_runtime_skip(): pytest.skip("runtime skip")
@pytest.mark.xfail(reason="expected failure")
def test_xfail(): assert False
def test_plain_pass(): pass
'''

ORDINARY = '''
import pytest
@pytest.fixture
def broken_setup(): raise RuntimeError("setup defect")
@pytest.fixture
def broken_teardown():
    yield
    raise RuntimeError("teardown defect")
def test_pass(): assert 1 == 1
def test_fail(): assert 1 == 2
def test_setup_error(broken_setup): pass
def test_teardown_error(broken_teardown): pass
def test_long_diagnostic(): assert False, "d" * 300000
'''

INTERRUPTED = '''
import os, signal
def test_before(): pass
def test_killed(): os.kill(os.getpid(), signal.SIGKILL)
def test_after(): pass
'''

CAP = '''
import pytest
@pytest.mark.parametrize("n", range(50))
def test_many(n): pass
'''

# name: (source, report_limit, v3 expectation, v2 RED expectation or None)
CASES = {
    'oversized': (OVERSIZED, 4 * 1048576,
                  dict(counts=dict(collected=3, passed=3), complete=True, identity_contains=['[' * 40000, 'x' * 200000]),
                  dict(v2_incomplete=True)),
    'skips': (SKIPS, 1048576,
              dict(counts=dict(collected=5, passed=1, skipped=4), complete=True),
              dict(v2_incomplete=True)),
    'ordinary': (ORDINARY, 4 * 1048576,
                 dict(counts=dict(collected=5, passed=1, failed=2, errored=2), complete=True,
                      diagnostic_truncations=1),
                 None),
    'interrupted': (INTERRUPTED, 1048576,
                    dict(counts=dict(collected=3, passed=1, incomplete=1, never_executed=1), complete=False),
                    None),
    'cap': (CAP, 4096,
            dict(complete=False, recorder_error='report_limit_exceeded', no_passes_beyond_cap=True),
            None),
}


def prepare(case_dir, name):
    source = CASES[name][0]
    case_dir = Path(case_dir)
    case_dir.mkdir()
    (case_dir / ('test_' + name + '.py')).write_text(source)
    return case_dir


def compare(name, result, collection_path):
    """Return {check: bool} for one v3 GREEN result against its expectation."""
    import bounded_pytest_runner_v3 as v3
    expect = CASES[name][2]
    checks = {}
    for key, value in expect.get('counts', {}).items():
        checks['count_' + key] = result['counts'].get(key) == value
    if 'complete' in expect:
        checks['complete'] = (not result['incomplete_evidence']) == expect['complete']
    if 'diagnostic_truncations' in expect:
        checks['diagnostic_truncations'] = result['diagnostic_truncations'] == expect['diagnostic_truncations']
    if 'recorder_error' in expect:
        checks['recorder_error'] = result['recorder_error'] == expect['recorder_error']
    if expect.get('no_passes_beyond_cap'):
        checks['cap_fail_closed'] = result['counts']['passed'] < 50 and result['child_exit'] is not None
    recovered = v3.identities(collection_path)
    checks['identities_distinct'] = len(set(recovered.values())) == len(recovered)
    checks['identities_cover_collection'] = sorted(recovered) == list(range(len(recovered)))
    if 'identity_contains' in expect:
        checks['oversized_identities_exact'] = all(
            any(('[' + part + ']') in n for n in recovered.values()) for part in expect['identity_contains'])
    checks['no_protocol_defects'] = not result['protocol_defects']
    return checks


def compare_v2_red(name, result):
    """The retained v2 defect is reproduced when v2 reports incomplete evidence."""
    return {'v2_defect_reproduced': bool(result['incomplete_evidence'])}


def compare_observed(result, collection_path):
    import hashlib
    import bounded_pytest_runner_v3 as v3
    recovered = v3.identities(collection_path)
    digests = {hashlib.sha256(n.encode()).hexdigest(): len(n.encode()) for n in recovered.values()}
    return {'observed_identities_recovered': all(digests.get(k) == v for k, v in OBSERVED_IDENTITIES.items()),
            'all_terminal': result['counts']['collected'] == sum(
                result['counts'][k] for k in ('passed', 'failed', 'errored', 'skipped')),
            'complete': not result['incomplete_evidence'],
            'no_protocol_defects': not result['protocol_defects']}


if __name__ == '__main__':
    print(json.dumps(sorted(CASES)))
