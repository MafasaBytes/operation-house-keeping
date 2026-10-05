"""Design §5 aggregation twins (AG1-AG14) and declaration states (DC1-DC3).

Pure unit tests of `checked_applicability.assess` over one calibration claim at
selection phase with an explicit empty allowlist unless a case names A1.
"""
from datetime import datetime, timezone
import pytest
from applications.bounded_decision_workflow import checked_applicability as ap
from applications.bounded_decision_workflow.checked_contracts import EDITION_LIMITS, canonical_bytes, sha
from tests.checked_temperature.fixtures import A1_ALLOWLIST, CONTEXT, PROFILE, WIDE, prov, r

SCOPE = (datetime(2026, 8, 7, 20, 30, tzinfo=timezone.utc), datetime(2026, 10, 4, 12, 0, tzinfo=timezone.utc))
CLAIM = {'schema': 'ct.claim.v1', 'profile': PROFILE, 'catalogue': 'ct.conditions.v2',
         'procedure_edition': 'ct.procedure.T1.v1', 'phase': 'selection',
         'model': {'kind': 'ct.model.v1', 'sha256': 'f' * 64},
         'subject_entity_anchor_id': CONTEXT['subject_entity_anchor_id'],
         'variable_anchor_id': CONTEXT['variable_anchor_id'],
         'binding': {'condition': 'reference_calibration',
                     'parameters': {'instrument_id': 'inst_' + 'a' * 32, 'b_ref': {'lo': r(0), 'hi': r(0)}}}}
CLAIM_REF = {'kind': 'ct.claim.v1', 'sha256': sha(canonical_bytes(CLAIM))}
EXPIRED = {'from': '2025-01-01T00:00:00Z', 'to': '2025-12-31T00:00:00Z'}
PARTIAL = {'from': '2026-09-01T00:00:00Z', 'to': '2026-12-31T00:00:00Z'}


def _ref(kind, value):
    return {'kind': kind, 'sha256': sha(canonical_bytes(value))}


def item(tag, validity=None, **kw):
    v = {'schema': 'ct.evidence-item.v1', 'profile': PROFILE, 'id': 'item-' + tag, 'revision': 1,
         'predecessor': None, 'provenance': prov('local_evidence_reviewer'), 'claims': [CLAIM_REF],
         'content': {'kind': 'ct.evidence-content', 'sha256': sha(tag.encode())}, 'validity': validity,
         'subject_entity_anchor_id': None, 'variable_anchor_id': None, 'instrument_id': None}
    v.update(kw)
    return _ref('ct.evidence-item.v1', v), v


def review(tag, item_ref, relevance='relevant', relation='support', completion='completed', covers=WIDE):
    v = {'schema': 'ct.evidence-review.v1', 'profile': PROFILE, 'id': 'review-' + tag, 'revision': 1,
         'predecessor': None, 'provenance': prov('local_evidence_reviewer'), 'item': item_ref, 'claim': CLAIM_REF,
         'completion': completion, 'relevance': relevance, 'relation': relation, 'rationale': '', 'covers': covers}
    return _ref('ct.evidence-review.v1', v), v


def decl(tag, state='true', covers=WIDE):
    v = {'schema': 'ct.condition-declaration.v1', 'profile': PROFILE, 'id': 'decl-' + tag, 'revision': 1,
         'predecessor': None, 'provenance': prov('local_condition_declarer'), 'claim': CLAIM_REF, 'state': state,
         'rationale': '', 'covers': covers}
    return _ref('ct.condition-declaration.v1', v), v


def assess(items=(), reviews=(), decls=None, allowlist=(), required_reviews=1):
    decls = [decl('d')] if decls is None else decls
    policy = {'unresolved_allowlist': list(allowlist), 'required_reviews_per_item': required_reviews}
    out = ap.assess(request_ref={'kind': 'ct.request.v1', 'sha256': '1' * 64},
                    policy_ref={'kind': 'ct.policy.v1', 'sha256': '2' * 64},
                    build_ref={'kind': 'ct.build.v1', 'sha256': '3' * 64}, phase='selection', scope=SCOPE,
                    required=[CLAIM], supplied={'claims': [(CLAIM_REF, CLAIM)], 'declarations': list(decls),
                                                'evidence_items': list(items), 'reviews': list(reviews)},
                    policy=policy, limits=EDITION_LIMITS)
    return out, out['claims'][0]


