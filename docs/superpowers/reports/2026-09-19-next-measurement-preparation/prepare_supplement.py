"""Static package documentation/accounting. Does not import or run the selector."""
from pathlib import Path
import json,hashlib,base64,shutil,sys,platform
P=Path(__file__).parent; ROOT=P.parents[3]
C=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
H=lambda b:hashlib.sha256(b).hexdigest()
def read(n):return json.loads((P/n).read_bytes())
def write(n,x):
 p=P/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(x if isinstance(x,bytes) else C(x))
for name,source,digest in [
 ('semantic-candidate.md','docs/superpowers/specs/2026-09-19-maintained-bounded-next-measurement-selection-identity-closure-candidate.md','8726f35dac9997ee82c0764c95f749cb462e796c6d04794758a90775d0671305'),
 ('independent-confirmation.md','docs/superpowers/reports/2026-09-19-maintained-bounded-next-measurement-selection-identity-closure-confirmation.md','70a8c4ba7909bc35ae1479c43cf70fcbbf703463cb9f1d4096358af3312a27ee')]:
 b=(ROOT/source).read_bytes();assert H(b)==digest;write('frozen/'+name,b)
write('public/source-snapshot.json',(ROOT/'applications/bounded_decision_workflow/examples/snapshot.json').read_bytes())
source_paths=['applications/bounded_decision_workflow/'+n+'.py' for n in ['__main__','cli','input','contracts','admission','governed_contracts','governed_input','governed_review','projection_profile','retention','build','preflight']]
source_paths += ['backend/state_classification/contracts.py','backend/state_classification/derivation.py','backend/constraint_evaluation/contracts.py','backend/model_kernel/store.py']
source_paths=[s for s in source_paths if (ROOT/s).exists()]
provenance=[]
for source in source_paths:
 b=(ROOT/source).read_bytes();write('source-context/'+source,b);provenance.append(dict(path=source,bytes=len(b),sha256=H(b)))
write('source-context/manifest.json',provenance)
cases=read('cases.json'); measurements=read('measurements.json'); objects={}
for f in (P/'objects').iterdir():
 h,k=f.name.split('.',1);objects[(k,h)]=f.read_bytes()
def obj(ref):return json.loads(objects[(ref['kind'],ref['sha256'])])
def refs(x):
 out=[]
 def walk(v,path=''):
  if isinstance(v,dict):
   if set(v)=={'kind','sha256'}:out.append((path,v));return
   for k in sorted(v):
    if k!='snapshot':walk(v[k],path+'/'+k)
  elif isinstance(v,list):
   for i,z in enumerate(v):walk(z,path+'/'+str(i))
 walk(x);return out
def stats(x):
 values=[];keys=[];depth=0;rationals=[]
 def walk(v,d=1):
  nonlocal depth
  depth=max(depth,d);values.append(v)
  if isinstance(v,dict):
   keys.extend(v)
   if set(v)=={'numerator','denominator'}:rationals.extend([v['numerator'],v['denominator']])
   for z in v.values():walk(z,d+1)
  elif isinstance(v,list):
   for z in v:walk(z,d+1)
 walk(x)
 return dict(nodes=len(values),depth=depth,key_occurrences=len(keys),max_key_bytes=max([len(k.encode()) for k in keys]+[0]),max_string_bytes=max([len(v.encode()) for v in values if isinstance(v,str)]+[0]),rational_integer_count=len(rationals),rational_digits=max([len(r.lstrip('-')) for r in rationals]+[0]))
