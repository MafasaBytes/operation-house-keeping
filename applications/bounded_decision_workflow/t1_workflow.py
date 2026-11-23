"""Maintained handoff, separately authorized delegation and F verification.

No authority, adoption, reranking or human disposition is produced here. A
completed synthetic workflow remains material for an explicit human decision.
"""
import base64
import json
import os
from argparse import Namespace
from pathlib import Path
from .t1_contracts import PROFILE, SCHEMAS, canonical_bytes, ref, refuse, sha
from .t1_records import parse
from .t1_package import Publication, safe_new_dir
from .t1_reassessment_handoff import assemble_carriage
from . import t1_simulation as simulation


def _calibration_members(delegated):
    if delegated:
        from .checked_runtime import BUNDLE_NAMES
        return {'workflow-receipt.json'} | {'bundle/' + name for name in BUNDLE_NAMES}
    return {'workflow-receipt.json', 'receipt/admission-closure.json',
            'receipt/base-applicability.json', 'receipt/build.json'}


def read_package(directory, *, cap=64 * 1048576, entries=256, target='/package', companion=False):
    root = Path(directory)
    files, total = {}, 0
    directories = set()
    try:
        if not root.exists():
            refuse('SIM_REFERENCE_MISSING', 1, target)
        if not root.is_dir() or root.is_symlink() or any(p.is_symlink() for p in root.parents):
            refuse('SIM_OUTPUT_UNSAFE', 0, '/argv/input-dir', 5)
        pending, observed = [root], 0
        while pending:
            parent = pending.pop()
            with os.scandir(parent) as children:
                for entry in children:
                    observed += 1
                    if observed > entries * 2:
                        refuse('SIM_RESOURCE_LIMIT', 1, '/package', 4)
                    path = Path(entry.path)
                    if companion and entry.name == 'PARTIAL':
                        refuse('SIM_PUBLICATION_INCOMPLETE', 1, target, 5)
                    if entry.is_symlink():
                        refuse('SIM_REFERENCE_INVALID', 1, '/package')
                    if entry.is_dir(follow_symlinks=False):
                        if companion:
                            relative = path.relative_to(root).as_posix()
                            if relative not in ('receipt', 'bundle'):
                                refuse('CALIBRATION_PACKAGE_MISMATCH', 9, '/F/package')
                            directories.add(relative)
                        pending.append(path)
                        continue
                    if not entry.is_file(follow_symlinks=False) or len(files) >= entries:
                        refuse('SIM_RESOURCE_LIMIT', 1, '/package', 4)
                    with path.open('rb') as stream:
                        wire = stream.read(min(cap - total, 4 * 1048576) + 1)
                    total += len(wire)
                    if total > cap or len(wire) > 4 * 1048576:
                        refuse('SIM_RESOURCE_LIMIT', 1, '/package', 4)
                    files[path.relative_to(root).as_posix()] = wire
    except OSError:
        refuse('SIM_REFERENCE_MISSING', 1, '/package', 5)
    if 'PARTIAL' in files:
        refuse('SIM_PUBLICATION_INCOMPLETE', 1, target, 5)
    if companion:
        if 'workflow-receipt.json' not in files:
            refuse('SIM_REFERENCE_MISSING', 1, target)
        if (directories not in ({'bundle'}, {'receipt'}) or
                set(files) != _calibration_members(directories == {'bundle'})):
            refuse('CALIBRATION_PACKAGE_MISMATCH', 9, '/F/package')
    return dict(sorted(files.items()))


