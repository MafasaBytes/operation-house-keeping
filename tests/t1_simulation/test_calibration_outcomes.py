"""W-level complete companion composition; injected development identity only."""
import copy
import json
import pytest
from applications.bounded_decision_workflow import checked_cli, checked_runtime as rt
from applications.bounded_decision_workflow import t1_calibration_gate as gate, t1_workflow as workflow
from applications.bounded_decision_workflow.t1_contracts import SimRefusal, canonical_bytes, sha
from applications.bounded_decision_workflow.checked_contracts import CheckedRefusal
from .calibration_fixtures import scenario, evaluate, preflight_finding, classifier_rows


@pytest.mark.parametrize('beta,expected_effect', [
    ('-0.999999', 'block_counterexample'), ('0', 'permission_to_delegate')])
def test_full_review_fanout_publishes_and_replays(tmp_path, monkeypatch, beta, expected_effect):
    from . import calibration_fixtures as fixtures
    from . import admitted_fixtures
    from functools import partial

    # Bind test inputs before hashing/admission. Both branches use the ordinary
    # policy and closure ceilings and a labelled component build provider.
    monkeypatch.setattr(admitted_fixtures, 'fx1', partial(admitted_fixtures.fx1,
                        b_ref=((-100001, 1000000), (100001, 1000000))))
    original_case = fixtures.admitted_case

    def long_context(**kwargs):
        case = original_case(**kwargs)
        world = case['world']
        context = world.value('C')
        context.update(binding_set_id='b' * 64, interpretation_set_id='i' * 64)
        target = world.value('J')
        target['context'] = world.put(context, 'C')
        world.put(target, 'J')
        fixtures.source_edit(case)
        return case

    monkeypatch.setattr(fixtures, 'admitted_case', long_context)
    expected_refs = []

    def add_reviews(kind, request, world):
        if kind != 'R':
            return
        for original in request['reviews']:
            review = json.loads(world.objects[original['sha256']])
            claim = json.loads(world.objects[review['claim']['sha256']])
            if claim['binding']['condition'] == 'reference_calibration':
                break
        else:
            pytest.fail('missing calibration review in base request')
        item = json.loads(world.objects[review['item']['sha256']])
        for i in range(8):
            item_ref = review['item'] if i == 0 else world.put(dict(item, id=f'fan-item-{i}'))
            expected_refs.append(item_ref)
            if i:
                request['evidence_items'].append(item_ref)
            for j in range(4):
                if (i, j) == (0, 0):
                    expected_refs.append(original)
                else:
                    extra = world.put(dict(review, item=item_ref, id=f'fan-review-{i}-{j}'))
                    expected_refs.append(extra)
                    request['reviews'].append(extra)
        for key in ('evidence_items', 'reviews'):
            request[key].sort(key=lambda rr: rr['sha256'])

    spec = scenario(tmp_path, beta=beta, assessment_policy=True, mutate=add_reviews)
    files = evaluate(spec, tmp_path)
    replay = workflow.replay_calibration_workflow(**spec['inputs'], workflow_files=files,
        workflow_pin=sha(files['workflow-receipt.json']), scratch=tmp_path / 'replay-scratch',
        output=tmp_path / 'replayed')
    for package, operation, stage in ((files, 't1-reassessment-evaluate', 'completion'),
                                      (replay, 't1-workflow-replay', 'replay')):
        wire = package['workflow-receipt.json']
        outcome = fixtures.verify(spec, package, tmp_path, 'verify-' + stage)['outcome']
        assert outcome == json.loads(wire)
        finding = outcome['finding']
        assert finding['effect'] == expected_effect
        assert finding['calibration']['computed_predicate'] is (beta == '0')
        interval = {'lo': {'numerator': '-100001', 'denominator': '1000000'},
                    'hi': {'numerator': '100001', 'denominator': '1000000'}}
        assert finding['calibration']['beta'] == beta
        assert finding['calibration']['b_ref'] == finding['required_claim_core']['binding']['parameters']['b_ref'] == interval
        assert len(expected_refs) == len({rr['sha256'] for rr in expected_refs}) == 40
        assert finding['review_refs'] == sorted(expected_refs, key=lambda rr: (rr['kind'], rr['sha256']))
        assert finding['subjects']['assessment_policy'] == json.loads(spec['supplied'].request_wire)['policy']
        assert finding['subjects']['captured_policy'] == spec['case']['world'].value('J')['captured_policy']
        assert finding['subjects']['assessment_policy'] != finding['subjects']['captured_policy']
        rows = finding['comparisons']
        assert len(rows) == 16
        operands = [op for row in rows for op in row['operands']]
        assert len(operands) == 71
        ids = {op['pointer']: op['normalized_value']['value'] for op in operands
               if op['subject'] == 'context' and op['pointer'].endswith('_set_id')}
        assert ids == {'/binding_set_id': 'b' * 64, '/interpretation_set_id': 'i' * 64}
        assert 18803 < len(gate.encode(finding)) <= 23770
        assert len(wire) <= 32768
        assert outcome['operation'] == operation
        if beta == '0':
            assert outcome['conclusion']['admissibility'] == 'permitted_under_declared_conditions'
            assert json.loads(package['bundle/result.json'])['disposition'] == 'one_compatible'
        else:
            assert outcome['conclusion']['admissibility'] == 'blocked'
            assert outcome['delegation']['status'] == 'not_run'
            assert not any(name.startswith('bundle/') for name in package)
        check = gate.build_check(outcome=outcome, command=operation, operation_class=stage,
                                 published=package, verified=stage == 'replay')
        check_wire = gate.encode(check)
        assert len(check_wire) + 1 <= 65536
        assert gate.parse(check_wire, gate.CHECK)['subject']['sha256'] == sha(wire)
    assert json.loads(replay['workflow-receipt.json'])['replay_of']['sha256'] == sha(files['workflow-receipt.json'])


