"""Fixed corpus preparation and independent set oracle. NOT a request evaluator.
No measurement runtime imported. Case expectations are declared below, not inferred
by executing a future validator, gate, mapper, selector or command implementation.
"""
from pathlib import Path
import json,hashlib,copy,itertools,time,resource,base64
P=Path(__file__).parent
ROOT=P.parents[3]
PROFILE='bdw.measurement.supplied.v1'
C=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
H=lambda b:hashlib.sha256(b).hexdigest()
def write(name,x):
 p=P/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(x if isinstance(x,bytes) else C(x))
def rat(n,d=1):return {'numerator':str(n),'denominator':str(d)}
def head(k,i,r=1,**kw):return dict(schema='nm.'+k+'.v1',profile=PROFILE,id=i,revision=r,**kw)
att={'issuer_label':'local-preparation-owner','authenticated':False,'basis':'Explicit synthetic premise, conditional only; semantic approval is not empirical calibration.'}
objects={}
def put(x,kind=None):
 b=x if isinstance(x,bytes) else C(x);k=kind or x['schema'];h=H(b);objects[(k,h)]=b;return {'kind':k,'sha256':h}
def get(r):return json.loads(objects[(r['kind'],r['sha256'])])
basis=put(b'Preparation synthetic basis: permits below are stipulated conditional possibilities. Only complete_envelope assertions explicitly assert that all successful outcomes lie in the listed envelope and justify its complement exclusions; positive-only assertions do not. This is not an empirical confidence bound. Calibration/fidelity/hold flags are synthetic assumptions.','nm.basis')
snap=json.loads((P/'public/snapshot-60.1.json').read_bytes());legacy=json.loads((P/'public/legacy-request.json').read_bytes())
binding={k:v for k,v in legacy['observed_input_binding'].items() if k not in ('role','token_role_premises')}
context=dict(subject_entity_anchor_id=binding['subject_entity_anchor_id'],variable_anchor_id=binding['variable_anchor_id'],assertion_context=snap['context'],as_of=snap['as_of'],scenario_label='nominated-comparison')
def evidence(snapshot,id):
 return put(head('evidence',id,snapshot=snapshot,question=legacy['current_condition_question'],binding=binding,token_roles=dict(quantity=binding['expected_quantity_kind'],observation_role=binding['expected_observation_role'],unit=binding['expected_unit'],basis=[basis])))
e=evidence(snap,'E');eu=evidence(json.loads((P/'public/snapshot-unavailable.json').read_bytes()),'EU')
policy={'schema':'nm.resource-policy.v1','profile':PROFILE,'id':'prepared-policy','revision':1,'status':'proposed_not_approved','limits':{'object_bytes':262144,'invocation_bytes':16384,'capture_bytes':1048576,'unique_objects':128,'json_nodes':65536,'json_depth':40,'string_bytes':4096,'integer_digits':128,'reference_occurrences':4096,'edge_visits':4096,'active_depth':32,'request_contexts':8,'request_chain':4,'scoped_expansions':1024,'context_scan_bytes':16777216,'public_reconstruction_nodes':131072,'result_bytes':65536,'trace_bytes':131072,'closure_bytes':524288,'build_bytes':65536,'manifest_bytes':16384,'bundle_bytes':1048576,'diagnostic_bytes':2048,'receipt_bytes':1024},'safety_ceiling_proposals':{'wall_seconds_per_command':30,'address_space_bytes':536870912,'retained_corpus_bytes':67108864},'safety_status':'unmeasured_future_enforcement_proposal'}
pr=put(policy)
build={'schema':'nm.prepared-build.v1','profile':PROFILE,'id':'build-placeholder','revision':1,'status':'prepared_not_executable','checkpoint':'6351750b3cacad288cb99d9d11a8b61b6fe85b71','semantic_candidate_sha256':'8726f35dac9997ee82c0764c95f749cb462e796c6d04794758a90775d0671305','binding_rule':'Replace this complete object by actual approved source/environment/contract witness and regenerate all dependent I/results before runtime execution.'}
br=put(build)
k=put(head('policy','K',algorithm='finite_compatibility_minimax/v1',secondary='none',coverage_rule='whole_nominated_matrix',tie_rule='preserve_all_best',authority=att))
def outcome(i,lower=None,lc=False,upper=None,uc=False):return dict(id=i,region=dict(kind='interval',lower=lower,lower_closed=lc,upper=upper,upper_closed=uc))
def defs():
 hs=[head('hypothesis','H'+str(i+1),account_kind=kind,context=context,evidence=e,requirements=[dict(id='baseline',kind='baseline_decimal_equals',expected=rat(601,10)),dict(id='criterion',kind='baseline_cn_verdict_equals',expected='violated')],provenance=att) for i,kind in enumerate(['high_underlying_faithful_baseline','low_underlying_positive_offset'])]
 os=[head('decoder','O1',domain=dict(kind='scalar_finite_decimal',unit='degree_celsius',values=None),outcomes=[outcome('high',rat(50),False,None,False),outcome('low',None,False,rat(50),True)]),head('decoder','O2',domain=dict(kind='literal_codes',unit='code',values=['code_a','code_b']),outcomes=[dict(id=v,region=dict(kind='literal_set',values=[v])) for v in ['code_a','code_b']])]
 ps=[head('procedure','T'+str(i+1),context=context,evidence=e,method=method,method_edition=1,decoder=None,conditions=[dict(id=j,kind='local_assumption',state='true',basis=[basis]) for j in ['applicability','availability','calibration','fidelity','hold']],provenance=att) for i,method in enumerate(['reference_scalar','nonspecific_code'])]
 return hs,os,ps
