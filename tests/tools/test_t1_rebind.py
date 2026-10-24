"""Tests for tools/fixtures/t1_rebind.py (t1-rebind.v1).

Written under the 2026-10-23 implementation grant and NOT RUN under it:
running them needs a separate owner grant. The governing specification is
docs/superpowers/reports/2026-10-22-t1-rebind-implementation-specification.md
(SHA-256 42d92411d35a3d7764930ac8867329e643e3442d95dba07f2789316b03a4ff61).
Owner dispositions A (literal provenance prose) and B (preflight versus
partial output) of 2026-10-23 supersede its contradictory wording.

Every authority, attestation and approval-shaped value here is TEST-ONLY
synthetic data: none is owner approval, an owner attestation or runtime
authority. The source chain is generated in tmp directories from the
maintained in-process fixtures (build 1 = TestDoubleBuild('1')); no retained
runtime workspace is read. The rendering target is TestDoubleBuild('2'),
which is a labelled test double, not an executable identity.
"""
import copy
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from applications.bounded_decision_workflow import checked_cli, t1_cli, t1_workflow
from applications.bounded_decision_workflow.t1_records import parse as t1_parse
from tests.checked_temperature.fixtures import TestDoubleBuild
from tests.t1_simulation.admitted_fixtures import admitted_case
from tests.t1_simulation.request_fixtures import request_for, request_inputs_for

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'tools' / 'fixtures' / 't1_rebind.py'
REVIEW = 'REBIND-REVIEW.json'
PACKET = 'packet/APPROVAL-PACKET.json'
BUILD2 = TestDoubleBuild(marker='2')
HISTORICAL_LABEL, HISTORICAL_BASIS = 'gate1 test fixture', 'synthetic Gate 1 unit-test fixture'
TEST_ONLY_LABEL = 'TEST-ONLY synthetic attestation'
TEST_ONLY_BASIS = 'pytest fixture text; not an owner attestation; not approval; confers no authority'
STAGE_RECORDS = {'stage1': ('policy', 'P', 'A0'), 'stage2': ('simulator_policy', 'X', 'E', 'J', 'G'),
                 'stage3': ('R',)}
DIRS = {'selection_objects': 'selection/objects', 'simulation_input': 'positive/simulation-input',
        'request_input': 'positive/request-input'}
# Specification §3.1, written out independently of the tool's rule table.
EXPECTED_POINTERS = {
    'policy': {'/permitted_builds/0'},
    'P': {'/policy/sha256'},
    'A0': {'/target/sha256'},
    'simulator_policy': {'/permitted_producer_builds/0', '/permitted_checker_builds/0'},
    'X': {'/prior_selection/manifest/sha256', '/prior_selection/selection/sha256'},
    'E': {'/target/sha256'},
    'J': {'/captured_policy/sha256', '/producer_build/sha256', '/simulator_policy/sha256',
          '/execution_target/sha256'},
    'G': {'/execution_authority/sha256', '/scope/captured_policy/sha256', '/scope/producer_build/sha256',
          '/scope/simulator_policy/sha256', '/target/sha256'},
    'R': {'/policy/sha256', '/prior_selection/manifest/sha256', '/prior_selection/selection/sha256',
          '/execution_target/sha256', '/result/execution_authority/sha256',
          '/result/acquisition/public_evidence/sha256'}}
KINDS = {'policy': 'ct.policy.v1', 'P': 'ct.request.v1', 'A0': 'ct.authority.v1',
         'simulator_policy': 'ct.t1-simulator-policy.v1', 'X': 'ct.execution-target.v1', 'E': 'ct.authority.v1',
         'J': 'ct.t1-simulation-target.v1', 'G': 'ct.t1-simulation-permission.v1', 'R': 'ct.request.v1'}


def _load_tool():
    spec = importlib.util.spec_from_file_location('t1_rebind_under_test', TOOL)
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True   # no .pyc beside the tool (specification §9.3 caveat)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


rb = _load_tool()


# ----------------------------------------------------------------- helpers

def canon(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def kref(kind, digest):
    return {'kind': kind, 'sha256': digest}


def write_tree(directory, files):
    directory.mkdir(parents=True)
    for name, wire in files.items():
        destination = directory / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(wire)


def read_tree(directory):
    tree = {}
    for parent, _dirs, names in os.walk(directory):
        for name in names:
            path = Path(parent) / name
            tree[path.relative_to(directory).as_posix()] = path.read_bytes()
    return tree


def get(value, pointer):
    for part in pointer.split('/')[1:]:
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def diff(a, b, pointer=''):
    """Independent leaf diff (not the tool's)."""
    if isinstance(a, dict):
        assert isinstance(b, dict) and set(a) == set(b), pointer
        return {p for k in a for p in diff(a[k], b[k], pointer + '/' + k)}
    if isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), pointer
        return {p for i in range(len(a)) for p in diff(a[i], b[i], pointer + '/' + str(i))}
    return set() if (type(a) is type(b) and a == b) else {pointer}


def attestation(directory, stage, name=None, edit=None):
    """TEST-ONLY attestation text; never owner attestation."""
    value = {'schema': 't1-rebind-attestations.v1', 'stage': stage,
             'records': {role: {'label': TEST_ONLY_LABEL, 'basis': TEST_ONLY_BASIS + ' [' + role + ']'}
                         for role in STAGE_RECORDS[stage]}}
    if edit:
        edit(value)
    path = Path(directory) / (name or ('attest-' + stage + '.json'))
    wire = canon(value)
    path.write_bytes(wire)
    return path, sha(wire)


def invoke(stage, flags):
    argv = [stage]
    for key, value in flags.items():
        argv += ['--' + key, str(value)]
    out, err = io.StringIO(), io.StringIO()
    code = rb.main(argv, out=out, err=err)
    stdout, stderr = out.getvalue(), err.getvalue()
    return SimpleNamespace(code=code, raw_out=stdout, raw_err=stderr,
                           out=json.loads(stdout) if stdout else None, err=json.loads(stderr) if stderr else None)


def refused(result, code):
    assert result.err is not None and result.err['code'] == code, (result.raw_err, result.raw_out)
    assert result.code == rb.EXIT[code]
    assert result.raw_out == '' and 'Traceback' not in result.raw_err
    assert not re.search(r'"target":"/(tmp|home|mnt)/', result.raw_err)
    return result


def common(source, att, out, root=None, pins=None):
    pins_path, pins_sha = pins or (source.pins_path, source.pins_sha)
    return {'source-dir': root or source.root, 'source-pins': pins_path, 'expected-source-pins-sha256': pins_sha,
            'attestations': att[0], 'expected-attestations-sha256': att[1], 'out': out}


def t1_command(operation, build, **flags):
    argv = [operation]
    for key, value in flags.items():
        argv += ['--' + key.replace('_', '-'), str(value)]
    return t1_cli.execute(t1_cli.arguments(argv), build=build)


def review_of(directory):
    return json.loads((Path(directory) / REVIEW).read_bytes())


def rendered_wire(directory, role):
    review = review_of(directory)
    return (Path(directory) / review['rendered'][role]['path']).read_bytes()


def rendered_value(directory, role):
    return json.loads(rendered_wire(directory, role))


# ------------------------------------------------------------ source chain

@pytest.fixture(scope='module')
def source(tmp_path_factory):
    """Historical source layout generated in tmp: build-1 selection, acquisition, then R from its evidence."""
    base = tmp_path_factory.mktemp('rebind-source')
    case = admitted_case(theta='60.1', baseline_theta='60.1')
    build1 = case['build']
    write_tree(base / 'h-prior', case['prior_files'])
    write_tree(base / 'h-input', case['objects'])
    t1_command('t1-simulation-run', build1, expected_target_pin=case['pins']['J'],
               expected_execution_authority_pin=case['pins']['E'], expected_permission_pin=case['pins']['G'],
               expected_prior_request_pin=case['prior_pins']['request_sha256'],
               expected_prior_authority_pin=case['prior_pins']['authority_sha256'],
               prior_bundle=base / 'h-prior', output_dir=base / 'h-producer', objects_dir=base / 'h-input')
    package = t1_workflow.read_package(base / 'h-producer')
    receipt = json.loads(package['receipt/receipt.json'])
    evidence = package['evidence/public/evidence.json']
    supplied = request_for(case, {'public_evidence': evidence}, receipt)
    request_objects = request_inputs_for(supplied, case)
    request_objects[sha(supplied.request_wire)] = supplied.request_wire
    selection = case['base']
    j = json.loads(case['objects'][case['pins']['J']])
    roles = {'policy': selection.world.refof('policy')['sha256'], 'P': selection.request_pin,
             'A0': selection.authority_pin, 'simulator_policy': j['simulator_policy']['sha256'],
             'X': j['execution_target']['sha256'], 'E': case['pins']['E'], 'J': case['pins']['J'],
             'G': case['pins']['G'], 'evidence': sha(evidence), 'R': sha(supplied.request_wire)}
    contents = {'selection_objects': dict(selection.objects), 'simulation_input': dict(case['objects']),
                'request_input': request_objects}
    joins = {'selection_objects': ('policy', 'A0'), 'simulation_input': ('simulator_policy', 'X', 'E', 'J', 'G'),
             'request_input': ('policy', 'X', 'E', 'R', 'evidence')}
    for key, members in joins.items():   # the generated topology must be the specified one
        assert {roles[r] for r in members} <= set(contents[key]), key
    root = base / 'source'
    (root / 'selection').mkdir(parents=True)
    (root / 'selection/request.json').write_bytes(selection.request_wire)
    for key, relative in DIRS.items():
        write_tree(root / relative, contents[key])
    write_tree(root / 'prior', case['prior_files'])
    pins = {'schema': 't1-rebind-source-pins.v1', 'label': 'pytest synthetic source (test-only)',
            'historical_build': build1.digest, 'roles': roles,
            'unchanged': {key: sorted(set(contents[key]) - {roles[r] for r in joins[key]}) for key in DIRS},
            'prior_bundle': {name: sha(wire) for name, wire in case['prior_files'].items()}}
    pins_path = base / 'pins.json'
    pins_path.write_bytes(canon(pins))
    return SimpleNamespace(root=root, pins=pins, pins_path=pins_path, pins_sha=sha(pins_path.read_bytes()),
                           case=case, build1=build1, evidence=evidence, receipt=receipt, supplied=supplied,
                           contents=contents, roles=roles, base=base)


