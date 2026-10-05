"""Gate 1 real-build success path through the real command entry point.

No TestDoubleBuild here: the captured policy permits exactly the maintained
executable identity computed by `ExecutableBuild` in this environment. Every
command runs as `python -m applications.bounded_decision_workflow ...` in a
subprocess, which recomputes that identity itself. The maintained identity's
cleanliness rule covers only `applications/` and `backend/`; this test file
lives under `tests/` and does not enter the identity. Policy and evidence are
test-only fixtures.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from applications.bounded_decision_workflow.checked_contracts import canonical_bytes, sha
from applications.bounded_decision_workflow.checked_runtime import ExecutableBuild
from tests.checked_temperature.fixtures import ROOT, co1, fx1, r

MODULE = 'applications.bounded_decision_workflow'


class MaintainedBuildPin:
    """Pin to the real maintained identity (not a test double)."""

    def __init__(self, wire):
        self._wire = wire
        self.digest = sha(wire)

    def wire(self):
        return self._wire


def run(*argv):
    proc = subprocess.run([sys.executable, '-m', MODULE, *argv], cwd=ROOT, capture_output=True, timeout=900,
                          env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    return proc.returncode, proc.stdout, proc.stderr


def write_inputs(directory, case):
    directory.mkdir(parents=True)
    objects = directory / 'objects'
    objects.mkdir()
    for d, data in case.objects.items():
        (objects / d).write_bytes(data)
    request = directory / 'request.json'
    request.write_bytes(case.request_wire)
    return request, objects


def pins(case):
    return ['--expected-request-pin', case.request_pin, '--expected-authority-pin', case.authority_pin]


def files(directory):
    return {p.name: p.read_bytes() for p in Path(directory).iterdir()}


@pytest.fixture(scope='module')
def real(tmp_path_factory):
    wire = ExecutableBuild().wire()   # refuses BUILD_IDENTITY_UNAVAILABLE if not a clean committed executable
    record = json.loads(wire)
    head = subprocess.run(['git', '--no-optional-locks', '-C', str(ROOT), 'rev-parse', 'HEAD'],
                          capture_output=True, timeout=60).stdout.decode().strip()
    assert record['checkpoint'] == head and record['clean_application_backend'] is True
    provenance = {'build_sha256': sha(wire), 'build_bytes': len(wire), 'checkpoint': record['checkpoint'],
                  'python': record['environment_manifest']['python'],
                  'dependency_lock_sha256': record['environment_manifest']['dependency_lock_sha256'],
                  'source_manifest_entries': len(record['source_manifest']),
                  'contract_editions': record['contract_editions'], 'sys_executable': sys.executable}
    out = tmp_path_factory.mktemp('real-build') / 'real-build-identity.json'
    out.write_bytes(canonical_bytes(provenance))
    return MaintainedBuildPin(wire), provenance


@pytest.fixture(scope='module')
def selection(real, tmp_path_factory):
    pin, _ = real
    case = fx1(build=pin)
    root = tmp_path_factory.mktemp('real-selection')
    request, objects = write_inputs(root / 'in', case)
    out = root / 'SEL'
    rc, stdout, stderr = run('checked-selection-evaluate', *pins(case), '--request', str(request),
                             '--objects-dir', str(objects), '--output-dir', str(out))
    return case, out, (rc, stdout, stderr)


@pytest.fixture(scope='module')
def reassessment(selection, tmp_path_factory):
    base, sel, _ = selection
    case = co1(files(sel), base)   # coherent later synthetic evidence chain (amendments C1/C2)
    root = tmp_path_factory.mktemp('real-reassessment')
    request, objects = write_inputs(root / 'in', case)
    out = root / 'REA'
    rc, stdout, stderr = run('checked-reassessment-evaluate', *pins(case), '--request', str(request),
                             '--objects-dir', str(objects), '--prior-bundle', str(sel), '--output-dir', str(out))
    return case, out, (rc, stdout, stderr)


def _common_bundle_checks(bundle, kind, pin):
    f = files(bundle)
    assert sorted(f) == sorted(['invocation.json', 'closure.json', 'derivation.json', 'applicability.json',
                                'result.json', 'trace.json', 'build.json', 'policy.json', 'manifest.json'])
    assert f['build.json'] == pin.wire() and sha(f['build.json']) == pin.digest   # the real identity, recorded
    manifest = json.loads(f['manifest.json'])
    assert manifest['bundle_kind'] == kind
    for entry in manifest['files']:
        assert sha(f[entry['name']]) == entry['sha256'] and len(f[entry['name']]) == entry['bytes']
    kinds = {m['kind'] for m in json.loads(f['closure.json'])['members']}
    assert not kinds & {'ct.adoption.v1', 'ct.reassessment.v1', 'ct.closure.v1'}   # nothing adopted or nested
    assert json.loads(f['policy.json'])['permitted_builds'] == [pin.digest]
    return f


def test_real_identity_provenance(real):
    pin, provenance = real
    assert provenance['python']['implementation'] == 'CPython'
    assert provenance['python']['version'].startswith('3.13.')
    assert len(pin.digest) == 64


def test_selection_through_real_command(real, selection):
    pin, _ = real
    case, sel, (rc, stdout, stderr) = selection
    assert (rc, stderr) == (0, b'')
    f = _common_bundle_checks(sel, 'selection', pin)
    assert json.loads(stdout) == {'operation': 'checked-selection-evaluate',
                                  'bundle_commitment': sha(f['manifest.json'])}
    res = json.loads(f['result.json'])
    h1, h2 = case.world.refof('H1'), case.world.refof('H2')
    t1 = [s for s in res['scores'] if s['procedure_edition'] == 'ct.procedure.T1.v1'][0]
    assert {b['outcome']: b['survivors'] for b in t1['branches']} == {'low': [h2], 'gap': [], 'high': [h1]}
    assert res['disposition'] == 'ranked' and res['best'] == ['ct.procedure.T1.v1']
    assert res['post_measurement_elimination_guaranteed'] is False
    assert json.loads(f['invocation.json'])['operation'] == 'checked-selection-evaluate'


def test_selection_verify_and_replay_through_real_command(real, selection, tmp_path):
    pin, _ = real
    case, sel, _ = selection
    rc, stdout, stderr = run('checked-selection-verify', *pins(case), '--bundle', str(sel))
    assert (rc, stderr) == (0, b'')
    assert json.loads(stdout) == {'operation': 'checked-selection-verify',
                                  'bundle_commitment': sha((sel / 'manifest.json').read_bytes()),
                                  'derivation_checked': True, 'applicability_policy_checked': True,
                                  'downstream_result_not_replayed': True}
    out = tmp_path / 'SEL-REPLAY'
    rc, stdout, stderr = run('checked-selection-replay', *pins(case), '--bundle', str(sel), '--output-dir', str(out))
    assert (rc, stderr) == (0, b'')
    again = _common_bundle_checks(out, 'selection', pin)
    for name in ('closure.json', 'derivation.json', 'applicability.json', 'result.json', 'trace.json',
                 'build.json', 'policy.json'):
        assert again[name] == (sel / name).read_bytes()
    inv = json.loads(again['invocation.json'])
    assert inv['operation'] == 'checked-selection-replay'
    assert inv['replay_of'] == {'manifest_sha256': sha((sel / 'manifest.json').read_bytes())}
    assert json.loads(stdout)['bundle_commitment'] == sha(again['manifest.json'])


def test_reassessment_through_real_command(real, reassessment):
    pin, _ = real
    case, rea, (rc, stdout, stderr) = reassessment
    assert (rc, stderr) == (0, b'')
    f = _common_bundle_checks(rea, 'reassessment', pin)
    assert json.loads(stdout) == {'operation': 'checked-reassessment-evaluate',
                                  'bundle_commitment': sha(f['manifest.json'])}
    res = json.loads(f['result.json'])
    h1, h2 = case.world.refof('H1')['sha256'], case.world.refof('H2')['sha256']
    assert res['interval'] == {'lo': r(119, 2), 'hi': r(121, 2)} and res['contained'] is True
    assert [b['outcome'] for b in res['branches']] == ['high']
    assert {h['hypothesis']['sha256']: h['status'] for h in res['hypotheses']} == {
        h1: 'compatible_under_declared_model', h2: 'conditionally_incompatible'}
    assert res['disposition'] == 'one_compatible'
    assert (res['ranking'], res['adoption']) == ('not_reassessed', 'derived_not_adopted')   # no rerank/adoption
    assert 'actual cause is not established' in res['presentation']
    assert res['observation']['public_evidence'] != case.world.refof('evidence')   # later chain, not baseline


def test_reassessment_verify_and_replay_through_real_command(real, reassessment, tmp_path):
    pin, _ = real
    case, rea, _ = reassessment
    rc, stdout, stderr = run('checked-reassessment-verify', *pins(case), '--bundle', str(rea))
    assert (rc, stderr) == (0, b'')
    assert json.loads(stdout) == {'operation': 'checked-reassessment-verify',
                                  'bundle_commitment': sha((rea / 'manifest.json').read_bytes()),
                                  'derivation_checked': True, 'applicability_policy_checked': True,
                                  'downstream_result_not_replayed': True, 'prior_material_checked': True}
    out = tmp_path / 'REA-REPLAY'
    rc, stdout, stderr = run('checked-reassessment-replay', *pins(case), '--bundle', str(rea),
                             '--output-dir', str(out))
    assert (rc, stderr) == (0, b'')
    again = _common_bundle_checks(out, 'reassessment', pin)
    for name in ('closure.json', 'derivation.json', 'applicability.json', 'result.json', 'trace.json',
                 'build.json', 'policy.json'):
        assert again[name] == (rea / name).read_bytes()
    assert json.loads(again['invocation.json'])['replay_of'] == {
        'manifest_sha256': sha((rea / 'manifest.json').read_bytes())}


def test_unpermitted_build_twin_through_real_command(real, tmp_path):
    pin, _ = real
    other = pin.digest[:-1] + ('0' if pin.digest[-1] != '0' else '1')   # otherwise-valid; one other build permitted

    class OtherPin:
        digest = other

        def wire(self):
            raise AssertionError('the twin is never evaluated in process')
    case = fx1(build=OtherPin())
    request, objects = write_inputs(tmp_path / 'in', case)
    out = tmp_path / 'NEW'
    rc, stdout, stderr = run('checked-selection-evaluate', *pins(case), '--request', str(request),
                             '--objects-dir', str(objects), '--output-dir', str(out))
    assert (rc, stdout) == (3, b'')
    assert json.loads(stderr) == {'schema': 'ct.diagnostic.v1', 'code': 'BUILD_NOT_PERMITTED', 'stage': 5,
                                  'target': '/build', 'exit_class': 3}
    assert not out.exists()
