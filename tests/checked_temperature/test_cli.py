"""Command-line integration.

The process entry point always uses the maintained executable identity. In
this uncommitted Gate 1 tree that identity is unavailable, so the real command
must refuse; that refusal is asserted rather than worked around. File-path
handling is exercised in process through `checked_cli.execute` with the
explicitly labelled TestDoubleBuild.
"""
import json
import os
import subprocess
import sys
import pytest
from applications.bounded_decision_workflow import checked_cli
from applications.bounded_decision_workflow.checked_contracts import CheckedRefusal, sha
from tests.checked_temperature.fixtures import ROOT, co1, fx1


def write_inputs(tmp_path, case):
    objects = tmp_path / 'objects'
    objects.mkdir()
    for d, data in case.objects.items():
        (objects / d).write_bytes(data)
    request = tmp_path / 'request.json'
    request.write_bytes(case.request_wire)
    return request, objects


def test_process_entry_point_refuses_without_a_clean_executable_identity(tmp_path):
    case = fx1()
    request, objects = write_inputs(tmp_path, case)
    out = tmp_path / 'NEW'
    proc = subprocess.run([sys.executable, '-m', 'applications.bounded_decision_workflow',
                           'checked-selection-evaluate', '--expected-request-pin', case.request_pin,
                           '--expected-authority-pin', case.authority_pin, '--request', str(request),
                           '--objects-dir', str(objects), '--output-dir', str(out)],
                          cwd=ROOT, capture_output=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
                          timeout=300)
    diagnostic = json.loads(proc.stderr)
    assert proc.returncode == 3 and proc.stdout == b''
    assert set(diagnostic) == {'schema', 'code', 'stage', 'target', 'exit_class'} and diagnostic['exit_class'] == 3
    # AMENDED expectation (CONTRACT §12.2 / DG1): Gate 1 asserted BUILD_NOT_PERMITTED with a
    # special target. An uncommitted tree has no executable identity -> BUILD_IDENTITY_UNAVAILABLE;
    # a clean committed checkout has one, absent from the fixture policy -> BUILD_NOT_PERMITTED.
    dirty = subprocess.run(['git', '--no-optional-locks', '-C', str(ROOT), 'status', '--porcelain',
                            '--untracked-files=all', '--', 'applications', 'backend'],
                           capture_output=True, timeout=60).stdout.strip() != b''
    if dirty:
        assert (diagnostic['code'], diagnostic['target']) == ('BUILD_IDENTITY_UNAVAILABLE', '/build/current')
    else:
        assert (diagnostic['code'], diagnostic['target']) == ('BUILD_NOT_PERMITTED', '/build')
    assert not out.exists()


def test_process_usage_error(tmp_path):
    proc = subprocess.run([sys.executable, '-m', 'applications.bounded_decision_workflow',
                           'checked-selection-verify', '--bundle', str(tmp_path)],
                          cwd=ROOT, capture_output=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
                          timeout=300)
    assert proc.returncode == 2 and json.loads(proc.stderr)['code'] == 'CLI_USAGE'


def run(argv, build):
    return checked_cli.execute(checked_cli.arguments(argv), build=build)


def test_in_process_paths_publish_verify_replay_and_collision(tmp_path):
    case = fx1()
    request, objects = write_inputs(tmp_path, case)
    pins = ['--expected-request-pin', case.request_pin, '--expected-authority-pin', case.authority_pin]
    sel = tmp_path / 'SEL'
    receipt = run(['checked-selection-evaluate', *pins, '--request', str(request), '--objects-dir', str(objects),
                   '--output-dir', str(sel)], case.world.build)
    names = sorted(os.listdir(sel))
    assert len(names) == 9 and receipt['bundle_commitment'] == sha((sel / 'manifest.json').read_bytes())
    manifest = json.loads((sel / 'manifest.json').read_bytes())
    assert manifest['filesystem'] in ('ext4', 'xfs', 'unknown')
    for f in manifest['files']:
        assert sha((sel / f['name']).read_bytes()) == f['sha256']
    report = run(['checked-selection-verify', *pins, '--bundle', str(sel)], case.world.build)
    assert report['operation'] == 'checked-selection-verify'
    again = tmp_path / 'SEL2'
    run(['checked-selection-replay', *pins, '--bundle', str(sel), '--output-dir', str(again)], case.world.build)
    assert (again / 'result.json').read_bytes() == (sel / 'result.json').read_bytes()
    with pytest.raises(CheckedRefusal) as e:
        run(['checked-selection-evaluate', *pins, '--request', str(request), '--objects-dir', str(objects),
             '--output-dir', str(sel)], case.world.build)
    assert (e.value.code, e.value.exit_class) == ('OUTPUT_COLLISION', 6)
    # Reassessment through paths, with the prior bundle directory.
    files = {n: (sel / n).read_bytes() for n in names}
    rcase = co1(files, case)
    (tmp_path / 'r').mkdir()
    rreq, robj = write_inputs(tmp_path / 'r', rcase)
    rpins = ['--expected-request-pin', rcase.request_pin, '--expected-authority-pin', rcase.authority_pin]
    rea = tmp_path / 'REA'
    run(['checked-reassessment-evaluate', *rpins, '--request', str(rreq), '--objects-dir', str(robj),
         '--prior-bundle', str(sel), '--output-dir', str(rea)], case.world.build)
    report = run(['checked-reassessment-verify', *rpins, '--bundle', str(rea)], case.world.build)
    assert report['prior_material_checked'] is True


def test_objects_dir_entries_must_be_digest_named(tmp_path):
    case = fx1()
    request, objects = write_inputs(tmp_path, case)
    (objects / 'notes.txt').write_bytes(b'x')
    with pytest.raises(CheckedRefusal) as e:
        run(['checked-selection-evaluate', '--expected-request-pin', case.request_pin, '--expected-authority-pin',
             case.authority_pin, '--request', str(request), '--objects-dir', str(objects),
             '--output-dir', str(tmp_path / 'NEW')], case.world.build)
    assert e.value.code == 'SCHEMA_INVALID'


def test_duplicate_flag_and_bad_pin_are_usage_errors():
    for argv in (['checked-selection-verify', '--bundle', 'a', '--bundle', 'b', '--expected-request-pin', '0' * 64,
                  '--expected-authority-pin', '0' * 64],
                 ['checked-selection-verify', '--bundle', 'a', '--expected-request-pin', 'xyz',
                  '--expected-authority-pin', '0' * 64]):
        with pytest.raises(CheckedRefusal) as e:
            checked_cli.arguments(argv)
        assert (e.value.code, e.value.exit_class) == ('CLI_USAGE', 2)


def test_bundle_directory_must_hold_exactly_nine_files(tmp_path):
    case = fx1()
    request, objects = write_inputs(tmp_path, case)
    pins = ['--expected-request-pin', case.request_pin, '--expected-authority-pin', case.authority_pin]
    sel = tmp_path / 'SEL'
    run(['checked-selection-evaluate', *pins, '--request', str(request), '--objects-dir', str(objects),
         '--output-dir', str(sel)], case.world.build)
    (sel / 'extra.json').write_bytes(b'{}')
    with pytest.raises(CheckedRefusal) as e:
        run(['checked-selection-verify', *pins, '--bundle', str(sel)], case.world.build)
    assert (e.value.code, e.value.target) == ('REFERENCE_MISSING', '/bundle')