# Explicit oracle cells for original case: no input-dependent production mapper.
base_cells={('H1','T1','high'):'permits',('H1','T1','low'):'excludes',('H2','T1','high'):'excludes',('H2','T1','low'):'permits',**{(h,'T2',o):'permits' for h in ['H1','H2'] for o in ['code_a','code_b']}}
variants=[]
def case(id,disposition='preferred_within_supplied_set',code=None,**v):variants.append(dict(id=id,disposition=disposition,code=code,**v))
case('P');case('V',twin_of='U');case('T',disposition='tied_best_within_supplied_set',tie=True)
case('U',disposition='withheld_due_to_incomplete_predictions',partial=True)
case('U-unavailable',disposition='withheld_due_to_incomplete_predictions',unavailable=True)
case('U-derived',disposition='withheld_due_to_incomplete_predictions',derived=True)
case('U-missing-row',disposition='withheld_due_to_incomplete_predictions',missing=True)
case('X-conflict',disposition='withheld_due_to_conflicting_predictions',conflict=True)
case('X-conflict-missing',disposition='withheld_due_to_conflicting_predictions',conflict=True,missing=True)
case('A-false',disposition='withheld_due_to_inapplicable_candidate',ceiling=40)
case('A-unknown',disposition='withheld_due_to_unknown_applicability',condition_unknown=True)
case('A-restored',ceiling=70)
case('G-denied',disposition='evaluation_denied',denied=True)
case('G-scope-false',disposition='evaluation_denied',scope='false')
case('G-denied-multiple',disposition='evaluation_denied',scope='false',denied=True)
case('G-scope-unknown',disposition='evaluation_permission_unknown',scope='unknown')
case('G-working',working=True)
case('G-adoption-bad',code='AUTHORITY_REFERENCE_MISMATCH',working=True,adoption_bad=True)
case('G-pin-missing',code='AUTHORITY_PIN_REQUIRED',pin_missing=True)
case('G-A-missing',code='REQUIRED_REFERENCE_MISSING',authority_missing=True)
case('S-edition',code='SUPPORT_SUBJECT_MISMATCH',edition=True,stale_support=True)
case('S-edition-valid',edition=True)
case('S-decoder',code='SUPPORT_SUBJECT_MISMATCH',threshold=45,stale_support=True)
case('S-decoder-valid',threshold=45)
case('J-gap',code='DECODER_INVALID',gap=True)
case('J-overlap',code='DECODER_INVALID',overlap=True)
case('J-empty-vocabulary',code='DECODER_INVALID',empty_o=True)
case('J-unit',code='PROCEDURE_DOMAIN_MISMATCH',bad_unit=True)
case('J-profile',code='PROFILE_MISMATCH',profile_bad=True)
case('J-stale-hash',code='REFERENCE_DIGEST_MISMATCH',bad_hash=True)
case('E-empty',disposition='no_discriminating_measurement',empty_branch=True)
case('E-extra-empty',third=True)
case('E-repeated-empty',disposition='no_discriminating_measurement',repeated_empty=True)
case('E-other',disposition='no_discriminating_measurement',other=True)
case('N-T1',only_m=0);case('N-T2',disposition='no_discriminating_measurement',only_m=1)
case('N-H1',disposition='no_discrimination_needed',only_h=0)
case('N-H1-T1',disposition='no_discrimination_needed',only_h=0,only_m=0)
case('N-one-incomplete',disposition='withheld_due_to_incomplete_predictions',refuted=1,missing=True)
case('N-one-viable',disposition='no_discrimination_needed',refuted=1)
case('N-zero-viable',disposition='no_viable_hypotheses',refuted=2)
case('N-zero-incomplete',disposition='withheld_due_to_incomplete_predictions',refuted=2,missing=True)
case('N-empty-H',code='HYPOTHESIS_SET_EMPTY',empty_h=True)
case('N-empty-M',code='MEASUREMENT_SET_EMPTY',empty_m=True)
case('N-both-empty',code='HYPOTHESIS_SET_EMPTY',empty_h=True,empty_m=True)
case('R-all-excluded',code='ROW_ALL_EXCLUDED',all_excluded=True)
case('R-baseline-unavailable',disposition='baseline_unavailable',baseline_unavailable=True)
case('ID-H-duplicate-ref',code='DUPLICATE_NOMINATION_REFERENCE',duplicate_h=True)
case('ID-P-duplicate-ref',code='DUPLICATE_NOMINATION_REFERENCE',duplicate_p=True)
case('ID-H-duplicate-version',code='DUPLICATE_NOMINATION_ID',same_h_id=True)
case('ID-P-duplicate-version',code='DUPLICATE_NOMINATION_ID',same_p_id=True)
case('ID-collision',code='IDENTITY_VERSION_COLLISION',same_h_id=True,collision=True)
case('ID-alias-H',code='SEMANTIC_ALIAS',alias_h=True)
case('ID-alias-P',code='SEMANTIC_ALIAS',alias_p=True)
case('ID-order-H',code='NOMINATION_ORDER_INVALID',reverse_h=True)
case('ID-order-P',code='NOMINATION_ORDER_INVALID',reverse_p=True)
case('CL-Q2-revised',chain=2,revised=True)
case('CL-Q3-shared',chain=3)
case('CL-Q4-envelope',chain=4)
case('CL-Q5-refused',code='RESOURCE_LIMIT_EXCEEDED',chain=5)
case('CL-Q3-missing-Q1',code='REQUIRED_REFERENCE_MISSING',chain=3,missing_ancestor=True)
case('CL-Q3-missing-basis',code='REQUIRED_REFERENCE_MISSING',chain=3,missing_basis=True)
case('CL-predecessor-version',code='PREDECESSOR_VERSION_MISMATCH',chain=2,bad_predecessor=True)
case('CL-predecessor-id',code='PREDECESSOR_VERSION_MISMATCH',chain=2,bad_predecessor_id=True)
case('CL-historical-unknown',chain=3,historical_unknown=True)
case('CL-historical-invalid',code='DECODER_INVALID',chain=3,historical_invalid=True)
case('CL-caller-tightened',code='RESOURCE_LIMIT_EXCEEDED',chain=3,tighten=True)
case('HARNESS-field-rejected',code='REQUEST_SCHEMA_INVALID',matrix_attack=True)

