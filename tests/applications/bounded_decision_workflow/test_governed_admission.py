"""Pure first-slice tests; no projection, CLI or bundle publication."""
import json
import pytest
from applications.bounded_decision_workflow import governed_admission as g
from applications.bounded_decision_workflow import governed_build as build
from applications.bounded_decision_workflow.governed_resources import Budget, Traversal
from applications.bounded_decision_workflow.errors import WorkflowInputError
from applications.bounded_decision_workflow.input import BUILD_LIMITS
from .governed_fixtures import C,H,TEST_BUILD,fixture,reference_boundary

@pytest.fixture(autouse=True)
def unit_build(monkeypatch):
    monkeypatch.setattr(build,'identity',lambda **kw:(TEST_BUILD,H(TEST_BUILD)))

def run(name='W0',**kw):
    i,o,p=fixture(name);return g.assess(i,o,expected_authority_pin=p,**kw)

@pytest.mark.parametrize('name,disposition',[
 ('W0','admissible'),('J1','admissible'),('X-denied','inadmissible'),
 ('time-alias','admissible'),('presentation-alias','admissible'),
 ('applicability-unknown','applicability_unknown'),('applicability-false','declaration_not_applicable'),
 ('beta-missing','admissibility_unknown'),('fixed-policy-changed','declaration_not_applicable'),
 ('issuer-context-changed','declaration_not_applicable'),('working-adopted','admissible'),
 ('D2-W0','admissible'),('D2-X','admissible'),('sharing-diamond','admissible'),
 ('four-pair-cap-valid','admissible'),('amended-four-0','admissible'),
 ('amended-four-1','admissible'),('amended-four-2','admissible'),('amended-four-3','admissible'),
 ('amended-unavailable','admissible')])
def test_gate_twins(name,disposition,monkeypatch):
    from applications.bounded_decision_workflow import projection,policy
    monkeypatch.setattr(projection,'_prepare_projection',lambda *a,**kw:pytest.fail('projection reached'))
    monkeypatch.setattr(policy,'_assess_admitted',lambda *a,**kw:pytest.fail('policy reached'))
    a=run(name)
    assert a.disposition==disposition and a.evaluation_permitted==(disposition=='admissible')
    assert a.scope=='pure_nomination_not_workflow'
    assert len(a.physical_bytes)<=8192

@pytest.mark.parametrize('name,code',[
 ('missing-authority','AUTHORITY_UNAVAILABLE'),('stale-external-pin','AUTHORITY_REFERENCE_MISMATCH'),
 ('missing-adoption','WORKING_ADOPTION_REQUIRED'),('stale-adoption','AUTHORITY_REFERENCE_MISMATCH'),
 ('fraction-alias-rejected','SUPPORT_MALFORMED'),('beta-key-omitted','REQUEST_SCHEMA_INVALID'),
 ('time-unknown-offset','WORLD_REPRESENTATION_UNSUPPORTED'),
 ('changed-cutoff-public-mismatch','OBSERVATION_BINDING_MISMATCH'),
 ('snapshot-commitment-mismatch','SNAPSHOT_COMMITMENT_MISMATCH'),
 ('role-misuse','AUTHORITY_REFERENCE_MISMATCH'),('duplicate-pairs','DECLARATION_SCHEMA_INVALID'),
 ('empty-domain','DECLARATION_SCHEMA_INVALID'),('five-pairs','DECLARATION_SCHEMA_INVALID'),
 ('stale-declaration','AUTHORITY_REFERENCE_MISMATCH'),('adoption-on-hypothetical','AUTHORITY_REFERENCE_MISMATCH'),
 ('non-singleton-box','GOVERNED_PROFILE_UNSUPPORTED'),('revision-gap','HISTORY_INCOMPATIBLE')])
def test_refusal_twins(name,code):
    with pytest.raises(WorkflowInputError) as e:run(name)
    assert e.value.diagnostic.code==code

