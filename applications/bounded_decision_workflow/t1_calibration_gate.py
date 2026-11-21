"""Carried-acquisition calibration gate; no owning result, override or adoption.

Only workflow orchestration may publish the guarantee, after genuine producer,
handoff and owning admission checks. These pure helpers accept call-local
verified material, never a persisted 'verified' flag or supplied finding.
"""
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

from .t1_contracts import PROFILE, canonical_bytes, fraction, ref, refuse, sha
from .t1_schemas import validate as validate_schema

RULE = 'ct.t1-calibration-primary-gate.v2'
GUARANTEE = 'producer-checked-primary-calibration-gated-v1'
FINDING = 'ct.t1-calibration-gate-finding.v1'
OUTCOME = 'ct.t1-calibration-gate-outcome.v1'
CHECK = 'ct.t1-calibration-gate-check.v1'
SCHEMAS_SHA256 = '81126f8f63cd6ef5ff4bd3046e814d0a1a1d51680828522ace8ad3910aa25a39'
CAPS = {FINDING: 23770, OUTCOME: 32768, CHECK: 65536}
GROUPS = ('producer_closure', 'source_editions', 'handoff_request', 'request_carriage',
          'observation_occurrence', 'raw_occurrence', 'instrument', 'model_claim_bound',
          'intended_actual', 'structural_lifecycle', 'source_configuration',
          'effective_binding', 'effective_interpretation_units', 'time_scope',
          'review_and_base', 'arithmetic')
LIMITATIONS = ["The guarantee requires this companion package and exact retained producer, handoff and prior inputs.","The owning bundle alone and direct owning invocation do not carry the companion calibration guarantee.","Only the carried declared synthetic acquisition is checked; physical-source qualification is not established.","A noncontradictory gate permits delegation; it does not establish interval-wide calibration or scientific validity.","General historical-evidence adjudication and correction release are not supported; nothing is adopted."]
_wire = Path(__file__).with_name('t1_calibration_schemas_v2.json').read_bytes()
if sha(_wire) != SCHEMAS_SHA256:
    refuse('SIM_EDITION_NOT_PERMITTED', 2, '/calibration/schemas')
SCHEMAS = json.loads(_wire)


def _error(code='CALIBRATION_PACKAGE_MISMATCH', target='/calibration'):
    refuse(code, 9, target)


def _common(kind):
    return dict(schema=kind, profile=PROFILE, rule_edition=RULE, schemas_sha256=SCHEMAS_SHA256)


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _error(target='/calibration/duplicate_key')
        result[key] = value
    return result


def _bad_number(_value):
    _error(target='/calibration/number')


def parse(wire, kind):
    if kind not in CAPS or len(wire) > CAPS[kind]:
        refuse('SIM_RESOURCE_LIMIT', 9, '/calibration/record', 4)
    try:
        value = json.loads(wire, object_pairs_hook=_unique, parse_float=_bad_number,
                           parse_constant=_bad_number)
    except RecursionError:
        refuse('SIM_RESOURCE_LIMIT', 9, '/calibration/depth', 4)
    except (UnicodeError, ValueError, TypeError):
        _error(target='/calibration/json')
    pending, nodes = [(value, 1)], 0
    while pending:
        item, depth = pending.pop()
        nodes += 1
        if depth > 24 or nodes > 65536:
            refuse('SIM_RESOURCE_LIMIT', 9, '/calibration/structure', 4)
        if isinstance(item, dict):
            pending.extend((x, depth + 1) for pair in item.items() for x in pair)
        elif isinstance(item, list):
            pending.extend((x, depth + 1) for x in item)
    if canonical_bytes(value) != wire:
        _error(target='/calibration/canonical')
    validate(value, kind)
    return value


