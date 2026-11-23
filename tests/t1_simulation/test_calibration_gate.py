"""C-level classification/contracts. No native-provider evidence is claimed."""
import copy
import json
import pytest

from applications.bounded_decision_workflow import t1_calibration_gate as gate
from applications.bounded_decision_workflow.t1_contracts import SimRefusal, canonical_bytes
from .calibration_fixtures import classifier_rows, scenario, preflight_finding

# Independently specified single-condition exclusions: not reachable malformed
# primary carriage presented as successful native qualification.
@pytest.mark.parametrize('group,reason', [('instrument', 'instrument_mismatch'),
    ('model_claim_bound', 'model_mismatch'), ('model_claim_bound', 'claim_or_bound_mismatch'),
    ('effective_binding', 'anchor_mismatch'), ('intended_actual', 'actual_measurand_mismatch')])
def test_c05_required_unrelated_source_leaves_gap(group, reason):
    rows = classifier_rows()
    row = next(r for r in rows if r['group'] == group)
    row.update(status='different', reason=reason)
    found = gate.decide(rows, False)
    assert found == dict(qualification='established_mismatch', effect='block_required_correspondence',
                        reasons=sorted([reason, 'required_primary_match_missing']))


@pytest.mark.parametrize('predicate', [False, True])
def test_c07_unknown_cannot_become_permission(predicate):
    rows = classifier_rows()
    rows[11].update(status='unknown', reason='effective_scope_unknown')
    assert gate.decide(rows, predicate) == dict(qualification='insufficient_information',
        effect='block_required_correspondence', reasons=['correspondence_unresolved', 'effective_scope_unknown'])


@pytest.mark.parametrize('predicate,effect,reason', [
    (False, 'block_counterexample', 'calibration_premise_counterexample'),
    (True, 'permission_to_delegate', 'no_counterexample_from_this_check')])
def test_c01_c03_predicate_only_applies_after_complete_qualification(predicate, effect, reason):
    assert gate.decide(classifier_rows(), predicate) == dict(
        qualification='qualified_match', effect=effect, reasons=[reason])


def test_c05_exclusion_does_not_turn_other_unknown_links_into_matches():
    rows = classifier_rows()
    rows[6].update(status='different', reason='instrument_mismatch')
    rows[11].update(status='unknown', reason='effective_scope_unknown')
    actual = gate.decide(rows, True)
    assert actual['qualification'] == 'established_mismatch'
    assert actual['effect'] == 'block_required_correspondence'
    assert actual['reasons'] == ['effective_scope_unknown', 'instrument_mismatch', 'required_primary_match_missing']


REQUIRED = {'from': '2026-08-07T20:30:00Z', 'to': '2026-10-05T09:02:00Z'}
WINDOW = {'from': '2026-10-05T09:00:00Z', 'to': '2026-10-05T09:02:00Z'}


@pytest.mark.parametrize('witness,supported,expected', [
    ('2026-08-07T20:30:00Z', REQUIRED, 'equal'),
    ('2026-10-05T09:02:00Z', WINDOW, 'equal'),
    ('2026-08-07T20:29:59Z', REQUIRED, 'different'),
    ('2026-10-05T09:02:01Z', WINDOW, 'different'),
    (None, WINDOW, 'unknown')])
def test_c06_closed_interval_witness_not_publication_recency(witness, supported, expected):
    assert gate.time_status(REQUIRED, supported, witness) == expected


@pytest.mark.parametrize('end,expected', [
    ({'kind': 'declared', 'at': '2026-10-05T09:02:00Z'}, 'different'),
    ({'kind': 'declared', 'at': '2026-10-05T09:02:01Z'}, 'equal'),
    ({'kind': 'unknown'}, 'unknown'),
    ({'kind': 'unbounded'}, 'equal')])
def test_c06_c07_half_open_full_window_scope(end, expected):
    scope = dict(axis='ingestion_received_at', interval_semantics='half_open',
                 start_boundary={'kind': 'unbounded'}, end_boundary=end)
    assert gate.scope_status(scope, WINDOW, '2026-10-05T09:00:08Z') == expected


def test_c06_conclusive_temporal_exclusion_survives_other_unknown_boundary():
    scope = dict(axis='ingestion_received_at', interval_semantics='half_open',
                 start_boundary={'kind': 'unknown'},
                 end_boundary={'kind': 'declared', 'at': '2026-10-05T08:00:00Z'})
    assert gate.scope_status(scope, WINDOW, '2026-10-05T09:00:08Z') == 'different'


