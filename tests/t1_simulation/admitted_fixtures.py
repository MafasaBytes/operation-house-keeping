"""Admitted in-process synthetic T1 test premises; never real-build authority.

Construction runs only inside enumerated tests. Selection is evaluated through
the maintained route. Binding/interpretation declarations use public builders;
no diagnostic store or acquisition is created here.
"""
import copy
import json
from datetime import datetime, timedelta
from pathlib import Path

from applications.bounded_decision_workflow.t1_contracts import (
    PROFILE, SCHEMAS_SHA256, canonical_bytes, ref, sha)
from applications.bounded_decision_workflow.t1_records import parse
from tests.checked_temperature.fixtures import (
    ROOT, REF_INST, T1, TestDoubleBuild, co1, fx1, prov, run_selection)


def _declarations():
    from backend.identity_binding.canonical import build_record as ib_build
    from backend.identity_binding.contracts import (
        AppliesScope, AuthorityRef, BindingAssertion, DeclaredBoundary)
    from backend.source_interpretation import (
        ObservationRoleInterpretation, QuantityKindInterpretation,
        SourcePropertyInterpretation, UnitInterpretation, build_record)
    from tests.behavior_evaluation.helpers import E1
    from tests.model_state.helpers import (
        PROP_TARGET, PROP_TEMP, SUBJECT, entity_declaration, var_declaration)
    from tests.model_kernel.builders import VAR_A, VAR_B, observation_role, quantity_kind
    from tests.model_kernel.bh001_slice_a_helpers import semantic_lock
    t0 = datetime.fromisoformat('2026-10-05T09:00:00Z')
    applies = AppliesScope(axis='ingestion_received_at',
        start_boundary=DeclaredBoundary(kind='declared', at=t0 - timedelta(hours=1)),
        end_boundary=DeclaredBoundary(kind='declared', at=t0 + timedelta(hours=1)),
        interval_semantics='half_open')
    authority = AuthorityRef(kind='test_fixture', agent='maintained_t1_development',
                             method='manual_declaration')
    common = dict(applies=applies, recorded_at=t0 - timedelta(minutes=30),
                  authority=authority, note='synthetic development test premise')
    bindings = [entity_declaration(E1, 'Demo entity'), var_declaration(VAR_A, E1, 'Variable A'),
                var_declaration(VAR_B, E1, 'Variable B')]
    interpretations = []
    for prop, variable, role in ((PROP_TEMP, VAR_A, 'measured'), (PROP_TARGET, VAR_B, 'reported')):
        bindings.append(ib_build(BindingAssertion, binding_kind='property', subject=SUBJECT,
                                property=prop, target_anchor_id=variable, **common))
        for interpretation in (
            QuantityKindInterpretation(dimension='quantity_kind', quantity_kind=quantity_kind()),
            ObservationRoleInterpretation(dimension='observation_role', observation_role=observation_role(role)),
            UnitInterpretation(dimension='unit', unit=semantic_lock(VAR_A).signature.unit)):
            interpretations.append(build_record(SourcePropertyInterpretation, subject=SUBJECT,
                property=prop, interpretation=interpretation, supersedes=(), **common))
    dump = lambda records: [r.model_dump(mode='json') for r in records]
    return dump(bindings), dump(interpretations)