def validate(value, kind):
    validate_schema(value, kind, '/calibration', schema_pack=SCHEMAS)
    if value['schema'] != kind or value['schemas_sha256'] != SCHEMAS_SHA256:
        _error(target='/calibration/edition')
    if kind == OUTCOME:
        validate(value['finding'], FINDING)
        if (value['operation'] == 't1-reassessment-evaluate') != (value['replay_of'] is None):
            _error(target='/calibration/replay_of')
        blocked = value['finding']['effect'] != 'permission_to_delegate'
        if blocked != (value['delegation']['status'] == 'not_run'):
            _error(target='/calibration/delegation')
    if kind == FINDING:
        rows = value['comparisons']
        if tuple(row['group'] for row in rows) != GROUPS or sum(len(r['operands']) for r in rows) > 128:
            _error(target='/calibration/comparisons')
        if ref('ct.claim.v1', canonical_bytes(value['required_claim_core'])) != value['subjects']['required_claim']:
            _error(target='/calibration/claim')
        decision = decide(rows, value['calibration']['computed_predicate'])
        if any(value[k] != decision[k] for k in ('qualification', 'reasons', 'effect')):
            _error('CALIBRATION_FINDING_MISMATCH')
        if value['calibration']['declared_predicate'] != value['calibration']['computed_predicate']:
            _error('CALIBRATION_FINDING_MISMATCH', '/calibration/diagnostic')
    if kind == CHECK:
        allowed = {'t1-reassessment-evaluate': ('completion',),
                   't1-workflow-verify': ('verification', 'completion'),
                   't1-workflow-replay': ('replay',)}
        if value['operation_class'] not in allowed[value['command']]:
            _error(target='/calibration/check/operation_class')
        if (value['command'] == 't1-workflow-replay') != (value['replay_origin'] is not None):
            _error(target='/calibration/check/replay_origin')
    if len(canonical_bytes(value)) > CAPS[kind]:
        refuse('SIM_RESOURCE_LIMIT', 9, '/calibration/record', 4)


def encode(value):
    validate(value, value['schema'])
    return canonical_bytes(value)


def _at(value):
    at = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if at.tzinfo is None or at.utcoffset() != timezone.utc.utcoffset(at):
        _error(target='/calibration/time_axis')
    return at


def scope_status(scope, window, witness):
    """Half-open effective scope must cover the whole closed acquisition."""
    if scope is None:
        return 'unknown'
    if scope['axis'] != 'ingestion_received_at' or scope['interval_semantics'] != 'half_open':
        return 'unknown'
    statuses = []
    for name, tests in (
        ('start_boundary', lambda at: at <= _at(window['from']) and at <= _at(witness)),
        ('end_boundary', lambda at: at > _at(window['to']) and at > _at(witness))):
        boundary = scope[name]
        statuses.append('equal' if boundary['kind'] == 'unbounded' else
                        ('equal' if tests(_at(boundary['at'])) else 'different')
                        if boundary['kind'] == 'declared' else 'unknown')
    return _combine(statuses)


def time_status(required, supported, witness):
    """A definitely supported failed instant, not overlapping uncertain ranges."""
    if witness is None:
        return 'unknown'
    t = _at(witness)
    return 'equal' if (_at(required['from']) <= t <= _at(required['to']) and
                       _at(supported['from']) <= t <= _at(supported['to'])) else 'different'


def _combine(statuses):
    return 'different' if 'different' in statuses else 'unknown' if 'unknown' in statuses else 'equal'


def effective_status(resolution, collection, window, witness):
    """Qualify the positive resolver basis, not every disclosed historical row.

    The owning resolver discloses inactive/outside assertions too. One active,
    definitely in-scope assertion supporting its unique result must cover the
    whole window. A redundant unknown is not a required missing link when an
    independently complete positive basis exists. Raw history stays retained.
    """
    statuses = []
    for summary in resolution.get('via_assertions', []):
        scope = collection.effective_applies.get(summary['record_id'])
        if scope is not None and scope.model_dump(mode='json') != summary['effective_applies']:
            _error('CALIBRATION_FINDING_MISMATCH', '/calibration/effective_scope')
        if not summary['active'] or summary['membership_at'] != 'in':
            continue
        target = resolution.get('resolved_target')
        if target is not None and summary.get('target_anchor_id') != target['anchor_id']:
            continue
        interpretation = resolution.get('interpretation')
        if interpretation is not None and summary.get('interpretation') != interpretation:
            continue
        statuses.append(scope_status(None if scope is None else scope.model_dump(mode='json'), window, witness))
    return 'equal' if 'equal' in statuses else 'unknown' if not statuses or 'unknown' in statuses else 'different'


