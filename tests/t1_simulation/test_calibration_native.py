"""N-level opt-in checks of separately prepared, genuine current-build inputs.

No fixture inputs/authorities are constructed here. Default collection cannot
capture a provider or launch native commands. Later validation must explicitly
supply the approved manifest and resource controller; a skip is not evidence.
"""
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time
import sys
import pytest

pytestmark = pytest.mark.skipif(os.environ.get('C05_NATIVE_VALIDATION') != '1',
                               reason='separate native execution grant and coherent fixtures required')
CORE = ('false_support', 'false_opposition', 'positive_support', 'positive_opposition')
FLAGS = {'producer-package', 'expected-producer-manifest-pin', 'expected-target-pin',
         'expected-execution-authority-pin', 'expected-permission-pin', 'expected-prior-request-pin',
         'expected-prior-authority-pin', 'prior-bundle', 'handoff-package', 'expected-handoff-pin',
         'expected-request-pin', 'expected-authority-pin', 'objects-dir'}


@pytest.fixture(scope='module')
def native_inputs():
    from applications.bounded_decision_workflow.checked_runtime import ExecutableBuild
    from applications.bounded_decision_workflow.t1_contracts import sha
    path = Path(os.environ['C05_NATIVE_FIXTURE_MANIFEST'])
    assert path.is_file() and not path.is_symlink() and path.stat().st_size <= 65536
    with path.open('rb') as stream:
        wire = stream.read(65537)
    assert len(wire) <= 65536
    assert sha(wire) == os.environ['C05_NATIVE_FIXTURE_SHA256']
    value = json.loads(wire)
    assert value['schema'] == 'c05-companion-native-fixtures.v1'
    assert set(value['cases']) in (set(CORE), set(CORE) | {'correspondence_gap'})
    actual = ExecutableBuild().wire()  # genuine provider; no saved identity seam
    assert value['build_sha256'] == sha(actual)
    for args in value['cases'].values():
        assert set(args) == FLAGS
    for left, right in (('false_support', 'false_opposition'), ('positive_support', 'positive_opposition')):
        a, b = value['cases'][left], value['cases'][right]
        assert a['expected-producer-manifest-pin'] == b['expected-producer-manifest-pin']
        assert a['producer-package'] == b['producer-package']
        _check_review_twins(a, b, value['expected']['claim_sha256'])
        for pin in ('expected-request-pin', 'expected-authority-pin', 'expected-handoff-pin'):
            assert a[pin] != b[pin]
    return value


def _object(directory, digest):
    assert len(digest) == 64 and all(c in '0123456789abcdef' for c in digest)
    with (Path(directory) / digest).open('rb') as stream:
        wire = stream.read(196609)
    assert len(wire) <= 196608 and hashlib.sha256(wire).hexdigest() == digest
    return json.loads(wire)


def _check_review_twins(support, opposed, claim_pin):
    # Compare the bound request graph, allowing only the calibration review edge
    # and the induced request/authority/handoff commitments to change.
    signatures = []
    for flags, relation in ((support, 'support'), (opposed, 'opposition')):
        handoff = Path(flags['handoff-package'])
        objects = handoff / 'objects'
        rpin = flags['expected-request-pin']
        request = _object(objects, rpin)
        auth = _object(flags['objects-dir'], flags['expected-authority-pin'])
        assert auth.pop('target') == {'kind': 'ct.request.v1', 'sha256': rpin}
        with (handoff / 'handoff.json').open('rb') as stream:
            wire = stream.read(32769)
        assert len(wire) <= 32768 and hashlib.sha256(wire).hexdigest() == flags['expected-handoff-pin']
        carriage = json.loads(wire)
        assert carriage.pop('request') == {'kind': 'ct.request.v1', 'sha256': rpin}
        selected, other = [], []
        for rr in request.pop('reviews'):
            review = _object(objects, rr['sha256'])
            if review['claim'] == {'kind': 'ct.claim.v1', 'sha256': claim_pin}:
                assert review.pop('relation') == relation
                selected.append(review)
            else:
                other.append(rr)
        assert len(selected) == 1
        signatures.append((request, other, selected, auth, carriage))
    assert signatures[0] == signatures[1]


def _write_record(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, sort_keys=True)


