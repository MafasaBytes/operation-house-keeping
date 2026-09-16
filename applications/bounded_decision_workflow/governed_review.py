"""Internal governed evaluation/review; no CLI, persistent writes or replay receipt."""
from dataclasses import dataclass,asdict
from fractions import Fraction
import json

from . import governed_admission as gate,governed_build,policy,projection
from .governed_contracts import I,S,D,A,T,Q,B,validate,decode,edges
from .governed_resources import Budget,problem,bounded_json
from .errors import refusal
from .input import canonical_json_bytes as C,effective_limits
from .decision_review import _support_and_decisions,_changed_paths
from .projection_profile import ACTIONS,validate_profile
from .governed_closure import validate_carried,Carried,shape,schemas
from .governed_context import make_closure,accounting

H=gate.H
BLOCK='not_computed_gate_blocked'

@dataclass(frozen=True)
class GovernedReview:
    result_bytes: bytes
    trace_bytes: bytes
    physical_bytes: bytes
    closure_bytes: bytes
    prior_results: tuple=()
    scope: str='internal_governed_review_not_published'

def compare_assessments(current,previous):
    flags={k+'_changed':None if previous is None else current[k]!=previous[k] for k in ('availability','status','diagnostics')}
    comparable=bool(previous is not None and current['numeric_kind']!='none' and
                    current['numeric_kind']==previous['numeric_kind'] and
                    current['numeric_value'] is not None and previous['numeric_value'] is not None and
                    current['availability']!='blocked' and previous['availability']!='blocked')
    flags.update(numeric_comparable=comparable,numeric_value_changed=current['numeric_value']!=previous['numeric_value'] if comparable else None)
    return flags

def _nominal(a,policy_result):
    if policy_result is not None:return _support_and_decisions(policy_result)
    # No projection planner runs for a denied world. Nominal dependency edges
    # follow the same fixed profile; all descendant values remain absent.
    q=a.request.model_dump(mode='json');p=q['premises'];supports={'snapshot':a.snapshot_input.raw,'question':q['current_condition_question'],
        'observed:T0':{'snapshot':a.snapshot_input.sha256,'binding':q['observed_input_binding']}}
    def register(x):
        if type(x) is dict:
            if 'premise_id' in x:supports['premise:'+x['premise_id']]=x
            else:
                for v in x.values():register(v)
    register(p);register(q['target_policy'])
    costs=q['target_policy']['costs'];supports['cost_policy']={k:v for k,v in costs.items() if k not in ('value','canonical_commitment')}
    supports['cost_policy']['cost_token']=costs['value']['cost_token'] if costs['value'] else None
    entries=costs['value']['entries'] if costs['value'] else []
    for action in ACTIONS:supports['cost:'+action['action_id']]=next((x for x in entries if x['action_id']==action['action_id']),None)
    deps={'current_condition':['snapshot','question']};values={'current_condition':a.current_condition.computed_match}
    common=[p[k] for k in ('actions','commands','global_applicability','hypotheses','law','support_semantics')]+list(p['coordinates'].values())
    for h in ('H_F','H_H'):
        for action in ACTIONS:
            req=common+[p['global_applicability']]+[p[group][pid] for field,group in
                [('precondition_ids','preconditions'),('timing_ids','timing'),('invariance_ids','invariances'),('effect_ids','effects')] for pid in action[field]]
            rid=f"raw:{h}:{action['action_id']}";deps[rid]=sorted({'observed:T0',*('premise:'+x['premise_id'] for x in req)});values[rid]=None
    for h in ('H_F','H_H'):
        for action in ACTIONS:
            rid=f"target:{h}:{action['action_id']}";deps[rid]=sorted([f"raw:{h}:{action['action_id']}",'premise:P-target']);values[rid]=None
    retained=q['target_policy']['retained_hypotheses'];hs=retained['value']['hypothesis_ids'] if retained['availability']=='present' else ['H_F','H_H']
    for action in ACTIONS:
        aid=action['action_id'];rid='feasibility:'+aid
        deps[rid]=sorted([f'target:{h}:{aid}' for h in hs]+['premise:'+p for p in action['precondition_ids']+action['timing_ids']+action['invariance_ids']]+['premise:P-retained','premise:P-feasibility','premise:P-applicability']);values[rid]=None
    deps['selection']=sorted(['feasibility:'+x['action_id'] for x in ACTIONS]+['premise:P-actions','premise:P-applicability','premise:P-selection','cost_policy']+['cost:'+x['action_id'] for x in ACTIONS]);values['selection']=None
    return supports,deps,values