def make(v):
 hs,os,ps=defs();cells=copy.deepcopy(base_cells);id=v['id'];ere=e
 if v.get('baseline_unavailable'):ere=eu
 for h in hs:h['evidence']=ere
 for p in ps:p['evidence']=ere
 if v.get('refuted'):
  for h in hs[-v['refuted']:]:h['requirements'][1]['expected']='satisfied'
 if v.get('alias_h'):hs[1]['account_kind']=hs[0]['account_kind']
 if v.get('same_h_id'):hs[1]['id']='H1';hs[1]['revision']=1 if v.get('collision') else 2
 if v.get('same_p_id'):ps[1]['id']='T1';ps[1]['revision']=2
 if v.get('threshold'):
  os[0]['revision']=2
  os[0]['outcomes'][0]['region']['lower']=rat(v['threshold']);os[0]['outcomes'][1]['region']['upper']=rat(v['threshold'])
 if v.get('gap'):os[0]['outcomes'][1]['region']['upper_closed']=False
 if v.get('overlap'):os[0]['outcomes'][0]['region']['lower_closed']=True
 if v.get('empty_o'):os[0]['outcomes']=[]
 if v.get('bad_unit'):os[0]['domain']['unit']='code'
 if v.get('third') or v.get('repeated_empty'):
  os[1]['domain']['values'].append('code_c');os[1]['outcomes'].append(dict(id='code_c',region=dict(kind='literal_set',values=['code_c'])))
  for h in ['H1','H2']:cells[h,'T2','code_c']='excludes'
 if v.get('repeated_empty'):
  for h in ['H1','H2']:cells[h,'T2','code_b']='excludes'
  v['empty_branch']=True
 if v.get('other'):
  os[0]['outcomes'][0]['region'].update(upper=rat(100),upper_closed=True)
  os[0]['outcomes'].append(outcome('other',rat(100),False,None,False))
  for h in ['H1','H2']:cells[h,'T1','other']='permits'
 if v.get('empty_branch'):
  for h in ['H1','H2']:cells[h,'T1','high']='excludes';cells[h,'T1','low']='permits'
 if v.get('tie'):cells['H1','T2','code_b']='excludes';cells['H2','T2','code_a']='excludes'
 if v.get('edition'):ps[0]['method_edition']=2;ps[0]['revision']=2
 if v.get('threshold'):ps[0]['revision']=2
 if 'ceiling' in v:ps[1]['conditions'].append(dict(id='baseline_ceiling',kind='baseline_le',threshold=rat(v['ceiling'])));ps[1]['conditions'].sort(key=lambda x:x['id'])
 if v.get('condition_unknown'):ps[1]['conditions'][2]['state']='unknown';ps[1]['conditions'][2]['basis']=[]
 ors=[put(x) for x in os]
 for p,o in zip(ps,ors):p['decoder']=o
 if v.get('alias_p'):ps[1]=dict(copy.deepcopy(ps[0]),id='T2')
 hrs=[put(x) for x in hs];prs=[put(x) for x in ps]
 if v.get('duplicate_h'):hrs=[hrs[0],hrs[0]]
 if v.get('duplicate_p'):prs=[prs[0],prs[0]]
 if v.get('only_h') is not None:hrs=[hrs[v['only_h']]]
 if v.get('only_m') is not None:prs=[prs[v['only_m']]]
 if v.get('empty_h'):hrs=[]
 if v.get('empty_m'):prs=[]
 if v.get('reverse_h'):hrs.reverse()
 if v.get('reverse_p'):prs.reverse()
 if v.get('all_excluded'):
  cells['H1','T1','high']='excludes';cells['H1','T1','low']='excludes'
 ss=[];serial=0
 for hi,hr in enumerate(hrs):
  for mi,mr in enumerate(prs):
   hid=get(hr)['id'];mid=get(mr)['id'];md=get(mr);od=md['decoder'];vocab=[z['id'] for z in get(od)['outcomes']]
   logicalh='H'+str(hi+1);logicalm='T1' if md['method']=='reference_scalar' else 'T2'
   if v.get('only_h') is not None:logicalh='H'+str(v['only_h']+1)
   if v.get('missing') and hi==len(hrs)-1 and mi==len(prs)-1:continue
   serial+=1
   permit=[o for o in vocab if cells.get((logicalh,logicalm,o))=='permits']
   coverage='complete_envelope';exclude=[];eb=[basis];qual=dict(status='qualified_conditional',reason='explicit_synthetic_premise');origin='supplied_synthetic'
   if v.get('all_excluded') and hi==0 and mi==0:coverage='explicit_exclusions';exclude=vocab
   if (v.get('partial') or v.get('conflict')) and hi==0 and mi==0:coverage='partial_positive';eb=[]
   if (v.get('unavailable') or v.get('derived')) and hi==0 and mi==0:
    qual=dict(status='unavailable',reason='unverified_derivation' if v.get('derived') else 'missing_support');origin='supplied_unverified_derivation' if v.get('derived') else origin
   source_p=mr;source_o=od
   if v.get('stale_support') and mid=='T1':
    oh,oo,op=defs();source_o=put(oo[0]);op[0]['decoder']=source_o;source_p=put(op[0])
   sr=put(head('support','S'+str(serial),hypothesis=hr,procedure=source_p,decoder=source_o,evidence=ere,context=context,origin=origin,coverage=coverage,permits=permit,excludes=exclude,uncertainty=dict(kind='declared_hard_outcome_support',statement='Finite successful-domain synthetic support; not a confidence interval.',basis=[basis]),qualification=qual,basis=[basis],exclusion_basis=eb,provenance=att));ss.append(sr)
 if v.get('conflict'):
  x=get(ss[0]);x.update(id='S5',coverage='explicit_exclusions',permits=[],excludes=['high'],exclusion_basis=[basis]);ss.append(put(x))
 q=head('request','Q-'+id,context=context,evidence=ere,hypotheses=hrs,measurements=prs,support=ss,policy=k,predecessor=None)
 if v.get('matrix_attack'):q['matrix']=[dict(h='H1',m='T1',o='low',relation='excludes')]
 ancestors=[]
 if v.get('chain',1)>1:
  hq=copy.deepcopy(q)
  if v.get('historical_unknown'):hq['support']=[]
  if v.get('historical_invalid'):
   bad_o=get(ors[0]);bad_o['id']='OLD-O';bad_o['outcomes'][1]['region']['upper_closed']=False;bo=put(bad_o)
   bad_p=get(prs[0]);bad_p['id']='OLD-P';bad_p['decoder']=bo;bp=put(bad_p)
   hq['measurements']=[bp];hq['support']=[]
  for rev in range(1,v['chain']):
   hq['revision']=rev;hq['predecessor']=ancestors[-1] if ancestors else None;ancestors.append(put(hq))
  q['revision']=v['chain'];q['predecessor']=ancestors[-1]
  if v.get('bad_predecessor'):q['revision']+=1
  if v.get('bad_predecessor_id'):q['id']='different-request'
  if v.get('revised'):
   changed_h=get(hrs[0]);changed_h['revision']=2;changed_h['provenance']=dict(att,basis='Revised explicit declaration; same comparison semantics.')
   changed_p=get(prs[0]);changed_p['revision']=2;changed_p['method_edition']=2
   nh=put(changed_h);np=put(changed_p)
   q['hypotheses']=[nh,*hrs[1:]];q['measurements']=[np,*prs[1:]]
   ns=[]
   for r in ss:
    z=get(r);z['revision']=2
    if z['hypothesis']==hrs[0]:z['hypothesis']=nh
    if z['procedure']==prs[0]:z['procedure']=np
    ns.append(put(z))
   q['support']=ns
 qr=put(q)
 member=qr
 if v.get('denied'):
  z=copy.deepcopy(q);z['id']='Q-allowed-other';member=put(z)
 d=head('declaration','D-'+id,requests=[member],scope_state=v.get('scope','true'),attestation=att)
 if v.get('profile_bad'):d['profile']='singleton-gamma-beta.v1'
 dr=put(d);ar=put(head('selection','A-'+id,declaration=dr,request=qr,purpose='accepted_working_evaluation' if v.get('working') else 'hypothetical_evaluation',attestation=att))
 tr=None
 if v.get('working'):tr=put(head('adoption','T-'+id,declaration=dr,request=qr,selection=ar,attestation=att))
 if v.get('adoption_bad'):
  other=copy.deepcopy(q);other['id']='Q-adoption-other';otherref=put(other);z=get(tr);z['request']=otherref;tr=put(z)
 inv=head('invocation','I-'+id,request=qr,selection=ar,adoption=tr,build_identity=br['sha256'],resource_policy=pr['sha256']);ir=put(inv)
 omitted=[];override={}
 if v.get('authority_missing'):omitted.append(ar)
 if v.get('missing_ancestor'):omitted.append(ancestors[0])
 if v.get('missing_basis'):omitted.append(basis)
 if v.get('bad_hash'):override[qr['sha256']]=C(dict(q,context=dict(context,scenario_label='tampered')))
 return dict(spec=v,invocation=ir,request=qr,authority_pin=None if v.get('pin_missing') else ar['sha256'],omitted=omitted,overrides=override,cells=cells,ancestors=ancestors)

