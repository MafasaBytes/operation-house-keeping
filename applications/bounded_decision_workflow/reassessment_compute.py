"""Slice 3: model-relative full-envelope reporting from captured input only.

No file access, caller validation flags, expected-output input, ranking, adoption,
publication or replay. Admission is always recomputed through its owning adapter.
"""
from copy import deepcopy
from itertools import zip_longest

from .reassessment_admission import admit, _get, _reason
from .reassessment_contracts import PROFILE
from .measurement_compute import ratio
from .measurement_wire import key, ref, rational, fail, bounded_json
from .measurement_contracts import canonical_json_bytes
from .support_qualification import qualify_supplied_support


def _finite_decimal(number, work):
    denominator = number.denominator
    for factor in (2, 5):
        while True:
            work.charge('rational_operations')
            if denominator % factor: break
            denominator //= factor
    return denominator == 1


def intersect(region, lo, hi, work):
    """Intersect with a closed envelope in the finite-decimal scalar domain."""
    work.charge('interval_intersections')
    lower = None if region['lower'] is None else rational(region['lower'],work)
    upper = None if region['upper'] is None else rational(region['upper'],work)
    left, right = lo, hi
    lc = uc = True
    if lower is not None:
        work.charge('rational_operations',2)
        left = max(lo,lower); lc = lo>lower or region['lower_closed']
    if upper is not None:
        work.charge('rational_operations',2)
        right = min(hi,upper); uc = hi<upper or region['upper_closed']
    work.charge('rational_operations',2)
    if left>right or left==right and not (lc and uc and _finite_decimal(left,work)):
        return None
    return dict(lo=ratio(left),hi=ratio(right),lower_closed=lc,upper_closed=uc)


def _cover(branches, lo, hi, work, request, decoder):
    """Defensive no-hole/no-overlap check over all represented supported values."""
    intervals=[]
    for b in branches:
        r=b['intersection'];intervals.append((rational(r['lo'],work),rational(r['hi'],work),r['lower_closed'],r['upper_closed']))
    intervals.sort()
    invalid=not intervals
    if intervals:
        work.charge('rational_operations',2)
        invalid |= intervals[0][0]!=lo or intervals[-1][1]!=hi
        invalid |= _finite_decimal(lo,work) and not intervals[0][2]
        invalid |= _finite_decimal(hi,work) and not intervals[-1][3]
        for a,b in zip(intervals,intervals[1:]):
            work.charge('rational_operations',2)
            invalid |= a[1]!=b[0]
            if a[1]==b[0] and _finite_decimal(a[1],work):invalid |= a[3]==b[2]
    if invalid:fail('DECODER_INVALID','/interpretation/branches','phase_7',request=request,references=[decoder])


def _ordered_reasons(reasons):
    unique={canonical_json_bytes(r):r for r in reasons}
    return sorted(unique.values(),key=lambda r:(r['code'],r['path'],[key(x) for x in r['references']]))


def _gate_reasons(a,g,q,oq):
    """Map internal admission reasons to the approved result coordinates."""
    reasons=[]
    names=('applicability','availability','calibration','fidelity','hold')
    for original in a.reasons:
        r=deepcopy(original);code=r['code']
        if code in ('evaluation_denied','evaluation_permission_unknown'):
            r['code']='permission_'+a.permission
        elif r['path'].startswith('/conditions/'):
            ident=r['path'].split('/')[-1];idx=names.index(ident)
            execution=q['execution'] in r['references']
            r['path']=('/execution/conditions/' if execution else '/original/procedure/conditions/')+str(idx)
            if execution and ident=='hold' and code=='condition_unknown':r['code']='hold_unknown'
        elif code.startswith('uncertainty_'):r['references']=[g.root]
        elif a.disposition=='baseline_unavailable':r['path']='/original/evidence'+r['path']
        reasons.append(r)
    # Admission already preserves phase/condition order; do not replace this by
    # alphabetical condition names or lose independently reached reasons.
    return reasons


