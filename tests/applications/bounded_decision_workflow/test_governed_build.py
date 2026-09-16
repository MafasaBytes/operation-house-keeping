"""Actual clean-checkout binding plus adverse identity twins; no workflow calls."""
import hashlib
import json
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
    assert len(wire)<=8192 and evidence[0]['source_files']>173
    assert set(v['contract_source_sha256'])==set(b.CONTRACTS)
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