# Static structural graph listing ONLY: no semantic validation or runtime evaluation.
def edges(x):
 found=[]
 def walk(v,path):
  if isinstance(v,dict):
   if set(v)=={'kind','sha256'}:found.append((path,v));return
   for key in sorted(v):
    if key=='snapshot':continue # public-owning material, accounted separately
    walk(v[key],path+'/'+key)
  elif isinstance(v,list):
   for i,vv in enumerate(v):walk(vv,path+'/'+str(i))
 walk(x,'')
 if x.get('schema')=='nm.invocation.v1':found.extend([('/build_identity',dict(kind=br['kind'],sha256=x['build_identity'])),('/resource_policy',dict(kind=pr['kind'],sha256=x['resource_policy']))])
 return sorted(found)
def graph(root):
 seen={};occ=[];missing=[];maxdepth=0
 def walk(r,d):
  nonlocal maxdepth
  maxdepth=max(maxdepth,d);key=(r['kind'],r['sha256'])
  if key in seen:return
  if key not in objects:missing.append(r);return
  b=objects[key];seen[key]=b
  if r['kind']=='nm.basis':return
  for path,t in edges(json.loads(b)):
   occ.append(dict(source=r,path=path,target=t));walk(t,d+1)
 walk(root,1)
 return seen,occ,missing,maxdepth

