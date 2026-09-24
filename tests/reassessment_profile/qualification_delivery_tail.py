"""Original remaining V/R/D matrix entries; no retry allocation or oracle input."""
import base64,json,os,subprocess,sys,zipfile
import qualification as q
from qualification_retry19 import SCHEDULE
from qualification_remaining import evaluate
from applications.bounded_decision_workflow.reassessment_build import identity
from test_capture import actual_case,key,wire,sha,ref,replace
S=json.loads(SCHEDULE.read_bytes())

def ready():
    assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==S['target_head']
    assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--','applications','backend'])
    assert q.sha(identity())==S['build_sha256']

def source(name):
    row=next(r for r in S['entries'] if r['case']==name)
    p=q.ROOT/'repairs'/row['tag'].lower()/'bundle'
    assert json.loads((p/'build.json').read_bytes())['checkpoint']==S['target_head']
    return p

def commands():
    with zipfile.ZipFile(q.PACKAGE) as z:return json.loads(z.read('command-matrix.json'))['commands']

def retained_command(row,bundle,receipt_source=None):
    ready();tag=row['id'];op=row['argv'][3];out=q.ROOT/'outputs'/tag.lower() if op=='reassessment-replay' else None
    charges={'logs':32768}
    if out:charges['outputs']=1048576
    with q.transaction(tag,charges,files=15,dirs=1 if out else 0):
        args=[op,'--bundle',bundle]+(['--output-dir',out] if out else [])
        a,so,se=q.command(tag,args,out);checks=dict(exit=a['exit']==row['expected']['exit'],no_timeout=a['termination'] is None)
        if a['exit']==0 and row['expected']['exit']==0:
            receipt=json.loads(so);result=json.loads((bundle/'result.json').read_bytes())
            target=out or bundle
            want=dict(schema='nr.receipt.v2',operation=op,evaluation_permitted=result['authority']['permission']=='true',disposition=result['summary']['disposition'],result_sha256=sha((target/'result.json').read_bytes()),bundle_sha256=sha((target/'manifest.json').read_bytes()))
            checks['exact_streams']=se==b'' and so==wire(want)+b'\n'
            if out:checks['six_semantic_files']=all((bundle/n).read_bytes()==(out/n).read_bytes() for n in ['invocation.json','closure.json','result.json','trace.json','build.json','policy.json'])
        else:
            d=json.loads(se) if se else {};checks.update(code=d.get('code')==row['expected'].get('code'),streams=so==b'' and se==wire(d)+b'\n',no_output=out is None or not out.exists())
        q.record(dict(event='tail_comparison',id=tag,head=S['target_head'],checks=checks,source_bundle=str(bundle)))
        print(tag,checks,flush=True)
    if not all(checks.values()):raise RuntimeError(('classify before further execution',tag,checks))

def vr():
    for row in commands():
        if row['id'].startswith(('V-','R-')):retained_command(row,source(row['case']))

def copy_bundle(name,bundle,change):
    files={p.name:p.read_bytes() for p in bundle.iterdir()};change(files)
    if 'manifest.json' in files:
        m=json.loads(files['manifest.json'])
        for r in m['files']:r.update(bytes=len(files[r['name']]),sha256=sha(files[r['name']]))
        files['manifest.json']=wire(m)
    assert sum(map(len,files.values()))<=1048576
    out=q.ROOT/'inputs'/name
    with q.transaction(name,{'inputs':1048576},files=len(files)+3,dirs=1):
        q.reserve({'inputs':sum(map(len,files.values()))},files=len(files),dirs=1);out.mkdir()
        for n,b in files.items():
            with (out/n).open('xb') as f:f.write(b)
        q.record(dict(event='retained_adversarial_fixture',id=name,source=str(bundle),files={n:dict(bytes=len(b),sha256=sha(b)) for n,b in files.items()}))
    return out

def final_d():
    rows={r['id']:r for r in commands()}
    c,p=actual_case('P10-context8');qk=next(k for k,b in p.items() if k[0]=='nm.request.v1' and json.loads(b)['id']=='Q-extra-0')
    oldq=json.loads(p[qk]);hk=key(oldq['hypotheses'][0]);h=json.loads(p[hk]);h['requirements'][0]['expected']={'numerator':'60','denominator':'1'}
    cache={}
    def clone(k):
        if k in cache:return cache[k]
        if k[0]=='nm.basis':return k
        v=h if k==hk else json.loads(p[k])
        def descend(x):
            if type(x) is dict:
                if set(x)=={'kind','sha256'}:return ref(*clone(key(x)))
                return {f:descend(y) for f,y in x.items()}
            if type(x) is list:return [descend(y) for y in x]
            return x
        b=wire(descend(v));nk=(k[0],sha(b));p[nk]=b;cache[k]=nk;return nk
    changed=clone(qk);replace(c,p,qk,json.loads(p[changed]))
    checks=evaluate(rows['D-identity-collision'],c,p)
    if not all(checks.values()):raise RuntimeError('identity-collision discrepancy')
    def extra(files):
        c=json.loads(files['closure.json']);b=b'{}'
        c['members'].append(dict(reference=ref('nm.basis',sha(b)),encoding='base64',bytes=base64.b64encode(b).decode()))
        c['members'].sort(key=lambda m:key(m['reference']));files['closure.json']=wire(c)
    bad=copy_bundle('d-extra-closure-bundle',source('P8-before'),extra)
    retained_command(rows['D-extra-closure'],bad)
    def forge(files):
        r=json.loads(files['result.json']);a,b=r['hypotheses']
        for field in ['cells','status','reasons','outcome_state']:a[field],b[field]=b[field],a[field]
        r['summary']['compatible'],r['summary']['incompatible']=r['summary']['incompatible'],r['summary']['compatible']
        files['result.json']=wire(r)
        # Trace has only aggregate dependency refs and phase reasons; the swapped
        # empty reasons leave these exact dependency sets and phase claims unchanged.
    bad=copy_bundle('d-forged-bundle',source('P1-point60'),forge)
    retained_command(rows['D-forged-verify'],bad);retained_command(rows['D-forged-replay'],bad)
    bad=copy_bundle('d-incomplete-bundle',source('P8-before'),lambda f:f.pop('manifest.json'))
    retained_command(rows['D-incomplete'],bad)

if __name__=='__main__':
    if sys.argv[1:]==['--vr']:vr()
    elif sys.argv[1:]==['--delivery']:final_d()
    else:raise SystemExit('only --vr or --delivery')
