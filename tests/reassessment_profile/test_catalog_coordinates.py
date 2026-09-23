"""Internal algorithm conformance, explicitly not filesystem admission proof."""
import base64
import json
import pytest
from test_capture import actual_case,bound_internal,graph,replace,key,ref,sha,wire
from applications.bounded_decision_workflow.measurement_contracts import MeasurementContractError
from applications.bounded_decision_workflow.measurement_wire import Work
from applications.bounded_decision_workflow.reassessment_capture import _walk
from applications.bounded_decision_workflow import reassessment_runtime as runtime

@pytest.mark.parametrize('adj',[{'a':['a']},{'a':['b'],'b':['a']}])
def test_actual_traversal_catalog_cycle(adj):
    with pytest.raises(MeasurementContractError,match='^CYCLE$'):
        _walk('a',lambda *args:None,lambda k:[('/edge',v) for v in adj[k]],Work())

def test_captured_identity_catalog():
    c,p=bound_internal('P1-point60');qk=next(k for k in p if k[0]=='nm.request.v1');q=json.loads(p[qk])
    h=json.loads(p[key(q['hypotheses'][0])]);h['account_kind']='low_underlying_positive_offset'
    b=wire(h);r=ref(h['schema'],sha(b));p[key(r)]=b;q['hypotheses'][1]=r;replace(c,p,qk,q)
    with pytest.raises(MeasurementContractError,match='^IDENTITY_COLLISION$'):graph(c,p)

def test_retained_closure_catalog(monkeypatch):
    c,p=actual_case('P1-point60');g=graph(c,p);g.closure_bytes=g.closure(c['authority_pin'])
    files=runtime._payloads(g);closure=json.loads(files['closure.json'])
    raw=b'{}';closure['members'].append(dict(reference=ref('nm.basis',sha(raw)),encoding='base64',bytes=base64.b64encode(raw).decode()))
    closure['members'].sort(key=lambda x:key(x['reference']));files['closure.json']=wire(closure)
    # Bypass only the owning file-integrity layer in this internal test; the
    # public D-extra-closure matrix command remains a separate obligation.
    monkeypatch.setattr(runtime,'inspect_bundle',lambda *args:files)
    with pytest.raises(MeasurementContractError,match='^EXTRANEOUS_CLOSURE_MEMBER$'):
        runtime._retained('unused-internal-path')