def test_determinism_and_presentation():
    i,o,p=fixture();a=g.assess(i,o,expected_authority_pin=p)
    b=g.assess(i,list(reversed(o)),expected_authority_pin=p)
    assert a.semantic_bytes==b.semantic_bytes
    assert a.world_key==run('time-alias').world_key==run('presentation-alias').world_key
    assert a.world_key!=run('J1').world_key
    assert a.fixed_key==run('J1').fixed_key==run('X-denied').fixed_key

def test_no_build_or_version_fallback():
    i,o,p=fixture();v=json.loads(i);v['build_identity']='0'*64
    with pytest.raises(WorkflowInputError):g.assess(C(v),o,expected_authority_pin=p)
    v['schema']='bdw001.1'
    with pytest.raises(WorkflowInputError):g.assess(C(v),o,expected_authority_pin=p)
    assert BUILD_LIMITS['decision_rows']==22 and BUILD_LIMITS['input_resolution_charges']==8192

def test_omitted_pin_and_changed_content():
    i,o,p=fixture()
    with pytest.raises(WorkflowInputError):g.assess(i,o,expected_authority_pin=None)
    v=json.loads(i);v['selection']['sha256']='0'*64
    with pytest.raises(WorkflowInputError):g.assess(C(v),o,expected_authority_pin=p)
    with pytest.raises(WorkflowInputError):g.assess(i+b'\n',o,expected_authority_pin=p)

def test_current_boundary_before_work():
    events=[];b=Budget(observer=events.append)
    for _ in range(128):b.work('supplied_references',1,scope='synthetic-edge-counter')
    assert b.logical['supplied_references']==128
    with pytest.raises(WorkflowInputError):b.work('supplied_references',1,scope='synthetic-edge-counter')
    assert b.logical['supplied_references']==128
    assert events[-1]['outcome']=='refused' and events[-1]['before']==128
    assert all(x['after']<=128 for x in events if x['dimension']=='supplied_references' and x['outcome']=='completed')

def test_sharing_active_cycles_and_scopes():
    b=Budget();t=Traversal(b)
    with t.enter('root','full'):
        with t.enter('leaf','request'):pass
        with t.enter('leaf','request') as fresh:assert not fresh
        with t.enter('leaf','snapshot') as fresh:assert fresh
        with pytest.raises(WorkflowInputError):
            with t.enter('root','other-role'):pass
        with t.enter('middle','full'):
            with pytest.raises(WorkflowInputError):
                with t.enter('root','full'):pass
    assert b.physical['cache_hits']==1

def test_lower_guard_before_reconstruction(monkeypatch):
    from applications.bounded_decision_workflow import admission
    monkeypatch.setattr(admission,'_admit_parsed',lambda *a:pytest.fail('prohibited reconstruction'))
    with pytest.raises(WorkflowInputError) as e:run(limits={'review_resolution_charges':3948})
    assert e.value.diagnostic.exit_code==4

def test_caller_cannot_raise_cap():
    with pytest.raises(WorkflowInputError):run(limits={'supplied_references':129})

def test_physical_operation_evidence():
    events=[];a=run(observer=events.append)
    p=json.loads(a.physical_bytes)
    assert p['operations']['public_reconstruction']['completed']==1
    assert p['operations']['decode_object']['completed']>0
    assert p['operations']['membership']['completed']==1
    assert p['operations']['graph_validation']['completed']==1
    assert p['operations']['envelope_validation']['completed']==1
    assert any(e['phase']=='operation' and e['scope']=='public_reconstruction' and e['outcome']=='started' for e in events)
    assert all(len(C(e))<=512 for e in events)

def test_reference_array_order_is_numeric():
    from applications.bounded_decision_workflow.governed_contracts import edges,D
    v={'schema':D,'provenance':{'basis_artifacts':[{'kind':'captured-basis','sha256':f'{i:064x}'} for i in range(12)]}}
    assert [int(e[1]['sha256'],16) for e in edges(D,v)]==list(range(12))

def test_observer_failure_cannot_complete():
    def fail(e):raise RuntimeError('sink failure')
    with pytest.raises(WorkflowInputError) as e:run(observer=fail)
    assert e.value.diagnostic.exit_code==7

