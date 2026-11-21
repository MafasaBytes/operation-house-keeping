"""Checked-temperature runtime: closure, stages 1-7, bundles, verify and replay.

In-process API (bytes in, bundle file bytes out); `checked_cli` owns paths.
The executable build identity is supplied by a provider. The maintained
provider (`ExecutableBuild`) refuses when the tree is not a clean committed
executable; nothing here fabricates a clean build.
"""
import base64
from datetime import datetime, timezone
from fractions import Fraction
import json

from .checked_contracts import (
    CALCULATOR, CATALOGUE, EDITION_LIMITS, KINDS, LEGACY_EVIDENCE_KIND, OPAQUE_KIND, POLICY_EDITION,
    POLICY_EDITION_SHA256, PROFILE, SCHEMAS, SCHEMAS_SHA256, T1, T2, B_REF_BOUND, H2_MAX, HALF_WIDTH_MAX,
    CheckedRefusal, Ops, canonical_bytes, decimal, enforce_roles, frac, instant, interval, parse_canonical,
    ref, refuse, scan, sha, validate, window)
from . import checked_applicability, checked_derivation, checked_reassessment, checked_selection

CLOSURE_KINDS = tuple(SCHEMAS['records']['ct.closure.v1']['properties']['members']['items']
                      ['properties']['kind']['enum'])
SELECTION_KINDS = CLOSURE_KINDS[:12]
AUTHORED = {k for k, r in SCHEMAS['records'].items() if r.get('x-class') == 'authored'}
FILE_ROLES = (('invocation.json', 'ct.invocation.v1'), ('closure.json', 'ct.closure.v1'),
              ('derivation.json', 'ct.derivation.v1'), ('applicability.json', 'ct.applicability.v1'),
              ('result.json', None), ('trace.json', 'ct.trace.v1'), ('build.json', 'ct.build.v1'),
              ('policy.json', 'ct.policy.v1'))
FILE_CAPS = {'invocation.json': 'invocation_bytes', 'derivation.json': 'derivation_bytes',
             'applicability.json': 'applicability_bytes', 'result.json': 'result_bytes',
             'trace.json': 'trace_bytes', 'build.json': 'build_bytes', 'policy.json': 'policy_bytes',
             'manifest.json': 'manifest_bytes'}
BUNDLE_NAMES = tuple(n for n, _ in FILE_ROLES) + ('manifest.json',)


# ------------------------------------------------------------------ build

class ExecutableBuild:
    """Maintained executable identity: clean committed tree and exact lock.

    Refuses BUILD_IDENTITY_UNAVAILABLE (CONTRACT §12.2) when the maintained
    measurement identity is unavailable, for example when
    applications/ or backend/ has uncommitted or untracked files.
    """

    def wire(self):
        from . import measurement_build
        from .errors import WorkflowInputError
        from .measurement_contracts import MeasurementContractError
        try:
            nm = json.loads(measurement_build.identity())
        except (WorkflowInputError, MeasurementContractError, OSError, ValueError, ImportError,
                __import__('subprocess').SubprocessError):
            refuse('BUILD_IDENTITY_UNAVAILABLE', 5, '/build/current')
        return canonical_bytes({
            'schema': 'ct.build.v1', 'profile': PROFILE, 'checkpoint': nm['checkpoint'],
            'clean_application_backend': True, 'source_manifest': nm['source_manifest'],
            'environment_manifest': nm['environment_manifest'],
            'contract_editions': {'schemas_sha256': SCHEMAS_SHA256, 'policy_edition_sha256': POLICY_EDITION_SHA256,
                                  'catalogue': CATALOGUE, 'calculator': CALCULATOR}})


def _current_build(provider):
    wire = provider.wire()
    value = parse_canonical(wire, EDITION_LIMITS, cap_name='build_bytes', target='/build')
    validate(value, 'ct.build.v1')
    return wire


# ---------------------------------------------------------------- closure

class Records:
    """Resolved closure: digest -> (kind, value-or-bytes)."""

    def __init__(self):
        self.by_digest = {}
        self.annotations = []   # (source digest, path, ref) non-edge references

    def get(self, r):
        kind, value = self.by_digest[r['sha256']]
        return value

    def kind(self, digest):
        return self.by_digest[digest][0]


def load_member(digest, data, kind_hint, limits, target):
    if sha(data) != digest:
        refuse('REFERENCE_DIGEST_MISMATCH', 3, target)
    if kind_hint == OPAQUE_KIND:
        if len(data) > limits['object_bytes']:
            refuse('RESOURCE_LIMIT_EXCEEDED', 1, target)
        return OPAQUE_KIND, data, None
    value = parse_canonical(data, limits, target=target)
    kind = value.get('schema') if isinstance(value, dict) else None
    if kind == LEGACY_EVIDENCE_KIND:
        return kind, value, None
    if kind == 'ct.policy.v1' and value.get('edition') != POLICY_EDITION:
        refuse('POLICY_EDITION_MISMATCH', 4, target + '/edition')
    found = validate(value, kind if kind in SCHEMAS['records'] else '')
    return kind, value, found


def resolve(roots, pool, limits, member_kinds, unique_cap, *, target='/closure'):
    """Stages 1-3 over the reachable set; member set must equal reachable set."""
    records = Records()
    queue = list(roots)
    while queue:
        r = queue.pop(0)
        d = r['sha256']
        if d in records.by_digest:
            if records.kind(d) != r['kind']:
                refuse('REFERENCE_KIND_MISMATCH', 3, f'{target}/{d}')
            continue
        if r['kind'] not in member_kinds:
            refuse('REFERENCE_KIND_MISMATCH', 3, f'{target}/{d}')
        if d not in pool:
            refuse('REFERENCE_MISSING', 3, f'{target}/{d}')
        kind, value, found = load_member(d, pool[d], r['kind'], limits, f'{target}/{d}')
        if kind != r['kind']:
            refuse('REFERENCE_KIND_MISMATCH', 3, f'{target}/{d}')
        records.by_digest[d] = (kind, value)
        if len(records.by_digest) > unique_cap:
            refuse('RESOURCE_LIMIT_EXCEEDED', 3, f'{target}/unique_objects')
        if found is None:
            continue
        enforce_roles(found, f'{target}/{d}')
        for path, rr, allowed, edge in sorted(found.refs, key=lambda x: x[0]):
            if rr['kind'] not in allowed:
                refuse('REFERENCE_KIND_MISMATCH', 3, f'{target}/{d}{path}')
            if edge:
                queue.append(rr)
            else:
                records.annotations.append((d, path, rr))
    extra = sorted(set(pool) - set(records.by_digest))
    if extra:
        refuse('UNREFERENCED_MEMBER', 3, f'{target}/{extra[0]}')
    identities = set()
    for d, (kind, value) in sorted(records.by_digest.items()):
        if kind not in AUTHORED:
            continue
        key = (kind, value['id'], value['revision'])
        if key in identities:
            refuse('SCHEMA_INVALID', 3, f'{target}/{d}/identity_duplicate')
        identities.add(key)
        pred = value['predecessor']
        if (value['revision'] == 1) != (pred is None):
            refuse('PREDECESSOR_INVALID', 3, f'{target}/{d}/predecessor')
        if pred is not None:
            p = records.get(pred)
            if p['schema'] != kind or p['id'] != value['id'] or p['revision'] != value['revision'] - 1:
                refuse('PREDECESSOR_INVALID', 3, f'{target}/{d}/predecessor')
    return records


