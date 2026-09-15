"""Approved P1/P2 conformance; independent byte oracle, real command twins."""
from dataclasses import replace
import hashlib
import io
import json
import os
import subprocess
import sys
from types import SimpleNamespace

import pytest

from applications.bounded_decision_workflow import BUILD_LIMITS, WorkflowDiagnostic, WorkflowInputError, verify_bundle
from tests.applications.bounded_decision_workflow.test_s6_cli import ROOT, inputs, run, success, failure
from tests.applications.bounded_decision_workflow.test_s1_input_public_admission import PACKAGE_PATH


FALLBACK = b'{"bundle_state":"unknown","code":"INTERNAL_ERROR","exit_code":7,"message_key":"internal_error","retry_class":"investigate","stage":"internal_failure","target":"application"}\n'


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def ordinary():
    return WorkflowDiagnostic("OUTPUT_LIMIT_EXCEEDED", "output_resource", "result_or_trace",
                              "output_limit_exceeded", "reduce_input", 4, "optional_refusal")


@pytest.mark.parametrize("text", ['x', '\n', '"', '\\', 'é', '😀', '\x00'])
def test_encoded_byte_boundary_with_valid_twin(text):
    from applications.bounded_decision_workflow.terminal import diagnostic_line
    # Trusted synthetic diagnostic strings test the encoder, not caller admission.
    from dataclasses import asdict
    base = asdict(ordinary()); base['target'] = ''
    n = 1
    while len(encode(dict(base, target=text * (n + 1)))) <= 512: n += 1
    for count, accepted in ((n, True), (n + 1, False)):
        d = replace(ordinary(), target=text * count)
        wire, status = diagnostic_line(d)
        assert len(wire) <= 512
        assert (wire, status) == ((encode(asdict(d)), 4) if accepted else (FALLBACK, 7))
    # Exact 512/513, including required LF, independent of the string character.
    body = text * n
    body += 'x' * (512 - len(encode(dict(base, target=body))))
    assert len(diagnostic_line(replace(ordinary(), target=body))[0]) == 512
    assert diagnostic_line(replace(ordinary(), target=body + 'x')) == (FALLBACK, 7)


@pytest.mark.parametrize('mutation', [dict(target='x' * 1000000), dict(target='\ud800'),
    dict(target=object()), dict(exit_code=True), dict(exit_code=0), dict(bundle_state='invented'),
    dict(code=[]), dict(message_key='wrong'), dict(stage='unknown_stage')])
def test_malformed_diagnostic_is_constant_fallback(mutation):
    from applications.bounded_decision_workflow.terminal import diagnostic_line
    assert diagnostic_line(replace(ordinary(), **mutation)) == (FALLBACK, 7)
    assert diagnostic_line(ordinary())[1] == 4


def test_encoder_failure_does_not_reenter_encoder(monkeypatch):
    from applications.bounded_decision_workflow import terminal
    calls = []
    def fail(*args):
        calls.append(1)
        raise RuntimeError('do not expose')
    monkeypatch.setattr(terminal, '_encode', fail)
    assert terminal.diagnostic_line(ordinary()) == (FALLBACK, 7)
    assert calls == [1]


@pytest.mark.parametrize('mode', ['write', 'flush', 'short', 'ok'])
def test_sink_failure_is_nonrecursive(monkeypatch, mode):
    from applications.bounded_decision_workflow import cli
    class Sink:
        def __init__(self): self.writes = []; self.flushes = 0
        def write(self, value):
            self.writes.append(value)
            if mode == 'write': raise OSError('private sink')
            return len(value) - (mode == 'short')
        def flush(self):
            self.flushes += 1
            if mode == 'flush': raise OSError('private sink')
    sink = Sink(); out = io.BytesIO()
    monkeypatch.setattr(cli.sys, 'stderr', SimpleNamespace(buffer=sink))
    monkeypatch.setattr(cli.sys, 'stdout', SimpleNamespace(buffer=out))
    assert cli.main(['evaluate']) == (2 if mode == 'ok' else 7)
    assert len(sink.writes) == 1 and sink.flushes <= 1 and out.getvalue() == b''


def test_catalogue_exact_canonical_bytes():
    from applications.bounded_decision_workflow.terminal import diagnostic_line
    p = json.loads(PACKAGE_PATH.read_bytes())
    for d in p['diagnostic_catalogue']:
        assert diagnostic_line(WorkflowDiagnostic(**d)) == (encode(d), d['exit_code'])


