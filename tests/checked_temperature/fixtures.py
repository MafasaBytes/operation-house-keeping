"""Complete, hash-consistent checked-temperature fixtures (no placeholders).

Every referenced object exists and every digest is recomputed from canonical
bytes. Baseline and result public evidence is the genuine committed
`nm.evidence.v1` object from the 2026-09-19 next-measurement preparation
capture (read-only historical evidence). Claim cores are written here
independently of the application so tests cross-check its derivation.

TEST DOUBLE: `TestDoubleBuild` is NOT an executable identity. Its record is
schema-shaped (the schema forces `clean_application_backend: true`) but every
identity field is an explicit all-zero / TEST_DOUBLE marker. It exists only so
in-process unit tests can exercise permitted-build logic; it proves nothing
about a clean build.
"""
import base64
import copy
import hashlib
import json
from pathlib import Path

from applications.bounded_decision_workflow.checked_contracts import (
    EDITION_LIMITS, POLICY_EDITION_SHA256, SCHEMAS_SHA256, T1, T2)

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / 'docs/superpowers/reports/2026-09-19-next-measurement-preparation/inputs/A-restored/capture.json'
PROFILE = 'bdw.checked-temperature.v1'
REF_INST = 'inst_' + 'a' * 32
IND_INST = 'inst_' + 'b' * 32
CONTEXT = {'as_of': '2026-08-07T20:30:00Z',
           'assertion_context': {'kind': 'lifecycle_view', 'view': 'as_operated'},
           'scenario_label': 'ct-gate1-fixture',
           'subject_entity_anchor_id': 'ent_' + '9' * 32,
           'variable_anchor_id': 'var_' + '1' * 32,
           'structural_model_revision': 'mrv_d93f49fd3a20eabde14c2015430e8382b374d51b6a63cadb5e7eb9dbaad5e5e4'}
WIDE = {'from': '2026-08-01T00:00:00Z', 'to': '2026-12-31T00:00:00Z'}
A1_ALLOWLIST = [{'condition': c, 'phase': p} for c in ('reference_calibration', 'reference_mapping', 'state_hold')
                for p in ('selection', 'reassessment')]


