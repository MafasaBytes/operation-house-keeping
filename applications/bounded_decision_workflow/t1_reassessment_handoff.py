"""Pure carriage assembly over proposer-supplied reassessment inputs.

This component does not issue A, transfer selection reviews, evaluate a request
or confer producer-checked status. The complete command still needs owning
producer verification and publication gates around this pure assembly step.
"""
import json
import base64
from fractions import Fraction
from .t1_contracts import PROFILE, canonical_bytes, fraction, ref, refuse, sha
from .t1_records import parse
from .t1_schemas import validate


def _request_closure(request_wire, request_objects, admission, receipt, producer_evidence_wire, *, check_identity=True):
    """R-only traversal; A and unrelated delegated material confer no R edge."""
    from .t1_oracle import evidence_identity_check
    pool = dict(admission.objects)
    pool.update(request_objects)
    for item in json.loads(admission.prior_files['closure.json'])['members']:
        wire = base64.b64decode(item['data'], validate=True)
        if sha(wire) != item['sha256']:
            refuse('SIM_REFERENCE_INVALID', 1, '/R/' + item['sha256'])
        pool.setdefault(item['sha256'], wire)
    root = ref('ct.request.v1', request_wire)
    pool[root['sha256']] = request_wire
    if ref('nm.evidence.v1', producer_evidence_wire) != receipt['public_evidence']:
        refuse('SIM_REFERENCE_INVALID', 1, '/receipt/public_evidence')
    parse(producer_evidence_wire, 'nm.evidence.v1', '/O')
    pending, seen, evidence = [(root, '/R')], {}, [('/O', producer_evidence_wire)]
    validated = {}
    while pending:
        rr, target = pending.pop(0)
        digest = rr['sha256']
        if digest in seen:
            if seen[digest] != rr['kind']:
                refuse('SIM_REFERENCE_INVALID', 1, target)
            continue
        seen[digest] = rr['kind']
        if digest not in pool:
            refuse('SIM_REFERENCE_MISSING', 1, target)
        wire = pool[digest]
        if sha(wire) != digest:
            refuse('SIM_REFERENCE_INVALID', 1, target)
        if digest in admission.prior_digests:
            if json.loads(wire).get('schema') != rr['kind']:
                refuse('SIM_REFERENCE_INVALID', 1, target)
            continue
        if rr['kind'] == 'ct.evidence-content':
            continue  # The prior's opaque-file exception was already verified.
        value, annotations = parse(wire, rr['kind'], target)
        validated[digest] = (value, target)
        if value['schema'] == 'nm.evidence.v1':
            evidence.append((target, wire))
        if annotations:
            for pointer, provenance, allowed in annotations.roles:
                if provenance['role'] not in allowed:
                    refuse('SIM_REFERENCE_INVALID', 1, target + pointer + '/role')
            for pointer, child, allowed, edge in annotations.refs:
                if child['kind'] not in allowed:
                    refuse('SIM_REFERENCE_INVALID', 1, target + pointer)
                if edge:
                    pending.append((child, target + pointer))
    for digest, (value, target) in validated.items():
        if 'predecessor' not in value:
            continue
        predecessor = value['predecessor']
        if (value['revision'] == 1) != (predecessor is None):
            refuse('SIM_REFERENCE_INVALID', 1, target + '/predecessor')
        if predecessor is not None:
            previous = validated.get(predecessor['sha256'])
            previous_value = previous[0] if previous is not None else admission.records.get(predecessor['sha256'])
            if previous_value is None or previous_value['schema'] != value['schema'] or \
                    previous_value['id'] != value['id'] or previous_value['revision'] != value['revision'] - 1:
                refuse('SIM_REFERENCE_INVALID', 1, target + '/predecessor')
    extra = sorted(set(request_objects) - set(seen))
    if extra:
        refuse('SIM_REFERENCE_INVALID', 1, '/R/' + extra[0])
    if check_identity:
        evidence_identity_check(evidence, order=8, receipt_digest=receipt['public_evidence']['sha256'])
    return {d: pool[d] for d in seen}


def assemble_carriage(*, request_wire, manifest_wire, admission, receipt, prior_pins, request_objects,
                      producer_evidence_wire):
    """Keep authored R byte-identical; compare every prescribed carriage join."""
    r, _annotations = parse(request_wire, 'ct.request.v1', '/R')
    _request_closure(request_wire, request_objects, admission, receipt, producer_evidence_wire)
    j = admission.root('J')
    x = admission.get(j['execution_target'])
    result = r['result']
    if result['execution_authority'] != admission.references['E']:
        refuse('HANDOFF_AUTHORITY_JOIN_MISMATCH', 8, '/R/result/execution_authority')
    equalities = [('model', x['model']), ('prior_selection', x['prior_selection']),
        ('selection_basis', 'inherited'), ('plan_change', None), ('execution_target', j['execution_target']),
        ('result/procedure_edition', 'ct.procedure.T1.v1'),
        ('result/interpretation_plan', x['interpretation_plan']),
        ('result/observation/scalar', receipt['r']),
        ('result/acquisition/instrument_id', j['instrument_id']),
        ('result/acquisition/started', j['window']['from']), ('result/acquisition/ended', j['window']['to']),
        ('result/acquisition/public_evidence', receipt['public_evidence'])]
    for pointer, expected in equalities:
        actual = r
        for key in pointer.split('/'):
            actual = actual[key]
        equal = Fraction(actual) == Fraction(expected) if pointer == 'result/observation/scalar' else actual == expected
        if not equal:
            refuse('HANDOFF_JOIN_MISMATCH', 8, '/R/' + pointer)
    handoff = dict(schema='ct.t1-handoff.v1', profile=PROFILE,
        request=ref('ct.request.v1', request_wire), producer_manifest=ref('ct.t1-producer-manifest.v1', manifest_wire),
        target=admission.references['J'], permission=admission.references['G'], execution_authority=admission.references['E'],
        execution_target=j['execution_target'], prior=x['prior_selection'], prior_pins=prior_pins,
        public_evidence=receipt['public_evidence'], carriage=dict(model=x['model'], selection_basis='inherited', plan_change=None,
            scalar=receipt['r'], instrument_id=j['instrument_id'], interpretation_plan=x['interpretation_plan'],
            started=j['window']['from'], ended=j['window']['to']))
    validate(handoff, 'ct.t1-handoff.v1', '/H')
    return canonical_bytes(handoff)
