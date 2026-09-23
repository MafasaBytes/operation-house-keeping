"""Closure-owned admission, support qualification and finite minimax composition.

No public_request wrapper, external source list or supplied survivor matrix is
accepted here. Every input is selected by the captured invocation/request graph.
"""
from fractions import Fraction
from types import SimpleNamespace
from pydantic import ValidationError
from backend.state_classification import StateClassificationResult
from .admission import _assess_current_condition, _admit_observed_value
from .contracts import CurrentConditionQuestion, ObservedInputBinding
from .input import parse_snapshot_wire, enforce_snapshot_limits, BUILD_LIMITS
from .errors import WorkflowInputError
from .measurement_wire import canonical_json_bytes, key, ref, rational, fail, PROFILE
from .support_qualification import qualify_supplied_support
from .measurement_ranking import rank_measurements


def ratio(n):return {'numerator':str(n.numerator),'denominator':str(n.denominator)}


def public_evidence(e,context,work):
    """Reconstruct with owning validator, then reuse maintained exact joins.

    The small attribute adapter carries measurement roles, not a thermal
    WorkflowRequest or a thermal premise commitment/authority.
    """
    wire=canonical_json_bytes(e['snapshot'])
    parsed=parse_snapshot_wire(wire);enforce_snapshot_limits(parsed,dict(BUILD_LIMITS))
    work.charge('public_reconstruction_nodes',parsed.counts.nodes)
    work.charge('public_reconstructions')
    try:
        snapshot=StateClassificationResult.model_validate(parsed.raw)
    except (ValidationError,ValueError,TypeError,AttributeError,KeyError):
        fail('PUBLIC_RECONSTRUCTION_INVALID','evidence.snapshot','phase_4')
    try:
        question=CurrentConditionQuestion.model_validate(e['question'])
        # Reuse owning primitive validation for the binding without constructing
        # thermal role premises. Only their validated public tokens/indices are used.
        typed=ObservedInputBinding.model_validate(dict(e['binding'],role='T0',token_role_premises=[]))
        values={k:getattr(typed,k) for k in e['binding']}
        roles=[]
        for field,expected,pid,meaning in [
            ('quantity','expected_quantity_kind','ROLE-temperature','temperature'),
            ('observation_role','expected_observation_role','ROLE-measured','measured_actual'),
            ('unit','expected_unit','ROLE-unit','degree_celsius')]:
            if e['token_roles'][field]!=e['binding'][expected]:fail('EVIDENCE_JOIN_MISMATCH','token_roles','phase_4')
            roles.append(SimpleNamespace(premise_id=pid,availability='present',value={
                'profile_role':meaning,'public_token':e['token_roles'][field]}))
        binding=SimpleNamespace(**values,token_role_premises=roles)
        adapter=SimpleNamespace(current_condition_question=question,observed_input_binding=binding)
        if (context['as_of']!=e['question']['as_of'] or context['assertion_context']!=e['question']['assertion_context'] or
            context['variable_anchor_id']!=binding.variable_anchor_id or context['subject_entity_anchor_id']!=binding.subject_entity_anchor_id):
            fail('EVIDENCE_JOIN_MISMATCH','context','phase_4')
        _assess_current_condition(adapter,snapshot)
        observed=_admit_observed_value(adapter,snapshot)
        candidate=snapshot.constraint_evaluations[binding.constraint_evaluation_index].candidates[binding.semantic_candidate_index]
    except (ValidationError,WorkflowInputError,IndexError,KeyError,AttributeError):
        fail('EVIDENCE_JOIN_MISMATCH','evidence.binding','phase_4')
    return observed,candidate.verdict