def test_c06_disclosed_inactive_or_redundant_unknown_assertions_do_not_veto_known_basis():
    from types import SimpleNamespace
    class Scope:
        def __init__(self, end):
            self.value = dict(axis='ingestion_received_at', interval_semantics='half_open',
                              start_boundary={'kind': 'unbounded'}, end_boundary=end)
        def model_dump(self, *, mode):
            return self.value
    current = Scope({'kind': 'declared', 'at': '2026-10-05T10:00:00Z'})
    old = Scope({'kind': 'declared', 'at': '2026-10-05T08:00:00Z'})
    unknown = Scope({'kind': 'unknown'})
    def summary(identity, scope, active, membership):
        return dict(record_id=identity, target_anchor_id='var_A', active=active,
                    membership_at=membership, effective_applies=scope.value)
    known = summary('current', current, True, 'in')
    resolution = dict(resolved_target={'anchor_id': 'var_A'}, via_assertions=[known,
        summary('old', old, False, 'out'), summary('unknown', unknown, True, 'unknown')])
    collection = SimpleNamespace(effective_applies={'current': current, 'old': old, 'unknown': unknown})
    assert gate.effective_status(resolution, collection, WINDOW, '2026-10-05T09:00:08Z') == 'equal'
    resolution['via_assertions'] = resolution['via_assertions'][1:]
    assert gate.effective_status(resolution, collection, WINDOW, '2026-10-05T09:00:08Z') == 'unknown'


@pytest.mark.parametrize('wire', [b'{"schema":1,"schema":2}', b'{"number":1.0}', b'{"number":NaN}'])
def test_c08_closed_canonical_parser_rejects_ambiguous_numbers_or_keys(wire):
    with pytest.raises(SimRefusal):
        gate.parse(wire, gate.FINDING)


def test_c01_c07_complete_graph_qualifies_despite_null_item_and_source_unit(tmp_path):
    spec = scenario(tmp_path, beta='10', theta='50')
    ctx = preflight_finding(spec, tmp_path)
    finding = ctx['finding']
    assert finding['qualification'] == 'qualified_match'
    assert finding['calibration'] == dict(beta='10', b_ref={'lo': {'numerator': '0', 'denominator': '1'},
        'hi': {'numerator': '0', 'denominator': '1'}}, predicate='beta_in_closed_b_ref',
        declared_predicate=False, computed_predicate=False)
    assert finding['effect'] == 'block_counterexample'
    assert [row['group'] for row in finding['comparisons']] == [row['group'] for row in classifier_rows()]
    assert len(gate.encode(finding)) == 18803
    assert sum(len(r['operands']) for r in finding['comparisons']) <= 128
    owner = ctx['preflight']['admitted']
    assert all(item['instrument_id'] is None and item['validity'] is None
               for _ref, item in owner.supplied['evidence_items'])


def test_c08_declared_diagnostic_is_not_the_recomputation(tmp_path):
    spec = scenario(tmp_path, beta='10', theta='50')
    ctx = preflight_finding(spec, tmp_path)
    verified = copy.deepcopy(ctx['verified'])
    verified['receipt']['diagnostics']['reference_calibration']['beta_in_b_ref'] = True
    with pytest.raises(SimRefusal) as refused:
        gate.qualify_carried_calibration(verified=verified, producer_files=spec['producer'],
            handoff_wire=spec['handoff']['handoff.json'], request_wire=spec['supplied'].request_wire,
            preflight=ctx['preflight'])
    assert refused.value.code == 'SIM_DERIVATION_MISMATCH'


@pytest.mark.parametrize('kind,limit', [(gate.FINDING, 23770), (gate.OUTCOME, 32768),
                                       (gate.CHECK, 65536)])
def test_c13_record_cap_is_hard_not_evidence_truncation(kind, limit):
    # Exact-cap payload is intentionally not a valid scientific record.
    with pytest.raises(SimRefusal) as boundary:
        gate.parse(b' ' * limit, kind)
    assert boundary.value.exit_class == 3
    with pytest.raises(SimRefusal) as over:
        gate.parse(b' ' * (limit + 1), kind)
    assert (over.value.exit_class, over.value.target) == (4, '/calibration/record')