def counts(x,depth=1):
 if isinstance(x,dict):
  rs=[counts(v,depth+1) for v in x.values()];return (1+sum(r[0] for r in rs),max([depth]+[r[1] for r in rs]))
 if isinstance(x,list):
  rs=[counts(v,depth+1) for v in x];return (1+sum(r[0] for r in rs),max([depth]+[r[1] for r in rs]))
 return 1,depth

# Oracle computes finite set arithmetic only on explicit case tables above.
def expected(c):
 v=c['spec'];q=get(c['request']);id=v['id'];code=v['code'];disp=v['disposition'];hr=q['hypotheses'];mr=q['measurements']
 if code:
  phase=3; field='/'; refs=[]; lid=None; count=None; dimension=None; used=None; limit=None
  if code in ('AUTHORITY_PIN_REQUIRED','PROFILE_MISMATCH'):phase=1 if code=='AUTHORITY_PIN_REQUIRED' else 2;field='/authority_pin' if phase==1 else '/selection/declaration/profile'
  if code in ('REFERENCE_DIGEST_MISMATCH','REQUIRED_REFERENCE_MISSING','IDENTITY_VERSION_COLLISION','PREDECESSOR_VERSION_MISMATCH','AUTHORITY_REFERENCE_MISMATCH'):phase=2
  if code=='REQUIRED_REFERENCE_MISSING':
   refs=c['omitted'];field='/required_closure'
   for edge in graph(c['invocation'])[1]:
    if edge['target'] in c['omitted']:
     field='/closure/'+edge['source']['sha256']+edge['path'];refs=[edge['source'],edge['target']];break
  if code=='REFERENCE_DIGEST_MISMATCH':refs=[c['request']];field='/request'
  if code=='PREDECESSOR_VERSION_MISMATCH':refs=[q['predecessor']];field='/predecessor'
  if code=='AUTHORITY_REFERENCE_MISMATCH':refs=[get(c['invocation'])['adoption']];field='/adoption/request'
  if code=='SUPPORT_SUBJECT_MISMATCH':field='/support/0/procedure';refs=[q['support'][0],get(q['support'][0])['procedure'],mr[0]]
  if code in ('DECODER_INVALID','PROCEDURE_DOMAIN_MISMATCH'):field='/measurements/0/decoder';refs=[get(mr[0])['decoder']]
  if v.get('historical_invalid'):field='/predecessor/predecessor/measurements/0/decoder';refs=[get(get(c['ancestors'][0])['measurements'][0])['decoder']]
  if code in ('HYPOTHESIS_SET_EMPTY','MEASUREMENT_SET_EMPTY'):field='/hypotheses' if code.startswith('HYPOTHESIS') else '/measurements'
  if code.startswith('DUPLICATE_NOMINATION') or code=='NOMINATION_ORDER_INVALID' or code=='IDENTITY_VERSION_COLLISION' or code=='SEMANTIC_ALIAS':
   is_h=any(v.get(x) for x in ('duplicate_h','same_h_id','reverse_h','alias_h'));field='/hypotheses' if is_h else '/measurements';refs=hr if is_h else mr
   lid=get(refs[0])['id'];count=len(refs) if code.startswith('DUPLICATE') else None
  if code=='ROW_ALL_EXCLUDED':phase=7;field='/cells/H1/T1';refs=[hr[0],mr[0]]
  if code=='REQUEST_SCHEMA_INVALID':phase=3;field='/matrix'
  if code=='RESOURCE_LIMIT_EXCEEDED':phase=2;field='/required_closure';dimension='edge_visits' if v.get('tighten') else 'request_chain';used=2 if v.get('tighten') else 5;limit=1 if v.get('tighten') else 4
  return dict(kind='refusal',exit_code=4 if code=='RESOURCE_LIMIT_EXCEEDED' else 3,diagnostic=dict(schema='nm.diagnostic.v1',code=code,stage='phase_'+str(phase),target=dict(request=c['request'],field=field,logical_id=lid,references=sorted(refs,key=lambda r:(r['kind'],r['sha256'])),occurrence_count=count),resource=dict(dimension=dimension,attempted=used,limit=limit) if dimension else None,retry='reduce_input_or_request_policy_review' if dimension else 'correct_input',bundle_state='absent',message_key=code.lower()),stdout='')
 phase='assessed';permit=disp not in ('evaluation_denied','evaluation_permission_unknown')
 available=disp!='baseline_unavailable'
 applicable=available and permit and not disp.startswith('withheld_due_to_inapplicable') and disp!='withheld_due_to_unknown_applicability'
 mapped=applicable
 rankable=disp in ('preferred_within_supplied_set','tied_best_within_supplied_set','no_discriminating_measurement')
 identities=lambda rs:[dict(id=get(r)['id'],revision=get(r)['revision'],reference=r) for r in sorted(rs,key=lambda r:get(r)['id'])]
 viable=[get(r)['id'] for r in hr]
 if v.get('refuted'):viable=viable[:-v['refuted']]
 cellrows=[]
 for h in hr:
  for m in mr:
   hid=get(h)['id'];mid=get(m)['id'];o=get(m)['decoder']
   for out in get(o)['outcomes']:
    key=(hid,mid,out['id']);value=c['cells'][key];reasons=[]
    if (v.get('partial') or v.get('conflict')) and key==('H1','T1','low'):value='unknown';reasons=['missing_exclusion_support']
    if v.get('conflict') and key==('H1','T1','high'):value='unknown';reasons=['opposing_qualified_sources']
    if (v.get('unavailable') or v.get('derived')) and hid=='H1' and mid=='T1':value='unknown';reasons=['unverified_derivation' if v.get('derived') else 'missing_support']
    if v.get('missing') and hid==get(hr[-1])['id'] and mid==get(mr[-1])['id']:value='unknown';reasons=['missing_row']
    relevant=[s for s in q['support'] if get(s)['hypothesis']==h and get(s)['procedure']==m]
    cellrows.append(dict(hypothesis=h,procedure=m,decoder=o,outcome=out['id'],relation=value,reasons=reasons,source_refs=sorted(relevant,key=lambda r:(r['kind'],r['sha256']))))
 branches=None;scores=None;best=None;recommend=None;equiv=None
 if rankable:
  branches=[];scores=[];equiv=[]
  for m in mr:
   mid=get(m)['id'];rows=[]
   for out in get(get(m)['decoder'])['outcomes']:
    survivors=sorted(h for h in viable if c['cells'][h,mid,out['id']]=='permits')
    rows.append(dict(outcome=out['id'],survivors=survivors))
   branches.append(dict(procedure=m,outcomes=rows))
   worst=max(len(x['survivors']) for x in rows)
   scores.append(dict(procedure=m,worst=worst,reduction=len(viable)-worst))
   equiv.append(dict(procedure=m,survivor_multiset=sorted([x['survivors'] for x in rows])))
  mn=min(x['worst'] for x in scores);best=[x['procedure'] for x in scores if x['worst']==mn]
  if len(best)==1 and len(viable)>mn:recommend=best[0]
 reasons=[]
 if disp=='evaluation_denied':
  dr=get(get(c['invocation'])['selection'])['declaration']
  if v.get('scope')=='false':reasons.append(dict(code='declaration_scope_false',subject=c['request'],detail=dict(declaration=dr)))
  if v.get('denied'):reasons.append(dict(code='request_not_member',subject=c['request'],detail=dict(declaration=dr)))
 elif disp=='evaluation_permission_unknown':reasons=[dict(code='declaration_scope_unknown',subject=c['request'],detail=dict(declaration=get(get(c['invocation'])['selection'])['declaration']))]
 elif not available:reasons=[dict(code='observation_absent',subject=q['evidence'],detail=None)]
 elif not applicable:reasons=[dict(code='condition_false' if 'inapplicable' in disp else 'condition_unknown',subject=mr[1],detail=dict(condition='baseline_ceiling' if 'ceiling' in v else 'calibration',observed=rat(601,10) if 'ceiling' in v else None,threshold=rat(v['ceiling']) if 'ceiling' in v else None))]
 else:
  for r in cellrows:
   if r['relation']=='unknown':reasons.append(dict(code=r['reasons'][0],subject=r['procedure'],detail=dict(hypothesis=r['hypothesis'],outcome=r['outcome'],decoder=r['decoder'],sources=r['source_refs'])))
 blocked='not_assessed_gate_blocked' if not permit else 'not_assessed_baseline_unavailable' if not available else 'not_assessed_inapplicable_candidate'
 assessments=[]
 if permit and available:
  for m in mr:
   rows=[]
   for con in get(m)['conditions']:
    state=con['state'] if con['kind']=='local_assumption' else ('true' if 601<=int(con['threshold']['numerator'])*10 else 'false')
    rows.append(dict(id=con['id'],state=state,basis=con.get('basis',[]),observed=rat(601,10) if con['kind']=='baseline_le' else None,threshold=con.get('threshold')))
   assessments.append(dict(procedure=m,conditions=rows))
 result=dict(schema='nm.result.v1',profile=PROFILE,invocation=c['invocation'],authority=dict(assessment_state='assessed',selection=get(c['invocation'])['selection'],declaration=get(get(c['invocation'])['selection'])['declaration'],adoption=get(c['invocation'])['adoption'],request=c['request'],policy=q['policy'],evaluation_permitted=permit,permission_state='permitted' if permit else 'denied' if disp=='evaluation_denied' else 'unknown'),evidence=dict(assessment_state='assessed',reference=q['evidence'],availability='admitted' if available else 'unavailable',observed=rat(601,10) if available else None,cn_verdict='violated' if available else None,lower_reasons=[] if available else [dict(code='observation_absent',path='/snapshot/constraint_evaluations/0/candidates/0/not_evaluated_reason')]),procedure_assessments=dict(assessment_state='assessed' if permit and available else blocked,procedure_identity_map=identities(mr),rows=assessments),hypothesis_assessments=dict(assessment_state='assessed' if permit and available else blocked,hypothesis_identity_map=identities(hr),viable=viable if permit and available else None,rows=[dict(hypothesis=h,checks=[dict(id=x['id'],expected=x['expected'],actual=rat(601,10) if x['kind']=='baseline_decimal_equals' else 'violated',status='satisfied' if x['kind']=='baseline_decimal_equals' or x['expected']=='violated' else 'contradicted') for x in get(h)['requirements']]) for h in hr] if permit and available else []),cells=dict(assessment_state='assessed' if mapped else blocked,rows=cellrows if mapped else []),ranking=dict(assessment_state='assessed' if rankable or disp in ('no_viable_hypotheses','no_discrimination_needed') else 'not_assessed_'+disp,disposition=disp,reasons=reasons,scores=scores,best=best,recommendation=recommend,branches=branches,equivalence=equiv),review=dict(assessment_state='assessed',groups=['evidence','hypotheses','procedures','decoders','support','authority','ranking_policy'],comparison='not_requested'),accounting={})
 return dict(kind='completed',exit_code=0,result=result)