details=[];commands=[]
for case in cases:
 cid=case['id'];cap=read('inputs/'+cid+'/capture.json');oracle=read(case['oracle']);q=obj(case['request'])
 rows=cap['members'];parsed=[]
 for row in rows:
  if row['reference']['kind']!='nm.basis':parsed.append(json.loads(base64.b64decode(row['bytes'])))
 st=[stats(z) for z in parsed];qs=[z for z in parsed if z['schema']=='nm.request.v1']; contextual=[]
 for cq in qs:
  seen=set();incoming=0;bytes_=0;nodes=0
  def expand(r):
   key=(r['kind'],r['sha256'])
   if key in seen:return (0,0,0)
   seen.add(key);b=objects[key]
   if key[0]=='nm.basis':return (len(b),0,0)
   z=json.loads(b);scan=stats(z)['nodes'];edge=0;sz=len(b)
   for path,t in refs(z):
    # Predecessor creates its own request context, not an eligibility import.
    if path=='/predecessor':edge+=1;continue
    a,bb,cc=expand(t);sz+=a;scan+=bb;edge+=1+cc
   return sz,scan,edge
  for path,t in refs(cq):
   if path=='/predecessor':incoming+=1;continue
   a,b,c=expand(t);bytes_+=a;nodes+=b;incoming+=1+c
  contextual.append(dict(request=dict(kind=cq['schema'],sha256=H(C(cq))),unique_scope_objects=len(seen)+1,scan_bytes=bytes_+len(C(cq)),scan_nodes=nodes+stats(cq)['nodes'],edge_occurrences=incoming))
 h=len(q['hypotheses']);m=len(q['measurements']);outs=sum(len(obj(obj(r)['decoder'])['outcomes']) for r in q['measurements'])
 future_cells=h*outs;conditions=sum(len(obj(r)['conditions']) for r in q['measurements']);checks=sum(len(obj(r)['requirements']) for r in q['hypotheses'])
 contributions=sum(len(obj(obj(s)['decoder'])['outcomes']) for s in q['support'])
 interval_regions=sum(1 for r in q['measurements'] for o in obj(obj(r)['decoder'])['outcomes'] if o['region']['kind']=='interval')
 result=read('expected/'+cid+'/result.json') if case['kind']=='completed' else None
 detail=dict(case=cid,physical_supplied_member_bytes=sum(len(base64.b64decode(r['bytes'])) for r in rows),capture_transport_bytes=len(C(cap)),capture_transport_nodes=stats(cap)['nodes'],object_max_json_depth=max(x['depth'] for x in st),object_max_key_bytes=max(x['max_key_bytes'] for x in st),object_max_string_bytes=max(x['max_string_bytes'] for x in st),object_total_keys=sum(x['key_occurrences'] for x in st),rational_integer_count=sum(x['rational_integer_count'] for x in st),rational_max_digits=max(x['rational_digits'] for x in st),contexts=contextual,scoped_expansions=sum(x['unique_scope_objects'] for x in contextual),scoped_edge_occurrences=sum(x['edge_occurrences'] for x in contextual),contextual_scan_bytes=sum(x['scan_bytes'] for x in contextual),contextual_scan_nodes=sum(x['scan_nodes'] for x in contextual),current_cells_full_demand=future_cells,current_source_contribution_full_demand=contributions,current_condition_full_demand=conditions,current_requirement_full_demand=checks,scalar_interval_regions=interval_regions,decoder_endpoint_comparison_reserve=4*interval_regions**2,integer_product_digit_reserve=256,result_nodes=stats(result)['nodes'] if result else 0,trace_nodes=stats(read('expected/'+cid+'/trace.json'))['nodes'] if result else 0,expected_reconstruction_bytes=sum(len(base64.b64decode(r['bytes'])) for r in rows),expected_recovery_member_writes=len(rows),expected_bundle_payload_files=7 if result else 0,physical_runtime='not_measured')
 details.append(detail)
 base=['python','-m','applications.bounded_decision_workflow']
 argv=base+['measurement-evaluate','--invocation','inputs/'+cid+'/invocation.json','--objects-dir','<isolated-recovery/'+cid+'>','--authority-pin',case['authority_pin'] or '<omit-flag-for-this-negative-case>','--output-dir','<new-output/'+cid+'>']
 if case['authority_pin'] is None:at=argv.index('--authority-pin');del argv[at:at+2]
 if cap['limits_override']:
  write('inputs/'+cid+'/limits.json',cap['limits_override']);argv+=['--limits','inputs/'+cid+'/limits.json']
 operations=['evaluate','verify','replay'] if result else ['evaluate']
 for op in operations:
  args=argv if op=='evaluate' else base+['measurement-'+op,'--bundle','<successful-runtime-output/'+cid+'>']+(['--output-dir','<new-replay/'+cid+'>'] if op=='replay' else [])
  commands.append(dict(case=cid,operation='measurement-'+op,argv=args,expected_exit=case['expected_exit'],stdout='expected/'+cid+'/'+op+'-stdout.jsonl' if result else 'expected/'+cid+'/stdout',stderr='expected/'+cid+'/stderr' if result else 'expected/'+cid+'/stderr.jsonl',binding_parameters=['actual executable build witness and all dependent hashes','actual physical manifest and bundle commitment'],execution_status='not_executed'))
