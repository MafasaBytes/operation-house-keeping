"""Bounded companion intake and pure pre-production admission.

This module owns no permission issuance and performs no acquisition or store I/O.
"""
import base64
from dataclasses import dataclass
from datetime import timedelta
from fractions import Fraction
import json

from . import checked_contracts as inherited
from .t1_contracts import (CAPS, PRESET_SHA256, PROFILE, REVISION, RULE_SHA256, SCHEMAS_SHA256,
                           SUBJECT, VARIABLE, SCHEMAS, SimRefusal, canonical_bytes, instant, refuse, sha)
from .t1_schemas import validate

LETTERS = {'ct.t1-world.v1': 'W', 'ct.t1-context.v1': 'C', 'ct.t1-simulation-target.v1': 'J',
           'ct.t1-simulation-permission.v1': 'G', 'ct.authority.v1': 'E', 'ct.request.v1': 'R',
           'ct.execution-target.v1': 'X', 'ct.t1-simulator-rule.v2': 'rule',
           'ct.t1-simulator-policy.v1': 'simulator_policy', 'ct.t1-carrier-preset.v1': 'preset'}
GENERIC_CAP = 196608


def parse(wire, kind, target):
    if len(wire) > CAPS.get(kind, GENERIC_CAP):
        refuse('SIM_RESOURCE_LIMIT', 0, target, 4)
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                refuse('SIM_SCHEMA_INVALID', 0, target)
            value[key] = item
        return value
    def constant(_):
        refuse('SIM_SCHEMA_INVALID', 0, target)
    try:
        value = json.loads(wire.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant)
        stack, nodes = [(value, 1)], 0
        while stack:
            item, depth = stack.pop()
            nodes += 1
            if depth > 24 or nodes > 65536:
                refuse('SIM_RESOURCE_LIMIT', 0, target, 4)
            if isinstance(item, dict):
                stack.extend((x, depth + 1) for pair in item.items() for x in pair)
            elif isinstance(item, list):
                stack.extend((x, depth + 1) for x in item)
            elif isinstance(item, str) and len(item.encode('utf-8')) > 4096:
                # The legacy prior closure is opaque carriage, not parsed here.
                refuse('SIM_RESOURCE_LIMIT', 0, target, 4)
        if canonical_bytes(value) != wire:
            refuse('SIM_SCHEMA_INVALID', 0, target)
    except RecursionError:
        refuse('SIM_RESOURCE_LIMIT', 0, target, 4)
    except (UnicodeError, ValueError, TypeError):
        refuse('SIM_SCHEMA_INVALID', 0, target)
    if kind == 'nm.evidence.v1':
        return value, None
    if kind.startswith('ct.t1-'):
        found = validate(value, kind, target)
        prefix = target.rstrip('/')
        found.refs = [(p[len(prefix):], r, allowed, edge) for p, r, allowed, edge in found.refs]
        found.roles = [(p[len(prefix):], r, allowed) for p, r, allowed in found.roles]
    else:
        try:
            found = inherited.validate(value, kind)
        except inherited.CheckedRefusal as error:
            refuse('SIM_SCHEMA_INVALID', 0, target + error.target.rstrip('/'))
    if value.get('schema') != kind:
        refuse('SIM_REFERENCE_INVALID', 1, target)
    if kind == 'ct.t1-simulation-target.v1':
        start, end = instant(value['window']['from']), instant(value['window']['to'])
        if end - start != timedelta(seconds=120) or instant(value['t0']) != start:
            refuse('SIM_SCHEMA_INVALID', 0, '/J/window')
        if value['question_as_of'] != value['window']['to']:
            refuse('SIM_SCHEMA_INVALID', 0, '/J/question_as_of')
    return value, found


def _declared_caps(value, node):
    """Reference cap comes from the governing field's target, not the asserted kind."""
    if '$ref' in node:
        child = SCHEMAS
        for part in node['$ref'][2:].split('/'):
            child = child[part]
        yield from _declared_caps(value, child)
    if 'x-target' in node and isinstance(value, dict) and isinstance(value.get('sha256'), str):
        kinds = node['x-target']
        # Multiple target alternatives all use the generic cap in this edition.
        yield value['sha256'], min(CAPS.get(k, GENERIC_CAP) for k in kinds), kinds[0]
    for name in ('allOf', 'anyOf', 'oneOf'):
        for child in node.get(name, []):
            yield from _declared_caps(value, child)
    if isinstance(value, dict):
        for key, child in node.get('properties', {}).items():
            if key in value:
                yield from _declared_caps(value[key], child)
    if isinstance(value, list) and 'items' in node:
        for item in value:
            yield from _declared_caps(item, node['items'])


