"""Fresh internal Slice-2 work evidence, no CLI, publication or replay execution."""
import base64
import gzip
import json
import time
from unittest.mock import patch

from applications.bounded_decision_workflow import governed_build,governed_review,policy,projection,retention
from .governed_fixtures import fixture,C,H
from .test_governed_review import carry


def measure():
    startup=[];build,bid=governed_build.identity(observer=startup.append)
    cases={};prepared={};dispatch=[]
    real_policy=policy._assess_admitted;real_plan=projection._prepare_projection
    def p(a,**kw):
        dispatch.append({'entry':'policy','request':a.request_input.sha256})
        return real_policy(a,**kw)
    def plan(a,*args,**kw):
        dispatch.append({'entry':'projection_plan','request':a.request_input.sha256})
        return real_plan(a,*args,**kw)
    def forbidden(*a,**kw):raise AssertionError('publication is outside Slice 2')
    schedule=[('W0','W0',None),('D1-X','X-denied','W0'),('D2-X','D2-X','D1-X'),
              ('J1','J1',None),('unavailable','amended-unavailable','W0'),
              *[(f'four-{i}',f'amended-four-{i}',None) for i in range(4)],('working','working-adopted',None)]
    with patch.object(policy,'_assess_admitted',p),patch.object(projection,'_prepare_projection',plan),patch.object(retention,'_publish_bundle',forbidden):
        for name,source,prior in schedule:
            old,objects,pin=fixture(source);iv=json.loads(old);iv['build_identity']=bid
            files=prepared.get(prior)
            iv['comparison']=None if files is None else {'kind':'prior-bundle-manifest','sha256':H(files['manifest.json'])}
            wire=C(iv);events=[]
            def observe(e):
                if len(events)>=4096 or len(C(e))>512:raise AssertionError('bounded test observer exceeded')
                events.append(e)
            before=len(dispatch);start=time.perf_counter()
            review=governed_review.evaluate(wire,objects,expected_authority_pin=pin,prior_files=files,observer=observe)
            elapsed=time.perf_counter()-start
            prepared[name]=carry(review,build)
            r=json.loads(review.result_bytes);rows=r['decision_review']['rows']
            cases[name]={'source':source,'old_pure_fixture_invocation':H(old),'new_invocation':H(wire),'seconds':elapsed,
                'permission':r['admissibility']['evaluation_permitted'],'disposition':r['admissibility']['disposition'],
                'selection':r['selection'],'logical':r['resource_accounting'],'physical':json.loads(review.physical_bytes),
                'rows':len(rows),'performed':sum(x['performed'] for x in rows),'required':sum(x['reevaluation']=='required' for x in rows),
                'typed_changes':sum(x['value_changed'] is True for x in rows),'numeric_comparable':sum(x['numeric_comparable'] for x in rows),
                'blocked':sum(not x['performed'] for x in rows),'dispatch':dispatch[before:],
                'result_bytes':len(review.result_bytes),'trace_bytes':len(review.trace_bytes),'closure_bytes':len(review.closure_bytes),
                'physical_bytes':len(review.physical_bytes),'carried_bytes':sum(map(len,prepared[name].values())),
                'events':events,'files':{k:base64.b64encode(v).decode() for k,v in prepared[name].items()}}
    return {'schema':'slice2-in-memory-measurement.v1','build':json.loads(build),'build_sha256':bid,'build_bytes':len(build),
            'startup':startup,'cases':cases,'publication':'not_called_guard_installed',
            'retention_metadata':'in-memory test adapter; filesystem/time labels synthetic, work counters observed; no filesystem or replay claim',
            'event_caps':{'events_per_case':4096,'bytes_per_event':512}}


if __name__=='__main__':
    raw=C(measure());packed=gzip.compress(raw,mtime=0)
    print(json.dumps({'uncompressed_sha256':H(raw),'uncompressed_bytes':len(raw),'compressed_sha256':H(packed),
                      'base64_gzip':base64.b64encode(packed).decode()}))