def _capture(directory, args, *, timeout=90, cap=131072):
    """Retain a shared bounded prefix, kill the process group on incomplete capture."""
    directory.mkdir()
    _write_record(directory / 'argv.json', args)
    start = time.monotonic()
    # Leave a bounded interval within the entry allowance for termination and reap.
    cleanup = min(2, timeout / 4)
    deadline = start + timeout - cleanup
    process = None
    count = 0
    status = 'incomplete'
    try:
        with (directory / 'stdout').open('xb') as stdout, (directory / 'stderr').open('xb') as stderr:
            process = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, start_new_session=True)
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ, stdout)
                selector.register(process.stderr, selectors.EVENT_READ, stderr)
                while selector.get_map():
                    if time.monotonic() >= deadline:
                        raise subprocess.TimeoutExpired(args, timeout)
                    for key, _events in selector.select(max(0, deadline - time.monotonic())):
                        room = cap - count
                        chunk = os.read(key.fd, min(room + 1, 8192))
                        if not chunk:
                            selector.unregister(key.fileobj)
                            continue
                        retained = chunk[:room]
                        key.data.write(retained)
                        count += len(retained)
                        if len(chunk) > room:
                            status = 'truncated'
                            raise AssertionError('native capture exceeded combined stream limit')
            process.wait(timeout=max(0, deadline - time.monotonic()))
        if time.monotonic() >= deadline:
            raise subprocess.TimeoutExpired(args, timeout)
        status = 'complete'
    except subprocess.TimeoutExpired:
        status = 'timeout'
        raise
    finally:
        if process is not None:
            try:
                if status != 'complete':
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    try:
                        process.wait(timeout=min(cleanup, max(0, start + timeout - time.monotonic())))
                    except subprocess.TimeoutExpired:
                        pass  # Exit remains unknown; enclosing controller owns final containment.
            finally:
                process.stdout.close()
                process.stderr.close()
        rc = process.returncode if process is not None else None
        _write_record(directory / 'capture.json', dict(status=status, retained_bytes=count,
            elapsed_seconds=time.monotonic() - start, returncode=rc,
            signal=-rc if rc is not None and rc < 0 else None))
    return rc


def invoke(directory, operation, flags, *, refusal=None):
    args = [sys.executable, '-B', '-m', 'applications.bounded_decision_workflow', operation]
    for flag, value in sorted(flags.items()):
        args.extend(['--' + flag, str(value)])
    rc = _capture(directory, args)
    if refusal is None:
        assert rc == 0 and (directory / 'stderr').stat().st_size == 0
        return json.loads((directory / 'stdout').read_bytes())
    code, exit_class, target = refusal
    assert rc == exit_class and (directory / 'stdout').stat().st_size == 0
    diagnostic = json.loads((directory / 'stderr').read_bytes())
    assert (diagnostic['code'], diagnostic['exit_class'], diagnostic['target']) == (code, rc, target)
    return diagnostic


@pytest.fixture(scope='module')
def native_cases(native_inputs, tmp_path_factory):
    root = tmp_path_factory.mktemp('c05-native')
    cache = {}
    def get(name):
        if name not in native_inputs['cases']:
            pytest.skip('no admitted native correspondence-gap specimen supplied; C/W evidence only')
        if name not in cache:
            case = root / name
            case.mkdir()
            args = dict(native_inputs['cases'][name])
            args.update({'output-dir': case / 'evaluation', 'scratch-dir': case / 'evaluation-scratch'})
            completion = invoke(case / 'evaluate-command', 't1-reassessment-evaluate', args)
            cache[name] = (case, completion, dict(native_inputs['cases'][name]))
        return cache[name]
    return get


@pytest.mark.parametrize('name,status,admissibility', [
    ('false_support', 'blocked_calibration_counterexample', 'blocked'),
    ('false_opposition', 'blocked_calibration_counterexample', 'blocked'),
    ('positive_support', 'delegated_assessment', 'permitted_under_declared_conditions'),
    ('positive_opposition', 'delegated_assessment', 'blocked')])