def axes(row):
    return row['reviewed_relation'], row['review_completeness'], row['governing_state']


A = item('A')
B = item('B')


def test_ag1_one_completed_support():
    out, row = assess([A], [review('a', A[0])])
    assert axes(row) == ('support_only', 'complete', 'supported') and row['use_effect'] == 'permitted'
    assert out['use_disposition'] == 'use_permitted'


def test_ag2_support_plus_unreviewed_attachment_blocks_under_empty_allowlist():
    out, row = assess([A, B], [review('a', A[0])])
    assert axes(row) == ('support_only', 'pending', 'unresolved')
    assert row['block_reasons'] == ['unresolved_not_permitted'] and out['use_disposition'] == 'blocked'
    b = [i for i in row['items'] if i['item'] == B[0]][0]
    assert b['status'] == 'pending' and b['pending_reasons'] == ['unreviewed']
    assert out['pending_items'] == [B[0]]


def test_ag3_same_graph_with_a1_allowlist_is_conditional():
    out, row = assess([A, B], [review('a', A[0])], allowlist=A1_ALLOWLIST)
    assert axes(row) == ('support_only', 'pending', 'unresolved') and row['policy_permits_unresolved'] is True
    assert out['use_disposition'] == 'conditional_use_with_unresolved_conditions'
    assert out['assumed_conditions'] == [CLAIM_REF] and out['pending_items'] == [B[0]]


def test_ag4_opposition_plus_pending_is_contradicted_regardless_of_allowlist():
    out, row = assess([A, B], [review('a', A[0], relation='opposition')], allowlist=A1_ALLOWLIST)
    assert axes(row) == ('opposition_only', 'pending', 'contradicted')
    assert row['block_reasons'] == ['governing_state_contradicted'] and out['use_disposition'] == 'blocked'


def test_ag5_support_opposition_pending_is_conflicting_regardless_of_allowlist():
    C = item('C')
    out, row = assess([A, B, C], [review('a', A[0]), review('b', B[0], relation='opposition')],
                      allowlist=A1_ALLOWLIST)
    assert axes(row) == ('support_and_opposition', 'pending', 'conflicting')
    assert row['block_reasons'] == ['governing_state_conflicting']


def test_ag6_irrelevant_does_not_suppress_unresolved_relevance():
    out, row = assess([A, B], [review('a', A[0]), review('b1', B[0], relevance='irrelevant', relation='not_applicable'),
                               review('b2', B[0], relevance='unresolved', relation='unresolved')])
    assert axes(row) == ('support_only', 'pending', 'unresolved')
    b = [i for i in row['items'] if i['item'] == B[0]][0]
    assert 'irrelevant_with_unresolved' in b['pending_reasons'] and b['status'] == 'pending'


def test_ag7_same_item_relevant_support_plus_irrelevant_is_disputed():
    out, row = assess([A], [review('a', A[0]), review('a2', A[0], relevance='irrelevant', relation='not_applicable')])
    assert axes(row) == ('support_only', 'pending', 'unresolved')
    assert row['items'][0]['pending_reasons'] == ['disputed_relevance']
    assert row['items'][0]['contributions'] == ['support']


def test_ag8_same_item_relevant_opposition_plus_irrelevant_stays_contradicted():
    out, row = assess([A], [review('a', A[0], relation='opposition'),
                            review('a2', A[0], relevance='irrelevant', relation='not_applicable')])
    assert axes(row) == ('opposition_only', 'pending', 'contradicted')


def test_ag9_unopposed_completed_irrelevant_is_reviewed_exclusion():
    out, row = assess([A, B], [review('a', A[0]), review('b', B[0], relevance='irrelevant', relation='not_applicable')])
    assert axes(row) == ('support_only', 'complete', 'supported')
    b = [i for i in row['items'] if i['item'] == B[0]][0]
    assert (b['status'], b['exclusion_basis']) == ('excluded_reviewed', 'reviewed_irrelevant_unanimous')
    assert b['reviews']   # retained