def decide(rows, predicate):
    """Total restrictive classifier, used separately by classifier-level tests."""
    if type(predicate) is not bool or not rows:
        _error(target='/calibration/decision')
    states = [r['status'] for r in rows]
    if any(s not in ('equal', 'different', 'unknown', 'not_applicable') for s in states):
        _error(target='/calibration/decision/status')
    reasons = {r['reason'] for r in rows if r['reason'] is not None and r['status'] != 'equal'}
    if 'different' in states:
        qualification, effect = 'established_mismatch', 'block_required_correspondence'
        reasons.add('required_primary_match_missing')
    elif 'unknown' in states or 'not_applicable' in states:
        qualification, effect = 'insufficient_information', 'block_required_correspondence'
        reasons.add('correspondence_unresolved')
    else:
        qualification = 'qualified_match'
        effect = 'permission_to_delegate' if predicate else 'block_counterexample'
        reasons.add('no_counterexample_from_this_check' if predicate else 'calibration_premise_counterexample')
    return dict(qualification=qualification, effect=effect, reasons=sorted(reasons))


def _pointer(value, pointer):
    for part in pointer.split('/')[1:] if pointer else ():
        part = part.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def _normalized(value):
    if value is None:
        return dict(kind='missing', value=None)
    if type(value) is bool:
        return dict(kind='boolean', value=value)
    if isinstance(value, dict) and set(value) == {'kind', 'sha256'}:
        return dict(kind='ref', value=value)
    if isinstance(value, (dict, list)) or type(value) is int:
        return dict(kind='canonical_object_digest', value=sha(canonical_bytes(value)))
    if not isinstance(value, str):
        _error(target='/calibration/operand')
    return dict(kind='text', value=value)


