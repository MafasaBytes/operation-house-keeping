"""Bounded synthetic component fixtures, constructed only by future tests.

Injected TestDoubleBuild is development evidence only. Native tests instead
consume separately prepared, coherently real-current-build packages.
"""
import copy
import json
from pathlib import Path

from applications.bounded_decision_workflow import checked_runtime as rt
from applications.bounded_decision_workflow import t1_simulation as sim, t1_workflow as workflow
from applications.bounded_decision_workflow.t1_contracts import PROFILE, SCHEMAS, canonical_bytes, ref, sha
from applications.bounded_decision_workflow.t1_records import parse
from tests.checked_temperature.fixtures import co1
from .admitted_fixtures import admitted_case
from .request_fixtures import request_inputs_for


def write_package(path, files):
    path = Path(path)
    path.mkdir()
    for name, wire in files.items():
        destination = path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as stream:
            stream.write(wire)


def source_edit(case, *, actual_variable=None, instrument=None):
    """Rebind the entire source root graph, never edit a retained fixture."""
    world = case['world']
    w = world.value('W')
    if actual_variable is not None:
        w['actual_measurand']['variable_anchor_id'] = actual_variable
    if instrument is not None:
        w['instrument_id'] = instrument
    wr = world.put(w, 'W')
    j = world.value('J')
    j['world'] = wr
    jr = world.put(j, 'J')
    permission = world.value('G')
    permission['target'] = jr
    gr = world.put(permission, 'G')
    prior = {sha(wire) for wire in case['prior_files'].values()}
    objects, pending = {}, [jr, gr, world.refof('E')]
    while pending:
        rr = pending.pop()
        if rr['sha256'] in objects or rr['sha256'] in prior:
            continue
        wire = world.objects[rr['sha256']]
        objects[rr['sha256']] = wire
        if rr['kind'] != 'ct.evidence-content':
            _, annotations = parse(wire, rr['kind'], '/fixture')
            if annotations:
                pending.extend(r for _, r, _, edge in annotations.refs if edge)
    case['objects'] = objects
    case['pins'] = dict(J=jr['sha256'], G=gr['sha256'], E=world.refof('E')['sha256'])


def scenario(tmp_path, *, beta='0', theta='60.1', relation='support',
             actual_variable=None, phase_kw=None, assessment_policy=False, mutate=None, carried=None):
    if carried is None:
        case = admitted_case(beta=beta, theta=theta, baseline_theta=theta)
        if actual_variable is not None:
            source_edit(case, actual_variable=actual_variable)
        sim.acquire(objects=case['objects'], prior_files=case['prior_files'], pins=case['pins'],
            prior_pins=case['prior_pins'], build=case['build'], output=tmp_path / 'producer')
        producer = workflow.read_package(tmp_path / 'producer')
    else:
        assert actual_variable is None
        case, producer = carried['case'], dict(carried['producer'])
        assert carried['receipt']['operands']['beta'] == beta
        assert carried['receipt']['operands']['theta'] == theta
    receipt = json.loads(producer['receipt/receipt.json'])
    observation = json.loads(producer['evidence/public/evidence.json'])

    def edit(kind, value, world):
        if kind == 'R':
            value['result']['acquisition']['ended'] = '2026-10-05T09:02:00Z'
            if assessment_policy:
                policy = world.value('policy')
                policy['id'] = 'distinct-assessment-policy'
                if assessment_policy == 'conditional':
                    policy['unresolved_allowlist'] = [{'condition': 'reference_mapping', 'phase': 'reassessment'}]
                value['policy'] = world.put(policy, 'assessment-policy')
        if mutate is not None:
            mutate(kind, value, world)

    pk = dict(phase_kw or {})
    pk['relation'] = dict(pk.get('relation', {}), reference_calibration=relation)
    supplied = co1(case['prior_files'], case['base'], scalar=receipt['r'],
        evidence=lambda world: world.put(observation, 'fresh-synthetic-observation'),
        mutate=edit, phase_kw=pk)
    request_objects = request_inputs_for(supplied, case)
    handoff = workflow.prepare_handoff(producer_files=producer, manifest_pin=sha(producer['manifest.json']),
        pins=case['pins'], prior_pins=case['prior_pins'], build=case['build'],
        scratch=tmp_path / 'prepare-scratch', output=tmp_path / 'handoff',
        request_wire=supplied.request_wire, request_objects=request_objects)
    inputs = dict(producer_files=producer, manifest_pin=sha(producer['manifest.json']),
        pins=case['pins'], prior_pins=case['prior_pins'], build=case['build'],
        handoff_files=handoff, handoff_pin=sha(handoff['handoff.json']),
        request_pin=supplied.request_pin, authority_pin=supplied.authority_pin)
    authority_objects = {supplied.authority_pin: supplied.objects[supplied.authority_pin]}
    # Preserve any separately supplied A predecessor closure in a test revision.
    rr = supplied.auth.get('predecessor') if supplied.auth is not None else None
    while rr is not None:
        authority_objects[rr['sha256']] = supplied.objects[rr['sha256']]
        rr = json.loads(authority_objects[rr['sha256']])['predecessor']
    return dict(case=case, supplied=supplied, inputs=inputs, authority_objects=authority_objects,
                producer=producer, handoff=handoff, receipt=receipt, request_objects=request_objects)


