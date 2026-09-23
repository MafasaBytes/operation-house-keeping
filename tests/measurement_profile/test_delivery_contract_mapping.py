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


@pytest.mark.parametrize('case,disposition,phase7',[
    ('U','withheld_due_to_incomplete_predictions','assessed'),
    ('X-conflict-missing','withheld_due_to_conflicting_predictions','assessed'),
    ('G-denied','evaluation_denied','not_assessed_gate_blocked'),
    ('A-false','withheld_due_to_inapplicable_candidate','not_assessed_inapplicable_candidate'),
])
def test_complete_withholding_is_retained_without_pruning(tmp_path,case,disposition,phase7):
    iv,objects,pin=recover_case(tmp_path,case)
    out=tmp_path/'withheld'
    run=command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',out)
    assert run.returncode==0,run.stderr.decode()
    r=json.loads((out/'result.json').read_bytes());t=json.loads((out/'trace.json').read_bytes())
    assert r['ranking']['disposition']==disposition
    assert r['ranking']['scores'] is None and r['ranking']['recommendation'] is None
    assert len(r['procedure_assessments']['procedure_identity_map'])==2
    assert t['phases'][6]['state']==phase7
    if phase7!='assessed':assert r['accounting']['logical_required'].get('mapped_cells',0)==0
    replay=command('measurement-replay','--bundle',out,'--output-dir',tmp_path/'replayed')
    assert replay.returncode==0,replay.stderr.decode()


@pytest.mark.parametrize('case,code',[
    ('S-edition','SUPPORT_SUBJECT_MISMATCH'),
    ('CL-Q3-missing-basis','REQUIRED_REFERENCE_MISSING'),
    ('CL-Q5-refused','RESOURCE_LIMIT_EXCEEDED'),
    ('HARNESS-field-rejected','SCHEMA_INVALID'),
])
def test_adverse_frozen_carriage_controls(tmp_path,case,code):
    iv,objects,pin=recover_case(tmp_path,case)
    run=command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',tmp_path/'refused')
    assert run.returncode in (3,4),run.stderr.decode()
    assert json.loads(run.stderr)['code']==code
    assert not (tmp_path/'refused').exists()


def test_external_pin_substitution_and_safe_path_twins(tmp_path):
    iv,objects,pin=recover_case(tmp_path)
    def run(iv=iv,pin=pin,output=None):
        return command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',output or tmp_path/'result')
    denied=run(pin='0'*64)
    assert denied.returncode==3 and json.loads(denied.stderr)['code']=='AUTHORITY_PIN_REQUIRED'
    symlink=tmp_path/'linked';symlink.symlink_to(iv)
    unsafe=run(iv=symlink)
    assert unsafe.returncode==5 and json.loads(unsafe.stderr)['code']=='PATH_FINAL_SYMLINK'
    fifo=tmp_path/'fifo';import os;os.mkfifo(fifo)
    assert run(iv=fifo).returncode==5
    bad_parent=tmp_path/'linked-parent';bad_parent.symlink_to(tmp_path,target_is_directory=True)
    assert run(output=bad_parent/'escape').returncode==5
    existing=tmp_path/'existing';existing.mkdir();(existing/'untouched').write_bytes(b'preserve')
    collision=run(output=existing)
    assert collision.returncode==5 and json.loads(collision.stderr)['code']=='OUTPUT_COLLISION'
    assert (existing/'untouched').read_bytes()==b'preserve'
    incomplete=tmp_path/'incomplete';incomplete.mkdir();(incomplete/'invocation.json').write_bytes(iv.read_bytes())
    assert command('measurement-verify','--bundle',incomplete).returncode!=0
    # Unreferenced hostile bytes cannot become candidates or be discovered.
    (objects/'extraneous').symlink_to(fifo)
    good=run();assert good.returncode==0,good.stderr.decode()