def prepare_handoff(*, producer_files, manifest_pin, pins, prior_pins, build, scratch, output,
                    request_wire, request_objects):
    safe_new_dir(output)
    _intake_request(request_wire, request_objects, producer_files, manifest_pin, pins, build)
    verified = simulation.verify(files=producer_files, manifest_pin=manifest_pin, pins=pins,
                                 prior_pins=prior_pins, build=build, workspace=scratch)
    h = assemble_carriage(request_wire=request_wire, manifest_wire=producer_files['manifest.json'],
        admission=verified['admission'], receipt=verified['receipt'], prior_pins=prior_pins,
        request_objects=request_objects, producer_evidence_wire=producer_files['evidence/public/evidence.json'])
    from .t1_reassessment_handoff import _request_closure
    complete = _request_closure(request_wire, request_objects, verified['admission'], verified['receipt'],
                                producer_files['evidence/public/evidence.json'])
    files = {'objects/' + d: w for d, w in complete.items()}
    files['objects/' + sha(request_wire)] = request_wire
    publication = Publication(output, final='handoff.json', target='/H')
    for path, wire in sorted(files.items()):
        publication.write(path, wire)
    publication.finish(h)
    return dict(files, **{'handoff.json': h})


def _handoff(*, handoff_files, handoff_pin, producer_files, verified, request_pin, prior_pins):
    if 'PARTIAL' in handoff_files:
        refuse('SIM_PUBLICATION_INCOMPLETE', 1, '/H', 5)
    wire = handoff_files.get('handoff.json')
    if wire is None:
        refuse('SIM_REFERENCE_MISSING', 1, '/H')
    h, _ = parse(wire, 'ct.t1-handoff.v1', '/H')
    if sha(wire) != handoff_pin:
        refuse('SIM_PIN_MISMATCH', 1, '/H')
    if h['request']['sha256'] != request_pin:
        refuse('SIM_PIN_MISMATCH', 1, '/R')
    objects = {}
    for path, value in sorted(handoff_files.items()):
        if path == 'handoff.json':
            continue
        if path != 'objects/' + sha(value):
            refuse('SIM_REFERENCE_INVALID', 1, '/H/objects')
        objects[sha(value)] = value
    if request_pin not in objects:
        refuse('SIM_REFERENCE_MISSING', 1, '/R')
    request = objects.pop(request_pin)
    from .t1_reassessment_handoff import _request_closure
    reached = _request_closure(request, objects, verified['admission'], verified['receipt'],
                               producer_files['evidence/public/evidence.json'])
    if set(reached) != set(objects) | {request_pin}:
        refuse('SIM_REFERENCE_MISSING', 1, '/H/objects')
    expected = assemble_carriage(request_wire=request, manifest_wire=producer_files['manifest.json'],
        admission=verified['admission'], receipt=verified['receipt'], prior_pins=prior_pins,
        request_objects=objects, producer_evidence_wire=producer_files['evidence/public/evidence.json'])
    expected_value = json.loads(expected)
    # The authority equality is deliberately checked before other H joins.
    if h['execution_authority'] != verified['admission'].references['E']:
        refuse('HANDOFF_AUTHORITY_JOIN_MISMATCH', 8, '/H/execution_authority')
    for key in sorted(expected_value):
        if h[key] != expected_value[key]:
            refuse('HANDOFF_JOIN_MISMATCH', 8, '/H/' + key)
    return h, request, objects