def locate_roots(objects, kinds=('ct.t1-simulation-target.v1', 'ct.authority.v1',
                                 'ct.t1-simulation-permission.v1')):
    """Intake 1–5, including all candidates before presence/multiplicity checks."""
    roots = {kind: [] for kind in kinds}
    claims = {}
    lengths = {digest: len(wire) for digest, wire in sorted(objects.items())}
    for digest, wire in sorted(objects.items()):
        if len(wire) <= GENERIC_CAP:
            try:
                value = json.loads(wire)
                kind = value.get('schema') if isinstance(value, dict) else None
                claims[digest] = value
                if kind in roots:
                    roots[kind].append(digest)
            except (ValueError, UnicodeError, RecursionError):
                pass
    for kind, candidates in roots.items():
        for digest in candidates:
            if lengths[digest] > CAPS.get(kind, GENERIC_CAP):
                refuse('SIM_RESOURCE_LIMIT', 0, '/' + LETTERS[kind], 4)
            schema = SCHEMAS['records'].get(kind, inherited.SCHEMAS['records'].get(kind))
            for rr_digest, cap, rr_kind in _declared_caps(claims[digest], schema):
                if rr_digest in lengths and lengths[rr_digest] > cap:
                    refuse('SIM_RESOURCE_LIMIT', 0, '/' + LETTERS.get(rr_kind, rr_kind), 4)
    for digest, length in lengths.items():
        if length > GENERIC_CAP:
            refuse('SIM_RESOURCE_LIMIT', 0, '/objects/' + digest, 4)
    return roots


@dataclass
class Admission:
    objects: dict
    records: dict
    references: dict
    prior_files: dict
    prior_digests: set
    build: object

    def get(self, reference):
        digest = reference['sha256']
        if digest not in self.records:
            refuse('SIM_REFERENCE_MISSING', 1, '/' + LETTERS.get(reference['kind'], reference['kind']))
        value = self.records[digest]
        if value.get('schema') != reference['kind']:
            refuse('SIM_REFERENCE_INVALID', 1, '/' + LETTERS.get(reference['kind'], reference['kind']))
        return value

    def root(self, letter):
        return self.get(self.references[letter])


def _equal(actual, expected, order, target, code):
    if actual != expected:
        refuse(code, order, target)


