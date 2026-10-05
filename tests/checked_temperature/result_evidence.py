"""TEST-SIDE builder: value-variant T1 result evidence through backend public derivations.

Mirrors the committed generator
`docs/superpowers/reports/2026-09-19-next-measurement-preparation/prepare_public_evidence.py`:
the retained synthetic carrier observation is transformed to a new value with a
distinct payload, raw-record and occurrence identity, then candidate evaluation
and state classification are re-derived by the owning backend functions and
re-validated. The backend is used, not extended.

Limitation (CONTRACT §12.3, pending choice C1): the evidence keeps the retained
synthetic instant 2026-08-07T20:30:00Z. It is value-distinct, occurrence-distinct
evidence; it is NOT a temporally subsequent physical acquisition.
"""
import copy
import functools
import hashlib
import json

from tests.checked_temperature.fixtures import canon, public_evidence_bytes


@functools.lru_cache(maxsize=None)
def result_evidence_bytes(value, reuse_occurrence=False):
    """`reuse_occurrence` keeps the baseline occurrence identity (adverse twin only)."""
    from backend.model_kernel import ModelQueries
    from backend.model_kernel.store import validate_record_collection
    from backend.state_classification import StateClassificationResult
    from backend.state_classification.derivation import derive_classification
    from backend.constraint_evaluation.contracts import ConstraintEvaluationResult, derive_candidate_evaluation
    from backend.semantic_compatibility import VariableSemanticCompatibilityResult

    evidence = json.loads(public_evidence_bytes())
    old = evidence['snapshot']
    base = StateClassificationResult.model_validate(old)
    loaded = base.state.material.loaded()
    queries = ModelQueries(validate_record_collection(loaded.revision.model_id, dict(loaded.records)))
    payload = canon({'result': {'eventtime': 3721.845,
                                'status': {'extruder': {'temperature': json.loads(value), 'target': 60}}}})
    payload_hash = hashlib.sha256(payload).hexdigest()
    rawid = hashlib.sha256(b'gate1-result-raw:' + payload).hexdigest()[:32]
    occid = hashlib.sha256(b'gate1-result-occurrence:' + payload).hexdigest()[:32]
    obsid = hashlib.sha256(b'gate1-result-observation:' + payload).hexdigest()[:32]

    def transform(x):
        if isinstance(x, dict):
            y = {k: transform(v) for k, v in x.items()}
            if not reuse_occurrence and 'occurrence_id' in y and 'value_json' in y and \
                    y.get('property', {}).get('json_pointer', '').endswith('/temperature'):
                y.update(value_json=value, payload_checksum='sha256:' + payload_hash, raw_record_id=rawid,
                         occurrence_id=occid, observation_id=obsid)
            return y
        if isinstance(x, list):
            return [transform(v) for v in x]
        return x
    results = []
    for old_cn in old['constraint_evaluations']:
        es = VariableSemanticCompatibilityResult.model_validate(transform(copy.deepcopy(old_cn['semantic_compatibility'])))
        constraint = queries.constraint_declaration(old_cn['constraint']['constraint_anchor_id'])
        rows = tuple(derive_candidate_evaluation(constraint, es, i) for i in range(len(es.candidates)))
        results.append(ConstraintEvaluationResult(constraint=constraint, as_of=base.as_of, semantic_compatibility=es,
                                                  candidates=rows, ruleset_version='cn001.1'))
    state = queries.state_declaration(base.state_anchor_id, context=base.context)
    args = dict(state=state, state_anchor_id=base.state_anchor_id, context=base.context, as_of=base.as_of,
                condition_sources=base.condition_sources, constraint_evaluations=tuple(results))
    result = StateClassificationResult(**args, **derive_classification(**args))
    snapshot = json.loads(canon(result.model_dump(mode='json')))
    assert StateClassificationResult.model_validate_json(canon(snapshot)) == result
    assert result.constraint_evaluations[0].candidates[0].observed_decimal is not None
    tag = value.replace('.', '_') + ('-reused-occurrence' if reuse_occurrence else '')
    return canon(dict(evidence, id='E-result-' + tag, snapshot=snapshot))
