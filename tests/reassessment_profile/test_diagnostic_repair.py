"""Focused decoder-coordinate and test-harness export-accounting checks."""
import json
from pathlib import Path
import zipfile
import pytest
import qualification as budget
from test_capture import structural, PACKAGE
from applications.bounded_decision_workflow.measurement_contracts import MeasurementContractError

@pytest.mark.parametrize('name',['P4-gap','P4-overlap','P4-remote_gap'])
def test_decoder_owning_target(name):
    with zipfile.ZipFile(PACKAGE) as z:
        expected=json.loads(z.read('cases/'+name+'/stderr.expected'))
    with pytest.raises(MeasurementContractError) as caught:structural(name)
    e=caught.value
    assert (e.code,e.stage,e.target)==(expected['code'],expected['stage'],expected['target']['field'])
    assert e.details['request']==expected['target']['request']
    assert e.details['references']==expected['target']['references']

def test_decoder_partition_valid_twin():
    assert structural('P4-partition').objects

def test_revision_policy_target_is_captured_revision():
    with zipfile.ZipFile(PACKAGE) as z:
        expected=json.loads(z.read('cases/P10-fifth/stderr.expected'))
    with pytest.raises(MeasurementContractError) as caught:structural('P10-fifth')
    e=caught.value
    assert e.target=='/revision'
    assert e.details['request']==expected['target']['request']
    assert {k:e.details[k] for k in ('dimension','attempted','limit')}==expected['resource']
    assert e.code=='RESOURCE_LIMIT_EXCEEDED' and e.stage=='phase_2'

@pytest.mark.parametrize('name', ['P9-context', 'P10b-external',
    'P10-rational129', 'P10-context9', 'P10-objects129'])
def test_refusal_preserves_owning_request(name):
    from applications.bounded_decision_workflow.reassessment_admission import admit
    with zipfile.ZipFile(PACKAGE) as z:
        expected=json.loads(z.read('cases/'+name+'/stderr.expected'))
    with pytest.raises(MeasurementContractError) as caught:
        admit(structural(name))
    e=caught.value
    assert (e.code,e.stage,e.target)==(expected['code'],expected['stage'],expected['target']['field'])
    assert e.details['request']==expected['target']['request']

@pytest.fixture
def isolated_budget(tmp_path,monkeypatch):
    root=tmp_path/'corpus';root.mkdir()
    for k in budget.CAPS:(root/k).mkdir()
    (root/'indexes'/'0000-identity.json').write_bytes(b'{}')
    monkeypatch.setattr(budget,'ROOT',root)
    return tmp_path/'export.md'

def test_export_charged_before_create(isolated_budget,monkeypatch):
    path=isolated_budget;original=Path.open;seen=[]
    def opened(p,mode='r',*a,**kw):
        if p==path and mode=='xb':
            seen.append(budget.census()['categories']['exports'])
            assert seen[-1]==5 and not path.exists()
        return original(p,mode,*a,**kw)
    monkeypatch.setattr(Path,'open',opened)
    budget.publish_export(path,b'hello')
    assert seen==[5] and path.read_bytes()==b'hello'
    assert budget.census()['categories']['exports']==5
    with pytest.raises(AssertionError):budget.publish_export(path,b'other')
    assert path.read_bytes()==b'hello'

def test_export_reservation_denial_writes_nothing(isolated_budget,monkeypatch):
    before=list((budget.ROOT/'indexes').iterdir())
    def denied(*a,**kw):raise AssertionError('reservation denied')
    monkeypatch.setattr(budget,'reserve',denied)
    with pytest.raises(AssertionError):budget.publish_export(isolated_budget,b'hello')
    assert not isolated_budget.exists()
    assert list((budget.ROOT/'indexes').iterdir())==before

def test_interrupted_export_retains_charge(isolated_budget,monkeypatch):
    original=Path.open
    def opened(p,mode='r',*a,**kw):
        if p==isolated_budget and mode=='xb':raise OSError('test-only interruption')
        return original(p,mode,*a,**kw)
    monkeypatch.setattr(Path,'open',opened)
    with pytest.raises(OSError):budget.publish_export(isolated_budget,b'hello')
    assert not isolated_budget.exists()
    assert budget.census()['categories']['exports']==5
