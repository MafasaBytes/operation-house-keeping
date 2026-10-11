"""Maintained synthetic acquisition and independently checked retained carriage.

Inputs and permissions are supplied; this module issues no authority. Backend
acquisition is a deterministic in-process transport, never physical I/O.
"""
import json
from fractions import Fraction
from pathlib import Path
from contextlib import nullcontext

from . import t1_acquisition as acquisition
from .t1_contracts import PROFILE, SCHEMAS, canonical_bytes, fraction, instant, rational, ref, refuse, sha
from .t1_records import preflight
from .t1_closure import OPAQUE, build_manifest, inspect_package
from .t1_package import Publication, safe_new_dir


def _decimal(q):
    from .t1_carrier import fixed
    return fixed(q)


def _values(a):
    """Generation comparands; verification uses the separate receipt oracle."""
    j = a.root('J')
    w, c = a.get(j['world']), a.get(j['context'])
    x = a.get(j['execution_target'])
    m, p = a.get(x['model']), a.get(x['interpretation_plan'])
    theta, old, beta, epsilon = map(Fraction, (w['theta'], w['baseline_theta'], w['beta'], w['epsilon']))
    subject = w['actual_measurand']['subject_entity_anchor_id'] == c['intended_subject_entity_anchor_id']
    variable = w['actual_measurand']['variable_anchor_id'] == c['intended_variable_anchor_id']
    same = subject and variable
    rows = []
    for h in m['hypotheses']:
        lo, hi = (fraction(m['baseline']) - fraction(h['b_suspect'][k]) for k in ('hi', 'lo'))
        rows.append(dict(explanation=h['explanation'], interval=dict(lo=rational(lo), hi=rational(hi)),
                         same_referent=same, theta_in_interval=lo <= theta <= hi if same else None))
    delta = _decimal(theta - old)
    return dict(operands={k: w[k] for k in ('theta', 'baseline_theta', 'beta', 'epsilon')},
        r=_decimal(theta + beta + epsilon), d=min(6, a.get(j['captured_policy'])['limits']['fractional_digits']),
        intended=dict(subject=c['intended_subject_entity_anchor_id'], variable=c['intended_variable_anchor_id'], unit=w['unit']),
        actual_measurand=w['actual_measurand'], reading_locator=c['reading_locator'], diagnostics=dict(
            reference_calibration=dict(b_ref=m['b_ref'], beta_in_b_ref=fraction(m['b_ref']['lo']) <= beta <= fraction(m['b_ref']['hi'])),
            observation_error_bound=dict(w=p['half_width'], abs_epsilon_le_w=abs(epsilon) <= fraction(p['half_width'])),
            reference_mapping=dict(subject_mapping_matches=subject, variable_mapping_matches=variable),
            state_hold=dict(model_baseline=m['baseline'], theta_equals_baseline_theta=theta == old, delta=delta,
                per_hypothesis=rows, intended_variable_hold=dict(basis='same_declared_measurand' if same else 'not_declared_for_intended_variable',
                    theta_equals_baseline_theta=theta == old if same else None, delta=delta if same else None))))