def source_value(source, role):
    digest = source.roles[role]
    if role == 'P':
        return json.loads((source.root / 'selection/request.json').read_bytes())
    for key, relative in DIRS.items():
        if digest in source.contents[key]:
            return json.loads(source.contents[key][digest])
    raise KeyError(role)


@pytest.fixture(scope='module')
def chain(source, tmp_path_factory):
    """stage1 -> maintained selection (build 2) -> stage2 -> maintained acquisition (build 2) -> stage3."""
    base = tmp_path_factory.mktemp('rebind-chain')
    c = SimpleNamespace(source=source, base=base)
    c.att1 = attestation(base, 'stage1')
    r1 = invoke('stage1', dict(common(source, c.att1, base / 'out1'), **{'build-digest': BUILD2.digest}))
    assert r1.code == 0, r1.raw_err
    c.out1, c.rev1 = base / 'out1', r1.out['review_sha256']
    c.new = {role: row['new_sha256'] for role, row in review_of(c.out1)['rendered'].items()}
    # EX-1 analogue under this test only: the maintained checked selection command, in process, build 2.
    checked_cli.execute(checked_cli.arguments([
        'checked-selection-evaluate', '--request', str(c.out1 / 'selection/request.json'),
        '--objects-dir', str(c.out1 / 'selection/objects'), '--expected-request-pin', c.new['P'],
        '--expected-authority-pin', c.new['A0'], '--output-dir', str(base / 'b0')]), build=BUILD2)
    c.b0 = base / 'b0'
    c.b0_pin = sha((c.b0 / 'manifest.json').read_bytes())
    c.att2 = attestation(base, 'stage2')
    r2 = invoke('stage2', stage2_flags(c, base / 'out2'))
    assert r2.code == 0, r2.raw_err
    c.out2, c.rev2 = base / 'out2', r2.out['review_sha256']
    c.new.update({role: row['new_sha256'] for role, row in review_of(c.out2)['rendered'].items()})
    # EX-2 analogue under this test only: the maintained producer command, in process, build 2.
    c.m2 = base / 'm2'
    produce(c, c.out2, c.m2)
    c.m2_pin = sha((c.m2 / 'manifest.json').read_bytes())
    c.att3 = attestation(base, 'stage3')
    r3 = invoke('stage3', stage3_flags(c, base / 'out3'))
    assert r3.code == 0, r3.raw_err
    c.out3, c.rev3 = base / 'out3', r3.out['review_sha256']
    c.new.update({role: row['new_sha256'] for role, row in review_of(c.out3)['rendered'].items()})
    return c


def produce(c, stage2_dir, output):
    review = review_of(stage2_dir)
    digests = {role: row['new_sha256'] for role, row in review['rendered'].items()}
    t1_command('t1-simulation-run', BUILD2, expected_target_pin=digests['J'],
               expected_execution_authority_pin=digests['E'], expected_permission_pin=digests['G'],
               expected_prior_request_pin=c.new['P'], expected_prior_authority_pin=c.new['A0'],
               prior_bundle=c.b0, output_dir=output, objects_dir=Path(stage2_dir) / 'simulation-input')


def stage2_flags(c, out, att=None, **over):
    flags = dict(common(c.source, att or c.att2, out), **{
        'stage1-dir': c.out1, 'expected-stage1-review-sha256': c.rev1, 'prior-bundle': c.b0,
        'expected-prior-manifest-sha256': c.b0_pin})
    flags.update(over)
    return flags


def stage3_flags(c, out, att=None, **over):
    flags = dict(common(c.source, att or c.att3, out), **{
        'stage1-dir': c.out1, 'expected-stage1-review-sha256': c.rev1, 'stage2-dir': c.out2,
        'expected-stage2-review-sha256': c.rev2, 'producer-package': c.m2,
        'expected-producer-manifest-sha256': c.m2_pin})
    flags.update(over)
    return flags


def stage1_flags(source, out, att, **over):
    flags = dict(common(source, att, out), **{'build-digest': BUILD2.digest})
    flags.update(over)
    return flags


def source_variant(source, tmp_path, *, replace=(), roles=None, pins_edit=None, tree_edit=None):
    """Copy of the source with replaced objects (renamed to their digest) and refreshed pins."""
    Path(tmp_path).mkdir(parents=True, exist_ok=True)
    root = tmp_path / 'source-variant'
    shutil.copytree(source.root, root, symlinks=True)
    pins = copy.deepcopy(source.pins)
    for key, old, wire in replace:
        (root / DIRS[key] / old).unlink()
        (root / DIRS[key] / sha(wire)).write_bytes(wire)
        if old in pins['unchanged'][key]:
            pins['unchanged'][key] = sorted(set(pins['unchanged'][key]) - {old} | {sha(wire)})
    pins['roles'].update(roles or {})
    if pins_edit:
        pins_edit(pins)
    if tree_edit:
        tree_edit(root)
    path = tmp_path / 'pins-variant.json'
    path.write_bytes(canon(pins))
    return root, (path, sha(path.read_bytes()))


def world_digest(source):
    return json.loads(source.contents['simulation_input'][source.roles['J']])['world']['sha256']


def world_variant(source, tmp_path, edit):
    old = world_digest(source)
    value = json.loads(source.contents['simulation_input'][old])
    edit(value)
    return source_variant(source, tmp_path, replace=[('simulation_input', old, canon(value))])


# ---------------------------------------------------------------- T01-T05

def test_t01_rendering_is_deterministic(chain, tmp_path):
    again1 = invoke('stage1', stage1_flags(chain.source, tmp_path / 'again1', chain.att1))
    assert again1.code == 0 and again1.out['review_sha256'] == chain.rev1
    assert read_tree(tmp_path / 'again1') == read_tree(chain.out1)
    again2 = invoke('stage2', stage2_flags(chain, tmp_path / 'again2'))
    assert again2.code == 0 and read_tree(tmp_path / 'again2') == read_tree(chain.out2)
    again3 = invoke('stage3', stage3_flags(chain, tmp_path / 'again3'))
    assert again3.code == 0 and read_tree(tmp_path / 'again3') == read_tree(chain.out3)
    for out in (chain.out1, chain.out2, chain.out3):
        text = (out / REVIEW).read_text('utf-8') + (out / PACKET).read_text('utf-8')
        assert str(chain.base) not in text and str(chain.source.root) not in text


def test_t02_canonical_form_and_hash_names(chain):
    for out, prefix in ((chain.out1, 'selection/objects/'), (chain.out2, 'simulation-input/'),
                        (chain.out3, 'request-input/')):
        tree = read_tree(out)
        names = [rel for rel in tree if rel.startswith(prefix)]
        assert names and all(rel[len(prefix):] == sha(tree[rel]) for rel in names)
        review = review_of(out)
        for row in review['rendered'].values():
            wire = tree[row['path']]
            assert canon(json.loads(wire)) == wire and sha(wire) == row['new_sha256']
        assert tree[REVIEW] == (json.dumps(review, indent=1, sort_keys=True, ensure_ascii=False) + '\n').encode()
        assert PARTIAL_ABSENT(out)
    assert sha(read_tree(chain.out1)['selection/request.json']) == chain.new['P']


def PARTIAL_ABSENT(out):
    return not (Path(out) / 'PARTIAL').exists()


def test_t03_only_rule_pointers_and_two_attestation_leaves_change(chain):
    outs = {'stage1': chain.out1, 'stage2': chain.out2, 'stage3': chain.out3}
    for stage, roles in STAGE_RECORDS.items():
        for role in roles:
            before, after = source_value(chain.source, role), rendered_value(outs[stage], role)
            assert diff(before, after) == EXPECTED_POINTERS[role] | {'/provenance/label', '/provenance/basis'}, role
            for key in ('id', 'revision', 'predecessor', 'profile', 'schema'):
                assert after[key] == before[key]
            assert after['revision'] == 1 and after['predecessor'] is None
            assert after['provenance']['role'] == before['provenance']['role']
            assert after['provenance']['authenticated'] is False


def test_t04_dependency_ordering(chain):
    n, b = chain.new, BUILD2.digest
    value = lambda stage_out, role: rendered_value(stage_out, role)
    assert value(chain.out1, 'policy')['permitted_builds'] == [b]
    assert value(chain.out1, 'P')['policy'] == kref('ct.policy.v1', n['policy'])
    assert value(chain.out1, 'A0')['target'] == kref('ct.request.v1', n['P'])
    s = value(chain.out2, 'simulator_policy')
    assert s['permitted_producer_builds'] == [b] and s['permitted_checker_builds'] == [b]
    assert value(chain.out2, 'X')['prior_selection'] == {
        'manifest': kref('ct.bundle-manifest.v1', chain.b0_pin),
        'selection': kref('ct.selection.v1', sha((chain.b0 / 'result.json').read_bytes()))}
    assert value(chain.out2, 'E')['target'] == kref('ct.execution-target.v1', n['X'])
    j = value(chain.out2, 'J')
    assert (j['captured_policy'], j['producer_build'], j['simulator_policy'], j['execution_target']) == (
        kref('ct.policy.v1', n['policy']), kref('ct.build.v1', b),
        kref('ct.t1-simulator-policy.v1', n['simulator_policy']), kref('ct.execution-target.v1', n['X']))
    g = value(chain.out2, 'G')
    assert g['execution_authority'] == kref('ct.authority.v1', n['E'])
    assert g['target'] == kref('ct.t1-simulation-target.v1', n['J'])
    assert g['scope'] == dict(g['scope'], captured_policy=j['captured_policy'], producer_build=j['producer_build'],
                              simulator_policy=j['simulator_policy'])
    r = value(chain.out3, 'R')
    assert r['policy'] == kref('ct.policy.v1', n['policy'])
    assert r['prior_selection'] == value(chain.out2, 'X')['prior_selection']
    assert r['execution_target'] == kref('ct.execution-target.v1', n['X'])
    assert r['result']['execution_authority'] == kref('ct.authority.v1', n['E'])
    evidence = (chain.m2 / 'evidence/public/evidence.json').read_bytes()
    assert r['result']['acquisition']['public_evidence'] == kref('nm.evidence.v1', sha(evidence))
    edges = [e for out in (chain.out1, chain.out2, chain.out3) for e in review_of(out)['edges']]
    assert {(e['from_role'], e['to_role']) for e in edges} >= {
        ('P', 'policy'), ('A0', 'P'), ('X', 'B0.manifest'), ('X', 'B0.result'), ('E', 'X'), ('J', 'policy'),
        ('J', 'B'), ('J', 'simulator_policy'), ('J', 'X'), ('G', 'E'), ('G', 'J'), ('R', 'evidence')}