def _intake_handoff(handoff_files, handoff_pin, request_pin, producer_files, manifest_pin, pins, build):
    """Pure order1 root/closure intake, before permission or backend effects."""
    from .t1_closure import inspect_package
    from .t1_records import Admission
    from .t1_reassessment_handoff import _request_closure
    closure = inspect_package(producer_files['manifest.json'], producer_files, manifest_pin=manifest_pin)
    for name, letter in (('target', 'J'), ('execution_authority', 'E'), ('permission', 'G')):
        if closure.manifest['roots'][name]['sha256'] != pins[letter]:
            refuse('SIM_PIN_MISMATCH', 1, '/' + letter)
    if 'PARTIAL' in handoff_files: refuse('SIM_PUBLICATION_INCOMPLETE', 1, '/H', 5)
    wire = handoff_files.get('handoff.json')
    if wire is None: refuse('SIM_REFERENCE_MISSING', 1, '/H')
    h, _ = parse(wire, 'ct.t1-handoff.v1', '/H')
    if sha(wire) != handoff_pin: refuse('SIM_PIN_MISMATCH', 1, '/H')
    if h['request']['sha256'] != request_pin: refuse('SIM_PIN_MISMATCH', 1, '/R')
    pool = {}
    for path, data in handoff_files.items():
        if path == 'handoff.json': continue
        if path != 'objects/' + sha(data): refuse('SIM_REFERENCE_INVALID', 1, '/H/objects')
        pool[sha(data)] = data
    request = pool.pop(request_pin, None)
    if request is None: refuse('SIM_REFERENCE_MISSING', 1, '/R')
    parse(request, 'ct.request.v1', '/R')
    a = Admission({sha(w): w for p, w in producer_files.items() if p.startswith('objects/')}, closure.records,
        {letter: closure.manifest['roots'][name] for name, letter in
            (('target', 'J'), ('execution_authority', 'E'), ('permission', 'G'))},
        closure.prior_files, {sha(w) for w in closure.prior_files.values()}, build)
    receipt = closure.get(closure.manifest['roots']['receipt'])
    reached = _request_closure(request, pool, a, receipt, producer_files['evidence/public/evidence.json'], check_identity=False)
    if set(reached) != set(pool) | {request_pin}: refuse('SIM_REFERENCE_MISSING', 1, '/H/objects')


def _intake_request(request, pool, producer_files, manifest_pin, pins, build):
    from .t1_closure import inspect_package
    from .t1_records import Admission
    from .t1_reassessment_handoff import _request_closure
    closure = inspect_package(producer_files['manifest.json'], producer_files, manifest_pin=manifest_pin)
    for name, letter in (('target', 'J'), ('execution_authority', 'E'), ('permission', 'G')):
        if closure.manifest['roots'][name]['sha256'] != pins[letter]:
            refuse('SIM_PIN_MISMATCH', 1, '/' + letter)
    parse(request, 'ct.request.v1', '/R')
    a = Admission({sha(w): w for p, w in producer_files.items() if p.startswith('objects/')}, closure.records,
        {letter: closure.manifest['roots'][name] for name, letter in
            (('target', 'J'), ('execution_authority', 'E'), ('permission', 'G'))},
        closure.prior_files, {sha(w) for w in closure.prior_files.values()}, build)
    return _request_closure(request, pool, a, closure.get(closure.manifest['roots']['receipt']),
                            producer_files['evidence/public/evidence.json'], check_identity=False)


def require_disjoint_paths(inputs, outputs):
    """New companion operations cannot write into or above retained input roots."""
    roots = [Path(os.path.abspath(p)) for p in inputs]
    dests = [Path(os.path.abspath(p)) for p in outputs if p is not None]
    for destination in dests:
        safe_new_dir(destination)
    for i, destination in enumerate(dests):
        for other in roots + dests[:i]:
            if destination == other or destination in other.parents or other in destination.parents:
                refuse('SIM_OUTPUT_UNSAFE', 0, '/argv/path-overlap', 5)