@pytest.mark.parametrize('limits',[{'lower_nodes_per_file':1},{'membership_rows':1},{'input_json_depth':1},{'input_max_string_bytes':1}])
def test_all_applicable_tightened_guards(limits):
    with pytest.raises(WorkflowInputError) as e:run(limits=limits)
    assert e.value.diagnostic.exit_code==4

def test_diagnostic_state_and_stage():
    from applications.bounded_decision_workflow.governed_resources import problem
    from applications.bounded_decision_workflow.terminal import diagnostic_line
    e=problem('OUTPUT_LIMIT_EXCEEDED',resource=True,target='build_bytes')
    line,exit=diagnostic_line(e.diagnostic)
    assert len(line)<=512 and exit==4
    assert json.loads(line)['stage']=='output_resource'
    assert json.loads(line)['bundle_state']=='absent'

@pytest.mark.parametrize('bad',[b'[]',b'{}',b'{"schema":"governed-scenario.v1"}'])
def test_malformed_outer_objects_are_typed_refusals(bad):
    i,o,p=fixture();o.append(('governed-scenario.v1',bad))
    with pytest.raises(WorkflowInputError):g.assess(i,o,expected_authority_pin=p)

def test_malformed_capture_record():
    i,o,p=fixture();o.append(('governed-scenario.v1',))
    with pytest.raises(WorkflowInputError):g.assess(i,o,expected_authority_pin=p)

def test_instrumentation_stops_before_full_serialization(monkeypatch):
    from applications.bounded_decision_workflow import governed_resources as resource
    b=Budget(limits={'physical_evidence_bytes':1})
    monkeypatch.setattr(resource,'canonical_json_bytes',lambda value:pytest.fail('unbounded complete summary allocation'))
    with pytest.raises(WorkflowInputError) as e:b.summary()
    assert e.value.diagnostic.code=='OUTPUT_LIMIT_EXCEEDED'

def test_partial_slice_does_not_claim_comparison():
    i,o,p=fixture();v=json.loads(i)
    v['comparison']={'kind':'prior-bundle-manifest','sha256':'0'*64}
    with pytest.raises(WorkflowInputError) as e:g.assess(C(v),o,expected_authority_pin=p)
    assert e.value.diagnostic.code=='HISTORY_INCOMPATIBLE'

def test_no_favorable_refund_for_extra_work():
    b=Budget();b.work('review_resolution_charges',11847,scope='synthetic-three-context-counter')
    b.work('review_resolution_charges',441,scope='synthetic-extra',extra=True)
    with pytest.raises(WorkflowInputError):b.work('review_resolution_charges',1,scope='synthetic-extra',extra=True)
    assert b.logical['review_resolution_charges']==11847 and b.extra['review_resolution_charges']==441

def test_hash_valid_128_129_reference_twins():
    i,o,p=reference_boundary(128);a=g.assess(i,o,expected_authority_pin=p)
    assert a.evaluation_permitted
    assert json.loads(a.semantic_bytes)['logical']['supplied_references']==128
    i,o,p=reference_boundary(129)
    with pytest.raises(WorkflowInputError) as e:g.assess(i,o,expected_authority_pin=p)
    assert e.value.diagnostic.code=='GRAPH_REFERENCE_LIMIT_EXCEEDED'

def test_zero_byte_copies_are_not_free():
    b=Budget(limits={'context_nodes':2})
    with pytest.raises(WorkflowInputError):g._Captured([('captured-basis',b'')]*3,b)

def test_missing_policy_is_typed_build_refusal(monkeypatch,tmp_path):
    from applications.bounded_decision_workflow import governed_resources as r
    monkeypatch.setattr(r,'ROOT',tmp_path)
    with pytest.raises(WorkflowInputError) as e:r.policy()
    assert e.value.diagnostic.code=='REPLAY_BUILD_UNAVAILABLE'

def test_measurement_harness_observes_forbidden_dispatch(monkeypatch):
    from . import measure_governed_slice as m
    from applications.bounded_decision_workflow import projection
    monkeypatch.setattr(m,'_measure',lambda:projection._prepare_projection(),raising=False)
    with pytest.raises(AssertionError,match='outside pure slice'):m.measure()