def _wire(record):
    return json.dumps(record, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def test_successor_wire_boundaries_include_escaped_utf8_and_inline_finding(tmp_path):
    from .calibration_fixtures import evaluate
    spec = scenario(tmp_path, beta='10', theta='50')
    outcome = json.loads(evaluate(spec, tmp_path)['workflow-receipt.json'])
    finding = outcome['finding']
    operands = [op for row in finding['comparisons'] for op in row['operands']]
    # Parser specimens. Invented locators cannot stand in for a rebuilt ledger.
    operands[0]['pointer'] += '/é"'
    needed = 23770 - len(_wire(finding))
    assert needed > 0
    for op in operands[:-1]:
        count = min(needed, 768 - len(op['pointer']))
        op['pointer'] += 'x' * count
        needed -= count
        if not needed:
            break
    wire = _wire(finding)
    assert len(wire) == 23770
    assert gate.encode(finding) == wire
    assert gate.parse(wire, gate.FINDING) == finding
    assert gate.parse(_wire(outcome), gate.OUTCOME) == outcome
    operands[-1]['pointer'] += 'x'
    assert len(_wire(finding)) == 23771
    assert len(_wire(outcome)) < 32768
    for record in (finding, outcome):
        for operation in (lambda: gate.encode(record),
                          lambda: gate.parse(_wire(record), record['schema'])):
            with pytest.raises(SimRefusal) as denied:
                operation()
            assert (denied.value.code, denied.value.target, denied.value.exit_class) == (
                'SIM_RESOURCE_LIMIT', '/calibration/record', 4)

    operands[-1]['pointer'] = operands[-1]['pointer'][:-1]
    # Vary only the wrapper, keeping the exact-limit inline finding intact.
    outcome['conclusion']['explanation'] = ''
    gap = 32768 - len(_wire(outcome))
    count, remainder = divmod(gap, 6)  # JSON spells each NUL as six ASCII bytes
    outcome['conclusion']['explanation'] = '\x00' * count + 'a' * remainder
    assert len(outcome['conclusion']['explanation']) < 2048
    assert len(_wire(outcome)) == 32768
    assert gate.encode(outcome) == _wire(outcome)
    outcome['conclusion']['explanation'] += 'x'
    with pytest.raises(SimRefusal) as denied:
        gate.encode(outcome)
    assert (denied.value.target, denied.value.exit_class) == ('/calibration/record', 4)


def test_successor_pack_and_edition_bind_all_three_kinds(tmp_path):
    from .calibration_fixtures import evaluate
    current = 'ct.t1-calibration-primary-gate.v2'
    digest = '81126f8f63cd6ef5ff4bd3046e814d0a1a1d51680828522ace8ad3910aa25a39'
    old = 'ct.t1-calibration-primary-gate.v1'
    old_digest = 'f7f8fce1b85fa6343a2116586039c6f62acb40f35f0babaa9f4c0ef04d0f3b5e'
    files = evaluate(scenario(tmp_path), tmp_path)
    outcome = json.loads(files['workflow-receipt.json'])
    check = gate.build_check(outcome=outcome, command='t1-reassessment-evaluate',
                             operation_class='completion', published=files)
    assert len(_wire(check)) < 16384
    for record in (outcome, outcome['finding'], check):
        assert (record['rule_edition'], record['schemas_sha256']) == (current, digest)
        for rule, pack in ((old, old_digest), (old, digest), (current, old_digest),
                           ('ct.t1-calibration-primary-gate.v3', digest), (current, '0' * 64)):
            forged = dict(record, rule_edition=rule, schemas_sha256=pack)
            with pytest.raises(SimRefusal) as denied:
                gate.parse(_wire(forged), forged['schema'])
            assert denied.value.exit_class != 4
    for rule, pack in ((old, digest), (current, old_digest)):
        outcome['finding'].update(rule_edition=rule, schemas_sha256=pack)
        with pytest.raises(SimRefusal):
            gate.parse(_wire(outcome), gate.OUTCOME)
    # Small, wire-only finding. Prove the historical pair refuses on edition,
    # even when its bytes would fit the original resource budget.
    small = outcome['finding']
    for row in small['comparisons']:
        row['operands'] = row['operands'][:1]
    small.update(rule_edition=current, schemas_sha256=digest)
    assert len(gate.encode(small)) < 16384
    small.update(rule_edition=old, schemas_sha256=old_digest)
    with pytest.raises(SimRefusal) as denied:
        gate.parse(_wire(small), gate.FINDING)
    assert denied.value.code == 'SIM_SCHEMA_INVALID'


@pytest.mark.parametrize('record_size,status', [(65535, 0), (65536, 4), (65537, 4)])
def test_completion_stdout_counts_newline(monkeypatch, record_size, status):
    from applications.bounded_decision_workflow import checked_cli, t1_cli
    # Transport-only control. No command, provider or scientific check is run.
    record = {'pad': ''}
    record['pad'] = 'x' * (record_size - len(_wire(record)))
    assert len(_wire(record)) == record_size
    emitted = []
    monkeypatch.setattr(t1_cli, 'ExecutableBuild', object)
    monkeypatch.setattr(t1_cli, 'execute', lambda args, build: record)
    monkeypatch.setattr(checked_cli, '_emit', lambda fd, wire: emitted.append((fd, wire)))
    assert t1_cli.main(_argv('t1-reassessment-evaluate')) == status
    if status == 0:
        assert emitted == [(1, _wire(record) + b'\n')]
    else:
        (fd, wire), = emitted
        assert fd == 2
        assert json.loads(wire)['target'] == '/completion'


def test_c09_no_correction_release_field_in_finding(tmp_path):
    spec = scenario(tmp_path, beta='10', theta='50')
    finding = preflight_finding(spec, tmp_path)['finding']
    finding['correction_release'] = 'accepted'
    with pytest.raises(SimRefusal):
        gate.encode(finding)


def _argv(operation):
    flags = {'expected-target-pin': 'a' * 64, 'expected-execution-authority-pin': 'b' * 64,
        'expected-permission-pin': 'c' * 64, 'expected-prior-request-pin': 'd' * 64,
        'expected-prior-authority-pin': 'e' * 64, 'prior-bundle': 'prior', 'output-dir': 'out',
        'producer-package': 'producer', 'expected-producer-manifest-pin': 'f' * 64,
        'scratch-dir': 'scratch', 'handoff-package': 'handoff', 'expected-handoff-pin': '1' * 64,
        'expected-request-pin': '2' * 64, 'expected-authority-pin': '3' * 64}
    if operation == 't1-reassessment-evaluate':
        flags['objects-dir'] = 'objects'
    else:
        flags.update({'expected-workflow-receipt-pin': '4' * 64, 'workflow-package': 'workflow'})
    return [operation] + [token for key, value in flags.items() for token in ('--' + key, value)]


def test_c15_no_legacy_or_correction_bypass_flag():
    from applications.bounded_decision_workflow import t1_cli
    argv = _argv('t1-reassessment-evaluate')
    assert t1_cli.arguments(argv).operation == 't1-reassessment-evaluate'
    for flag in ('--skip-gate', '--legacy-evaluate', '--correction-release'):
        with pytest.raises(SimRefusal) as denied:
            t1_cli.arguments(argv + [flag])
        assert denied.value.exit_class == 2


def test_c15_verification_forms_are_explicit_and_exclusive():
    from applications.bounded_decision_workflow import t1_cli
    argv = _argv('t1-workflow-verify')
    assert t1_cli.arguments(argv).workflow_package == 'workflow'
    with pytest.raises(SimRefusal) as denied:
        t1_cli.arguments(argv + ['--bundle', 'B'])
    assert denied.value.exit_class == 2


def test_c15_completion_kind_cannot_mislabel_an_evaluation_as_replay(tmp_path):
    from .calibration_fixtures import evaluate
    spec = scenario(tmp_path, beta='10', theta='50')
    files = evaluate(spec, tmp_path)
    outcome = gate.parse(files['workflow-receipt.json'], gate.OUTCOME)
    record = gate.build_check(outcome=outcome, command='t1-reassessment-evaluate',
                              operation_class='completion', published=files)
    record['operation_class'] = 'replay'
    with pytest.raises(SimRefusal):
        gate.encode(record)


@pytest.mark.parametrize('beta,theta,effect', [('10', '50', 'block_counterexample'),
                                               ('0', '60.1', 'permission_to_delegate')])
def test_candidate_and_occurrence_locator_ledger(tmp_path, beta, theta, effect):
    from hashlib import sha256
    from .calibration_fixtures import evaluate
    spec = scenario(tmp_path, beta=beta, theta=theta)
    finding = json.loads(evaluate(spec, tmp_path)['workflow-receipt.json'])['finding']
    observation = json.loads(spec['producer']['evidence/public/evidence.json'])
    binding = observation['binding']
    i, j = binding['constraint_evaluation_index'], binding['semantic_candidate_index']
    prefix = f'/snapshot/constraint_evaluations/{i}/semantic_compatibility/candidates/{j}'
    indexed = [op['pointer'] for row in finding['comparisons'] for op in row['operands']
               if op['pointer'].startswith('/snapshot/constraint_evaluations/')]
    assert len(indexed) == 8
    assert all(p == prefix or p.startswith(prefix + '/') for p in indexed)
    # Upper-width wire control, independent of whether six-digit indices can
    # occur in this acquisition. Keep the real candidate checks below.
    wide = copy.deepcopy(finding)
    for row in wide['comparisons']:
        for op in row['operands']:
            if op['pointer'] in indexed:
                op['pointer'] = op['pointer'].replace(prefix,
                    '/snapshot/constraint_evaluations/131071/semantic_compatibility/candidates/131071', 1)
    assert 0 <= len(gate.encode(wide)) - len(gate.encode(finding)) <= 80
    state_path = (f'/snapshot/constraint_evaluations/{i}/semantic_compatibility/candidates/{j}'
                  '/value_candidate/state_candidate')
    occurrence_path = state_path + '/bound/observed/occurrence'
    row = next(r for r in finding['comparisons'] if r['group'] == 'source_configuration')
    assert row['status'] == 'equal' and finding['effect'] == effect
    groups = {r['group']: r['operands'] for r in finding['comparisons']}
    def operand(group, subject, pointer):
        return next(x['normalized_value'] for x in groups[group]
                    if (x['subject'], x['pointer']) == (subject, pointer))
    request = spec['supplied'].request
    assert operand('model_claim_bound', 'execution_target', '/model') == dict(kind='ref', value=request['model'])
    instrument = dict(kind='text', value=request['result']['acquisition']['instrument_id'])
    assert operand('instrument', 'required_claim', '/binding/parameters/instrument_id') == instrument
    assert operand('instrument', 'world', '/instrument_id') == instrument
    for key in ('variable_anchor_id', 'subject_entity_anchor_id'):
        assert operand('intended_actual', 'required_claim', '/' + key) == dict(kind='text', value=binding[key])
    operands = {x['pointer']: x['normalized_value'] for x in row['operands']
                if x['subject'] == 'public_evidence'}
    assert set(operands) == {base + '/' + key for base in (state_path, occurrence_path)
                            for key in ('subject', 'property')}
    for pointer, normalized in operands.items():
        value = observation
        for key in pointer.split('/')[1:]:
            value = value[int(key)] if isinstance(value, list) else value[key]
        assert value == spec['receipt']['reading_locator'][pointer.rsplit('/', 1)[1]]
        assert normalized == dict(kind='canonical_object_digest', value=sha256(canonical_bytes(value)).hexdigest())


def test_missing_candidate_locator_cannot_use_occurrence_as_fallback(tmp_path):
    # Isolate the join after admission. A real substituted O also fails reconstruction.
    spec = scenario(tmp_path)
    ctx = preflight_finding(spec, tmp_path)
    path = 'evidence/public/evidence.json'
    observation = json.loads(spec['producer'][path])
    b = observation['binding']
    evaluation = observation['snapshot']['constraint_evaluations'][b['constraint_evaluation_index']]
    candidate = evaluation['semantic_compatibility']['candidates'][b['semantic_candidate_index']]
    del candidate['value_candidate']['state_candidate']['property']
    altered = canonical_bytes(observation)
    verified = dict(ctx['verified'], reconstructed=dict(ctx['verified']['reconstructed'], public_evidence=altered))
    with pytest.raises(SimRefusal) as failure:
        gate.qualify_carried_calibration(verified=verified, producer_files=dict(spec['producer'], **{path: altered}),
            handoff_wire=spec['handoff']['handoff.json'], request_wire=spec['supplied'].request_wire,
            preflight=ctx['preflight'])
    assert (failure.value.code, failure.value.target) == ('SIM_REFERENCE_INVALID', '/calibration/reading_locator')


def test_individually_permitted_measurements_must_agree(tmp_path, monkeypatch):
    from tests.checked_temperature.fixtures import TestDoubleBuild
    from applications.bounded_decision_workflow import checked_runtime
    from .calibration_fixtures import evaluate
    other = TestDoubleBuild(marker='2')
    def assessment_only(kind, value, world):
        if kind == 'R':
            policy = world.value('policy')
            policy.update(id='assessment-only', permitted_builds=[other.digest])
            value['policy'] = world.put(policy)
    spec = scenario(tmp_path, beta='10', theta='50', mutate=assessment_only)
    ordinary_preflight = checked_runtime.preflight_reassessment
    def second_measurement(**args):
        args['build'] = other
        return ordinary_preflight(**args)
    monkeypatch.setattr(checked_runtime, 'preflight_reassessment', second_measurement)
    with pytest.raises(SimRefusal) as failure:
        evaluate(spec, tmp_path)
    assert (failure.value.code, failure.value.target) == ('SIM_EDITION_NOT_PERMITTED', '/calibration/checker_build')
    assert not (tmp_path / 'evaluation').exists()
