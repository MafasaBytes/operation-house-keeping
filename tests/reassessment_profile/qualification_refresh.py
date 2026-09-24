"""One reserved refresh per frozen core case; oracle is comparison-only."""
import json
import subprocess
import sys
import zipfile
import qualification as q
from test_capture import case,key,ref
from applications.bounded_decision_workflow.reassessment_build import identity
from applications.bounded_decision_workflow.measurement_wire import Work


def refresh():
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    build=identity();newbuild=ref('nr.build.v2',q.sha(build))
    with zipfile.ZipFile(q.PACKAGE) as z:
        rows=[r for r in json.loads(z.read('command-matrix.json'))['commands'] if r['id'].startswith('E-')]
        assert len(rows)==72
        for slot,row in enumerate(rows,1):
            assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
            name=row['case'];c,p=case(name);oldroot=c['invocation'];iv=json.loads(p.pop(key(oldroot)))
            oldbuild=iv['build'];p.pop(key(oldbuild));p[key(newbuild)]=build;iv['build']=newbuild
            raw=q.wire(iv);newroot=ref('nr.invocation.v2',q.sha(raw));p[key(newroot)]=raw
            tag='F-'+row['id'];root=q.ROOT/'repairs'/tag.lower();out=root/'bundle'
            assert sum(map(len,p.values()))+len(raw)<=1048576
            with q.transaction(tag,{'repairs':2097152,'logs':32768},files=len(p)+16,dirs=3):
                q.record(dict(event='planned_refresh',slot=slot,case=name,head=head,build_sha256=newbuild['sha256'],build_bytes=len(build)))
                q.mkdir(root);q.mkdir(root/'objects')
                for (kind,digest),b in sorted(p.items()):q.put(root/'objects'/(digest+'.'+kind),b)
                q.put(root/'invocation.json',raw)
                a,so,se=q.command(tag,['reassessment-evaluate','--invocation',root/'invocation.json','--objects-dir',root/'objects','--authority-pin',c['authority_pin'],'--output-dir',out],out)
                def bind(x):
                    if x==oldroot:return newroot
                    if x==oldbuild:return newbuild
                    if isinstance(x,dict):return {k:bind(v) for k,v in x.items()}
                    if isinstance(x,list):return [bind(v) for v in x]
                    return x
                checks=dict(exit=a['exit']==row['expected']['exit'],no_timeout=a['termination'] is None)
                measures={}
                if row['expected']['exit']==0 and a['exit']==0:
                    r=json.loads((out/'result.json').read_bytes());want=bind(json.loads(z.read('cases/'+name+'/result.json')))
                    accounting=r.pop('accounting');want.pop('accounting');checks['semantic_result']=r==want
                    trace=bind(json.loads(z.read('cases/'+name+'/trace.json')));trace['required_closure'].sort(key=lambda x:(x['kind'],x['sha256']))
                    checks['trace']=json.loads((out/'trace.json').read_bytes())==trace
                    receipt=json.loads(so);checks['streams']=se==b'' and so==q.wire(receipt)+b'\n'
                    checks['receipt_result']=receipt['result_sha256']==q.sha((out/'result.json').read_bytes())
                    checks['receipt_manifest']=receipt['bundle_sha256']==q.sha((out/'manifest.json').read_bytes())
                    measures=dict(files={p.name:p.stat().st_size for p in out.iterdir()},accounting=accounting,manifest=json.loads((out/'manifest.json').read_bytes()))
                    checks['retained_bound']=sum(measures['files'].values())<=1048576
                elif row['expected']['exit']:
                    expected=q.wire(bind(json.loads(q.expected_member(z,'cases/'+name+'/stderr.expected'))))+b'\n'
                    checks.update(exact_diagnostic=se==expected,empty_stdout=so==b'',no_bundle=not out.exists())
                else:checks['unexpected_refusal']=False
                q.record(dict(event='final_core_comparison',id=row['id'],case=name,head=head,checks=checks,measurements=measures))
                print(slot,name,all(checks.values()),flush=True)
            if not all(checks.values()):raise RuntimeError(('retained final-candidate discrepancy',name,checks))

if __name__=='__main__':refresh()