def test_tight_budget_admission_precedence_and_valid_twin(tmp_path, inputs):
    request, snapshot = inputs; original = json.loads(request.read_bytes())
    expected = next(d for d in json.loads(PACKAGE_PATH.read_bytes())['diagnostic_catalogue']
                    if d['code'] == 'SNAPSHOT_COMMITMENT_MISMATCH')
    for i, budget in enumerate((1, 246, 247, 1024)):
        value = dict(original, requested_limits=dict(BUILD_LIMITS, output_diagnostic_bytes=budget,
                                                      output_stdout_stderr_bytes=1), snapshot_commitment='0' * 64)
        request.write_bytes(encode(value).rstrip(b'\n'))
        dest = tmp_path / f'bad-{i}'
        p = run('evaluate', '--request', request, '--snapshot', snapshot, '--output-dir', dest)
        assert p.returncode == 3 and p.stdout == b'' and p.stderr == encode(expected)
        assert not dest.exists()
    value = dict(original, requested_limits=dict(BUILD_LIMITS, output_diagnostic_bytes=1))
    request.write_bytes(encode(value).rstrip(b'\n'))
    dest = tmp_path / 'twin'
    receipt = success(run('evaluate', '--request', request, '--snapshot', snapshot, '--output-dir', dest))
    kept = json.loads((dest / 'request.json').read_bytes())
    assert kept['requested_limits']['output_diagnostic_bytes'] == 1
    success(run('replay', '--bundle', dest, '--output-dir', tmp_path / 'replay'))
    # Receipt size is fixed for this disposition: hashes are always 64 characters.
    length = len(encode(receipt))
    for n in (1, length - 1, length):
        value['requested_limits']['output_stdout_stderr_bytes'] = n
        request.write_bytes(encode(value).rstrip(b'\n'))
        dest = tmp_path / f'success-cap-{n}'
        p = run('evaluate', '--request', request, '--snapshot', snapshot, '--output-dir', dest)
        if n == length: success(p); assert len(p.stdout) == n
        else:
            failure(p, 'OUTPUT_LIMIT_EXCEEDED', 4)
            assert len(p.stderr) == 201 and not dest.exists()


@pytest.mark.parametrize('after', [False, True])
def test_actual_entrypoint_malformed_error_before_after_publication(tmp_path, inputs, after):
    request, snapshot = inputs; dest = tmp_path / 'fault'
    script = '''import runpy,sys
from dataclasses import replace
from applications.bounded_decision_workflow import cli,WorkflowInputError
original=cli.execute
after=sys.argv.pop(1)=='True'
def execute(args, **kwargs):
    if after: original(args, **kwargs)
    d=replace(cli._problem('INTERNAL_ERROR').diagnostic,target='x'*10000)
    raise WorkflowInputError(d)
cli.execute=execute
sys.argv[0]='applications.bounded_decision_workflow'
runpy.run_module('applications.bounded_decision_workflow',run_name='__main__')
'''
    p = subprocess.run([sys.executable, '-c', script, str(after), 'evaluate', '--request', str(request),
        '--snapshot', str(snapshot), '--output-dir', str(dest)], cwd=ROOT,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'), capture_output=True, timeout=30)
    assert p.returncode == 7 and p.stdout == b'' and p.stderr == FALLBACK
    if after: success(run('verify', '--bundle', dest))
    else: assert not dest.exists()


def test_incomplete_malformed_complete_and_api_inventory(tmp_path, inputs):
    request, snapshot = inputs; dest = tmp_path / 'bundle'
    success(run('evaluate', '--request', request, '--snapshot', snapshot, '--output-dir', dest))
    manifest = (dest / 'manifest.json').read_bytes()
    catalogue = {d['code']: d for d in json.loads(PACKAGE_PATH.read_bytes())['diagnostic_catalogue']}
    for state in ('missing', 'invalid', 'complete'):
        if state == 'missing': (dest / 'manifest.json').unlink()
        else: (dest / 'manifest.json').write_bytes(b'{}' if state == 'invalid' else manifest)
        before = {p.name:p.read_bytes() for p in dest.iterdir()}
        inspected = verify_bundle(dest)
        process = run('verify', '--bundle', dest)
        if state == 'complete':
            success(process); assert inspected.integrity_state == 'complete_bundle'
        else:
            code = 'BUNDLE_INCOMPLETE' if state == 'missing' else 'MANIFEST_INVALID'
            assert process.returncode == 3 and process.stdout == b'' and process.stderr == encode(catalogue[code])
            assert inspected.integrity_state == 'incomplete_bundle' and inspected.bundle_kind is None
        assert dict(inspected.captured) == before
        assert {p.name:p.read_bytes() for p in dest.iterdir()} == before
    (dest / 'manifest.json').unlink()
    (dest / 'private-extra').write_bytes(b'do-not-disclose-or-open')
    inspected = verify_bundle(dest)
    assert len(inspected.captured) == 6 and 'private-extra' not in inspected.captured
    assert run('verify', '--bundle', dest).stderr == encode(catalogue['BUNDLE_INCOMPLETE'])
    empty = tmp_path / 'empty'; empty.mkdir()
    assert not verify_bundle(empty).captured
    assert run('verify', '--bundle', empty).stderr == encode(catalogue['BUNDLE_INCOMPLETE'])


def test_incomplete_unsafe_and_oversized_capture_twins(tmp_path, inputs):
    request, snapshot = inputs; dest = tmp_path / 'incomplete'; dest.mkdir()
    path = dest / 'request.json'
    path.symlink_to(request)
    failure(run('verify', '--bundle', dest), 'PATH_FINAL_SYMLINK', 5)
    path.unlink(); path.write_bytes(b'x' * (BUILD_LIMITS['request_wire_bytes'] + 1))
    failure(run('verify', '--bundle', dest), 'INPUT_WIRE_LIMIT_EXCEEDED', 4)
    path.write_bytes(request.read_bytes())
    failure(run('verify', '--bundle', dest), 'BUNDLE_INCOMPLETE', 3)
    assert verify_bundle(dest).captured['request.json'] == request.read_bytes()
