"""Checked-temperature command line: six commands, trusted external pins.

Pins are entry-point arguments, never read from a bundle. The maintained
executable build identity is always used here; there is no build override.
"""
import argparse
import json
import os
from pathlib import Path
import re
import sys

from .checked_contracts import (EDITION_LIMITS, EXIT_FILESYSTEM, EXIT_OUTPUT, EXIT_RETENTION, EXIT_USAGE,
                                CheckedRefusal, canonical_bytes, refuse)
from . import checked_runtime as runtime

COMMANDS = tuple('checked-%s-%s' % (k, m) for k in ('selection', 'reassessment')
                 for m in ('evaluate', 'verify', 'replay'))
HEX = re.compile(r'[0-9a-f]{64}\Z')


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        refuse('CLI_USAGE', 0, '/arguments', exit_class=EXIT_USAGE)


def arguments(argv):
    p = _Parser(add_help=False, allow_abbrev=False)
    sub = p.add_subparsers(dest='operation', required=True, parser_class=_Parser)
    for command in COMMANDS:
        c = sub.add_parser(command, add_help=False, allow_abbrev=False)
        c.add_argument('--expected-request-pin', required=True)
        c.add_argument('--expected-authority-pin', required=True)
        if command.endswith('evaluate'):
            c.add_argument('--request', required=True)
            c.add_argument('--objects-dir', required=True)
            if command.startswith('checked-reassessment'):
                c.add_argument('--prior-bundle', required=True)
            c.add_argument('--cached-derivation', required=False)   # CONTRACT §12.8 comparison artifact
        else:
            c.add_argument('--bundle', required=True)
        if not command.endswith('verify'):
            c.add_argument('--output-dir', required=True)
    flags = [a.split('=', 1)[0] for a in argv if a.startswith('--')]
    if len(flags) != len(set(flags)):
        refuse('CLI_USAGE', 0, '/arguments', exit_class=EXIT_USAGE)
    args = p.parse_args(argv)
    for pin in (args.expected_request_pin, args.expected_authority_pin):
        if not HEX.match(pin):
            refuse('CLI_USAGE', 0, '/pins', exit_class=EXIT_USAGE)
    return args


def _read(path, cap, target):
    try:
        with open(path, 'rb') as stream:
            data = stream.read(cap + 1)
    except OSError:
        refuse('REFERENCE_MISSING', 1, target, exit_class=EXIT_FILESYSTEM)
    if len(data) > cap:
        refuse('RESOURCE_LIMIT_EXCEEDED', 1, target)
    return data


def read_objects(directory):
    objects = {}
    try:
        names = sorted(os.listdir(directory))
    except OSError:
        refuse('REFERENCE_MISSING', 1, '/objects-dir', exit_class=EXIT_FILESYSTEM)
    if len(names) > EDITION_LIMITS['reassessment_unique_objects']:   # review I8: cap before reading
        refuse('RESOURCE_LIMIT_EXCEEDED', 1, '/objects-dir')
    total = 0
    for name in names:
        if not HEX.match(name) or not os.path.isfile(os.path.join(directory, name)):
            refuse('SCHEMA_INVALID', 1, '/objects-dir/' + name)
        objects[name] = _read(os.path.join(directory, name), EDITION_LIMITS['object_bytes'], '/objects/' + name)
        total += len(objects[name])
        if total > EDITION_LIMITS['reassessment_closure_decoded_bytes']:
            refuse('RESOURCE_LIMIT_EXCEEDED', 1, '/objects-dir')
    return objects


def read_bundle_dir(directory, *, cap=EDITION_LIMITS['bundle_bytes_reassessment']):
    files = {}
    try:
        names = sorted(os.listdir(directory))
    except OSError:
        refuse('REFERENCE_MISSING', 1, '/bundle', exit_class=EXIT_FILESYSTEM)
    if len(names) != len(runtime.BUNDLE_NAMES):   # review I8: exactly nine files, checked before reading
        refuse('REFERENCE_MISSING', 3, '/bundle')
    for name in names:
        files[name] = _read(os.path.join(directory, name), cap, '/bundle/' + name)
    return files


def filesystem_of(path):
    """ext4 or xfs from /proc/mounts (longest mount prefix), else unknown."""
    try:
        target = str(Path(path).resolve())
        best, kind = '', 'unknown'
        with open('/proc/mounts') as mounts:
            for line in mounts:
                parts = line.split()
                if len(parts) > 2 and (target == parts[1] or target.startswith(parts[1].rstrip('/') + '/')) \
                        and len(parts[1]) > len(best):
                    best, kind = parts[1], parts[2]
        return kind if kind in ('ext4', 'xfs') else 'unknown'
    except OSError:
        return 'unknown'


