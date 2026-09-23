"""Slice 6 test-only controls; no production bypass or synthetic identity API."""
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

import pytest

from tests.measurement_profile.test_delivery_contract_mapping import PACKAGE, recover_case, command
from applications.bounded_decision_workflow.measurement_contracts import canonical_json_bytes as wire, MeasurementContractError


def test_harness_only_unsupported_exclusion_is_invalid_counterfactual():
    # Hand source audit: U's H1/T1 source is partial_positive, not exhaustive.
    cap=json.loads((PACKAGE/'inputs/U/capture.json').read_bytes())
    objects={m['reference']['sha256']:json.loads(base64.b64decode(m['bytes'])) for m in cap['members'] if m['reference']['kind']!='nm.basis'}
    sources=[x for x in objects.values() if x.get('schema')=='nm.support.v1' and x['coverage']=='partial_positive']
    assert len(sources)==1 and sources[0]['permits']==['high'] and sources[0]['excludes']==sources[0]['exclusion_basis']==[]
    result=json.loads((PACKAGE/'expected/U/result.json').read_bytes())
    matrix=copy.deepcopy(result['cells']['rows'])
    changed=[r for r in matrix if r['hypothesis']==sources[0]['hypothesis'] and r['procedure']==sources[0]['procedure'] and r['outcome']=='low']
    assert len(changed)==1 and changed[0]['relation']=='unknown'
    changed[0]['relation']='excludes'  # Isolated deliberately unjustified control.
    score={}
    for p in result['procedure_assessments']['procedure_identity_map']:
        counts={}
        for row in matrix:
            if row['procedure']==p['reference']:
                counts.setdefault(row['outcome'],0)
                counts[row['outcome']]+=row['relation']=='permits'
        score[p['id']]=max(counts.values())
    artifact=dict(label='invalid_counterfactual_not_recommendation',scores=score)
    assert artifact['scores']=={'T1':1,'T2':2}
    assert result['ranking']['scores'] is None
    valid=json.loads((PACKAGE/'expected/V/result.json').read_bytes())
    assert [s['worst'] for s in valid['ranking']['scores']]==[1,2]


def test_current_traversal_internal_cycle_and_shared_diamond(monkeypatch,tmp_path):
    # Synthetic edges only inside this test. Actual current Graph DFS is used;
    # closed schema/intrinsic checks are bypassed only to isolate its algorithm.
    # This does not claim SHA-consistent typed cycle admission via public input.
    from applications.bounded_decision_workflow import measurement_wire as mw
    iv,objects,pin=recover_case(tmp_path)
    original=json.loads(iv.read_bytes());original['id']='root'
    documents={}
    for name in ['root','a','b','c']:
        value=dict(original,id=name);documents[name]=wire(value)
    refs={name:('nm.invocation.v1',hashlib.sha256(b).hexdigest()) for name,b in documents.items()}
    payloads={refs[name]:b for name,b in documents.items()}
    monkeypatch.setattr(mw.Graph,'_integrity',lambda self:None)
    def exercise(mapping):
        monkeypatch.setattr(mw,'edges',lambda v:[('/'+str(i),refs[n]) for i,n in enumerate(mapping.get(v['id'],[]))])
        return mw.Graph(documents['root'],lambda k,w:payloads[k],pin,mw.Work())
    for mapping in [{'root':['a'],'a':['a']},{'root':['a'],'a':['b'],'b':['a']}]:
        with pytest.raises(MeasurementContractError) as error:exercise(mapping)
        assert error.value.code=='REFERENCE_CYCLE'
    shared=exercise({'root':['a','c'],'a':['b'],'c':['b']})
    assert len(shared.objects)==4 and len(shared.occurrences)==4
    assert shared.work.logical['edge_visits']==4


def test_canonical_construction_and_directory_order_control(tmp_path):
    roots=[]
    for name in ['forward','reverse']:
        root=tmp_path/name;root.mkdir();roots.append(root)
        iv,objects,pin=recover_case(root)
        if name=='reverse':
            # Recreate copies in reverse order; originals are preserved separately.
            alternate=root/'reverse-objects';alternate.mkdir()
            for p in sorted(objects.iterdir(),reverse=True):(alternate/p.name).write_bytes(p.read_bytes())
            objects=alternate
        out=root/'result';run=command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',out)
        assert run.returncode==0,run.stderr
    for name in ['result.json','trace.json','closure.json']:
        assert (roots[0]/'result'/name).read_bytes()==(roots[1]/'result'/name).read_bytes()
    cap=json.loads((PACKAGE/'inputs/P/capture.json').read_bytes())
    q=next(json.loads(base64.b64decode(m['bytes'])) for m in cap['members'] if m['reference']['kind']=='nm.request.v1')
    # Construction ordering of object keys is immaterial; wire H/P arrays are
    # unchanged and their deliberately reversed twins are separate refusals.
    for items in [list(q.items()),list(reversed(list(q.items())))]:assert wire(dict(items))==wire(q)


def test_completed_validation_cannot_waive_stricter_replay_context(tmp_path):
    iv,objects,pin=recover_case(tmp_path,'CL-Q4-envelope');out=tmp_path/'four'
    assert command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',out).returncode==0
    f=tmp_path/'stricter.json';f.write_bytes(wire({'request_chain':3}))
    bad=command('measurement-replay','--bundle',out,'--output-dir',tmp_path/'refused','--limits',f)
    assert bad.returncode==4 and json.loads(bad.stderr)['resource']['dimension']=='request_chain'
    assert not (tmp_path/'refused').exists()
    good=command('measurement-replay','--bundle',out,'--output-dir',tmp_path/'same')
    assert good.returncode==0,good.stderr