def test_correctly_shaped_build_substitution_and_policy_substitution(tmp_path):
    iv,objects,pin=recover_case(tmp_path)
    root=json.loads(iv.read_bytes())
    build_path=objects/(root['build_identity']+'.nm.build.v1')
    fake=json.loads(build_path.read_bytes());fake['checkpoint']='0'*40
    wire=canonical_json_bytes(fake);digest=hashlib.sha256(wire).hexdigest()
    (objects/(digest+'.nm.build.v1')).write_bytes(wire);root['build_identity']=digest;iv.write_bytes(canonical_json_bytes(root))
    run=command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',tmp_path/'bad-build')
    assert run.returncode==3 and json.loads(run.stderr)['code']=='BUILD_IDENTITY_MISMATCH'
    root['build_identity']=build_path.name.split('.')[0]
    policy=json.loads((objects/(root['resource_policy']+'.nm.resource-policy.v1')).read_bytes())
    policy['id']='substituted';wire=canonical_json_bytes(policy);digest=hashlib.sha256(wire).hexdigest()
    (objects/(digest+'.nm.resource-policy.v1')).write_bytes(wire);root['resource_policy']=digest;iv.write_bytes(canonical_json_bytes(root))
    run=command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',tmp_path/'bad-policy')
    assert run.returncode==3 and json.loads(run.stderr)['code']=='RESOURCE_POLICY_IDENTITY_MISMATCH'


def test_closed_flags_and_cross_profile_dispatch(tmp_path):
    for args in [[],['--invocation','a','--invocation=b'],['--matrix','x'],['--inv','x']]:
        run=command('measurement-evaluate',*args)
        assert run.returncode==2 and not run.stdout
    thermal=tmp_path/'thermal';thermal.write_bytes(canonical_json_bytes({'schema_version':'bdw001.1'}))
    objects=tmp_path/'objects';objects.mkdir()
    run=command('measurement-evaluate','--invocation',thermal,'--objects-dir',objects,'--authority-pin','0'*64,'--output-dir',tmp_path/'foreign')
    assert run.returncode==3 and json.loads(run.stderr)['code']=='PROFILE_MISMATCH'


def test_legacy_unbound_computation_arguments_are_not_production_interfaces():
    import inspect
    from applications.bounded_decision_workflow import measurement_delivery
    for name in ['evaluate_semantic_bundle','replay_semantic_bundle']:
        assert not {'public_request','public_snapshot','support_rows','candidates','result','trace'} & set(inspect.signature(getattr(measurement_delivery,name)).parameters)


def test_logical_exact_limit_plus_one_and_shared_history(tmp_path):
    # Public inputs, not internal counter injection; build is the real executable.
    iv,objects,pin=recover_case(tmp_path,'CL-Q4-envelope')
    def run(limits,out):
        f=tmp_path/(out+'-limits.json');f.write_bytes(canonical_json_bytes(limits))
        return command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',tmp_path/out,'--limits',f)
    good=run({'request_chain':4},'four');assert good.returncode==0,good.stderr.decode()
    r=json.loads((tmp_path/'four'/'result.json').read_bytes())
    logical=r['accounting']['logical_required']
    assert logical['request_chain']==4 and logical['request_contexts']==4
    assert logical['reference_occurrences']>logical['unique_objects']
    bad=run({'request_chain':3},'three');assert bad.returncode==4
    assert json.loads(bad.stderr)['resource']=={'dimension':'request_chain','attempted':4,'limit':3}
    exact=run({'unique_objects':logical['unique_objects']},'exact');assert exact.returncode==0,exact.stderr.decode()
    insufficient=run({'unique_objects':logical['unique_objects']-1},'one-less');assert insufficient.returncode==4
    resource=json.loads(insufficient.stderr)['resource']
    assert resource['attempted']==logical['unique_objects'] and resource['limit']==logical['unique_objects']-1
    replay=command('measurement-replay','--bundle',tmp_path/'four','--output-dir',tmp_path/'history-replay')
    assert replay.returncode==0,replay.stderr.decode()