def publish(output_dir, files):
    """Create NEW, write the eight records, then the manifest last."""
    path = Path(output_dir)
    if path.exists():
        refuse('OUTPUT_COLLISION', 6, '/output-dir', exit_class=EXIT_RETENTION)
    try:
        path.mkdir(parents=False)
    except OSError:
        refuse('OUTPUT_COLLISION', 6, '/output-dir', exit_class=EXIT_RETENTION)   # CONTRACT §12.2: exit 6
    order = [n for n, _ in runtime.FILE_ROLES] + ['manifest.json']
    try:
        for name in order:
            fd = os.open(path / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            try:
                view = memoryview(files[name])
                while view:
                    view = view[os.write(fd, view):]
                os.fsync(fd)
            finally:
                os.close(fd)
        dfd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except OSError:
        refuse('OUTPUT_COLLISION', 6, '/output-dir', exit_class=EXIT_RETENTION)
    return runtime.sha(files['manifest.json'])


def execute(args, *, build):
    op = args.operation
    pins = dict(request_pin=args.expected_request_pin, authority_pin=args.expected_authority_pin)
    if op.endswith('evaluate'):
        parent = Path(args.output_dir).parent
        fs = filesystem_of(parent)
        request = _read(args.request, EDITION_LIMITS['object_bytes'], '/request')
        objects = read_objects(args.objects_dir)
        cached = None if args.cached_derivation is None else \
            _read(args.cached_derivation, EDITION_LIMITS['derivation_bytes'], '/cached-derivation')
        if op == 'checked-selection-evaluate':
            files = runtime.evaluate_selection(request_wire=request, objects=objects, build=build,
                                               filesystem=fs, cached_derivation=cached, **pins)
        else:
            prior = read_bundle_dir(args.prior_bundle, cap=EDITION_LIMITS['bundle_bytes_selection'])
            files = runtime.evaluate_reassessment(request_wire=request, objects=objects, prior_files=prior,
                                                  build=build, filesystem=fs, cached_derivation=cached, **pins)
        return {'operation': op, 'bundle_commitment': publish(args.output_dir, files)}
    bundle = read_bundle_dir(args.bundle)
    if op.endswith('verify'):
        report = runtime.verify(bundle_files=bundle, build=build, **pins)
        if report['operation'] != op:
            refuse('SCHEMA_INVALID', 2, '/bundle/manifest/bundle_kind')
        return report
    fs = filesystem_of(Path(args.output_dir).parent)
    files = runtime.replay(bundle_files=bundle, build=build, filesystem=fs, **pins)
    kind = json.loads(files['manifest.json'])['bundle_kind']
    if op != 'checked-%s-replay' % kind:
        refuse('SCHEMA_INVALID', 2, '/bundle/manifest/bundle_kind')
    return {'operation': op, 'bundle_commitment': publish(args.output_dir, files)}


def _emit(fd, wire):
    view = memoryview(wire)
    while view:
        n = os.write(fd, view)
        if n <= 0:
            raise OSError('output unavailable')
        view = view[n:]


def main(argv=None):
    """Process entry point: always the maintained executable build identity."""
    build = runtime.ExecutableBuild()
    try:
        args = arguments(sys.argv[1:] if argv is None else argv)
        answer = execute(args, build=build)
        wire = canonical_bytes(answer) + b'\n'
        if len(wire) > EDITION_LIMITS['receipt_bytes']:
            refuse('RESOURCE_LIMIT_EXCEEDED', 7, '/receipt', exit_class=EXIT_OUTPUT)
        try:
            _emit(1, wire)
        except OSError:
            return EXIT_OUTPUT
        return 0
    except CheckedRefusal as e:
        code, stage, target, status = e.code, e.stage, e.target, e.exit_class
    except Exception:
        code, stage, target, status = 'INTERNAL_ERROR', 0, '/application', EXIT_OUTPUT
    diagnostic = {'schema': 'ct.diagnostic.v1', 'code': code, 'stage': stage, 'target': target[:256],
                  'exit_class': status}
    try:
        _emit(2, canonical_bytes(diagnostic)[:EDITION_LIMITS['diagnostic_bytes'] - 1] + b'\n')
    except OSError:
        return EXIT_OUTPUT
    return status