start=time.perf_counter();cases=[];resources=[];allcommands=[]
for v in variants:
 c=make(v);id=v['id'];seen,edges_,missing,depth=graph(c['invocation']);expected_=expected(c)
 members=[dict(kind=k,sha256=h) for k,h in sorted(seen)]
 capture=[r for r in members if r not in c['omitted']]
 closure=dict(schema='nm.closure.v1',profile=PROFILE,invocation=c['invocation'],authority_pin=c['authority_pin'],members=[dict(reference=r,encoding='base64',bytes=base64.b64encode(seen[(r['kind'],r['sha256'])]).decode()) for r in capture],limits_override={'edge_visits':1} if v.get('tighten') else None)
 for row in closure['members']:
  if row['reference']['sha256'] in c['overrides']:row['bytes']=base64.b64encode(c['overrides'][row['reference']['sha256']]).decode()
 nodes=sum(counts(json.loads(b))[0] for (kind,h),b in seen.items() if kind!='nm.basis')
 qs=[json.loads(b) for (kind,h),b in seen.items() if kind=='nm.request.v1']
 es=[json.loads(b) for (kind,h),b in seen.items() if kind=='nm.evidence.v1']
 publicnodes=sum(counts(x['snapshot'])[0] for x in es)
 fullscan=sum(len(seen[(r['kind'],r['sha256'])]) for r in members)
 scanbytes=sum(len(seen.get((z['source']['kind'],z['source']['sha256']),b''))+len(seen.get((z['target']['kind'],z['target']['sha256']),b''))+66 for z in edges_)
 measurement=dict(case=id,unique_objects=len(seen),unique_bytes=fullscan,capture_bytes=sum(len(base64.b64decode(x['bytes'])) for x in closure['members']),reference_occurrences=len(edges_),edge_visits=len(edges_),active_depth=depth,request_contexts=len(qs),request_chain=v.get('chain',1),json_nodes=nodes,public_reconstruction_unique_nodes=publicnodes,public_reconstruction_context_nodes=sum(counts(get(x['evidence'])['snapshot'])[0] for x in qs),context_scan_bytes=scanbytes,closure_bytes=len(C(closure)),object_bytes=max(len(b) for b in seen.values()),invocation_bytes=len(C(get(c['invocation']))))
 # Phase 8 here means completion/publication, not an assertion that arithmetic ran.
 # Full structural trace is retained only for completed expectations; it records expected work, not observations.
 trace=dict(schema='nm.trace.v1',profile=PROFILE,invocation=c['invocation'],origin='independent_prepared_expectation',required_closure=members,reference_occurrences=edges_,phases=[dict(phase=i,state=('expected_reached' if i<=5 or i==8 else ('not_assessed_gate_blocked' if expected_.get('result',{}).get('authority',{}).get('evaluation_permitted') is False else 'not_assessed_baseline_unavailable' if v.get('baseline_unavailable') else 'not_assessed_inapplicable_candidate' if i==7 and (v.get('condition_unknown') or v.get('ceiling')==40) else 'expected_reached'))) for i in range(1,9)],semantic_origin='synthetic_conditional',physical_observed=False)
 if expected_['kind']=='completed':
  expected_['result']['accounting']=dict(assessment_state='assessed',logical_required={key:value for key,value in measurement.items() if key!='case'},physical='not_part_of_semantic_result')
  result=expected_['result'];files={'invocation.json':C(get(c['invocation'])),'closure.json':C(closure),'result.json':C(result),'trace.json':C(trace),'build.json':C(build),'policy.json':C(policy)}
  man=dict(schema='nm.bundle.v1',profile=PROFILE,files=[dict(name=n,bytes=len(b),sha256=H(b)) for n,b in sorted(files.items())],physical=dict(status='prepared_not_observed',bytes_read=None,read_operations=None,bytes_written=None,write_operations=None,elapsed_ns=None,peak_rss_bytes=None),completeness='manifest_last')
  files['manifest.json']=C(man)
  for n,b in files.items():write('expected/'+id+'/'+n,b)
  receipt=dict(schema='nm.receipt.v1',operation='measurement-evaluate',evaluation_permitted=result['authority']['evaluation_permitted'],disposition=result['ranking']['disposition'],result_sha256=H(files['result.json']),bundle_sha256=H(files['manifest.json']))
  write('expected/'+id+'/stdout.jsonl',C(receipt)+b'\n');write('expected/'+id+'/stderr',b'')
  measurement.update(result_bytes=len(files['result.json']),trace_bytes=len(files['trace.json']),bundle_bytes=sum(map(len,files.values())),manifest_bytes=len(files['manifest.json']),receipt_bytes=len(C(receipt))+1,diagnostic_bytes=0)
  for op in ['evaluate','verify','replay']:
   opreceipt=dict(receipt,operation='measurement-'+op)
   write('expected/'+id+'/'+op+'-stdout.jsonl',C(opreceipt)+b'\n')
   allcommands.append(dict(case=id,operation='measurement-'+op,expected_exit=0,expected='expected/'+id,actual_build_binding_required=True))
 else:
  write('expected/'+id+'/stderr.jsonl',C(expected_['diagnostic'])+b'\n');write('expected/'+id+'/stdout',b'')
  measurement.update(result_bytes=0,trace_bytes=0,bundle_bytes=0,manifest_bytes=0,receipt_bytes=0,diagnostic_bytes=len(C(expected_['diagnostic']))+1)
  allcommands.append(dict(case=id,operation='measurement-evaluate',expected_exit=expected_['exit_code'],expected='expected/'+id,actual_build_binding_required=True))
 write('inputs/'+id+'/invocation.json',get(c['invocation']));write('inputs/'+id+'/capture.json',closure)
 # Retain explicit oracle table independently of result serialization.
 write('oracle/'+id+'.json',dict(spec=v,cell_table=[dict(h=h,m=m,o=o,relation=rel) for (h,m,o),rel in sorted(c['cells'].items())],expected_kind=expected_['kind'],expected_exit=expected_['exit_code'],expected_disposition=None if v['code'] else v['disposition'],nomination_request=c['request'],authority_pin=c['authority_pin'],omitted=c['omitted'],static_missing=missing))
 cases.append(dict(id=id,kind=expected_['kind'],expected_exit=expected_['exit_code'],disposition=v['disposition'] if not v['code'] else None,request=c['request'],invocation=c['invocation'],authority_pin=c['authority_pin'],input='inputs/'+id,expected='expected/'+id,oracle='oracle/'+id+'.json',notes='Prepared exact bytes bind a NONEXECUTABLE build witness. Not a runtime success.'))
 resources.append(measurement)