def preflight(*, objects, prior_files, pins, prior_pins, build, prepare=False, checker=False):
    """Orders 0–6. Does not derive r until all earlier orders have passed."""
    root_kinds = ('ct.t1-simulation-target.v1',) if prepare else (
        'ct.t1-simulation-target.v1', 'ct.authority.v1', 'ct.t1-simulation-permission.v1')
    candidates = locate_roots(objects, root_kinds)
    roots, records, annotations = {}, {}, {}
    # Order 0 shapes precede every pin check.
    for kind in root_kinds:
        for digest in candidates[kind]:
            records[digest], annotations[digest] = parse(objects[digest], kind, '/' + LETTERS[kind])
    for kind in root_kinds:
        letter = LETTERS[kind]
        if not candidates[kind]:
            refuse('SIM_REFERENCE_MISSING', 1, '/' + letter)
        if len(candidates[kind]) != 1:
            refuse('SIM_REFERENCE_INVALID', 1, '/' + letter)
        digest = candidates[kind][0]
        if not prepare and digest != pins[letter]:
            refuse('SIM_PIN_MISMATCH', 1, '/' + letter)
        roots[letter] = {'kind': kind, 'sha256': digest}
    pool = dict(objects)
    prior_digests = {sha(wire) for wire in prior_files.values()}
    for wire in prior_files.values():
        pool[sha(wire)] = wire
    # Prior material can be recovered, without importing its internal refs into M.
    try:
        for item in json.loads(prior_files['closure.json'])['members']:
            wire = base64.b64decode(item['data'], validate=True)
            if sha(wire) != item['sha256']:
                refuse('SIM_PRIOR_MISMATCH', 2, '/prior/closure.json')
            pool.setdefault(item['sha256'], wire)
    except (KeyError, ValueError, TypeError):
        refuse('SIM_PRIOR_MISMATCH', 2, '/prior/closure.json')
    pending = [(r, '/' + letter) for letter, r in roots.items()]
    seen = set()
    while pending:
        reference, target = pending.pop(0)
        digest, kind = reference['sha256'], reference['kind']
        if digest not in pool:
            refuse('SIM_REFERENCE_MISSING', 1, target)
        if sha(pool[digest]) != digest:
            refuse('SIM_REFERENCE_INVALID', 1, target)
        if digest in seen:
            if records.get(digest, {}).get('schema') != kind:
                refuse('SIM_REFERENCE_INVALID', 1, target)
            continue
        seen.add(digest)
        if digest in prior_digests:
            # Prior file edges are recomputed from the prior manifest, not its records.
            records[digest] = json.loads(pool[digest])
            if records[digest].get('schema') != kind:
                refuse('SIM_REFERENCE_INVALID', 1, target)
            if kind == 'ct.bundle-manifest.v1':
                for i, entry in enumerate(records[digest]['files']):
                    name = entry['name']
                    if name not in prior_files or sha(prior_files[name]) != entry['sha256']:
                        refuse('SIM_REFERENCE_INVALID', 1, '/prior/' + name)
                    pending.append(({'kind': json.loads(prior_files[name])['schema'],
                                     'sha256': entry['sha256']}, target + '/files/' + str(i)))
            continue
        value, found = parse(pool[digest], kind, target)
        records[digest], annotations[digest] = value, found
        if found:
            for path, provenance, allowed in found.roles:
                if provenance['role'] not in allowed:
                    refuse('SIM_REFERENCE_INVALID', 1, target + path + '/role')
            for path, rr, allowed, _edge in sorted(found.refs, key=lambda row: row[0]):
                if rr['kind'] not in allowed:
                    refuse('SIM_REFERENCE_INVALID', 1, target + path)
                # E/G joins compare digests in order 3 rather than resolving substitutions.
                if kind in ('ct.authority.v1', 'ct.t1-simulation-permission.v1') and path != '/predecessor':
                    continue
                pending.append((rr, target + path))
    extra = sorted(set(objects) - seen)
    if extra:
        refuse('SIM_REFERENCE_INVALID', 1, '/objects/' + extra[0])
    for digest, value in records.items():
        if 'predecessor' not in value:
            continue
        predecessor = value['predecessor']
        target = '/' + LETTERS.get(value['schema'], value['schema']) + '/predecessor'
        if (value['revision'] == 1) != (predecessor is None):
            refuse('SIM_REFERENCE_INVALID', 1, target)
        if predecessor is not None:
            previous = records[predecessor['sha256']]
            if previous['schema'] != value['schema'] or previous['id'] != value['id'] or \
                    previous['revision'] != value['revision'] - 1:
                refuse('SIM_REFERENCE_INVALID', 1, target)
    admitted = Admission({d: pool[d] for d in seen | prior_digests}, records, roots,
                         prior_files, prior_digests, build)
    _orders_2_to_6(admitted, prior_pins, prepare=prepare, checker=checker)
    return admitted


