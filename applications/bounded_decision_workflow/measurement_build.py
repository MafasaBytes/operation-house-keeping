"""Measurement executable witness, derived locally; never a caller assertion."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
from . import build
from .measurement_contracts import PROFILE, APPROVED_POLICY_SHA, canonical_json_bytes
from .measurement_wire import fail

CONTRACT_SHA = '2e802d1a04f570378c83963d21f7979415b061bc7f68794024a2c9fc9231fa24'


def identity(work=None):
    # Preserve the maintained clean executable, exact lock/interpreter gate.
    def git(*args):
        return subprocess.check_output(['git','--no-optional-locks','-C',str(build.ROOT),*args],timeout=10).decode().strip()
    if platform.python_implementation()!='CPython' or platform.python_version_tuple()[:2]!=('3','13'):
        raise build.unavailable()
    if git('status','--porcelain','--untracked-files=all','--','applications','backend'):
        raise build.unavailable()
    checkpoint=git('rev-parse','HEAD')
    def digest_bytes(data):
        if work is not None:work.physical['build_hash_bytes']=work.physical.get('build_hash_bytes',0)+len(data)
        return hashlib.sha256(data).hexdigest()
    names=subprocess.check_output(['git','--no-optional-locks','-C',str(build.ROOT),
                                  'ls-files','applications','backend'],timeout=10).decode().splitlines()
    def digest_file(path):
        h=hashlib.sha256();size=0
        with path.open('rb') as stream:
            while True:
                chunk=stream.read(65536)
                if work is not None:work.physical['build_read_operations']=work.physical.get('build_read_operations',0)+1
                if not chunk:break
                size+=len(chunk);h.update(chunk)
                if work is not None:work.physical['build_hash_bytes']=work.physical.get('build_hash_bytes',0)+len(chunk)
        if work is not None:work.physical['build_bytes_read']=work.physical.get('build_bytes_read',0)+size
        return h.hexdigest(),size
    sources=[]
    for name in sorted(names):
        # Complete maintained Python executable tree and dependency lock. Data
        # fixtures and historical result JSON are not executable source inputs.
        if name.endswith('.py') or name==build.LOCK:
            digest,size=digest_file(build.ROOT/name)
            sources.append(dict(path=name,sha256=digest,bytes=size))
    lock=(build.ROOT/build.LOCK).read_bytes()
    if work is not None:
        work.physical['build_bytes_read']=work.physical.get('build_bytes_read',0)+len(lock)
        work.physical['build_read_operations']=work.physical.get('build_read_operations',0)+1
    lock_digest=digest_bytes(lock)
    if lock_digest!='7c87f0d7a3f12c271311cc0c33e59025e0161c37f16336901a0764b4330c0817':raise build.unavailable()
    dependencies=[]
    for name,version in sorted(line.split('==') for line in lock.decode().splitlines()):
        if importlib.metadata.version(name)!=version:raise build.unavailable()
        dist=importlib.metadata.distribution(name);artifacts=[]
        for entry in sorted(dist.files or (),key=str):
            if str(entry).endswith('.pyc'):continue
            path=Path(dist.locate_file(entry))
            if not path.is_file():fail('BUILD_IDENTITY_MISMATCH','installed_distribution','phase_1')
            digest,size=digest_file(path)
            artifacts.append(dict(path=str(entry),sha256=digest,bytes=size))
        if not artifacts:fail('BUILD_IDENTITY_MISMATCH','installed_distribution','phase_1')
        dependencies.append(dict(name=name,version=version,artifact_count=len(artifacts),
            artifact_manifest_sha256=digest_bytes(canonical_json_bytes(artifacts))))
    executable_digest,executable_bytes=digest_file(Path(sys.executable))
    environment=dict(python=dict(implementation=platform.python_implementation(),version=platform.python_version(),
                        executable_sha256=executable_digest,executable_bytes=executable_bytes),
                     platform=dict(system=platform.system(),machine=platform.machine(),libc=list(platform.libc_ver())),
                     distributions=dependencies,dependency_lock_sha256=lock_digest)
    value=dict(schema='nm.build.v1',profile=PROFILE,id='maintained-measurement-build',revision=1,
               checkpoint=checkpoint,source_manifest=sources,environment_manifest=environment,
               entrypoint='python -m applications.bounded_decision_workflow',contract_sha256=CONTRACT_SHA,
               resource_policy_sha256=APPROVED_POLICY_SHA)
    wire=canonical_json_bytes(value)
    if work is not None:work.high('build_bytes',len(wire))
    return wire