for (kind,h),b in objects.items():write('objects/'+h+'.'+kind,b)
write('cases.json',cases);write('commands.json',allcommands);write('resource-policy.json',policy)
write('build-placeholder.json',build)
maxima={key:max(r[key] for r in resources) for key in resources[0] if key!='case'}
write('measurements.json',dict(status='measured_static_bytes_and_structure_not_runtime',per_case=resources,corpus_maxima=maxima,physical_preparation=dict(elapsed_seconds=time.perf_counter()-start,peak_rss_platform_units=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,unit='KiB_on_this_Linux_host',not_future_runtime_measurement=True),case_count=len(cases),completed=sum(c['kind']=='completed' for c in cases),refused=sum(c['kind']=='refusal' for c in cases),planned_commands=len(allcommands)))
write('harness-only.json',dict(status='not_executed',cases=[dict(id='B-bypass',input_from='U',mutation='Replace only H1/T1/low unknown with unsupported excludes.',expected_scores={'T1':1,'T2':2},expected_label='invalid_counterfactual_not_recommendation',production_option=False),dict(id='cycle-active-path',nodes=['a','b'],edges=[['a','b'],['b','a']],expected='REFERENCE_CYCLE',boundary='isolated_future_graph_harness_not_hash_consistent_wire'),dict(id='cycle-shared-twin',nodes=['a','b','c'],edges=[['a','b'],['a','c'],['c','b']],expected='shared_completed_not_cycle'),dict(id='stricter-context',expected='recheck_effective_limits_not_cached_permission'),dict(id='permutation-construction',expected='same_canonical_Q_and_semantic_result'),dict(id='reverse-directory-order',expected='same_semantic_closure_and_result')]))
write('manual-C.json',dict(status='unresolved',claims=[dict(id='C-left',gamma='4',scope='same_quantity_unit_step'),dict(id='C-right',gamma='2',scope='same_quantity_unit_step')],basis='opposed synthetic declarations; no independent physical evidence',invocation='withheld',recommendation=None,application_commands=0,negative_draft='Reject a draft choosing gamma=4 without owner disposition.'))
print(json.dumps(dict(cases=len(cases),completed=sum(c['kind']=='completed' for c in cases),refused=sum(c['kind']=='refusal' for c in cases),commands=len(allcommands),objects=len(objects),maxima=maxima)))