def qualify_carried_calibration(*, verified, producer_files, handoff_wire, request_wire, preflight):
    """Join the admitted carried graph; fresh reconstruction supplies resolver truth.

    Graph integrity/admission is performed by the workflow before calling here.
    Every verify/replay repeats that work; no retained Q/report is accepted here.
    """
    from .checked_applicability import claim_core
    from .t1_oracle import receipt_values
    from .t1_acquisition import context_components
    a = verified['admission']
    j, d = a.root('J'), verified['receipt']
    x = a.get(j['execution_target'])
    w, c, model = a.get(j['world']), a.get(j['context']), a.get(x['model'])
    plan = a.get(x['interpretation_plan'])
    r, h = json.loads(request_wire), json.loads(handoff_wire)
    o = json.loads(producer_files['evidence/public/evidence.json'])
    # The producer verifier has recomputed classification through the owning
    # backend. Check the exact observation, not an asserted resolver summary.
    if producer_files['evidence/public/evidence.json'] != verified['reconstructed']['public_evidence']:
        _error('CALIBRATION_FINDING_MISMATCH', '/calibration/reconstructed_observation')
    owner = preflight['admitted']
    claim = claim_core(model_ref=owner.model_ref, model=owner.model, procedure='ct.procedure.T1.v1',
                       phase='reassessment', condition='reference_calibration')
    core_ref = ref('ct.claim.v1', canonical_bytes(claim))
    source_manifest = json.loads(producer_files['manifest.json'])
    subjects = dict(producer_manifest=ref('ct.t1-producer-manifest.v1', producer_files['manifest.json']),
        producer_receipt=source_manifest['roots']['receipt'], target=a.references['J'],
        permission=a.references['G'], execution_authority=a.references['E'], execution_target=j['execution_target'],
        world=j['world'], context=j['context'], public_evidence=d['public_evidence'],
        request=ref('ct.request.v1', request_wire), evaluation_authority=preflight['roots']['evaluation_authority'],
        handoff=ref('ct.t1-handoff.v1', handoff_wire), model=r['model'], interpretation_plan=x['interpretation_plan'],
        required_claim=core_ref, captured_policy=j['captured_policy'], assessment_policy=r['policy'],
        simulator_policy=j['simulator_policy'], producer_build=j['producer_build'],
        checker_build=ref('ct.build.v1', preflight['build_wire']))
    if subjects['producer_build'] != subjects['checker_build']:
        refuse('SIM_EDITION_NOT_PERMITTED', 2, '/calibration/checker_build')
    bodies = dict(producer_manifest=source_manifest, producer_receipt=d, target=j, permission=a.root('G'),
        execution_authority=a.root('E'), execution_target=x, world=w, context=c, public_evidence=o,
        request=r, handoff=h, model=owner.model, interpretation_plan=plan, required_claim=claim,
        captured_policy=a.get(j['captured_policy']), assessment_policy=owner.policy,
        simulator_policy=a.get(j['simulator_policy']), producer_build=a.get(j['producer_build']),
        checker_build=json.loads(preflight['build_wire']),
        evaluation_authority=preflight['records'].get(preflight['roots']['evaluation_authority']))
    rows = []

    def row(group, locations, status='equal', reason=None):
        rows.append(dict(group=group, relation='all_required_links',
            operands=[dict(subject=s, pointer=p, normalized_value=_normalized(_pointer(bodies[s], p)))
                      for s, p in locations],
            status=status, reason=None if status == 'equal' else reason))

    def equal(values):
        known = [v for v in values if v is not None]
        if known and any(v != known[0] for v in known[1:]):
            return 'different'
        return 'unknown' if len(known) != len(values) else 'equal'

    checks = [d[key] == j[key] for key in ('execution_target', 'world', 'context', 'rule',
              'simulator_policy', 'captured_policy', 'producer_build')]
    checks += [d['target'] == a.references['J'], d['permission'] == a.references['G'],
               d['execution_authority'] == a.references['E']]
    row('producer_closure', [('producer_manifest', '/roots'), ('producer_receipt', '/target'),
        ('target', '')], 'equal' if all(checks) else 'different', 'context_mismatch')
    # These two policies have different ownership. Do not demand their equality.
    row('source_editions', [('target', '/producer_build'), ('target', '/companion_schemas_sha256'),
        ('target', '/rule'), ('target', '/captured_policy'), ('request', '/policy'),
        ('simulator_policy', '/permitted_checker_builds'), ('simulator_policy', '/permitted_producer_builds'),
        ('simulator_policy', '/preset_sha256'), ('captured_policy', '/permitted_builds'),
        ('assessment_policy', '/permitted_builds'), ('context', '/preset')])
    joins = dict(request=subjects['request'], producer_manifest=subjects['producer_manifest'],
        target=subjects['target'], permission=subjects['permission'], execution_authority=subjects['execution_authority'],
        execution_target=subjects['execution_target'], prior=x['prior_selection'], public_evidence=d['public_evidence'])
    row('handoff_request', [('handoff', ''), ('request', '')],
        'equal' if all(h[k] == v for k, v in joins.items()) else 'different', 'context_mismatch')
    acq = r['result']['acquisition']
    carriage = (h['carriage']['model'] == r['model'] == x['model'] and
        r['execution_target'] == j['execution_target'] and r['prior_selection'] == x['prior_selection'] and
        r['selection_basis'] == 'inherited' and r['plan_change'] is None and
        r['result']['procedure_edition'] == 'ct.procedure.T1.v1' and
        r['result']['execution_authority'] == a.references['E'] and
        r['result']['interpretation_plan'] == x['interpretation_plan'] and
        Fraction(r['result']['observation']['scalar']) == Fraction(d['r']) and
        acq['started'] == j['window']['from'] and acq['ended'] == j['window']['to'] and
        acq['public_evidence'] == d['public_evidence'])
    row('request_carriage', [('request', '/result'), ('handoff', '/carriage')],
        'equal' if carriage else 'different', 'context_mismatch')
    b = o['binding']
    cp = '/snapshot/constraint_evaluations/%d/semantic_compatibility/candidates/%d' % (
        b['constraint_evaluation_index'], b['semantic_candidate_index'])
    candidate = _pointer(o, cp)
    sp = cp + '/value_candidate/state_candidate'
    state_candidate = candidate['value_candidate']['state_candidate']
    bp = sp + '/bound'
    op = bp + '/observed/occurrence'
    occurrence = _pointer(o, op)
    occurrence_checks = [d['admitted'][k] == (occurrence[k].replace('+00:00', 'Z') if k.endswith('_at')
                         else occurrence[k]) for k in ('occurrence_id', 'raw_record_id', 'ingestion_run_id',
                         'payload_checksum', 'received_at', 'finished_at', 'attempt_started_at')]
    occurrence_checks += [d['admitted']['evidence_id'] == o['id'],
                          ref('nm.evidence.v1', producer_files['evidence/public/evidence.json']) == d['public_evidence']]
    row('observation_occurrence', [('public_evidence', op), ('producer_receipt', '/admitted')],
        'equal' if all(occurrence_checks) else 'different', 'context_mismatch')
    raw_digest = d['raw_response_digests']['printer_objects']
    raw_ok = occurrence['payload_checksum'] == 'sha256:' + sha(producer_files['evidence/raw/' + raw_digest])
    row('raw_occurrence', [('public_evidence', op + '/payload_checksum'),
        ('producer_receipt', '/raw_response_digests')], 'equal' if raw_ok else 'different', 'context_mismatch')
    instruments = [j['instrument_id'], w['instrument_id'], x['instrument_id'], plan['instrument_id'],
                   owner.model['reference_instrument_id'], acq['instrument_id'],
                   claim['binding']['parameters']['instrument_id']]
    row('instrument', [('target', '/instrument_id'), ('world', '/instrument_id'),
        ('execution_target', '/instrument_id'), ('interpretation_plan', '/instrument_id'),
        ('model', '/reference_instrument_id'), ('request', '/result/acquisition/instrument_id'),
        ('required_claim', '/binding/parameters/instrument_id')],
        equal(instruments), 'instrument_mismatch')
    bound_equal = (r['model'] == x['model'] == claim['model'] and
        all(fraction(owner.model['b_ref'][k]) == fraction(model['b_ref'][k]) ==
            fraction(d['diagnostics']['reference_calibration']['b_ref'][k]) ==
            fraction(claim['binding']['parameters']['b_ref'][k]) for k in ('lo', 'hi')))
    row('model_claim_bound', [('execution_target', '/model'), ('required_claim', ''),
        ('model', '/b_ref'), ('producer_receipt', '/diagnostics/reference_calibration/b_ref')],
        'equal' if bound_equal else 'different', 'claim_or_bound_mismatch')
    intended = dict(subject_entity_anchor_id=claim['subject_entity_anchor_id'],
                    variable_anchor_id=claim['variable_anchor_id'])
    anchor_checks = []
    for key, short in (('subject_entity_anchor_id', 'subject'), ('variable_anchor_id', 'variable')):
        anchor_checks.extend([w['intended_' + key] == c['intended_' + key] == b[key] ==
                              owner.model['context'][key] == intended[key],
                              d['intended'][short] == intended[key]])
    anchor_checks += [w['actual_measurand'] == d['actual_measurand'] == intended]
    loaded, bindings, interpretations = context_components(c)
    variable = loaded.variable_registrations_by_anchor.get(intended['variable_anchor_id'])
    anchor_checks.append(variable is not None and variable.anchor.entity_anchor_id == intended['subject_entity_anchor_id'])
    row('intended_actual', [('world', '/actual_measurand'), ('producer_receipt', '/actual_measurand'),
        ('required_claim', '/subject_entity_anchor_id'), ('required_claim', '/variable_anchor_id')],
        'equal' if all(anchor_checks) else 'different', 'actual_measurand_mismatch')
    baseline = a.get(model['baseline_evidence'])
    structural = (owner.model['context']['structural_model_revision'] == c['material']['revision']['revision_id'] and
        c['material'] == baseline['snapshot']['state']['material'] == o['snapshot']['state']['material'] and
        owner.model['context']['assertion_context'] == c['assertion_context'] == o['question']['assertion_context'])
    row('structural_lifecycle', [('model', '/context'), ('context', '/material'),
        ('context', '/assertion_context'), ('public_evidence', '/question/assertion_context')],
        'equal' if structural else 'different', 'context_mismatch')
    locator = c['reading_locator']
    bound = _pointer(o, bp)
    for record in (state_candidate, occurrence, locator):
        if not all(isinstance(record.get(key), dict) for key in ('subject', 'property')):
            refuse('SIM_REFERENCE_INVALID', 1, '/calibration/reading_locator')
    config_ok = (w['source'] == dict(source_id=c['source_definition']['source_id'], adapter_id='moonraker') and
                 state_candidate['subject'] == occurrence['subject'] == locator['subject'] and
                 state_candidate['property'] == occurrence['property'] == locator['property'])
    row('source_configuration', [('world', '/source'), ('context', '/source_definition'),
        ('context', '/reading_locator'), ('context', '/condition_sources'), ('public_evidence', sp + '/subject'),
        ('public_evidence', sp + '/property'), ('public_evidence', op + '/subject'),
        ('public_evidence', op + '/property')], 'equal' if config_ok else 'different', 'context_mismatch')
    witness = d['admitted']['received_at']

    resolution = bound['resolution']
    bs = effective_status(resolution, bindings, j['window'], witness)
    binding_reason = 'source_scope_insufficient'
    if resolution['status'] != 'bound' or resolution['resolved_target'] is None:
        bs = _combine([bs, 'unknown'])
    elif (resolution['resolved_target']['anchor_id'] != intended['variable_anchor_id'] or
          resolution['resolved_target']['entity_anchor_id'] != intended['subject_entity_anchor_id']):
        bs = 'different'
        binding_reason = 'anchor_mismatch'
    row('effective_binding', [('public_evidence', bp + '/resolution'), ('context', '/binding_set_id'),
        ('context', '/bindings')], bs, 'effective_scope_unknown' if bs == 'unknown' else binding_reason)
    istates = []
    for dimension, field in (('quantity_kind', 'expected_quantity_kind'),
                              ('observation_role', 'expected_observation_role'), ('unit', 'expected_unit')):
        result = candidate['interpretation'][dimension]
        istates.append(effective_status(result, interpretations, j['window'], witness))
        if result['status'] != 'interpreted' or result['interpretation'] is None:
            istates.append('unknown')
        elif result['interpretation'][dimension] != b[field] or b[field] != c[field]:
            istates.append('different')
    istates.append('equal' if w['unit'] == d['intended']['unit'] == plan['unit'] == 'degree_celsius'
                   else 'different')
    state = _combine(istates)
    row('effective_interpretation_units', [('public_evidence', cp + '/interpretation'),
        ('public_evidence', '/binding/expected_unit'), ('context', '/interpretation_set_id'),
        ('context', '/interpretations'), ('world', '/unit')], state,
        'effective_scope_unknown' if state == 'unknown' else 'context_mismatch')
    required = dict(axis='declared_assessment_time', **{'from': owner.model['context']['as_of'],
                                                      'to': acq['ended']})
    ts = time_status(required, j['window'], witness)
    if not (_at(j['window']['from']) <= _at(d['admitted']['finished_at']) <= _at(j['window']['to'])):
        ts = 'different'
    if not (j['question_as_of'] == o['question']['as_of'] == o['snapshot']['as_of'] == j['window']['to']):
        ts = 'different'
    row('time_scope', [('model', '/context/as_of'), ('target', '/window'),
        ('producer_receipt', '/admitted/received_at'), ('producer_receipt', '/admitted/finished_at'),
        ('target', '/question_as_of'), ('public_evidence', '/question/as_of'),
        ('public_evidence', '/snapshot/as_of')],
        ts, 'failure_outside_required_interval')
    row('review_and_base', [('request', '/claims'), ('request', '/evidence_items'), ('request', '/reviews'),
        ('request', '/policy')])
    independent = receipt_values(j, a.root('E'), a.get)
    declared = d['diagnostics']['reference_calibration']['beta_in_b_ref']
    beta = Fraction(w['beta'])
    predicate = fraction(claim['binding']['parameters']['b_ref']['lo']) <= beta <= fraction(
        claim['binding']['parameters']['b_ref']['hi'])
    if (d['operands'] != independent['operands'] or
            independent['diagnostics'] != d['diagnostics'] or declared != predicate):
        refuse('SIM_DERIVATION_MISMATCH', 7, '/receipt/diagnostics/reference_calibration')
    row('arithmetic', [('world', '/beta'), ('required_claim', '/binding/parameters/b_ref'),
        ('producer_receipt', '/diagnostics/reference_calibration/beta_in_b_ref')])
    review_refs = []
    for item_ref, item in owner.supplied['evidence_items']:
        if core_ref in item['claims']:
            review_refs.append(item_ref)
            review_refs.extend(rr for rr, review in owner.supplied['reviews']
                               if review['item'] == item_ref and review['claim'] == core_ref)
    finding = dict(_common(FINDING), subjects=subjects, required_claim_core=claim, required_scope=required,
        source_scope=dict(axis='declared_synthetic_acquisition_time', **j['window'], witness_instant=witness),
        comparisons=rows, calibration=dict(beta=w['beta'], b_ref=claim['binding']['parameters']['b_ref'],
            predicate='beta_in_closed_b_ref', declared_predicate=declared, computed_predicate=predicate),
        review_refs=sorted({(rr['kind'], rr['sha256']): rr for rr in review_refs}.values(),
                           key=lambda rr: (rr['kind'], rr['sha256'])),
        base_applicability=ref('ct.applicability.v1', canonical_bytes(preflight['applicability'])),
        source_qualification='declared_synthetic', physical_source_qualification='not_established',
        **decide(rows, predicate))
    encode(finding)
    return finding