def closure_record(roots, records):
    members = []
    for d, (kind, value) in records.by_digest.items():
        data = value if kind == OPAQUE_KIND else canonical_bytes(value)
        members.append({'kind': kind, 'sha256': d, 'decoded_bytes': len(data), 'encoding': 'base64',
                        'data': base64.b64encode(data).decode('ascii')})
    members.sort(key=lambda m: (m['kind'], m['sha256']))
    return {'schema': 'ct.closure.v1', 'profile': PROFILE, 'roots': roots, 'members': members}


def closure_pool(closure, limits, target='/closure.json'):
    pool = {}
    for m in closure['members']:
        try:
            data = base64.b64decode(m['data'].encode('ascii'), validate=True)
        except ValueError:
            refuse('SCHEMA_INVALID', 1, target)
        if len(data) != m['decoded_bytes'] or base64.b64encode(data).decode('ascii') != m['data']:
            refuse('SCHEMA_INVALID', 1, target)
        if sha(data) != m['sha256']:
            refuse('REFERENCE_DIGEST_MISMATCH', 3, target + '/' + m['sha256'])
        pool[m['sha256']] = data
    order = [(m['kind'], m['sha256']) for m in closure['members']]
    if order != sorted(set(order)) or len(pool) != len(order):
        refuse('SCHEMA_INVALID', 2, target + '/members')
    return pool, {m['sha256']: m['kind'] for m in closure['members']}


# ------------------------------------------------------------- admission

class Admitted:
    pass


def _baseline_observation(evidence, context):
    """Legacy public-evidence reconstruction (owning validator semantics)."""
    from .measurement_compute import public_evidence
    from .measurement_contracts import MeasurementContractError
    from .measurement_wire import Work
    try:
        observed, verdict = public_evidence(evidence, context, Work())
    except (MeasurementContractError, KeyError, TypeError, AttributeError, ValueError, IndexError):
        # Malformed legacy evidence is a structural refusal, never an internal error.
        refuse('SCHEMA_INVALID', 4, '/nm.evidence.v1')
    scalar = None if observed.status != 'admitted' or observed.canonical_decimal is None \
        else Fraction(observed.canonical_decimal)
    return scalar, verdict if verdict in ('violated', 'satisfied') else None, observed


def _plan(records, plan_ref, target):
    if plan_ref is None:
        return None
    plan = records.get(plan_ref)
    w = frac(plan['half_width'], target + '/half_width')
    if w == 0:
        refuse('INTERPRETATION_POINT_UNSUPPORTED', 4, target + '/half_width')
    if not 0 < w <= HALF_WIDTH_MAX:
        refuse('INTERPRETATION_HALF_WIDTH_OUT_OF_RANGE', 4, target + '/half_width')
    return plan


def _captured_counts(records, limits):
    """Review v4 I-1: captured count and format limits (CONTRACT §12.9)."""
    def over(name, target):
        refuse('RESOURCE_LIMIT_EXCEEDED', 4, '/captured_limits/' + name + target)
    fd = 10 ** limits['fractional_digits']
    for d, (kind, value) in sorted(records.by_digest.items()):
        if kind in AUTHORED and value['revision'] > limits['successor_chain']:
            over('successor_chain', '/' + d)
        if kind == 'ct.model.v1':
            if len(value['hypotheses']) > limits['hypotheses']:
                over('hypotheses', '/' + d)
            if len(value['procedures']) > limits['procedures']:
                over('procedures', '/' + d)
            for p in value['procedures']:
                if (3 if p['edition'] == T1 else 2) > limits['outcomes_per_procedure']:
                    over('outcomes_per_procedure', '/' + d)
        if kind in (OPAQUE_KIND, LEGACY_EVIDENCE_KIND):
            continue
        stack = [value]
        while stack:
            v = stack.pop()
            if isinstance(v, dict):
                if set(v) == {'numerator', 'denominator'} and isinstance(v['denominator'], str) and \
                        v['denominator'].isdigit() and 10 ** 6 % int(v['denominator']) == 0 and \
                        fd % int(v['denominator']) != 0:
                    # Edition-invalid denominators stay RATIONAL_INVALID (F5b); only the captured
                    # tightening of an edition-valid rational is a resource refusal.
                    over('fractional_digits', '/' + d)
                stack.extend(v.values())
            elif isinstance(v, list):
                stack.extend(v)
        if kind == 'ct.request.v1' and value['purpose'] == 'reassessment':
            obs = value['result']['observation']
            if obs['kind'] == 'scalar' and '.' in obs['scalar'] and \
                    len(obs['scalar'].split('.')[1]) > limits['fractional_digits']:
                over('fractional_digits', '/' + d)
        if kind == 'ct.retained-selection.v1' and \
                len(canonical_bytes(value)) > limits['retained_selection_bytes']:
            over('retained_selection_bytes', '/' + d)


def admit(records, request_ref, limits_cap):
    """Stage 4 profile semantics shared by selection and reassessment."""
    a = Admitted()
    a.records = records
    a.request_ref = request_ref
    a.request = records.get(request_ref)
    a.policy_ref = a.request['policy']
    a.policy = records.get(a.policy_ref)
    for k, v in a.policy['limits'].items():
        if v > EDITION_LIMITS[k]:
            refuse('POLICY_LIMIT_INVALID', 4, '/policy/limits/' + k)
    a.limits = dict(a.policy['limits'])
    # CONTRACT §12.9: captured limits are enforced after policy discovery, in addition to
    # the edition ceilings already applied at stage 1.
    for d, (kind, value) in sorted(records.by_digest.items()):
        data = value if kind == OPAQUE_KIND else canonical_bytes(value)
        if len(data) > a.limits['object_bytes']:
            refuse('RESOURCE_LIMIT_EXCEEDED', 4, '/captured_limits/object_bytes/' + d)
        if kind != OPAQUE_KIND:
            try:
                scan(value, a.limits, '/captured_limits/' + d)
            except CheckedRefusal as e:
                refuse(e.code, 4, e.target)
    _captured_counts(records, a.limits)
    phase = a.request['purpose']
    if len(records.by_digest) > a.limits[phase + '_unique_objects']:   # captured cap may be tighter
        refuse('RESOURCE_LIMIT_EXCEEDED', 4, '/closure/unique_objects')
    a.model_ref = a.request['model']
    a.model = records.get(a.model_ref)
    m = a.model
    kinds = []
    for i, h in enumerate(m['hypotheses']):
        e = records.get(h['explanation'])
        lo, hi = interval(h['b_suspect'], f'/model/hypotheses/{i}/b_suspect')
        kinds.append(e['account_kind'])
        if e['account_kind'] == 'high_underlying_faithful_baseline' and (lo, hi) != (0, 0):
            refuse('ACCOUNT_KIND_CONSTRAINT_VIOLATED', 4, f'/model/hypotheses/{i}')
        if e['account_kind'] == 'low_underlying_positive_offset' and not (0 < lo <= hi <= H2_MAX):
            refuse('ACCOUNT_KIND_CONSTRAINT_VIOLATED', 4, f'/model/hypotheses/{i}')
    if len(set(kinds)) != len(kinds):
        refuse('ACCOUNT_KIND_CONSTRAINT_VIOLATED', 4, '/model/hypotheses')
    b_lo, b_hi = interval(m['b_ref'], '/model/b_ref')
    if b_lo < -B_REF_BOUND or b_hi > B_REF_BOUND:
        refuse('ACCOUNT_KIND_CONSTRAINT_VIOLATED', 4, '/model/b_ref')
    editions = [p['edition'] for p in m['procedures']]
    if len(set(editions)) != len(editions):
        refuse('SCHEMA_INVALID', 4, '/model/procedures')
    a.procedures = editions
    frac(m['baseline'], '/model/baseline')
    for p in m['procedures']:
        if p['edition'] == T2:
            frac(p['target'], '/model/procedures/target')
    a.model_plan_ref = next((p['interpretation_plan'] for p in m['procedures'] if p['edition'] == T1), None)
    a.model_plan = _plan(records, a.model_plan_ref, '/model/plan')
    supplied = {}
    for field, cap in (('claims', 'claims'), ('declarations', 'condition_declarations'),
                       ('evidence_items', 'evidence_items'), ('reviews', 'reviews')):
        refs = a.request[field]
        if len(refs) > a.limits[cap]:
            refuse('RESOURCE_LIMIT_EXCEEDED', 4, '/request/' + field)
        supplied[field] = [(r, records.get(r)) for r in refs]
    for r, d in supplied['declarations']:
        window(d['covers'], '/declarations/covers')
    for r, v in supplied['reviews']:
        window(v['covers'], '/reviews/covers')
        rel, relation, done = v['relevance'], v['relation'], v['completion']
        ok = ((done == 'incomplete' and rel == 'unresolved' and relation == 'unresolved') or
              (done == 'completed' and (
                  (rel == 'irrelevant' and relation == 'not_applicable') or
                  (rel == 'relevant' and relation in ('support', 'opposition', 'unresolved')) or
                  (rel == 'unresolved' and relation == 'unresolved'))))
        if not ok:
            refuse('SCHEMA_INVALID', 4, '/reviews/' + r['sha256'])
    for r, i in supplied['evidence_items']:
        if i['validity'] is not None:
            window(i['validity'], '/evidence_items/validity')
    # Review C1: a review whose item is not a supplied evidence item, or whose claim is not
    # among that item's claims, could otherwise drop out of aggregation as "unbound" while
    # binding a required claim. It is refused structurally (design §5: never pending/unbound).
    items = {r['sha256']: i for r, i in supplied['evidence_items']}
    for r, v in supplied['reviews']:
        item = items.get(v['item']['sha256'])
        if item is None or v['claim'] not in item['claims']:
            refuse('SCHEMA_INVALID', 4, '/reviews/%s/item_claim_binding' % r['sha256'])
    a.supplied = supplied
    a.scalar, a.verdict, a.baseline_admission = _baseline_observation(records.get(m['baseline_evidence']),
                                                                      m['context'])
    return a