def test_ag10_validity_outside_scope_is_conclusive_exclusion():
    Bx = item('B', validity=EXPIRED)
    out, row = assess([A, Bx], [review('a', A[0]), review('b', Bx[0], relevance='unresolved',
                                                           relation='unresolved')])
    assert axes(row) == ('support_only', 'complete', 'supported')
    b = [i for i in row['items'] if i['item'] == Bx[0]][0]
    assert (b['status'], b['exclusion_basis']) == ('excluded_conclusive', 'validity_non_overlapping')
    assert b['reviews']   # unresolved review retained historically


def test_ag11_partial_validity_overlap_stays_pending():
    Bp = item('B', validity=PARTIAL)
    out, row = assess([A, Bp], [review('a', A[0]), review('b', Bp[0], covers=PARTIAL)])
    assert axes(row) == ('support_only', 'pending', 'unresolved')
    b = [i for i in row['items'] if i['item'] == Bp[0]][0]
    assert b['pending_reasons'] == ['partial_or_unknown_scope']


def test_ag12_only_expired_support_is_none_complete_unresolved():
    Ax = item('A', validity=EXPIRED)
    out, row = assess([Ax], [review('a', Ax[0])])
    assert axes(row) == ('none', 'complete', 'unresolved') and out['use_disposition'] == 'blocked'


def test_ag13_sole_completed_unresolved_relation():
    out, row = assess([A], [review('a', A[0], relation='unresolved')])
    assert axes(row) == ('none', 'pending', 'unresolved')
    assert row['items'][0]['pending_reasons'] == ['unresolved_relation']


def test_ag14_same_item_support_opposition_irrelevant_is_conflicting():
    out, row = assess([A], [review('a', A[0]), review('a2', A[0], relation='opposition'),
                            review('a3', A[0], relevance='irrelevant', relation='not_applicable')])
    assert axes(row) == ('support_and_opposition', 'pending', 'conflicting')


def test_review_covers_disjoint_is_never_an_applicable_opposition():
    out, row = assess([A], [review('a', A[0]), review('old', A[0], relation='opposition', covers=EXPIRED)])
    assert axes(row) == ('support_only', 'complete', 'supported')
    assert row['inapplicable'] == [{'record': review('old', A[0], relation='opposition', covers=EXPIRED)[0],
                                    'reason': 'covers_disjoint'}]


def test_missing_required_review_is_pending():
    out, row = assess([A], [review('a', A[0])], required_reviews=2)
    assert row['items'][0]['pending_reasons'] == ['missing_required_review']


def test_dc1_conflicting_declarations_block_and_are_retained():
    d1, d2 = decl('t', 'true'), decl('f', 'false')
    out, row = assess([A], [review('a', A[0])], decls=[d1, d2])
    assert row['declaration_state'] == 'conflicting' and row['block_reasons'] == ['conflicting_declarations']
    assert sorted(row['declarations'], key=lambda x: x['sha256']) == sorted([d1[0], d2[0]], key=lambda x: x['sha256'])


def test_dc2_undeclared_claim_blocks():
    out, row = assess([A], [review('a', A[0])], decls=[])
    assert row['declaration_state'] == 'missing' and row['block_reasons'] == ['declaration_missing']


def test_dc3_declared_true_never_erases_reviewed_opposition():
    out, row = assess([A], [review('a', A[0], relation='opposition')], allowlist=A1_ALLOWLIST)
    assert row['declaration_state'] == 'true' and row['governing_state'] == 'contradicted'
    assert out['use_disposition'] == 'blocked'


@pytest.mark.parametrize('covers,reason', [(PARTIAL, 'declaration_covers_partial'), (EXPIRED, 'covers_disjoint')])
def test_declaration_not_fully_covering_scope_is_inapplicable(covers, reason):
    d = decl('p', covers=covers)
    out, row = assess([A], [review('a', A[0])], decls=[d])
    assert row['declaration_state'] == 'missing'
    assert {'record': d[0], 'reason': reason} in row['inapplicable']
