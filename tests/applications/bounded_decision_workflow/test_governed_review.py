"""Kernel expectations derived from the approved law, not generated output."""
import json
import pytest
from applications.bounded_decision_workflow import governed_review as g, governed_build
from applications.bounded_decision_workflow.errors import WorkflowInputError
from .governed_fixtures import fixture,C,H,TEST_BUILD
BUILD=C({'schema':'test-only-build-not-executable'})

@pytest.fixture(autouse=True)
def build(monkeypatch):
    monkeypatch.setattr(governed_build,'identity',lambda **kw:(BUILD,H(BUILD)))

def run(name='W0',**kw):
    i,o,p=fixture(name)
    iv=json.loads(i);iv['build_identity']=H(BUILD);i=C(iv)
    return g.evaluate(i,o,expected_authority_pin=p,**kw)

@pytest.mark.parametrize('name,permission,selection',[
 ('W0',True,['aH']),('J1',True,['aH']),('D2-X',True,[]),
 ('X-denied',False,None),('beta-missing',False,None),
 ('applicability-unknown',False,None),('applicability-false',False,None),
 ('working-adopted',True,['aH']),('amended-unavailable',True,[])])
def test_outcomes(name,permission,selection):
    v=run(name);r=json.loads(v.result_bytes);t=json.loads(v.trace_bytes)
    assert r['admissibility']['evaluation_permitted'] is permission
    rows=r['decision_review']['rows'];assert len(rows)==23 and rows==t['rows']
    assert sum(x['performed'] for x in rows)==(23 if permission else 2)
    assert all(x['numeric_value_changed'] is None for x in rows)
    if permission:assert r['selection']['selected_action_ids']==selection
    else:assert all(x['value'] is None and not x['computed'] for x in rows[2:])

@pytest.mark.parametrize('name',['X-denied','applicability-unknown','beta-missing','missing-authority','stale-adoption'])
def test_no_denied_or_refused_dispatch(name,monkeypatch):
    from applications.bounded_decision_workflow import policy,projection
    monkeypatch.setattr(policy,'_assess_admitted',lambda *a,**k:pytest.fail('prohibited policy'))
    monkeypatch.setattr(projection,'_prepare_projection',lambda *a,**k:pytest.fail('prohibited projection'))
    if name in ['missing-authority','stale-adoption']:
        with pytest.raises(WorkflowInputError):run(name)
    else:run(name)

@pytest.mark.parametrize('a,b,comparable,change',[(1,1,True,False),(1,2,True,True),(1,None,False,None),(None,1,False,None),(None,None,False,None)])
def test_numeric_truth(a,b,comparable,change):
    def assess(n):return {'availability':'available' if n is not None else 'unavailable','status':'ready' if n is not None else 'unknown','diagnostics':[],
                          'numeric_kind':'supplied_cost' if n is not None else 'none','numeric_value':None if n is None else {'numerator':n,'denominator':1}}
    flags=g.compare_assessments(assess(b),assess(a))
    assert flags['numeric_comparable'] is comparable and flags['numeric_value_changed'] is change


def carry(review,build=BUILD):
    """Synthetic in-memory retention adapter for testing; no filesystem claim.

    Complete semantic outputs and kernel work counters are measured. Filesystem
    and timestamp metadata are fixture labels, not a publication or replay run.
    """
    z=json.loads(review.closure_bytes);table=z['objects'];iv=table[z['invocation']['sha256']]['canonical_json']
    s=table[iv['scenario']['sha256']]['canonical_json']
    files={'request.json':C(iv),'snapshot.json':C(table[s['snapshot']['sha256']]['canonical_json']),
           'resolved-input.json':review.closure_bytes,'result.json':review.result_bytes,'trace.json':review.trace_bytes,'build.json':build}
    r=json.loads(review.result_bytes);logical=r['resource_accounting']
    keys=['scope_expansions','edge_visits','context_nodes','context_bytes','lower_charges','lower_references',
          'lower_resolved_bytes','prior_capture_bytes','reconstruction_bytes','corner_evaluations','capture_bytes']
    measured=json.loads(review.physical_bytes)
    physical={'schema':'physical-work.v1','observed':True,'logical_commitment':H(C(logical)),
              'actual':measured['actual'],'extra':measured['extra'],'charged':measured['charged'],'cache_hits':0,
              'output_reserved_bytes':measured['output_reserved_bytes'],'coverage':'through_payloads_manifest_publication_reserved','checks':'all_effective_limits_checked_before_work'}
    manifest={'schema_version':'governed-bundle.v2','bundle_kind':'complete','operation':'evaluate','build_identity':H(build),
              'files':{k:{'bytes':len(v),'sha256':H(v)} for k,v in files.items()},
              'semantic_commitments':{k:H(files[k]) for k in ('result.json','trace.json')},
              'run_metadata':{'created_at_utc':'2026-09-16T00:00:00Z','filesystem':'ext4','operation_work':physical}}
    files['manifest.json']=C(manifest)
    return files