def evaluate(specimen, tmp_path, label='evaluation'):
    return workflow.evaluate(**specimen['inputs'], authority_objects=specimen['authority_objects'],
                             scratch=tmp_path / (label + '-scratch'), output=tmp_path / label)


def verify(specimen, files, tmp_path, label='verification'):
    return workflow.verify_calibration_workflow(**specimen['inputs'], workflow_files=files,
        workflow_pin=sha(files['workflow-receipt.json']), scratch=tmp_path / label)


def preflight_finding(specimen, tmp_path):
    return workflow._calibration_context(**specimen['inputs'], authority_objects=specimen['authority_objects'],
                                         scratch=tmp_path / 'finding-scratch')


def legacy_workflow(specimen):
    """Explicit old-contract component specimen; not an old executable claim."""
    supplied, case = specimen['supplied'], specimen['case']
    bundle = rt.evaluate_reassessment(request_wire=supplied.request_wire,
        objects=dict(specimen['request_objects'], **specimen['authority_objects']),
        prior_files=case['prior_files'], request_pin=supplied.request_pin,
        authority_pin=supplied.authority_pin, build=case['build'])
    j = case['world'].value('J')
    inputs = specimen['inputs']
    f = dict(schema='ct.t1-workflow-receipt.v1', profile=PROFILE, guarantee='producer-checked',
        request=ref('ct.request.v1', supplied.request_wire),
        evaluation_authority=ref('ct.authority.v1', supplied.objects[supplied.authority_pin]),
        handoff=ref('ct.t1-handoff.v1', specimen['handoff']['handoff.json']),
        producer_manifest=ref('ct.t1-producer-manifest.v1', specimen['producer']['manifest.json']),
        target={'kind': 'ct.t1-simulation-target.v1', 'sha256': inputs['pins']['J']},
        permission={'kind': 'ct.t1-simulation-permission.v1', 'sha256': inputs['pins']['G']},
        execution_authority={'kind': 'ct.authority.v1', 'sha256': inputs['pins']['E']},
        world=j['world'], prior_pins=inputs['prior_pins'],
        output_manifest=ref('ct.bundle-manifest.v1', bundle['manifest.json']),
        producer_build=j['producer_build'], checker_build=ref('ct.build.v1', case['build'].wire()),
        limitations=SCHEMAS['records']['ct.t1-workflow-receipt.v1']['properties']['limitations']['const'])
    return canonical_bytes(f), bundle


def rehash_owner_result(bundle):
    """Valid metadata/digests but false downstream row, discriminating full replay."""
    from tests.checked_temperature.fixtures import rehash_bundle
    result = json.loads(bundle['result.json'])
    result['hypotheses'][0]['status'] = 'conditionally_incompatible'
    return rehash_bundle(dict(bundle, **{'result.json': canonical_bytes(result)}))


def classifier_rows():
    groups = ('producer_closure', 'source_editions', 'handoff_request', 'request_carriage',
              'observation_occurrence', 'raw_occurrence', 'instrument', 'model_claim_bound',
              'intended_actual', 'structural_lifecycle', 'source_configuration', 'effective_binding',
              'effective_interpretation_units', 'time_scope', 'review_and_base', 'arithmetic')
    return [dict(group=group, relation='all_required_links', operands=[
        dict(subject='world', pointer='/beta', normalized_value=dict(kind='text', value='10'))],
        status='equal', reason=None) for group in groups]