def conclusion(finding, base, result=None):
    effect = finding['effect']
    reasons = sorted({reason for row in base['claims'] for reason in row['block_reasons']})
    if effect != 'permission_to_delegate':
        status = ('blocked_calibration_counterexample' if effect == 'block_counterexample'
                  else 'blocked_calibration_correspondence')
        if effect == 'block_counterexample':
            calibration = finding['calibration']
            lo, hi = (str(fraction(calibration['b_ref'][key])) for key in ('lo', 'hi'))
            detail = ('Required reference_calibration contradicted for instrument %s, claim %s: '
                      'recomputed bias %s is outside [%s,%s] at %s within [%s,%s]. Receipt %s. ' % (
                          finding['required_claim_core']['binding']['parameters']['instrument_id'],
                          finding['subjects']['required_claim']['sha256'], calibration['beta'], lo, hi,
                          finding['source_scope']['witness_instant'], finding['required_scope']['from'],
                          finding['required_scope']['to'], finding['subjects']['producer_receipt']['sha256']))
        else:
            links = ', '.join(row['group'] + ':' + row['status'] for row in finding['comparisons']
                              if row['status'] != 'equal')
            detail = ('Required calibration correspondence %s: %s. No calibration falsity is asserted. ' % (
                finding['qualification'], links))
        detail += 'Owning hypothesis assessment was not run. Reviews are retained. No admissible hypothesis conclusion.'
        disposition, admissibility = None, 'blocked'
    else:
        if result is None:
            _error(target='/calibration/missing_result')
        status = 'delegated_assessment'
        disposition = result['disposition']
        allowed = base['use_disposition']
        if (allowed == 'blocked') != (disposition == 'applicability_blocked'):
            _error('CALIBRATION_OUTCOME_MISMATCH', '/calibration/base_result')
        if disposition == 'applicability_blocked':
            admissibility = 'blocked'
        elif disposition == 'incomplete_assessment':
            admissibility = 'unresolved'
        elif disposition == 'model_prediction_mismatch':
            admissibility = 'no_compatible_conclusion'
        elif disposition in ('one_compatible', 'multiple_compatible'):
            admissibility = ('conditional' if allowed == 'conditional_use_with_unresolved_conditions'
                             else 'permitted_under_declared_conditions' if allowed == 'use_permitted' else None)
            if admissibility is None:
                _error('CALIBRATION_OUTCOME_MISMATCH')
        else:
            _error('CALIBRATION_OUTCOME_MISMATCH', '/calibration/disposition')
        detail = ('Gate permitted delegation only. Owning disposition: %s. '
                  'Existing applicability restrictions remain; scientific validity and adoption are not established.' % disposition)
    return dict(admissibility=admissibility, owning_disposition=disposition, gate_status=status,
        gate_reasons=finding['reasons'], base_reasons=reasons, assumed_conditions=base['assumed_conditions'],
        explanation_code=status, explanation=detail)