def _calibration_context(*, producer_files, manifest_pin, pins, prior_pins, build, scratch,
                         handoff_files, handoff_pin, request_pin, authority_pin, authority_objects):
    from . import checked_runtime, t1_calibration_gate as gate
    producer_files, handoff_files, authority_objects = dict(producer_files), dict(handoff_files), dict(authority_objects)
    if 'manifest.json' not in producer_files:
        refuse('SIM_REFERENCE_MISSING', 1, '/M')
    _intake_handoff(handoff_files, handoff_pin, request_pin, producer_files, manifest_pin, pins, build)
    verified = simulation.verify(files=producer_files, manifest_pin=manifest_pin, pins=pins,
                                 prior_pins=prior_pins, build=build, workspace=scratch)
    h, request, objects = _handoff(handoff_files=handoff_files, handoff_pin=handoff_pin,
        producer_files=producer_files, verified=verified, request_pin=request_pin, prior_pins=prior_pins)
    # Every separately supplied object remains in the owning input pool; extra
    # correction/source-set objects must be refused, not silently discarded.
    delegated_objects = dict(objects, **authority_objects)
    preflight = checked_runtime.preflight_reassessment(request_wire=request, objects=delegated_objects,
        prior_files=verified['admission'].prior_files, request_pin=request_pin,
        authority_pin=authority_pin, build=build)
    finding = gate.qualify_carried_calibration(verified=verified, producer_files=producer_files,
        handoff_wire=handoff_files['handoff.json'], request_wire=request, preflight=preflight)
    input_pins = dict(M=manifest_pin, J=pins['J'], E=pins['E'], G=pins['G'], H=handoff_pin,
        R=request_pin, A=authority_pin, prior_request=prior_pins['request_sha256'],
        prior_authority=prior_pins['authority_sha256'])
    return dict(verified=verified, request=request, objects=delegated_objects,
                preflight=preflight, finding=finding, input_pins=input_pins)


def _finish_calibration(publication, context, *, bundle=None, operation='t1-reassessment-evaluate', replay_of=None):
    from . import t1_calibration_gate as gate
    preflight = context['preflight']
    outcome = gate.build_outcome(finding=context['finding'], preflight=preflight,
        input_pins=context['input_pins'], bundle=bundle, operation=operation, replay_of=replay_of)
    wire = gate.encode(outcome)
    if bundle is None:
        members = {'receipt/admission-closure.json': preflight['closure_wire'],
                   'receipt/base-applicability.json': canonical_bytes(preflight['applicability']),
                   'receipt/build.json': preflight['build_wire']}
        for path, value in members.items():
            publication.write(path, value)
    else:
        members = {'bundle/' + n: w for n, w in bundle.items()}
    publication.finish(wire)
    return dict(members, **{'workflow-receipt.json': wire})


def evaluate(*, producer_files, manifest_pin, pins, prior_pins, build, scratch, output,
             handoff_files, handoff_pin, request_pin, authority_pin, authority_objects):
    from . import checked_cli
    from .checked_contracts import CheckedRefusal
    from .t1_contracts import SimRefusal
    require_disjoint_paths([], [scratch, output])
    context = _calibration_context(producer_files=producer_files, manifest_pin=manifest_pin,
        pins=pins, prior_pins=prior_pins, build=build, scratch=scratch,
        handoff_files=handoff_files, handoff_pin=handoff_pin, request_pin=request_pin,
        authority_pin=authority_pin, authority_objects=authority_objects)
    # A completed scientific block still requires valid source, H and full
    # owning authority/admission. No owner result or derivation is fabricated.
    if context['finding']['effect'] != 'permission_to_delegate':
        from . import t1_calibration_gate as gate
        # Freeze/validate the complete no-B root before starting publication.
        gate.build_outcome(finding=context['finding'], preflight=context['preflight'],
                           input_pins=context['input_pins'])
        publication = Publication(output, final='workflow-receipt.json', target='/F')
        return _finish_calibration(publication, context)
    publication = Publication(output, final='workflow-receipt.json', target='/F')
    delegate = Path(scratch) / 'delegate'
    try:
        delegate.mkdir()
        (delegate / 'objects').mkdir()
        (delegate / 'prior').mkdir()
        (delegate / 'request.json').write_bytes(context['request'])
        for digest, wire in context['objects'].items():
            (delegate / 'objects' / digest).write_bytes(wire)
        for name, wire in context['verified']['admission'].prior_files.items():
            (delegate / 'prior' / name).write_bytes(wire)
    except OSError:
        refuse('SIM_PUBLICATION_INCOMPLETE', 9, '/delegate', 5)
    try:
        checked_cli.execute(Namespace(operation='checked-reassessment-evaluate',
            expected_request_pin=request_pin, expected_authority_pin=authority_pin,
            request=str(delegate / 'request.json'), objects_dir=str(delegate / 'objects'),
            prior_bundle=str(delegate / 'prior'), cached_derivation=None,
            output_dir=str(Path(output) / 'bundle')), build=build)
    except (CheckedRefusal, SimRefusal):
        raise
    except Exception:
        refuse('SIM_INTERNAL_ERROR', 9, '/delegate', 7)
    bundle = checked_cli.read_bundle_dir(Path(output) / 'bundle')
    return _finish_calibration(publication, context, bundle=bundle)