numeric=[k for k,v in details[0].items() if type(v)==int]
write('resource-detail.json',dict(status='static_structure_and_full_demand_not_runtime',per_case=details,maxima={k:max(d[k] for d in details) for k in numeric},interpretation='Full-demand counts include unexecuted gated/refused work as upper preparation requirements, not claimed dispatch. Unique graph and per-Q scope counts are separate.'))
write('command-matrix.json',commands)
# Exact field inventory / normative type references: no runtime validators generated.
basecap=read('inputs/P/capture.json');catalog={}
def shape(x):
 if isinstance(x,dict):return dict(type='closed_object',required={k:shape(v) for k,v in sorted(x.items())})
 if isinstance(x,list):return dict(type='array',example_element=shape(x[0]) if x else None)
 return dict(type='null' if x is None else 'boolean' if type(x)==bool else 'integer' if type(x)==int else 'string')
for row in basecap['members']:
 if row['reference']['kind']=='nm.basis':continue
 x=json.loads(base64.b64decode(row['bytes']));k=x['schema'];catalog.setdefault(k,dict(fields=sorted(x),representative_shape=shape(x),normative_types='frozen/semantic-candidate.md §§2–4; CONTRACTS.md'))
for n in ['result','trace','manifest']:
 x=read('expected/P/'+n+'.json');catalog[x['schema']]=dict(fields=sorted(x),representative_shape=shape(x),normative_types='CONTRACTS.md')
for cid in ['G-working']:
 for row in read('inputs/'+cid+'/capture.json')['members']:
  if row['reference']['kind']=='nm.adoption.v1':
   x=json.loads(base64.b64decode(row['bytes']));catalog[x['schema']]=dict(fields=sorted(x),representative_shape=shape(x),normative_types='frozen/semantic-candidate.md §4')
for n in ['inputs/P/capture.json','expected/ID-H-duplicate-ref/stderr.jsonl','expected/P/stdout.jsonl']:
 x=read(n);catalog[x['schema']]=dict(fields=sorted(x),representative_shape=shape(x),normative_types='CONTRACTS.md')