# ---------------------------------------------------------- stage 5 helpers

def _authority(records, r, purpose, target):
    a = records.get(r)
    if a['purpose'] != purpose:
        refuse('AUTHORITY_SCOPE_MISMATCH', 5, target + '/purpose')
    return a


def _plan_digests(plan_change):
    if plan_change is None:
        return None
    return {'former_plan_sha256': plan_change['former_plan']['sha256'],
            'new_plan_sha256': plan_change['new_plan']['sha256']}


def _permitted_build(policy, build_wire, target):
    if sha(build_wire) not in policy['permitted_builds']:
        refuse('BUILD_NOT_PERMITTED', 5, target)


# ------------------------------------------------------------ computation

def _trace(entries):
    return {'schema': 'ct.trace.v1', 'profile': PROFILE,
            'entries': [{'step': s, 'target': t, 'outcome': o} for s, t, o in entries]}


def _cell_limit(derivation, limits):
    if len(derivation['cells']) > limits['derivation_cells']:   # review v4 I-1
        refuse('RESOURCE_LIMIT_EXCEEDED', 6, '/derivation_cells')


def _work_limit(ops, limits):
    if ops.count > limits['rational_operations']:   # CONTRACT §12.9 accounting
        refuse('RESOURCE_LIMIT_EXCEEDED', 6, '/rational_operations')


def _selection_records(records, a, request_ref, build_ref):
    ops = Ops()
    derivation = checked_derivation.derive(request_ref=request_ref, model_ref=a.model_ref, build_ref=build_ref,
                                           model=a.model, observed_scalar=a.scalar, observed_verdict=a.verdict,
                                           ops=ops)
    _work_limit(ops, a.limits)
    _cell_limit(derivation, a.limits)
    plans = {T1: (a.model_plan_ref, a.model_plan)} if a.model_plan_ref is not None else {}
    required = checked_applicability.required_claims(model_ref=a.model_ref, model=a.model, phase='selection',
                                                     procedures=a.procedures, plans=plans)
    scope = (instant(a.model['context']['as_of']), instant(a.request['as_of']))
    if scope[0] > scope[1]:
        refuse('SCHEMA_INVALID', 4, '/request/as_of')
    applicability = checked_applicability.assess(
        request_ref=request_ref, policy_ref=a.policy_ref, build_ref=build_ref, phase='selection', scope=scope,
        required=required, supplied=a.supplied, policy=a.policy, limits=a.limits)
    plan_claim = next((ref('ct.claim.v1', sha(canonical_bytes(c))) for c in required
                       if c['binding']['condition'] == 'observation_error_bound'), None)
    return derivation, applicability, plan_claim


def _selection_result(a, request_ref, build_ref, derivation, applicability, plan_claim):
    d_ref = ref('ct.derivation.v1', sha(canonical_bytes(derivation)))
    p_ref = ref('ct.applicability.v1', sha(canonical_bytes(applicability)))
    return checked_selection.select(
        request_ref=request_ref, derivation_ref=d_ref, applicability_ref=p_ref, build_ref=build_ref,
        model=a.model, derivation=derivation, applicability=applicability, plan_ref=a.model_plan_ref,
        plan=a.model_plan, plan_claim_ref=plan_claim)


def _reassessment_records(records, a, request_ref, build_ref, plan_ref, plan, ops):
    derivation = checked_derivation.derive(request_ref=request_ref, model_ref=a.model_ref, build_ref=build_ref,
                                           model=a.model, observed_scalar=a.scalar, observed_verdict=a.verdict,
                                           ops=ops)
    applicability = _reassessment_applicability(a, request_ref, build_ref, plan_ref, plan)
    return derivation, applicability


def _reassessment_applicability(a, request_ref, build_ref, plan_ref, plan):
    """Existing base aggregation, usable before companion hypothesis delegation."""
    edition = a.request['result']['procedure_edition']
    plans = {T1: (plan_ref, plan)} if plan_ref is not None else {}
    required = checked_applicability.required_claims(model_ref=a.model_ref, model=a.model, phase='reassessment',
                                                     procedures=[edition], plans=plans)
    scope = (instant(a.model['context']['as_of']), instant(a.request['result']['acquisition']['ended']))
    if scope[0] > scope[1]:
        refuse('SCHEMA_INVALID', 4, '/result/acquisition/ended')
    applicability = checked_applicability.assess(
        request_ref=request_ref, policy_ref=a.policy_ref, build_ref=build_ref, phase='reassessment',
        scope=scope, required=required, supplied=a.supplied, policy=a.policy, limits=a.limits)
    return applicability


# ---------------------------------------------------- reassessment checks

def _prior_p0(prior_selection, edition):
    if edition != T1:
        return None
    rows = prior_selection['observation_uncertainty_not_in_score']
    return rows[0]['plan'] if rows else None


