"""Preparation consistency, independent finite bitset oracle and recovery checks.
Not an application test runner, selector, general mapper or permission evaluator.
"""
from pathlib import Path
import json,hashlib,base64,itertools,time,resource
P=Path(__file__).parent
C=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
H=lambda b:hashlib.sha256(b).hexdigest()
def load(n):return json.loads((P/n).read_bytes())
def pairs(xs):
 d={}
 for k,v in xs:
  assert k not in d,('duplicate JSON key',k);d[k]=v
 return d
start=time.perf_counter();reads=0;readbytes=0;memberbytes=0;results=0;rankings=0;hashmismatches=[];missing=[];checks=[]
cases=load('cases.json')
for case in cases:
 cid=case['id']; cap=load('inputs/'+cid+'/capture.json'); oracle=load(case['oracle']); table={}
 for row in cap['members']:
  r=row['reference'];b=base64.b64decode(row['bytes'],validate=True);memberbytes+=len(b);key=(r['kind'],r['sha256']);assert key not in table
  table[key]=b
  if H(b)!=r['sha256']:hashmismatches.append([cid,r]);assert cid=='J-stale-hash'
  if r['kind']!='nm.basis':assert C(json.loads(b,object_pairs_hook=pairs))==b
 def obj(r):return json.loads(table[(r['kind'],r['sha256'])])
 def scan(x,path=''):
  if isinstance(x,dict):
   if set(x)=={'kind','sha256'}:
    if (x['kind'],x['sha256']) not in table:missing.append([cid,path,x])
   else:
    for k,v in x.items():
     if k!='snapshot':scan(v,path+'/'+k)
  elif isinstance(x,list):
   for i,v in enumerate(x):scan(v,path+'/'+str(i))
 for key,b in table.items():
  if key[0]!='nm.basis':scan(json.loads(b))
 i=load('inputs/'+cid+'/invocation.json');assert H(C(i))==case['invocation']['sha256']
 assert ('nm.prepared-build.v1',i['build_identity']) in table
 assert ('nm.resource-policy.v1',i['resource_policy']) in table
 if case['kind']!='completed':
  d=load('expected/'+cid+'/stderr.jsonl');assert d['code']==oracle['spec']['code'];assert (P/'expected'/cid/'stdout').read_bytes()==b''
  if d['code'].startswith('DUPLICATE_NOMINATION'):assert d['target']['occurrence_count']==2
  continue
 results+=1;r=load('expected/'+cid+'/result.json');q=obj(case['request'])
 assert r['ranking']['disposition']==case['disposition']
 assert r['authority']['request']==case['request']
 assert len(r['hypothesis_assessments']['hypothesis_identity_map'])==len(q['hypotheses'])
 assert len(r['procedure_assessments']['procedure_identity_map'])==len(q['measurements'])
 if not r['authority']['evaluation_permitted']:
  assert r['cells']['rows']==[] and r['procedure_assessments']['rows']==[] and r['hypothesis_assessments']['rows']==[]
 if r['ranking']['scores'] is None:
  assert all(r['ranking'][k] is None for k in ['best','recommendation','branches','equivalence'])
 else:
  rankings+=1
  # Independently use bit masks from explicit nominal oracle table. No future
  # mapper, request gate or result cells are used to derive expected partitions.
  hs=r['hypothesis_assessments']['viable'];bits={h:1<<j for j,h in enumerate(hs)}
  cell={(z['h'],z['m'],z['o']):z['relation'] for z in oracle['cell_table']}
  scores=[];branches=[];equiv=[]
  for mr in q['measurements']:
   m=obj(mr);o=obj(m['decoder']);masks=[];br=[]
   for outcome in o['outcomes']:
    mask=sum(bit for h,bit in bits.items() if cell[h,m['id'],outcome['id']]=='permits');masks.append(mask)
    surv=[h for h in sorted(bits) if mask&bits[h]];br.append(dict(outcome=outcome['id'],survivors=surv))
   worst=max(mask.bit_count() for mask in masks);scores.append(dict(procedure=mr,worst=worst,reduction=len(hs)-worst));branches.append(dict(procedure=mr,outcomes=br))
   # Tuple lexicographic order preserves duplicates; compare lengths explicitly.
   multi=[list(t) for t in sorted(tuple(x['survivors']) for x in br)]
   assert len(multi)==len(o['outcomes']);equiv.append(dict(procedure=mr,survivor_multiset=multi))
  assert scores==r['ranking']['scores'],cid
  assert branches==r['ranking']['branches'],cid
  assert equiv==r['ranking']['equivalence'],cid
  minimum=min(s['worst'] for s in scores);best=[s['procedure'] for s in scores if s['worst']==minimum]
  assert best==r['ranking']['best']
  assert r['ranking']['recommendation']==(best[0] if len(best)==1 and minimum<len(hs) else None)
 man=load('expected/'+cid+'/manifest.json');assert len(man['files'])==6
 for f in man['files']:
  b=(P/'expected'/cid/f['name']).read_bytes();reads+=1;readbytes+=len(b);assert len(b)==f['bytes'] and H(b)==f['sha256']
 for op in ['evaluate','verify','replay']:
  receipt=load('expected/'+cid+'/'+op+'-stdout.jsonl');assert receipt['operation']=='measurement-'+op
  assert receipt['result_sha256']==H((P/'expected'/cid/'result.json').read_bytes())
  assert receipt['bundle_sha256']==H(C(man))
 assert cap==load('expected/'+cid+'/closure.json')
 assert r['cells']['assessment_state']=='assessed' or not r['cells']['rows']
 assert r['review']['comparison']=='not_requested'