def test_t05_rendered_records_pass_the_application_validators(chain):
    outs = {'stage1': chain.out1, 'stage2': chain.out2, 'stage3': chain.out3}
    for stage, roles in STAGE_RECORDS.items():
        for role in roles:
            value, _ = t1_parse(rendered_wire(outs[stage], role), KINDS[role], '/')
            assert value['schema'] == KINDS[role]


# ---------------------------------------------------------------- T06-T09

def test_t06_in_process_chain_reaches_the_maintained_handoff(chain, tmp_path):
    assert sha((chain.b0 / 'build.json').read_bytes()) == BUILD2.digest
    t1_command('t1-reassessment-prepare', BUILD2, expected_target_pin=chain.new['J'],
               expected_execution_authority_pin=chain.new['E'], expected_permission_pin=chain.new['G'],
               expected_prior_request_pin=chain.new['P'], expected_prior_authority_pin=chain.new['A0'],
               prior_bundle=chain.b0, output_dir=tmp_path / 'handoff', producer_package=chain.m2,
               expected_producer_manifest_pin=chain.m2_pin, scratch_dir=tmp_path / 'scratch',
               objects_dir=chain.out3 / 'request-input')
    handoff = json.loads((tmp_path / 'handoff/handoff.json').read_bytes())
    assert handoff['request'] == kref('ct.request.v1', chain.new['R'])
    assert not (tmp_path / 'handoff/PARTIAL').exists()


def test_t07_simulator_evidence_flows_into_r_unchanged(chain):
    evidence = (chain.m2 / 'evidence/public/evidence.json').read_bytes()
    assert json.loads(evidence)['id'] == 'E-t1-' + chain.new['J'][:59]
    assert len(json.loads(evidence)['id']) == len('E-t1-') + 59
    r = rendered_value(chain.out3, 'R')
    assert r['result']['acquisition']['public_evidence']['sha256'] == sha(evidence)
    assert read_tree(chain.out3)['request-input/' + sha(evidence)] == evidence
    row = [o for o in review_of(chain.out3)['outputs'] if o['path'] == 'request-input/' + sha(evidence)][0]
    assert (row['disposition'], row['source'], row['kind']) == ('copied_generated', 'producer', 'nm.evidence.v1')
    assert sha(evidence) != chain.source.roles['evidence']


def test_t08_evidence_must_belong_to_the_exact_producer_package(chain, tmp_path):
    other = attestation(tmp_path, 'stage2', edit=lambda v: v['records']['G'].update(basis='G text differs only'))
    assert invoke('stage2', stage2_flags(chain, tmp_path / 'out2g', att=other)).code == 0
    review_g = review_of(tmp_path / 'out2g')
    assert review_g['rendered']['J']['new_sha256'] == chain.new['J']   # J unchanged, G differs
    assert review_g['rendered']['G']['new_sha256'] != chain.new['G']
    produce(chain, tmp_path / 'out2g', tmp_path / 'm2g')
    evidence_g = (tmp_path / 'm2g/evidence/public/evidence.json').read_bytes()
    assert sha(evidence_g) != sha((chain.m2 / 'evidence/public/evidence.json').read_bytes())
    pin_g = sha((tmp_path / 'm2g/manifest.json').read_bytes())
    refused(invoke('stage3', stage3_flags(chain, tmp_path / 'x1', **{
        'producer-package': tmp_path / 'm2g', 'expected-producer-manifest-sha256': pin_g})),
        'REBIND_DEPENDENCY_MISMATCH')
    rev_g = sha((tmp_path / 'out2g' / REVIEW).read_bytes())
    refused(invoke('stage3', stage3_flags(chain, tmp_path / 'x2', **{
        'stage2-dir': tmp_path / 'out2g', 'expected-stage2-review-sha256': rev_g})), 'REBIND_DEPENDENCY_MISMATCH')
    paired = invoke('stage3', stage3_flags(chain, tmp_path / 'x3', **{
        'stage2-dir': tmp_path / 'out2g', 'expected-stage2-review-sha256': rev_g,
        'producer-package': tmp_path / 'm2g', 'expected-producer-manifest-sha256': pin_g}))
    assert paired.code == 0
    assert rendered_value(tmp_path / 'x3', 'R')['result']['acquisition']['public_evidence']['sha256'] == \
        sha(evidence_g)
    for name in ('x1', 'x2'):
        assert not (tmp_path / name).exists()


def test_t09_unchanged_objects_are_byte_identical(chain):
    for out, key, prefix in ((chain.out1, 'selection_objects', 'selection/objects/'),
                             (chain.out2, 'simulation_input', 'simulation-input/'),
                             (chain.out3, 'request_input', 'request-input/')):
        tree, rows = read_tree(out), review_of(out)['outputs']
        unchanged = [o for o in rows if o['disposition'] == 'copied_unchanged']
        assert sorted(o['path'][len(prefix):] for o in unchanged) == chain.source.pins['unchanged'][key]
        for row in unchanged:
            digest = row['path'][len(prefix):]
            assert tree[row['path']] == chain.source.contents[key][digest]
    assert len([r for r in read_tree(chain.out1) if r.startswith('selection/objects/')]) == \
        len(chain.source.pins['unchanged']['selection_objects']) + 2
    names2 = {r.split('/')[1] for r in read_tree(chain.out2) if r.startswith('simulation-input/')}
    assert len(names2) == len(chain.source.pins['unchanged']['simulation_input']) + 5
    assert chain.new['policy'] not in names2   # J' reaches policy' only through the prior bundle
    tree3 = read_tree(chain.out3)
    assert tree3['request-input/' + chain.new['policy']] == rendered_wire(chain.out1, 'policy')
    for role in ('X', 'E'):
        assert tree3['request-input/' + chain.new[role]] == rendered_wire(chain.out2, role)
    assert len([r for r in tree3 if r.startswith('request-input/')]) == \
        len(chain.source.pins['unchanged']['request_input']) + 5


def test_source_fixture_has_the_specified_topology_and_legitimate_floats(source):
    evidence = json.loads(source.evidence)
    assert evidence['id'] == 'E-t1-' + source.roles['J'][:59]
    r = source_value(source, 'R')
    assert r['result']['acquisition']['public_evidence']['sha256'] == source.roles['evidence']
    assert r['result']['observation']['scalar'] == source.receipt['r']
    assert r['prior_selection']['manifest']['sha256'] == source.pins['prior_bundle']['manifest.json']
    assert source.pins['prior_bundle']['policy.json'] == source.roles['policy']
    assert source.pins['prior_bundle']['build.json'] == source.build1.digest

    def floats(value):
        if isinstance(value, float):
            return True
        if isinstance(value, dict):
            return any(floats(v) for v in value.values())
        return isinstance(value, list) and any(floats(v) for v in value)
    unchanged = [w for key in DIRS for d, w in source.contents[key].items() if d in source.pins['unchanged'][key]]
    assert any(floats(json.loads(w)) for w in unchanged if w[:1] == b'{')   # e.g. baseline evidence


# ---------------------------------------------------------------- T10-T11

def test_t10_review_lists_every_output_and_change(chain, tmp_path):
    for out in (chain.out1, chain.out2, chain.out3):
        tree, review = read_tree(out), review_of(out)
        listed = {o['path']: o for o in review['outputs']}
        assert set(tree) == set(listed) | {PACKET, REVIEW}
        for path, row in listed.items():
            assert (row['sha256'], row['bytes']) == (sha(tree[path]), len(tree[path]))
        assert (review['packet']['sha256'], review['packet']['bytes']) == (sha(tree[PACKET]), len(tree[PACKET]))
        for role, changes in review['changes'].items():
            before, after = source_value(chain.source, role), json.loads(tree[review['rendered'][role]['path']])
            leaves = {c['pointer'] + ('/0' if c['rule'] == 'list:B' else '') for c in changes}
            assert leaves == diff(before, after) | {'/provenance/label', '/provenance/basis'}
            for change in changes:   # a list rule records the whole one-element list
                assert (get(before, change['pointer']), get(after, change['pointer'])) == (change['old'],
                                                                                          change['new'])
        assert review['approval_state'] == 'not_approved'
    edited = tmp_path / 'edited1'
    shutil.copytree(chain.out1, edited)
    victim = sorted((edited / 'selection/objects').iterdir())[0]
    victim.write_bytes(victim.read_bytes() + b' ')
    refused(invoke('stage2', stage2_flags(chain, tmp_path / 'o1', **{'stage1-dir': edited})),
            'REBIND_INPUT_INVALID')
    extra = tmp_path / 'extra1'
    shutil.copytree(chain.out1, extra)
    (extra / 'selection/objects/note.txt').write_bytes(b'unlisted')
    refused(invoke('stage2', stage2_flags(chain, tmp_path / 'o2', **{'stage1-dir': extra})), 'REBIND_INPUT_INVALID')
    missing = tmp_path / 'missing1'
    shutil.copytree(chain.out1, missing)
    (missing / PACKET).unlink()
    refused(invoke('stage2', stage2_flags(chain, tmp_path / 'o3', **{'stage1-dir': missing})),
            'REBIND_INPUT_INVALID')