def test_c01_c02_c03_c04_c10_c11_native_complete_path(native_inputs, native_cases, name, status, admissibility):
    from applications.bounded_decision_workflow.t1_contracts import sha
    case, completion, flags = native_cases(name)
    assert completion['schema'] == 'ct.t1-calibration-gate-check.v1'
    assert completion['decision']['gate_status'] == status
    assert completion['decision']['admissibility'] == admissibility
    wire = (case / 'evaluation/workflow-receipt.json').read_bytes()
    old = json.loads(wire)
    base_name = 'receipt/base-applicability.json' if old['delegation']['status'] == 'not_run' else 'bundle/applicability.json'
    base = json.loads((case / 'evaluation' / base_name).read_bytes())
    calibration = next(row for row in base['claims'] if row['condition'] == 'reference_calibration')
    assert calibration['governing_state'] == ('contradicted' if name.endswith('opposition') else 'supported')
    expected = native_inputs['expected']  # independently frozen model, claim and H1 refs
    positive = name.startswith('positive')
    support = name.endswith('support')
    beta, theta, scalar = ('0', '60.1', '60.1') if positive else ('10', '50', '60')
    finding = old['finding']
    q = finding['subjects']
    assert completion['subject'] == {'kind': 'ct.t1-calibration-gate-outcome.v1', 'sha256': sha(wire)}
    assert old['operation'] == 't1-reassessment-evaluate' and old['replay_of'] is None
    assert old['conclusion'] == completion['decision'] and old['process_completion'] == 'completed'
    assert q['required_claim'] == {'kind': 'ct.claim.v1', 'sha256': expected['claim_sha256']}
    assert calibration['claim'] == q['required_claim']
    assert q['model'] == {'kind': 'ct.model.v1', 'sha256': expected['model_sha256']}
    zero = {'numerator': '0', 'denominator': '1'}
    bound = {'lo': zero, 'hi': zero}
    assert finding['required_claim_core']['binding'] == dict(condition='reference_calibration',
        parameters={'b_ref': bound, 'instrument_id': expected['instrument_id']})
    assert finding['qualification'] == 'qualified_match'
    assert finding['calibration'] == dict(beta=beta, b_ref=bound, predicate='beta_in_closed_b_ref',
        declared_predicate=positive, computed_predicate=positive)
    assert finding['source_scope'] == {'axis': 'declared_synthetic_acquisition_time',
        'from': '2026-10-05T09:00:00Z', 'to': '2026-10-05T09:02:00Z',
        'witness_instant': '2026-10-05T09:00:08Z'}
    assert finding['required_scope'] == {'axis': 'declared_assessment_time',
        'from': '2026-08-07T20:30:00Z', 'to': '2026-10-05T09:02:00Z'}
    producer = Path(flags['producer-package'])
    receipt_wire = (producer / 'receipt/receipt.json').read_bytes()
    assert hashlib.sha256(receipt_wire).hexdigest() == q['producer_receipt']['sha256']
    receipt = json.loads(receipt_wire)
    assert receipt['world'] == q['world'] and Fraction(receipt['r']) == Fraction(scalar)
    assert receipt['diagnostics']['reference_calibration'] == {'b_ref': bound, 'beta_in_b_ref': positive}
    world = _object(producer / 'objects', q['world']['sha256'])
    assert {k: world[k] for k in ('beta', 'theta', 'baseline_theta', 'epsilon')} == dict(
        beta=beta, theta=theta, baseline_theta=theta, epsilon='0')
    request = _object(Path(flags['handoff-package']) / 'objects', flags['expected-request-pin'])
    assert request['model'] == q['model']
    assert Fraction(request['result']['observation']['scalar']) == Fraction(scalar)
    assert request['result']['acquisition']['instrument_id'] == expected['instrument_id']
    assert base['use_disposition'] == ('use_permitted' if support else 'blocked')
    assert old['conclusion']['base_reasons'] == ([] if support else ['governing_state_contradicted'])
    if not positive:
        assert finding['effect'] == 'block_counterexample'
        assert finding['reasons'] == ['calibration_premise_counterexample']
        assert old['delegation'] == dict(status='not_run', owning_manifest=None, owning_result=None)
        assert old['conclusion']['owning_disposition'] is None and not (case / 'evaluation/bundle').exists()
    else:
        assert finding['effect'] == 'permission_to_delegate'
        assert finding['reasons'] == ['no_counterexample_from_this_check']
        bundle = case / 'evaluation/bundle'
        assert old['delegation']['status'] == 'completed'
        assert old['delegation']['owning_manifest']['sha256'] == sha((bundle / 'manifest.json').read_bytes())
        result_wire = (bundle / 'result.json').read_bytes()
        result = json.loads(result_wire)
        assert old['delegation']['owning_result']['sha256'] == sha(result_wire)
        assert result['disposition'] == ('one_compatible' if support else 'applicability_blocked')
        assert old['conclusion']['owning_disposition'] == result['disposition']
        assert result['adoption'] == 'derived_not_adopted'
        statuses = {h['hypothesis']['sha256']: h['status'] for h in result['hypotheses']}
        assert len(statuses) == len(result['hypotheses']) == 2
        assert statuses[expected['h1_sha256']] == ('compatible_under_declared_model' if support else 'not_assessed')
        assert sorted(statuses.values()) == (['compatible_under_declared_model', 'conditionally_incompatible']
                                             if support else ['not_assessed', 'not_assessed'])
        invocation = json.loads((bundle / 'invocation.json').read_bytes())
        assert invocation['operation'] == 'checked-reassessment-evaluate' and invocation['replay_of'] is None
    check_flags = {k: v for k, v in flags.items() if k != 'objects-dir'}
    check_flags.update({'workflow-package': case / 'evaluation', 'expected-workflow-receipt-pin': sha(wire)})
    for operation, output, scratch in [('t1-workflow-verify', 'verify', 'verify-scratch'),
                                      ('t1-workflow-replay', 'replay', 'replay-scratch')]:
        args = dict(check_flags, **{'output-dir': case / output, 'scratch-dir': case / scratch})
        checked = invoke(case / (output + '-command'), operation, args)
        assert checked['decision'] == completion['decision']
    replay_wire = (case / 'replay/workflow-receipt.json').read_bytes()
    new = json.loads(replay_wire)
    assert new['finding'] == old['finding'] and new['conclusion'] == old['conclusion']
    assert new['operation'] == 't1-workflow-replay' and new['replay_of'] == completion['subject']
    if positive:
        replay = case / 'replay/bundle'
        invocation = json.loads((replay / 'invocation.json').read_bytes())
        assert invocation['operation'] == 'checked-reassessment-replay'
        assert invocation['replay_of'] == {'manifest_sha256': old['delegation']['owning_manifest']['sha256']}
        assert new['delegation']['owning_manifest']['sha256'] == sha((replay / 'manifest.json').read_bytes())
        for member in ('result.json', 'trace.json'):
            assert sha((replay / member).read_bytes()) == sha((bundle / member).read_bytes())
    else:
        assert new['delegation'] == old['delegation'] and not (case / 'replay/bundle').exists()
    check_flags.update({'workflow-package': case / 'replay', 'expected-workflow-receipt-pin': sha(replay_wire),
                        'output-dir': case / 'reverify', 'scratch-dir': case / 'reverify-scratch'})
    reverified = invoke(case / 'reverify-command', 't1-workflow-verify', check_flags)
    assert reverified['subject']['sha256'] == sha(replay_wire)
    assert reverified['decision'] == completion['decision']


