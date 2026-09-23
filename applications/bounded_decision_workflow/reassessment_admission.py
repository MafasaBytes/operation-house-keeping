"""Slice 2: owning public admission and frozen baseline, never outcome inference.

Inputs are the captured typed graph. No supplied expected outputs or computation
callbacks participate. Historical contexts receive joins and declaration checks,
not renewed baseline eligibility or support adjudication.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from fractions import Fraction

from .measurement_compute import public_evidence, ratio
from .measurement_contracts import MeasurementContractError
from .measurement_wire import key, ref, rational, fail


LIMITATION = ('Content and declared dependency relationships verified; chronology '
               'is locally declared and unverified. No independent pre-exposure '
               'custody or predictive-validation claim.')


@dataclass(frozen=True, slots=True)
class Admission:
    """Internal stage record; not an nr.result or an adopted interpretation."""
    request: dict
    permission: str
    disposition: str
    observation: dict
    envelope: dict | None
    exposure: dict
    hypotheses: tuple
    conditions: tuple
    reasons: tuple


def _time(s):
    return None if s is None else datetime.fromisoformat(s[:-1]+'Z' if s.endswith('z') else s)


def _decimal(value, work):
    """Reserve decimal expansion before powers/integers; no binary rounding."""
    if value is None:
        return None
    t = Decimal(value).as_tuple()
    digits = ''.join(map(str, t.digits)).lstrip('0')
    if not digits:
        return Fraction(0)
    exponent = t.exponent
    while digits.endswith('0'):
        digits = digits[:-1]
        exponent += 1
    n = len(digits) + max(0, exponent)
    # Strip powers of two/five textually before allocating a denominator. This
    # also admits reduced fractions at the boundary without constructing 10**N.
    def divide(s, by):
        out = []; carry = 0
        for ch in s:
            q, carry = divmod(carry * 10 + int(ch), by)
            if out or q: out.append(str(q))
        return ''.join(out) or '0', carry
    a = b = max(0, -exponent)
    if exponent < 0:
        for prime in (2, 5):
            count = a if prime == 2 else b
            while count:
                reduced, remainder = divide(digits, prime)
                if remainder: break
                work.charge('rational_operations')
                digits = reduced; count -= 1
            if prime == 2: a = count
            else: b = count
        n = len(digits)
    limit = work.limits['integer_digits']
    def overflow(attempted):
        fail('RESOURCE_LIMIT_EXCEEDED', '/observation/scalar', 'phase_3',
             dimension='integer_digits', attempted=attempted, limit=limit)
    if n > limit: overflow(n)
    denominator = 1
    ceiling = 10 ** limit - 1
    for prime, count in ((2, a), (5, b)):
        # At most a bounded number of iterations can pass the next check.
        for _ in range(count):
            work.charge('rational_operations')
            if denominator > ceiling // prime: overflow(limit + 1)
            denominator *= prime
    numerator = int(digits) * (10 ** max(0, exponent))
    work.high('integer_digits', max(n, len(str(denominator))))
    work.charge('rational_operations')
    return Fraction(-numerator if t.sign else numerator, denominator)


def _reason(code, path, references):
    return dict(code=code, path=path, references=sorted(references, key=key))


def _get(g, reference):
    """A contextual reference use is work even on already captured material."""
    g.work.charge('reference_occurrences')
    g.work.charge('edge_visits')
    g.work.charge('context_scan_bytes', len(g.objects[key(reference)]))
    return g.get(reference)


def _public(g, e_ref, context, request):
    e = _get(g,e_ref); w = g.work
    try:
        observed, verdict = public_evidence(e, context, w, reconstruction_work=w)
    except MeasurementContractError as exc:
        if exc.code == 'RESOURCE_LIMIT_EXCEEDED': raise
        fail(exc.code, exc.target, 'phase_3', request=request, references=[e_ref])
    # This path is read only after the owning model/binding validator succeeds.
    received = None
    if observed.status == 'admitted':
        b = e['binding']
        occurrence = e['snapshot']['constraint_evaluations'][b['constraint_evaluation_index']][
            'semantic_compatibility']['candidates'][b['semantic_candidate_index']][
            'value_candidate']['state_candidate']['bound']['observed']['occurrence']
        received = occurrence['received_at']
    try:
        scalar = _decimal(observed.canonical_decimal, w)
    except MeasurementContractError as exc:
        exc.details.setdefault('request', request)
        raise
    return dict(availability=observed.status, scalar=None if scalar is None else ratio(scalar),
        occurrence_id=observed.occurrence_id, raw_record_id=observed.raw_record_id,
        payload_checksum=observed.payload_checksum, unit=e['binding']['expected_unit'],
        received_at=received, as_of=e['question']['as_of'],
        reasons=[] if observed.unavailable_reason is None else [_reason(
            observed.unavailable_reason, '/snapshot/constraint_evaluations/'+str(e['binding']['constraint_evaluation_index'])+
            '/candidates/'+str(e['binding']['semantic_candidate_index'])+'/not_evaluated_reason', [e_ref])]), scalar, verdict


def _joins(g, qr):
    q=_get(g,qr); original=_get(g,q['original_invocation']); oq=_get(g,original['request'])
    p=_get(g,q['procedure']); decoder=_get(g,q['decoder']); o=_get(g,q['observation'])
    execution=_get(g,q['execution']); exposure=_get(g,q['exposure']); e=_get(g,o['evidence'])
    problems=[]
    def check(ok, path, code='OBSERVATION_JOIN_MISMATCH'):
        if not ok: problems.append((code, path))
    check(q['original_selection_pin']==original['selection']['sha256'], '/original_selection_pin', 'ORIGINAL_SELECTION_PIN_MISMATCH')
    check(q['procedure'] in oq['measurements'], '/procedure')
    check(q['decoder']==p['decoder'], '/decoder')
    check(p['context']==oq['context'] and p['evidence']==oq['evidence'], '/procedure/context')
    check(p['method']=='reference_scalar' and decoder['domain']==dict(kind='scalar_finite_decimal',unit='degree_celsius',values=None), '/procedure', 'RESULT_DOMAIN_UNSUPPORTED')
    check(o['procedure']==q['procedure'], '/observation/procedure')
    check(o['decoder']==q['decoder'], '/observation/decoder')
    check(execution['observation']==q['observation'], '/execution/observation')
    check(exposure['observation']==q['observation'], '/exposure/observation')
    check(exposure['original_invocation']==q['original_invocation'], '/exposure/original_invocation')
    check(execution['original_context']==oq['context'], '/execution/original_context')
    check(all(execution['result_context'][f]==oq['context'][f] for f in oq['context'] if f!='as_of'), '/execution/result_context')
    check(q['interpretation']['unit']==e['binding']['expected_unit']==e['token_roles']['unit'], '/interpretation/unit')
    if exposure['prior_bundle'] is not None:
        check(_get(g,exposure['prior_bundle'])['closure']['invocation']==q['original_invocation'], '/exposure/prior_bundle')
    if problems:
        code,path=min(problems)
        fail(code,path,'phase_3',request=qr)
    return q, original, oq, execution, exposure, o


def _declarations(g, qr, data):
    q, original, oq, execution, exposure, o, observation, scalar, verdict = data
    w=g.work; problems=[]; u=q['interpretation']; envelope=None
    if u['kind']=='hard_interval':
        lo=rational(u['lo'],w);hi=rational(u['hi'],w)
        w.charge('containment_comparisons');w.charge('rational_operations')
        inconsistent=lo>hi
        if scalar is not None:
            w.charge('containment_comparisons',2);w.charge('rational_operations',2)
            inconsistent |= not lo<=scalar<=hi
        if inconsistent:problems.append(('OBSERVATION_UNCERTAINTY_INCONSISTENT','/interpretation'))
        if scalar is not None:envelope=dict(lo=u['lo'],hi=u['hi'],lower_closed=True,upper_closed=True,basis_kind='hard_interval',basis=u['basis'])
    elif u['kind']=='declared_point' and scalar is not None:
        envelope=dict(lo=ratio(scalar),hi=ratio(scalar),lower_closed=True,upper_closed=True,basis_kind='declared_point_assumption',basis=u['basis'])
    acq=execution['acquisition'];start=_time(acq['start']);end=_time(acq['end'])
    if acq['state']=='known':
        invalid=start is None or end is None or not acq['basis']
        if not invalid: invalid=start>end or (observation['received_at'] is not None and end>_time(observation['received_at']))
    else:invalid=start is not None or end is not None
    if invalid:problems.append(('ACQUISITION_DECLARATION_INCONSISTENT','/execution/acquisition'))
    before=_time(exposure['declared_prediction_commitment_at']);learned=_time(exposure['declared_first_learned_at'])
    relation=exposure['declared_relation']
    if before is not None and learned is not None and relation!='unknown':
        if (before<learned)!=(relation=='predictions_before_learning_result'):
            problems.append(('EXPOSURE_DECLARATION_INCONSISTENT','/exposure'))
    if problems:
        code,path=min(problems);fail(code,path,'phase_4',request=qr)
    return envelope


def admit(g):
    """Validate all captured contexts, then gate only the current assessment.

    This internal composition entry consumes Slice 1 capture; it is not a new
    command or a public substitute for executable/capture validation.
    """
    w=g.work; current=g.invocation['request']; public={}; data={}; errors=[]
    def attempt(fn):
        try:return fn()
        except MeasurementContractError as exc:
            if exc.code=='RESOURCE_LIMIT_EXCEEDED':raise
            errors.append(exc)
    def finish():
        if errors:
            raise min(errors,key=lambda e:(e.code,e.target,str(e.details.get('request'))))
    # Reconstruct every owning original request, including declaration members.
    for k in sorted(g.values):
        if k[0]=='nm.request.v1':
            q=g.values[k]
            public[k]=attempt(lambda q=q,k=k:_public(g,q['evidence'],q['context'],ref(*k)))
    for k in sorted(g.values):
        if k[0]!='nr.request.v2':continue
        qr=ref(*k); joined=attempt(lambda qr=qr:_joins(g,qr))
        if joined is None:continue
        q,original,oq,execution,exposure,o=joined
        observed=attempt(lambda o=o,execution=execution,qr=qr:_public(g,o['evidence'],execution['result_context'],qr))
        if observed is not None:data[k]=(*joined,*observed)
    finish()
    envelopes={}
    for k in sorted(data):envelopes[k]=attempt(lambda k=k:_declarations(g,ref(*k),data[k]))
    finish()
    q,original,oq,execution,exposure,o,observation,scalar,verdict=data[key(current)]
    observation=dict(reference=q['observation'],evidence=o['evidence'],**observation)
    exposure_result=dict(reference=q['exposure'],content_relationship='original_closure_verified' if exposure['prior_bundle'] is None else 'prior_bundle_integrity_and_reference_verified',
        chronology={'unknown':'exposure_unknown','predictions_before_learning_result':'declared_pre_exposure_unverified','predictions_after_learning_result':'declared_retrospective'}[exposure['declared_relation']],
        declared_prediction_commitment_at=exposure['declared_prediction_commitment_at'],
        declared_first_learned_at=exposure['declared_first_learned_at'],limitation=LIMITATION)
    permission=_get(g,g.invocation['authority'])['permission']; reasons=[]; conditions=[]
    hypotheses=[dict(reference=h,baseline='not_assessed',baseline_checks=None) for h in oq['hypotheses']]
    def done(disposition):
        return Admission(current,permission,disposition,observation,envelopes[key(current)],exposure_result,tuple(hypotheses),tuple(conditions),tuple(reasons))
    if permission!='true':
        disposition='evaluation_denied' if permission=='false' else 'evaluation_permission_unknown'
        reasons.append(_reason(disposition,'/authority/permission',[g.invocation['authority']]))
        return done(disposition)
    baseline,bs,bv=public[key(original['request'])]
    if bs is None:
        for h in hypotheses:h['baseline']='baseline_unknown'
        reasons.extend(baseline['reasons'])
        return done('baseline_unavailable')
    for row in hypotheses:
        checks=[]
        for check in _get(g,row['reference'])['requirements']:
            w.charge('baseline_checks');w.charge('hypothesis_checks')
            actual=ratio(bs) if check['kind']=='baseline_decimal_equals' else bv
            checks.append(dict(id=check['id'],expected=check['expected'],actual=actual,status='satisfied' if actual==check['expected'] else 'contradicted'))
        row.update(baseline_checks=checks,baseline='baseline_eligible' if all(c['status']=='satisfied' for c in checks) else 'baseline_ineligible')
    if not any(h['baseline']=='baseline_eligible' for h in hypotheses):return done('no_baseline_eligible_hypotheses')
    states=[]
    for source,rows in ((q['procedure'],_get(g,q['procedure'])['conditions']),(q['execution'],execution['conditions'])):
        for c in rows:
            w.charge('condition_assessments')
            numeric=c.get('kind')=='baseline_le'
            if numeric:w.charge('rational_operations')
            state=('true' if bs<=rational(c['threshold'],w) else 'false') if numeric else c['state']
            states.append(state)
            conditions.append(dict(reference=source,id=c['id'],state=state,basis=[] if numeric else c['basis'],observed=ratio(bs) if numeric else None,threshold=c['threshold'] if numeric else None))
            if state!='true':reasons.append(_reason('condition_'+state,'/conditions/'+c['id'],[source]))
    if scalar is None:reasons.extend(observation['reasons'])
    if execution['acquisition']['state']=='unknown':reasons.append(_reason('acquisition_unknown','/execution/acquisition',[q['execution']]))
    if q['interpretation']['kind'] in ('unknown','confidence_only'):reasons.append(_reason('uncertainty_'+q['interpretation']['kind'],'/interpretation',[current]))
    order={name:i for i,name in enumerate(('applicability','availability','calibration','fidelity','hold'))}
    reasons.sort(key=lambda r:(order.get(r['path'].rsplit('/',1)[-1],5),r['code'],r['path'],[key(x) for x in r['references']]))
    if 'false' in states:return done('withheld_due_to_inapplicable_execution')
    if 'unknown' in states or execution['acquisition']['state']=='unknown':return done('withheld_due_to_unknown_execution')
    if scalar is None:return done('observation_unavailable')
    if envelopes[key(current)] is None:return done('withheld_due_to_unknown_uncertainty')
    return done('ready_for_interpretation')
