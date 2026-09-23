"""Public closure boundary twins; observations do not replace captured bytes."""
import hashlib
import json
from pathlib import Path
import pytest
from applications.bounded_decision_workflow import measurement_runtime as runtime
from applications.bounded_decision_workflow.measurement_contracts import canonical_json_bytes as wire, MeasurementContractError
from tests.measurement_profile.test_delivery_contract_mapping import recover_case, command


def test_history_guard_precedes_fifth_revision_dependency_work(tmp_path,monkeypatch):
    iv,objects,pin=recover_case(tmp_path,'CL-Q5-refused')
    reads=[];original=runtime._read
    def observe(fd,name,cap,work,*args,**kw):
        reads.append(name);return original(fd,name,cap,work,*args,**kw)
    monkeypatch.setattr(runtime,'_read',observe)
    with pytest.raises(MeasurementContractError) as error:runtime.evaluate(iv,objects,pin,tmp_path/'refused')
    assert error.value.code=='RESOURCE_LIMIT_EXCEEDED'
    assert error.value.details['dimension']=='request_chain'
    assert not any(n.endswith(('.nm.evidence.v1','.nm.hypothesis.v1','.nm.support.v1')) for n in reads),reads
    assert not (tmp_path/'refused').exists()


def context_twin(root,count):
    iv,objects,pin=recover_case(root)
    def get(r):return json.loads((objects/(r['sha256']+'.'+r['kind'])).read_bytes())
    def put(v):
        b=wire(v);r=dict(kind=v['schema'],sha256=hashlib.sha256(b).hexdigest());(objects/(r['sha256']+'.'+r['kind'])).write_bytes(b);return r
    i=json.loads(iv.read_bytes());q=get(i['request']);a=get(i['selection']);d=get(a['declaration']);requests=[i['request']]
    for n in range(1,count):requests.append(put(dict(q,id='Q-resource-'+str(n))))
    d['requests']=sorted(requests,key=lambda r:(r['kind'],r['sha256']));a['declaration']=put(d);i['selection']=put(a);iv.write_bytes(wire(i))
    return iv,objects,i['selection']['sha256']


def test_eight_contexts_valid_and_ninth_context_refuses_without_partial_success(tmp_path):
    for count in [8,9]:
        root=tmp_path/str(count);root.mkdir();iv,objects,pin=context_twin(root,count);out=root/'result'
        run=command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',out)
        if count==8:
            assert run.returncode==0,run.stderr
            result=json.loads((out/'result.json').read_bytes())
            assert result['accounting']['logical_required']['request_contexts']==8
            assert [s['worst'] for s in result['ranking']['scores']]==[1,2]
        else:
            assert run.returncode==4,run.stderr
            assert json.loads(run.stderr)['resource']==dict(dimension='request_contexts',attempted=9,limit=8)
            assert not out.exists()