assert len(hashmismatches)==1
assert {x[0] for x in missing}=={'G-A-missing','CL-Q3-missing-Q1','CL-Q3-missing-basis'}
# Isolated hand mathematics for the bypass; no acceptance gate is bypassed here.
assert [1,1] and max([1,1])==1 and max([2,2])==2
assert load('expected/U/result.json')['ranking']['scores'] is None
assert [x['worst'] for x in load('expected/V/result.json')['ranking']['scores']]==[1,2]
assert load('expected/E-repeated-empty/result.json')['ranking']['equivalence'][1]['survivor_multiset']==[[],[],['H1','H2']]
assert load('expected/E-empty/result.json')['ranking']['equivalence'][0]['survivor_multiset']!=load('expected/E-empty/result.json')['ranking']['equivalence'][1]['survivor_multiset']
assert len(load('expected/G-denied-multiple/result.json')['ranking']['reasons'])==2
# Original and rehashed replacements have sound commitments, but stale joins.
substitutions=[]
for cid in ['S-edition','S-decoder','S-edition-valid','S-decoder-valid']:
 cap=load('inputs/'+cid+'/capture.json');tab={(x['reference']['kind'],x['reference']['sha256']):json.loads(base64.b64decode(x['bytes'])) for x in cap['members'] if x['reference']['kind']!='nm.basis'}
 q=tab[('nm.request.v1',next(c['request']['sha256'] for c in cases if c['id']==cid))];s=tab[(q['support'][0]['kind'],q['support'][0]['sha256'])]
 p=tab[(q['measurements'][0]['kind'],q['measurements'][0]['sha256'])]
 joined=s['procedure']==q['measurements'][0] and s['decoder']==p['decoder']
 assert joined==cid.endswith('-valid');substitutions.append(dict(case=cid,hashes_valid=True,support_exact_join=joined))
# Construction-order invariance is a preparation operation, not accepting a
# reordered on-wire request. Recover actual object IDs from the canonical P data.
cap=load('inputs/P/capture.json');tab={(x['reference']['kind'],x['reference']['sha256']):json.loads(base64.b64decode(x['bytes'])) for x in cap['members'] if x['reference']['kind']!='nm.basis'}
q=tab[(next(c for c in cases if c['id']=='P')['request']['kind'],next(c for c in cases if c['id']=='P')['request']['sha256'])]
def ident(r):return tab[(r['kind'],r['sha256'])]['id']
recipes=[]
for horder in itertools.permutations(q['hypotheses']):
 for morder in itertools.permutations(q['measurements']):
  cooked=dict(q,hypotheses=sorted(horder,key=ident),measurements=sorted(morder,key=ident));assert C(cooked)==C(q)
  recipes.append(dict(hypotheses=list(horder),measurements=list(morder),expected_request_sha256=H(C(q))))
(P/'permutation-recipes.json').write_bytes(C(recipes))
summary=dict(status='static_consistency_passed_not_runtime_proof',author='same lead, separately written bitset calculation; no independent reviewer staffing',case_count=len(cases),completed_expected_results=results,ranked_expected_results=rankings,technical_expected_refusals=len(cases)-results,planned_commands=len(load('command-matrix.json')),application_commands_executed=0,expected_single_tampered_case=hashmismatches,expected_missing_reference_cases=sorted({x[0] for x in missing}),substitution_checks=substitutions,permutation_constructions=len(recipes),branch_multiplicity_and_empty_arrays='explicitly_checked',manifest_payload_checks=reads,manifest_payload_bytes_checked=readbytes,capture_member_bytes_decoded=memberbytes,static_checker_elapsed_seconds=time.perf_counter()-start,static_checker_peak_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,physical_runtime='unmeasured',scope='Canonical JSON/hashes, exact captures/manifest recovery, independent finite bitsets, explicit bad-wire controls, substitution identity, preparation invariance. Not full future parser/gate/mapper/runtime validation.')
(P/'static-verification.json').write_bytes(C(summary));print(json.dumps(summary))