def rebundle(files, replace):
    files = dict(files, **replace)
    manifest = json.loads(files['manifest.json'])
    for entry in manifest['files']:
        entry['sha256'], entry['bytes'] = sha(files[entry['name']]), len(files[entry['name']])
    files['manifest.json'] = canon(manifest)
    return files


def b0_case(name, chain, source):
    files = read_tree(chain.b0)
    if name == 'stale-historical-bundle':
        return read_tree(source.root / 'prior'), None, 'REBIND_DEPENDENCY_MISMATCH'
    if name == 'policy-not-rendered':
        return rebundle(files, {'policy.json': (source.root / 'prior/policy.json').read_bytes()}), None, \
            'REBIND_DEPENDENCY_MISMATCH'
    if name == 'other-build':
        return rebundle(files, {'build.json': TestDoubleBuild(marker='3').wire()}), None, 'REBIND_DEPENDENCY_MISMATCH'
    if name == 'invocation-pin':
        invocation = json.loads(files['invocation.json'])
        invocation['expected_request_pin'] = source.roles['P']
        return rebundle(files, {'invocation.json': canon(invocation)}), None, 'REBIND_DEPENDENCY_MISMATCH'
    if name == 'unlisted-change':
        result = json.loads(files['result.json'])
        result['presentation'] = 'edited after publication'
        return dict(files, **{'result.json': canon(result)}), None, 'REBIND_DEPENDENCY_MISMATCH'
    if name == 'wrong-manifest-pin':
        return files, '1' * 64, 'REBIND_PIN_MISMATCH'
    if name == 'missing-file':
        return {k: v for k, v in files.items() if k != 'trace.json'}, None, 'REBIND_INPUT_MISSING'
    if name == 'extra-file':
        return dict(files, **{'extra.json': b'{}'}), None, 'REBIND_RESOURCE_LIMIT'
    raise KeyError(name)


@pytest.mark.parametrize('name', ['stale-historical-bundle', 'policy-not-rendered', 'other-build', 'invocation-pin',
                                  'unlisted-change', 'wrong-manifest-pin', 'missing-file', 'extra-file'])
def test_t11_stage2_refuses_mismatched_selection_bundle(chain, tmp_path, name):
    files, pin, code = b0_case(name, chain, chain.source)
    write_tree(tmp_path / 'b0x', files)
    pin = pin or (sha(files['manifest.json']) if 'manifest.json' in files else '1' * 64)
    refused(invoke('stage2', stage2_flags(chain, tmp_path / 'out', **{
        'prior-bundle': tmp_path / 'b0x', 'expected-prior-manifest-sha256': pin})), code)
    assert not (tmp_path / 'out').exists()


PRODUCER_FILES = ('manifest.json', 'receipt/receipt.json', 'evidence/public/evidence.json')


def producer_variant(chain, directory, *, evidence=None, receipt=None, manifest=None, rehash=True, partial=False):
    tree = read_tree(chain.m2)
    files = {k: tree[k] for k in PRODUCER_FILES}
    if evidence is not None:
        files['evidence/public/evidence.json'] = evidence
    value = json.loads(files['receipt/receipt.json'])
    if rehash:
        value['public_evidence']['sha256'] = sha(files['evidence/public/evidence.json'])
    if receipt:
        receipt(value)
    files['receipt/receipt.json'] = canon(value)
    man = json.loads(files['manifest.json'])
    if rehash:
        for member in man['members']:
            if member['path'] in files:
                member['sha256'], member['bytes'] = sha(files[member['path']]), len(files[member['path']])
        man['roots']['receipt']['sha256'] = sha(files['receipt/receipt.json'])
    if manifest:
        manifest(man)
    files['manifest.json'] = canon(man)
    write_tree(directory, files)
    if partial:
        (directory / 'PARTIAL').write_bytes(b'')
    return sha(files['manifest.json'])


def m_case(name, chain):
    s = chain.source
    if name == 'receipt-target':
        return dict(receipt=lambda r: r['target'].update(sha256='1' * 64))
    if name == 'receipt-historical-build':
        return dict(receipt=lambda r: r['producer_build'].update(sha256=s.build1.digest))
    if name == 'roots-historical-permission':
        return dict(manifest=lambda m: m['roots']['permission'].update(sha256=s.roles['G']))
    if name == 'evidence-id':
        value = json.loads((chain.m2 / 'evidence/public/evidence.json').read_bytes())
        value['id'] = 'E-t1-' + '0' * 59
        return dict(evidence=canon(value))
    if name == 'evidence-as-of':
        value = json.loads((chain.m2 / 'evidence/public/evidence.json').read_bytes())
        value['question']['as_of'] = '2026-10-05T09:03:00Z'
        return dict(evidence=canon(value))
    if name == 'scalar-text-differs':   # same rational, different text: intentionally refused (§7.4.7)
        return dict(receipt=lambda r: r.update(r=r['r'] + '0'))
    if name == 'swapped-evidence':
        return dict(evidence=s.evidence, rehash=False)
    if name == 'historical-evidence-rehashed':
        return dict(evidence=s.evidence)
    if name == 'partial':
        return dict(partial=True)
    raise KeyError(name)


@pytest.mark.parametrize('name', ['receipt-target', 'receipt-historical-build', 'roots-historical-permission',
                                  'evidence-id', 'evidence-as-of', 'scalar-text-differs', 'swapped-evidence',
                                  'historical-evidence-rehashed', 'partial'])
def test_t11_stage3_refuses_mismatched_producer_package(chain, tmp_path, name):
    pin = producer_variant(chain, tmp_path / 'mx', **m_case(name, chain))
    refused(invoke('stage3', stage3_flags(chain, tmp_path / 'out', **{
        'producer-package': tmp_path / 'mx', 'expected-producer-manifest-sha256': pin})),
        'REBIND_DEPENDENCY_MISMATCH')
    assert not (tmp_path / 'out').exists()


def test_t11_stage3_refuses_wrong_producer_manifest_pin(chain, tmp_path):
    refused(invoke('stage3', stage3_flags(chain, tmp_path / 'out', **{
        'expected-producer-manifest-sha256': '2' * 64})), 'REBIND_PIN_MISMATCH')


def test_t11_earlier_stage_directories_and_pins(chain, tmp_path):
    refused(invoke('stage2', stage2_flags(chain, tmp_path / 'o1', **{'stage1-dir': tmp_path / 'absent'})),
            'REBIND_INPUT_MISSING')
    refused(invoke('stage2', stage2_flags(chain, tmp_path / 'o2', **{'expected-stage1-review-sha256': '3' * 64})),
            'REBIND_PIN_MISMATCH')
    refused(invoke('stage2', stage2_flags(chain, tmp_path / 'o3', **{
        'stage1-dir': chain.out2, 'expected-stage1-review-sha256': chain.rev2})), 'REBIND_INPUT_INVALID')
    no_review = tmp_path / 'no-review'
    shutil.copytree(chain.out1, no_review)
    (no_review / REVIEW).unlink()
    refused(invoke('stage2', stage2_flags(chain, tmp_path / 'o4', **{'stage1-dir': no_review})),
            'REBIND_INPUT_MISSING')
    # A stage-1 directory from another lineage cannot be paired with this stage 2.
    other = attestation(tmp_path, 'stage1', edit=lambda v: v['records']['A0'].update(label='other lineage'))
    assert invoke('stage1', stage1_flags(chain.source, tmp_path / 'out1b', other)).code == 0
    rev1b = sha((tmp_path / 'out1b' / REVIEW).read_bytes())
    refused(invoke('stage3', stage3_flags(chain, tmp_path / 'o5', **{
        'stage1-dir': tmp_path / 'out1b', 'expected-stage1-review-sha256': rev1b})), 'REBIND_PIN_MISMATCH')
    # Different source pins than the ones the earlier stage was rendered from.
    root, pins = source_variant(chain.source, tmp_path, pins_edit=lambda p: p.update(label='relabelled pins'))
    flags = stage2_flags(chain, tmp_path / 'o6')
    flags.update({'source-dir': root, 'source-pins': pins[0], 'expected-source-pins-sha256': pins[1]})
    refused(invoke('stage2', flags), 'REBIND_PIN_MISMATCH')


def test_t11_source_inventory_and_canonical_form(source, tmp_path):
    att = attestation(tmp_path, 'stage1')
    old = world_digest(source)
    sim = DIRS['simulation_input']

    def run(name, **variant):
        root, pins = source_variant(source, tmp_path / name, **variant)
        return invoke('stage1', dict(common(source, att, tmp_path / name / 'out', root, pins),
                                     **{'build-digest': BUILD2.digest}))
    refused(run('extra', tree_edit=lambda r: (r / sim / sha(b'{}')).write_bytes(b'{}')), 'REBIND_RESOURCE_LIMIT')
    refused(run('missing', tree_edit=lambda r: (r / sim / old).unlink()), 'REBIND_INPUT_MISSING')
    refused(run('misnamed', tree_edit=lambda r: (r / sim / old).rename(r / sim / ('f' * 64))),
            'REBIND_INPUT_INVALID')
    refused(run('corrupt', tree_edit=lambda r: (r / sim / old).write_bytes(
        (r / sim / old).read_bytes() + b' ')), 'REBIND_INPUT_INVALID')
    world = json.loads(source.contents['simulation_input'][old])
    pretty_world = json.dumps(world, indent=1).encode()
    refused(run('noncanonical', replace=[('simulation_input', old, pretty_world)]), 'REBIND_INPUT_INVALID')
    refused(run('duplicate-key', replace=[('simulation_input', old, b'{"a":1,"a":1}')]), 'REBIND_INPUT_INVALID')
    refused(run('prior-altered', tree_edit=lambda r: (r / 'prior/trace.json').write_bytes(b'{}')),
            'REBIND_INPUT_INVALID')
    refused(run('prior-pin-missing', pins_edit=lambda p: p['prior_bundle'].pop('trace.json')),
            'REBIND_INPUT_INVALID')
    refused(run('prior-policy-pin', pins_edit=lambda p: p['prior_bundle'].update({'policy.json': '4' * 64})),
            'REBIND_INPUT_INVALID')
    refused(run('role-link', pins_edit=lambda p: p['roles'].update(E=p['roles']['X'])), 'REBIND_INPUT_INVALID')
    assert not any((tmp_path / n / 'out').exists() for n in ('extra', 'missing', 'noncanonical', 'prior-altered'))


