"""Proposer-authored R test premises built from an actual acquisition's evidence.

Moved unchanged from test_maintained_increment.py so that more than one test
module can construct the historical R and its exact request-input closure.
Authorities and requests here are synthetic test premises, never operational
authority or owner approval.
"""
import json

from applications.bounded_decision_workflow.t1_contracts import ref, sha
from tests.checked_temperature.fixtures import co1


def request_for(case,produced,receipt):
    evidence=json.loads(produced['public_evidence'])
    def mutate(kind,value,world):
        if kind=='R':
            value['result']['acquisition']['ended']='2026-10-05T09:02:00Z'
    # Proposer-authored R and separately supplied A are test premises. The
    # maintained assembler neither constructs nor modifies either authority.
    return co1(case['prior_files'],case['base'],scalar=receipt['r'],
               evidence=lambda w:w.put(evidence,'synthetic-acquisition-evidence'),mutate=mutate)


def request_inputs_for(supplied,case,request_wire=None):
    """Test proposer supplies an exact R-only closure, keeping A separate."""
    from applications.bounded_decision_workflow.t1_records import parse
    wire=supplied.request_wire if request_wire is None else request_wire
    pool=dict(supplied.objects)
    import base64
    for item in json.loads(case['prior_files']['closure.json'])['members']:
        pool.setdefault(item['sha256'],base64.b64decode(item['data']))
    for value in case['prior_files'].values():
        pool.setdefault(sha(value),value)
    root=ref('ct.request.v1',wire)
    pool[root['sha256']]=wire
    prior={sha(w) for w in case['prior_files'].values()}
    pending,seen=[root],set()
    while pending:
        rr=pending.pop(0)
        if rr['sha256'] in seen:
            continue
        seen.add(rr['sha256'])
        if rr['sha256'] in prior or rr['kind']=='ct.evidence-content':
            continue
        _,annotations=parse(pool[rr['sha256']],rr['kind'],'/')
        if annotations:
            pending.extend(child for _,child,_,edge in annotations.refs if edge)
    return {d:w for d,w in supplied.objects.items() if d in seen}
