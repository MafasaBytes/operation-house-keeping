"""Original B commands with recorded guard-demand calibration; no altered policy."""
import json,subprocess,sys,zipfile
import qualification as q
from qualification_retry19 import SCHEDULE
from qualification_delivery_tail import source,ready,commands
from applications.bounded_decision_workflow import reassessment_runtime as runtime
from applications.bounded_decision_workflow.measurement_wire import Work
S=json.loads(SCHEDULE.read_bytes())

def run(remaining=False):
    ready();seed=source('P10-shared_four');root=seed.parent
    rows=[r for r in commands() if r['id'].startswith('B-')]
    if remaining:
        # Original, unused commands only. The failed manifest fit and its paired
        # below command remain explicitly unresolved; no retry is allocated here.
        pivot=next(i for i,r in enumerate(rows) if r['id']=='B-manifest_bytes-below')
        rows=rows[pivot+1:]
        used={json.loads(p.read_bytes()).get('tag') for p in (q.ROOT/'indexes').glob('*record.json')
              if json.loads(p.read_bytes()).get('event')=='command'}
        assert len(rows)==16 and not used.intersection(r['id'] for r in rows)
    maxima={};original=Work.guard
    def observed(self,k,n):
        maxima[k]=max(maxima.get(k,0),n)
        return original(self,k,n)
    # Observational, internal calibration only. Original guard always runs;
    # neither the CLI nor production accepts a supplied work/result callback.
    Work.guard=observed
    try:
        iv=json.loads((root/'invocation.json').read_bytes());pin=iv['authority']['sha256']
        g=runtime.capture(root/'invocation.json',root/'objects',pin)
        payloads=runtime._payloads(g)
    finally:Work.guard=original
    maxima['receipt_bytes']=len(q.wire(runtime._receipt('reassessment-evaluate',payloads,'0'*64)))+1
    maxima['manifest_bytes']=max(maxima.get('manifest_bytes',0),len((seed/'manifest.json').read_bytes()))
    maxima['bundle_bytes']=sum(map(len,payloads.values()))+g.work.limits['manifest_bytes']
    maxima['closure_bytes']=len(payloads['closure.json'])
    diagnostic=(q.ROOT/'logs'/'T19-E-P2-below.stderr').read_bytes();maxima['diagnostic_bytes']=len(diagnostic)
    expected_diagnostic=json.loads(diagnostic)
    # The operational override itself is retained in closure. Derive its exact
    # framing delta; no application result is used as a semantic oracle.
    for dim in ['closure_bytes','bundle_bytes']:
        base=maxima[dim];d=base
        for _ in range(4):d=base+len(q.wire({dim:d}))-len(b'null')
        assert d==base+len(q.wire({dim:d}))-4
        maxima[dim]=d
    assert all(1<maxima[r['id'][2:].rsplit('-',1)[0]]<=g.work.limits[r['id'][2:].rsplit('-',1)[0]] for r in rows)
    with q.transaction('B-tail-demand-calibration' if remaining else 'B-demand-calibration',{'indexes':8192},files=4,dirs=0):
        q.record(dict(event='resource_demand_calibration',head=S['target_head'],guard_maxima=maxima,logical=g.work.logical,physical=g.work.physical,source_bundle=str(seed),manifest_demand_basis='observed seed manifest size; fresh elapsed/RSS widths remain checked, not assumed constant',closure_override_adjustment='exact retained null-to-map framing; decimal width fixed point',method='owning capture/compute with observational guard wrapper calling original guard; no publication'))
    for row in rows:
        ready();tag=row['id'];dim,suffix=tag[2:].rsplit('-',1);d=maxima[dim];limit=d if suffix=='fit' else d-1
        inp=source(row['case']).parent if row['case']!='P2-below' else q.ROOT/'repairs/t19-e-p2-below'
        iv=json.loads((inp/'invocation.json').read_bytes());pin=iv['authority']['sha256']
        lim=q.ROOT/'inputs'/(tag.lower()+'.json');out=q.ROOT/'outputs'/tag.lower()
        with q.transaction(tag,{'inputs':4096,'outputs':1048576,'logs':32768},files=16,dirs=1):
            q.put(lim,q.wire({dim:limit}))
            q.record(dict(event='resource_pair_intent',id=tag,head=S['target_head'],dimension=dim,calibrated_demand=d,limit=limit,expected=row['expected']))
            a,so,se=q.command(tag,['reassessment-evaluate','--invocation',inp/'invocation.json','--objects-dir',inp/'objects','--authority-pin',pin,'--output-dir',out,'--limits',lim],out)
            checks=dict(exit=a['exit']==row['expected']['exit'],no_timeout=a['termination'] is None);actual={}
            if row['expected']['exit']==0 and a['exit']==0:
                receipt=json.loads(so);checks.update(streams=se==b'' and so==q.wire(receipt)+b'\n',complete=(out/'manifest.json').exists(),receipt_result=receipt['result_sha256']==q.sha((out/'result.json').read_bytes()),receipt_manifest=receipt['bundle_sha256']==q.sha((out/'manifest.json').read_bytes()))
                # Tightened operational guards cannot alter the frozen semantics.
                r=json.loads((out/'result.json').read_bytes());r.pop('accounting');want=json.loads((seed/'result.json').read_bytes());want.pop('accounting')
                checks['semantics']=r==want and (out/'trace.json').read_bytes()==(seed/'trace.json').read_bytes()
                actual=dict(files={p.name:p.stat().st_size for p in out.iterdir()},manifest=json.loads((out/'manifest.json').read_bytes()))
            elif se:
                actual=json.loads(se);checks.update(code=actual['code']==row['expected'].get('code'),streams=so==b'' and se==q.wire(actual)+b'\n',no_partial_success=not out.exists())
                if dim=='diagnostic_bytes':
                    want=dict(expected_diagnostic)
                    if suffix=='below':want.update(code='DIAGNOSTIC_LIMIT_EXCEEDED',target=None,resource=None,message_key='diagnostic_limit_exceeded')
                    checks['exact_diagnostic']=actual==want
                else:
                    resource=actual.get('resource') or {};checks['dimension']=resource.get('dimension')==dim;checks['limit']=resource.get('limit')==limit;checks['attempted_exceeds']=resource.get('attempted',0)>limit
            else:checks['missing_stream']=False
            q.record(dict(event='resource_pair_comparison',id=tag,head=S['target_head'],checks=checks,actual=actual));print(tag,checks,flush=True)
        if not all(checks.values()):raise RuntimeError(('stop; classify product/fixture/infrastructure/contract',tag,checks,actual))

if __name__=='__main__':
    assert sys.argv[1:] in ([],['--remaining-unconsumed'])
    run(bool(sys.argv[1:]))