def next_world(name,prior,build=BUILD,**kw):
    i,o,p=fixture(name);iv=json.loads(i);iv['build_identity']=H(build)
    iv['comparison']={'kind':'prior-bundle-manifest','sha256':H(prior['manifest.json'])}
    return g.evaluate(C(iv),o,expected_authority_pin=p,prior_files=prior,**kw)


def test_complete_three_world_comparison(monkeypatch):
    from applications.bounded_decision_workflow import policy
    called=[];real=policy._assess_admitted
    def record(a,**kw):
        called.append(a.request_input.sha256)
        return real(a,**kw)
    monkeypatch.setattr(policy,'_assess_admitted',record)
    w=run();x=next_world('X-denied',carry(w));assert len(called)==2
    before=len(called);d=next_world('D2-X',carry(x))
    assert len(called)-before==2
    r=json.loads(d.result_bytes)
    assert r['selection']['disposition']=='no_feasible_action_in_supplied_set'
    assert r['resource_accounting']['lower_charges']==11847
    assert r['resource_accounting']['corner_evaluations']==16
    assert len(d.prior_results)==2
    assert sum(row['reevaluation']=='required' for row in r['decision_review']['rows'])==22
    assert all(not row['numeric_comparable'] for row in r['decision_review']['rows'])


def test_current_128_boundary():
    from .governed_fixtures import reference_boundary
    i,o,p=reference_boundary(128);iv=json.loads(i);iv['build_identity']=H(BUILD)
    assert json.loads(g.evaluate(C(iv),o,expected_authority_pin=p).result_bytes)['admissibility']['evaluation_permitted']


def test_result_trace_shapes():
    from applications.bounded_decision_workflow.governed_closure import schemas,shape
    defs=schemas()
    for name in ['W0','X-denied','amended-unavailable']:
        v=run(name)
        assert shape(json.loads(v.result_bytes),defs['result'],defs)
        assert shape(json.loads(v.trace_bytes),defs['trace'],defs)


def recommit(files):
    files=dict(files);m=json.loads(files['manifest.json'])
    m['files']={k:{'bytes':len(v),'sha256':H(v)} for k,v in files.items() if k!='manifest.json'}
    m['semantic_commitments']={k:H(files[k]) for k in ('result.json','trace.json')}
    files['manifest.json']=C(m);return files


@pytest.mark.parametrize('attack',['output','pin','work','recipe','edition'])
def test_carried_hostile_twins(attack,monkeypatch):
    files=carry(next_world('X-denied',carry(run())))
    if attack=='output':
        r=json.loads(files['result.json']);r['decision_review']['rows'][0]['value_changed']=False;files['result.json']=C(r)
    elif attack=='pin':
        z=json.loads(files['resolved-input.json']);z['expected_authority_pin']='0'*64;files['resolved-input.json']=C(z)
    elif attack=='work':
        m=json.loads(files['manifest.json']);m['run_metadata']['operation_work']['charged']['lower_charges']=0;files['manifest.json']=C(m)
    elif attack=='recipe':
        z=json.loads(files['resolved-input.json']);e=next(e for e in z['objects'].values() if 'recipe' in e);e['recipe']['members'].pop();files['resolved-input.json']=C(z)
    else:
        m=json.loads(files['manifest.json']);m['schema_version']='bdw001.1';files['manifest.json']=C(m)
    files=recommit(files)
    from applications.bounded_decision_workflow import policy
    monkeypatch.setattr(policy,'_assess_admitted',lambda *a,**k:pytest.fail('malformed prior reached numerical work'))
    with pytest.raises(WorkflowInputError):next_world('D2-X',files)