def canon(v):
    return json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def r(n, d=1):
    from math import gcd
    g = gcd(abs(n), d)
    return {'numerator': str(n // g), 'denominator': str(d // g)}


def ref(kind, digest):
    return {'kind': kind, 'sha256': digest}


def prov(role):
    return {'role': role, 'label': 'gate1 test fixture', 'authenticated': False,
            'basis': 'synthetic Gate 1 unit-test fixture'}


def public_evidence_bytes():
    capture = json.loads(CAPTURE.read_bytes())
    for m in capture['members']:
        if m['reference']['kind'] == 'nm.evidence.v1':
            data = base64.b64decode(m['bytes'])
            assert sha(data) == m['reference']['sha256']
            return data
    raise AssertionError('committed public evidence not found')


class TestDoubleBuild:
    """TEST DOUBLE build provider — not an executable identity (see module doc)."""

    __test__ = False

    def __init__(self, marker='0'):
        self.record = {
            'schema': 'ct.build.v1', 'profile': PROFILE, 'checkpoint': marker * 40,
            'clean_application_backend': True,
            'source_manifest': [{'path': 'applications/TEST_DOUBLE_NOT_AN_EXECUTABLE_IDENTITY',
                                 'sha256': marker * 64, 'bytes': 0}],
            'environment_manifest': {
                'python': {'implementation': 'CPython', 'version': '3.13.0', 'executable_sha256': marker * 64,
                           'executable_bytes': 1},
                'platform': {'system': 'TEST_DOUBLE', 'machine': 'TEST_DOUBLE', 'libc': ['TEST_DOUBLE', '0']},
                'distributions': [], 'dependency_lock_sha256': marker * 64},
            'contract_editions': {'schemas_sha256': SCHEMAS_SHA256, 'policy_edition_sha256': POLICY_EDITION_SHA256,
                                  'catalogue': 'ct.conditions.v2', 'calculator': 'ct.calculator.v1'}}

    def wire(self):
        return canon(self.record)

    @property
    def digest(self):
        return sha(self.wire())


class World:
    """A content-addressed object store plus named handles for twins."""

    def __init__(self):
        self.objects = {}
        self.h = {}

    def put(self, value, name=None):
        if isinstance(value, bytes):
            data, kind = value, 'ct.evidence-content'
        else:
            data, kind = canon(value), value['schema']
        d = sha(data)
        self.objects[d] = data
        rr = ref(kind, d)
        if name:
            self.h[name] = (rr, value)
        return rr

    def clone(self):
        other = World()
        other.objects = dict(self.objects)
        other.h = copy.deepcopy(self.h)
        other.build = self.build
        return other

    def replace(self, name, value):
        """Swap a named object for a new version, dropping the old bytes."""
        old = self.h[name][0]['sha256']
        self.objects.pop(old, None)
        return self.put(value, name)

    def value(self, name):
        return copy.deepcopy(self.h[name][1])

    def refof(self, name):
        return self.h[name][0]


def claim(*, model_ref, procedure, phase, condition, params):
    return {'schema': 'ct.claim.v1', 'profile': PROFILE, 'catalogue': 'ct.conditions.v2',
            'procedure_edition': procedure, 'phase': phase, 'model': model_ref,
            'subject_entity_anchor_id': CONTEXT['subject_entity_anchor_id'],
            'variable_anchor_id': CONTEXT['variable_anchor_id'],
            'binding': {'condition': condition, 'parameters': params}}


def claim_params(condition, *, model, plan_ref=None, plan=None):
    if condition == 'reference_calibration':
        return {'instrument_id': model['reference_instrument_id'], 'b_ref': model['b_ref']}
    if condition == 'reference_mapping':
        return {'instrument_id': model['reference_instrument_id'],
                'structural_model_revision': CONTEXT['structural_model_revision'],
                'subject_entity_anchor_id': CONTEXT['subject_entity_anchor_id'],
                'variable_anchor_id': CONTEXT['variable_anchor_id']}
    if condition == 'state_hold':
        return {'baseline_as_of': CONTEXT['as_of'],
                'b_suspect': [{'explanation': h['explanation'], 'interval': h['b_suspect']}
                              for h in model['hypotheses']]}
    if condition == 'indicator_fidelity':
        t2 = [p for p in model['procedures'] if p['edition'] == T2][0]
        return {'instrument_id': t2['indicator_instrument_id'], 'target': t2['target']}
    return {'instrument_id': plan['instrument_id'], 'plan': plan_ref, 'half_width': plan['half_width']}


CONDITIONS = {T1: ('reference_calibration', 'reference_mapping', 'state_hold', 'observation_error_bound'),
              T2: ('state_hold', 'indicator_fidelity')}


def support_graph(w, claim_ref, tag, *, review=True, relation='support'):
    """One true declaration, one evidence item and (optionally) one completed review."""
    decl = w.put({'schema': 'ct.condition-declaration.v1', 'profile': PROFILE, 'id': 'decl-' + tag, 'revision': 1,
                  'predecessor': None, 'provenance': prov('local_condition_declarer'), 'claim': claim_ref,
                  'state': 'true', 'rationale': 'fixture declaration', 'covers': WIDE}, 'decl-' + tag)
    content = w.put(('fixture evidence content for %s' % tag).encode())
    item = w.put({'schema': 'ct.evidence-item.v1', 'profile': PROFILE, 'id': 'item-' + tag, 'revision': 1,
                  'predecessor': None, 'provenance': prov('local_evidence_reviewer'), 'claims': [claim_ref],
                  'content': content, 'validity': None, 'subject_entity_anchor_id': None,
                  'variable_anchor_id': None, 'instrument_id': None}, 'item-' + tag)
    out = {'declarations': [decl], 'evidence_items': [item], 'reviews': []}
    if review:
        out['reviews'].append(w.put({
            'schema': 'ct.evidence-review.v1', 'profile': PROFILE, 'id': 'review-' + tag, 'revision': 1,
            'predecessor': None, 'provenance': prov('local_evidence_reviewer'), 'item': item, 'claim': claim_ref,
            'completion': 'completed', 'relevance': 'relevant', 'relation': relation,
            'rationale': 'fixture review', 'covers': WIDE}, 'review-' + tag))
    return out


def base_world(*, h2=(5, 15), b_ref=((0, 1), (0, 1)), plan_w=(1, 2), t2_target=(60, 1), allowlist=None,
               build=None, plan_instrument=REF_INST):
    """Shared objects: explanations, plan, evidence, model, policy."""
    w = World()
    build = build or TestDoubleBuild()
    w.build = build
    h1 = w.put({'schema': 'ct.explanation.v1', 'profile': PROFILE, 'id': 'H1', 'revision': 1, 'predecessor': None,
                'provenance': prov('local_model_proposer'), 'account_kind': 'high_underlying_faithful_baseline',
                'statement': 'Underlying temperature equals the faithful baseline.', 'rationale': 'fixture',
                'context': CONTEXT}, 'H1')
    h2r = w.put({'schema': 'ct.explanation.v1', 'profile': PROFILE, 'id': 'H2', 'revision': 1, 'predecessor': None,
                 'provenance': prov('local_model_proposer'), 'account_kind': 'low_underlying_positive_offset',
                 'statement': 'Underlying temperature is below the suspect baseline by a positive offset.',
                 'rationale': 'fixture', 'context': CONTEXT}, 'H2')
    plan_ref = None
    if plan_w is not None:
        plan_ref = w.put({'schema': 'ct.interpretation-plan.v1', 'profile': PROFILE, 'id': 'plan-P0', 'revision': 1,
                          'predecessor': None, 'provenance': prov('local_model_proposer'),
                          'edition': 'ct.interpretation.hard-interval.v1', 'instrument_id': plan_instrument,
                          'half_width': r(*plan_w), 'unit': 'degree_celsius'}, 'P0')
    evidence = w.put(json.loads(public_evidence_bytes()), 'evidence')
    model = {'schema': 'ct.model.v1', 'profile': PROFILE, 'id': 'model', 'revision': 1, 'predecessor': None,
             'provenance': prov('local_model_proposer'), 'template_edition': 'ct.template.two-account-temperature.v1',
             'calculator_edition': 'ct.calculator.v1', 'baseline': r(601, 10), 'baseline_verdict': 'violated',
             'baseline_evidence': evidence,
             'hypotheses': [{'explanation': h1, 'b_suspect': {'lo': r(0), 'hi': r(0)}},
                            {'explanation': h2r, 'b_suspect': {'lo': r(h2[0]), 'hi': r(h2[1])}}],
             'b_ref': {'lo': r(*b_ref[0]), 'hi': r(*b_ref[1])}, 'reference_instrument_id': REF_INST,
             'reference_mapping_provenance': 'declared using the suspect sensor path (fixture)',
             'procedures': [{'edition': T1, 'interpretation_plan': plan_ref},
                            {'edition': T2, 'target': r(*t2_target), 'indicator_instrument_id': IND_INST}],
             'context': CONTEXT}
    w.put(model, 'model')
    w.put({'schema': 'ct.policy.v1', 'profile': PROFILE, 'id': 'policy', 'revision': 1, 'predecessor': None,
           'provenance': prov('local_policy_owner'), 'edition': 'ct.policy-edition.v4', 'catalogue': 'ct.conditions.v2',
           # Explicit empty allowlist is the recorded default choice; A1 only where a case names it.
           'unresolved_allowlist': [] if allowlist is None else allowlist,
           'permitted_builds': [build.digest], 'limits': dict(EDITION_LIMITS), 'required_reviews_per_item': 1},
          'policy')
    return w


def phase_graph(w, phase, procedures, *, plan_name='P0', skip=(), relation=None, no_review=(), no_item=(), omit=()):
    """Required claims for a phase plus one supported declaration/item/review each.

    skip: claim only; no_item: declaration only; no_review: declaration + unreviewed item.
    """
    model_ref, model = w.refof('model'), w.value('model')
    plan_ref, plan = (w.refof(plan_name), w.value(plan_name)) if plan_name in w.h else (None, None)
    graph = {'claims': [], 'declarations': [], 'evidence_items': [], 'reviews': []}
    for p in procedures:
        for c in CONDITIONS[p]:
            if c == 'observation_error_bound' and plan_ref is None:
                continue
            if c == 'indicator_fidelity' and not any(x['edition'] == T2 for x in model['procedures']):
                continue
            if c in omit:   # required claim core neither supplied nor declared
                continue
            cr = w.put(claim(model_ref=model_ref, procedure=p, phase=phase, condition=c,
                             params=claim_params(c, model=model, plan_ref=plan_ref, plan=plan)),
                       'claim-%s-%s-%s' % (phase, p[-5:-3], c))
            graph['claims'].append(cr)
            if c in skip:
                continue
            g = support_graph(w, cr, '%s-%s-%s' % (phase, p[-5:-3], c),
                              relation=(relation or {}).get(c, 'support'), review=c not in no_review)
            if c in no_item:   # declaration only: remove the item, its content and its review entirely
                for x in g['evidence_items'] + g['reviews']:
                    v = json.loads(w.objects.pop(x['sha256']))
                    if v['schema'] == 'ct.evidence-item.v1':
                        w.objects.pop(v['content']['sha256'])
                g['evidence_items'], g['reviews'] = [], []
            for k in ('declarations', 'evidence_items', 'reviews'):
                graph[k] += g[k]
    return graph


def selection_request(w, graph, *, as_of='2026-10-04T12:00:00Z', rid='request-S'):
    return {'schema': 'ct.request.v1', 'profile': PROFILE, 'id': rid, 'revision': 1, 'predecessor': None,
            'provenance': prov('local_model_proposer'), 'model': w.refof('model'),
            'claims': sorted(graph['claims'], key=lambda x: x['sha256']),
            'declarations': sorted(graph['declarations'], key=lambda x: x['sha256']),
            'evidence_items': sorted(graph['evidence_items'], key=lambda x: x['sha256']),
            'reviews': sorted(graph['reviews'], key=lambda x: x['sha256']),
            'policy': w.refof('policy'), 'purpose': 'selection', 'as_of': as_of}


def authority(*, purpose, target, phase, procedures, plan_change=None, aid=None,
              valid=None, role=None):
    return {'schema': 'ct.authority.v1', 'profile': PROFILE, 'id': aid or ('auth-%s-%s' % (purpose, phase)),
            'revision': 1, 'predecessor': None,
            'provenance': prov(role or ('local_evaluation_issuer' if purpose == 'evaluation'
                                        else 'local_execution_issuer')),
            'purpose': purpose, 'target': target, 'scope': {'phase': phase, 'procedure_editions': procedures},
            'plan_change': plan_change, 'valid': valid or {'from': '2026-10-01T00:00:00Z', 'to': '2026-10-31T00:00:00Z'}}


class Case:
    """Request wire, objects and the external pins for one invocation."""

    def __init__(self, world, request, auth):
        self.world = world
        self.request = request
        self.request_wire = canon(request)
        self.request_pin = sha(self.request_wire)
        self.auth = auth
        self.authority_pin = world.put(auth, 'A')['sha256'] if auth is not None else None
        self.objects = {d: b for d, b in world.objects.items() if d != self.request_pin}


def fx1(*, phase_kw=None, extra_graph=None, model_edit=None, policy_edit=None, as_of='2026-10-04T12:00:00Z',
        auth_valid=None, **kw):
    """FX1: the common selection baseline (plan w=1/2, every required claim supported)."""
    w = base_world(**kw)
    if model_edit:
        model = w.value('model')
        model_edit(model, w)
        w.replace('model', model)
    if policy_edit:
        policy = w.value('policy')
        policy_edit(policy)
        w.replace('policy', policy)
    graph = phase_graph(w, 'selection', [T1, T2], **(phase_kw or {}))
    if extra_graph:
        for k, v in extra_graph(w).items():
            graph[k] = graph[k] + v
    return selection_case(w, graph, as_of=as_of, auth_valid=auth_valid)


def selection_case(w, graph, *, as_of='2026-10-04T12:00:00Z', auth_valid=None):
    request = selection_request(w, graph, as_of=as_of)
    rref = w.put(request, 'S')
    auth = authority(purpose='evaluation', target=rref, phase='selection', procedures=[T1, T2],
                     aid='auth-eval-S', valid=auth_valid)
    return Case(w, request, auth)


def selection_objects(case):
    return dict(case.objects)


def _normal(decimal_text):
    from decimal import Decimal
    return format(Decimal(decimal_text).normalize(), 'f')


def code_evidence(w, *, code='heater_off', instrument=IND_INST, observed_at='2026-10-05T09:02:00Z', tag='1'):
    content = w.put(('raw indicator record %s %s (fixture)' % (code, tag)).encode())
    return w.put({'schema': 'ct.code-evidence.v1', 'profile': PROFILE, 'id': 'code-evidence-' + tag, 'revision': 1,
                  'predecessor': None, 'provenance': prov('local_evidence_reviewer'), 'instrument_id': instrument,
                  'code': code, 'observed_at': observed_at, 'content': content}, 'code-evidence-' + tag)


def co1(prior_files, base, *, scalar='60.0', procedure=T1, code=None, selection_basis='inherited',
        new_plan_w=None, mutate=None, phase_kw=None, extra_graph=None, evidence=None, evidence_value=None):
    """`evidence`: None = genuine-derivation value evidence (T1) / code evidence (T2);
    'baseline' = reuse the model baseline evidence; a callable(w) returning a reference."""
    """CO1 construction order: X -> E -> O -> R -> A, against prior bundle files.

    Works on a clone of the base world so twins never leak objects into each other.
    """
    w = base.world.clone()
    manifest_ref = ref('ct.bundle-manifest.v1', sha(prior_files['manifest.json']))
    result_entry = [f for f in json.loads(prior_files['manifest.json'])['files'] if f['name'] == 'result.json'][0]
    prior_selection = {'manifest': manifest_ref, 'selection': ref('ct.selection.v1', result_entry['sha256'])}
    plan_change = None
    plan_name = 'P0'
    if selection_basis != 'inherited':
        w.put({'schema': 'ct.interpretation-plan.v1', 'profile': PROFILE, 'id': 'plan-P1', 'revision': 1,
               'predecessor': None, 'provenance': prov('local_model_proposer'),
               'edition': 'ct.interpretation.hard-interval.v1', 'instrument_id': REF_INST,
               'half_width': r(*new_plan_w), 'unit': 'degree_celsius'}, 'P1')
        plan_change = {'former_plan': w.refof('P0'), 'new_plan': w.refof('P1'), 'reason': 'newly scoped plan'}
        plan_name = 'P1'
    plan_ref = w.refof(plan_name) if procedure == T1 else None
    if evidence == 'baseline':
        ev_ref = w.refof('evidence')
    elif callable(evidence):
        ev_ref = evidence(w)
    elif procedure == T1:   # amendment C1: coherent later-chain evidence inside the acquisition window
        from tests.checked_temperature.later_chain import later_evidence_bytes
        ev_ref = w.put(json.loads(later_evidence_bytes(_normal(evidence_value or scalar))), 'result-evidence')
    else:
        ev_ref = code_evidence(w, code=code)
    spec = {'X': {'schema': 'ct.execution-target.v1', 'profile': PROFILE, 'id': 'xt-1', 'revision': 1,
                  'predecessor': None, 'provenance': prov('local_model_proposer'),
                  'prior_selection': prior_selection, 'selection_basis': selection_basis,
                  'plan_change': plan_change, 'model': w.refof('model'), 'procedure_edition': procedure,
                  'instrument_id': w.value(plan_name)['instrument_id'] if procedure == T1 else IND_INST,
                  'interpretation_plan': plan_ref}}
    if mutate:
        mutate('X', spec['X'], w)
    xref = w.put(spec['X'], 'X')
    digests = None if plan_change is None else {'former_plan_sha256': plan_change['former_plan']['sha256'],
                                                'new_plan_sha256': plan_change['new_plan']['sha256']}
    spec['E'] = authority(purpose='execution', target=xref, phase='reassessment', procedures=[procedure],
                          plan_change=digests, aid='auth-exec-1',
                          valid={'from': '2026-10-05T08:00:00Z', 'to': '2026-10-05T18:00:00Z'})
    if mutate:
        mutate('E', spec['E'], w)
    eref = w.put(spec['E'], 'E')
    graph = phase_graph(w, 'reassessment', [procedure], plan_name=plan_name, **(phase_kw or {}))
    if extra_graph:
        for k, v in extra_graph(w).items():
            graph[k] = graph[k] + v
    obs = {'kind': 'scalar', 'scalar': scalar, 'unit': 'degree_celsius'} if procedure == T1 else \
        {'kind': 'code', 'code': code}
    spec['R'] = {'schema': 'ct.request.v1', 'profile': PROFILE, 'id': 'request-R', 'revision': 1,
                 'predecessor': None, 'provenance': prov('local_model_proposer'), 'model': w.refof('model'),
                 'claims': sorted(graph['claims'], key=lambda x: x['sha256']),
                 'declarations': sorted(graph['declarations'], key=lambda x: x['sha256']),
                 'evidence_items': sorted(graph['evidence_items'], key=lambda x: x['sha256']),
                 'reviews': sorted(graph['reviews'], key=lambda x: x['sha256']),
                 'policy': w.refof('policy'), 'purpose': 'reassessment', 'selection_basis': selection_basis,
                 'prior_selection': prior_selection, 'plan_change': plan_change, 'execution_target': xref,
                 'result': {'procedure_edition': procedure, 'observation': obs,
                            'acquisition': {'started': '2026-10-05T09:00:00Z', 'ended': '2026-10-05T09:05:00Z',
                                            'public_evidence': ev_ref,
                                            'instrument_id': spec['X']['instrument_id']},
                            'interpretation_plan': plan_ref, 'execution_authority': eref}}
    if mutate:
        mutate('R', spec['R'], w)
    rref = w.put(spec['R'], 'R')
    spec['A'] = authority(purpose='evaluation', target=rref, phase='reassessment', procedures=[procedure],
                          plan_change=digests, aid='auth-eval-R')
    if mutate:
        mutate('A', spec['A'], w)
    case = Case(w, spec['R'], spec['A'])
    case.spec = spec
    return case


# ------------------------------------------------------------ run helpers

STAMP = '2026-10-05T12:00:00Z'


def run_selection(case, *, build=None, objects=None):
    from applications.bounded_decision_workflow import checked_runtime as rt
    return rt.evaluate_selection(request_wire=case.request_wire,
                                 objects=case.objects if objects is None else objects,
                                 request_pin=case.request_pin, authority_pin=case.authority_pin,
                                 build=build or case.world.build, created_at=STAMP)


def run_reassessment(case, prior_files, *, build=None, objects=None, request_pin=None, authority_pin=None):
    from applications.bounded_decision_workflow import checked_runtime as rt
    return rt.evaluate_reassessment(request_wire=case.request_wire,
                                    objects=case.objects if objects is None else objects, prior_files=prior_files,
                                    request_pin=request_pin or case.request_pin,
                                    authority_pin=authority_pin or case.authority_pin,
                                    build=build or case.world.build, created_at=STAMP)


def run_verify(case, files, *, build=None, request_pin=None, authority_pin=None):
    from applications.bounded_decision_workflow import checked_runtime as rt
    return rt.verify(bundle_files=files, request_pin=request_pin or case.request_pin,
                     authority_pin=authority_pin or case.authority_pin, build=build or case.world.build)


def run_replay(case, files, *, build=None):
    from applications.bounded_decision_workflow import checked_runtime as rt
    return rt.replay(bundle_files=files, request_pin=case.request_pin, authority_pin=case.authority_pin,
                     build=build or case.world.build, created_at=STAMP)


def load(files, name):
    return json.loads(files[name])


def _swap_refs(value, mapping):
    if isinstance(value, dict):
        if set(value) == {'kind', 'sha256'} and value['sha256'] in mapping:
            return dict(value, sha256=mapping[value['sha256']])
        return {k: _swap_refs(v, mapping) for k, v in value.items()}
    if isinstance(value, list):
        return [_swap_refs(v, mapping) for v in value]
    return value


def rehash_bundle(files, **replace):
    """Harness mutation: replace record files, carry every changed digest into the
    downstream records that name it (result.json, then trace.json), then rewrite
    the manifest. The external pins are never changed."""
    files = dict(files)
    for name, value in replace.items():
        files[name.replace('_', '.', 1) if not name.endswith('.json') else name] = value
    manifest = json.loads(files['manifest.json'])
    old = {e['name']: e['sha256'] for e in manifest['files']}
    for downstream in ('result.json', 'trace.json'):
        mapping = {old[n]: sha(files[n]) for n in old if n not in ('manifest.json', downstream)
                   and old[n] != sha(files[n])}
        if mapping:
            files[downstream] = canon(_swap_refs(json.loads(files[downstream]), mapping))
    for entry in manifest['files']:
        data = files[entry['name']]
        entry['sha256'], entry['bytes'] = sha(data), len(data)
    files['manifest.json'] = canon(manifest)
    return files


def closure_with(files, mutate):
    """Harness mutation of closure.json members/roots, then rehash the manifest."""
    closure = json.loads(files['closure.json'])
    mutate(closure)
    closure['members'].sort(key=lambda m: (m['kind'], m['sha256']))
    out = dict(files)
    out['closure.json'] = canon(closure)
    return rehash_bundle(out)


def member(kind, data):
    return {'kind': kind, 'sha256': sha(data), 'decoded_bytes': len(data), 'encoding': 'base64',
            'data': base64.b64encode(data).decode('ascii')}