@pytest.mark.parametrize('relation,base_state', [('support', 'supported'), ('opposition', 'contradicted')])
def test_c01_c02_false_primary_completes_without_owning_assessment(tmp_path, monkeypatch, relation, base_state):
    spec = scenario(tmp_path, beta='10', theta='50', relation=relation)
    def forbidden(*args, **kw):
        raise AssertionError('gate block delegated')
    monkeypatch.setattr(checked_cli, 'execute', forbidden)
    files = evaluate(spec, tmp_path)
    assert set(files) == {'workflow-receipt.json', 'receipt/admission-closure.json',
                         'receipt/base-applicability.json', 'receipt/build.json'}
    outcome = gate.parse(files['workflow-receipt.json'], gate.OUTCOME)
    assert outcome['delegation'] == dict(status='not_run', owning_manifest=None, owning_result=None)
    assert outcome['conclusion']['admissibility'] == 'blocked'
    assert outcome['conclusion']['gate_status'] == 'blocked_calibration_counterexample'
    assert outcome['correction_release'] == 'disabled'
    base = json.loads(files['receipt/base-applicability.json'])
    calibration = next(row for row in base['claims'] if row['condition'] == 'reference_calibration')
    assert calibration['governing_state'] == base_state
    assert ('governing_state_contradicted' in outcome['conclusion']['base_reasons']) == (relation == 'opposition')
    assert not (tmp_path / 'evaluation/bundle').exists()
    assert len(files['workflow-receipt.json']) <= 32768


@pytest.mark.parametrize('relation,disposition,admissibility', [
    ('support', 'one_compatible', 'permitted_under_declared_conditions'),
    ('opposition', 'applicability_blocked', 'blocked')])
def test_c03_c04_positive_only_delegates_and_retains_opposition(tmp_path, relation, disposition, admissibility):
    spec = scenario(tmp_path, relation=relation)
    files = evaluate(spec, tmp_path)
    outcome = gate.parse(files['workflow-receipt.json'], gate.OUTCOME)
    result = json.loads(files['bundle/result.json'])
    assert result['disposition'] == disposition
    assert result['adoption'] == 'derived_not_adopted'
    assert outcome['delegation']['status'] == 'completed'
    assert outcome['conclusion']['admissibility'] == admissibility
    assert outcome['finding']['effect'] == 'permission_to_delegate'
    assert outcome['delegation']['owning_result']['sha256'] == sha(files['bundle/result.json'])


def test_review_finding_distinct_source_and_assessment_policies(tmp_path):
    spec = scenario(tmp_path, assessment_policy=True)
    files = evaluate(spec, tmp_path)
    outcome = gate.parse(files['workflow-receipt.json'], gate.OUTCOME)
    refs = outcome['finding']['subjects']
    assert refs['captured_policy'] != refs['assessment_policy']
    request = json.loads(spec['supplied'].request_wire)
    target = spec['case']['world'].value('J')
    assert refs['captured_policy'] == target['captured_policy']
    assert refs['assessment_policy'] == request['policy']
    assert json.loads(files['bundle/policy.json']) == spec['supplied'].world.value('assessment-policy')
    assert outcome['conclusion']['admissibility'] == 'permitted_under_declared_conditions'


