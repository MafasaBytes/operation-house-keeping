"""Prepared targeted checks for the v4 external reporter (not collected by pytest).

New cases cover captured-output retention: stdout/stderr per phase, fd-level
subprocess stderr (the ``git fetch`` shape), exact node/phase attribution with
unique markers, no retention for passing nodes, and per-section / per-node
overflow. Regression cases reuse the committed v3 check module's sources and
comparators unchanged (oversized identities, skips, interruption, cap), run
under v4. A v3 RED on the capture case shows v3 retains no sections.

The caller owns reservation, capture controller and ledger; this module only
writes below the case directory it is given. Nothing has been executed at
preparation time.
"""
from pathlib import Path

import slice5_reporter_v3_checks as v3checks

CAPTURE = r'''
import subprocess, sys, pytest
@pytest.fixture
def noisy_setup():
    print("MARK-A-SETUP-OUT"); sys.stderr.write("MARK-A-SETUP-ERR\n"); raise RuntimeError("setup defect")
def test_call_streams():
    print("MARK-B-CALL-OUT"); sys.stderr.write("MARK-B-CALL-ERR\n"); assert False
def test_subprocess_stderr():
    subprocess.run([sys.executable, "-c", "import sys; sys.stderr.write('MARK-C-FD-ERR\\n')"])
    assert False
def test_setup_error(noisy_setup):
    pass
def test_passing_output():
    print("MARK-D-PASS-OUT")
'''

OVERFLOW = r'''
import logging, sys
def test_overflow():
    sys.stdout.write("o" * 100000); sys.stderr.write("e" * 100000)
    logging.getLogger("overflow").warning("l" * 100000)
    assert False
'''

# node name -> {section title: marker that must appear}; markers must appear nowhere else.
CAPTURE_EXPECT = {
    'test_call_streams': ('failed', {'Captured stdout call': 'MARK-B-CALL-OUT', 'Captured stderr call': 'MARK-B-CALL-ERR'}),
    'test_subprocess_stderr': ('failed', {'Captured stderr call': 'MARK-C-FD-ERR'}),
    'test_setup_error': ('errored', {'Captured stdout setup': 'MARK-A-SETUP-OUT', 'Captured stderr setup': 'MARK-A-SETUP-ERR'}),
    'test_passing_output': ('passed', {}),
}
MARKERS = ['MARK-A-SETUP-OUT', 'MARK-A-SETUP-ERR', 'MARK-B-CALL-OUT', 'MARK-B-CALL-ERR', 'MARK-C-FD-ERR', 'MARK-D-PASS-OUT']

CASES = {
    'capture': (CAPTURE, 4 * 1048576),
    'overflow': (OVERFLOW, 4 * 1048576),
}
REGRESSION = ('oversized', 'skips', 'interrupted', 'cap')


def prepare(case_dir, name):
    case_dir = Path(case_dir)
    case_dir.mkdir()
    source = CASES[name][0] if name in CASES else v3checks.CASES[name][0]
    (case_dir / ('test_' + name + '.py')).write_text(source)
    return case_dir


def report_limit(name):
    return CASES[name][1] if name in CASES else v3checks.CASES[name][1]


def _by_node(result_dir):
    import bounded_pytest_runner_v4 as v4
    ids = v4.identities(Path(result_dir) / 'collection.jsonl')
    sections = v4.captured_sections(Path(result_dir) / 'results.jsonl')
    names = {index: text.split('::')[-1] for index, text in ids.items()}
    grouped = {}
    for (index, when, number), value in sections.items():
        grouped.setdefault(names[index], []).append(value)
    return names, grouped


def compare_capture(result, result_dir, categories):
    """categories: node name -> category from the parsed v4 report."""
    names, grouped = _by_node(result_dir)
    checks = {'complete': not result['incomplete_evidence'],
              'no_protocol_defects': not result['protocol_defects'],
              'capture_mode_recorded': result.get('capture_mode') not in (None, 'no', 'unknown')}
    for node, (category, expected) in CAPTURE_EXPECT.items():
        values = grouped.get(node, [])
        checks['category_' + node] = categories.get(node) == category
        for title, marker in expected.items():
            checks['%s:%s' % (node, title)] = any(v['title'] == title and v['text'] is not None
                                                  and marker in v['text'] for v in values)
        foreign = [m for m in MARKERS if m not in expected.values()]
        checks['no_foreign_markers_' + node] = not any(m in (v['text'] or '') for v in values for m in foreign)
        checks['no_untruncated_digest_mismatch_' + node] = all(
            v['section_truncated'] or v['section_bytes'] == v['retained_bytes'] for v in values)
    checks['passing_node_retains_nothing'] = not grouped.get('test_passing_output')
    return checks


def compare_overflow(result, result_dir):
    import bounded_pytest_runner_v4 as v4
    names, grouped = _by_node(result_dir)
    values = grouped.get('test_overflow', [])
    titles = {v['title']: v for v in values}
    retained = sum(v['retained_bytes'] for v in values)
    return {'three_sections': {'Captured stdout call', 'Captured stderr call', 'Captured log call'} <= set(titles),
            'all_flagged_truncated': all(v['section_truncated'] for v in values) and len(values) >= 3,
            'full_lengths_recorded': all(v['section_bytes'] >= 100000 for v in values),
            'per_section_bound': all(v['retained_bytes'] <= v4.MAX_SECTION_BYTES for v in values),
            'per_node_bound': retained <= v4.MAX_SECTION_BYTES_PER_NODE,
            'truncation_counted': result['captured_section_truncations'] >= 3,
            'failure_retained': result['counts'].get('failed') == 1,
            'complete': not result['incomplete_evidence']}


def compare_regression(name, result, collection_path):
    return v3checks.compare(name, result, collection_path)


def compare_v3_red(result_dir):
    """v3 RED: the capture case's reports carry no captured-section events.

    Marker absence is not checked: pytest's long traceback quotes the test
    source, which contains the marker literals, so they can appear in v3's
    longrepr without any captured output having been retained.
    """
    text = (Path(result_dir) / 'results.jsonl').read_bytes()
    return {'v3_retains_no_sections': b'"event":"section"' not in text}