def test_t11_float_inside_a_rendered_kind_is_refused(source, tmp_path):
    old = source.roles['A0']
    value = json.loads(source.contents['selection_objects'][old])
    value['x'] = 1.5
    wire = canon(value)
    root, pins = source_variant(source, tmp_path, replace=[('selection_objects', old, wire)],
                                roles={'A0': sha(wire)})
    att = attestation(tmp_path, 'stage1')
    refused(invoke('stage1', dict(common(source, att, tmp_path / 'out', root, pins),
                                  **{'build-digest': BUILD2.digest})), 'REBIND_INPUT_INVALID')


# ---------------------------------------------------------------- T12-T14

ATTESTATION_EDITS = {
    'missing-key': lambda v: v['records'].pop('A0'),
    'extra-key': lambda v: v['records'].update(R={'label': 'x', 'basis': 'y'}),
    'extra-field': lambda v: v['records']['P'].update(note='z'),
    'label-too-long': lambda v: v['records']['P'].update(label='x' * 129),
    'label-empty': lambda v: v['records']['P'].update(label=''),
    'basis-too-long': lambda v: v['records']['P'].update(basis='x' * 1025),
    'control-character': lambda v: v['records']['policy'].update(basis='bell\x07'),
    'not-a-string': lambda v: v['records']['policy'].update(label=1),
    'wrong-stage': lambda v: v.update(stage='stage2'),
    'wrong-schema': lambda v: v.update(schema='t1-rebind-attestations.v0'),
    'extra-top-level': lambda v: v.update(approved=True)}


@pytest.mark.parametrize('name', sorted(ATTESTATION_EDITS))
def test_t12_attestation_shape_is_enforced(source, tmp_path, name):
    att = attestation(tmp_path, 'stage1', edit=ATTESTATION_EDITS[name])
    refused(invoke('stage1', stage1_flags(source, tmp_path / 'out', att)), 'REBIND_ATTESTATION_INVALID')
    assert not (tmp_path / 'out').exists()


def test_t12_attestation_file_presence_pin_and_bounds(source, tmp_path):
    att = attestation(tmp_path, 'stage1')
    refused(invoke('stage1', stage1_flags(source, tmp_path / 'o1', (tmp_path / 'absent.json', att[1]))),
            'REBIND_INPUT_MISSING')
    refused(invoke('stage1', stage1_flags(source, tmp_path / 'o2', (att[0], '5' * 64))), 'REBIND_PIN_MISMATCH')
    edge = attestation(tmp_path, 'stage1', name='edge.json', edit=lambda v: v['records'].update(
        P={'label': 'é' * 128, 'basis': '€' * 1024}))
    assert invoke('stage1', stage1_flags(source, tmp_path / 'o3', edge)).code == 0
    assert rendered_value(tmp_path / 'o3', 'P')['provenance'] == dict(
        rendered_value(tmp_path / 'o3', 'P')['provenance'], label='é' * 128, basis='€' * 1024)


def test_t12_supplied_text_verbatim_and_historical_text_only_when_supplied(chain, tmp_path):
    outs = {'stage1': chain.out1, 'stage2': chain.out2, 'stage3': chain.out3}
    for stage, roles in STAGE_RECORDS.items():
        packet = json.loads((outs[stage] / PACKET).read_bytes())
        for role in roles:
            provenance = rendered_value(outs[stage], role)['provenance']
            assert provenance['label'] == TEST_ONLY_LABEL
            assert provenance['basis'] == TEST_ONLY_BASIS + ' [' + role + ']'
            assert HISTORICAL_LABEL not in (provenance['label'], provenance['basis'])
        assert not any(r['matches_historical_text'] for r in packet['records'])
    knowing = attestation(tmp_path, 'stage1', edit=lambda v: v['records'].update(
        P={'label': HISTORICAL_LABEL, 'basis': HISTORICAL_BASIS}))
    assert invoke('stage1', stage1_flags(chain.source, tmp_path / 'out', knowing)).code == 0
    flags = {r['role']: r['matches_historical_text'] for r in json.loads((tmp_path / 'out' / PACKET).read_bytes())[
        'records']}
    assert flags == {'policy': False, 'P': True, 'A0': False}
    assert review_of(tmp_path / 'out')['diagnostics']['matches_historical_text'] == flags


def test_t13_no_inferred_approval(chain):
    for stage, out in (('stage1', chain.out1), ('stage2', chain.out2), ('stage3', chain.out3)):
        review = review_of(out)
        packet = json.loads((out / PACKET).read_bytes())
        assert review['approval_state'] == packet['approval_state'] == 'not_approved'
        assert review['statement'] == packet['statement'] == (
            'Candidate rendering only. Not owner approval. No application execution is authorized by this record.')
        assert packet['blocked_next_operation']['status'] == 'NOT AUTHORIZED BY THIS PACKET'
        assert packet['approval_record_required']['partial_approval_supported'] is False
        tree = read_tree(out)
        for rel in (REVIEW, PACKET):   # tool-authored files carry no approval decision anywhere
            assert not {'decision', 'recorded_on', 'approved'} & set(keys_of(json.loads(tree[rel]))), rel
        for rel, wire in tree.items():
            try:
                value = json.loads(wire)
            except ValueError:
                continue   # opaque evidence content
            assert not (isinstance(value, dict) and value.get('schema') == 't1-rebind-owner-approval.v1'), rel
        for record in packet['records']:
            assert record['candidate_text'].encode('utf-8') == tree[review['rendered'][record['role']]['path']]
            assert sha(record['candidate_text'].encode('utf-8')) == record['sha256']
    assert not any('approv' in flag for flags in rb.FLAGS.values() for flag in flags)
    result = invoke('approve', {})
    refused(result, 'REBIND_USAGE')


