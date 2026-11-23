"""New companion recomputation; legacy owning semantics remain separate."""
import copy
import json
import pytest

from applications.bounded_decision_workflow import t1_calibration_gate as gate, t1_workflow as workflow
from applications.bounded_decision_workflow import checked_runtime as rt, t1_acquisition, t1_carrier
from applications.bounded_decision_workflow.t1_contracts import SimRefusal, canonical_bytes, sha
from applications.bounded_decision_workflow.checked_contracts import CheckedRefusal
from .calibration_fixtures import scenario, evaluate, verify, legacy_workflow, rehash_owner_result


@pytest.mark.parametrize('beta,relation,variable,expected', [
    ('10', 'support', None, 'blocked_calibration_counterexample'),
    ('0', 'support', 'var_' + '2' * 32, 'blocked_calibration_correspondence'),
    ('0', 'support', None, 'delegated_assessment'),
    ('0', 'opposition', None, 'delegated_assessment')])
def test_c10_c11_honest_branches_verify_replay_and_reverify(tmp_path, monkeypatch, beta, relation, variable, expected):
    spec = scenario(tmp_path, beta=beta, theta='50' if beta == '10' else '60.1',
                    relation=relation, actual_variable=variable)
    files = evaluate(spec, tmp_path)
    def forbidden(*args, **kw):
        raise AssertionError('verification/replay attempted acquisition')
    monkeypatch.setattr(t1_acquisition, 'produce', forbidden)
    monkeypatch.setattr(t1_carrier, 'Transport', forbidden)
    checked = verify(spec, files, tmp_path)
    assert checked['outcome']['conclusion']['gate_status'] == expected
    replay = workflow.replay_calibration_workflow(**spec['inputs'], workflow_files=files,
        workflow_pin=sha(files['workflow-receipt.json']), scratch=tmp_path / 'replay-scratch',
        output=tmp_path / 'replayed')
    old = gate.parse(files['workflow-receipt.json'], gate.OUTCOME)
    new = gate.parse(replay['workflow-receipt.json'], gate.OUTCOME)
    assert new['finding'] == old['finding']
    assert new['conclusion'] == old['conclusion']
    assert new['replay_of']['sha256'] == sha(files['workflow-receipt.json'])
    assert new['operation'] == 't1-workflow-replay'
    if beta == '10' or variable is not None:
        assert new['delegation']['status'] == 'not_run'
        assert not any(p.startswith('bundle/') for p in replay)
    else:
        assert replay['bundle/result.json'] == files['bundle/result.json']
        assert replay['bundle/trace.json'] == files['bundle/trace.json']
    verify(spec, replay, tmp_path, 'reverify-scratch')


@pytest.mark.parametrize('fault,code', [('finding', 'CALIBRATION_FINDING_MISMATCH'),
                                      ('pointer', 'CALIBRATION_FINDING_MISMATCH'),
                                      ('headline', 'CALIBRATION_OUTCOME_MISMATCH')])
def test_c12_rehashed_finding_or_summary_cannot_claim_permission(tmp_path, fault, code):
    spec = scenario(tmp_path, beta='10', theta='50')
    files = evaluate(spec, tmp_path)
    value = json.loads(files['workflow-receipt.json'])
    if fault == 'finding':
        value['finding']['comparisons'][0]['operands'][0]['normalized_value']['value'] = 'f' * 64
    elif fault == 'pointer':
        value['finding']['comparisons'][0]['operands'][0]['pointer'] += '/invented'
        gate.encode(value)  # structurally admissible, rejected by reconstruction below
    else:
        value['conclusion']['admissibility'] = 'permitted_under_declared_conditions'
    forged = dict(files, **{'workflow-receipt.json': canonical_bytes(value)})
    with pytest.raises(SimRefusal) as denied:
        verify(spec, forged, tmp_path)
    assert denied.value.code == code


def test_c12_delegated_false_result_fails_full_replay_even_if_legacy_verify_accepts(tmp_path):
    spec = scenario(tmp_path)
    files = evaluate(spec, tmp_path)
    bundle = {n: files['bundle/' + n] for n in rt.BUNDLE_NAMES}
    forged_b = rehash_owner_result(bundle)
    original_legacy = rt.verify(bundle_files=forged_b, request_pin=spec['inputs']['request_pin'],
                               authority_pin=spec['inputs']['authority_pin'], build=spec['inputs']['build'])
    assert original_legacy['downstream_result_not_replayed'] is True
    # Rebind only public B references/metadata, leaving input/scientific finding
    # unchanged, so the owning replay comparison is the discriminating guard.
    from .calibration_fixtures import preflight_finding
    ctx = preflight_finding(spec, tmp_path)
    value = gate.build_outcome(finding=ctx['finding'], preflight=ctx['preflight'],
        input_pins=ctx['input_pins'], bundle=forged_b)
    forged = {'bundle/' + n: w for n, w in forged_b.items()}
    forged['workflow-receipt.json'] = gate.encode(value)
    with pytest.raises(CheckedRefusal) as denied:
        verify(spec, forged, tmp_path)
    assert denied.value.code == 'DOWNSTREAM_REPLAY_MISMATCH'