@pytest.mark.parametrize('fault,flag', [('authority', 'expected-authority-pin'),
                                      ('source-pin', 'expected-producer-manifest-pin')])
def test_c08_native_external_pin_refusal(native_cases, fault, flag):
    case, _completion, source = native_cases('false_support')
    args = dict(source)
    args[flag] = 'f' * 64
    args.update({'output-dir': case / (fault + '-refusal'), 'scratch-dir': case / (fault + '-scratch')})
    refusal = (('AUTHORITY_PIN_MISMATCH', 3, '/evaluation_authority') if fault == 'authority'
               else ('SIM_PIN_MISMATCH', 3, '/M'))
    invoke(case / (fault + '-command'), 't1-reassessment-evaluate', args, refusal=refusal)
    assert not (case / (fault + '-refusal') / 'workflow-receipt.json').exists()


def test_c07_native_gap_if_reachable(native_inputs, native_cases):
    from applications.bounded_decision_workflow.t1_contracts import sha
    case, completion, source = native_cases('correspondence_gap')
    assert completion['decision']['gate_status'] == 'blocked_calibration_correspondence'
    assert completion['decision']['admissibility'] == 'blocked'
    assert not (case / 'evaluation/bundle').exists()
    flags = {k: v for k, v in source.items() if k != 'objects-dir'}
    wire = (case / 'evaluation/workflow-receipt.json').read_bytes()
    finding = json.loads(wire)['finding']
    expected = native_inputs['expected']['gap_qualification']
    reason = {'established_mismatch': 'required_primary_match_missing',
              'insufficient_information': 'correspondence_unresolved'}[expected]
    assert finding['qualification'] == expected and reason in finding['reasons']
    assert finding['effect'] == 'block_required_correspondence'
    flags.update({'workflow-package': case / 'evaluation', 'expected-workflow-receipt-pin': sha(wire)})
    for op, label in [('t1-workflow-verify', 'verify'), ('t1-workflow-replay', 'replay')]:
        result = invoke(case / (label + '-command'), op, dict(flags, **{
            'output-dir': case / label, 'scratch-dir': case / (label + '-scratch')}))
        assert result['decision'] == completion['decision']
    replay_wire = (case / 'replay/workflow-receipt.json').read_bytes()
    flags.update({'workflow-package': case / 'replay', 'expected-workflow-receipt-pin': sha(replay_wire),
                  'output-dir': case / 'reverify', 'scratch-dir': case / 'reverify-scratch'})
    invoke(case / 'reverify-command', 't1-workflow-verify', flags)


