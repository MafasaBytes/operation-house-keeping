"""Slice 3 owning persistence twins; test-only build provider, no release claim."""
import json
import pytest
from applications.bounded_decision_workflow import governed_persistence as p
from applications.bounded_decision_workflow import governed_build, governed_review, policy
from applications.bounded_decision_workflow.errors import WorkflowInputError
from .governed_fixtures import fixture,C,H,ROOT
from applications.bounded_decision_workflow.build import LOCK,PUBLIC
from applications.bounded_decision_workflow.governed_resources import policy as limits,POLICY_SHA

# Structural record only, supplied by an explicitly patched unit-test provider.
# It is NOT an executable witness: the source paths/commit below are synthetic.
# Real command acceptance always derives the unpatched exact executable identity.
BUILD=C({'schema':'governed-executable-build.v1','git_commit':'0'*40,
 'implementation_id':'bdw.governed-application.v1','inner_schema':'bdw001.1',
 'workflow_profile':'hypothetical_enclosure_one_step.v1','build_policy_id':'bdw.governed-resource-policy.v1',
 'application_source_sha256':{'applications/test_only_not_an_executable.py':'0'*64},
 'backend_source_inventory_sha256':'0'*64,'public_module_sha256':{p:'0'*64 for p in PUBLIC},
 'python':{'implementation':'CPython','version':'3.13.11'},
 'dependencies':dict(line.split('==') for line in (ROOT/LOCK).read_text().splitlines()),
 'dependency_lock_sha256':H((ROOT/LOCK).read_bytes()),'contract_source_sha256':governed_build.CONTRACTS,
 'policy_file_sha256':POLICY_SHA,'limit_policy_sha256':H(C(limits()))})

@pytest.fixture(autouse=True)
def build(monkeypatch):
    monkeypatch.setattr(governed_build,'identity',lambda **kw:(BUILD,H(BUILD)))

def run(name='W0',prior=None):
    i,o,pin=fixture(name);v=json.loads(i);v['build_identity']=H(BUILD)
    v['comparison']=None if prior is None else {'kind':'prior-bundle-manifest','sha256':H(prior['manifest.json'])}
    return governed_review.evaluate(C(v),o,expected_authority_pin=pin,prior_files=prior)

def test_publish_recover_no_overwrite(tmp_path):
    review=run();path=tmp_path/'w0'
    result=p.publish(path,review)
    assert result.integrity_state=='complete_bundle'
    got=p.capture_bundle(path)
    assert dict(got.captured)==dict(result.captured)
    assert len(got.captured)==7
    assert p.verify(path).manifest_sha256==result.manifest_sha256
    with pytest.raises(WorkflowInputError) as e:p.publish(path,review)
    assert e.value.diagnostic.code=='OUTPUT_COLLISION'

@pytest.mark.parametrize('stage,code',[
 ('write','RETENTION_WRITE_FAILED'),('file_fsync','RETENTION_FILE_FSYNC_FAILED'),
 ('manifest_before_rename','RETENTION_MANIFEST_FAILED'),
 ('directory_fsync','RETENTION_DIR_FSYNC_FAILED'),('parent_fsync','RETENTION_PARENT_FSYNC_FAILED')])
def test_fault_visible_not_success(tmp_path,stage,code):
    def fail(s,n):
        if s==stage:raise OSError('controlled')
    path=tmp_path/'fault'
    with pytest.raises(WorkflowInputError) as e:p.publish(path,run(),fault=fail)
    assert e.value.diagnostic.code==code
    if stage in ('directory_fsync','parent_fsync'):assert p.verify(path).integrity_state=='complete_bundle'
    else:
        with pytest.raises(WorkflowInputError):p.verify(path)

def test_integrity_not_permission_or_computation(tmp_path,monkeypatch):
    path=tmp_path/'denied';v=run('X-denied');p.publish(path,v)
    monkeypatch.setattr(policy,'_assess_admitted',lambda *a,**kw:pytest.fail('verify must not project'))
    assert p.verify(path).integrity_state=='complete_bundle'
    (path/'result.json').write_bytes(b'{}')
    with pytest.raises(WorkflowInputError):p.verify(path)

def test_full_comparison_recovery(tmp_path):
    a=p.publish(tmp_path/'w',run());b=p.publish(tmp_path/'x',run('X-denied',dict(a.captured)))
    d=p.publish(tmp_path/'d',run('D2-X',dict(b.captured)))
    assert p.verify(tmp_path/'d').integrity_state=='complete_bundle'
    assert len(d.captured['resolved-input.json'])<=262144
    assert sum(map(len,d.captured.values()))<=393216

def test_replay_recomputes_and_preserves_historical_denial(tmp_path,monkeypatch):
    a=p.publish(tmp_path/'w',run());b=p.publish(tmp_path/'x',run('X-denied',dict(a.captured)))
    p.publish(tmp_path/'d',run('D2-X',dict(b.captured)))
    calls=[];real=policy._assess_admitted
    def record(a,**kw):calls.append(a.request_input.sha256);return real(a,**kw)
    monkeypatch.setattr(policy,'_assess_admitted',record)
    replay=p.replay(tmp_path/'x',tmp_path/'replay')
    assert len(calls)==1 # Historical W0 only; denied X never enters.
    for name in ('request.json','result.json','trace.json','resolved-input.json'):
        assert replay.captured[name]==b.captured[name]
    assert json.loads(replay.captured['manifest.json'])['operation']=='replay'