def _changes(g,q,oq,original):
    if q['predecessor'] is None:return []
    previous=_get(g,q['predecessor']);pi=_get(g,previous['original_invocation']);pq=_get(g,pi['request'])
    pairs=[('/original_invocation',previous['original_invocation'],q['original_invocation']),
           ('/original/request',pi['request'],original['request']),
           ('/original/evidence',pq['evidence'],oq['evidence']),
           ('/procedure',previous['procedure'],q['procedure']),
           ('/decoder',previous['decoder'],q['decoder'])]
    for field in ('support','hypotheses'):
        pairs.extend(('/original/'+field+'/'+str(i),before,after)
                     for i,(before,after) in enumerate(zip_longest(pq[field],oq[field])))
    return [dict(path=path,before=before,after=after) for path,before,after in sorted(pairs) if before!=after]


def compute(g):
    """Derive result/trace; no prepared output can supply the computation."""
    a=admit(g);w=g.work;q=_get(g,a.request);original=_get(g,q['original_invocation']);oq=_get(g,original['request'])
    reasons=_gate_reasons(a,g,q,oq);ready=a.disposition=='ready_for_interpretation'
    rows=[]
    for h in a.hypotheses:
        baseline=h['baseline']
        status='not_assessed' if baseline=='not_assessed' else 'baseline_ineligible' if baseline=='baseline_ineligible' else 'unresolved'
        outcome='not_assessed_'+baseline if baseline in ('baseline_unknown','baseline_ineligible') else 'not_assessed'
        rows.append(dict(reference=h['reference'],baseline=baseline,baseline_checks=deepcopy(h['baseline_checks']),
            status=status,outcome_state=outcome,cells=None,reasons=[] if baseline in ('not_assessed','baseline_ineligible') else deepcopy(reasons)))
    observation=deepcopy(a.observation)
    if observation['availability']=='unavailable':observation['unit']=None
    envelope=deepcopy(a.envelope)
    if envelope is not None and envelope['basis_kind']=='hard_interval':envelope['basis_kind']='declared_hard_interval'
    branches=None
    if ready:
        decoder=_get(g,q['decoder']);lo=rational(envelope['lo'],w);hi=rational(envelope['hi'],w)
        branches=[]
        for outcome in decoder['outcomes']:
            intersection=intersect(outcome['region'],lo,hi,w)
            if intersection is not None:branches.append(dict(outcome=outcome['id'],intersection=intersection))
        _cover(branches,lo,hi,w,a.request,q['decoder'])
        outcomes=[o['id'] for o in decoder['outcomes']];in_envelope={b['outcome'] for b in branches}
        # The original full nomination is retained. Qualification is restricted
        # to the selected procedure and baseline-eligible H, not a new H set.
        for row in rows:
            if row['baseline']!='baseline_eligible':continue
            hr=row['reference'];sources=[];support=[]
            for sr in oq['support']:
                s=_get(g,sr)
                if s['hypothesis']==hr and s['procedure']==q['procedure']:sources.append(sr);support.append(s)
            pairs=sorted(zip(sources,support),key=lambda p:key(p[0]));sources=[p[0] for p in pairs];support=[p[1] for p in pairs]
            w.charge('qualified_cells',len(outcomes));w.charge('mapped_cells',len(outcomes))
            w.charge('source_contributions',len(support)*len(outcomes))
            cells=qualify_supplied_support(support,hypothesis=hr,procedure=q['procedure'],decoder=q['decoder'],
                evidence=oq['evidence'],context=oq['context'],outcomes=outcomes)
            if cells and all(c.relation=='excludes' for c in cells):
                fail('ROW_ALL_EXCLUDED','/cells/'+_get(g,hr)['id']+'/'+_get(g,q['procedure'])['id'],'phase_7',
                    request=original['request'],references=sorted([hr,q['procedure']],key=key))
            row['cells']=[];row['outcome_state']='assessed'
            for cell in cells:
                if cell.outcome not in in_envelope:continue
                relation={'supports':'permits','excludes':'excludes'}.get(cell.relation,'unknown')
                codes=[]
                if relation=='unknown':
                    if 'support_conflict' in cell.reasons:codes.append('opposing_qualified_sources')
                    if 'support_unavailable' in cell.reasons:
                        codes.extend(s['qualification']['reason'] for s in support if s['qualification']['status']=='unavailable')
                    if 'unsupported_exclusion' in cell.reasons:codes.append('unsupported_exclusion')
                    if not codes:codes.append('missing_exclusion_support' if support else 'missing_row')
                cr=[_reason(code,'/support',sources) for code in sorted(set(codes))]
                row['cells'].append(dict(outcome=cell.outcome,relation=relation,sources=sources,reasons=cr))
            relations={c['relation'] for c in row['cells']}
            row['status']=('compatible_under_declared_model' if relations=={'permits'} else
                           'conditionally_incompatible' if relations=={'excludes'} else 'unresolved')
            row['reasons']=_ordered_reasons([r for c in row['cells'] for r in c['reasons']])
            if row['status']=='unresolved' and not row['reasons']:
                row['reasons']=[_reason('mixed_permit_exclude','/hypotheses/'+_get(g,hr)['id']+'/cells',sources)]
    categories={name:sorted([r['reference'] for r in rows if r['status']==status],key=key)
        for name,status in [('compatible','compatible_under_declared_model'),('incompatible','conditionally_incompatible'),
                            ('unresolved','unresolved'),('baseline_ineligible','baseline_ineligible')]}
    if a.permission!='true':categories={name:None for name in categories}
    disposition=a.disposition
    if ready:
        disposition=('incomplete_assessment' if categories['unresolved'] else 'model_prediction_mismatch' if not categories['compatible'] else
                     'one_compatible' if len(categories['compatible'])==1 else 'multiple_compatible')
        reasons=_ordered_reasons([r for row in rows for r in row['reasons']])
    exposure=deepcopy(a.exposure);exposure['changed_references']=_changes(g,q,oq,original)
    result=dict(schema='nr.result.v2',profile=PROFILE,invocation=g.root,
        authority=dict(reference=g.invocation['authority'],pin=g.invocation['authority']['sha256'],permission=a.permission),
        original=dict(invocation=q['original_invocation'],request=original['request'],procedure=q['procedure'],decoder=q['decoder'],
            evidence=oq['evidence'],hypotheses=oq['hypotheses'],ranking='not_reassessed'),
        observation=observation,interpretation=dict(state='assessed' if ready else 'not_assessed',envelope=envelope,branches=branches,reasons=[]),
        exposure=exposure,hypotheses=rows,summary=dict(disposition=disposition,**categories,reasons=reasons),adoption='derived_not_adopted',
        accounting=dict(logical={k:w.logical.get(k,0) for k in (
            'unique_objects','capture_bytes','object_bytes','closure_bytes','reference_occurrences','json_nodes','json_depth','string_bytes',
            'containment_comparisons','interval_intersections','baseline_checks','qualified_cells','source_contributions')},physical='recorded_in_manifest'))
    result['accounting']['logical']['prior_bundle_bytes']=w.logical.get('reconstructed_file_bytes',0)
    reason_phase=5 if a.permission!='true' else 7 if ready else 6
    trace=dict(schema='nr.trace.v2',profile=PROFILE,invocation=g.root,required_closure=[ref(*k) for k in sorted(g.objects)],
        phases=[dict(phase=i,state='not_assessed' if (i==6 and a.permission!='true') or (i==7 and not ready) else 'assessed',
                     reasons=reasons if i==reason_phase else []) for i in range(1,9)],
        dependencies=sorted([dict(result_path='/observation',references=[q['observation'],observation['evidence']]),
            dict(result_path='/hypotheses',references=sorted(oq['hypotheses']+oq['support']+[oq['evidence'],q['decoder']],key=key)),
            dict(result_path='/exposure',references=[q['exposure']]),dict(result_path='/authority',references=[g.invocation['authority']])],key=lambda r:r['result_path']))
    # Only bounded semantic output is built here. Phase 8 does not claim filesystem
    # publication; the later delivery layer must reserve/publish the whole bundle.
    w.high('result_bytes',len(bounded_json(result,w,'result_bytes')))
    w.high('trace_bytes',len(bounded_json(trace,w,'trace_bytes')))
    return result,trace