write('contract-catalog.json',dict(status='descriptive_closed_field_inventory_not_executable_schema',warning='Representative null/array values illustrate shape, not inferred restrictions. Normative union/null/enumeration/cardinality rules are the complete frozen semantic tables and CONTRACTS.md.',contracts=catalog))
fixturecodes=sorted({read('expected/'+c['id']+'/stderr.jsonl')['code'] for c in cases if c['kind']=='refusal'})
generic={'CLI_USAGE':2,'INPUT_JSON_INVALID':3,'CANONICAL_FORM_REQUIRED':3,'REFERENCE_KIND_MISMATCH':3,'REFERENCE_CYCLE':3,'SUPPORT_QUALIFICATION_INVALID':3,'PUBLIC_RECONSTRUCTION_INVALID':3,'EVIDENCE_JOIN_MISMATCH':3,'BUILD_IDENTITY_MISMATCH':3,'RESOURCE_POLICY_MISMATCH':3,'DIAGNOSTIC_LIMIT_EXCEEDED':4,'PATH_UNSAFE':5,'OUTPUT_ALREADY_EXISTS':5,'RETENTION_FAILED':6,'REPLAY_SEMANTIC_MISMATCH':3,'INTERNAL_ERROR':7}
write('diagnostic-catalog.json',dict(fixture_codes={k:4 if k=='RESOURCE_LIMIT_EXCEEDED' else 3 for k in fixturecodes},other_codes=generic,public_translation=dict(validation_exception='PUBLIC_RECONSTRUCTION_INVALID',valid_unavailable='completed baseline_unavailable with exact owning reason/path',post_reconstruction_binding_mismatch='EVIDENCE_JOIN_MISMATCH',unknown_exception='INTERNAL_ERROR'),status='proposed_exact_vocabulary'))
write('decoder-oracle.json',dict(authorship='Lead manual interval/literal algebra, not runtime output',cases=[dict(decoder='original50',partitions={'high':'(50,+infinity)','low':'(-infinity,50]'},samples={'49.9':'low','50':'low','50.1':'high'}),dict(decoder='replacement45',partitions={'high':'(45,+infinity)','low':'(-infinity,45]'},samples={'44.9':'low','45':'low','45.1':'high'}),dict(decoder='other',partitions={'high':'(50,100]','low':'(-infinity,50]','other':'(100,+infinity)'},samples={'50':'low','50.1':'high','100':'high','100.1':'other'}),dict(decoder='gap',point='50',membership=[]),dict(decoder='overlap',point='50',membership=['high','low'])]))
write('delivery-obligations.json',dict(status='not_executed_future_controls_outside_measurement_command_matrix',legacy_commands=['evaluate','verify','replay','governed-evaluate','governed-verify','governed-replay'],controls=[dict(id='J-thermal-endpoint',input='inputs/P/invocation.json',endpoint='governed-evaluate',expected='existing AUTHORITY_REFERENCE_MISMATCH/exit 3; no measurement dispatch',note='Maintained governed_contracts.exact rejects the different I field set before schema dispatch; governed_resources.problem fixes the old envelope.'),dict(id='D-path',expected='path 5, no manifest',mutations=['symlink','nonregular','outside_root','preexisting_output']),dict(id='D-publication',expected='retention 6 with incomplete state',mutations=['failed write','failed manifest publication']),dict(id='D-stream',expected='internal 7 or bounded output refusal, no false success'),dict(id='D-replay',expected='exact same-build semantics or technical mismatch; no repair',mutations=['missing required object','changed result','wrong build','wrong policy']),dict(id='D-resource',expected='exit 4 before bounded operation',mutations=['each proposed dimension just below required demand','caller enlargement rejected','output reserve insufficient']),dict(id='D-legacy',expected='accepted original 22/23-row and governed results/replay unchanged',reference='existing retained suites/results; not executed by preparation')],unknown_H_check=dict(status='unreachable_in_this_closed_first_profile',reason='Both allowed check operands are available after permitted admitted scalar/CN evidence. Missing observation exits baseline_unavailable earlier. Do not forge public data to manufacture an unknown check.',future_obligation='If a new allowed lower check can be unavailable, profile revision and explicit withheld_due_to_unresolved_hypotheses proof required.')))
write('preparation-provenance.json',dict(author='lead /root',independent_reviewer_of_this_package=False,oracle='Hand-declared source/cell mutations plus separately written finite-set enumeration; same author/shared frozen semantics, not independent empirical or reviewer evidence.',public_baseline='Synthetic 60.1 observation and upper-50 model in memory via public owning producers/reconstruction; no physical acquisition or ledger/store write.',recovered_unavailable_source='Exact retained bytes originally recovered from 2026-09-15 bounded workflow candidate package; complete bytes now in public/snapshot-unavailable.json, recovery needs no historical loose file.',actual_actions=['file read/hash','static JSON/graph/byte accounting','in-memory public model/result construction and validation','writing this preparation package'],not_executed=['application commands','future selector or proof harness','runtime tests','physical experiments','remote operations'],preparation_corrections=['Initial in-memory model construction retained an old constraint evidence reference; owning integrity validator refused. Reference was coherently rebuilt before successful public reconstruction.','Initial packaging script eagerly evaluated a numeric threshold default on nonnumeric conditions; corrected template code and regenerated new package artifacts.','Static review tightened result authority refs, reason paths, refusal coordinates and blocked-phase labels.'],dependency_note='jsonschema was unavailable; no dependency acquired. Public schema exported by existing Pydantic. No generic schema-validation success is claimed.',environment=dict(python=sys.version,platform=platform.platform()),source_context='source-context/manifest.json is selected review provenance, not a complete executable/environment archive.'))
print(json.dumps(dict(cases=len(cases),commands=len(commands),maxima=read('resource-detail.json')['maxima'])))