def _artifacts(result):
    """Keep actual backend bytes; embedded observations remain embedded."""
    files = {}
    def put(path, wire, kind=OPAQUE):
        files[path] = wire
        return ref(kind, wire)
    evidence = dict(snapshot=put('evidence/public/snapshot.json', result['snapshot']),
        run_result=put('evidence/run/run.json', result['run']),
        projection_report=put('evidence/projection/projection.json', result['projection']),
        logical_query_results=[put('evidence/query/logical.json', result['logical'])], db_diagnostics=[],
        raw_envelopes=[], acquisition_attempts=[], extraction_results=[])
    public = put('evidence/public/evidence.json', result['public_evidence'], 'nm.evidence.v1')
    transcripts = {k: put('evidence/transcripts/' + k, result[k]) for k in ('wall_clock', 'monotonic', 'transport')}
    raw = Path(result['raw_root'])
    stored = result['store'].retained_files() if hasattr(result.get('store'), 'retained_files') else None
    for source, prefix, field in (('envelopes', 'evidence/raw/envelope-', 'raw_envelopes'),
                                 ('attempts', 'evidence/attempts/', 'acquisition_attempts'),
                                 ('extracted', 'evidence/extraction/', 'extraction_results')):
        entries = sorted((p, w) for p, w in stored.items() if p.startswith(prefix)) if stored is not None else \
            [(prefix + path.name, path.read_bytes()) for path in sorted((raw / source).glob('*.json'))]
        for path, wire in entries:
            evidence[field].append(put(path, wire))
    bodies = {}
    for path in sorted(p for p in files if p.startswith('evidence/raw/envelope-')):
        envelope = json.loads(files[path])
        digest = envelope['payload_checksum'].removeprefix('sha256:')
        put('evidence/raw/' + digest, stored['evidence/raw/' + digest] if stored is not None else (raw / 'payloads' / digest).read_bytes())
        bodies[envelope['api_locator']['item_key']] = digest
    diagnostics = result.get('diagnostic_paths', sorted(Path(result['db_path']).parent.glob('temporal.db*')))
    for path in diagnostics:
        evidence['db_diagnostics'].append(put('evidence/db/' + path.name, path.read_bytes()))
    envelopes = [json.loads(files[p]) for p in sorted(files) if p.startswith('evidence/raw/envelope-')]
    envelope = next(e for e in envelopes if e['api_locator']['item_key'] == 'printer_objects')
    attempts = [json.loads(files[p]) for p in sorted(files) if p.startswith('evidence/attempts/')]
    attempt = next(t for t in attempts if t['raw_record_id'] == envelope['record_id'])
    extraction = json.loads(files['evidence/extraction/' + envelope['record_id'] + '.json'])
    public_record = json.loads(result['public_evidence'])
    binding = public_record['binding']
    evaluation = public_record['snapshot']['constraint_evaluations'][binding['constraint_evaluation_index']]
    candidate = evaluation['semantic_compatibility']['candidates'][binding['semantic_candidate_index']]
    occurrence = candidate['value_candidate']['state_candidate']['bound']['observed']['occurrence']
    run = json.loads(result['run'])
    admitted = dict(attempt_started_at=attempt['started_at'], finished_at=attempt['finished_at'],
        ingestion_run_id=run['run_id'], occurrence_id=occurrence['occurrence_id'],
        payload_checksum=envelope['payload_checksum'], raw_record_id=envelope['record_id'],
        received_at=attempt['received_at'], evidence_id=json.loads(result['public_evidence'])['id'])
    # Backend serializes UTC as +00:00; companion has an exact Z grammar.
    for key in ('attempt_started_at', 'finished_at', 'received_at'):
        admitted[key] = admitted[key].replace('+00:00', 'Z')
    return files, dict(evidence=evidence, public_evidence=public, transcripts=transcripts,
                       raw_response_digests=bodies, admitted=admitted)


def build_carriage(*, admission, produced):
    """Pure complete retained-package construction, before command gates.

    This component constructs exact reachability and measures actual manifest
    demand. It does not attest the outstanding production/verification gates.
    """
    a = admission
    files, retained = _artifacts(produced)
    j = a.root('J')
    receipt = dict(schema='ct.t1-producer-receipt.v1', profile=PROFILE, target=a.references['J'],
                  permission=a.references['G'], execution_authority=a.references['E'], **_values(a), **retained)
    for key in ('execution_target', 'world', 'context', 'rule', 'simulator_policy', 'captured_policy', 'producer_build'):
        receipt[key] = j[key]
    receipt['limitations'] = SCHEMAS['records'][receipt['schema']]['properties']['limitations']['const']
    wire = canonical_bytes(receipt)
    files.update({'objects/' + d: w for d, w in a.objects.items()})
    files['receipt/receipt.json'] = wire
    roots = dict(target=a.references['J'], permission=a.references['G'], execution_authority=a.references['E'],
                 receipt=ref(receipt['schema'], wire))
    files['manifest.json'] = build_manifest(files, roots)
    return files


