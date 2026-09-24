"""Actual clean-checkout binding plus adverse identity twins; no workflow calls."""
import hashlib
import json
from pathlib import Path
import subprocess
import pytest
from applications.bounded_decision_workflow import governed_build as b
from applications.bounded_decision_workflow.errors import WorkflowInputError

def test_actual_identity_or_explicit_dirty_refusal():
    dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--','applications','backend'],cwd=b.ROOT)
    if dirty:
        with pytest.raises(WorkflowInputError) as e:b.identity()
        assert e.value.diagnostic.code=='REPLAY_BUILD_UNAVAILABLE'
        return
    evidence=[];wire,digest=b.identity(observer=evidence.append)
    assert hashlib.sha256(wire).hexdigest()==digest
    v=json.loads(wire)
    assert v['build_policy_id']=='bdw.governed-resource-policy.v1'
    assert v['schema']=='governed-executable-build.v2'
    assert v['implementation_id']=='bdw.governed-application.v2'
    assert len(wire)<=8192 and evidence[0]['source_files']>173
    assert set(v['contract_source_sha256'])==set(b.CONTRACTS)
    paths=subprocess.check_output(['git','-C',str(b.ROOT),'ls-files','applications'],text=True).splitlines()
    inventory={p:hashlib.sha256((b.ROOT/p).read_bytes()).hexdigest() for p in paths}
    canonical=json.dumps(inventory,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    assert v['application_source_inventory_sha256']==hashlib.sha256(canonical).hexdigest()
    forged=dict(v,application_source_inventory_sha256='0'*64)
    with pytest.raises(WorkflowInputError):b.require_identity(hashlib.sha256(b.canonical_json_bytes(forged)).hexdigest())
    assert b.identity()[0]==wire
    assert b.require_identity(digest)[0]==wire
    with pytest.raises(WorkflowInputError):b.require_identity('0'*64)

def test_dependency_mismatch(monkeypatch):
    # Only bypass dirty-worktree inspection in this unit twin, never the runtime API.
    real=b._git
    monkeypatch.setattr(b,'_git',lambda *args:'' if args[0]=='status' else real(*args))
    monkeypatch.setattr(b,'version',lambda name:'not-the-locked-version')
    with pytest.raises(WorkflowInputError) as e:b.identity()
    assert e.value.diagnostic.code=='REPLAY_BUILD_UNAVAILABLE'

def test_contract_policy_mismatch(monkeypatch):
    real=b._git
    monkeypatch.setattr(b,'_git',lambda *args:'' if args[0]=='status' else real(*args))
    monkeypatch.setattr(b,'CONTRACTS',dict(b.CONTRACTS,**{b.POLICY_PATH:'0'*64}))
    with pytest.raises(WorkflowInputError):b.identity()

def test_interpreter_mismatch(monkeypatch):
    monkeypatch.setattr(b.platform,'python_version_tuple',lambda:('3','12','0'))
    with pytest.raises(WorkflowInputError):b.identity()

def test_untracked_executable_refuses(monkeypatch):
    monkeypatch.setattr(b,'_git',lambda *a:'?? applications/injected.py')
    with pytest.raises(WorkflowInputError):b.identity()

def test_legacy_builder_remains_original():
    from applications.bounded_decision_workflow import build
    assert build.identity is not b.identity
    assert build.BUILD_LIMITS['decision_rows']==22

def test_missing_distribution_is_build_unavailable(monkeypatch):
    from importlib.metadata import PackageNotFoundError
    real=b._git
    monkeypatch.setattr(b,'_git',lambda *args:'' if args[0]=='status' else real(*args))
    def missing(name):raise PackageNotFoundError(name)
    monkeypatch.setattr(b,'version',missing)
    with pytest.raises(WorkflowInputError):b.identity()

def test_oversized_build_preserves_resource_refusal(monkeypatch):
    real=b._git;canonical=b.canonical_json_bytes
    monkeypatch.setattr(b,'_git',lambda *args:'' if args[0]=='status' else real(*args))
    monkeypatch.setattr(b,'canonical_json_bytes',lambda v:b'x'*8193 if isinstance(v,str) else canonical(v))
    with pytest.raises(WorkflowInputError) as e:b.identity()
    assert e.value.diagnostic.exit_code==4

def test_inventory_changes_additions_omissions_and_order_are_bound():
    rows={'applications/a.py':'1'*64,'applications/b.py':'2'*64}
    digest=lambda path:rows[path]
    _,root=b._application_inventory(['applications/b.py','applications/a.py'],digest)
    _,reverse=b._application_inventory(['applications/a.py','applications/b.py'],digest)
    assert root==reverse
    rows['applications/a.py']='3'*64
    _,changed=b._application_inventory(rows.keys(),digest)
    assert changed!=root
    rows['applications/c.py']='4'*64
    _,added=b._application_inventory(rows.keys(),digest)
    _,omitted=b._application_inventory(['applications/a.py','applications/b.py'],digest)
    assert added!=changed and omitted!=added

def test_inventory_duplicate_and_non_application_paths_refuse():
    with pytest.raises(WorkflowInputError):b._application_inventory(['applications/a.py']*2,lambda _: '1'*64)
    with pytest.raises(WorkflowInputError):b._application_inventory(['backend/a.py'],lambda _: '1'*64)

def test_v1_and_v2_record_dispatch_is_explicit():
    from applications.bounded_decision_workflow import governed_persistence as p
    assert p._build_edition('governed-executable-build.v1')[0]=='application_source_sha256'
    assert p._build_edition('governed-executable-build.v2')[0]=='application_source_inventory_sha256'
    with pytest.raises(WorkflowInputError):p._build_edition('governed-executable-build.v3')
    assert len(b.CONTRACTS_V1)==6
    assert 'application_source_sha256' in json.loads(Path(b.ROOT/b.V1_SCHEMA).read_bytes())['properties']
    assert 'application_source_inventory_sha256' in json.loads(Path(b.ROOT/b.V2_SCHEMA).read_bytes())['properties']