def admitted_case(*, theta='60', baseline_theta='60', beta='0', epsilon='0'):
    """Return objects/prior_files/pins/prior_pins/build/world and selection handles.

    The test-double build is explicitly labelled and has nonzero fixture fields.
    The local policy and permissions are supplied synthetic premises.
    """
    build = TestDoubleBuild(marker='1')
    base = fx1(build=build)
    prior_files = run_selection(base)
    inherited = co1(prior_files, base, evidence='baseline')
    world = inherited.world
    baseline = world.value('evidence')
    model = world.value('model')
    specdir = ROOT / 'docs/superpowers/specs/2026-10-09-maintained-t1-simulated-acquisition-contract-preparation-v3'
    def authored(kind, identity, role='local_model_proposer'):
        return dict(schema=kind, profile=PROFILE, id=identity, revision=1,
                    predecessor=None, provenance=prov(role))
    rule = json.loads((specdir / 'rule.json').read_bytes())
    preset = json.loads((specdir / 'preset/preset.json').read_bytes())
    rule_ref = world.put(rule, 'rule')
    preset_ref = world.put(preset, 'preset')
    policy = json.loads((specdir / 'simulator-policy.json').read_bytes())
    policy.pop('x-unresolved')
    policy.update(companion_schemas_sha256=SCHEMAS_SHA256,
                  permitted_producer_builds=[build.digest], permitted_checker_builds=[build.digest],
                  provenance=prov('local_policy_owner'))
    policy_ref = world.put(policy, 'simulator_policy')
    build_ref = world.put(build.record, 'producer_build')
    bindings, interpretations = _declarations()
    b = baseline['binding']
    context = authored('ct.t1-context.v1', 'development-context')
    context.update(carrier_edition='ct.t1-carrier.printer-1-extruder.v1', preset=preset_ref,
        source_definition=dict(source_id='printer-1', display_name='development-test-double',
            source_kind='operational_api', connector_type='http_api', credential_reference=None,
            declared_content_types=['application/json'], enabled=True,
            configuration=dict(base_url='http://127.0.0.1:7125', adapter='moonraker',
                               allow_plaintext_http='true', plaintext_scope='loopback_only')),
        reading_locator=baseline['snapshot']['condition_sources'][0]['source'],
        intended_subject_entity_anchor_id=b['subject_entity_anchor_id'],
        intended_variable_anchor_id=b['variable_anchor_id'],
        constraint_anchor_id=b['constraint_anchor_id'], state_anchor_id=baseline['question']['state_anchor_id'],
        declared_state_label='synthetic development premise', assertion_context=model['context']['assertion_context'],
        condition_sources=baseline['snapshot']['condition_sources'],
        material=baseline['snapshot']['state']['material'], binding_set_id='development-binding',
        bindings=bindings, interpretation_set_id='development-interpretation', interpretations=interpretations)
    for key in ('expected_quantity_kind', 'expected_observation_role', 'expected_unit'):
        context[key] = b[key]
    context_ref = world.put(context, 'C')
    w = authored('ct.t1-world.v1', 'development-world')
    w.update(origin='synthetic', rule=rule_ref, source=dict(source_id='printer-1', adapter_id='moonraker'),
        instrument_id=REF_INST, intended_subject_entity_anchor_id=b['subject_entity_anchor_id'],
        intended_variable_anchor_id=b['variable_anchor_id'], unit='degree_celsius',
        theta=theta, baseline_theta=baseline_theta, beta=beta, epsilon=epsilon,
        actual_measurand=dict(subject_entity_anchor_id=b['subject_entity_anchor_id'],
                              variable_anchor_id=b['variable_anchor_id']))
    w_ref = world.put(w, 'W')
    target = authored('ct.t1-simulation-target.v1', 'development-target')
    target.update(execution_target=world.refof('X'), world=w_ref, context=context_ref,
        rule=rule_ref, simulator_policy=policy_ref, captured_policy=world.refof('policy'),
        producer_build=build_ref, companion_schemas_sha256=SCHEMAS_SHA256,
        logical_run_id='development-run', instrument_id=REF_INST, t0='2026-10-05T09:00:00Z',
        window={'from': '2026-10-05T09:00:00Z', 'to': '2026-10-05T09:02:00Z'},
        question_as_of='2026-10-05T09:02:00Z', clock_rule='wall:t0+k;monotonic:k/1024',
        resource_bounds=copy.deepcopy(policy['resource_maxima']))
    target_ref = world.put(target, 'J')
    permission = authored('ct.t1-simulation-permission.v1', 'development-permission', 'local_execution_issuer')
    permission.update(purpose='simulation', target=target_ref, execution_authority=world.refof('E'),
        scope={key: target[key] for key in ('rule', 'simulator_policy', 'producer_build', 'captured_policy')},
        valid={'from': '2026-10-05T08:00:00Z', 'to': '2026-10-05T18:00:00Z'},
        grants=dict(simulation=True, physical_acquisition=False, evaluation=False, adoption=False))
    permission_ref = world.put(permission, 'G')
    # Follow only schema-annotated refs. Prior files are opaque retained carriage;
    # their internal material is recovered by admission from the prior closure.
    prior_digests = {sha(wire) for wire in prior_files.values()}
    pending = [target_ref, world.refof('E'), permission_ref]
    objects = {}
    while pending:
        rr = pending.pop(0)
        digest = rr['sha256']
        if digest in objects or digest in prior_digests:
            continue
        wire = world.objects[digest]
        objects[digest] = wire
        if rr['kind'] == 'ct.evidence-content':
            continue
        _, annotations = parse(wire, rr['kind'], '/')
        if annotations:
            pending.extend(row[1] for row in annotations.refs)
    return dict(objects=objects, prior_files=prior_files,
                pins=dict(J=target_ref['sha256'], E=world.refof('E')['sha256'], G=permission_ref['sha256']),
                prior_pins=dict(request_sha256=base.request_pin, authority_sha256=base.authority_pin),
                build=build, world=world, base=base, inherited=inherited)