def _reassessment_stage5(records, a, request_ref, evaluation_ref, descriptor_ref):
    """Stage 5 steps 3-7 for reassessment (step 4 prior material via the descriptor)."""
    R = a.request
    result = R['result']
    A = _authority(records, evaluation_ref, 'evaluation', '/evaluation_authority')
    if A['target'] != request_ref:
        refuse('AUTHORITY_TARGET_MISMATCH', 5, '/evaluation_authority/target')
    E = _authority(records, result['execution_authority'], 'execution', '/execution_authority')
    if E['target'] != R['execution_target']:
        refuse('AUTHORITY_TARGET_MISMATCH', 5, '/execution_authority/target')
    check_prior_material(records, R, descriptor_ref)
    prior_selection = records.get(R['prior_selection']['selection'])
    edition = result['procedure_edition']
    P0 = _prior_p0(prior_selection, edition)
    plan_ref = result['interpretation_plan']
    if R['selection_basis'] == 'inherited':
        if R['plan_change'] is not None or plan_ref != P0:
            refuse('INTERPRETATION_PLAN_MISMATCH', 5, '/result/interpretation_plan')
        former, executed = None, P0
    else:
        pc = R['plan_change']
        if pc is None or pc['former_plan'] != P0 or pc['new_plan'] == P0 or plan_ref != pc['new_plan']:
            refuse('PLAN_CHANGE_INVALID', 5, '/plan_change')
        former, executed = P0, pc['new_plan']
    X = records.get(R['execution_target'])
    obs = result['observation']
    if (X['model'] != R['model'] or X['selection_basis'] != R['selection_basis'] or
            X['prior_selection'] != R['prior_selection'] or X['plan_change'] != R['plan_change'] or
            X['procedure_edition'] != edition or X['interpretation_plan'] != plan_ref or
            X['instrument_id'] != result['acquisition']['instrument_id']):
        refuse('EXECUTION_TARGET_MISMATCH', 5, '/execution_target')
    if (edition == T1) != (X['interpretation_plan'] is not None):
        refuse('EXECUTION_TARGET_MISMATCH', 5, '/execution_target/interpretation_plan')
    plan = _plan(records, plan_ref, '/result/interpretation_plan')
    if plan is not None and plan['instrument_id'] != X['instrument_id']:
        refuse('EXECUTION_TARGET_MISMATCH', 5, '/execution_target/instrument_id')
    if (edition == T1) != (obs['kind'] == 'scalar') or edition not in a.procedures:
        refuse('SCHEMA_INVALID', 4, '/result/observation')
    started = instant(result['acquisition']['started'])
    ended = instant(result['acquisition']['ended'])
    if started > ended:
        refuse('SCHEMA_INVALID', 4, '/result/acquisition')
    if started < instant(a.model['context']['as_of']):   # amendment C1.1 rule 2
        refuse('SCHEMA_INVALID', 4, '/result/acquisition/started_before_baseline')
    scalar = decimal(obs['scalar'], '/result/observation/scalar') if obs['kind'] == 'scalar' else None
    _result_evidence(records, a, result, scalar, started, ended)
    digests = _plan_digests(R['plan_change'])
    if A['scope']['phase'] != 'reassessment' or edition not in A['scope']['procedure_editions'] or \
            A['plan_change'] != digests:
        refuse('AUTHORITY_SCOPE_MISMATCH', 5, '/evaluation_authority/scope')
    v_from, v_to = window(A['valid'], '/evaluation_authority/valid')   # CONTRACT §12.7
    if not v_from <= ended <= v_to:
        refuse('AUTHORITY_SCOPE_MISMATCH', 5, '/evaluation_authority/valid')
    e_from, e_to = window(E['valid'], '/execution_authority/valid')
    if X['procedure_edition'] not in E['scope']['procedure_editions'] or E['plan_change'] != digests or \
            not (e_from <= started and ended <= e_to):
        refuse('AUTHORITY_SCOPE_MISMATCH', 5, '/execution_authority/scope')
    return plan_ref, plan, former, executed, scalar


def _result_evidence(records, a, result, scalar, started, ended):
    """CONTRACT §12.3 result-evidence bindings (stage 5, after execution-target agreement).

    T1: owning legacy reconstruction under the evidence's own question time; value,
    instrument, anchor, distinct-occurrence and (amendments C1/C2) occurrence-window
    bindings: received_at and finished_at of the admitted occurrence. T2: application-owned ct.code-evidence.v1 with value, instrument and
    acquisition-window bindings. These are declared-time consistency checks, not
    authenticated chronology or proof of physical acquisition.
    """
    def bad(where):
        refuse('RESULT_EVIDENCE_MISMATCH', 5, '/result/acquisition/public_evidence' + where)
    ev_ref = result['acquisition']['public_evidence']
    kind = records.kind(ev_ref['sha256'])
    m, context = a.model, a.model['context']
    if result['procedure_edition'] == T1:
        if kind != LEGACY_EVIDENCE_KIND:
            bad('/kind')
        if result['acquisition']['instrument_id'] != m['reference_instrument_id']:
            bad('/instrument')
        if ev_ref == m['baseline_evidence']:
            bad('/baseline_reuse')
        evidence = records.get(ev_ref)
        binding, question = evidence.get('binding'), evidence.get('question')
        if not isinstance(binding, dict) or not isinstance(question, dict) or \
                not isinstance(question.get('as_of'), str) or 'assertion_context' not in question:
            refuse('SCHEMA_INVALID', 4, '/result/acquisition/public_evidence')
        if (binding.get('subject_entity_anchor_id') != context['subject_entity_anchor_id'] or
                binding.get('variable_anchor_id') != context['variable_anchor_id']):
            bad('/anchors')
        # Review v4 I-4: the model's assertion context is enforced; only the evidence's own
        # as_of is used, because the T1 acquisition-time binding is pending choice C1.
        own = dict(context, as_of=question['as_of'])
        value, _, admission = _baseline_observation(evidence, own)
        if value is None or value != scalar:
            bad('/value')
        if admission.occurrence_id is None or admission.occurrence_id == a.baseline_admission.occurrence_id:
            bad('/occurrence')
        # Amendment C2.1 (supersedes C1.1 rule 1): received_at and finished_at of the same
        # admitted occurrence both lie in the closed acquisition window.
        try:
            evaluation = evidence['snapshot']['constraint_evaluations'][binding['constraint_evaluation_index']]
            candidate = evaluation['semantic_compatibility']['candidates'][binding['semantic_candidate_index']]
            occurrence = candidate['value_candidate']['state_candidate']['bound']['observed']['occurrence']
            received = datetime.fromisoformat(occurrence['received_at'])
            finished = datetime.fromisoformat(occurrence['finished_at'])
            occurrence_id = occurrence['occurrence_id']
            if received.tzinfo is None or finished.tzinfo is None:
                raise ValueError('naive occurrence instant')
        except (KeyError, IndexError, TypeError, AttributeError, ValueError):
            bad('/acquisition_window')
        if occurrence_id != admission.occurrence_id or not started <= received <= ended or \
                not started <= finished <= ended:
            bad('/acquisition_window')
    else:
        if kind != 'ct.code-evidence.v1':
            bad('/kind')
        evidence = records.get(ev_ref)
        t2 = next(p for p in m['procedures'] if p['edition'] == T2)
        if evidence['code'] != result['observation']['code']:
            bad('/value')
        if not evidence['instrument_id'] == result['acquisition']['instrument_id'] == t2['indicator_instrument_id']:
            bad('/instrument')
        if not started <= instant(evidence['observed_at']) <= ended:
            bad('/acquisition')


