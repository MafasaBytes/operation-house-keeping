"""Preparation only: in-memory synthetic public-result construction; no stores/app run."""
from pathlib import Path
import json,hashlib,copy,base64,zlib
from backend.model_kernel import ModelQueries,build_record
from backend.model_kernel.store import validate_record_collection
from backend.state_classification import StateClassificationResult
from backend.state_classification.derivation import derive_classification
from backend.constraint_evaluation.contracts import ConstraintEvaluationResult,derive_candidate_evaluation
from backend.semantic_compatibility import VariableSemanticCompatibilityResult
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
C=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
old=json.loads((ROOT/'applications/bounded_decision_workflow/examples/snapshot.json').read_bytes())
base=StateClassificationResult.model_validate(old)
loaded=base.state.material.loaded()
records=dict(loaded.records)
change={}
for k,r in list(records.items()):
 if r.record_kind=='variable_constraint_declaration' and r.constraint_anchor_id.endswith('a'*32):
  f=r.model_dump(mode='json',exclude={'record_id'});f['predicate']['upper']['value']='50'
  nr=build_record(type(r),**f);change[k]=nr.record_id;del records[k];records[nr.record_id]=nr
for k,r in list(records.items()):
 if r.record_kind=='state_declaration':
  f=r.model_dump(mode='json',exclude={'record_id'})
  for ev in f['evidence']:
   if ev.get('kind')=='model_record':ev['record_id']=change.get(ev['record_id'],ev['record_id'])
  for row in f['conditions']:
   row['constraint_declaration_record_id']=change.get(row['constraint_declaration_record_id'],row['constraint_declaration_record_id'])
  nr=build_record(type(r),**f);del records[k];records[nr.record_id]=nr
new=validate_record_collection(loaded.revision.model_id,records)
queries=ModelQueries(new)
# Retained synthetic observation is transformed as a complete content-bound input,
# not asserted as a newly acquired physical observation or a new ingestion event.
payload=C({'result':{'eventtime':3721.845,'status':{'extruder':{'temperature':60.1,'target':60}}}})
payload_hash=hashlib.sha256(payload).hexdigest()
rawid=hashlib.sha256(b'prepared-raw:'+payload).hexdigest()[:32]
occid=hashlib.sha256(b'prepared-occurrence:'+payload).hexdigest()[:32]
obsid=hashlib.sha256(b'prepared-observation:'+payload).hexdigest()[:32]
oldrev=loaded.revision.model_dump(mode='json');newrev=new.revision.model_dump(mode='json')
def transform(x):
 if isinstance(x,dict):
  if x==oldrev:return copy.deepcopy(newrev)
  y={k:transform(v) for k,v in x.items()}
  if 'occurrence_id' in y and 'value_json' in y and y.get('property',{}).get('json_pointer','').endswith('/temperature'):
   y.update(value_json='60.1',payload_checksum='sha256:'+payload_hash,raw_record_id=rawid,occurrence_id=occid,observation_id=obsid)
  return y
 if isinstance(x,list):return [transform(v) for v in x]
 return x
results=[]
for old_cn in old['constraint_evaluations']:
 es=VariableSemanticCompatibilityResult.model_validate(transform(old_cn['semantic_compatibility']))
 constraint=queries.constraint_declaration(old_cn['constraint']['constraint_anchor_id'])
 rows=tuple(derive_candidate_evaluation(constraint,es,i) for i in range(len(es.candidates)))
 results.append(ConstraintEvaluationResult(constraint=constraint,as_of=base.as_of,semantic_compatibility=es,candidates=rows,ruleset_version='cn001.1'))
state=queries.state_declaration(base.state_anchor_id,context=base.context)
args=dict(state=state,state_anchor_id=base.state_anchor_id,context=base.context,as_of=base.as_of,condition_sources=base.condition_sources,constraint_evaluations=tuple(results))
result=StateClassificationResult(**args,**derive_classification(**args))
assert str(result.constraint_evaluations[0].candidates[0].observed_decimal)=='60.1'
assert result.constraint_evaluations[0].candidates[0].verdict=='violated'
wire=C(result.model_dump(mode='json'))
assert StateClassificationResult.model_validate_json(wire)==result
(OUT/'public').mkdir(exist_ok=True)
for name,b in [('snapshot-60.1.json',wire),('synthetic-payload.json',payload)]:
 p=OUT/'public'/name
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
package=json.loads((ROOT/'docs/superpowers/reports/2026-09-15-bounded-decision-workflow-candidate-package.json').read_bytes())
d='72c057d8707f4904cf2dfb658937a4610c56b364217ec073239530756f128ea6'
u=zlib.decompress(base64.b64decode(package['objects'][d]['payload']))
assert hashlib.sha256(u).hexdigest()==d
StateClassificationResult.model_validate_json(u)
(OUT/'public'/'snapshot-unavailable.json').write_bytes(u)
(OUT/'public'/'legacy-request.json').write_bytes((ROOT/'applications/bounded_decision_workflow/examples/request.json').read_bytes())
print(json.dumps({'baseline_bytes':len(wire),'baseline_sha256':hashlib.sha256(wire).hexdigest(),'baseline':'60.1','verdict':'violated','unavailable_bytes':len(u),'no_store_writes':True,'no_application_execution':True,'observation_origin':'synthetically_transformed_public_carrier_not_acquisition'}))
