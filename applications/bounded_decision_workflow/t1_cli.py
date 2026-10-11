"""Maintained T1 dispatch with trusted external pins and honest build identity.

No command-line identity override exists. In-process execute(build=...) is the
same labelled development seam as the owning checked command composition.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from .t1_contracts import PROFILE, SCHEMAS, SimRefusal, canonical_bytes, refuse, sha
from .t1_package import Publication, safe_new_dir
from . import t1_simulation, t1_workflow
from .checked_contracts import CheckedRefusal
from .checked_runtime import ExecutableBuild

COMMANDS = ('t1-simulation-prepare', 't1-simulation-run', 't1-simulation-verify', 't1-reassessment-prepare',
            't1-reassessment-evaluate', 't1-workflow-verify')
HEX = re.compile('[0-9a-f]{64}\\Z')


class Parser(argparse.ArgumentParser):
    def error(self, message): refuse('SIM_USAGE', 0, '/argv', 2)


def arguments(argv):
    parser = Parser(add_help=False, allow_abbrev=False)
    sub = parser.add_subparsers(dest='operation', required=True, parser_class=Parser)
    for op in COMMANDS:
        child = sub.add_parser(op, add_help=False, allow_abbrev=False)
        if op == 't1-simulation-prepare':
            for flag in ('expected-prior-request-pin', 'expected-prior-authority-pin', 'prior-bundle',
                         'world', 'context', 'objects-dir', 'output-dir'):
                child.add_argument('--' + flag, required=True)
            child.add_argument('--diagnostic-dir')
            continue
        flags = ['expected-target-pin', 'expected-execution-authority-pin', 'expected-permission-pin',
                 'expected-prior-request-pin', 'expected-prior-authority-pin', 'prior-bundle', 'output-dir']
        if op == 't1-simulation-run': flags += ['objects-dir']
        else: flags += ['producer-package', 'expected-producer-manifest-pin', 'scratch-dir']
        if op in ('t1-reassessment-prepare', 't1-reassessment-evaluate'): flags += ['objects-dir']
        if op in ('t1-reassessment-evaluate', 't1-workflow-verify'):
            flags += ['handoff-package', 'expected-handoff-pin', 'expected-request-pin', 'expected-authority-pin']
        if op == 't1-workflow-verify': flags += ['bundle', 'expected-workflow-receipt-pin']
        for flag in flags: child.add_argument('--' + flag, required=True)
        child.add_argument('--diagnostic-dir')
    flags = [v.split('=', 1)[0] for v in argv if v.startswith('--')]
    if len(flags) != len(set(flags)): refuse('SIM_USAGE', 0, '/argv', 2)
    args = parser.parse_args(argv)
    for name, value in vars(args).items():
        if name.endswith('_pin') and not HEX.fullmatch(value): refuse('SIM_USAGE', 0, '/argv/' + name, 2)
    return args


def _objects(path):
    files = t1_workflow.read_package(path)
    for name, wire in files.items():
        if len(wire) > 196608:
            refuse('SIM_RESOURCE_LIMIT', 0, '/objects/' + name, 4)
        if not HEX.fullmatch(name):
            refuse('SIM_REFERENCE_INVALID', 1, '/objects/' + name)
    return files


def execute(args, *, build):
    from . import checked_cli
    from .t1_closure import inspect_package
    op = args.operation
    if op == 't1-simulation-prepare':
        refuse('SIM_INTERNAL_ERROR', 0, '/incomplete/prepare-templates', 7)
    if args.diagnostic_dir is not None:
        safe_new_dir(args.diagnostic_dir, '/argv/diagnostic-dir')
    workflow_entries = None
    if op == 't1-workflow-verify':
        from .t1_records import parse
        workflow_entries = t1_workflow.read_package(Path(args.bundle).parent, target='/F')
        workflow_wire = workflow_entries.get('workflow-receipt.json')
        if workflow_wire is None: refuse('SIM_REFERENCE_MISSING', 1, '/F')
        parse(workflow_wire, 'ct.t1-workflow-receipt.v1', '/F')
        if sha(workflow_wire) != args.expected_workflow_receipt_pin:
            refuse('SIM_PIN_MISMATCH', 1, '/F')
    pins = {'J': args.expected_target_pin, 'E': args.expected_execution_authority_pin,
            'G': args.expected_permission_pin}
    prior_pins = dict(request_sha256=args.expected_prior_request_pin, authority_sha256=args.expected_prior_authority_pin)
    prior = None
    safe_new_dir(args.output_dir)
    common = dict(pins=pins, prior_pins=prior_pins, build=build)
    if op == 't1-simulation-run':
        prior = checked_cli.read_bundle_dir(args.prior_bundle)
        t1_simulation.acquire(objects=_objects(args.objects_dir), prior_files=prior,
                              output=args.output_dir, **common)
    else:
        producer = t1_workflow.read_package(args.producer_package, target='/M')
        if 'manifest.json' not in producer:
            refuse('SIM_REFERENCE_MISSING', 1, '/M')
        closure = inspect_package(producer['manifest.json'], producer, manifest_pin=args.expected_producer_manifest_pin)
        handoff = None
        prepared_objects = None
        request = None
        if op == 't1-reassessment-prepare':
            from .t1_records import locate_roots
            prepared_objects = _objects(args.objects_dir)
            roots = locate_roots(prepared_objects, ('ct.request.v1',))
            if len(roots['ct.request.v1']) != 1:
                refuse('SIM_REFERENCE_INVALID', 1, '/R')
            request = prepared_objects.pop(roots['ct.request.v1'][0])
            t1_workflow._intake_request(request, prepared_objects, producer,
                args.expected_producer_manifest_pin, pins, build)
        elif op in ('t1-reassessment-evaluate', 't1-workflow-verify'):
            handoff = t1_workflow.read_package(args.handoff_package, target='/H')
            t1_workflow._intake_handoff(handoff, args.expected_handoff_pin, args.expected_request_pin,
                producer, args.expected_producer_manifest_pin, pins, build)
            if op == 't1-workflow-verify':
                if json.loads(workflow_wire)['evaluation_authority']['sha256'] != args.expected_authority_pin:
                    refuse('SIM_PIN_MISMATCH', 1, '/A')
                t1_workflow._intake_authority(checked_cli.read_bundle_dir(args.bundle), args.expected_authority_pin)
        prior = checked_cli.read_bundle_dir(args.prior_bundle)
        if closure.prior_files != prior:
            refuse('SIM_PRIOR_MISMATCH', 2, '/prior')
        if op == 't1-simulation-verify':
            verified = t1_simulation.verify(files=producer, manifest_pin=args.expected_producer_manifest_pin,
                                           workspace=args.scratch_dir, **common)
            report = t1_workflow.verification_report(verified, operation=op, subject_wire=producer['manifest.json'],
                                                    scratch=args.scratch_dir, build=build)
            Publication(args.output_dir, final='report.json', target='/report').finish(report)
        elif op == 't1-reassessment-prepare':
            t1_workflow.prepare_handoff(producer_files=producer, manifest_pin=args.expected_producer_manifest_pin,
                scratch=args.scratch_dir, output=args.output_dir, request_wire=request, request_objects=prepared_objects, **common)
        elif op == 't1-reassessment-evaluate':
            t1_workflow.evaluate(producer_files=producer, manifest_pin=args.expected_producer_manifest_pin,
                scratch=args.scratch_dir, output=args.output_dir, handoff_files=handoff,
                handoff_pin=args.expected_handoff_pin, request_pin=args.expected_request_pin,
                authority_pin=args.expected_authority_pin, authority_objects=_objects(args.objects_dir), **common)
        elif op == 't1-workflow-verify':
            workflow_root = Path(args.bundle).parent
            entries = workflow_entries
            if set(entries) != {'workflow-receipt.json'} | {'bundle/' + n for n in checked_cli.runtime.BUNDLE_NAMES}:
                refuse('SIM_REFERENCE_INVALID', 1, '/F/package')
            f = entries['workflow-receipt.json']
            verified = t1_workflow.verify_workflow(workflow_wire=f, workflow_pin=args.expected_workflow_receipt_pin,
                bundle_files=checked_cli.read_bundle_dir(args.bundle), producer_files=producer,
                manifest_pin=args.expected_producer_manifest_pin, handoff_files=handoff,
                handoff_pin=args.expected_handoff_pin, request_pin=args.expected_request_pin,
                authority_pin=args.expected_authority_pin, scratch=args.scratch_dir, **common)
            report = t1_workflow.verification_report(verified, operation=op, subject_wire=f,
                                                    scratch=args.scratch_dir, build=build)
            Publication(args.output_dir, final='report.json', target='/report').finish(report)
        else:
            refuse('SIM_USAGE', 0, '/argv', 2)
    published = t1_workflow.read_package(args.output_dir)
    value = dict(schema='ct.t1-completion-record.v1', profile=PROFILE, command=op,
        published=[dict(role=('producer_manifest' if p == 'manifest.json' else 'handoff' if p == 'handoff.json'
            else 'workflow_receipt' if p == 'workflow-receipt.json' else 'verification_report' if p == 'report.json' else 'member'),
                       path=p, sha256=sha(w)) for p, w in sorted(published.items())],
        guarantee='simulation-verified' if op == 't1-simulation-verify' else 'producer-checked' if op in
            ('t1-reassessment-evaluate', 't1-workflow-verify') else None,
        limitations=next(branch['properties']['limitations']['const'] for branch in
            SCHEMAS['records']['ct.t1-completion-record.v1']['oneOf']
            if op in branch['properties']['command']['enum']))
    from .t1_schemas import validate
    validate(value, value['schema'], '/completion')
    return value


def main(argv=None):
    from .checked_cli import _emit
    try:
        args = arguments(sys.argv[1:] if argv is None else argv)
        result = execute(args, build=ExecutableBuild())
        wire = canonical_bytes(result) + b'\n'
        if len(wire) > 65536: refuse('SIM_RESOURCE_LIMIT', 7, '/completion', 4)
        _emit(1, wire)
        return 0
    except SimRefusal as e:
        record, status = e.record(), e.exit_class
    except CheckedRefusal as e:
        record, status = dict(schema='ct.diagnostic.v1', code=e.code, stage=e.stage, target=e.target[:256], exit_class=e.exit_class), e.exit_class
    except Exception:
        record, status = dict(schema='ct.t1-diagnostic.v1', code='SIM_INTERNAL_ERROR', order='0', target='/application', exit_class=7), 7
    try:
        _emit(2, canonical_bytes(record) + b'\n')
    except OSError:
        return 7
    return status