@pytest.mark.parametrize('phase_kw', [
    {'no_review': ('reference_mapping',)}, {'skip': ('reference_calibration',)},
    {'no_item': ('reference_calibration',)}])
def test_c04_c06_positive_does_not_fill_missing_scope_or_evidence(tmp_path, phase_kw):
    spec = scenario(tmp_path, phase_kw=phase_kw)
    files = evaluate(spec, tmp_path)
    assert json.loads(files['bundle/result.json'])['disposition'] == 'applicability_blocked'
    assert gate.parse(files['workflow-receipt.json'], gate.OUTCOME)['finding']['effect'] == 'permission_to_delegate'


def test_c04_conditional_assessment_policy_does_not_get_replaced_by_source_policy(tmp_path):
    spec = scenario(tmp_path, phase_kw={'no_review': ('reference_mapping',)}, assessment_policy='conditional')
    files = evaluate(spec, tmp_path)
    outcome = gate.parse(files['workflow-receipt.json'], gate.OUTCOME)
    assert outcome['conclusion']['admissibility'] == 'conditional'
    assert outcome['conclusion']['assumed_conditions']


def test_c07_source_valid_actual_mapping_difference_completes_gap(tmp_path):
    # A W-level candidate, not a claim of demonstrated native reachability.
    spec = scenario(tmp_path, actual_variable='var_' + '2' * 32)
    files = evaluate(spec, tmp_path)
    outcome = gate.parse(files['workflow-receipt.json'], gate.OUTCOME)
    assert outcome['finding']['qualification'] == 'established_mismatch'
    assert outcome['conclusion']['gate_status'] == 'blocked_calibration_correspondence'
    assert 'actual_measurand_mismatch' in outcome['finding']['reasons']
    assert not any(name.startswith('bundle/') for name in files)


def test_c08_bad_authority_cannot_be_hidden_by_early_counterexample(tmp_path):
    def invalid(kind, value, world):
        if kind == 'A':
            value['valid']['to'] = '2026-10-05T09:00:01Z'
    spec = scenario(tmp_path, beta='10', theta='50', mutate=invalid)
    with pytest.raises(CheckedRefusal) as failure:
        evaluate(spec, tmp_path)
    assert failure.value.code == 'AUTHORITY_SCOPE_MISMATCH'
    assert not (tmp_path / 'evaluation').exists()


def test_c09_risk_and_proposed_correction_prose_do_not_release_failure(tmp_path):
    def prose(kind, value, world):
        if kind == 'R':
            value['provenance']['basis'] = 'risk accepted; correction proposed; reviewer approves'
    spec = scenario(tmp_path, beta='10', theta='50', mutate=prose)
    files = evaluate(spec, tmp_path)
    outcome = gate.parse(files['workflow-receipt.json'], gate.OUTCOME)
    assert outcome['conclusion']['gate_status'] == 'blocked_calibration_counterexample'
    outcome['correction_release'] = 'accepted'
    with pytest.raises(SimRefusal):
        gate.encode(outcome)


def test_c13_no_b_publication_fault_retains_partial_without_terminal(tmp_path, monkeypatch):
    spec = scenario(tmp_path, beta='10', theta='50')
    original = workflow.Publication.write
    def fail(publication, name, wire):
        if name == 'receipt/base-applicability.json':
            raise OSError('injected member write')
        return original(publication, name, wire)
    monkeypatch.setattr(workflow.Publication, 'write', fail)
    with pytest.raises((OSError, SimRefusal)):
        evaluate(spec, tmp_path)
    assert (tmp_path / 'evaluation/PARTIAL').exists()
    assert not (tmp_path / 'evaluation/workflow-receipt.json').exists()
    assert not (tmp_path / 'evaluation/bundle').exists()


