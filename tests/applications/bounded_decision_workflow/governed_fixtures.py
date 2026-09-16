"""Recover frozen fixture bytes from the committed authority chain, never runtime files."""
import base64
import gzip
import hashlib
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
C = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
H = lambda b: hashlib.sha256(b).hexdigest()
TEST_BUILD = b'unit-test-build-provider-only'

@lru_cache
def recovered():
    p = ROOT / 'docs/superpowers/reports'
    r = json.loads((p / '2026-09-16-admissibility-first-slice-authority-recovery.json').read_bytes())
    packed = b''.join(base64.b64decode(json.loads((p/n).read_bytes())['base64']) for n in r['parts'])
    assert H(packed) == r['archive_sha256']
    files = {n: base64.b64decode(v['base64']) for n,v in json.loads(gzip.decompress(packed)).items()}
    prefix = 'docs/superpowers/reports/2026-09-16-maintained-admissibility-preparation-closure/'
    old = json.loads(files[prefix+'frozen-recovery.json'])
    b = b''.join(base64.b64decode(json.loads(files[prefix+n])['base64']) for n in old['parts'])
    assert H(b) == old['archive_sha256']
    files.update({n:base64.b64decode(v['base64']) for n,v in json.loads(gzip.decompress(b)).items()})
    prefix = 'docs/superpowers/reports/2026-09-16-maintained-admissibility-preparation/'
    objects = {}
    for n,b in files.items():
        if n.startswith(prefix+'objects/shard-'):
            for h,v in json.loads(b).items():
                raw = base64.b64decode(v['base64']); assert H(raw) == h
                objects[h] = (v['kind'], raw)
    cases = {x['id']:x for x in json.loads(files[prefix+'cases.json'])['cases']}
    prefix='docs/superpowers/reports/2026-09-16-maintained-admissibility-amendment/'
    packed=json.loads(files[prefix+'objects-recovery.json'])
    values=json.loads(gzip.decompress(base64.b64decode(packed['base64'])))
    for h,v in values.items():
        wire=C(v['canonical_json']);assert H(wire)==h
        objects[h]=(v['kind'],wire)
    for n,v in json.loads(files[prefix+'witness-index.json'])['cases'].items():
        cases['amended-'+n]={'invocation':v['invocation'],'expected_authority_pin':v['pin']}
    return objects,cases

def fixture(name='W0'):
    objects,cases = recovered(); case=cases[name]
    iv=json.loads(objects[case['invocation']['sha256']][1])
    # Pure-slice nomination only: comparison adapter is a later slice. Original I
    # stays in the archive; exact binding substitution is explicitly a new I.
    iv['comparison']=None;iv['build_identity']=H(TEST_BUILD)
    selected={}
    def visit(ref, shallow=False):
        if ref is None:return
        kind,raw=objects[ref['sha256']];selected[ref['sha256']] = (kind,raw)
        if shallow or kind in ('bdw001.1','public-snapshot','captured-basis'):return
        def descend(x):
            if isinstance(x,dict):
                if set(x)=={'kind','sha256'}:
                    visit(x);return
                for k,v in sorted(x.items()):
                    if k=='predecessor':visit(v,True)
                    else:descend(v)
            elif isinstance(x,list):
                for v in x:descend(v)
        descend(json.loads(raw))
    for k in ['scenario','selection','adoption']:visit(iv[k])
    for h in case.get('omit_captured_sha256',[]):selected.pop(h,None)
    return C(iv),list(selected.values()),case['expected_authority_pin']

def reference_boundary(total):
    """New, hash-valid repeated-basis twin. Domain unchanged; fresh D/S/A/I refs."""
    iw,entries,_=fixture();iv=json.loads(iw);db={H(b):(k,json.loads(b) if k!='captured-basis' else b) for k,b in entries}
    sc=db[iv['scenario']['sha256']][1];d=db[sc['declaration']['sha256']][1];a=db[iv['selection']['sha256']][1]
    leaf=d['provenance']['basis_artifacts'][0]
    d['provenance']['basis_artifacts']=[leaf]*(total-9)
    def put(kind,v):return {'kind':kind,'sha256':H(C(v))}
    dr=put('finite-declaration.v1',d);sc['declaration']=dr;sr=put('governed-scenario.v1',sc)
    a['declaration']=dr;a['scenario']=sr;ar=put('local-authority-selection.v1',a)
    iv['scenario']=sr;iv['selection']=ar
    kept=[(k,b) for k,b in entries if k in ('bdw001.1','public-snapshot','captured-basis')]
    kept += [(dr['kind'],C(d)),(sr['kind'],C(sc)),(ar['kind'],C(a))]
    return C(iv),kept,ar['sha256']