@pytest.mark.parametrize('fault', ['extra-b', 'missing-a-closure', 'build', 'base', 'detached'])
def test_c16_package_context_is_required(tmp_path, fault):
    spec = scenario(tmp_path, beta='10', theta='50')
    files = evaluate(spec, tmp_path)
    if fault == 'extra-b':
        files['bundle/result.json'] = b'{}'
    elif fault == 'missing-a-closure':
        files.pop('receipt/admission-closure.json')
    elif fault == 'build':
        files['receipt/build.json'] += b' '
    elif fault == 'base':
        files['receipt/base-applicability.json'] += b' '
    else:
        files = {'workflow-receipt.json': files['workflow-receipt.json']}
    with pytest.raises((SimRefusal, CheckedRefusal)):
        verify(spec, files, tmp_path)


def test_c12_source_pin_substitution_is_not_a_finding(tmp_path):
    spec = scenario(tmp_path, beta='10', theta='50')
    files = evaluate(spec, tmp_path)
    spec['inputs']['manifest_pin'] = 'f' * 64
    with pytest.raises(SimRefusal):
        verify(spec, files, tmp_path)


def test_c15_legacy_f_and_direct_b_keep_only_original_guarantees(tmp_path):
    spec = scenario(tmp_path, beta='10', theta='50')
    wire, bundle = legacy_workflow(spec)
    legacy = workflow.verify_workflow(**spec['inputs'], workflow_wire=wire, workflow_pin=sha(wire),
        bundle_files=bundle, scratch=tmp_path / 'legacy-scratch')
    assert legacy['guarantee'] == 'producer-checked'
    assert json.loads(bundle['result.json'])['disposition'] == 'one_compatible'
    direct = rt.verify(bundle_files=bundle, request_pin=spec['inputs']['request_pin'],
        authority_pin=spec['inputs']['authority_pin'], build=spec['inputs']['build'])
    assert 'guarantee' not in direct
    with pytest.raises(SimRefusal):
        gate.parse(wire, gate.OUTCOME)


def test_c15_old_bound_producer_cannot_use_another_provider(tmp_path):
    from tests.checked_temperature.fixtures import TestDoubleBuild
    spec = scenario(tmp_path)
    spec['inputs']['build'] = TestDoubleBuild(marker='2')
    with pytest.raises(SimRefusal) as denied:
        evaluate(spec, tmp_path)
    assert denied.value.code == 'SIM_EDITION_NOT_PERMITTED'


def test_c16_removing_actual_a_from_committed_closure_is_admission_failure(tmp_path):
    spec = scenario(tmp_path, beta='10', theta='50')
    files = evaluate(spec, tmp_path)
    value = json.loads(files['receipt/admission-closure.json'])
    value['members'] = [m for m in value['members'] if m['sha256'] != spec['inputs']['authority_pin']]
    files['receipt/admission-closure.json'] = canonical_bytes(value)
    with pytest.raises(CheckedRefusal) as denied:
        verify(spec, files, tmp_path)
    assert denied.value.code == 'AUTHORITY_PIN_MISMATCH'


def test_c12_rehashed_resolvable_trace_fails_new_full_comparison(tmp_path):
    from tests.checked_temperature.fixtures import rehash_bundle
    from .calibration_fixtures import preflight_finding
    spec = scenario(tmp_path)
    files = evaluate(spec, tmp_path)
    bundle = {n: files['bundle/' + n] for n in rt.BUNDLE_NAMES}
    trace = json.loads(bundle['trace.json'])
    trace['entries'][0]['target'] = trace['entries'][1]['target']
    forged_b = rehash_bundle(dict(bundle, **{'trace.json': canonical_bytes(trace)}))
    assert rt.verify(bundle_files=forged_b, request_pin=spec['inputs']['request_pin'],
        authority_pin=spec['inputs']['authority_pin'], build=spec['inputs']['build'])['downstream_result_not_replayed']
    ctx = preflight_finding(spec, tmp_path)
    outcome = gate.build_outcome(finding=ctx['finding'], preflight=ctx['preflight'],
        input_pins=ctx['input_pins'], bundle=forged_b)
    forged = {'bundle/' + n: w for n, w in forged_b.items()}
    forged['workflow-receipt.json'] = gate.encode(outcome)
    with pytest.raises(CheckedRefusal) as denied:
        verify(spec, forged, tmp_path)
    assert denied.value.code == 'DOWNSTREAM_REPLAY_MISMATCH'