def verify_calibration_workflow(*, workflow_files, workflow_pin, producer_files, manifest_pin,
                    handoff_files, handoff_pin, request_pin, authority_pin, pins, prior_pins,
                    build, scratch, replay_filesystem='unknown'):
    """Recompute the new companion guarantee; do not strengthen legacy verify."""
    from . import checked_runtime as rt, t1_calibration_gate as gate
    files = dict(workflow_files)
    wire = files.get('workflow-receipt.json')
    if wire is None:
        refuse('SIM_REFERENCE_MISSING', 1, '/F')
    if sha(wire) != workflow_pin:
        refuse('SIM_PIN_MISMATCH', 1, '/F')
    outcome = gate.parse(wire, gate.OUTCOME)
    delegated = outcome['delegation']['status'] == 'completed'
    if set(files) != _calibration_members(delegated):
        refuse('CALIBRATION_PACKAGE_MISMATCH', 9, '/F/package')
    prefix = 'bundle/' if delegated else 'receipt/'
    closure_name = prefix + ('closure.json' if delegated else 'admission-closure.json')
    # Decode using the existing capped, kind-aware ordinary checked closure.
    closure = rt._parse_closure(files[closure_name], rt.EDITION_LIMITS,
                               'reassessment_closure_file_bytes', '/F/closure')
    rt._enforce_kinds(rt.validate(closure, 'ct.closure.v1'), '/F/closure')
    pool, _kinds = rt.closure_pool(closure, rt.EDITION_LIMITS, '/F/closure')
    # All members are forwarded. Recomputed roots/descriptor and exact closure
    # comparison below reject dropped A/predecessors and unreferenced additions.
    context = _calibration_context(producer_files=producer_files, manifest_pin=manifest_pin,
        pins=pins, prior_pins=prior_pins, build=build, scratch=scratch,
        handoff_files=handoff_files, handoff_pin=handoff_pin, request_pin=request_pin,
        authority_pin=authority_pin, authority_objects=pool)
    if outcome['finding'] != context['finding']:
        refuse('CALIBRATION_FINDING_MISMATCH', 9, '/F/finding')
    bundle = {n: files['bundle/' + n] for n in rt.BUNDLE_NAMES} if delegated else None
    replay_bundle = None
    if delegated:
        if context['finding']['effect'] != 'permission_to_delegate':
            refuse('CALIBRATION_OUTCOME_MISMATCH', 9, '/F/delegation')
        rt.verify(bundle_files=bundle, request_pin=request_pin, authority_pin=authority_pin, build=build)
        # Full result/trace agreement is deliberately stronger than the old
        # verify report, achieved without changing that report's semantics.
        replay_bundle = rt.replay(bundle_files=bundle, request_pin=request_pin,
            authority_pin=authority_pin, build=build, filesystem=replay_filesystem)
    expected = gate.build_outcome(finding=context['finding'], preflight=context['preflight'],
        input_pins=context['input_pins'], bundle=bundle,
        operation=outcome['operation'], replay_of=outcome['replay_of'])
    if gate.encode(expected) != wire:
        refuse('CALIBRATION_OUTCOME_MISMATCH', 9, '/F')
    # These fixed members have no owning manifest on a no-B branch.
    for member in expected['members']:
        data = files[member['path']]
        if sha(data) != member['sha256'] or len(data) != member['bytes']:
            refuse('CALIBRATION_PACKAGE_MISMATCH', 9, '/F/members')
    if not delegated:
        preflight = context['preflight']
        for name, expected_wire in ((closure_name, preflight['closure_wire']),
                ('receipt/base-applicability.json', canonical_bytes(preflight['applicability'])),
                ('receipt/build.json', preflight['build_wire'])):
            if files[name] != expected_wire:
                refuse('CALIBRATION_OUTCOME_MISMATCH', 9, '/F/' + name)
    return dict(context, outcome=outcome, replay_bundle=replay_bundle)