def _rows(a,g,iv,sc,policy_result,previous,budget):
    supports,deps,values=_nominal(a,policy_result)
    gv={'evaluation_permitted':g.evaluation_permitted,'disposition':g.disposition,'reason':g.reason}
    supports['governing']={'declaration':sc['declaration'],'scenario':iv['scenario'],'selection':iv['selection'],'adoption':iv['adoption'],
                         'world':H(g.world_key),'fixed':H(g.fixed_key)}
    deps={'admissibility':['governing'],**{k:sorted(v+(['admissibility'] if k!='current_condition' else [])) for k,v in deps.items()}}
    values={'admissibility':gv,**values};rows=[];required=set();assessments={}
    old_supports,old_deps,old_rows=previous if previous else (supports,deps,{})
    def diagnostics(rid,value):
        if rid=='admissibility':return [{'source':'gate','id':rid,'reason':g.reason}]
        if rid=='current_condition':return [{'source':'current_condition','id':'refusals/'+str(i),'reason':v} for i,v in enumerate(a.current_condition.refusals)]
        out=[]
        frontier=None
        if rid.startswith('raw:') and policy_result is not None:
            tr=next(x for x in policy_result.projection.raw_trace['projection_rows'] if rid==f"raw:{x['hypothesis_id']}:{x['action_id']}")
            frontier=set(tr['frontier_ids'])
        for d in deps[rid]:
            # Gate permission is a dependency, not an unavailable physical cause.
            if d=='admissibility':continue
            if d in assessments:out+=assessments[d]['diagnostics']
            elif d=='observed:T0' and a.observed_value.status=='unavailable' and (frontier is None or d in frontier):out.append({'source':'observed','id':d,'reason':a.observed_value.unavailable_reason})
            elif d.startswith('premise:'):
                p=supports[d]
                if frontier is not None and p['premise_id'] not in frontier:continue
                if p['availability']!='present':out.append({'source':'premise','id':p['premise_id'],'reason':p['availability']})
                elif type(p['value']) is dict and p['value'].get('status') is False:out.append({'source':'premise','id':p['premise_id'],'reason':'false'})
        unique=[]
        for d in out:
            if d not in unique:unique.append(d)
        return unique
    for rid in deps:
        budget.work('decision_rows',1,scope='current_rows')
        inputs=sorted(set(deps[rid])|set(old_deps.get(rid,[])))
        need=previous is not None and (deps[rid]!=old_deps.get(rid) or any(
            d in required if d in deps else supports.get(d)!=old_supports.get(d) for d in inputs))
        if need:required.add(rid)
        performed=rid in ('admissibility','current_condition') or g.evaluation_permitted
        value=values[rid] if performed else None;computed=performed and value is not None
        number=None;kind='none'
        if not performed:status=BLOCK;availability='blocked';ds=[]
        else:
            ds=diagnostics(rid,value)
            if rid=='admissibility':status=g.disposition;availability='available'
            elif rid=='current_condition':status=a.current_condition.disposition;availability='available' if computed else 'unavailable'
            elif rid.startswith('raw:'):
                status=value['raw_status'];availability='available' if status=='ready' else 'unavailable'
                if status=='ready':kind='degree_celsius_interval';number=value['raw_interval']
            elif rid=='selection':
                status=value['disposition'];availability='unavailable' if status in ('unknown','inapplicable_for_declared_model') else 'available'
                if value['minimum_cost'] is not None:kind='supplied_cost';number=value['minimum_cost']
            else:status=value;availability='unavailable' if status in ('unknown','inapplicable') else 'available'
        assessment={'availability':availability,'status':status,'diagnostics':ds,'numeric_kind':kind,'numeric_value':number}
        assessments[rid]=assessment;old=old_rows.get(rid)
        typed=bool(old and computed and old['computed']);changed=(value!=old['value']) if typed else None
        flags=compare_assessments(assessment,old['assessment'] if old else None)
        if previous and not need and (changed or any(flags[k] is True for k in ('availability_changed','status_changed','diagnostics_changed','numeric_value_changed'))):
            raise RuntimeError('assessment changed without governing dependency')
        rows.append({'decision_id':rid,'depends_on':inputs,'value':value,'computed':computed,'performed':performed,
                     'reevaluation':'not_applicable_no_prior' if previous is None else 'required' if need else 'not_required',
                     'value_changed':changed,'equal_after_reevaluation':not changed if typed and need and performed else None,
                     'blocked_reason':None if performed else BLOCK,'assessment':assessment,**flags})
    return rows,(supports,deps,{x['decision_id']:x for x in rows})

