"""Actual closed-stdout control and nearest valid twin; test driver only."""
import json
import os
import resource
import subprocess
import sys
import qualification as q
from test_capture import actual_case,key


def fixed_channel():
    c,p=actual_case('P8-before');raw=p[key(c['invocation'])]
    assert sum(map(len,p.values()))+len(raw)<=1048576
    rows=[json.loads(f.read_bytes()) for f in (q.ROOT/'indexes').glob('*record.json')]
    used={r['slot'] for r in rows if r.get('event') in ('approved_contingency','approved_contingency_intent','contingency')}
    for r in rows:used.update(range(1,r.get('contingency_slots_used',0)+1))
    assert used==set(range(1,16)),('contingency state',used)
    root=q.ROOT/'repairs/channel-fixed'
    with q.transaction('contingency-16-channel-fixed',{'repairs':2097152,'logs':32768},files=len(p)+32,dirs=4):
        q.record(dict(event='contingency',slot=16,purpose='actual closed stdout repair and nearest valid production twin'))
        q.mkdir(root);q.mkdir(root/'objects')
        for (kind,digest),b in p.items():q.put(root/'objects'/(digest+'.'+kind),b)
        q.put(root/'invocation.json',raw)
        args=['reassessment-evaluate','--invocation',root/'invocation.json','--objects-dir',root/'objects','--authority-pin',c['authority_pin']]
        out=root/'valid';a,so,se=q.command('K-channel-valid',[*args,'--output-dir',out],out)
        valid=a['exit']==0 and se==b'' and so==q.wire(json.loads(so))+b'\n'
        target=root/'broken';argv=[sys.executable,'-m','applications.bounded_decision_workflow',*map(str,[*args,'--output-dir',target])]
        q.reserve({'repairs':1048576,'logs':4096},files=10,dirs=1)
        head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
        q.record(dict(event='command',tag='K-channel-broken',head=head,argv=argv,fault='close stdout fd 1 before interpreter start'))
        def bounds():
            resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912))
            resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,1048576));os.close(1)
        run=subprocess.run(argv,cwd=q.ROOT/'recovery',env=dict(os.environ,PYTHONPATH=str(q.REPO),PYTHONDONTWRITEBYTECODE='1'),stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=30,preexec_fn=bounds)
        assert len(run.stderr)<=32768;q.put(q.ROOT/'logs/K-channel-broken.stderr',run.stderr)
        d=json.loads(run.stderr)
        checks=dict(valid_twin=valid,exit=run.returncode==7,code=d['code']=='OUTPUT_CHANNEL_FAILURE',canonical_stderr=run.stderr==q.wire(d)+b'\n',complete_visible=(target/'manifest.json').exists(),bundle_state=d['bundle_state']=='complete_visible_durability_unknown')
        q.record(dict(event='internal_control_fixed',id='broken-stream',head=head,checks=checks,actual=d,exit=run.returncode))
        print(checks,flush=True)
        assert all(checks.values())

if __name__=='__main__':fixed_channel()
