"""Governed command contract; actual clean-build subprocess coverage below."""
import json
from types import SimpleNamespace
import pytest
from applications.bounded_decision_workflow import cli, governed_build
from applications.bounded_decision_workflow.errors import WorkflowInputError
from .governed_fixtures import fixture,C,H
BUILD=C({'schema':'test-only-build-not-executable'})

def test_explicit_governed_usage_no_legacy_fallback():
    a=cli._arguments(['governed-evaluate','--invocation','i','--objects-dir','o','--authority-pin','0'*64,'--output-dir','r'])
    assert a.operation=='governed-evaluate'
    for args in [['governed-evaluate'],['evaluate','--invocation','i'],['governed-replay','--bundle','b']]:
        with pytest.raises(WorkflowInputError):cli._arguments(args)

def prepare(tmp_path,name='W0'):
    i,o,pin=fixture(name);v=json.loads(i);v['build_identity']=H(BUILD)
    q=tmp_path/'invocation.json';q.write_bytes(C(v));d=tmp_path/'objects';d.mkdir()
    for kind,b in o:(d/(H(b)+'.'+kind)).write_bytes(b)
    return SimpleNamespace(operation='governed-evaluate',invocation=str(q),objects_dir=str(d),authority_pin=pin,output_dir=str(tmp_path/'result'),compare_to=None)

@pytest.mark.parametrize('name,permission',[('W0',True),('X-denied',False),('applicability-unknown',False),('amended-unavailable',True)])
def test_command_composition(tmp_path,monkeypatch,name,permission):
    monkeypatch.setattr(governed_build,'identity',lambda **kw:(BUILD,H(BUILD)))
    args=prepare(tmp_path,name);receipt=cli.execute(args)
    assert set(receipt)=={'operation','evaluation_permitted','disposition','result_commitment','bundle_commitment'}
    assert receipt['evaluation_permitted'] is permission
    r=json.loads((tmp_path/'result/result.json').read_bytes())
    assert r['admissibility']['evaluation_permitted'] is permission
    receipt=cli.execute(SimpleNamespace(operation='governed-verify',bundle=args.output_dir))
    assert set(receipt)=={'operation','integrity_state','bundle_commitment'}
    receipt=cli.execute(SimpleNamespace(operation='governed-replay',bundle=args.output_dir,output_dir=str(tmp_path/'replay')))
    assert receipt['evaluation_permitted'] is permission

def test_wrong_pin_before_projection(tmp_path,monkeypatch):
    from applications.bounded_decision_workflow import policy
    monkeypatch.setattr(governed_build,'identity',lambda **kw:(BUILD,H(BUILD)))
    args=prepare(tmp_path);args.authority_pin='0'*64
    monkeypatch.setattr(policy,'_assess_admitted',lambda *a,**kw:pytest.fail('prohibited numerical work'))
    with pytest.raises(WorkflowInputError) as e:cli.execute(args)
    assert e.value.diagnostic.code=='AUTHORITY_REFERENCE_MISMATCH'
    assert not (tmp_path/'result').exists()