def check_prior_material(records, R, descriptor_ref):
    """CONTRACT §7.3: prior material checkable from the closure alone."""
    D = records.get(descriptor_ref)

    def bad(where):
        refuse('PRIOR_BUNDLE_MISMATCH', 5, '/retained_selection' + where)
    if D['prior_manifest'] != R['prior_selection']['manifest']:
        bad('/prior_manifest')
    if D['selection'] != R['prior_selection']['selection']:
        bad('/selection')
    manifest = records.get(D['prior_manifest'])
    if manifest['bundle_kind'] != 'selection' or \
            [(f['name'], f['role']) for f in manifest['files']] != _roles('selection'):
        bad('/prior_manifest/files')
    carried = {'invocation.json': D['invocation'], 'derivation.json': D['derivation'],
               'applicability.json': D['applicability'], 'result.json': D['selection'],
               'trace.json': D['trace'], 'build.json': D['build'], 'policy.json': D['policy']}
    entries = {f['name']: f for f in manifest['files']}
    for name, r in carried.items():
        f = entries[name]
        if f['sha256'] != r['sha256'] or f['bytes'] != len(canonical_bytes(records.get(r))):
            bad('/' + name)
    pc = D['prior_closure']
    if entries['closure.json']['sha256'] != pc['sha256'] or entries['closure.json']['bytes'] != pc['bytes']:
        bad('/prior_closure')
    sub = Records()
    for m in pc['members']:
        sub.by_digest[m['sha256']] = records.by_digest[m['sha256']]
    rebuilt = canonical_bytes(closure_record(pc['roots'], sub))
    if sha(rebuilt) != pc['sha256'] or len(rebuilt) != pc['bytes']:
        bad('/prior_closure/rebuild')
    pool = {m['sha256']: (sub.by_digest[m['sha256']][1] if sub.kind(m['sha256']) == OPAQUE_KIND
                          else canonical_bytes(sub.by_digest[m['sha256']][1])) for m in pc['members']}
    try:
        resolve([pc['roots']['request'], pc['roots']['evaluation_authority']], pool, EDITION_LIMITS,
                SELECTION_KINDS, EDITION_LIMITS['selection_unique_objects'], target='/prior_closure')
    except CheckedRefusal:
        bad('/prior_closure/reachability')
    inv = records.get(D['invocation'])
    if inv['request'] != pc['roots']['request'] or inv['authority'] != pc['roots']['evaluation_authority']:
        bad('/invocation')
    # Review I5: retained calculated records are not trusted; recompute them freshly from the
    # carried prior closure under the carried prior build and compare (design §6).
    try:
        _, _, derivation, applicability, selection = _selection_compute(
            sub, pc['roots']['request'], pc['roots']['evaluation_authority'],
            canonical_bytes(records.get(D['build'])))
    except CheckedRefusal:
        bad('/recompute_refused')
    for name, fresh in (('derivation', derivation), ('applicability', applicability), ('selection', selection)):
        if canonical_bytes(fresh) != canonical_bytes(records.get(D[name])):
            bad('/%s_recomputed' % name)
    # Carried prior trace targets are annotations: prior closure member or prior manifest file record.
    allowed = {m['sha256'] for m in pc['members']} | {f['sha256'] for f in manifest['files']}
    for entry in records.get(D['trace'])['entries']:
        if entry['target'] is not None and entry['target']['sha256'] not in allowed:
            bad('/trace/target')


# --------------------------------------------------------------- bundles

def _utc_now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _enforce_kinds(found, target):
    for path, r, allowed, _ in found.refs:
        if r['kind'] not in allowed:
            refuse('REFERENCE_KIND_MISMATCH', 3, target + path)


def make_bundle(kind, records_by_name, limits, *, filesystem='unknown', created_at=None):
    for name, role in FILE_ROLES:   # computed outputs must satisfy their closed schemas
        if name != 'policy.json':
            value = records_by_name[name]
            validate(value, value['schema'])
    files = {name: canonical_bytes(records_by_name[name]) if name != 'policy.json' else records_by_name[name]
             for name, _ in FILE_ROLES}
    entries = []
    for name, role in FILE_ROLES:
        if role is None:
            role = 'ct.selection.v1' if kind == 'selection' else 'ct.reassessment.v1'
        entries.append({'name': name, 'role': role, 'sha256': sha(files[name]), 'bytes': len(files[name])})
    manifest = {'schema': 'ct.bundle-manifest.v1', 'profile': PROFILE, 'bundle_kind': kind, 'files': entries,
                'created_at_utc': created_at or _utc_now(), 'filesystem': filesystem}
    files['manifest.json'] = canonical_bytes(manifest)
    closure_cap = 'selection_closure_file_bytes' if kind == 'selection' else 'reassessment_closure_file_bytes'
    for name, data in files.items():
        cap = closure_cap if name == 'closure.json' else FILE_CAPS[name]
        if len(data) > limits[cap]:
            refuse('RESOURCE_LIMIT_EXCEEDED', 6, '/bundle/' + name)
    if sum(map(len, files.values())) > limits['bundle_bytes_' + kind]:
        refuse('RESOURCE_LIMIT_EXCEEDED', 6, '/bundle')
    return files


def _closure_decoded_check(closure, limits, kind):
    total = sum(m['decoded_bytes'] for m in closure['members'])
    if total > limits[kind + '_closure_decoded_bytes']:
        refuse('RESOURCE_LIMIT_EXCEEDED', 1, '/closure/decoded_bytes')


def _invocation(operation, request_ref, authority_ref, request_pin, authority_pin, build_ref, replay_of=None):
    return {'schema': 'ct.invocation.v1', 'profile': PROFILE, 'operation': operation, 'request': request_ref,
            'authority': authority_ref, 'expected_request_pin': request_pin,
            'expected_authority_pin': authority_pin, 'build': build_ref,
            'replay_of': None if replay_of is None else {'manifest_sha256': replay_of}}


def _roles(kind):
    result = 'ct.selection.v1' if kind == 'selection' else 'ct.reassessment.v1'
    return [(n, role or result) for n, role in FILE_ROLES]


def read_bundle(files, limits, *, target='/bundle'):
    """Integrity of the nine files against the manifest; returns parsed manifest."""
    if set(files) != set(BUNDLE_NAMES):
        refuse('REFERENCE_MISSING', 3, target)
    manifest = parse_canonical(files['manifest.json'], limits, cap_name='manifest_bytes', target=target + '/manifest')
    validate(manifest, 'ct.bundle-manifest.v1')
    if [(f['name'], f['role']) for f in manifest['files']] != _roles(manifest['bundle_kind']):
        refuse('SCHEMA_INVALID', 2, target + '/manifest/files')
    for f in manifest['files']:
        data = files[f['name']]
        if sha(data) != f['sha256'] or len(data) != f['bytes']:
            refuse('REFERENCE_DIGEST_MISMATCH', 3, target + '/' + f['name'])
    return manifest


def _parse_file(files, name, limits, kind_cap, target):
    value = parse_canonical(files[name], limits, cap_name=kind_cap, target=target + '/' + name,
                            ) if name != 'closure.json' else _parse_closure(files[name], limits, kind_cap, target)
    return value


def _parse_closure(data, limits, cap, target):
    # CONTRACT §12.5: only members[*].data is exempt from string_bytes.
    return parse_canonical(data, limits, cap_name=cap, target=target + '/closure.json', base64_data=True)


# -------------------------------------------------------- public operations

def _start(request_wire, objects, request_pin, authority_pin):
    if sha(request_wire) != request_pin:
        refuse('REQUEST_PIN_MISMATCH', 5, '/request')
    if authority_pin not in objects:
        refuse('AUTHORITY_PIN_MISMATCH', 5, '/evaluation_authority')
    for d, data in objects.items():
        if sha(data) != d:
            refuse('REFERENCE_DIGEST_MISMATCH', 3, '/objects/' + d)
    request = parse_canonical(request_wire, EDITION_LIMITS, target='/request')
    validate(request, 'ct.request.v1') if request.get('schema') == 'ct.request.v1' else refuse(
        'SCHEMA_INVALID', 2, '/request/schema')
    return request


def evaluate_selection(*, request_wire, objects, request_pin, authority_pin, build, filesystem='unknown',
                       created_at=None, cached_derivation=None):
    request = _start(request_wire, objects, request_pin, authority_pin)
    if request['purpose'] != 'selection':
        refuse('SCHEMA_INVALID', 2, '/request/purpose')
    request_ref, authority_ref = ref('ct.request.v1', request_pin), ref('ct.authority.v1', authority_pin)
    pool = dict(objects)
    pool[request_pin] = request_wire
    records = resolve([request_ref, authority_ref], pool, EDITION_LIMITS, SELECTION_KINDS,
                      EDITION_LIMITS['selection_unique_objects'])
    return _selection_bundle(records, request_ref, authority_ref, request_pin, authority_pin, build,
                             'checked-selection-evaluate', None, filesystem, created_at, cached_derivation)