def keys_of(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from keys_of(item)
    elif isinstance(value, list):
        for item in value:
            yield from keys_of(item)


def test_t14_existing_or_symlinked_output_is_refused(source, tmp_path):
    att = attestation(tmp_path, 'stage1')
    existing = tmp_path / 'existing'
    existing.mkdir()
    (existing / 'keep').write_bytes(b'owner data')
    refused(invoke('stage1', stage1_flags(source, existing, att)), 'REBIND_OUTPUT_UNSAFE')
    assert read_tree(existing) == {'keep': b'owner data'}
    (tmp_path / 'link').symlink_to(tmp_path / 'link-target')
    refused(invoke('stage1', stage1_flags(source, tmp_path / 'link', att)), 'REBIND_OUTPUT_UNSAFE')
    assert not (tmp_path / 'link-target').exists()
    (tmp_path / 'real-parent').mkdir()
    (tmp_path / 'link-parent').symlink_to(tmp_path / 'real-parent', target_is_directory=True)
    refused(invoke('stage1', stage1_flags(source, tmp_path / 'link-parent' / 'out', att)), 'REBIND_OUTPUT_UNSAFE')
    assert list((tmp_path / 'real-parent').iterdir()) == []
    root, pins = source_variant(source, tmp_path)
    refused(invoke('stage1', dict(common(source, att, root / 'nested-out', root, pins),
                                  **{'build-digest': BUILD2.digest})), 'REBIND_OUTPUT_UNSAFE')
    assert not (root / 'nested-out').exists()
    inside = ROOT / ('.t1-rebind-test-must-not-exist-%d' % os.getpid())
    assert not inside.exists()
    try:
        refused(invoke('stage1', stage1_flags(source, inside, att)), 'REBIND_OUTPUT_UNSAFE')
        assert not inside.exists()
    finally:
        if inside.is_dir() and not inside.is_symlink():
            shutil.rmtree(inside)   # only reached if the refusal under test is broken


def test_t14_output_inside_an_earlier_stage_or_generated_input_is_refused(chain, tmp_path):
    for nested in (chain.out1 / 'nested', chain.b0 / 'nested'):
        refused(invoke('stage2', stage2_flags(chain, nested)), 'REBIND_OUTPUT_UNSAFE')
        assert not nested.exists()
    refused(invoke('stage3', stage3_flags(chain, chain.m2 / 'nested')), 'REBIND_OUTPUT_UNSAFE')
    assert not (chain.m2 / 'nested').exists()


def test_rendered_record_must_fit_the_application_byte_cap(chain, tmp_path):
    wide = attestation(tmp_path, 'stage2', edit=lambda v: v['records']['G'].update(basis='\U0001F600' * 1024))
    refused(invoke('stage2', stage2_flags(chain, tmp_path / 'out', att=wide)), 'REBIND_ATTESTATION_INVALID')
    assert not (tmp_path / 'out').exists()


def test_pins_implying_outputs_over_the_fixed_caps_are_refused_early(source, tmp_path):
    root, pins = source_variant(source, tmp_path, pins_edit=lambda p: p['unchanged'].update(
        selection_objects=sorted(p['unchanged']['selection_objects'] + ['e' * 64])))
    att = attestation(tmp_path, 'stage1')
    result = refused(invoke('stage1', dict(common(source, att, tmp_path / 'out', root, pins),
                                           **{'build-digest': BUILD2.digest})), 'REBIND_INPUT_INVALID')
    assert result.err['target'] == '/source-pins/unchanged/selection_objects'


def test_t14_rerun_into_the_same_path_is_refused(chain):
    before = read_tree(chain.out1)
    refused(invoke('stage1', stage1_flags(chain.source, chain.out1, chain.att1)), 'REBIND_OUTPUT_UNSAFE')
    assert read_tree(chain.out1) == before


def test_t14_write_failure_leaves_partial_and_the_next_stage_refuses(chain, tmp_path, monkeypatch):
    calls = []
    real = rb._write_fd

    def failing(fd, data):
        calls.append(len(data))
        if len(calls) == 4:
            raise OSError('injected test failure')
        return real(fd, data)
    monkeypatch.setattr(rb, '_write_fd', failing)
    refused(invoke('stage1', stage1_flags(chain.source, tmp_path / 'broken', chain.att1)), 'REBIND_PARTIAL')
    monkeypatch.undo()
    assert (tmp_path / 'broken/PARTIAL').exists() and not (tmp_path / 'broken' / REVIEW).exists()
    refused(invoke('stage2', stage2_flags(chain, tmp_path / 'next', **{'stage1-dir': tmp_path / 'broken'})),
            'REBIND_PARTIAL')
    refused(invoke('stage1', stage1_flags(chain.source, tmp_path / 'broken', chain.att1)), 'REBIND_OUTPUT_UNSAFE')
    assert (tmp_path / 'broken/PARTIAL').exists()


def test_preflight_refusal_creates_no_output(source, tmp_path, monkeypatch):
    """Owner disposition B: checks before the output directory exists need not leave PARTIAL."""
    monkeypatch.setitem(rb.OUTPUT_CAPS, 'stage1', (rb.OUTPUT_CAPS['stage1'][0], 1))
    att = attestation(tmp_path, 'stage1')
    refused(invoke('stage1', stage1_flags(source, tmp_path / 'out', att)), 'REBIND_RESOURCE_LIMIT')
    assert not os.path.lexists(tmp_path / 'out')


@pytest.mark.parametrize('failure', ['differs', 'unreadable'])
def test_readback_failure_after_creation_is_partial(source, tmp_path, monkeypatch, failure):
    """Owner disposition B: an expected readback failure after mkdir is REBIND_PARTIAL, exit 5."""
    real = rb.read_capped

    def faulty(path, cap, target):
        if not target.startswith('/out/'):
            return real(path, cap, target)
        if failure == 'unreadable':
            raise rb.Refusal('REBIND_INPUT_MISSING', target)
        return real(path, cap, target)[:-1]
    monkeypatch.setattr(rb, 'read_capped', faulty)
    att = attestation(tmp_path, 'stage1')
    result = refused(invoke('stage1', stage1_flags(source, tmp_path / 'out', att)), 'REBIND_PARTIAL')
    assert result.code == 5 and result.err['target'].startswith('/out/')
    monkeypatch.undo()
    written = read_tree(tmp_path / 'out')
    assert written['PARTIAL'] == b'' and REVIEW not in written and 'selection/request.json' in written


def test_failure_after_marker_removal_restores_the_marker(source, tmp_path, monkeypatch):
    """Owner disposition B: the final directory sync failing after PARTIAL is unlinked still leaves PARTIAL."""
    out = tmp_path / 'out'
    real = os.fsync

    def fsync(fd):
        if not (out / 'PARTIAL').exists():
            raise OSError('injected test failure')
        return real(fd)
    monkeypatch.setattr(os, 'fsync', fsync)
    att = attestation(tmp_path, 'stage1')
    result = refused(invoke('stage1', stage1_flags(source, out, att)), 'REBIND_PARTIAL')
    monkeypatch.undo()
    assert result.err['target'] == '/out/PARTIAL'
    assert (out / 'PARTIAL').read_bytes() == b'' and (out / REVIEW).exists()


def test_unexpected_failure_after_creation_stays_internal(source, tmp_path, monkeypatch):
    """A programming defect inside the write path is REBIND_INTERNAL, exit 7, never disguised as partial output."""
    calls = []
    real = rb._write_fd

    def defect(fd, data):
        calls.append(len(data))
        if len(calls) == 2:   # the first write after the PARTIAL marker
            raise RuntimeError('/home/somebody/defect')
        return real(fd, data)
    monkeypatch.setattr(rb, '_write_fd', defect)
    att = attestation(tmp_path, 'stage1')
    result = refused(invoke('stage1', stage1_flags(source, tmp_path / 'out', att)), 'REBIND_INTERNAL')
    assert result.code == 7 and result.raw_err == '{"code":"REBIND_INTERNAL","target":"/"}\n'
    monkeypatch.undo()
    assert calls[0] == 0
    written = read_tree(tmp_path / 'out')
    assert written['PARTIAL'] == b'' and REVIEW not in written   # retained, nothing deleted


# ---------------------------------------------------------------- T15-T16

def test_t15_legitimate_historical_references_remain(chain):
    j_before, j_after = source_value(chain.source, 'J'), rendered_value(chain.out2, 'J')
    for key in ('world', 'context', 'rule', 'companion_schemas_sha256', 'window', 'question_as_of', 'instrument_id'):
        assert j_after[key] == j_before[key]
    s_before, s_after = source_value(chain.source, 'simulator_policy'), rendered_value(chain.out2, 'simulator_policy')
    for key in ('rule', 'preset_sha256', 'companion_schemas_sha256', 'resource_maxima', 'record_caps'):
        assert s_after[key] == s_before[key]
    r_before, r_after = source_value(chain.source, 'R'), rendered_value(chain.out3, 'R')
    for key in ('model', 'claims', 'declarations', 'evidence_items', 'reviews', 'selection_basis', 'plan_change'):
        assert r_after[key] == r_before[key]
    assert r_after['result']['observation'] == r_before['result']['observation']
    assert review_of(chain.out1)['diagnostics']['output_scan'] == []


def test_t15_attestation_citing_old_digests_is_preserved_and_reported(source, tmp_path):
    old_j = source.roles['J']
    att = attestation(tmp_path, 'stage1', edit=lambda v: v['records']['policy'].update(
        basis='rebinds the fixture whose target was ' + old_j + ' (prefix ' + old_j[:12] + ')'))
    result = invoke('stage1', stage1_flags(source, tmp_path / 'out', att))
    assert result.code == 0, result.raw_err
    policy = rendered_value(tmp_path / 'out', 'policy')
    assert old_j in policy['provenance']['basis']
    hits = review_of(tmp_path / 'out')['diagnostics']['output_scan']
    assert hits and all(h['classification'] == 'in_attestation_text' and h['pointer'] == '/provenance/basis'
                        for h in hits)
    assert {h['historical'] for h in hits} == {'roles/J'}
    assert all(h['record'] == 'rendered' for h in hits)


@pytest.mark.parametrize('name,edit', [
    ('full-digest-outside-rule', lambda v, s: v.update(note=s.roles['J'])),
    ('prefix-outside-rule', lambda v, s: v.update(note='see ' + s.roles['G'][:12])),
    ('old-build-in-text', lambda v, s: v.update(note='built by ' + s.build1.digest)),
    ('stale-structured-reference', lambda v, s: v.update(stale=kref(KINDS['X'], s.roles['X']))),
    ('old-digest-in-other-provenance-field', lambda v, s: v['provenance'].update(note='cites ' + s.roles['X'])),
    ('old-digest-in-nested-provenance', lambda v, s: v.update(detail={'provenance': {'basis': s.roles['X']}})),
    ('old-digest-as-key', lambda v, s: v.update({s.roles['E']: 1}))])
def test_t15_unmodelled_dependency_is_refused_not_rewritten(source, tmp_path, name, edit):
    root, pins = world_variant(source, tmp_path, lambda v: edit(v, source))
    att = attestation(tmp_path, 'stage1')
    refused(invoke('stage1', dict(common(source, att, tmp_path / 'out', root, pins),
                                  **{'build-digest': BUILD2.digest})), 'REBIND_UNMODELLED_DEPENDENCY')
    assert not (tmp_path / 'out').exists()


def opaque_references(value):
    """Find typed opaque references without relying on the tool's parser."""
    found, stack = set(), [value]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            if item.get('kind') == 'ct.evidence-content' and isinstance(item.get('sha256'), str):
                found.add(item['sha256'])
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    return found


def opaque_digests(source):
    """Digests referenced as ct.evidence-content anywhere in the source (independent of the tool)."""
    found = set()
    for files in source.contents.values():
        for wire in files.values():
            try:
                value = json.loads(wire)
            except ValueError:
                continue
            found.update(opaque_references(value))
    return found


def test_t15_literal_historical_digest_in_provenance_prose_is_preserved(source, tmp_path):
    """Owner disposition A: provenance label/basis prose may cite historical digests verbatim."""
    opaque = opaque_digests(source)
    candidates = []
    for digest in source.pins['unchanged']['selection_objects']:
        if digest in opaque:
            continue
        value = json.loads(source.contents['selection_objects'][digest])
        # Rehashing the sole referrer to opaque bytes would disconnect that payload
        # from the role roots. Keep this test focused on provenance prose, rather
        # than introducing an unrelated source-closure mutation.
        if opaque_references(value):
            continue
        if isinstance(value.get('provenance'), dict) and isinstance(value['provenance'].get('basis'), str):
            candidates.append((digest, value))
    assert candidates, 'the source needs an unchanged parsed record with provenance prose'
    old_copy, copied = candidates[0]
    prose = ' [cites build ' + source.build1.digest + ' and target ' + source.roles['J'][:12] + ']'
    copied['provenance']['basis'] += prose
    copied_wire = canon(copied)
    a0 = source_value(source, 'A0')
    a0['provenance']['basis'] += prose
    a0_wire = canon(a0)
    root, pins = source_variant(source, tmp_path / 'ok', replace=[('selection_objects', old_copy, copied_wire),
                                                                   ('selection_objects', source.roles['A0'], a0_wire)],
                                roles={'A0': sha(a0_wire)})
    att = attestation(tmp_path, 'stage1')
    out = tmp_path / 'ok-out'
    result = invoke('stage1', dict(common(source, att, out, root, pins), **{'build-digest': BUILD2.digest}))
    assert result.code == 0, result.raw_err
    # The copied record keeps its literal prose byte for byte; nothing is rewritten.
    assert (out / 'selection/objects' / sha(copied_wire)).read_bytes() == copied_wire
    hits = review_of(out)['diagnostics']['output_scan']
    path = 'selection/objects/' + sha(copied_wire)
    assert {(h['path'], h['pointer'], h['historical'], h['classification']) for h in hits} >= {
        (path, '/provenance/basis', 'historical_build', 'in_attestation_text'),
        (path, '/provenance/basis', 'roles/J', 'in_attestation_text')}
    assert all(h['pointer'] in ('/provenance/label', '/provenance/basis') for h in hits)
    assert {h['record'] for h in hits if h['path'] == path} == {'copied'}
    # The rendered A0 takes the supplied attestation (the declared rule); its lineage keeps the old prose verbatim.
    packet = json.loads((out / PACKET).read_bytes())
    change = [c for r in packet['records'] if r['role'] == 'A0' for c in r['changes']
              if c['pointer'] == '/provenance/basis']
    assert change == [{'pointer': '/provenance/basis', 'old': a0['provenance']['basis'],
                       'new': TEST_ONLY_BASIS + ' [A0]', 'rule': 'attestation'}]
    # The same historical digest as a structured reference in the same record still refuses.
    copied['stale'] = kref(KINDS['X'], source.roles['X'])
    stale_wire = canon(copied)
    root, pins = source_variant(source, tmp_path / 'stale', replace=[('selection_objects', old_copy, stale_wire)])
    refusal = refused(invoke('stage1', dict(common(source, att, tmp_path / 'stale-out', root, pins),
                                            **{'build-digest': BUILD2.digest})), 'REBIND_UNMODELLED_DEPENDENCY')
    assert refusal.err['target'] == '/source/objects/' + sha(stale_wire) + '/stale/sha256'
    assert not (tmp_path / 'stale-out').exists()


def test_t15_misleading_digest_like_text_is_not_a_dependency(source, tmp_path):
    root, pins = world_variant(source, tmp_path, lambda v: v.update(
        note='abcdef0123456789' * 4 + ' ' + BUILD2.digest[:16]))
    att = attestation(tmp_path, 'stage1')
    result = invoke('stage1', dict(common(source, att, tmp_path / 'out', root, pins),
                                   **{'build-digest': BUILD2.digest}))
    assert result.code == 0, result.raw_err


@pytest.mark.parametrize('digest,code', [('0' * 64, 'REBIND_USAGE'), ('g' * 64, 'REBIND_USAGE'),
                                         ('A' * 64, 'REBIND_USAGE'), ('a' * 63, 'REBIND_USAGE')])
def test_t16_build_argument_shape(source, tmp_path, digest, code):
    att = attestation(tmp_path, 'stage1')
    refused(invoke('stage1', stage1_flags(source, tmp_path / 'out', att, **{'build-digest': digest})), code)


def test_t16_historical_build_argument_is_refused(source, tmp_path):
    att = attestation(tmp_path, 'stage1')
    refused(invoke('stage1', stage1_flags(source, tmp_path / 'out', att, **{'build-digest': source.build1.digest})),
            'REBIND_INPUT_INVALID')
    assert not (tmp_path / 'out').exists()


def test_t16_resource_bounds(source, tmp_path):
    att = attestation(tmp_path, 'stage1')
    big = tmp_path / 'big-attest.json'
    big.write_bytes(att[0].read_bytes() + b' ' * 32769)
    refused(invoke('stage1', stage1_flags(source, tmp_path / 'o1', (big, sha(big.read_bytes())))),
            'REBIND_RESOURCE_LIMIT')
    big_pins = tmp_path / 'big-pins.json'
    big_pins.write_bytes(source.pins_path.read_bytes() + b' ' * 65537)
    refused(invoke('stage1', dict(common(source, att, tmp_path / 'o2', pins=(big_pins, sha(big_pins.read_bytes()))),
                                  **{'build-digest': BUILD2.digest})), 'REBIND_RESOURCE_LIMIT')
    deep = tmp_path / 'deep-pins.json'
    nested = []
    for _ in range(30):
        nested = [nested]
    deep.write_bytes(canon(dict(source.pins, label='deep', unused=nested)))
    refused(invoke('stage1', dict(common(source, att, tmp_path / 'o3', pins=(deep, sha(deep.read_bytes()))),
                                  **{'build-digest': BUILD2.digest})), 'REBIND_RESOURCE_LIMIT')
    root, pins = source_variant(source, tmp_path / 'v', replace=[('simulation_input', world_digest(source),
                                                                   b' ' * 196609)])
    refused(invoke('stage1', dict(common(source, att, tmp_path / 'o4', root, pins),
                                  **{'build-digest': BUILD2.digest})), 'REBIND_RESOURCE_LIMIT')


def test_parser_accepts_finite_floats_and_refuses_nonfinite_or_noncanonical():
    assert rb.parse_strict(b'{"a":1794.0,"b":[3721.845,45.2]}', '/t') == {'a': 1794.0, 'b': [3721.845, 45.2]}
    for wire in (b'{"a":NaN}', b'{"a":Infinity}', b'{"a":-Infinity}', b'{"a":1e400}', b'{"a":1E3}',
                 b'{"a":1,"a":1}', b'{"b":1,"a":2}', b'{"a":1} ', b'\xef\xbb\xbf{"a":1}', b'{"a":"\\ud800"}'):
        with pytest.raises(rb.Refusal) as denied:
            rb.parse_strict(wire, '/t')
        assert denied.value.code == 'REBIND_INPUT_INVALID', wire
    for wire in (canon([0] * 70000), canon({'a': 'x' * 4097}), canon(json.loads('[' * 25 + ']' * 25))):
        with pytest.raises(rb.Refusal) as denied:
            rb.parse_strict(wire, '/t')
        assert denied.value.code == 'REBIND_RESOURCE_LIMIT'


def test_usage_refusals():
    for argv in ([], ['stage4'], ['stage1', '--out'], ['stage1', '--unknown', 'x'],
                 ['stage1', '--out=x'], ['stage1', 'positional', 'x']):
        out, err = io.StringIO(), io.StringIO()
        assert rb.main(argv, out=out, err=err) == 2
        refusal = json.loads(err.getvalue())
        assert set(refusal) == {'code', 'target'} and refusal['code'] == 'REBIND_USAGE'
        assert refusal['target'].startswith('/argv') and out.getvalue() == ''
    flags = []
    for name in rb.FLAGS['stage1']:
        flags += ['--' + name, '1' * 64]
    out, err = io.StringIO(), io.StringIO()
    assert rb.main(['stage1'] + flags + ['--out', 'again'], out=out, err=err) == 2   # duplicate flag
    assert rb.main(['stage1'] + flags[:-2], out=out, err=err) == 2                 # missing flag


def test_unexpected_failure_never_leaks_a_traceback_or_path(monkeypatch):
    def boom(_values):
        raise RuntimeError('/home/somebody/secret/path')
    monkeypatch.setitem(rb.STAGES, 'stage1', boom)
    flags = []
    for name in rb.FLAGS['stage1']:
        flags += ['--' + name, '1' * 64]
    out, err = io.StringIO(), io.StringIO()
    assert rb.main(['stage1'] + flags, out=out, err=err) == 7
    assert err.getvalue() == '{"code":"REBIND_INTERNAL","target":"/"}\n' and out.getvalue() == ''


def test_isolated_entry_point_renders_stage1(source, tmp_path):
    att = attestation(tmp_path, 'stage1')
    argv = [sys.executable, '-I', '-B', str(TOOL), 'stage1']
    for key, value in stage1_flags(source, tmp_path / 'out', att).items():
        argv += ['--' + key, str(value)]
    done = subprocess.run(argv, capture_output=True, timeout=300, env={}, cwd=str(tmp_path))
    assert done.returncode == 0, done.stderr
    line = json.loads(done.stdout)
    assert line['outcome'] == 'rendered' and line['stage'] == 'stage1' and line['out'] == str(tmp_path / 'out')
    assert line['review_sha256'] == sha((tmp_path / 'out' / REVIEW).read_bytes())
    usage = subprocess.run([sys.executable, '-I', '-B', str(TOOL)], capture_output=True, timeout=60, env={})
    assert usage.returncode == 2 and json.loads(usage.stderr)['code'] == 'REBIND_USAGE' and b'Traceback' not in usage.stderr


def test_tool_imports_only_the_standard_library():
    text = TOOL.read_text('utf-8')
    modules = set(re.findall(r'^(?:import|from)\s+([A-Za-z_][\w.]*)', text, flags=re.MULTILINE))
    assert modules <= {'copy', 'hashlib', 'json', 'os', 're', 'stat', 'sys'}, modules
    assert 'applications' not in modules and 'backend' not in modules and 'subprocess' not in text


# --------------------------------------------- retained pilot pins (static data)

PILOT_PINS = {
    'historical_build': '0fc2cd251919ed1d47fc9476627c1beb6f486480d14d104016c1910cd6de4f31',
    'label': 't1-real-build-07055c6-pilot1 retained synthetic inputs',
    'prior_bundle': {
        'applicability.json': 'b2b47b40d36b74738ebaf95c34ee6bef28a5923ec50507c8532d86ac4b0ccffd',
        'build.json': '0fc2cd251919ed1d47fc9476627c1beb6f486480d14d104016c1910cd6de4f31',
        'closure.json': '395d99e71757fe9df63e830d52cb4c70644019ae37d797c098811e7bf35432fe',
        'derivation.json': '241be4a57715518979e0b803e8cd2af74ab2b6e024a526d1c29ad70c2509216a',
        'invocation.json': '2ba0eb59fd64adcd1fc348549f9f6ceb64e2a00c0a2cd15a6adc92fcf8fb5abf',
        'manifest.json': '55241fa16e73735f18ed0e345545ad7420c2cd8e1a4f1c99891f8625d2233c03',
        'policy.json': '9bf140fb5ceba8e4c9713b05b5a68982139020545557b2150994a0c5eb4e5bd0',
        'result.json': '3d30270d1b412d8ed4f907b3f5df85767b5c99e021628c438c1b0c45ed9b03e1',
        'trace.json': 'ce249a6b179bbf1215936c3b16ad958a340b5ecbfa1c80a6f98fc1ca85aac336'},
    'roles': {
        'A0': '40ae3dcb176d23f01962eac23f75253ee75c4ea6a14ba94e60dedd00c68bf9a8',
        'E': '408492e8fb8622a6b833a4b53bf915ad826e6799a056eb0c5ec87ac5eaa32623',
        'G': 'd4cd11c672c574d0cbe7c3ec59d9b913a910ae357689b9c3c55e268bd80cddff',
        'J': '11669422a04923b0a0a9f142596fb550e0b80525ab65a5ac59a9a922c3037c22',
        'P': 'f32c2ce2b35cb99096a0d0e9292884f863b362a37c0b649008cb1967943501ea',
        'R': '5f72989d8fae0e84ffdcf9e56201d512f3c202755adb1dcf318c875ff9318419',
        'X': '38c7e3b27579bdee438422e0a9af09b0289a274c0bfd4bed97df0d7176f2923e',
        'evidence': '686ecc43776ea181b08affd0a6f358569f7d14f6abcce1f6b0a53e892c0302f3',
        'policy': '9bf140fb5ceba8e4c9713b05b5a68982139020545557b2150994a0c5eb4e5bd0',
        'simulator_policy': '2342bbcb7cd6e8d3844babe2cf02da77789e31f9afc5ff663f280baa4d9e3b03'},
    'schema': 't1-rebind-source-pins.v1',
    'unchanged': {
        'request_input': [
            '0556afd2d6a07b7d7707b3bbfd6cce931fe16f7958dcdd1edc29607a0398ed2b',
            '12e8aef124dd02d5e8fc03041f97c7ce6358a2e764c13b420c9b0b02d003e432',
            '1bf93c61b0257c52d73ba3f5e5fe2edac891be7cd01b1e4747a499f55cca1dd5',
            '26f7f721c58eb14d9b408b6f57ee106940775988374a7d3cd4c28f08cba88523',
            '30046f1d78fd7ba9042c42b5d912541e875c54a0168e91bc28f77fdfae061d48',
            '3a8c64c80f526ab412740cc7c53a4de404d321f2ffe34c10fb5446d0a83af49e',
            '4563057222ca24d6551ad34f5f253edcb934df5fe87288dd56dad6459f479cf1',
            '6856bb132d9f09e132a99edfcc610fdf26eb0cc71c1ea21c6f55b0801ca82687',
            '781f17e256116d8ef3ee2830ef53f8d3909442aaec4e327d631ebde7fd931702',
            '7acd0ff4cd6cda435363efad1e13c47d9491f9ca539a9bc887538778c3e04b33',
            '8cdc79795904891d46cbfe36c9e190c8f5b8a609d3826f73f129ebf59a50e9cf',
            '8da15d1e3ed4aa8eacecb9bb4a2786bc91c0451c22739fb5537efad4fcbf53f1',
            '9010a3e9936ee25a1480ab098591f4169ce76d8e64a0253b352c45a681ffe140',
            '9022a97109eb1292e41b24931fb65984699828206be1dd18a0dec643f8beec29',
            '9199aebfad6169354ff7b791ec1b5e16c3509f9daef1d305b1465aae43cb1fee',
            '92af15b3cd6c75de6ca8c02bd806888aebb6ef429d240d78c7f534af34d0086e',
            '981c547126a208c49230d93b09ae8df70e83d7c9fbe74b4806a812d27c5b2953',
            'a0784c0cca3ff194048876715a07bc21ffc3be28ba75da9cc65eb27aa79db491',
            'ad2b02d8853c1f1a3c35e6775fee7349b7cba45ab8e56483457751e3c9edea54',
            'b49f67d428a1c1da3109ddbea446f1f0445ffb62053f0da3ffc7fdf6de8c3023',
            'b93c883d9a9bbb8aeafee4461a57d395aee336fa8e9a0d8da78f529ca3910d95',
            'c391db986ebc81f827f37f47f9d66dc762dd2ba85670bfda983b94f1de5f2e66',
            'd40aae9ab374a6abfa9590f434625f699193d7f5e06527163f17a7d06c1ec49f',
            'dfe3bd99d1411285a94b2b58c688736b8db37a9aa4934118289131cf862c09a7',
            'e9d5de69e05ecf61c4b875aabf049b2afa5ba208b25039969262b268360f4218'],
        'selection_objects': [
            '002a0661d5d3cc138fe1d60084fbb43f518f04867165ba6d1b50b8106f137230',
            '0caa3b60b1ca3741bf3089dc0ca0621d50fe066c94f6ea6612211da8c749a73e',
            '129da0f451934439d834542d949e85e666881809c588cc9bd9097b2b4eeb017f',
            '18c97d3341a1c83c64a2e385738e6e51662c0f272b089293091bc033e0f6761b',
            '3ae1b420f270e61c1a10d9772fd6ec931d9b7ef338cdce2ea5829981f6e503df',
            '3db3088cbd0f60b7e442bf23d9fc8973a457a48cb8a1f371f601f7416756e7b4',
            '3e7872efdb23d251e03638a1d3cd1d8b49b9db5933fca7864b87d8792a87fc3b',
            '3ee074cfd7658b417d1e7da6544a8da7726d1bb193e5143d2e466f7a6236773d',
            '3f9359a6a37492cf420ab2328dc528425ddebe99999d630af8e059dbe2bd9b71',
            '40794ad73a65a327447208daad6e178ab1540dc30df4254e30bc15684cba083b',
            '409dfcc56e3fd8e0489e38fd3f5281945c088540c2614d22f4b6e297b1607dfa',
            '64958dbf1d62c6e80f86c84cddbee55abdb6f80e00393ed95cd0749000b98d78',
            '6833d60e908e835fc5f1bb2e71fb13f629fde5fa1927c2caeb2b3b92d874e4ca',
            '68549a7d01c78a19ec58ff92663e43d3d9f9cb58cfc44735fa10c82fc19a2fcd',
            '74ed047e310c49bf407ef6a9992fec8af2d9e0044bd120c00bf380605c2d3d15',
            '7ef655c8292ecccf2fe1acd6c1c2359f17cdf29afb64f768c9897e5e9033fec9',
            '8e887c241326027181701d35a6a834f3ace3be9f01925370a6e8f6c945901a93',
            '92af15b3cd6c75de6ca8c02bd806888aebb6ef429d240d78c7f534af34d0086e',
            '94a409640ceeaf3a5d1bb1420d2a3f6aa6648f0b0696329519bf227c45f26db7',
            'a0784c0cca3ff194048876715a07bc21ffc3be28ba75da9cc65eb27aa79db491',
            'a33a4700231333faff70c6a02bc7c592c2735feb4c0c3529a1c2a109b05b2161',
            'a82ec558e9daa45bcc3ae12d1de70f607d0d947eadd91e7f1a11b653989cd80f',
            'ac18f99ea2410b94d51273b19f21769873e642a5a62c6d48431ef3decb1997d7',
            'ad2b02d8853c1f1a3c35e6775fee7349b7cba45ab8e56483457751e3c9edea54',
            'b14af7212efde7dafe38f3861268af5c8ac6b7de9eca69b075f40e1726a92b33',
            'b49f67d428a1c1da3109ddbea446f1f0445ffb62053f0da3ffc7fdf6de8c3023',
            'b7a0f2251fbc185378047db93475ec6b38e988de8bb9ac682c52d8a4ba7c41d3',
            'c391db986ebc81f827f37f47f9d66dc762dd2ba85670bfda983b94f1de5f2e66',
            'c6b94b19c6e151b0b9f7f6114a3683781b5d7ba63eea8ff304c1f834931e0dee',
            'c97ee427cba1ec2e43e510cbeb039d825d3af577697f7a718b6eb803414a1a89',
            'de04f010551007452290eab72d3fb0793321970d368e9b4085930edd6199ccfe',
            'dfd037fa139adf8b9c79bcae3aaf2fce2abf4d1278f8e0e4f543254c2020cef1',
            'ef085887789a1e4d2cdb15bb5731acd8e50f049cb755363e40d95e261d6c1105',
            'f124e640af847355b852d3af6dacfb68c6a6fbbb3e8979ee138d0d7420525b2c',
            'fdd34c6a138d5fe8860844aed7302265d3c7d3fa1bd08cfebe92fd407a2a02d3'],
        'simulation_input': [
            '13ec186684a467474d516589a4d8c39d9630fd6fa24226b8bac722279caa27a8',
            '529b18406a7daf8ed0218b72a12d031c7cca76c3fb0cc574b420da620dfb858b',
            '92af15b3cd6c75de6ca8c02bd806888aebb6ef429d240d78c7f534af34d0086e',
            'a0784c0cca3ff194048876715a07bc21ffc3be28ba75da9cc65eb27aa79db491',
            'ad2b02d8853c1f1a3c35e6775fee7349b7cba45ab8e56483457751e3c9edea54',
            'b49f67d428a1c1da3109ddbea446f1f0445ffb62053f0da3ffc7fdf6de8c3023',
            'c29ebd6fe7f0b0ae0308b354fcec96528b06023f724aa78fb07679879fd47c17',
            'c391db986ebc81f827f37f47f9d66dc762dd2ba85670bfda983b94f1de5f2e66',
            'c6f0cafaed466ab8a18d3d7340632a9863d0526e4656b8311b8db55c96f03125']}}


def test_specification_pilot_pins_are_accepted_with_their_inventory():
    membership = rb.validate_pins(copy.deepcopy(PILOT_PINS))
    assert {k: len(v) for k, v in membership.items()} == {
        'selection_objects': 37, 'simulation_input': 14, 'request_input': 30}
    distinct = {d for v in membership.values() for d in v} | {PILOT_PINS['roles']['P']}
    assert len(distinct) == 69
    broken = copy.deepcopy(PILOT_PINS)
    del broken['prior_bundle']['manifest.json']
    with pytest.raises(rb.Refusal) as denied:
        rb.validate_pins(broken)
    assert denied.value.code == 'REBIND_INPUT_INVALID'