def test_review_numeric_available_and_unavailable():
    first=carry(run())
    j=next_world('J1',first);rows=json.loads(j.result_bytes)['decision_review']['rows']
    assert sum(r['reevaluation']=='required' for r in rows)==22
    assert sum(r['numeric_comparable'] for r in rows)==9
    u=next_world('amended-unavailable',first);rows=json.loads(u.result_bytes)['decision_review']['rows']
    assert all(not r['numeric_comparable'] and r['numeric_value_changed'] is None for r in rows)
    assert sum(r['performed'] for r in rows)==23
    assert rows[1]['computed'] is False


def test_changed_unavailability_reason():
    a={'availability':'unavailable','status':'unknown','diagnostics':[{'source':'observed','id':'observed:T0','reason':'observation_absent'}],'numeric_kind':'none','numeric_value':None}
    b=dict(a,diagnostics=[{'source':'observed','id':'observed:T0','reason':'evidence_not_assessable'}])
    flags=g.compare_assessments(b,a)
    assert flags['diagnostics_changed'] and not flags['numeric_comparable'] and flags['numeric_value_changed'] is None


def test_three_world_lower_boundary_before_dispatch(monkeypatch):
    files=carry(next_world('X-denied',carry(run())))
    next_world('D2-X',files,limits={'review_resolution_charges':11847})
    from applications.bounded_decision_workflow import policy
    monkeypatch.setattr(policy,'_assess_admitted',lambda *a,**k:pytest.fail('overbudget projection'))
    with pytest.raises(WorkflowInputError) as e:next_world('D2-X',files,limits={'review_resolution_charges':11846})
    assert e.value.diagnostic.exit_code==4


@pytest.mark.parametrize('name',['amended-four-0','amended-four-1','amended-four-2','amended-four-3','sharing-diamond','time-alias','presentation-alias'])
def test_valid_scope_twins(name):
    assert json.loads(run(name).result_bytes)['admissibility']['evaluation_permitted']


def test_129_refuses():
    from .governed_fixtures import reference_boundary
    i,o,p=reference_boundary(129);iv=json.loads(i);iv['build_identity']=H(BUILD)
    with pytest.raises(WorkflowInputError):g.evaluate(C(iv),o,expected_authority_pin=p)


def test_internal_observer_failure_is_not_success():
    def fail(event):raise RuntimeError('sink')
    with pytest.raises(WorkflowInputError):run(observer=fail)


@pytest.mark.parametrize('name,code',[
 ('missing-authority','AUTHORITY_UNAVAILABLE'),('beta-key-omitted','REQUEST_SCHEMA_INVALID'),
 ('fraction-alias-rejected','SUPPORT_MALFORMED'),('role-misuse','AUTHORITY_REFERENCE_MISMATCH'),
 ('stale-external-pin','AUTHORITY_REFERENCE_MISMATCH'),('missing-adoption','WORKING_ADOPTION_REQUIRED')])
def test_exact_refusal_contracts(name,code):
    with pytest.raises(WorkflowInputError) as e:run(name)
    assert e.value.diagnostic.code==code


def test_required_floor_cannot_be_offset_by_cache_savings():
    from applications.bounded_decision_workflow.governed_resources import Budget
    events=[];b=Budget({'context_nodes':10},events.append)
    b.require_floor({'context_nodes':10})
    with pytest.raises(WorkflowInputError):b.work('context_nodes',1,scope='extra-copy',extra=True)
    assert b.extra['context_nodes']==0