def _selection_stage5(records, a, request_ref, authority_ref):
    A = _authority(records, authority_ref, 'evaluation', '/evaluation_authority')
    if A['target'] != request_ref:
        refuse('AUTHORITY_TARGET_MISMATCH', 5, '/evaluation_authority/target')
    if A['scope']['phase'] != 'selection' or not set(a.procedures) <= set(A['scope']['procedure_editions']) or \
            A['plan_change'] is not None:
        refuse('AUTHORITY_SCOPE_MISMATCH', 5, '/evaluation_authority/scope')
    v_from, v_to = window(A['valid'], '/evaluation_authority/valid')   # CONTRACT §12.7
    if not v_from <= instant(a.request['as_of']) <= v_to:
        refuse('AUTHORITY_SCOPE_MISMATCH', 5, '/evaluation_authority/valid')


def _selection_compute(records, request_ref, authority_ref, build_wire):
    a = admit(records, request_ref, None)
    _selection_stage5(records, a, request_ref, authority_ref)
    _permitted_build(a.policy, build_wire, '/build')
    build_ref = ref('ct.build.v1', sha(build_wire))
    derivation, applicability, plan_claim = _selection_records(records, a, request_ref, build_ref)
    result = _selection_result(a, request_ref, build_ref, derivation, applicability, plan_claim)
    return a, build_ref, derivation, applicability, result


def _bundle_trace(request_ref, closure_bytes, derivation, applicability, result, policy_ref, model_ref, kind):
    step = 'score' if kind == 'selection' else 'interpret'
    rkind = 'ct.selection.v1' if kind == 'selection' else 'ct.reassessment.v1'
    return _trace([
        ('admit', request_ref, 'request_admitted'),
        ('resolve', ref('ct.closure.v1', sha(closure_bytes)), 'closure_equals_reachable_set'),
        ('baseline', model_ref, 'baseline_checks_recorded'),
        ('derive', ref('ct.derivation.v1', sha(canonical_bytes(derivation))), 'fresh_derivation'),
        ('aggregate', ref('ct.applicability.v1', sha(canonical_bytes(applicability))),
         applicability['use_disposition']),
        ('gate', policy_ref, 'captured_policy_applied'),
        (step, ref(rkind, sha(canonical_bytes(result))), result['disposition']),
        ('publish', None, 'manifest_written_last')])


def _trace_limit(trace, limits):
    if len(trace['entries']) > limits['trace_entries']:   # CONTRACT §12.9
        refuse('RESOURCE_LIMIT_EXCEEDED', 6, '/trace_entries')


def _compare_cache(cached, derivation):
    """CONTRACT §12.8: a submitted cache is a comparison artifact only."""
    if cached is None:
        return
    value = parse_canonical(cached, EDITION_LIMITS, cap_name='derivation_bytes', target='/cached_derivation')
    if not isinstance(value, dict) or value.get('schema') != 'ct.derivation.v1':
        refuse('SCHEMA_INVALID', 2, '/cached_derivation/schema')
    validate(value, 'ct.derivation.v1')
    if cached != canonical_bytes(derivation):
        refuse('CACHED_DERIVATION_MISMATCH', 7, '/cached_derivation')


def _selection_bundle(records, request_ref, authority_ref, request_pin, authority_pin, build, operation, replay_of,
                      filesystem, created_at, cached=None):
    build_wire = _current_build(build)
    a, build_ref, derivation, applicability, result = _selection_compute(records, request_ref, authority_ref,
                                                                         build_wire)
    closure = closure_record({'request': request_ref, 'evaluation_authority': authority_ref,
                              'retained_selection': None}, records)
    _closure_decoded_check(closure, a.limits, 'selection')
    cbytes = canonical_bytes(closure)
    trace = _bundle_trace(request_ref, cbytes, derivation, applicability, result, a.policy_ref, a.model_ref,
                          'selection')
    _trace_limit(trace, a.limits)
    _compare_cache(cached, derivation)
    invocation = _invocation(operation, request_ref, authority_ref, request_pin, authority_pin, build_ref, replay_of)
    return make_bundle('selection', {
        'invocation.json': invocation, 'closure.json': closure, 'derivation.json': derivation,
        'applicability.json': applicability, 'result.json': result, 'trace.json': trace,
        'build.json': json.loads(build_wire), 'policy.json': canonical_bytes(a.policy)}, a.limits,
        filesystem=filesystem, created_at=created_at)


def descriptor_from_prior(prior_files, prior_closure, prior_records):
    manifest = json.loads(prior_files['manifest.json'])
    get = {f['name']: f for f in manifest['files']}

    def fref(name, kind):
        return ref(kind, get[name]['sha256'])
    data = prior_files['closure.json']
    return {'schema': 'ct.retained-selection.v1', 'profile': PROFILE,
            'prior_manifest': ref('ct.bundle-manifest.v1', sha(prior_files['manifest.json'])),
            'prior_closure': {'sha256': sha(data), 'bytes': len(data), 'roots': prior_closure['roots'],
                              'members': [ref(m['kind'], m['sha256']) for m in prior_closure['members']]},
            'invocation': fref('invocation.json', 'ct.invocation.v1'),
            'selection': fref('result.json', 'ct.selection.v1'),
            'derivation': fref('derivation.json', 'ct.derivation.v1'),
            'applicability': fref('applicability.json', 'ct.applicability.v1'),
            'trace': fref('trace.json', 'ct.trace.v1'), 'build': fref('build.json', 'ct.build.v1'),
            'policy': fref('policy.json', 'ct.policy.v1')}


def _intake_prior(prior_files, request):
    """Evaluate-time prior-bundle intake; every failure is PRIOR_BUNDLE_MISMATCH."""
    try:
        if set(prior_files) != set(BUNDLE_NAMES) or \
                sha(prior_files['manifest.json']) != request['prior_selection']['manifest']['sha256']:
            raise CheckedRefusal('PRIOR_BUNDLE_MISMATCH', stage=5)
        manifest = read_bundle(prior_files, EDITION_LIMITS, target='/prior')
        if manifest['bundle_kind'] != 'selection':
            raise CheckedRefusal('PRIOR_BUNDLE_MISMATCH', stage=5)
        closure = _parse_closure(prior_files['closure.json'], EDITION_LIMITS, 'selection_closure_file_bytes', '/prior')
        _enforce_kinds(validate(closure, 'ct.closure.v1'), '/prior/closure.json')
        pool, kinds = closure_pool(closure, EDITION_LIMITS, '/prior/closure.json')
        roots = closure['roots']
        if roots['retained_selection'] is not None:
            raise CheckedRefusal('PRIOR_BUNDLE_MISMATCH', stage=5)
        resolve([roots['request'], roots['evaluation_authority']], pool, EDITION_LIMITS, SELECTION_KINDS,
                EDITION_LIMITS['selection_unique_objects'], target='/prior/closure')
        carried = {}
        for name, kind in (('manifest.json', 'ct.bundle-manifest.v1'), ('invocation.json', 'ct.invocation.v1'),
                           ('derivation.json', 'ct.derivation.v1'), ('applicability.json', 'ct.applicability.v1'),
                           ('result.json', 'ct.selection.v1'), ('trace.json', 'ct.trace.v1'),
                           ('build.json', 'ct.build.v1'), ('policy.json', 'ct.policy.v1')):
            value = parse_canonical(prior_files[name], EDITION_LIMITS,
                                    cap_name=FILE_CAPS[name], target='/prior/' + name)
            if value.get('schema') != kind:
                raise CheckedRefusal('PRIOR_BUNDLE_MISMATCH', stage=5)
            found = validate(value, kind)
            carried[sha(prior_files[name])] = prior_files[name]
            # Carried edges must resolve inside the carried material. Derived claim
            # references are non-edges (CONTRACT §12.6) and are checked by recomputation.
            for _, r, _, edge in found.refs:
                if edge and r['sha256'] not in pool and r['sha256'] not in carried and \
                        r['sha256'] not in {sha(prior_files[n]) for n in BUNDLE_NAMES}:
                    raise CheckedRefusal('PRIOR_BUNDLE_MISMATCH', stage=5, target='/carried_reference_unresolvable')
    except CheckedRefusal as e:
        refuse('PRIOR_BUNDLE_MISMATCH', 5, '/prior_bundle' + (e.target if e.target != '/' else ''))
    return closure, pool, carried