@pytest.mark.parametrize('original_is_replay', [False, True])
def test_delegated_operation_cannot_be_cross_labelled(tmp_path, original_is_replay):
    spec = scenario(tmp_path)
    files = evaluate(spec, tmp_path)
    origin = dict(kind=gate.OUTCOME, sha256=sha(files['workflow-receipt.json']))
    if original_is_replay:
        files = workflow.replay_calibration_workflow(**spec['inputs'], workflow_files=files,
            workflow_pin=origin['sha256'], scratch=tmp_path / 'replay-scratch', output=tmp_path / 'replay')
    value = json.loads(files['workflow-receipt.json'])
    value.update(operation='t1-reassessment-evaluate' if original_is_replay else 't1-workflow-replay',
                 replay_of=None if original_is_replay else origin)
    with pytest.raises(SimRefusal) as denied:
        verify(spec, dict(files, **{'workflow-receipt.json': canonical_bytes(value)}), tmp_path)
    assert (denied.value.code, denied.value.target) == ('CALIBRATION_OUTCOME_MISMATCH', '/calibration/invocation')


def test_distinct_policy_refs_survive_replay_and_cannot_be_interchanged(tmp_path):
    spec = scenario(tmp_path, assessment_policy='conditional', phase_kw={'no_review': ('reference_mapping',)})
    files = evaluate(spec, tmp_path)
    value = json.loads(files['workflow-receipt.json'])
    subjects = value['finding']['subjects']
    source, assessment = subjects['captured_policy'], subjects['assessment_policy']
    assert source != assessment and value['conclusion']['admissibility'] == 'conditional'
    replay = workflow.replay_calibration_workflow(**spec['inputs'], workflow_files=files,
        workflow_pin=sha(files['workflow-receipt.json']), scratch=tmp_path / 'scratch', output=tmp_path / 'replay')
    checked = verify(spec, replay, tmp_path)['outcome']
    assert checked['finding'] == value['finding'] and checked['conclusion'] == value['conclusion']
    subjects.update(captured_policy=assessment, assessment_policy=source)
    with pytest.raises(SimRefusal) as denied:
        verify(spec, dict(files, **{'workflow-receipt.json': canonical_bytes(value)}), tmp_path, 'swapped')
    assert denied.value.code == 'CALIBRATION_FINDING_MISMATCH'


@pytest.mark.parametrize('beta,extra,code', [
    ('10', 'bundle', 'CALIBRATION_PACKAGE_MISMATCH'), ('0', 'receipt', 'CALIBRATION_PACKAGE_MISMATCH'),
    ('10', 'receipt/unexpected', 'CALIBRATION_PACKAGE_MISMATCH'),
    ('0', 'PARTIAL', 'SIM_PUBLICATION_INCOMPLETE')])
def test_strict_companion_reader_rejects_directory_only_substitution(tmp_path, beta, extra, code):
    spec = scenario(tmp_path, beta=beta, theta='50' if beta == '10' else '60.1')
    files = evaluate(spec, tmp_path)
    root = tmp_path / 'evaluation'
    assert workflow.read_package(root, companion=True) == files
    (root / extra).mkdir()
    with pytest.raises(SimRefusal) as denied:
        workflow.read_package(root, companion=True)
    assert denied.value.code == code


def test_capture_accepts_exact_combined_limit_and_retains_actual_status(tmp_path):
    import sys
    from .test_calibration_native import _capture
    argv = [sys.executable, '-I', '-B', '-S', '-c', "import os; os.write(1,b'ab'); os.write(2,b'c'); os._exit(3)"]
    root = tmp_path / 'entry'
    assert _capture(root, argv, cap=3) == 3
    assert (root / 'stdout').read_bytes() == b'ab' and (root / 'stderr').read_bytes() == b'c'
    assert json.loads((root / 'argv.json').read_bytes()) == argv
    record = json.loads((root / 'capture.json').read_bytes())
    assert (record['status'], record['retained_bytes'], record['returncode'], record['signal']) == (
        'complete', 3, 3, None)


@pytest.mark.parametrize('mode', ['overflow', 'timeout'])
def test_incomplete_capture_never_returns_a_scientific_result(tmp_path, mode):
    import subprocess
    import sys
    from .test_calibration_native import _capture
    root = tmp_path / 'entry'
    program = ("import os; os.write(1,b'{}'); os.write(2,b'xxxx')" if mode == 'overflow'
               else 'import time; time.sleep(30)')
    argv = [sys.executable, '-I', '-B', '-S', '-c', program]
    with pytest.raises(AssertionError if mode == 'overflow' else subprocess.TimeoutExpired):
        _capture(root, argv, timeout=5 if mode == 'overflow' else 0.5, cap=4)
    record = json.loads((root / 'capture.json').read_bytes())
    assert record['status'] == ('truncated' if mode == 'overflow' else 'timeout')
    total = sum((root / stream).stat().st_size for stream in ('stdout', 'stderr'))
    assert total == record['retained_bytes'] <= 4
    if mode == 'overflow':
        assert total == 4