def acquire(*, objects, prior_files, pins, prior_pins, build, output, workspace=None, observe=None):
    """Complete admission before creating acquisition or publication output."""
    a = preflight(objects=objects, prior_files=prior_files, pins=pins, prior_pins=prior_pins, build=build)
    safe_new_dir(output)
    if workspace is not None and Path(workspace) != Path(output):
        refuse('SIM_OUTPUT_UNSAFE', 0, '/argv/output-dir', 5)
    publication = Publication(output)
    result = acquisition.produce(objects=objects, prior_files=prior_files, pins=pins, prior_pins=prior_pins,
                                 build=build, workspace=output, output_only=True, observe=observe, publication=publication)
    files, retained = _artifacts(result)
    j = a.root('J')
    receipt = dict(schema='ct.t1-producer-receipt.v1', profile=PROFILE, target=a.references['J'],
                  permission=a.references['G'], execution_authority=a.references['E'], **_values(a), **retained)
    for key in ('execution_target', 'world', 'context', 'rule', 'simulator_policy', 'captured_policy', 'producer_build'):
        receipt[key] = j[key]
    receipt['limitations'] = SCHEMAS['records'][receipt['schema']]['properties']['limitations']['const']
    receipt_wire = canonical_bytes(receipt)
    files.update({'objects/' + d: w for d, w in a.objects.items()})
    files['receipt/receipt.json'] = receipt_wire
    roots = dict(target=a.references['J'], permission=a.references['G'], execution_authority=a.references['E'],
                 receipt=ref(receipt['schema'], receipt_wire))
    from .t1_reconstruction import raw_records
    independent_store, independent_records = raw_records(a, Path(output) / 'evidence/raw')
    model = a.get(a.get(j['execution_target'])['model'])
    independent_db = Path(output) / 'evidence/db/reconstruction.db'
    independent_o, independent_snapshot, independent_projection, independent_logical = acquisition.classify(
        a.get(j['context']), independent_store, independent_db, j, a.get(model['baseline_evidence']), a.references['J']['sha256'], memory=True)
    expected = dict(independent_records, store=independent_store, raw_root=independent_store.base_dir,
                    db_path=independent_db, public_evidence=independent_o, snapshot=independent_snapshot,
                    projection=independent_projection, logical=independent_logical)
    expected_files, expected_retained = _artifacts(expected)
    check_artifacts(files=files, expected_files=expected_files, retained=expected_retained, receipt=receipt, admission=a)
    # Logical self-reconstruction uses a fresh in-memory backend store. Every
    # actual physical production diagnostic remains retained and content-bound.
    result['diagnostic_paths'] = sorted(p for p in independent_db.parent.iterdir() if p.is_file())
    files, retained = _artifacts(result)
    receipt.update(retained)
    receipt_wire = canonical_bytes(receipt)
    files.update({'objects/' + d: w for d, w in a.objects.items()})
    files['receipt/receipt.json'] = receipt_wire
    roots['receipt'] = ref(receipt['schema'], receipt_wire)
    manifest = build_manifest(files, roots)
    for path, wire in sorted(files.items()):
        if path.startswith('evidence/db/'):
            publication.seal_existing(path, wire)
        elif (publication.root / path).exists():
            # RawStore already durably retained this immutable backend record.
            if (publication.root / path).read_bytes() != wire:
                refuse('SIM_PUBLICATION_INCOMPLETE', 7, '/M', 5)
        else:
            publication.write(path, wire)
    publication.finish(manifest)
    return dict(files, **{'manifest.json': manifest})


def verify(*, files, manifest_pin, pins, prior_pins, build, workspace, observe=None):
    """Fresh reconstruction from frozen inputs; DB bytes remain diagnostic only.

    The common owning backend is disclosed. Reconstructed raw bodies, envelopes,
    attempts, extraction results and embedded occurrence joins are all compared,
    independently of submitted companion index assertions.
    """
    from .t1_oracle import check_receipt, check_wrapper
    closure = inspect_package(files['manifest.json'], files, manifest_pin=manifest_pin)
    roots = closure.manifest['roots']
    for key, letter in (('target', 'J'), ('execution_authority', 'E'), ('permission', 'G')):
        if roots[key]['sha256'] != pins[letter]:
            refuse('SIM_PIN_MISMATCH', 1, '/' + letter)
    inputs = {path.split('/')[1]: wire for path, wire in files.items() if path.startswith('objects/')}
    prior = closure.prior_files
    objects = {d: w for d, w in inputs.items() if d not in {sha(w) for w in prior.values()}}
    safe_new_dir(workspace)
    a = preflight(objects=objects, prior_files=prior, pins=pins, prior_pins=prior_pins, build=build, checker=True)
    from .t1_reconstruction import reconstruct
    result = reconstruct(admission=a, workspace=workspace, observe=observe)
    expected_files, retained = _artifacts(result)
    receipt = closure.get(roots['receipt'])
    phase = observe if observe is not None else lambda _name: nullcontext()
    with phase('carriage_verification'):
        check_artifacts(files=files, expected_files=expected_files, retained=retained,
                        receipt=receipt, admission=a)
    # Diagnostic DB identity is checked as retained bytes, never compared with
    # platform-dependent fresh SQLite bytes or used to derive classifications.
    # A1 leaves diagnostics content-bound without a new semantic byte oracle.
    # Recompute diagnostic references from verified submitted paths, not scratch.
    for field, prefix in (('db_diagnostics', 'evidence/db/'),
                          ('logical_query_results', 'evidence/query/')):
        retained['evidence'][field] = [ref(OPAQUE, files[p]) for p in sorted(files) if p.startswith(prefix)]
    for field, path in (('snapshot', 'evidence/public/snapshot.json'),
                         ('run_result', 'evidence/run/run.json'),
                         ('projection_report', 'evidence/projection/projection.json')):
        retained['evidence'][field] = ref(OPAQUE, files[path])
    check_receipt(receipt, a.root('J'), a.root('E'), a.get, retained)
    return {'guarantee': 'simulation-verified', 'receipt': receipt, 'admission': a,
            'manifest_bytes': len(files['manifest.json']), 'reconstructed': result}