def _resolve_reassessment_inputs(*, request_wire, objects, prior_files, request_pin, authority_pin):
    request = _start(request_wire, objects, request_pin, authority_pin)
    if request['purpose'] != 'reassessment':
        refuse('SCHEMA_INVALID', 2, '/request/purpose')
    prior_closure, prior_pool, carried = _intake_prior(prior_files, request)
    descriptor = descriptor_from_prior(prior_files, prior_closure, None)
    d_bytes = canonical_bytes(descriptor)
    if len(d_bytes) > EDITION_LIMITS['retained_selection_bytes']:
        refuse('RESOURCE_LIMIT_EXCEEDED', 1, '/retained_selection')
    request_ref, authority_ref = ref('ct.request.v1', request_pin), ref('ct.authority.v1', authority_pin)
    descriptor_ref = ref('ct.retained-selection.v1', sha(d_bytes))
    pool = dict(prior_pool)
    pool.update(carried)
    pool.update(objects)
    pool[request_pin] = request_wire
    pool[descriptor_ref['sha256']] = d_bytes
    records = resolve([request_ref, authority_ref, descriptor_ref], pool, EDITION_LIMITS, CLOSURE_KINDS,
                      EDITION_LIMITS['reassessment_unique_objects'])
    return records, request_ref, authority_ref, descriptor_ref


def evaluate_reassessment(*, request_wire, objects, prior_files, request_pin, authority_pin, build,
                          filesystem='unknown', created_at=None, cached_derivation=None):
    records, request_ref, authority_ref, descriptor_ref = _resolve_reassessment_inputs(
        request_wire=request_wire, objects=objects, prior_files=prior_files,
        request_pin=request_pin, authority_pin=authority_pin)
    return _reassessment_bundle(records, request_ref, authority_ref, descriptor_ref, request_pin, authority_pin,
                                build, 'checked-reassessment-evaluate', None, filesystem, created_at,
                                cached_derivation)


def _admit_reassessment(records, request_ref, authority_ref, descriptor_ref, build_wire):
    a = admit(records, request_ref, None)
    plan_ref, plan, former, executed, scalar = _reassessment_stage5(records, a, request_ref, authority_ref,
                                                                    descriptor_ref)
    _permitted_build(a.policy, build_wire, '/build')
    return a, plan_ref, plan, former, executed, scalar


def preflight_reassessment(*, request_wire, objects, prior_files, request_pin, authority_pin, build):
    """Full ordinary admission and base applicability; no hypothesis computation/B.

    The returned byte commitments are private call-local facts, not permission
    tokens accepted by evaluate or by a later verification.
    """
    records, request_ref, authority_ref, descriptor_ref = _resolve_reassessment_inputs(
        request_wire=request_wire, objects=objects, prior_files=prior_files,
        request_pin=request_pin, authority_pin=authority_pin)
    build_wire = _current_build(build)
    a, plan_ref, plan, _former, _executed, _scalar = _admit_reassessment(
        records, request_ref, authority_ref, descriptor_ref, build_wire)
    build_ref = ref('ct.build.v1', sha(build_wire))
    applicability = _reassessment_applicability(a, request_ref, build_ref, plan_ref, plan)
    validate(applicability, 'ct.applicability.v1')
    if len(canonical_bytes(applicability)) > a.limits['applicability_bytes']:
        refuse('RESOURCE_LIMIT_EXCEEDED', 7, '/applicability.json')
    roots = {'request': request_ref, 'evaluation_authority': authority_ref,
             'retained_selection': descriptor_ref}
    closure = closure_record(roots, records)
    _closure_decoded_check(closure, a.limits, 'reassessment')
    closure_wire = canonical_bytes(closure)
    if len(closure_wire) > a.limits['reassessment_closure_file_bytes']:
        refuse('RESOURCE_LIMIT_EXCEEDED', 1, '/closure.json')
    return dict(admitted=a, records=records, roots=roots, build_wire=build_wire,
                plan_ref=plan_ref, plan=plan, applicability=applicability,
                closure_wire=closure_wire)


def _reassessment_compute(records, request_ref, authority_ref, descriptor_ref, build_wire):
    a, plan_ref, plan, former, executed, scalar = _admit_reassessment(
        records, request_ref, authority_ref, descriptor_ref, build_wire)
    build_ref = ref('ct.build.v1', sha(build_wire))
    ops = Ops()
    derivation, applicability = _reassessment_records(records, a, request_ref, build_ref, plan_ref, plan, ops)
    result = checked_reassessment.reassess(
        request_ref=request_ref, request=a.request,
        derivation_ref=ref('ct.derivation.v1', sha(canonical_bytes(derivation))),
        applicability_ref=ref('ct.applicability.v1', sha(canonical_bytes(applicability))), build_ref=build_ref,
        model=a.model, derivation=derivation, applicability=applicability, plan=plan, scalar=scalar,
        prior_selection_ref=a.request['prior_selection']['selection'], former_plan=former,
        executed_plan=executed, ops=ops)
    _work_limit(ops, a.limits)
    _cell_limit(derivation, a.limits)
    return a, build_ref, derivation, applicability, result


def _reassessment_bundle(records, request_ref, authority_ref, descriptor_ref, request_pin, authority_pin, build,
                         operation, replay_of, filesystem, created_at, cached=None):
    build_wire = _current_build(build)
    a, build_ref, derivation, applicability, result = _reassessment_compute(records, request_ref, authority_ref,
                                                                            descriptor_ref, build_wire)
    closure = closure_record({'request': request_ref, 'evaluation_authority': authority_ref,
                              'retained_selection': descriptor_ref}, records)
    _closure_decoded_check(closure, a.limits, 'reassessment')
    cbytes = canonical_bytes(closure)
    trace = _bundle_trace(request_ref, cbytes, derivation, applicability, result, a.policy_ref, a.model_ref,
                          'reassessment')
    _trace_limit(trace, a.limits)
    _compare_cache(cached, derivation)
    invocation = _invocation(operation, request_ref, authority_ref, request_pin, authority_pin, build_ref, replay_of)
    return make_bundle('reassessment', {
        'invocation.json': invocation, 'closure.json': closure, 'derivation.json': derivation,
        'applicability.json': applicability, 'result.json': result, 'trace.json': trace,
        'build.json': json.loads(build_wire), 'policy.json': canonical_bytes(a.policy)}, a.limits,
        filesystem=filesystem, created_at=created_at)


# ----------------------------------------------------------- verify/replay

SCORE_FIELDS = ('score_domain', 'post_measurement_elimination_guaranteed', 'presentation', 'use_disposition',
                'observation_uncertainty_not_in_score')