def replay_calibration_workflow(*, output, **inputs):
    from . import checked_cli, t1_calibration_gate as gate
    require_disjoint_paths([], [inputs['scratch'], output])
    checked = verify_calibration_workflow(**inputs,
        replay_filesystem=checked_cli.filesystem_of(Path(output).parent))
    bundle = checked['replay_bundle']
    if bundle is not None:
        original_manifest = checked['outcome']['delegation']['owning_manifest']['sha256']
        if json.loads(bundle['invocation.json'])['replay_of'] != {'manifest_sha256': original_manifest}:
            refuse('CALIBRATION_OUTCOME_MISMATCH', 9, '/calibration/replay_origin')
    # The existing replay computation already verified the original full B.
    # It is call-local; verification alone never publishes this prospective B.
    gate.build_outcome(finding=checked['finding'], preflight=checked['preflight'],
        input_pins=checked['input_pins'], bundle=bundle, operation='t1-workflow-replay',
        replay_of=ref(gate.OUTCOME, inputs['workflow_files']['workflow-receipt.json']))
    publication = Publication(output, final='workflow-receipt.json', target='/F')
    if bundle is not None:
        checked_cli.publish(Path(output) / 'bundle', bundle)
    return _finish_calibration(publication, checked, bundle=bundle, operation='t1-workflow-replay',
        replay_of=ref(gate.OUTCOME, inputs['workflow_files']['workflow-receipt.json']))


def verify_workflow(*, workflow_wire, workflow_pin, bundle_files, producer_files, manifest_pin,
                    handoff_files, handoff_pin, request_pin, authority_pin, pins, prior_pins,
                    build, scratch):
    from . import checked_runtime
    f, _ = parse(workflow_wire, 'ct.t1-workflow-receipt.v1', '/F')
    if sha(workflow_wire) != workflow_pin:
        refuse('SIM_PIN_MISMATCH', 1, '/F')
    _intake_handoff(handoff_files, handoff_pin, request_pin, producer_files, manifest_pin, pins, build)
    if f['evaluation_authority']['sha256'] != authority_pin:
        refuse('SIM_PIN_MISMATCH', 1, '/A')
    _intake_authority(bundle_files, authority_pin)
    verified = simulation.verify(files=producer_files, manifest_pin=manifest_pin, pins=pins,
                                 prior_pins=prior_pins, build=build, workspace=scratch)
    h, request, _objects = _handoff(handoff_files=handoff_files, handoff_pin=handoff_pin,
        producer_files=producer_files, verified=verified, request_pin=request_pin, prior_pins=prior_pins)
    a = verified['admission']
    if f['execution_authority'] != a.references['E']:
        refuse('HANDOFF_AUTHORITY_JOIN_MISMATCH', 8, '/F/execution_authority')
    for key, expected in (('world', a.root('J')['world']), ('prior_pins', prior_pins),
        ('producer_manifest', ref('ct.t1-producer-manifest.v1', producer_files['manifest.json'])),
        ('handoff', ref('ct.t1-handoff.v1', handoff_files['handoff.json'])),
        ('request', ref('ct.request.v1', request)),
        ('evaluation_authority', {'kind': 'ct.authority.v1', 'sha256': authority_pin}),
        ('target', a.references['J']), ('permission', a.references['G']),
        ('producer_build', a.root('J')['producer_build']), ('checker_build', ref('ct.build.v1', build.wire())),
        ('output_manifest', ref('ct.bundle-manifest.v1', bundle_files['manifest.json']))):
        if f[key] != expected:
            refuse('HANDOFF_JOIN_MISMATCH', 8, '/F/' + key)
    report = checked_runtime.verify(bundle_files=bundle_files, request_pin=request_pin,
                                   authority_pin=authority_pin, build=build)
    # Checked closure independently pins R/A and validates authority validity.
    return dict(verified, guarantee='producer-checked', checked_report=report, workflow=f)


