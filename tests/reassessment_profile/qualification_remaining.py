"""Bounded test driver; expected values never enter production computation."""
import json
import base64
import sys
import zipfile
import os
import qualification as q
from test_capture import actual_case,case,key,wire,sha,ref,replace

def evaluate(row,c,p,*,extra=(),file_attack=None):
    tag=row['id'];repair=tag.startswith('K-')
    root=q.ROOT/('repairs' if repair else 'inputs')/tag.lower()
    out=root/'bundle' if repair else q.ROOT/'outputs'/tag.lower()
    raw=p[key(c['invocation'])]
    assert sum(map(len,p.values()))+len(raw)<=1048576
    charges={'repairs':2097152,'logs':32768} if repair else {'inputs':1048576,'outputs':1048576,'logs':32768}
    with q.transaction(tag,charges,files=len(p)+18,dirs=4):
        if root.exists():
            assert (root/'invocation.json').read_bytes()==raw
            assert {x.name for x in (root/'objects').iterdir()}=={digest+'.'+kind for kind,digest in p}
            for (kind,digest),b in p.items():assert (root/'objects'/(digest+'.'+kind)).read_bytes()==b
            q.record(dict(event='exact_retained_input_reuse',path=str(root)))
        else:
            q.mkdir(root);q.mkdir(root/'objects')
            for (kind,digest),b in sorted(p.items()):q.put(root/'objects'/(digest+'.'+kind),b)
            q.put(root/'invocation.json',raw)
        object_dir=root/'objects'
        if file_attack in ('symlink','fifo','directory'):
            iv=json.loads(raw);request=json.loads(p[key(iv['request'])]);k=key(request['observation'])
            target=object_dir/(k[1]+'.'+k[0]);saved=root/'original-member';target.rename(saved)
            if file_attack=='symlink':target.symlink_to(saved)
            elif file_attack=='fifo':os.mkfifo(target)
            else:q.mkdir(target)
        elif file_attack=='escape':object_dir=str(q.ROOT)+'/../outside-qualification/objects'
        elif file_attack=='collision':q.mkdir(out);q.put(out/'sentinel',b'preserve')
        a,so,se=q.command(tag,['reassessment-evaluate','--invocation',root/'invocation.json','--objects-dir',object_dir,'--authority-pin',c['authority_pin'],'--output-dir',out,*extra],None if file_attack=='collision' else out)
        expected=row['expected'];d=json.loads(se) if se else {}
        checks=dict(exit=a['exit']==expected['exit'],code=d.get('code')==expected['code'],
            stdout=so==b'',canonical_stderr=se==wire(d)+b'\n',no_success=(not out.exists() if file_attack!='collision' else (out/'sentinel').read_bytes()==b'preserve' and list(out.iterdir())==[out/'sentinel']),termination=a['termination'] is None)
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

def graph_controls():
    with zipfile.ZipFile(q.PACKAGE) as z:
        rows={r['id']:r for r in json.loads(z.read('command-matrix.json'))['commands']}
        for name in ['D-missing-ancestor','D-digest-before-cycle','D-wrong-build',
                     'D-prepared-build','D-wrong-policy','D-wrong-profile','D-v1-wrapper']:
            row=rows[name];c,p=case(row['case']) if name=='D-prepared-build' else actual_case(row['case'])
            if name in ('D-missing-ancestor','D-digest-before-cycle'):
                k=next(k for k in p if k[0]=='nr.request.v2' and json.loads(p[k])['revision']==1)
                if name=='D-missing-ancestor':del p[k]
                else:
                    v=json.loads(p[k]);iv=json.loads(p[key(c['invocation'])]);v['predecessor']=iv['request'];p[k]=wire(v)
            elif name=='D-wrong-build':
                k=next(k for k in p if k[0]=='nr.build.v2');v=json.loads(p[k]);v['checkpoint']='0'*40
                v['id']=sha(wire({f:x for f,x in v.items() if f not in ('schema','profile','id','revision','predecessor')}));replace(c,p,k,v)
            elif name=='D-wrong-policy':
                k=next(k for k in p if k[0]=='nm.resource-policy.v1');v=json.loads(p[k]);v['limits']['unique_objects']-=1;replace(c,p,k,v)
            elif name=='D-wrong-profile':
                k=next(k for k in p if k[0]=='nr.observation.v2');v=json.loads(p[k]);v['profile']='bdw.thermal.action.v1';replace(c,p,k,v)
            elif name=='D-v1-wrapper':
                raw=z.read('authority/v1-wrapper-reconstructed.json');assert len(raw)==311968
                k=next(k for k in p if k[0]=='nr.retained-bundle.v2');replace(c,p,k,json.loads(raw))
            evaluate(row,c,p)

def file_controls():
    with zipfile.ZipFile(q.PACKAGE) as z:rows={r['id']:r for r in json.loads(z.read('command-matrix.json'))['commands']}
    for attack in ('escape','symlink','fifo','directory','collision'):
        row=rows['D-'+attack];evaluate(row,*actual_case(row['case']),file_attack=attack)

if __name__=='__main__':
    if '--carriage' in sys.argv:carriage_controls()
    elif '--graph' in sys.argv:graph_controls()
    elif '--files' in sys.argv:file_controls()
    else:dispatch_controls()