REASSESSMENT_FIELDS = ('ranking', 'adoption', 'presentation', 'selection_basis', 'prior_selection',
                       'former_plan', 'executed_plan', 'plan_changed', 'original_plan_executed')


def _open_bundle(files, request_pin, authority_pin):
    manifest = read_bundle(files, EDITION_LIMITS)
    kind = manifest['bundle_kind']
    cap = kind + '_closure_file_bytes'
    closure = _parse_closure(files['closure.json'], EDITION_LIMITS, cap, '/bundle')
    _enforce_kinds(validate(closure, 'ct.closure.v1'), '/closure.json')
    roots = closure['roots']
    if roots['request']['sha256'] != request_pin:
        refuse('REQUEST_PIN_MISMATCH', 5, '/closure/roots/request')
    if roots['evaluation_authority']['sha256'] != authority_pin:
        refuse('AUTHORITY_PIN_MISMATCH', 5, '/closure/roots/evaluation_authority')
    invocation = parse_canonical(files['invocation.json'], EDITION_LIMITS, cap_name='invocation_bytes',
                                 target='/bundle/invocation.json')
    validate(invocation, 'ct.invocation.v1')
    if invocation['request'] != roots['request']:
        refuse('REQUEST_PIN_MISMATCH', 5, '/invocation/request')
    if invocation['authority'] != roots['evaluation_authority']:
        refuse('AUTHORITY_PIN_MISMATCH', 5, '/invocation/authority')
    if (kind == 'selection') != (roots['retained_selection'] is None):
        refuse('SCHEMA_INVALID', 2, '/closure/roots/retained_selection')
    if not invocation['operation'].startswith('checked-%s-' % kind):
        refuse('SCHEMA_INVALID', 2, '/invocation/operation')
    pool, member_kinds = closure_pool(closure, EDITION_LIMITS)
    allowed = SELECTION_KINDS if kind == 'selection' else CLOSURE_KINDS
    for d, k in sorted(member_kinds.items()):
        if k not in allowed:   # CONTRACT §7.3 allowed member kinds per bundle kind
            refuse('REFERENCE_KIND_MISMATCH', 3, '/closure/' + d)
    _closure_decoded_check(closure, EDITION_LIMITS, kind)
    if kind == 'reassessment':
        d = roots['retained_selection']['sha256']
        if d not in pool:
            refuse('REFERENCE_MISSING', 3, '/closure/' + d)
        if len(pool[d]) > EDITION_LIMITS['retained_selection_bytes']:
            refuse('RESOURCE_LIMIT_EXCEEDED', 1, '/retained_selection')
    root_list = [roots['request'], roots['evaluation_authority']] + \
        ([roots['retained_selection']] if kind == 'reassessment' else [])
    records = resolve(root_list, pool, EDITION_LIMITS, SELECTION_KINDS if kind == 'selection' else CLOSURE_KINDS,
                      EDITION_LIMITS[kind + '_unique_objects'])
    return manifest, kind, closure, roots, invocation, records


def _compare(files, name, expected, code):
    if files[name] != canonical_bytes(expected):
        refuse(code, 7, '/bundle/' + name)


def _check_bundle(files, request_pin, authority_pin, build, *, replay):
    manifest, kind, closure, roots, invocation, records = _open_bundle(files, request_pin, authority_pin)
    request = records.get(roots['request'])
    if request['purpose'] != kind:
        refuse('SCHEMA_INVALID', 2, '/request/purpose')
    if files['closure.json'] != canonical_bytes(closure_record(roots, records)):
        refuse('REFERENCE_KIND_MISMATCH', 3, '/closure.json/members')   # review I1: labels must match
    current = _current_build(build)
    recorded = files['build.json']
    build_value = parse_canonical(recorded, EDITION_LIMITS, cap_name='build_bytes', target='/bundle/build.json')
    validate(build_value, 'ct.build.v1')
    if invocation['build']['sha256'] != sha(recorded):
        refuse('REFERENCE_DIGEST_MISMATCH', 3, '/invocation/build')
    policy = records.get(request['policy'])
    if files['policy.json'] != canonical_bytes(policy):
        refuse('REFERENCE_DIGEST_MISMATCH', 3, '/bundle/policy.json')
    _permitted_build(policy, recorded, '/bundle/build.json')
    _permitted_build(policy, current, '/build/current')
    if replay and current != recorded:
        refuse('HISTORICAL_BUILD_UNAVAILABLE', 5, '/build')
    if kind == 'selection':
        a, build_ref, derivation, applicability, result = _selection_compute(
            records, roots['request'], roots['evaluation_authority'], recorded)
    else:
        a, build_ref, derivation, applicability, result = _reassessment_compute(
            records, roots['request'], roots['evaluation_authority'], roots['retained_selection'], recorded)
    trace = parse_canonical(files['trace.json'], EDITION_LIMITS, cap_name='trace_bytes', target='/bundle/trace.json')
    validate(trace, 'ct.trace.v1')
    _trace_limit(trace, policy['limits'])
    allowed = set(records.by_digest) | {f['sha256'] for f in manifest['files']}
    for entry in trace['entries']:   # annotation targets resolve, but are not reachability edges
        if entry['target'] is not None and entry['target']['sha256'] not in allowed:
            refuse('REFERENCE_MISSING', 3, '/bundle/trace.json/target')
    _compare(files, 'derivation.json', derivation, 'DERIVATION_MISMATCH')
    _compare(files, 'applicability.json', applicability, 'APPLICABILITY_MISMATCH')
    supplied = parse_canonical(files['result.json'], EDITION_LIMITS, cap_name='result_bytes',
                               target='/bundle/result.json')
    for field in (SCORE_FIELDS if kind == 'selection' else REASSESSMENT_FIELDS):
        if supplied.get(field) != result[field]:
            refuse('SCORE_METADATA_INVALID', 7, '/result/' + field)
    validate(supplied, result['schema'])
    for field in ('request', 'derivation', 'applicability', 'build'):
        if supplied[field] != result[field]:
            refuse('REFERENCE_DIGEST_MISMATCH', 7, '/result/' + field)
    return manifest, kind, roots, records, result, derivation, applicability, a


def verify(*, bundle_files, request_pin, authority_pin, build):
    manifest, kind, roots, records, *_ = _check_bundle(bundle_files, request_pin, authority_pin, build,
                                                       replay=False)
    report = {'operation': 'checked-%s-verify' % kind, 'bundle_commitment': sha(bundle_files['manifest.json']),
              'derivation_checked': True, 'applicability_policy_checked': True,
              'downstream_result_not_replayed': True}
    if kind == 'reassessment':
        report['prior_material_checked'] = True
    return report


def replay(*, bundle_files, request_pin, authority_pin, build, filesystem='unknown', created_at=None):
    manifest, kind, roots, records, result, derivation, applicability, a = _check_bundle(
        bundle_files, request_pin, authority_pin, build, replay=True)
    _compare(bundle_files, 'result.json', result, 'DOWNSTREAM_REPLAY_MISMATCH')
    trace = _bundle_trace(roots['request'], bundle_files['closure.json'], derivation, applicability, result,
                          a.policy_ref, a.model_ref, kind)
    _compare(bundle_files, 'trace.json', trace, 'DOWNSTREAM_REPLAY_MISMATCH')
    replay_of = sha(bundle_files['manifest.json'])
    op = 'checked-%s-replay' % kind
    if kind == 'selection':
        return _selection_bundle(records, roots['request'], roots['evaluation_authority'], request_pin,
                                 authority_pin, build, op, replay_of, filesystem, created_at)
    return _reassessment_bundle(records, roots['request'], roots['evaluation_authority'],
                                roots['retained_selection'], request_pin, authority_pin, build, op, replay_of,
                                filesystem, created_at)