def test_exact_frozen_semantic_fields_and_full_accounting(tmp_path):
    iv,objects,pin=recover_case(tmp_path)
    out=tmp_path/'complete'
    run=command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',out)
    assert run.returncode==0,run.stderr.decode()
    result=json.loads((out/'result.json').read_bytes())
    expected=json.loads((PACKAGE/'expected/P/result.json').read_bytes())
    expected['invocation']=result['invocation']
    # The frozen oracle predates the executable witness. Only identity and
    # byte/graph demand change; no numerical outcome is generated by runtime.
    for field in expected.keys()-{'accounting'}:assert result[field]==expected[field],field
    capture=json.loads((out/'closure.json').read_bytes())
    wires=[base64.b64decode(m['bytes'],validate=True) for m in capture['members']]
    logical=result['accounting']['logical_required']
    assert set(logical)==set(expected['accounting']['logical_required'])
    assert logical['unique_bytes']==logical['capture_bytes']==sum(map(len,wires))
    assert logical['unique_objects']==len(wires)
    assert logical['closure_bytes']==len((out/'closure.json').read_bytes())
    manifest=json.loads((out/'manifest.json').read_bytes())
    assert manifest['physical']['bytes_written']==sum(x['bytes'] for x in manifest['files'])
    assert manifest['physical']['write_operations']==6
    assert manifest['physical']['status']=='observed_before_manifest_write'
    assert sum(p.stat().st_size for p in out.iterdir())<=1048576


def test_verify_rejects_rehashed_foreign_result_profile(tmp_path):
    iv,objects,pin=recover_case(tmp_path)
    out=tmp_path/'complete'
    run=command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',out)
    assert run.returncode==0,run.stderr.decode()
    result=json.loads((out/'result.json').read_bytes());result['profile']='thermal'
    wire=canonical_json_bytes(result);(out/'result.json').write_bytes(wire)
    m=json.loads((out/'manifest.json').read_bytes())
    for r in m['files']:
        if r['name']=='result.json':r.update(bytes=len(wire),sha256=hashlib.sha256(wire).hexdigest())
    (out/'manifest.json').write_bytes(canonical_json_bytes(m))
    checked=command('measurement-verify','--bundle',out)
    assert checked.returncode==3 and json.loads(checked.stderr)['code']=='PROFILE_MISMATCH'


def test_capture_rejects_path_replacement_after_read(tmp_path,monkeypatch):
    from applications.bounded_decision_workflow import measurement_runtime as runtime
    from applications.bounded_decision_workflow.measurement_wire import Work
    from applications.bounded_decision_workflow.measurement_contracts import MeasurementContractError
    path=tmp_path/'input.json';path.write_bytes(b'{}')
    original=runtime.retention._read_at
    def replaced(parent,name,cap,hook=None):
        captured=original(parent,name,cap,hook)
        other=tmp_path/'replacement';other.write_bytes(b'{}');other.replace(path)
        return captured
    monkeypatch.setattr(runtime.retention,'_read_at',replaced)
    with pytest.raises(MeasurementContractError) as error:runtime.read_path(path,'invocation_bytes',Work())
    assert error.value.code=='INPUT_CHANGED_DURING_READ'


def test_prepared_build_cannot_assert_executable_compatibility(tmp_path):
    iv,objects,pin=recover_case(tmp_path)
    root=json.loads(iv.read_bytes())
    prepared=next((PACKAGE/'objects').glob('*.nm.prepared-build.v1')).read_bytes()
    digest=hashlib.sha256(prepared).hexdigest()
    # Even presenting its actual bytes under the only allowed build filename
    # cannot promote the preparation witness into an executable identity.
    (objects/(digest+'.nm.build.v1')).write_bytes(prepared)
    root['build_identity']=digest;iv.write_bytes(canonical_json_bytes(root))
    bad=command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',tmp_path/'not-executable')
    assert bad.returncode==3 and json.loads(bad.stderr)['code']=='NONEXECUTABLE_BUILD_WITNESS'


def test_scoped_shared_edge_work_cannot_bypass_edge_budget(tmp_path):
    iv,objects,pin=recover_case(tmp_path)
    # P has 62 unique-graph edge occurrences in the frozen independent input
    # graph. Its per-request scope has additional edge checks; 62 is therefore
    # insufficient for the combined traversal work, although capture fits.
    limits=tmp_path/'edge-budget.json';limits.write_bytes(b'{"edge_visits":62}')
    run=command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,
                '--output-dir',tmp_path/'too-little-work','--limits',limits)
    assert run.returncode==4,run.stdout.decode()
    assert json.loads(run.stderr)['resource']=={'dimension':'edge_visits','attempted':63,'limit':62}