def _intake_authority(bundle_files, authority_pin):
    # The actual independently retained A root is recovered from owning B,
    # never from F's provenance assertion; target/validity remain owning9.
    try:
        pool = {}
        for item in json.loads(bundle_files['closure.json'])['members']:
            wire = base64.b64decode(item['data'], validate=True)
            if sha(wire) != item['sha256']:
                refuse('SIM_REFERENCE_INVALID', 1, '/A')
            pool[item['sha256']] = wire
        if authority_pin not in pool:
            refuse('SIM_REFERENCE_MISSING', 1, '/A')
        digest, current_id, expected_revision, seen = authority_pin, None, None, set()
        while digest is not None:
            if digest in seen:
                refuse('SIM_REFERENCE_INVALID', 1, '/A/predecessor')
            seen.add(digest)
            wire = pool.get(digest)
            if wire is None:
                refuse('SIM_REFERENCE_MISSING', 1, '/A/predecessor')
            authority, annotations = parse(wire, 'ct.authority.v1', '/A')
            if current_id is not None and (authority['id'] != current_id or authority['revision'] != expected_revision):
                refuse('SIM_REFERENCE_INVALID', 1, '/A/predecessor')
            if annotations:
                for pointer, provenance, allowed in annotations.roles:
                    if provenance['role'] not in allowed:
                        refuse('SIM_REFERENCE_INVALID', 1, '/A' + pointer + '/role')
            predecessor = authority['predecessor']
            if (authority['revision'] == 1) != (predecessor is None):
                refuse('SIM_REFERENCE_INVALID', 1, '/A/predecessor')
            if predecessor is not None and predecessor['kind'] != 'ct.authority.v1':
                refuse('SIM_REFERENCE_INVALID', 1, '/A/predecessor')
            current_id, expected_revision = authority['id'], authority['revision'] - 1
            digest = None if predecessor is None else predecessor['sha256']
    except (KeyError, ValueError, TypeError):
        refuse('SIM_REFERENCE_INVALID', 1, '/A')


def verification_report(verified, *, operation, subject_wire, scratch, build):
    index = 0 if operation == 't1-simulation-verify' else 1
    properties = SCHEMAS['records']['ct.t1-verification-report.v1']['oneOf'][index]['properties']
    paths = list(Path(scratch).rglob('*'))
    files = [p for p in paths if p.is_file()]
    result = dict(schema='ct.t1-verification-report.v1', profile=PROFILE, operation=operation,
        subject=ref('ct.t1-producer-manifest.v1' if index == 0 else 'ct.t1-workflow-receipt.v1', subject_wire),
        guarantee=properties['guarantee']['const'], checks=properties['checks']['const'],
        limitations=properties['limitations']['const'], checker_build=ref('ct.build.v1', build.wire()),
        reconstruction=dict(public_evidence_digest_equal=True, raw_digests_equal=True, transcripts_equal=True,
                            occurrence_id=verified['receipt']['admitted']['occurrence_id']),
        scratch_accounting=dict(files=len(files), directories=1 + sum(p.is_dir() for p in paths),
            logical_bytes=sum(p.stat().st_size for p in files), allocated_bytes=sum(p.stat().st_blocks * 512 for p in files)))
    wire = canonical_bytes(result)
    parse(wire, result['schema'], '/report')
    return wire