def _render(a,iv,sc,p,rows,counts,budget):
    ir={'kind':I,'sha256':H(C(iv))};bid=iv['build_identity']
    current=dict(asdict(a.current_condition),as_of=a.request.current_condition_question.as_of.isoformat(),declared_state_label=a.request.current_condition_question.declared_state_label,meaning='classification_at_exact_cutoff_not_projected_state')
    obs=asdict(a.observed_value);n=Fraction(obs['canonical_decimal']) if obs['canonical_decimal'] is not None else None
    obs.update(disposition=obs['status'],source='public_candidate_only',admitted_T0=None if n is None else {'numerator':n.numerator,'denominator':n.denominator})
    blocked={'status':BLOCK}
    result={'schema':'governed-result.v2','invocation':ir,'build_identity':bid,
            'authority_statement':{'status':'owner_attested_not_authenticated','declaration':sc['declaration'],'selection':iv['selection'],'adoption':iv['adoption'],'currentness':'relative_to_captured_selection_only'},
            'admissibility':rows[0]['value'],'current_condition':current,'observed_value_admission':obs,
            'raw_projections':p.projection.raw_projections if p else blocked,'target_relations':p.target_relations if p else blocked,
            'feasibility':p.feasibility if p else blocked,'selection':p.selection if p else blocked,
            'decision_review':{'comparison':'compared' if iv['comparison'] else 'no_prior_supplied','rows':rows},'resource_accounting':counts}
    trace={'schema':'governed-trace.v2','invocation':ir,'rows':rows,'projection_trace':p.projection.raw_trace['projection_rows'] if p else []}
    requested=a.request_input.raw['requested_limits'] or {}
    def cap(name,legacy):return min(budget.caps[name],requested.get(legacy,budget.caps[name]))
    rb=projection._serialize(result,cap('result_bytes','output_result_bytes'),cap('result_nodes','output_result_nodes'))
    tb=projection._serialize(trace,cap('trace_bytes','output_trace_bytes'))
    return rb,tb


class _KernelStore(gate._Captured):
    def __init__(self,current,entries,budget,carried):
        # Internal assembly is not a second supplied occurrence. Reuse the
        # already captured bytes; genuinely new carried objects still pay capture.
        fresh=gate._Captured([(k,w) for k,w in entries if H(w) not in current.items],budget)
        self.b=budget;self.items=dict(current.items);self.items.update(fresh.items)
        self.walker=current.walker
        self.manifests={H(w.files['manifest.json']):w.files['manifest.json'] for w in carried.worlds} if carried else {}

    def visit(self,ref,kind,*,shallow=False,source=None):
        if kind=='prior-bundle-manifest':
            # These bytes have passed complete owning in-memory validation, not
            # a caller flag. Ancestor inputs are separately gated before dispatch.
            if ref['sha256'] not in self.manifests:raise problem('HISTORY_INCOMPATIBLE')
            if source is not None:
                wire=self.manifests[ref['sha256']];raw=json.loads(wire)
                self.b.work('edge_visits',1,scope='comparison_reference')
                self.b.work('context_nodes',source[3]+gate._nodes(raw)+2,scope='comparison_reference')
                self.b.work('context_bytes',len(source[1])+len(wire)+66,scope='comparison_reference')
            return
        return super().visit(ref,kind,shallow=shallow,source=source)


