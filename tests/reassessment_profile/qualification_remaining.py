"""Bounded test driver; expected values never enter production computation."""
import json
import base64
import sys
import zipfile
import qualification as q
from test_capture import actual_case,case,key,wire,sha,ref,replace

def evaluate(row,c,p,*,extra=()):
    tag=row['id'];repair=tag.startswith('K-')
    root=q.ROOT/('repairs' if repair else 'inputs')/tag.lower()
    out=root/'bundle' if repair else q.ROOT/'outputs'/tag.lower()
    raw=p[key(c['invocation'])]
    assert sum(map(len,p.values()))+len(raw)<=1048576
    charges={'repairs':2097152,'logs':32768} if repair else {'inputs':1048576,'outputs':1048576,'logs':32768}
    with q.transaction(tag,charges,files=len(p)+16,dirs=3):
        if root.exists():
            assert (root/'invocation.json').read_bytes()==raw
            assert {x.name for x in (root/'objects').iterdir()}=={digest+'.'+kind for kind,digest in p}
            for (kind,digest),b in p.items():assert (root/'objects'/(digest+'.'+kind)).read_bytes()==b
            q.record(dict(event='exact_retained_input_reuse',path=str(root)))
        else:
            q.mkdir(root);q.mkdir(root/'objects')
            for (kind,digest),b in sorted(p.items()):q.put(root/'objects'/(digest+'.'+kind),b)
            q.put(root/'invocation.json',raw)
        a,so,se=q.command(tag,['reassessment-evaluate','--invocation',root/'invocation.json','--objects-dir',root/'objects','--authority-pin',c['authority_pin'],'--output-dir',out,*extra],out)
        expected=row['expected'];d=json.loads(se) if se else {}
        checks=dict(exit=a['exit']==expected['exit'],code=d.get('code')==expected['code'],
            stdout=so==b'',canonical_stderr=se==wire(d)+b'\n',no_success=not out.exists(),termination=a['termination'] is None)
        q.record(dict(event='remaining_matrix_comparison',id=tag,checks=checks,expected=expected,actual=d))
        print(tag,checks,flush=True)
    return checks

def dispatch_controls():
    with zipfile.ZipFile(q.PACKAGE) as z:
        rows={r['id']:r for r in json.loads(z.read('command-matrix.json'))['commands']}
    for name in ['D-v1-header','D-unknown-flag']:
        row=rows[name];c,p=actual_case(row['case']);extra=[]
        if name=='D-v1-header':
            iv=json.loads(p.pop(key(c['invocation'])));iv.update(schema='nr.invocation.v1',profile='measurement-reassessment/v1')
            raw=wire(iv);c['invocation']=ref('nr.invocation.v1',sha(raw));p[key(c['invocation'])]=raw
        else:extra=['--computed-result','untrusted']
        evaluate(row,c,p,extra=extra)

def carriage_controls():
    with zipfile.ZipFile(q.PACKAGE) as z:
        rows={r['id']:r for r in json.loads(z.read('command-matrix.json'))['commands']}
        original=json.loads(z.read('carriage-controls/shared_valid.json'))
        original_keys={key(m['reference']) for m in original['members']}
        for name in ['unknown_recipe','recipe_extra','missing_member','substituted_bytes',
                     'missing_recipe_member','duplicate_recipe_member','incompatible_role',
                     'manifest_mismatch','missing_file']:
            row=rows['D-'+name];c,p=actual_case(row['case'])
            variant=json.loads(z.read('carriage-controls/'+name+'.json'))
            pool={key(m['reference']):base64.b64decode(m['bytes']) for m in variant['members']}
            old=key(original['descriptor']);new=key(variant['descriptor'])
            # Rehash the new descriptor's owning exposure/Q/authority/I first;
            # then impose exact missing/stale member bytes. Never refill from p.
            p.update(pool)
            if old!=new:replace(c,p,old,json.loads(pool[new]))
            for victim in original_keys-set(pool):
                if victim!=old:p.pop(victim,None)
            p.update(pool)
            evaluate(row,c,p)

if __name__=='__main__':
    if '--carriage' in sys.argv:carriage_controls()
    else:dispatch_controls()
