"""Real byte/recipe reconstruction; frozen preparation is not runtime evidence."""
import json
import pytest
from .governed_fixtures import recovered,C,H
from applications.bounded_decision_workflow import governed_closure as closure
from applications.bounded_decision_workflow.errors import WorkflowInputError
from applications.bounded_decision_workflow.governed_resources import Budget


def carried(name='D2-X'):
    objects,cases=recovered()
    iv=json.loads(objects[cases['amended-'+name]['invocation']['sha256']][1])
    manifest=json.loads(objects[iv['comparison']['sha256']][1])
    files={k:objects[v['sha256']][1] for k,v in manifest['files'].items()}
    files['manifest.json']=C(manifest)
    return iv,files


def test_complete_carried_recipe_reconstruction():
    iv,files=carried();events=[]
    c=closure.validate_carried(files,expected_manifest=iv['comparison']['sha256'],
                               expected_build=files['build.json'],budget=Budget(observer=events.append))
    assert len(c.worlds)==2
    assert c.files['manifest.json']==files['manifest.json']
    assert c.reconstructed_bytes==sum(sum(map(len,w.files.values())) for w in c.worlds)
    assert all(len(w.files)==7 for w in c.worlds)


@pytest.mark.parametrize('name',['build.json','request.json','snapshot.json','resolved-input.json','result.json','trace.json','manifest.json'])
def test_each_file_is_required(name):
    iv,files=carried();files.pop(name)
    with pytest.raises(WorkflowInputError):closure.validate_carried(files,expected_manifest=iv['comparison']['sha256'],expected_build=b'{}',budget=Budget())


def test_tamper_and_build_twins():
    iv,files=carried()
    with pytest.raises(WorkflowInputError):closure.validate_carried(files,expected_manifest='0'*64,expected_build=files['build.json'],budget=Budget())
    with pytest.raises(WorkflowInputError):closure.validate_carried(files,expected_manifest=iv['comparison']['sha256'],expected_build=b'{}',budget=Budget())
    files['trace.json']+=b' '
    with pytest.raises(WorkflowInputError):closure.validate_carried(files,expected_manifest=iv['comparison']['sha256'],expected_build=files['build.json'],budget=Budget())


def test_prior_capture_refuses_before_json(monkeypatch):
    iv,files=carried()
    monkeypatch.setattr(closure,'decode_file',lambda *a,**k:pytest.fail('decode after refused capture'))
    with pytest.raises(WorkflowInputError):closure.validate_carried(files,expected_manifest=iv['comparison']['sha256'],expected_build=files['build.json'],budget=Budget({'prior_capture_bytes':1}))


def test_ordered_rows_apply_all_closed_predicates():
    defs=closure.schemas()
    assert not closure.shape([{}]*23,defs['rows'],defs)
    iv,files=carried();r=json.loads(files['result.json'])
    r['decision_review']['rows'][0]['unexpected']=True
    assert not closure.shape(r,defs['result'],defs)
