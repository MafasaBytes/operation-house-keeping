"""Analytical development inputs, not operational authorities or admitted records.

The minimal models below exercise the pure receipt oracle. They deliberately
do not claim to form an admitted workflow or a valid executable build.
"""
from applications.bounded_decision_workflow.t1_contracts import canonical_bytes, ref


def diagnostic_inputs(theta='60', baseline_theta='60', beta='0', epsilon='0', wrong_mapping=False):
    pool = {}
    def put(value, kind):
        rr = ref(kind, canonical_bytes(value))
        pool[rr['sha256']] = value
        return rr
    rat = lambda n, d=1: {'numerator': str(n), 'denominator': str(d)}
    c = {'intended_subject_entity_anchor_id': 'ent_' + '9' * 32,
         'intended_variable_anchor_id': 'var_' + '1' * 32,
         'reading_locator': {'subject': {'source_id': 'printer-1', 'adapter_id': 'moonraker',
                                        'subject_identifier': 'extruder'},
                             'property': {'extraction_route': 'api:moonraker:v1', 'item_key': 'printer_objects',
                                          'json_pointer': '/result/status/extruder/temperature'}}}
    w = {'theta': theta, 'baseline_theta': baseline_theta, 'beta': beta, 'epsilon': epsilon,
         'unit': 'degree_celsius', 'actual_measurand': {
             'subject_entity_anchor_id': c['intended_subject_entity_anchor_id'],
             'variable_anchor_id': 'var_' + '2' * 32 if wrong_mapping else c['intended_variable_anchor_id']}}
    model = {'baseline': rat(601, 10), 'b_ref': {'lo': rat(0), 'hi': rat(0)},
             'hypotheses': [{'explanation': {'kind': 'ct.explanation.v1', 'sha256': '1' * 64},
                             'b_suspect': {'lo': rat(0), 'hi': rat(0)}},
                            {'explanation': {'kind': 'ct.explanation.v1', 'sha256': '2' * 64},
                             'b_suspect': {'lo': rat(5), 'hi': rat(15)}}]}
    x = {'model': put(model, 'ct.model.v1'),
         'interpretation_plan': put({'half_width': rat(1, 2)}, 'ct.interpretation-plan.v1')}
    e = {'target': put(x, 'ct.execution-target.v1')}
    j = {'world': put(w, 'ct.t1-world.v1'), 'context': put(c, 'ct.t1-context.v1'),
         'captured_policy': put({'limits': {'fractional_digits': 4}}, 'ct.policy.v1')}
    return j, e, lambda rr: pool[rr['sha256']]


def world_record():
    return {'schema': 'ct.t1-world.v1', 'profile': 'bdw.checked-temperature.v1',
            'id': 'world-development-only', 'revision': 1, 'predecessor': None,
            'provenance': {'role': 'local_model_proposer', 'label': 'development-only',
                           'basis': 'synthetic test premise, not operational permission', 'authenticated': False},
            'origin': 'synthetic', 'rule': {'kind': 'ct.t1-simulator-rule.v2', 'sha256': 'a' * 64},
            'source': {'source_id': 'printer-1', 'adapter_id': 'moonraker'},
            'instrument_id': 'inst_' + 'a' * 32, 'intended_subject_entity_anchor_id': 'ent_' + '9' * 32,
            'intended_variable_anchor_id': 'var_' + '1' * 32, 'unit': 'degree_celsius',
            'theta': '60', 'beta': '0', 'epsilon': '0', 'baseline_theta': '60',
            'actual_measurand': {'subject_entity_anchor_id': 'ent_' + '9' * 32,
                                 'variable_anchor_id': 'var_' + '1' * 32}}