@pytest.mark.parametrize('fault,name', [('finding', 'false_support'), ('result', 'positive_support')])
def test_c12_native_rehashed_semantic_tampering_refuses(native_cases, fault, name):
    from applications.bounded_decision_workflow.t1_contracts import canonical_bytes, ref, sha
    from applications.bounded_decision_workflow import t1_workflow, checked_runtime as rt
    from .calibration_fixtures import write_package, rehash_owner_result
    case, _completion, source = native_cases(name)
    files = t1_workflow.read_package(case / 'evaluation')
    value = json.loads(files['workflow-receipt.json'])
    if fault == 'finding':
        value['finding']['comparisons'][0]['operands'][0]['normalized_value']['value'] = 'f' * 64
    else:
        bundle = rehash_owner_result({n: files['bundle/' + n] for n in rt.BUNDLE_NAMES})
        files.update({'bundle/' + n: w for n, w in bundle.items()})
        value['delegation']['owning_manifest'] = ref('ct.bundle-manifest.v1', bundle['manifest.json'])
        value['delegation']['owning_result'] = ref('ct.reassessment.v1', bundle['result.json'])
        for member in value['members']:
            if member['role'] == 'owning_manifest':
                member.update(sha256=sha(bundle['manifest.json']), bytes=len(bundle['manifest.json']))
        value['trace'][-1]['target'] = value['delegation']['owning_result']
    files['workflow-receipt.json'] = canonical_bytes(value)
    destination = case / ('forged-' + fault)
    write_package(destination, files)
    flags = {k: v for k, v in source.items() if k != 'objects-dir'}
    flags.update({'workflow-package': destination, 'expected-workflow-receipt-pin': sha(files['workflow-receipt.json']),
                  'output-dir': case / (fault + '-refusal'), 'scratch-dir': case / (fault + '-scratch')})
    refusal = (('CALIBRATION_FINDING_MISMATCH', 3, '/F/finding') if fault == 'finding'
               else ('DOWNSTREAM_REPLAY_MISMATCH', 3, '/bundle/result.json'))
    invoke(case / (fault + '-command'), 't1-workflow-verify', flags, refusal=refusal)


def test_c13_native_collision_preserves_completed_package(native_cases):
    case, _completion, source = native_cases('false_support')
    original = (case / 'evaluation/workflow-receipt.json').read_bytes()
    args = dict(source, **{'output-dir': case / 'evaluation', 'scratch-dir': case / 'collision-scratch'})
    invoke(case / 'collision-command', 't1-reassessment-evaluate', args,
           refusal=('SIM_OUTPUT_UNSAFE', 5, '/argv/output-dir'))
    assert (case / 'evaluation/workflow-receipt.json').read_bytes() == original


def test_c15_native_old_bound_identity_refuses_if_supplied(native_inputs, tmp_path):
    if 'historical_case' not in native_inputs:
        pytest.skip('old-byte execution is optional; no historical provider is provisioned')
    flags = native_inputs['historical_case']
    assert set(flags) == FLAGS
    args = dict(flags, **{'output-dir': tmp_path / 'refused', 'scratch-dir': tmp_path / 'scratch'})
    invoke(tmp_path / 'command', 't1-reassessment-evaluate', args,
           refusal=('SIM_EDITION_NOT_PERMITTED', 3, '/J/producer_build'))