def evaluate(invocation_wire,objects,*,expected_authority_pin,prior_files=None,limits=None,observer=None):
    """All current/ancestor gates finish before any projection; no writes or CLI."""
    budget=Budget(limits,observer)
    iv=validate(I,decode(invocation_wire,budget.caps['request_wire_bytes'],budget.caps))
    budget.world=H(invocation_wire)
    def startup(event):
        if observer:
            try:observer(dict(event,phase='startup_build',world=budget.world))
            except Exception as e:raise refusal('INTERNAL_ERROR',stage='internal_failure',target='instrumentation',retry='investigate',exit_code=7) from e
    bw,bid=governed_build.identity(observer=startup)
    if iv['build_identity']!=bid:raise governed_build.unavailable()
    carried=None
    if iv['comparison'] is not None:
        carried=validate_carried(prior_files,expected_manifest=iv['comparison']['sha256'],expected_build=bw,budget=budget)
    elif prior_files is not None:raise problem('HISTORY_INCOMPATIBLE')
    # Capture current objects under accepted admission's guards before assembly.
    current=gate._Captured(objects,budget)
    if H(invocation_wire) in current.items:
        # The separately supplied root is another capture occurrence even if its
        # immutable bytes were also supplied in the object list. Reuse parsing,
        # not the reference/capture allowance for that extra occurrence.
        budget.work('context_nodes',1,scope='root_capture_record',extra=True)
        budget.work('capture_bytes',len(invocation_wire),scope='root_capture')
        for _ in edges(I,iv):budget.work('supplied_references',1,scope='root_capture')
    entries=[(v[0],v[1]) for v in current.items.values()]
    z,zw,worlds=make_closure(invocation_wire,entries,expected_authority_pin,bw,carried,budget.caps)
    logical=accounting(z,zw,worlds,carried,budget.caps)
    floor_keys={'lower_charges':'review_resolution_charges','lower_references':'review_reference_occurrences',
                'lower_resolved_bytes':'review_resolved_bytes','reference_occurrences':'supplied_references','decision_slots':'decision_rows'}
    budget.require_floor({floor_keys.get(k,k):v for k,v in logical.items() if k not in ('schema','lower_reconstructions')})
    known={(z['objects'][x['scenario']['sha256']]['canonical_json']['request']['sha256'],
            z['objects'][x['scenario']['sha256']]['canonical_json']['snapshot']['sha256']) for x in worlds}
    # A single typed input store permits legitimate shared validation scopes.
    inputs=[]
    for h,e in z['objects'].items():
        if e['kind'] in (D,S,A,T,I,Q,B,'captured-basis'):
            if 'canonical_json' in e:wire=C(e['canonical_json'])
            else:
                import base64
                wire=base64.b64decode(''.join(e['opaque_chunks']),validate=True)
            inputs.append((e['kind'],wire))
    store=_KernelStore(current,inputs,budget,carried)
    admitted=[]
    for x in worlds:
        ir={'kind':I,'sha256':H(C(x))}
        if x['build_identity']!=bid:raise problem('HISTORY_INCOMPATIBLE')
        pin=expected_authority_pin if x is worlds[-1] else next(w.closure['expected_authority_pin'] for w in carried.worlds if w.closure['invocation']==ir)
        g,a=gate._assess_context(store,x,ir,pin,budget,nominated_pairs=known)
        admitted.append((x,g,a,store.get(x['scenario'],S)[2]))
    budget.work('retention_bytes',budget.caps['retention_bytes'],scope='output_reservation')
    for x,g,a,sc in admitted:
        local=effective_limits(a.request)
        if 23+(8 if g.evaluation_permitted else 0)>min(budget.caps['trace_rows'],local['output_trace_rows']):
            raise problem('OUTPUT_LIMIT_EXCEEDED',resource=True,target='trace_rows')
    # Preserve the existing changed-frontier cap, even though v2 exposes the
    # dependency rows rather than a new changed-path output field. This extra
    # scan is charged positively; a cache saving cannot pay for it.
    root_limit=effective_limits(admitted[-1][2].request)['changed_paths']
    for before,after in zip(admitted,admitted[1:]):
        old=before[2];new=after[2];budget.world=H(C(after[0]))
        left={'request':old.request_input.raw,'snapshot':old.snapshot_input.raw}
        right={'request':new.request_input.raw,'snapshot':new.snapshot_input.raw}
        budget.work('context_nodes',gate._nodes(left)+gate._nodes(right),scope='changed_paths',extra=True)
        budget.work('context_bytes',len(old.request_input.canonical_bytes)+len(old.snapshot_input.canonical_bytes)+
                    len(new.request_input.canonical_bytes)+len(new.snapshot_input.canonical_bytes),scope='changed_paths',extra=True)
        with budget.operation('dependency_preflight'):
            _changed_paths(left,right,min(root_limit,effective_limits(new.request)['changed_paths']))
    previous=None;completed=[];corners=0
    for index,(x,g,a,sc) in enumerate(admitted):
        budget.world=H(C(x));p=None
        if g.evaluation_permitted:
            local=effective_limits(a.request)
            with budget.operation('projection_plan'):
                count=projection._prepare_projection(a,local,validate_profile(a.request,local))[3]
            budget.work('corner_evaluations',count,scope='projection')
            with budget.operation('policy_assessment'):p=policy._assess_admitted(a,limits=local)
            if p.projection.corner_evaluations!=count:raise RuntimeError('projection work differs from reservation')
            corners+=count
        rows_budget=Budget(limits,observer);rows_budget.world=budget.world
        with budget.operation('row_review'):rows,previous=_rows(a,g,x,sc,p,previous,rows_budget)
        if index==len(admitted)-1:counts=dict(logical)
        else:
            w=carried.worlds[index]
            prior=Carried(carried.worlds[index-1].files,carried.worlds[:index],sum(sum(map(len,v.files.values())) for v in carried.worlds[:index])) if index else None
            counts=accounting(w.closure,w.files['resolved-input.json'],worlds[:index+1],prior,budget.caps)
        counts['corner_evaluations']=corners
        with budget.operation('output_construction'):rb,tb=_render(a,x,sc,p,rows,counts,budget)
        if index<len(admitted)-1:
            w=carried.worlds[index]
            if rb!=w.files['result.json'] or tb!=w.files['trace.json']:raise problem('HISTORY_INCOMPATIBLE')
        completed.append((rb,tb))
    # Required logical schedule is a floor, not a claim that cache savings may
    # cancel positive excess. Capture-record overhead is separately charged.
    mapping={'lower_charges':'review_resolution_charges','lower_references':'review_reference_occurrences','lower_resolved_bytes':'review_resolved_bytes'}
    dimensions=('scope_expansions','edge_visits','context_nodes','context_bytes','lower_charges','lower_references',
                'lower_resolved_bytes','prior_capture_bytes','reconstruction_bytes','corner_evaluations','capture_bytes')
    physical={'schema':'internal-governed-kernel-work.v1','coverage':'in_memory_kernel_only_not_publication',
              'logical_commitment':H(C(counts)),'operations':budget.operations,'actual':{},'extra':{},'charged':{},
              'output_reserved_bytes':budget.actual['retention_bytes']}
    for name in dimensions:
        k=mapping.get(name,name);extra=budget.extra[k];charged=counts[name]+extra
        if budget.actual[k]>charged or charged>budget.caps[k]:raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target=k)
        physical['actual'][name]=budget.actual[k];physical['extra'][name]=extra;physical['charged'][name]=charged
    pb=bounded_json(physical,budget.caps['physical_evidence_bytes'],'physical_evidence_bytes')
    return GovernedReview(rb,tb,pb,zw,tuple(completed[:-1]))