def build_outcome(*, finding, preflight, input_pins, bundle=None,
                  operation='t1-reassessment-evaluate', replay_of=None):
    members = []
    branch = bundle is not None
    prefix = 'bundle/' if branch else 'receipt/'
    paths = [('closure', 'closure.json' if branch else 'admission-closure.json', 'ct.closure.v1', preflight['closure_wire']),
             ('base_applicability', 'applicability.json' if branch else 'base-applicability.json',
              'ct.applicability.v1', canonical_bytes(preflight['applicability'])),
             ('checker_build', 'build.json', 'ct.build.v1', preflight['build_wire'])]
    for role, name, kind, wire in paths:
        if branch and bundle[name] != wire:
            _error('CALIBRATION_OUTCOME_MISMATCH', '/calibration/' + role)
        members.append(dict(role=role, path=prefix + name, kind=kind, sha256=sha(wire), bytes=len(wire)))
    if branch:
        invocation = json.loads(bundle['invocation.json'])
        expected_operation = {'t1-reassessment-evaluate': 'checked-reassessment-evaluate',
                              't1-workflow-replay': 'checked-reassessment-replay'}
        if (invocation['operation'] != expected_operation.get(operation) or
                (invocation['replay_of'] is None) != (replay_of is None)):
            _error('CALIBRATION_OUTCOME_MISMATCH', '/calibration/invocation')
        manifest_wire = bundle['manifest.json']
        members.append(dict(role='owning_manifest', path='bundle/manifest.json', kind='ct.bundle-manifest.v1',
                            sha256=sha(manifest_wire), bytes=len(manifest_wire)))
        delegation = dict(status='completed', owning_manifest=ref('ct.bundle-manifest.v1', manifest_wire),
                          owning_result=ref('ct.reassessment.v1', bundle['result.json']))
        result = json.loads(bundle['result.json'])
    else:
        delegation = dict(status='not_run', owning_manifest=None, owning_result=None)
        result = None
    subject = finding['subjects']
    steps = [('intake', subject['request'], 'admitted'),
             ('source_verified', subject['producer_manifest'], 'reconstructed'),
             ('handoff_checked', subject['handoff'], 'matched'),
             ('owning_admitted', subject['evaluation_authority'], 'admitted'),
             ('base_applicability', finding['base_applicability'], preflight['applicability']['use_disposition']),
             ('qualified', subject['required_claim'], finding['qualification']),
             ('compared', subject['producer_receipt'], str(finding['calibration']['computed_predicate']).lower()),
             ('gated', subject['required_claim'], finding['effect'])]
    if branch:
        steps.append(('owning_completed', delegation['owning_result'], result['disposition']))
    value = dict(_common(OUTCOME), guarantee=GUARANTEE, operation=operation, replay_of=replay_of,
        process_completion='completed', scope='carried_acquisition', correction_release='disabled',
        input_pins=input_pins, producer_build=subject['producer_build'], checker_build=subject['checker_build'],
        finding=finding, members=members, delegation=delegation,
        conclusion=conclusion(finding, preflight['applicability'], result),
        trace=[dict(step=s, target=t, outcome=o) for s, t, o in steps], limitations=LIMITATIONS)
    encode(value)
    return value


def build_check(*, outcome, command, operation_class, published, verified=False):
    checks = ['source_reconstruction', 'prior_validation', 'handoff_joins', 'owning_admission',
              'base_applicability', 'qualification', 'independent_arithmetic', 'calibration_gate', 'package_binding']
    if verified and outcome['delegation']['status'] == 'completed':
        checks.append('owning_full_result_trace_replay_comparison')
    if operation_class in ('completion', 'replay'):
        checks.append('durable_publication')
    result = dict(_common(CHECK), guarantee=GUARANTEE, command=command, operation_class=operation_class,
        subject=ref(OUTCOME, encode(outcome)), replay_origin=outcome['replay_of'] if command == 't1-workflow-replay' else None,
        checker_build=outcome['checker_build'], checks=checks, decision=outcome['conclusion'], limitations=LIMITATIONS,
        published=[dict(path=p, sha256=sha(w), bytes=len(w)) for p, w in sorted(published.items())])
    encode(result)
    return result