def compute(graph):
    g=graph;w=g.work;iv=g.invocation;q=g.get(iv['request'])
    evidence={}
    # All required requests undergo public reconstruction, never historical scoring.
    for qk in g.requests:
        old=g.values[qk];evidence[qk]=public_evidence(g.get(old['evidence']),old['context'],w)
    observed,verdict=evidence[key(iv['request'])]
    scalar=None if observed.canonical_decimal is None else Fraction(observed.canonical_decimal)
    a=g.get(iv['selection']);d=g.get(a['declaration'])
    reasons=[]
    def reason(phase,code,**kwargs):
        r={'phase':phase,'code':code,**kwargs};reasons.append(r);return r
    if d['scope_state']=='false':reason(5,'declaration_scope_false',declaration=a['declaration'])
    if iv['request'] not in d['requests']:reason(5,'request_not_member',request=iv['request'])
    permission='denied' if reasons else 'unknown' if d['scope_state']=='unknown' else 'permitted'
    if permission=='unknown':reason(5,'declaration_scope_unknown',declaration=a['declaration'])
    def identity_map(rs):return [{'id':g.get(r)['id'],'revision':g.get(r)['revision'],'reference':r} for r in rs]
    lower=[] if observed.status=='admitted' else [{'code':observed.unavailable_reason,'path':'/snapshot/constraint_evaluations/'+str(g.get(q['evidence'])['binding']['constraint_evaluation_index'])+'/candidates/'+str(g.get(q['evidence'])['binding']['semantic_candidate_index'])}]
    result={'schema':'nm.result.v1','profile':PROFILE,'invocation':g.root,
        'authority':dict(assessment_state='assessed',selection=iv['selection'],declaration=a['declaration'],adoption=iv['adoption'],request=iv['request'],policy=q['policy'],permission_state=permission,evaluation_permitted=permission=='permitted'),
        'evidence':dict(assessment_state='assessed',reference=q['evidence'],availability=observed.status,observed=None if scalar is None else ratio(scalar),cn_verdict=verdict,lower_reasons=lower),
        'procedure_assessments':dict(assessment_state='assessed',procedure_identity_map=identity_map(q['measurements']),rows=[]),
        'hypothesis_assessments':dict(assessment_state='assessed',hypothesis_identity_map=identity_map(q['hypotheses']),viable=None,rows=[]),
        'cells':dict(assessment_state='assessed',rows=[]),
        'ranking':dict(assessment_state='assessed',disposition=None,reasons=reasons,scores=None,best=None,recommendation=None,branches=None,equivalence=None),
        'review':dict(assessment_state='assessed',comparison='not_requested',groups=['evidence','hypotheses','procedures','decoders','support','authority','ranking_policy'])}
    phases=[{'phase':i,'state':'assessed'} for i in range(1,9)]
    def blocked(disposition,state,sections,phase_numbers):
        result['ranking']['disposition']=disposition
        for s in sections:result[s]['assessment_state']='not_assessed_'+state
        for i in phase_numbers:phases[i-1]['state']='not_assessed_'+state
    if permission!='permitted':
        blocked('evaluation_denied' if permission=='denied' else 'evaluation_permission_unknown','gate_blocked',
                ['procedure_assessments','hypothesis_assessments','cells','ranking'],[6,7])
    elif scalar is None:
        for r in lower:reason(6,r['code'],path=r['path'])
        blocked('baseline_unavailable','baseline_unavailable',['procedure_assessments','hypothesis_assessments','cells','ranking'],[6,7])
    else:
        states=[]
        for pr in q['measurements']:
            p=g.get(pr);rows=[]
            for c in p['conditions']:
                w.charge('condition_assessments')
                numeric=c['kind']=='baseline_le'
                state=('true' if scalar<=rational(c['threshold'],w) else 'false') if numeric else c['state']
                states.append(state)
                rows.append(dict(id=c['id'],state=state,basis=[] if numeric else c['basis'],observed=ratio(scalar) if numeric else None,threshold=c['threshold'] if numeric else None))
                if state!='true':reason(6,'procedure_condition_'+state,procedure=pr,condition=c['id'])
            result['procedure_assessments']['rows'].append(dict(procedure=pr,conditions=rows))
        viable=[]
        for hr in q['hypotheses']:
            h=g.get(hr);checks=[]
            for c in h['requirements']:
                w.charge('hypothesis_checks')
                actual=ratio(scalar) if c['kind']=='baseline_decimal_equals' else verdict
                status='satisfied' if actual==c['expected'] else 'contradicted'
                checks.append(dict(id=c['id'],expected=c['expected'],actual=actual,status=status))
            if all(c['status']=='satisfied' for c in checks):viable.append(h['id'])
            result['hypothesis_assessments']['rows'].append(dict(hypothesis=hr,checks=checks))
        result['hypothesis_assessments']['viable']=viable
        if any(s!='true' for s in states):
            disposition='withheld_due_to_inapplicable_candidate' if 'false' in states else 'withheld_due_to_unknown_applicability'
            blocked(disposition,'applicability_blocked',['cells','ranking'],[7])
        else:
            cells={};conflict=False;missing=False
            for hr in q['hypotheses']:
                for pr in q['measurements']:
                    p=g.get(pr);o=g.get(p['decoder']);outcomes=[x['id'] for x in o['outcomes']]
                    sr=[r for r in q['support'] if g.get(r)['hypothesis']==hr and g.get(r)['procedure']==pr]
                    rows=[g.get(r) for r in sr]
                    w.charge('source_contributions',len(rows)*len(outcomes));w.charge('mapped_cells',len(outcomes))
                    mapped=qualify_supplied_support(rows,hypothesis=hr,procedure=pr,decoder=p['decoder'],evidence=q['evidence'],context=q['context'],outcomes=outcomes)
                    relations=[]
                    for cell in mapped:
                        relation={'supports':'permits','excludes':'excludes'}.get(cell.relation,'unknown')
                        cr=[]
                        if relation=='unknown':
                            has_conflict='support_conflict' in cell.reasons
                            conflict|=has_conflict;missing|=not has_conflict or 'support_unavailable' in cell.reasons
                            for code in cell.reasons:cr.append(reason(7,code,hypothesis=hr,procedure=pr,outcome=cell.outcome,sources=sr))
                        cells[(key(hr),key(pr),cell.outcome)]=relation;relations.append(relation)
                        result['cells']['rows'].append(dict(hypothesis=hr,procedure=pr,decoder=p['decoder'],outcome=cell.outcome,relation=relation,reasons=cr,source_refs=sr))
                    if relations and set(relations)=={'excludes'}:fail('ROW_ALL_EXCLUDED','support','phase_7')
            if conflict or missing:
                blocked('withheld_due_to_conflicting_predictions' if conflict else 'withheld_due_to_incomplete_predictions','prediction_support_blocked',['ranking'],[])
            elif len(viable)<2:
                result['ranking']['disposition']='no_viable_hypotheses' if not viable else 'no_discrimination_needed'
            else:
                candidates=[]
                for pr in q['measurements']:
                    p=g.get(pr);branches=[]
                    for o in g.get(p['decoder'])['outcomes']:
                        branches.append(dict(outcome=o['id'],state='qualified',survivors=[g.get(hr)['id'] for hr in q['hypotheses'] if g.get(hr)['id'] in viable and cells[(key(hr),key(pr),o['id'])]=='permits']))
                    candidates.append(dict(id=p['id'],status='complete',branches=branches))
                w.charge('ranking_branches',sum(len(c['branches']) for c in candidates))
                ranked=rank_measurements(viable,candidates)
                mapping={g.get(pr)['id']:pr for pr in q['measurements']}
                scores=[dict(procedure=mapping[s.measurement_id],worst=s.worst_survivors,reduction=s.reduction) for s in ranked.scores]
                reduction=max(s['reduction'] for s in scores)
                disposition='no_discriminating_measurement' if reduction==0 else 'tied_best_within_supplied_set' if len(ranked.best)>1 else 'preferred_within_supplied_set'
                result['ranking'].update(disposition=disposition,scores=scores,best=[mapping[i] for i in ranked.best],recommendation=mapping[ranked.best[0]] if disposition=='preferred_within_supplied_set' else None,
                    branches=[dict(procedure=mapping[c['id']],outcomes=[{'outcome':b['outcome'],'survivors':b['survivors']} for b in c['branches']]) for c in candidates],
                    equivalence=[dict(procedure=mapping[s.measurement_id],survivor_multiset=s.survivor_multiset) for s in ranked.scores])
    trace=dict(schema='nm.trace.v1',profile=PROFILE,invocation=g.root,origin='observed_execution',physical_observed=True,semantic_origin='synthetic_conditional',
               required_closure=[ref(*k) for k in sorted(g.objects)],reference_occurrences=g.occurrences,phases=phases)
    result['accounting']=dict(assessment_state='assessed',logical_required=dict(w.logical),physical='not_part_of_semantic_result')
    return result,trace