def check_artifacts(*, files, expected_files, retained, receipt, admission):
    """Frozen 7.1–7.5; expected artifacts are independently reconstructed.

    No diagnostic DB/run/projection/logical byte oracle is added. Scratch owning
    O is compared in 7.5 after locator, material and occurrence joins.
    """
    from .t1_oracle import check_wrapper
    a = admission
    j = a.root('J')
    model = a.get(a.get(j['execution_target'])['model'])
    baseline = a.get(model['baseline_evidence'])
    ordered = ['evidence/transcripts/' + k for k in ('wall_clock', 'monotonic', 'transport')]
    for prefix in ('evidence/raw/', 'evidence/attempts/', 'evidence/extraction/'):
        paths = sorted(p for p in expected_files if p.startswith(prefix))
        if prefix == 'evidence/raw/':
            paths.sort(key=lambda p: (p.startswith('evidence/raw/envelope-'), p))
        ordered.extend(paths)
    for path in ordered:
        if files.get(path) != expected_files[path]:
            refuse('SIM_DERIVATION_MISMATCH', 7, '/' + path)
    evidence = json.loads(files['evidence/public/evidence.json'])
    if evidence['binding'] != baseline['binding']:
        refuse('SIM_MEASUREMENT_LOCATOR_MISMATCH', 7, '/O/binding')
    if evidence['snapshot']['state']['material'] != a.get(j['context'])['material']:
        refuse('SIM_MODEL_MATERIAL_MISMATCH', 7, '/O/snapshot/state/material')
    from .measurement_compute import public_evidence
    from .measurement_wire import Work
    from .measurement_contracts import MeasurementContractError
    context = dict(model['context'], as_of=j['question_as_of'])
    try:
        observed, _verdict = public_evidence(evidence, context, Work())
        baseline_observed, _ = public_evidence(baseline, model['context'], Work())
    except MeasurementContractError:
        refuse('SIM_OBSERVATION_JOIN_MISMATCH', 7, '/O/occurrence_id')
    binding = evidence['binding']
    ev = evidence['snapshot']['constraint_evaluations'][binding['constraint_evaluation_index']]
    candidate = ev['semantic_compatibility']['candidates'][binding['semantic_candidate_index']]
    occurrence = candidate['value_candidate']['state_candidate']['bound']['observed']['occurrence']
    if observed.occurrence_id == baseline_observed.occurrence_id:
        refuse('SIM_OBSERVATION_JOIN_MISMATCH', 7, '/O/occurrence_id')
    checksum = 'sha256:' + sha(expected_files['evidence/raw/' + retained['raw_response_digests']['printer_objects']])
    if occurrence['payload_checksum'] != checksum:
        refuse('SIM_OBSERVATION_JOIN_MISMATCH', 7, '/O/payload_checksum')
    lo, hi = instant(j['window']['from']), instant(j['window']['to'])
    for field in ('received_at', 'finished_at'):
        value = occurrence[field].replace('+00:00', 'Z')
        if not lo <= instant(value) <= hi:
            refuse('SIM_OBSERVATION_JOIN_MISMATCH', 7, '/O/' + field)
    from .t1_oracle import receipt_values
    independent = receipt_values(j, a.root('E'), a.get)
    if observed.canonical_decimal is None or Fraction(observed.canonical_decimal) != Fraction(independent['r']):
        refuse('SIM_OBSERVATION_JOIN_MISMATCH', 7, '/O/scalar')
    if evidence['question']['as_of'] != j['window']['to']:
        refuse('SIM_OBSERVATION_JOIN_MISMATCH', 7, '/O/question/as_of')
    if ref('nm.evidence.v1', files['evidence/public/evidence.json']) != receipt['public_evidence']:
        refuse('SIM_OBSERVATION_JOIN_MISMATCH', 7, '/receipt/public_evidence')
    joins = dict(occurrence, evidence_id=evidence['id'])
    for field in ('occurrence_id', 'raw_record_id', 'ingestion_run_id', 'payload_checksum',
                  'received_at', 'finished_at', 'attempt_started_at', 'evidence_id'):
        expected = joins[field]
        if field.endswith('_at'):
            expected = expected.replace('+00:00', 'Z')
        if receipt['admitted'][field] != expected:
            refuse('SIM_OBSERVATION_JOIN_MISMATCH', 7, '/receipt/admitted/' + field)
    check_wrapper(evidence, baseline, j, a.references['J']['sha256'])
    if sha(files['evidence/public/evidence.json']) != sha(expected_files['evidence/public/evidence.json']):
        refuse('SIM_DERIVATION_MISMATCH', 7, '/O')
