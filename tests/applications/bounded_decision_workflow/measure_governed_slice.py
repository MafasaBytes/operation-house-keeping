"""Read-only first-slice measurements; stdout is captured by the authorized runner.

Only pure admission and build binding. No CLI/projection/review/publication calls.
Caller retains this bounded evidence in the slice report, not in runtime bundles.
"""
import hashlib
import json
import time
from applications.bounded_decision_workflow import governed_admission as gate, governed_build
from applications.bounded_decision_workflow.errors import WorkflowInputError
from applications.bounded_decision_workflow.terminal import diagnostic_line
from .governed_fixtures import C,H,fixture,reference_boundary

def measure():
    startup=[];build,digest=governed_build.identity(observer=startup.append)
    cases={};event_max=0
    for name in ['W0','J1','X-denied','D2-X','working-adopted','amended-unavailable',
                 'amended-four-0','amended-four-1','amended-four-2','amended-four-3','references-128','references-129']:
        i,objects,pin=(reference_boundary(int(name.split('-')[1])) if name.startswith('references-') else fixture(name))
        original_i=H(i);iv=json.loads(i);iv['build_identity']=digest;i=C(iv)
        events=[]
        def observe(event):
            nonlocal event_max
            wire=C(event);event_max=max(event_max,len(wire))
            # Isolated test evidence ceiling, not a new operational policy.
            if len(wire)>512 or len(events)>=4096:raise RuntimeError('test observer bound')
            events.append(event)
        started=time.perf_counter()
        try:
            a=gate.assess(i,objects,expected_authority_pin=pin,observer=observe)
            result={'disposition':a.disposition,'permission':a.evaluation_permitted,
                    'semantic':json.loads(a.semantic_bytes),'physical':json.loads(a.physical_bytes),
                    'semantic_bytes':len(a.semantic_bytes),'physical_bytes':len(a.physical_bytes),
                    'semantic_sha256':H(a.semantic_bytes),'physical_sha256':H(a.physical_bytes)}
        except WorkflowInputError as e:
            wire,status=diagnostic_line(e.diagnostic)
            result={'refusal':json.loads(wire),'exit':status}
        result.update(seconds=time.perf_counter()-started,fixture_i_sha256=original_i,actual_i_sha256=H(i),
                      events=events,event_bytes=len(C(events)),event_sha256=H(C(events)))
        cases[name]=result
    return {'scope':'pure_first_slice_not_end_to_end','build':json.loads(build),'build_sha256':digest,
            'build_bytes':len(build),'startup_hashing':startup,'cases':cases,'max_event_bytes':event_max,
            'test_observer_caps':{'event_bytes':512,'events_per_case':4096},
            'projection_calls':0,'publication_calls':0,
            'binding_note':'Fresh I binds actual build; comparison=null is an explicitly separate pure nomination, never a three-world comparison. Originals retained in authority archive.'}

if __name__=='__main__':print(json.dumps(measure(),sort_keys=True,separators=(',',':')))
