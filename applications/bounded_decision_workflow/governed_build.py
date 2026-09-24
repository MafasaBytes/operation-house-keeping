"""Local governed executable witness. Separate from the untouched legacy builder."""
import hashlib
from importlib.metadata import version, PackageNotFoundError
import json
from pathlib import Path
import platform
import subprocess

from .build import LOCK, PUBLIC, unavailable
from .errors import WorkflowInputError
from .input import canonical_json_bytes
from .governed_resources import POLICY_PATH, POLICY_SHA, problem

ROOT=Path(__file__).resolve().parents[2]
CONTRACTS={
 'docs/superpowers/specs/2026-09-16-maintained-admissibility-enforcement-shared-reference-corrected-design.md':'fc8a8e644213f02694927c4f43f5a25d69c2dad2379b42342fc14e7e657e5268',
 'docs/superpowers/reports/2026-09-16-maintained-admissibility-amendment/AMENDMENT.md':'7a529dc39c07adcd63d6309e7a1d6648f1b6a64be8192df1f2d5351f2787dd56',
 POLICY_PATH:POLICY_SHA,
 'docs/superpowers/reports/2026-09-16-maintained-admissibility-amendment/schemas.json':'2485ccc25ac50379886a1a6a8819441991555d2ff8c36a0c2cca8032f2259069',
 'docs/superpowers/reports/2026-09-16-maintained-admissibility-consolidation/CONTRACT-AND-PLAN.md':'90949e1e3340dec1e7130163fa4f024f87bd04f400bc901097cae6c054a2515b',
 'docs/superpowers/reports/2026-09-16-maintained-admissibility-consolidation/build.schema.json':'f4f931a5912b4a7bf7ec321af67713fbbc235fa0319b85804178f16a8f874dc6',
 'docs/superpowers/reports/2026-09-24-reassessment-slice5-build-carriage-decision/build-carriage-v2-amendment.md':'60860da74407d8534fd58f8c765ef37c602f0427c15ea755033e2679e59f1365',
 'docs/superpowers/reports/2026-09-24-reassessment-slice5-build-carriage-decision/governed-executable-build-v2.schema.json':'6fb4262bdd6eddea0ea9a8b70b0908368e4286abfeb3469c9fcbcd499ddea223',
}
CONTRACTS_V1={k:v for k,v in CONTRACTS.items() if not k.startswith('docs/superpowers/reports/2026-09-24-')}
V1_SCHEMA='docs/superpowers/reports/2026-09-16-maintained-admissibility-consolidation/build.schema.json'
V2_SCHEMA='docs/superpowers/reports/2026-09-24-reassessment-slice5-build-carriage-decision/governed-executable-build-v2.schema.json'

def _git(*args):
    return subprocess.check_output(['git','--no-optional-locks','-C',str(ROOT),*args],
                                   stderr=subprocess.DEVNULL,timeout=10).decode().strip()

def inventory_commitment(sources):
    """Commit the complete sorted application path-to-SHA-256 inventory."""
    return hashlib.sha256(canonical_json_bytes(sources)).hexdigest()

def _application_inventory(paths, digest):
    paths=tuple(sorted(paths))
    if len(paths)!=len(set(paths)):raise unavailable()
    sources={};size=0
    for p in paths:
        path=Path(p)
        if path.is_absolute() or not p.startswith('applications/') or any(x in ('','.','..') for x in path.parts):raise unavailable()
        size+=len(canonical_json_bytes(p))+68
        if size>8192:raise problem('OUTPUT_LIMIT_EXCEEDED',resource=True,target='build_bytes')
        sources[p]=digest(p)
    return sources,inventory_commitment(sources)

def identity(*, observer=None):
    """Recompute, never accept supplied identity. Observer gets bounded startup totals.

    Does not restore environments, publish files or certify host authenticity.
    """
    counts={'source_files':0,'source_bytes':0,'contract_files':0,'contract_bytes':0}
    def digest(name,category='source'):
        path=Path(name)
        if path.is_absolute() or '..' in path.parts:raise unavailable()
        at=ROOT
        for part in path.parts:
            at=at/part
            if at.is_symlink():raise unavailable()
        h=hashlib.sha256()
        with at.open('rb') as f:
            while chunk:=f.read(65536):
                counts[category+'_bytes']+=len(chunk);h.update(chunk)
        counts[category+'_files']+=1
        return h.hexdigest()
    try:
        if platform.python_implementation()!='CPython' or platform.python_version_tuple()[:2]!=('3','13'):raise unavailable()
        if _git('status','--porcelain','--untracked-files=all','--','applications','backend'):raise unavailable()
        commit=_git('rev-parse','HEAD')
        contracts={p:digest(p,'contract') for p in sorted(CONTRACTS)}
        if contracts!=CONTRACTS:raise unavailable()
        if digest(LOCK)!='7c87f0d7a3f12c271311cc0c33e59025e0161c37f16336901a0764b4330c0817':raise unavailable()
        lock=(ROOT/LOCK).read_bytes();dependencies={}
        counts['source_files']+=1;counts['source_bytes']+=len(lock)
        for line in lock.decode().splitlines():
            name,pinned=line.split('==')
            if version(name)!=pinned:raise unavailable()
            dependencies[name]=pinned
        sources,application_root=_application_inventory(_git('ls-files','applications').splitlines(),digest)
        backend=hashlib.sha256();backend.update(b'{')
        for i,p in enumerate(sorted(_git('ls-files','backend').splitlines())):
            if i:backend.update(b',')
            backend.update(canonical_json_bytes(p)+b':'+canonical_json_bytes(digest(p)))
        backend.update(b'}')
        policy_wire=(ROOT/POLICY_PATH).read_bytes()
        if hashlib.sha256(policy_wire).hexdigest()!=POLICY_SHA:raise unavailable()
        counts['contract_files']+=1;counts['contract_bytes']+=len(policy_wire)
        limits=json.loads(policy_wire)['limits']
        v={'schema':'governed-executable-build.v2','git_commit':commit,
           'implementation_id':'bdw.governed-application.v2','inner_schema':'bdw001.1',
           'workflow_profile':'hypothetical_enclosure_one_step.v1','build_policy_id':'bdw.governed-resource-policy.v1',
           'application_source_inventory_sha256':application_root,'backend_source_inventory_sha256':backend.hexdigest(),
           'public_module_sha256':{p:digest(p) for p in PUBLIC},
           'python':{'implementation':'CPython','version':platform.python_version()},
           'dependencies':dependencies,'dependency_lock_sha256':hashlib.sha256(lock).hexdigest(),
           'contract_source_sha256':contracts,'policy_file_sha256':POLICY_SHA,
           'limit_policy_sha256':hashlib.sha256(canonical_json_bytes(limits)).hexdigest()}
        out=bytearray()
        for piece in json.JSONEncoder(sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).iterencode(v):
            b=piece.encode()
            if len(out)+len(b)>8192:raise problem('OUTPUT_LIMIT_EXCEEDED',resource=True,target='build_bytes')
            out.extend(b)
        wire=bytes(out)
        if observer:observer(dict(counts,build_bytes=len(wire),coverage='startup_identity_only'))
        return wire,hashlib.sha256(wire).hexdigest()
    except WorkflowInputError:
        raise
    except (OSError,ValueError,PackageNotFoundError,subprocess.SubprocessError) as e:
        raise unavailable() from e

def require_identity(expected):
    wire,digest=identity()
    if expected!=digest:raise unavailable()
    return wire,digest