def test_replay_three_world_complete(tmp_path):
    a=p.publish(tmp_path/'w',run());b=p.publish(tmp_path/'x',run('X-denied',dict(a.captured)))
    d=p.publish(tmp_path/'d',run('D2-X',dict(b.captured)))
    r=p.replay(tmp_path/'d',tmp_path/'r')
    assert r.captured['result.json']==d.captured['result.json']

def test_missing_publication_reservation_refuses(tmp_path):
    path=tmp_path/'w';p.publish(path,run())
    m=json.loads((path/'manifest.json').read_bytes());m['run_metadata']['operation_work']['output_reserved_bytes']=0
    (path/'manifest.json').write_bytes(C(m))
    with pytest.raises(WorkflowInputError):p.verify(path)

def test_caller_tight_retention_is_not_waived(tmp_path):
    from applications.bounded_decision_workflow.input import BUILD_LIMITS
    i,o,pin=fixture();iv=json.loads(i);db={H(b):(k,json.loads(b)) for k,b in o}
    s=db[iv['scenario']['sha256']][1];a=db[iv['selection']['sha256']][1];q=db[s['request']['sha256']][1]
    q['requested_limits']=dict(BUILD_LIMITS,retention_bundle_bytes=1)
    s['request']={'kind':'bdw001.1','sha256':H(C(q))};sr={'kind':'governed-scenario.v1','sha256':H(C(s))}
    a['scenario']=sr;ar={'kind':'local-authority-selection.v1','sha256':H(C(a))}
    iv.update(scenario=sr,selection=ar,build_identity=H(BUILD))
    o += [('bdw001.1',C(q)),(sr['kind'],C(s)),(ar['kind'],C(a))]
    # Full requested_limits also tightens result nodes to legacy 1024. The
    # earlier bounded output refusal legitimately wins over publication.
    with pytest.raises(WorkflowInputError) as e:
        review=governed_review.evaluate(C(iv),o,expected_authority_pin=ar['sha256'])
        p.publish(tmp_path/'small',review)
    assert e.value.diagnostic.code=='OUTPUT_LIMIT_EXCEEDED'
    assert not (tmp_path/'small').exists()

def test_replay_checks_computation_not_only_hashes(tmp_path):
    path=tmp_path/'w';p.publish(path,run())
    r=json.loads((path/'result.json').read_bytes());r['selection']['selected_action_ids']=['aF']
    (path/'result.json').write_bytes(C(r))
    m=json.loads((path/'manifest.json').read_bytes());b=C(r)
    m['files']['result.json']={'bytes':len(b),'sha256':H(b)};m['semantic_commitments']['result.json']=H(b)
    (path/'manifest.json').write_bytes(C(m))
    assert p.verify(path).integrity_state=='complete_bundle' # Not a semantic claim.
    with pytest.raises(WorkflowInputError) as e:p.replay(path,tmp_path/'bad-replay')
    assert e.value.diagnostic.code=='REPLAY_SEMANTIC_MISMATCH'
    assert not (tmp_path/'bad-replay').exists()

@pytest.mark.parametrize('attack',['symlink','incomplete','extra-file','changed-during-read','overbudget-work'])
def test_persistent_hostile_twins(tmp_path,attack):
    path=tmp_path/'w';p.publish(path,run());fault=None
    if attack=='symlink':
        old=(path/'build.json').read_bytes();(path/'build.json').unlink();(tmp_path/'outside').write_bytes(old);(path/'build.json').symlink_to(tmp_path/'outside')
    elif attack=='incomplete':(path/'manifest.json').rename(path/'.manifest.json.tmp')
    elif attack=='extra-file':(path/'extra').write_bytes(b'not part of bundle')
    elif attack=='changed-during-read':
        def fault(stage,name):
            if stage=='after_read' and name=='manifest.json':(path/'extra').write_bytes(b'race')
    else:
        m=json.loads((path/'manifest.json').read_bytes());m['run_metadata']['operation_work']['charged']['context_bytes']=4194305
        (path/'manifest.json').write_bytes(C(m))
    with pytest.raises(WorkflowInputError):p.verify(path,fault=fault)

def test_replay_build_mismatch_before_dispatch(tmp_path,monkeypatch):
    path=tmp_path/'w';p.publish(path,run())
    monkeypatch.setattr(governed_build,'identity',lambda **kw:(b'other-build',H(b'other-build')))
    monkeypatch.setattr(policy,'_assess_admitted',lambda *a,**kw:pytest.fail('mismatched build must not project'))
    with pytest.raises(WorkflowInputError) as e:p.replay(path,tmp_path/'r')
    assert e.value.diagnostic.code=='REPLAY_BUILD_UNAVAILABLE'

def test_observation_failure_cannot_publish(tmp_path):
    def fail(e):raise RuntimeError('bounded observer failure')
    with pytest.raises(WorkflowInputError):p.publish(tmp_path/'r',run(),observer=fail)
    assert not (tmp_path/'r').exists()

def test_byte_verify_does_not_accept_malformed_build_record(tmp_path,monkeypatch):
    monkeypatch.setitem(globals(),'BUILD',C({'schema':'test-only-build-not-executable'}))
    p.publish(tmp_path/'bad-build',run())
    with pytest.raises(WorkflowInputError):p.verify(tmp_path/'bad-build')
