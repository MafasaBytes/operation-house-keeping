"""Slice 5: exact frozen object carriage, never a caller-supplied matrix.

Input premises come from the approved P/U preparation captures. The numerical
assertions below are hand-derived (same author, not independent review).
"""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from applications.bounded_decision_workflow.measurement_contracts import canonical_json_bytes

PACKAGE = Path('docs/superpowers/reports/2026-09-19-next-measurement-preparation')


def test_closed_command_mapping_has_no_out_of_band_semantic_arguments():
    from applications.bounded_decision_workflow import measurement_runtime
    import inspect
    assert tuple(inspect.signature(measurement_runtime.evaluate).parameters) == (
        'invocation_file', 'objects_dir', 'authority_pin', 'output_dir', 'limits_file')


def recover_case(tmp_path, case='P'):
    from applications.bounded_decision_workflow.measurement_build import identity
    cap = json.loads((PACKAGE / 'inputs' / case / 'capture.json').read_bytes())
    objects = {}
    for member in cap['members']:
        ref = member['reference']
        objects[(ref['kind'], ref['sha256'])] = base64.b64decode(member['bytes'], validate=True)
    invocation = json.loads(objects.pop(('nm.invocation.v1', cap['invocation']['sha256'])))
    objects = {k:v for k,v in objects.items() if k[0] != 'nm.prepared-build.v1'}
    build = identity()
    invocation['build_identity'] = hashlib.sha256(build).hexdigest()
    objects[('nm.build.v1', invocation['build_identity'])] = build
    root = tmp_path / 'inputs'; root.mkdir()
    objdir = root / 'objects'; objdir.mkdir()
    for (kind, digest), wire in objects.items():
        (objdir / (digest + '.' + kind)).write_bytes(wire)
    iv = root / 'invocation.json'; iv.write_bytes(canonical_json_bytes(invocation))
    return iv, objdir, cap['authority_pin']


def command(*args):
    return subprocess.run([sys.executable, '-m', 'applications.bounded_decision_workflow', *map(str,args)],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def test_supported_delivery_and_standalone_recomputation(tmp_path):
    iv, objects, pin = recover_case(tmp_path)
    out = tmp_path / 'result'
    run = command('measurement-evaluate', '--invocation', iv, '--objects-dir', objects,
                  '--authority-pin', pin, '--output-dir', out)
    assert run.returncode == 0, run.stderr.decode()
    result = json.loads((out / 'result.json').read_bytes())
    assert result['evidence']['observed'] == {'numerator':'601','denominator':'10'}
    assert [row['worst'] for row in result['ranking']['scores']] == [1,2]
    assert result['ranking']['disposition'] == 'preferred_within_supplied_set'
    assert result['ranking']['branches'][1]['outcomes'] == [
        {'outcome':'code_a','survivors':['H1','H2']},
        {'outcome':'code_b','survivors':['H1','H2']}]
    # Remove original pathname access without removing historical bytes.
    iv.parent.rename(tmp_path / 'originals-not-at-input-path')
    replay = command('measurement-replay','--bundle',out,'--output-dir',tmp_path/'replay')
    assert replay.returncode == 0, replay.stderr.decode()
    assert (out/'result.json').read_bytes() == (tmp_path/'replay'/'result.json').read_bytes()
    assert command('measurement-verify','--bundle',out).returncode == 0
    forged = json.loads((out/'result.json').read_bytes())
    forged['ranking']['scores'][0]['worst'] = 2
    wire = canonical_json_bytes(forged);(out/'result.json').write_bytes(wire)
    manifest = json.loads((out/'manifest.json').read_bytes())
    for entry in manifest['files']:
        if entry['name']=='result.json':
            entry.update(bytes=len(wire),sha256=hashlib.sha256(wire).hexdigest())
    (out/'manifest.json').write_bytes(canonical_json_bytes(manifest))
    assert command('measurement-verify','--bundle',out).returncode == 0
    bad=command('measurement-replay','--bundle',out,'--output-dir',tmp_path/'forged-replay')
    assert bad.returncode==3
    assert json.loads(bad.stderr)['code']=='REPLAY_SEMANTIC_MISMATCH'