@pytest.mark.parametrize('file',['invocation.json','closure.json','result.json','trace.json','build.json','policy.json','manifest.json'])
@pytest.mark.parametrize('kind',['write_failure','interrupt'])
def test_actual_measurement_publication_fault_boundaries(tmp_path,file,kind):
    iv,objects,pin=recover_case(tmp_path);out=tmp_path/'partial'
    # Trusted test bootstrap patches the maintained writer only in this child.
    # No production CLI flag/environment variable/callback enables this seam.
    code='''
import os,signal,sys
from applications.bounded_decision_workflow import measurement_runtime as r
from applications.bounded_decision_workflow.cli import main
original=r.retention._write_file
filename,kind=sys.argv[1:3]
def fault(fd,name,data,unused):
    if name==filename:
        if kind=='interrupt':os.kill(os.getpid(),signal.SIGKILL)
        raise r.retention._error('RETENTION_WRITE_FAILED')
    return original(fd,name,data,unused)
r.retention._write_file=fault
raise SystemExit(main(sys.argv[3:]))
'''
    run=subprocess.run([sys.executable,'-c',code,file,kind,'measurement-evaluate','--invocation',str(iv),'--objects-dir',str(objects),'--authority-pin',pin,'--output-dir',str(out)],capture_output=True)
    assert run.returncode==(-signal.SIGKILL if kind=='interrupt' else 6),run.stderr
    assert not run.stdout and not (out/'manifest.json').exists()
    verify=command('measurement-verify','--bundle',out)
    assert verify.returncode==3 and json.loads(verify.stderr)['code']=='BUNDLE_INCOMPLETE'
    assert command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',out).returncode==5


def test_supported_filesystem_and_unsupported_output_twin(tmp_path):
    iv,objects,pin=recover_case(tmp_path)
    # Existing checkout is on DrvFS; nominate a fresh name but never create it.
    unsupported=Path.cwd()/('nm-slice6-refused-output-'+tmp_path.name.lower())
    assert not unsupported.exists()
    bad=command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',unsupported)
    assert bad.returncode==5 and not unsupported.exists(),bad.stderr
    good=command('measurement-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',tmp_path/'ext4')
    assert good.returncode==0,good.stderr


def test_frozen_source_to_cell_warrants_and_independent_finite_set_oracle():
    # Separately written same-author finite-set check; not reviewer endorsement.
    cases=json.loads((PACKAGE/'cases.json').read_bytes())
    checked=0
    for case in cases:
        if case['expected_exit']!=0:continue
        expected=json.loads((PACKAGE/case['expected']/'result.json').read_bytes())
        cap=json.loads((PACKAGE/case['input']/'capture.json').read_bytes())
        objects={m['reference']['sha256']:json.loads(base64.b64decode(m['bytes'])) for m in cap['members'] if m['reference']['kind']!='nm.basis'}
        required={m['reference']['sha256'] for m in cap['members']}
        iv=objects[cap['invocation']['sha256']];q=objects[iv['request']['sha256']]
        for cell in expected['cells']['rows']:
            sources=[objects[r['sha256']] for r in cell['source_refs']]
            positive=negative=unavailable=False
            for source in sources:
                assert source['hypothesis']==cell['hypothesis'] and source['procedure']==cell['procedure']
                assert source['decoder']==cell['decoder'] and source['evidence']==q['evidence'] and source['context']==q['context']
                if source['qualification']['status']=='unavailable':unavailable=True;continue
                assert source['qualification']['reason']=='explicit_synthetic_premise'
                assert source['origin']=='supplied_synthetic' and source['uncertainty']['kind']=='declared_hard_outcome_support'
                assert source['basis'] and all(b['sha256'] in required for b in source['basis'])
                positive |= cell['outcome'] in source['permits']
                if source['coverage'] in ['explicit_exclusions','complete_envelope']:
                    assert source['exclusion_basis'] and all(b['sha256'] in required for b in source['exclusion_basis'])
                    negative |= cell['outcome'] in source['excludes'] or (source['coverage']=='complete_envelope' and cell['outcome'] not in source['permits'])
                else:assert not source['excludes'] and not source['exclusion_basis']
            relation='unknown' if unavailable or positive==negative else 'permits' if positive else 'excludes'
            assert relation==cell['relation'],(case['id'],cell)
            checked+=1
        if expected['ranking']['scores'] is not None:
            identities={r['reference']['sha256']:r['id'] for r in expected['hypothesis_assessments']['hypothesis_identity_map']}
            viable=set(expected['hypothesis_assessments']['viable']);computed=[]
            for pr in q['measurements']:
                decoder=objects[objects[pr['sha256']]['decoder']['sha256']]
                branches=[]
                for outcome in decoder['outcomes']:
                    survivors=sorted(identities[c['hypothesis']['sha256']] for c in expected['cells']['rows'] if c['procedure']==pr and c['outcome']==outcome['id'] and c['relation']=='permits' and identities[c['hypothesis']['sha256']] in viable)
                    branches.append(survivors)
                worst=max(map(len,branches));computed.append(dict(procedure=pr,worst=worst,reduction=len(viable)-worst))
                equivalence=next(e for e in expected['ranking']['equivalence'] if e['procedure']==pr)
                assert equivalence['survivor_multiset']==sorted(branches)  # multiplicity and [] retained
            assert computed==expected['ranking']['scores']
            minimum=min(s['worst'] for s in computed)
            assert expected['ranking']['best']==[s['procedure'] for s in computed if s['worst']==minimum]
    assert checked>150
    manual=json.loads((PACKAGE/'manual-C.json').read_bytes())
    assert manual['status']=='unresolved' and manual['application_commands']==0 and manual['recommendation'] is None