def _orders_2_to_6(a, prior_pins, *, prepare, checker=False):
    j = a.root('J')
    w, c, rule, policy = (a.get(j[k]) for k in ('world', 'context', 'rule', 'simulator_policy'))
    x = a.get(j['execution_target'])
    model, plan = a.get(x['model']), a.get(x['interpretation_plan'])
    baseline = a.get(model['baseline_evidence'])
    captured = a.get(j['captured_policy'])
    try:
        build_wire = a.build.wire()
    except inherited.CheckedRefusal:
        refuse('SIM_BUILD_UNAVAILABLE', 2, '/checker_build' if checker else '/producer_build')
    bd = sha(build_wire)
    for actual, expected, target in (
            (j['producer_build']['sha256'], bd, '/J/producer_build'),
            (j['rule']['sha256'], RULE_SHA256, '/rule'),
            (policy['rule'], j['rule'], '/simulator_policy/rule'),
            (policy['preset_sha256'], PRESET_SHA256, '/preset'),
            (j['companion_schemas_sha256'], SCHEMAS_SHA256, '/J/companion_schemas_sha256')):
        _equal(actual, expected, 2, target, 'SIM_EDITION_NOT_PERMITTED')
    if bd not in policy['permitted_producer_builds'] or bd not in captured['permitted_builds'] or \
            policy['companion_schemas_sha256'] != SCHEMAS_SHA256:
        refuse('SIM_EDITION_NOT_PERMITTED', 2, '/producer_build')
    if checker and bd not in policy['permitted_checker_builds']:
        refuse('SIM_EDITION_NOT_PERMITTED', 2, '/checker_build')
    if any('0' * 64 in policy[key] for key in ('permitted_producer_builds', 'permitted_checker_builds')):
        refuse('SIM_EDITION_NOT_PERMITTED', 2, '/simulator_policy')
    _equal(j['captured_policy']['sha256'], sha(a.prior_files['policy.json']), 2, '/captured_policy',
           'SIM_EDITION_NOT_PERMITTED')
    _equal(captured['unresolved_allowlist'], [], 2, '/captured_policy/unresolved_allowlist',
           'SIM_EDITION_NOT_PERMITTED')
    preset = a.get(c['preset'])
    _equal(c['preset'], rule['preset'], 2, '/preset', 'SIM_EDITION_NOT_PERMITTED')
    from .t1_carrier import carrier_bytes
    for name in ('server_info', 'printer_objects'):
        # Reparse numeric leaves exactly from their pinned record, never binary floats.
        exact = json.loads(a.objects[c['preset']['sha256']], parse_float=Fraction)
        _equal(sha(carrier_bytes(exact['responses'][name]['body'])), preset['body_digests'][name],
               2, '/preset/body_digests/' + name, 'SIM_EDITION_NOT_PERMITTED')
    for key, bound in j['resource_bounds'].items():
        maximum = policy['resource_maxima'][key]
        if isinstance(bound, dict):
            over = any(v > maximum[k] for k, v in bound.items())
        else:
            over = bound > maximum
        if over:
            refuse('SIM_EDITION_NOT_PERMITTED', 2, '/J/resource_bounds/' + key)
    from . import checked_runtime
    try:
        checked_runtime.verify(bundle_files=a.prior_files, request_pin=prior_pins['request_sha256'],
                               authority_pin=prior_pins['authority_sha256'], build=a.build)
    except inherited.CheckedRefusal as error:
        refuse('SIM_PRIOR_MISMATCH', 2, '/prior')
    start, end = instant(j['window']['from']), instant(j['window']['to'])
    if not prepare:
        e, g = a.root('E'), a.root('G')
        for actual, expected, target in ((e['purpose'], 'execution', '/E/purpose'),
                (e['target'], j['execution_target'], '/E/target'), (g['target'], a.references['J'], '/G/target'),
                (g['execution_authority'], a.references['E'], '/G/execution_authority')):
            _equal(actual, expected, 3, target, 'SIM_PERMISSION_TARGET_MISMATCH')
        if e['scope']['phase'] != 'reassessment' or inherited.T1 not in e['scope']['procedure_editions']:
            refuse('SIM_PERMISSION_SCOPE_MISMATCH', 3, '/E/scope')
        _equal(e['plan_change'], None, 3, '/E/plan_change', 'SIM_PERMISSION_SCOPE_MISMATCH')
        for letter, authority in (('E', e), ('G', g)):
            if instant(authority['valid']['from']) > start or instant(authority['valid']['to']) < end:
                refuse('SIM_PERMISSION_SCOPE_MISMATCH', 3, '/' + letter + '/valid')
            if letter == 'G':
                for key in ('rule', 'simulator_policy', 'producer_build', 'captured_policy'):
                    _equal(g['scope'][key], j[key], 3, '/G/scope/' + key, 'SIM_PERMISSION_SCOPE_MISMATCH')
    for key, expected in (('selection_basis', 'inherited'), ('plan_change', None),
                          ('procedure_edition', inherited.T1)):
        _equal(x[key], expected, 4, '/X/' + key, 'SIM_EXECUTION_JOIN_MISMATCH')
    prior_model = json.loads(a.prior_files['derivation.json'])['model']
    _equal(x['model'], prior_model, 4, '/X/model', 'SIM_EXECUTION_JOIN_MISMATCH')
    _equal(x['prior_selection']['manifest']['sha256'], sha(a.prior_files['manifest.json']),
           4, '/X/prior_selection', 'SIM_EXECUTION_JOIN_MISMATCH')
    _equal(x['prior_selection']['selection']['sha256'], sha(a.prior_files['result.json']),
           4, '/X/prior_selection', 'SIM_EXECUTION_JOIN_MISMATCH')
    selected_plan = next(p['interpretation_plan'] for p in model['procedures'] if p['edition'] == inherited.T1)
    _equal(x['interpretation_plan'], selected_plan, 4, '/X/interpretation_plan', 'SIM_EXECUTION_JOIN_MISMATCH')
    for letter, value in (('X', x), ('P0', plan), ('J', j), ('W', w)):
        _equal(value['instrument_id'], model['reference_instrument_id'], 4, '/' + letter + '/instrument_id',
               'SIM_EXECUTION_JOIN_MISMATCH')
    _equal(w['source'], {'source_id': c['source_definition']['source_id'], 'adapter_id': 'moonraker'},
           4, '/W/source', 'SIM_EXECUTION_JOIN_MISMATCH')
    if start < instant(model['context']['as_of']):
        refuse('SIM_EXECUTION_JOIN_MISMATCH', 4, '/J/window/from')
    from backend.model_kernel import ModelQueryMaterial
    try:
        ModelQueryMaterial.model_validate(c['material']).loaded()
    except ValueError:
        refuse('SIM_MODEL_MATERIAL_MISMATCH', 4, '/C/material')
    _equal(c['material']['revision']['revision_id'], REVISION, 4, '/C/material/revision',
           'SIM_MODEL_MATERIAL_MISMATCH')
    _equal(c['material']['revision']['revision_id'], model['context']['structural_model_revision'],
           4, '/C/material/revision', 'SIM_MODEL_MATERIAL_MISMATCH')
    _equal(c['material'], baseline['snapshot']['state']['material'], 4, '/C/material',
           'SIM_MODEL_MATERIAL_MISMATCH')
    _equal(c['assertion_context'], model['context']['assertion_context'], 4, '/C/assertion_context',
           'SIM_MODEL_MATERIAL_MISMATCH')
    for key, expected in (('intended_subject_entity_anchor_id', SUBJECT),
                          ('intended_variable_anchor_id', VARIABLE), ('unit', 'degree_celsius')):
        _equal(w[key], expected, '4a', '/W/' + key, 'SIM_CONTEXT_MISMATCH')
        if key != 'unit':
            anchor_key = key.removeprefix('intended_')
            _equal(w[key], model['context'][anchor_key], '4a', '/W/' + key, 'SIM_CONTEXT_MISMATCH')
            _equal(w[key], baseline['binding'][anchor_key], '4a', '/W/' + key, 'SIM_CONTEXT_MISMATCH')
    d = min(6, captured['limits']['fractional_digits'])
    domains = {'theta': (-200, 1000), 'beta': (-10, 10), 'epsilon': (-5, 5), 'baseline_theta': (-200, 1000)}
    for key, (lo, hi) in domains.items():
        if not lo <= Fraction(w[key]) <= hi:
            refuse('SIM_WORLD_DOMAIN', 5, '/W/' + key)
    for key in domains:
        if 10 ** d % Fraction(w[key]).denominator:
            refuse('SIM_PRECISION_LIMIT', 5, '/W/' + key)
    reading = sum((Fraction(w[k]) for k in ('theta', 'beta', 'epsilon')), Fraction())
    if not -200 <= reading <= 1000:
        refuse('SIM_WORLD_DOMAIN', 5, '/r')
    if 10 ** d % reading.denominator:
        refuse('SIM_PRECISION_LIMIT', 5, '/r')
    # Port and display name are supplied within the closed governing source schema.
    # They are not fixed by the historical test fixture.
    fixed = [('reading_locator', baseline['snapshot']['condition_sources'][0]['source']),
             ('intended_subject_entity_anchor_id', SUBJECT), ('intended_variable_anchor_id', VARIABLE)]
    fixed.extend((key, baseline['binding'][key]) for key in (
        'expected_quantity_kind', 'expected_observation_role', 'expected_unit'))
    fixed.extend((('constraint_anchor_id', baseline['binding']['constraint_anchor_id']),
                  ('state_anchor_id', baseline['question']['state_anchor_id'])))
    for key, expected in fixed:
        _equal(c[key], expected, 6, '/C/' + key, 'SIM_MEASUREMENT_LOCATOR_MISMATCH')
    from .t1_acquisition import validate_context
    validate_context(c, start, end)
    _equal(c['condition_sources'], baseline['snapshot']['condition_sources'], 6, '/C/condition_sources',
           'SIM_CONTEXT_MISMATCH')