def test_c13_output_input_overlap_refused_before_work(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    with pytest.raises(SimRefusal) as failure:
        workflow.require_disjoint_paths([source], [source / 'new-output'])
    assert failure.value.exit_class == 5


def test_c14_true_calibration_does_not_hide_prediction_mismatch(tmp_path):
    spec = scenario(tmp_path, theta='57.5')
    files = evaluate(spec, tmp_path)
    outcome = gate.parse(files['workflow-receipt.json'], gate.OUTCOME)
    assert outcome['finding']['effect'] == 'permission_to_delegate'
    assert outcome['conclusion']['owning_disposition'] == 'model_prediction_mismatch'
    assert outcome['conclusion']['admissibility'] == 'no_compatible_conclusion'


def test_c16_unreferenced_correction_input_refuses_instead_of_disappearing(tmp_path):
    spec = scenario(tmp_path, beta='10', theta='50')
    extra = canonical_bytes({'schema': 'ct.t1-calibration-resolution.v1', 'release': True})
    spec['authority_objects'][sha(extra)] = extra
    with pytest.raises(CheckedRefusal) as failure:
        evaluate(spec, tmp_path)
    assert failure.value.code == 'UNREFERENCED_MEMBER'
    assert not (tmp_path / 'evaluation').exists()


@pytest.mark.parametrize('fault', ['false', 'unknown', 'missing', 'conflicting_reviews', 'partial_review'])
def test_c04_positive_gate_cannot_clear_each_existing_calibration_block(tmp_path, fault):
    def change(kind, request, world):
        if kind != 'R':
            return
        if fault in ('false', 'unknown', 'missing'):
            refs = []
            for rr in request['declarations']:
                declaration = json.loads(world.objects[rr['sha256']])
                claim = json.loads(world.objects[declaration['claim']['sha256']])
                if claim['binding']['condition'] == 'reference_calibration':
                    if fault == 'missing':
                        continue
                    declaration['state'] = fault
                    rr = world.put(declaration)
                refs.append(rr)
            request['declarations'] = sorted(refs, key=lambda rr: rr['sha256'])
        else:
            refs = []
            for rr in request['reviews']:
                review = json.loads(world.objects[rr['sha256']])
                claim = json.loads(world.objects[review['claim']['sha256']])
                if claim['binding']['condition'] == 'reference_calibration':
                    if fault == 'conflicting_reviews':
                        opposed = copy.deepcopy(review)
                        opposed.update(id='second-opposed-review', relation='opposition')
                        refs.append(world.put(opposed))
                    else:
                        review['covers']['to'] = '2026-09-01T00:00:00Z'
                        rr = world.put(review)
                refs.append(rr)
            request['reviews'] = sorted(refs, key=lambda rr: rr['sha256'])
    spec = scenario(tmp_path, mutate=change)
    files = evaluate(spec, tmp_path)
    outcome = gate.parse(files['workflow-receipt.json'], gate.OUTCOME)
    assert outcome['finding']['effect'] == 'permission_to_delegate'
    assert outcome['conclusion']['admissibility'] == 'blocked'
    assert json.loads(files['bundle/result.json'])['disposition'] == 'applicability_blocked'


def test_c09_ordinary_request_predecessor_keeps_same_failed_primary(tmp_path):
    def successor(kind, request, world):
        if kind == 'R':
            predecessor = world.put(copy.deepcopy(request), 'predecessor-request')
            request.update(revision=2, predecessor=predecessor)
    spec = scenario(tmp_path, beta='10', theta='50', mutate=successor)
    files = evaluate(spec, tmp_path)
    closure = json.loads(files['receipt/admission-closure.json'])
    old_request = json.loads(spec['supplied'].request_wire)['predecessor']
    assert any(m['sha256'] == old_request['sha256'] for m in closure['members'])
    assert gate.parse(files['workflow-receipt.json'], gate.OUTCOME)['conclusion']['gate_status'] == 'blocked_calibration_counterexample'


@pytest.mark.parametrize('disposition,admissibility', [
    ('incomplete_assessment', 'unresolved'), ('multiple_compatible', 'permitted_under_declared_conditions')])
def test_c04_projection_preserves_owning_uncertainty_without_new_scientific_calculator(tmp_path, disposition, admissibility):
    # Projection-only C case. This is not a new native baseline/cell specimen.
    spec = scenario(tmp_path)
    ctx = preflight_finding(spec, tmp_path)
    value = gate.conclusion(ctx['finding'], ctx['preflight']['applicability'], {'disposition': disposition})
    assert value['admissibility'] == admissibility
    assert value['owning_disposition'] == disposition


@pytest.mark.parametrize('exclusion', ['instrument', 'validity'])
def test_c05_c06_unrelated_or_stale_ordinary_opposition_does_not_veto_valid_primary(tmp_path, exclusion):
    def extra(kind, request, world):
        if kind != 'R':
            return
        for rr in request['reviews']:
            review = json.loads(world.objects[rr['sha256']])
            claim = json.loads(world.objects[review['claim']['sha256']])
            if claim['binding']['condition'] != 'reference_calibration':
                continue
            item = json.loads(world.objects[review['item']['sha256']])
            item['id'] = 'unrelated-opposition-item'
            if exclusion == 'instrument':
                item['instrument_id'] = 'inst_' + 'b' * 32
            else:
                item['validity'] = {'from': '2026-01-01T00:00:00Z', 'to': '2026-02-01T00:00:00Z'}
            item_ref = world.put(item)
            review.update(id='unrelated-opposition-review', item=item_ref, relation='opposition')
            request['evidence_items'] = sorted(request['evidence_items'] + [item_ref], key=lambda r: r['sha256'])
            request['reviews'] = sorted(request['reviews'] + [world.put(review)], key=lambda r: r['sha256'])
            break
    spec = scenario(tmp_path, mutate=extra)
    files = evaluate(spec, tmp_path)
    outcome = gate.parse(files['workflow-receipt.json'], gate.OUTCOME)
    assert outcome['conclusion']['admissibility'] == 'permitted_under_declared_conditions'
    base = json.loads(files['bundle/applicability.json'])
    row = next(r for r in base['claims'] if r['condition'] == 'reference_calibration')
    assert row['governing_state'] == 'supported'
    assert any(item['status'] == 'excluded_conclusive' for item in row['items'])


@pytest.mark.parametrize('field', ['model', 'instrument'])
def test_c05_wrong_required_carriage_refuses_before_qualification(tmp_path, field):
    def wrong(kind, request, world):
        if kind == 'R':
            if field == 'model':
                model = world.value('model')
                model['id'] = 'another-model'
                request['model'] = world.put(model)
            else:
                request['result']['acquisition']['instrument_id'] = 'inst_' + 'b' * 32
    # This is the native join guard at W level, not a completed mismatch case.
    with pytest.raises(SimRefusal) as denied:
        scenario(tmp_path, mutate=wrong)
    assert denied.value.code == 'HANDOFF_JOIN_MISMATCH'


def test_c09_proposed_correction_content_is_retained_without_release(tmp_path):
    import base64
    proposal = b'Proposed correction only; linked source is not released or rewritten.'
    def extra(kind, request, world):
        if kind != 'R':
            return
        for rr in request['reviews']:
            review = json.loads(world.objects[rr['sha256']])
            claim = json.loads(world.objects[review['claim']['sha256']])
            if claim['binding']['condition'] == 'reference_calibration':
                item = json.loads(world.objects[review['item']['sha256']])
                item.update(id='proposal-item', content=world.put(proposal))
                item_ref = world.put(item)
                review.update(id='proposal-review', item=item_ref)
                request['evidence_items'] = sorted(request['evidence_items'] + [item_ref], key=lambda r: r['sha256'])
                request['reviews'] = sorted(request['reviews'] + [world.put(review)], key=lambda r: r['sha256'])
                break
    spec = scenario(tmp_path, beta='10', theta='50', mutate=extra)
    files = evaluate(spec, tmp_path)
    closure = json.loads(files['receipt/admission-closure.json'])
    assert any(m['kind'] == 'ct.evidence-content' and base64.b64decode(m['data']) == proposal
               for m in closure['members'])
    value = gate.parse(files['workflow-receipt.json'], gate.OUTCOME)
    assert value['correction_release'] == 'disabled'
    assert value['conclusion']['gate_status'] == 'blocked_calibration_counterexample'


def test_c01_c02_both_review_arms_share_the_exact_carried_acquisition(tmp_path):
    supported = scenario(tmp_path, beta='10', theta='50')
    support_files = evaluate(supported, tmp_path)
    second = tmp_path / 'opposed'
    second.mkdir()
    opposed = scenario(second, beta='10', theta='50', relation='opposition', carried=supported)
    opposition_files = evaluate(opposed, second)
    assert supported['producer'] == opposed['producer']
    assert supported['inputs']['manifest_pin'] == opposed['inputs']['manifest_pin']
    assert supported['inputs']['request_pin'] != opposed['inputs']['request_pin']
    assert supported['inputs']['authority_pin'] != opposed['inputs']['authority_pin']
    for files in (support_files, opposition_files):
        assert gate.parse(files['workflow-receipt.json'], gate.OUTCOME)['conclusion']['gate_status'] == 'blocked_calibration_counterexample'
