#!/usr/bin/env python3
"""Bounded synthetic-fixture rebinding for the maintained T1 workflow (t1-rebind.v1).

Renders candidate synthetic input records bound to one new ct.build.v1 digest,
as specified by
docs/superpowers/reports/2026-10-22-t1-rebind-implementation-specification.md
(SHA-256 42d92411d35a3d7764930ac8867329e643e3442d95dba07f2789316b03a4ff61).

Standard library only. The tool never imports or invokes the application or
backend, never approves anything or issues runtime authority, never supplies
or inherits attestation text, never edits simulator output and never
overwrites an earlier stage. Every change is one (record role, JSON pointer,
dependency role) rule whose old value is checked before replacement; there is
no global string or prefix replacement.

A rendered candidate is not owner approval. A successful run authorizes no
application execution.

    python3 -I -B tools/fixtures/t1_rebind.py <stage1|stage2|stage3> --flag value ...
"""
import copy
import hashlib
import json
import os
import re
import stat
import sys

TOOL_EDITION = 't1-rebind.v1'
PINS_SCHEMA = 't1-rebind-source-pins.v1'
ATTESTATIONS_SCHEMA = 't1-rebind-attestations.v1'
REVIEW_SCHEMA = 't1-rebind-review.v1'
PACKET_SCHEMA = 't1-rebind-approval-packet.v1'
APPROVAL_SCHEMA = 't1-rebind-owner-approval.v1'
REVIEW_PATH = 'REBIND-REVIEW.json'
PACKET_PATH = 'packet/APPROVAL-PACKET.json'
PARTIAL = 'PARTIAL'
STATEMENT = ('Candidate rendering only. Not owner approval. No application execution is authorized by '
             'this record.')
NOT_AUTHORIZED = 'NOT AUTHORIZED BY THIS PACKET'
TIMES_NOTE = ('declared synthetic instants checked against declared request and acquisition times, not the '
              'wall clock and not the approval date')
SCOPE_NOTE = 'unauthenticated synthetic development premise; no physical, operational or adoption authority'
HEX64 = re.compile('[0-9a-f]{64}\\Z')
REL_PATH = re.compile('[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*\\Z')
ZERO = '0' * 64
T1 = 'ct.procedure.T1.v1'
OPAQUE = 'ct.evidence-content'
HISTORICAL_TEXT = {'label': 'gate1 test fixture', 'basis': 'synthetic Gate 1 unit-test fixture'}

EXIT = {'REBIND_USAGE': 2, 'REBIND_INPUT_MISSING': 3, 'REBIND_INPUT_INVALID': 3, 'REBIND_PIN_MISMATCH': 3,
        'REBIND_DEPENDENCY_MISMATCH': 3, 'REBIND_UNMODELLED_DEPENDENCY': 3, 'REBIND_ATTESTATION_INVALID': 3,
        'REBIND_RESOURCE_LIMIT': 4, 'REBIND_OUTPUT_UNSAFE': 5, 'REBIND_PARTIAL': 5, 'REBIND_INTERNAL': 7}

ROLES = ('policy', 'P', 'A0', 'simulator_policy', 'X', 'E', 'J', 'G', 'evidence', 'R')
RENDERED = ('policy', 'P', 'A0', 'simulator_policy', 'X', 'E', 'J', 'G', 'R')
KIND = {'policy': 'ct.policy.v1', 'P': 'ct.request.v1', 'A0': 'ct.authority.v1',
        'simulator_policy': 'ct.t1-simulator-policy.v1', 'X': 'ct.execution-target.v1',
        'E': 'ct.authority.v1', 'J': 'ct.t1-simulation-target.v1', 'G': 'ct.t1-simulation-permission.v1',
        'evidence': 'nm.evidence.v1', 'R': 'ct.request.v1', 'B': 'ct.build.v1',
        'B0.manifest': 'ct.bundle-manifest.v1', 'B0.result': 'ct.selection.v1'}
# x-allowed-roles of checked_temperature_schemas.json / t1_companion_schemas.json, copied as data.
ALLOWED_ROLES = {'ct.policy.v1': ('local_policy_owner',), 'ct.request.v1': ('local_model_proposer',),
                 'ct.authority.v1': ('local_evaluation_issuer', 'local_execution_issuer'),
                 'ct.t1-simulator-policy.v1': ('local_policy_owner',),
                 'ct.execution-target.v1': ('local_model_proposer',),
                 'ct.t1-simulation-target.v1': ('local_model_proposer',),
                 'ct.t1-simulation-permission.v1': ('local_execution_issuer',)}
LIST_B = 'LIST_B'
RULES = {
    'policy': (('/permitted_builds', LIST_B),),
    'P': (('/policy', 'policy'),),
    'A0': (('/target', 'P'),),
    'simulator_policy': (('/permitted_producer_builds', LIST_B), ('/permitted_checker_builds', LIST_B)),
    'X': (('/prior_selection/manifest', 'B0.manifest'), ('/prior_selection/selection', 'B0.result')),
    'E': (('/target', 'X'),),
    'J': (('/captured_policy', 'policy'), ('/producer_build', 'B'), ('/simulator_policy', 'simulator_policy'),
          ('/execution_target', 'X')),
    'G': (('/execution_authority', 'E'), ('/scope/captured_policy', 'policy'), ('/scope/producer_build', 'B'),
          ('/scope/simulator_policy', 'simulator_policy'), ('/target', 'J')),
    'R': (('/policy', 'policy'), ('/prior_selection/manifest', 'B0.manifest'),
          ('/prior_selection/selection', 'B0.result'), ('/execution_target', 'X'),
          ('/result/execution_authority', 'E'), ('/result/acquisition/public_evidence', 'evidence'))}
STAGE_ROLES = {'stage1': ('policy', 'P', 'A0'), 'stage2': ('simulator_policy', 'X', 'E', 'J', 'G'),
               'stage3': ('R',)}
APPROVAL_POINT = {'stage1': 'AP-S1', 'stage2': 'AP-S2', 'stage3': 'AP-S3'}
APPROVAL_IDS = {'policy': 'AP-S1-a', 'P': 'AP-S1-b', 'A0': 'AP-S1-c', 'simulator_policy': 'AP-S2-a',
                'X': 'AP-S2-b', 'E': 'AP-S2-c', 'J': 'AP-S2-d', 'G': 'AP-S2-e', 'R': 'AP-S3-a'}
APPROVAL_SUBJECT = {
    'policy': 'policy owner: the supplied build digest as the sole permitted build, and the policy text',
    'P': 'model proposer: the selection request bound to the rendered policy',
    'A0': 'evaluation issuer: selection evaluation of the rendered request within its declared window',
    'simulator_policy': 'policy owner: the supplied build digest as sole producer and checker build',
    'X': 'model proposer: the execution target inheriting the generated selection bundle',
    'E': 'execution issuer: T1 execution of the rendered execution target within its declared window',
    'J': 'model proposer: the synthetic simulation target and window',
    'G': 'execution issuer: simulation only within its declared window; every other grant stays false',
    'R': "model proposer: the reassessment request citing the producer package's actual evidence and scalar"}
AUTHORIZES = {'stage1': 'Use of these exact bytes as inputs to EX-1 checked-selection-evaluate',
              'stage2': 'Use of these exact bytes as inputs to EX-2 t1-simulation-run',
              'stage3': 'Use of these exact bytes as input to EX-3 t1-reassessment-prepare'}
EXCLUDES = {'stage1': ['any other build', 'any wall-clock authority', 'adoption', 'physical acquisition'],
            'stage2': ['physical acquisition', 'evaluation', 'adoption'],
            'stage3': ['evaluation', 'any claim beyond the synthetic result']}
NEXT_GRANT = {'stage1': 'EX-1', 'stage2': 'EX-2', 'stage3': 'EX-3'}
# Fixed source layout: directory key -> (relative path, role objects that join the unchanged set).
LAYOUT = {'selection_objects': ('selection/objects', ('policy', 'A0')),
          'simulation_input': ('positive/simulation-input', ('simulator_policy', 'X', 'E', 'J', 'G')),
          'request_input': ('positive/request-input', ('policy', 'X', 'E', 'R', 'evidence'))}
REQUEST_PATH = 'selection/request.json'
# checked_runtime.FILE_ROLES order, then the manifest (BUNDLE_NAMES).
BUNDLE_ROLES = (('invocation.json', 'ct.invocation.v1'), ('closure.json', 'ct.closure.v1'),
                ('derivation.json', 'ct.derivation.v1'), ('applicability.json', 'ct.applicability.v1'),
                ('result.json', 'ct.selection.v1'), ('trace.json', 'ct.trace.v1'),
                ('build.json', 'ct.build.v1'), ('policy.json', 'ct.policy.v1'))
BUNDLE_NAMES = tuple(name for name, _ in BUNDLE_ROLES) + ('manifest.json',)
BUNDLE_CAPS = {'closure.json': 1474560, 'build.json': 65536, 'policy.json': 16384, 'manifest.json': 16384,
               'invocation.json': 16384}
PRODUCER_FILES = (('manifest.json', 32768), ('receipt/receipt.json', 65536),
                  ('evidence/public/evidence.json', 196608))
CAPS = {'object': 196608, 'source_total': 4 * 1048576, 'bundle_default': 196608, 'bundle_total': 2097152,
        'pins': 65536, 'attestations': 32768, 'tool': 262144, 'review': 1048576, 'stage_total': 2 * 1048576,
        'producer_total': 294912}
OUTPUT_CAPS = {'stage1': (40, 2 * 1048576), 'stage2': (16, 1048576), 'stage3': (32, 1572864)}
# Rendered-record byte caps the application enforces (t1_contracts.CAPS; checked EDITION_LIMITS
# policy_bytes / object_bytes), copied as data so a candidate cannot pass here and fail admission.
RECORD_CAPS = {'ct.t1-simulation-permission.v1': 4096, 'ct.t1-simulation-target.v1': 16384,
               'ct.policy.v1': 16384}
PARSE_DEPTH, PARSE_NODES, PARSE_STRING = 24, 65536, 4096
COMMON_FLAGS = ('source-dir', 'source-pins', 'expected-source-pins-sha256', 'attestations',
                'expected-attestations-sha256', 'out')
FLAGS = {'stage1': COMMON_FLAGS + ('build-digest',),
         'stage2': COMMON_FLAGS + ('stage1-dir', 'expected-stage1-review-sha256', 'prior-bundle',
                                   'expected-prior-manifest-sha256'),
         'stage3': COMMON_FLAGS + ('stage1-dir', 'expected-stage1-review-sha256', 'stage2-dir',
                                   'expected-stage2-review-sha256', 'producer-package',
                                   'expected-producer-manifest-sha256')}
HEX_FLAGS = ('build-digest', 'expected-source-pins-sha256', 'expected-attestations-sha256',
             'expected-stage1-review-sha256', 'expected-stage2-review-sha256', 'expected-prior-manifest-sha256',
             'expected-producer-manifest-sha256')


class Refusal(Exception):
    """A stable refusal: code and a target that never holds an absolute path."""

    def __init__(self, code, target='/'):
        super().__init__(code)
        self.code, self.target = code, target


def refuse(code, target='/'):
    raise Refusal(code, target)


# ------------------------------------------------------------------ bytes

def canon(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def pretty(value):
    return (json.dumps(value, indent=1, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(kind, digest):
    return {'kind': kind, 'sha256': digest}


def is_hex(value):
    return isinstance(value, str) and HEX64.fullmatch(value) is not None


def parse_strict(wire, target, *, form='canonical', invalid='REBIND_INPUT_INVALID'):
    """Strict JSON under the t1_records.parse limits.

    Duplicate keys, NaN/Infinity, depth over 24, more than 65,536 nodes and
    strings over 4,096 UTF-8 bytes are refused. Finite floats are accepted,
    as the application accepts them; `form` requires canonical or pretty
    re-serialization to reproduce the bytes exactly.
    """
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                refuse(invalid, target)
            value[key] = item
        return value

    def constant(_):
        refuse(invalid, target)

    try:
        value = json.loads(wire.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant)
    except RecursionError:
        refuse('REBIND_RESOURCE_LIMIT', target)
    except (UnicodeError, ValueError):
        refuse(invalid, target)
    stack, nodes = [(value, 1)], 0
    while stack:
        item, depth = stack.pop()
        nodes += 1
        if depth > PARSE_DEPTH or nodes > PARSE_NODES:
            refuse('REBIND_RESOURCE_LIMIT', target)
        if isinstance(item, dict):
            stack.extend((x, depth + 1) for pair in item.items() for x in pair)
        elif isinstance(item, list):
            stack.extend((x, depth + 1) for x in item)
        elif isinstance(item, str) and len(item.encode('utf-8', 'surrogatepass')) > PARSE_STRING:
            refuse('REBIND_RESOURCE_LIMIT', target)
    try:
        again = pretty(value) if form == 'pretty' else canon(value)
    except (ValueError, UnicodeError):
        refuse(invalid, target)
    if form in ('canonical', 'pretty') and again != wire:
        refuse(invalid, target)
    return value


def escape(key):
    return key.replace('~', '~0').replace('/', '~1')


def walk_strings(value):
    """(pointer, text, is_key) for every key and string leaf, in sorted order."""
    out = []
    stack = [(value, '')]
    while stack:
        item, pointer = stack.pop()
        if isinstance(item, dict):
            children = []
            for key in sorted(item):
                child = pointer + '/' + escape(key)
                out.append((child, key, True))
                children.append((item[key], child))
            stack.extend(reversed(children))
        elif isinstance(item, list):
            stack.extend(reversed([(x, pointer + '/' + str(i)) for i, x in enumerate(item)]))
        elif isinstance(item, str):
            out.append((pointer, item, False))
    return out


def has_float(value):
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, float):
            return True
        if isinstance(item, dict):
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    return False


def typed_refs(value):
    """Every {kind, sha256} typed reference inside a parsed record."""
    found, stack = [], [value]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            if set(item) == {'kind', 'sha256'} and isinstance(item['kind'], str) and is_hex(item['sha256']):
                found.append(item)
            else:
                stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    return found


def dig(value, *keys):
    """Nested object member or None; never raises on a missing or non-object step."""
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def locate(value, pointer, target):
    """Parent container and key of a rule pointer (object members only)."""
    parts = pointer.split('/')[1:]
    node = value
    for part in parts[:-1]:
        if not isinstance(node, dict) or part not in node:
            refuse('REBIND_INPUT_INVALID', target + pointer)
        node = node[part]
    if not isinstance(node, dict) or parts[-1] not in node:
        refuse('REBIND_INPUT_INVALID', target + pointer)
    return node, parts[-1]


def leaf_diff(a, b, pointer=''):
    """Pointers whose leaves differ; structural differences are reported at their container."""
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            return [pointer + '#keys']
        return [p for key in sorted(a) for p in leaf_diff(a[key], b[key], pointer + '/' + escape(key))]
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [pointer + '#length']
        return [p for i, (x, y) in enumerate(zip(a, b)) for p in leaf_diff(x, y, pointer + '/' + str(i))]
    if type(a) is not type(b) or a != b:
        return [pointer]
    return []


# ------------------------------------------------------------ bounded reads

class Budget:
    def __init__(self, limit, target):
        self.limit, self.used, self.target = limit, 0, target

    def take(self, count):
        self.used += count
        if self.used > self.limit:
            refuse('REBIND_RESOURCE_LIMIT', self.target)


def read_capped(path, cap, target):
    """O_RDONLY|O_NOFOLLOW regular file, at most cap bytes (cap + 1 are read to detect excess)."""
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_CLOEXEC', 0)
    try:
        fd = os.open(path, flags)
    except FileNotFoundError:
        refuse('REBIND_INPUT_MISSING', target)
    except OSError:
        refuse('REBIND_INPUT_INVALID', target)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            refuse('REBIND_INPUT_INVALID', target)
        chunks, size = [], 0
        while size <= cap:
            chunk = os.read(fd, min(1048576, cap + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
        if size > cap:
            refuse('REBIND_RESOURCE_LIMIT', target)
        return b''.join(chunks)
    except OSError:
        refuse('REBIND_INPUT_INVALID', target)
    finally:
        os.close(fd)


def real_dir(path, target):
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        refuse('REBIND_INPUT_MISSING', target)
    except OSError:
        refuse('REBIND_INPUT_INVALID', target)
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        refuse('REBIND_INPUT_INVALID', target)


def scan_entries(path, limit, target):
    """At most limit + 1 directory entries; more than limit refuses."""
    real_dir(path, target)
    entries = []
    try:
        with os.scandir(path) as listing:
            for entry in listing:
                entries.append((entry.name, entry.is_symlink(), entry.is_file(follow_symlinks=False),
                                entry.is_dir(follow_symlinks=False)))
                if len(entries) > limit:
                    refuse('REBIND_RESOURCE_LIMIT', target)
    except OSError:
        refuse('REBIND_INPUT_INVALID', target)
    return sorted(entries)


def read_named_dir(path, names, caps, budget, target):
    """Exactly the named regular files (count first, then names), each capped."""
    entries = scan_entries(path, len(names), target)
    for name, link, regular, _ in entries:
        if link or not regular:
            refuse('REBIND_INPUT_INVALID', target + '/' + name)
    found = {name for name, _, _, _ in entries}
    if found != set(names):
        refuse('REBIND_INPUT_MISSING' if found < set(names) else 'REBIND_INPUT_INVALID', target)
    files = {}
    for name in sorted(names):
        files[name] = read_capped(os.path.join(path, name), caps(name), target + '/' + name)
        budget.take(len(files[name]))
    return files


def read_hex_dir(path, expected, cap, budget, target):
    """Exactly the expected 64-hex names, each regular, each named by the SHA-256 of its bytes."""
    for name in expected:
        if not is_hex(name):
            refuse('REBIND_INTERNAL', target)
    entries = scan_entries(path, len(expected), target)
    for name, link, regular, _ in entries:
        if link or not regular or not is_hex(name):
            refuse('REBIND_INPUT_INVALID', target + '/' + name)
    files = read_named_dir(path, sorted(expected), lambda _: cap, budget, target)
    for name, wire in files.items():
        if sha(wire) != name:
            refuse('REBIND_INPUT_INVALID', target + '/' + name)
    return files


# --------------------------------------------------------- owner-supplied data

def validate_pins(pins, target='/source-pins'):
    """Shape of t1-rebind-source-pins.v1; returns the layout membership it implies."""
    bad = lambda where='': refuse('REBIND_INPUT_INVALID', target + where)
    required = {'schema', 'historical_build', 'roles', 'unchanged', 'prior_bundle'}
    if not isinstance(pins, dict) or not required <= set(pins) <= required | {'label'}:
        bad()
    if pins['schema'] != PINS_SCHEMA:
        bad('/schema')
    if 'label' in pins and not (isinstance(pins['label'], str) and 1 <= len(pins['label']) <= 256):
        bad('/label')
    build = pins['historical_build']
    if not is_hex(build) or build == ZERO:
        bad('/historical_build')
    roles = pins['roles']
    if not isinstance(roles, dict) or set(roles) != set(ROLES) or not all(is_hex(v) for v in roles.values()):
        bad('/roles')
    if len(set(roles.values())) != len(ROLES) or build in roles.values():
        bad('/roles')
    unchanged = pins['unchanged']
    if not isinstance(unchanged, dict) or set(unchanged) != set(LAYOUT):
        bad('/unchanged')
    for key, names in unchanged.items():
        if not isinstance(names, list) or not all(is_hex(n) for n in names) or names != sorted(set(names)):
            bad('/unchanged/' + key)
        if set(names) & (set(roles.values()) | {build}):
            bad('/unchanged/' + key)
    prior = pins['prior_bundle']
    if not isinstance(prior, dict) or set(prior) != set(BUNDLE_NAMES) or not all(is_hex(v) for v in prior.values()):
        bad('/prior_bundle')
    if prior['policy.json'] != roles['policy'] or prior['build.json'] != build:
        bad('/prior_bundle')
    others = [prior[n] for n in BUNDLE_NAMES if n not in ('policy.json', 'build.json')]
    every_unchanged = {n for names in unchanged.values() for n in names}
    if len(set(others)) != len(others) or set(others) & (set(roles.values()) | {build} | every_unchanged):
        bad('/prior_bundle')
    return {key: sorted(set(unchanged[key]) | {roles[r] for r in extra}) for key, (_, extra) in LAYOUT.items()}


def load_attestations(path, expected, stage):
    wire = read_capped(path, CAPS['attestations'], '/attestations')
    if sha(wire) != expected:
        refuse('REBIND_PIN_MISMATCH', '/attestations')
    value = parse_strict(wire, '/attestations', form='any', invalid='REBIND_ATTESTATION_INVALID')
    bad = lambda where='': refuse('REBIND_ATTESTATION_INVALID', '/attestations' + where)
    if not isinstance(value, dict) or set(value) != {'schema', 'stage', 'records'}:
        bad()
    if value['schema'] != ATTESTATIONS_SCHEMA or value['stage'] != stage:
        bad('/stage' if value['schema'] == ATTESTATIONS_SCHEMA else '/schema')
    records = value['records']
    if not isinstance(records, dict) or set(records) != set(STAGE_ROLES[stage]):
        bad('/records')
    for role, text in sorted(records.items()):
        if not isinstance(text, dict) or set(text) != {'label', 'basis'}:
            bad('/records/' + role)
        for field, low, high in (('label', 1, 128), ('basis', 0, 1024)):
            item = text[field]
            if not isinstance(item, str) or not low <= len(item) <= high or \
                    any(ord(ch) < 0x20 for ch in item):
                bad('/records/' + role + '/' + field)
            try:
                item.encode('utf-8')
            except UnicodeError:
                bad('/records/' + role + '/' + field)
    return records, wire


# ------------------------------------------------------------------ source

class Source:
    """The verified source fixture: pins, inventory, parsed values, topology."""

    def __init__(self, directory, pins_path, expected_pins):
        wire = read_capped(pins_path, CAPS['pins'], '/source-pins')
        if sha(wire) != expected_pins:
            refuse('REBIND_PIN_MISMATCH', '/source-pins')
        self.pins_wire = wire
        self.pins = parse_strict(wire, '/source-pins', form='any')
        self.membership = validate_pins(self.pins)
        # Refuse early a source whose pinned inventory would exceed a stage's fixed output file cap
        # (each stage adds its packet and review; stage 1 also its request file).
        for stage, key, extra in (('stage1', 'selection_objects', 3), ('stage2', 'simulation_input', 2),
                                  ('stage3', 'request_input', 2)):
            if len(self.membership[key]) + extra > OUTPUT_CAPS[stage][0]:
                refuse('REBIND_INPUT_INVALID', '/source-pins/unchanged/' + key)
        self.roles = dict(self.pins['roles'])
        self.historical_build = self.pins['historical_build']
        self.old = dict(self.roles, B=self.historical_build, **{
            'B0.manifest': self.pins['prior_bundle']['manifest.json'],
            'B0.result': self.pins['prior_bundle']['result.json']})
        real_dir(directory, '/source')
        for part in ('selection', 'positive'):
            real_dir(os.path.join(directory, part), '/source/' + part)
        budget = Budget(CAPS['source_total'], '/source')
        self.request = read_capped(os.path.join(directory, *REQUEST_PATH.split('/')), CAPS['object'],
                                   '/source/' + REQUEST_PATH)
        budget.take(len(self.request))
        if sha(self.request) != self.roles['P']:
            refuse('REBIND_INPUT_INVALID', '/source/' + REQUEST_PATH)
        self.dirs = {}
        for key, (relative, _) in LAYOUT.items():
            self.dirs[key] = read_hex_dir(os.path.join(directory, *relative.split('/')), self.membership[key],
                                          CAPS['object'], budget, '/source/' + relative)
        self.prior = read_named_dir(os.path.join(directory, 'prior'), BUNDLE_NAMES,
                                    lambda n: BUNDLE_CAPS.get(n, CAPS['bundle_default']),
                                    Budget(CAPS['bundle_total'], '/source/prior'), '/source/prior')
        for name, data in self.prior.items():
            if sha(data) != self.pins['prior_bundle'][name]:
                refuse('REBIND_INPUT_INVALID', '/source/prior/' + name)
        self.objects = {self.roles['P']: self.request}
        for files in self.dirs.values():
            self.objects.update(files)
        self._parse()
        self.role_values = {role: self.values[self.roles[role]] for role in ROLES}
        check_topology(self)
        check_completeness(self)

    def _parse(self):
        """Opaque objects are those referenced as ct.evidence-content; they are only hashed."""
        self.values, self.opaque = {}, set()
        pending = [self.roles[r] for r in ROLES]
        while pending:
            digest = pending.pop(0)
            if digest in self.values or digest in self.opaque or digest not in self.objects:
                continue
            value = parse_strict(self.objects[digest], '/source/objects/' + digest)
            if not isinstance(value, dict):
                refuse('REBIND_INPUT_INVALID', '/source/objects/' + digest)
            self.values[digest] = value
            for item in typed_refs(value):
                if item['kind'] == OPAQUE:
                    if item['sha256'] in self.values:
                        refuse('REBIND_INPUT_INVALID', '/source/objects/' + item['sha256'])
                    self.opaque.add(item['sha256'])
                else:
                    pending.append(item['sha256'])
        for digest in sorted(self.objects):
            if digest not in self.values and digest not in self.opaque:
                value = parse_strict(self.objects[digest], '/source/objects/' + digest)
                if not isinstance(value, dict):
                    refuse('REBIND_INPUT_INVALID', '/source/objects/' + digest)
                self.values[digest] = value

    def kind_of(self, digest):
        if digest in self.opaque:
            return OPAQUE
        schema = self.values[digest].get('schema')
        return schema if isinstance(schema, str) else 'unknown'

    def targets(self):
        """Every to-be-replaced historical digest with a stable label."""
        labels = {}
        for role in ROLES:
            labels.setdefault(self.roles[role], 'roles/' + role)
        labels.setdefault(self.historical_build, 'historical_build')
        for name in BUNDLE_NAMES:
            labels.setdefault(self.pins['prior_bundle'][name], 'prior_bundle/' + name)
        return labels


def check_ref(node, kind, digest):
    return isinstance(node, dict) and set(node) == {'kind', 'sha256'} and node['kind'] == kind and \
        node['sha256'] == digest


def check_topology(src):
    """Role kinds, authored-record invariants, every rule precondition, EV-ID and prior pins."""
    for role in ROLES:
        value = src.role_values[role]
        if value.get('schema') != KIND[role]:
            refuse('REBIND_INPUT_INVALID', '/source/roles/' + role + '/schema')
    for role in RENDERED:
        value, target = src.role_values[role], '/source/roles/' + role
        if has_float(value):
            refuse('REBIND_INPUT_INVALID', target)
        if value.get('revision') != 1 or type(value.get('revision')) is not int or \
                'predecessor' not in value or value['predecessor'] is not None:
            refuse('REBIND_INPUT_INVALID', target + '/revision')
        provenance = value.get('provenance')
        if not isinstance(provenance, dict) or set(provenance) != {'role', 'label', 'basis', 'authenticated'} or \
                provenance['role'] not in ALLOWED_ROLES[KIND[role]] or provenance['authenticated'] is not False:
            refuse('REBIND_INPUT_INVALID', target + '/provenance')
        for pointer, dep in RULES[role]:
            parent, key = locate(value, pointer, target)
            if dep == LIST_B:
                if parent[key] != [src.historical_build]:
                    refuse('REBIND_INPUT_INVALID', target + pointer)
            elif not check_ref(parent[key], KIND[dep], src.old[dep]):
                refuse('REBIND_INPUT_INVALID', target + pointer)
    if src.role_values['evidence'].get('id') != 'E-t1-' + src.roles['J'][:59]:
        refuse('REBIND_INPUT_INVALID', '/source/roles/evidence/id')


def allowed_occurrences(src):
    """(object digest, pointer, historical digest) where a historical digest legitimately sits."""
    allowed = set()
    for role in RENDERED:
        for pointer, dep in RULES[role]:
            if dep == LIST_B:
                allowed.add((src.roles[role], pointer + '/0', src.historical_build))
            else:
                allowed.add((src.roles[role], pointer + '/sha256', src.old[dep]))
    return allowed


ATTESTATION_TEXT = ('/provenance/label', '/provenance/basis')


def attestation_text(pointer, is_key):
    """Literal provenance label/basis prose: preserved, reported, never rejected or rewritten.

    Owner disposition A (2026-10-23) supersedes the specification's §4.2
    wording for this prose only; structured fields are still checked.
    """
    return not is_key and pointer in ATTESTATION_TEXT


def prefix_hits(value, prefixes):
    """(pointer, text, is_key, digest, full) for every string holding a 12+ hex prefix of a target."""
    hits = []
    for pointer, text, is_key in walk_strings(value):
        if len(text) < 12:
            continue
        for prefix, digest in prefixes:
            if prefix in text:
                hits.append((pointer, text, is_key, digest, digest in text))
    return hits


def check_completeness(src):
    """Refuse an unmodelled dependency; never rewrite (specification §4.2, owner disposition A)."""
    labels = src.targets()
    prefixes = sorted((digest[:12], digest) for digest in labels)
    allowed = allowed_occurrences(src)
    ev_id = (src.roles['evidence'], '/id')
    for digest in sorted(src.values):
        for pointer, text, is_key, target, _ in prefix_hits(src.values[digest], prefixes):
            if not is_key and text == target and (digest, pointer, target) in allowed:
                continue
            if attestation_text(pointer, is_key):
                continue
            if not is_key and (digest, pointer) == ev_id and target == src.roles['J'] and \
                    text == 'E-t1-' + target[:59]:
                continue
            refuse('REBIND_UNMODELLED_DEPENDENCY', '/source/objects/' + digest + pointer)


# --------------------------------------------------------------- rendering

class Rendered:
    def __init__(self, role, old_digest, wire, value, changes, edges, dependencies):
        self.role, self.old_digest, self.wire, self.value = role, old_digest, wire, value
        self.digest = sha(wire)
        self.changes, self.edges, self.dependencies = changes, edges, dependencies


def render(role, src, new, attestation):
    """Apply exactly the rule table for one record, then the two attestation leaves."""
    source_value = src.role_values[role]
    value, target = copy.deepcopy(source_value), '/source/roles/' + role
    changes, edges, dependencies, expected = [], [], {}, set()
    for pointer, dep in RULES[role]:
        parent, key = locate(value, pointer, target)
        if dep == LIST_B:
            if parent[key] != [src.historical_build]:
                refuse('REBIND_INPUT_INVALID', target + pointer)
            parent[key] = [new['B']]
            changes.append({'pointer': pointer, 'old': [src.historical_build], 'new': [new['B']], 'rule': 'list:B'})
            edges.append({'from_role': role, 'pointer': pointer, 'to_role': 'B', 'to_sha256': new['B']})
            dependencies['B'] = new['B']
            expected.add(pointer + '/0')
        else:
            if not check_ref(parent[key], KIND[dep], src.old[dep]):
                refuse('REBIND_INPUT_INVALID', target + pointer)
            parent[key]['sha256'] = new[dep]
            changes.append({'pointer': pointer + '/sha256', 'old': src.old[dep], 'new': new[dep], 'rule': 'ref:' + dep})
            edges.append({'from_role': role, 'pointer': pointer, 'to_role': dep, 'to_sha256': new[dep]})
            dependencies[dep] = new[dep]
            expected.add(pointer + '/sha256')
    provenance = value['provenance']
    if provenance['role'] not in ALLOWED_ROLES[KIND[role]] or provenance['authenticated'] is not False:
        refuse('REBIND_INPUT_INVALID', target + '/provenance')
    for field in ('label', 'basis'):
        changes.append({'pointer': '/provenance/' + field, 'old': provenance[field], 'new': attestation[field],
                        'rule': 'attestation'})
        provenance[field] = attestation[field]
        expected.add('/provenance/' + field)
    wire = canon(value)
    if not set(leaf_diff(source_value, value)) <= expected or parse_strict(wire, target) != value:
        refuse('REBIND_INTERNAL', target)
    if len(wire) > RECORD_CAPS.get(KIND[role], CAPS['object']):
        refuse('REBIND_ATTESTATION_INVALID', '/attestations/records/' + role)
    return Rendered(role, src.roles[role], wire, value, changes, edges, dependencies)


def declared_times(role, value):
    times = {}
    for key in ('as_of', 'valid', 't0', 'window', 'question_as_of'):
        if key in value:
            times['/' + key] = value[key]
    if role == 'R':
        acquisition = value['result']['acquisition']
        for key in ('started', 'ended'):
            times['/result/acquisition/' + key] = acquisition[key]
    return times


# ------------------------------------------------------------ earlier stages

class StageInput:
    def __init__(self, directory, expected, stage, src):
        target = '/' + stage + '-dir'
        real_dir(directory, target)
        if os.path.lexists(os.path.join(directory, PARTIAL)):
            refuse('REBIND_PARTIAL', target)
        wire = read_capped(os.path.join(directory, REVIEW_PATH), CAPS['review'], target + '/' + REVIEW_PATH)
        if sha(wire) != expected:
            refuse('REBIND_PIN_MISMATCH', target + '/' + REVIEW_PATH)
        review = parse_strict(wire, target + '/' + REVIEW_PATH, form='pretty')
        bad = lambda where='': refuse('REBIND_INPUT_INVALID', target + where)
        if not isinstance(review, dict) or review.get('schema') != REVIEW_SCHEMA or review.get('stage') != stage or \
                review.get('tool_edition') != TOOL_EDITION or review.get('approval_state') != 'not_approved':
            bad('/' + REVIEW_PATH)
        if review.get('source_pins_sha256') != sha(src.pins_wire):
            refuse('REBIND_PIN_MISMATCH', target + '/source_pins_sha256')
        if not is_hex(review.get('build')):
            bad('/build')
        inventory = {}
        if not isinstance(review.get('outputs'), list) or not isinstance(review.get('inputs'), dict):
            bad('/' + REVIEW_PATH + '/outputs')
        for entry in review['outputs'] + [review.get('packet')]:
            if not isinstance(entry, dict) or not isinstance(entry.get('path'), str) or \
                    not REL_PATH.fullmatch(entry['path']) or '..' in entry['path'].split('/') or \
                    entry['path'] in (REVIEW_PATH, PARTIAL) or entry['path'] in inventory or \
                    not is_hex(entry.get('sha256')) or type(entry.get('bytes')) is not int or entry['bytes'] < 0:
                bad('/' + REVIEW_PATH + '/outputs')
            inventory[entry['path']] = (entry['sha256'], entry['bytes'])
        budget = Budget(CAPS['stage_total'], target)
        self.files = {}
        seen = set()
        pending = ['']
        limit = len(inventory) * 2 + 8
        while pending:
            relative = pending.pop()
            here = os.path.join(directory, *relative.split('/')) if relative else directory
            for name, link, regular, is_dir in scan_entries(here, limit, target):
                child = relative + '/' + name if relative else name
                if link:
                    bad('/' + child)
                if is_dir:
                    pending.append(child)
                    continue
                if not regular:
                    bad('/' + child)
                if child == REVIEW_PATH:
                    continue
                if child not in inventory:
                    bad('/' + child)
                digest, size = inventory[child]
                try:
                    data = read_capped(os.path.join(directory, *child.split('/')), size, target + '/' + child)
                except Refusal as refusal:
                    if refusal.code != 'REBIND_RESOURCE_LIMIT':
                        raise
                    bad('/' + child)   # larger than its recorded size: an inventory disagreement
                budget.take(len(data))
                if len(data) != size or sha(data) != digest:
                    bad('/' + child)
                self.files[child] = data
                seen.add(child)
        if seen != set(inventory):
            bad('/' + sorted(set(inventory) - seen)[0])
        rendered = review.get('rendered')
        if not isinstance(rendered, dict) or set(rendered) != set(STAGE_ROLES[stage]):
            bad('/' + REVIEW_PATH + '/rendered')
        self.digests, self.wires = {}, {}
        for role, row in rendered.items():
            if not isinstance(row, dict) or row.get('kind') != KIND[role] or not is_hex(row.get('new_sha256')) or \
                    row.get('path') not in self.files or sha(self.files[row['path']]) != row['new_sha256']:
                bad('/' + REVIEW_PATH + '/rendered/' + role)
            self.digests[role] = row['new_sha256']
            self.wires[role] = self.files[row['path']]
        self.review, self.wire, self.build = review, wire, review['build']

    def value(self, role):
        return parse_strict(self.wires[role], '/stage/' + role)


# --------------------------------------------------- generated dependencies

def check_prior_bundle(directory, expected_manifest, build, new, policy_wire, src):
    """Digest and field checks on B0' only (specification §6.3); not verification."""
    files = read_named_dir(directory, BUNDLE_NAMES, lambda n: BUNDLE_CAPS.get(n, CAPS['bundle_default']),
                           Budget(CAPS['bundle_total'], '/prior-bundle'), '/prior-bundle')
    mismatch = lambda where: refuse('REBIND_DEPENDENCY_MISMATCH', '/prior-bundle' + where)

    def record(name):
        value = parse_strict(files[name], '/prior-bundle/' + name)
        if not isinstance(value, dict):
            mismatch('/' + name)
        return value

    if sha(files['manifest.json']) != expected_manifest:
        refuse('REBIND_PIN_MISMATCH', '/prior-bundle/manifest.json')
    manifest = record('manifest.json')
    if manifest.get('schema') != 'ct.bundle-manifest.v1' or \
            manifest.get('bundle_kind') != 'selection' or not isinstance(manifest.get('files'), list):
        mismatch('/manifest.json')
    listed = manifest['files']
    if len(listed) != len(BUNDLE_ROLES):
        mismatch('/manifest.json/files')
    for entry, (name, role) in zip(listed, BUNDLE_ROLES):
        if not isinstance(entry, dict) or set(entry) != {'name', 'role', 'sha256', 'bytes'} or \
                entry['name'] != name or entry['role'] != role or entry['sha256'] != sha(files[name]) or \
                entry['bytes'] != len(files[name]) or type(entry['bytes']) is not int:
            mismatch('/' + name)
    if sha(files['build.json']) != build:
        mismatch('/build.json')
    if record('build.json').get('schema') != 'ct.build.v1':
        mismatch('/build.json')
    if files['policy.json'] != policy_wire:
        mismatch('/policy.json')
    invocation = record('invocation.json')
    for key, expected in (('operation', 'checked-selection-evaluate'), ('request', ref(KIND['P'], new['P'])),
                          ('authority', ref(KIND['A0'], new['A0'])), ('expected_request_pin', new['P']),
                          ('expected_authority_pin', new['A0']), ('build', ref(KIND['B'], build)),
                          ('replay_of', None)):
        if key not in invocation or invocation[key] != expected:
            mismatch('/invocation.json/' + key)
    result = record('result.json')
    if result.get('schema') != 'ct.selection.v1' or result.get('request') != ref(KIND['P'], new['P']) or \
            dig(result, 'build', 'sha256') != build:
        mismatch('/result.json')
    x = src.role_values['X']
    if record('derivation.json').get('model') != x.get('model'):
        mismatch('/derivation.json/model')
    model = src.values.get(dig(x, 'model', 'sha256')) if dig(x, 'model', 'kind') == 'ct.model.v1' else None
    if not isinstance(model, dict) or not isinstance(model.get('procedures'), list):
        refuse('REBIND_INPUT_INVALID', '/source/roles/X/model')
    t1 = [p for p in model['procedures'] if isinstance(p, dict) and p.get('edition') == T1]
    if len(t1) != 1 or t1[0].get('interpretation_plan') != x.get('interpretation_plan'):
        mismatch('/source/roles/X/interpretation_plan')
    uncertainty = result.get('observation_uncertainty_not_in_score', [])
    if not isinstance(uncertainty, list):
        mismatch('/result.json/observation_uncertainty_not_in_score')
    for entry in uncertainty:
        if isinstance(entry, dict) and entry.get('procedure_edition') == T1 and \
                entry.get('plan') != x.get('interpretation_plan'):
            mismatch('/result.json/observation_uncertainty_not_in_score')
    return files


def check_producer(directory, expected_manifest, s1, s2, src):
    """Stage-3 membership check of the simulator evidence in M' (specification §7.4).

    Consistency only; the simulation-verified guarantee comes from the
    maintained commands.
    """
    mismatch = lambda where: refuse('REBIND_DEPENDENCY_MISMATCH', '/producer-package' + where)
    real_dir(directory, '/producer-package')
    if os.path.lexists(os.path.join(directory, PARTIAL)):
        mismatch('/' + PARTIAL)
    for part in ('receipt', 'evidence', 'evidence/public'):
        real_dir(os.path.join(directory, *part.split('/')), '/producer-package/' + part)
    budget, files = Budget(CAPS['producer_total'], '/producer-package'), {}
    for relative, cap in PRODUCER_FILES:
        files[relative] = read_capped(os.path.join(directory, *relative.split('/')), cap,
                                      '/producer-package/' + relative)
        budget.take(len(files[relative]))
    manifest_wire = files['manifest.json']
    receipt_wire = files['receipt/receipt.json']
    evidence_wire = files['evidence/public/evidence.json']
    if sha(manifest_wire) != expected_manifest:
        refuse('REBIND_PIN_MISMATCH', '/producer-package/manifest.json')
    def record(relative, wire):
        value = parse_strict(wire, '/producer-package/' + relative)
        if not isinstance(value, dict):
            mismatch('/' + relative)
        return value

    manifest = record('manifest.json', manifest_wire)
    if manifest.get('schema') != 'ct.t1-producer-manifest.v1' or not isinstance(manifest.get('roots'), dict) or \
            not isinstance(manifest.get('members'), list):
        mismatch('/manifest.json')
    roots = manifest['roots']
    pins = {'target': ref(KIND['J'], s2.digests['J']), 'permission': ref(KIND['G'], s2.digests['G']),
            'execution_authority': ref(KIND['E'], s2.digests['E'])}
    for key, expected in pins.items():
        if roots.get(key) != expected:
            mismatch('/manifest.json/roots/' + key)
    members = [m for m in manifest['members'] if isinstance(m, dict)]
    if len(members) != len(manifest['members']):
        mismatch('/manifest.json/members')
    public = [m for m in members if m.get('role') == 'public_evidence']
    if len(public) != 1 or public[0].get('path') != 'evidence/public/evidence.json' or \
            public[0].get('kind') != KIND['evidence'] or public[0].get('sha256') != sha(evidence_wire) or \
            public[0].get('bytes') != len(evidence_wire):
        mismatch('/manifest.json/members/public_evidence')
    receipts = [m for m in members if m.get('role') == 'producer_receipt']
    if len(receipts) != 1 or receipts[0].get('path') != 'receipt/receipt.json' or \
            receipts[0].get('sha256') != sha(receipt_wire) or receipts[0].get('bytes') != len(receipt_wire) or \
            roots.get('receipt') != ref('ct.t1-producer-receipt.v1', sha(receipt_wire)):
        mismatch('/manifest.json/members/producer_receipt')
    receipt = record('receipt/receipt.json', receipt_wire)
    expected_receipt = dict(pins, public_evidence=ref(KIND['evidence'], sha(evidence_wire)),
                            producer_build=ref(KIND['B'], s1.build),
                            captured_policy=ref(KIND['policy'], s1.digests['policy']),
                            simulator_policy=ref(KIND['simulator_policy'], s2.digests['simulator_policy']),
                            execution_target=ref(KIND['X'], s2.digests['X']))
    if receipt.get('schema') != 'ct.t1-producer-receipt.v1':
        mismatch('/receipt/receipt.json/schema')
    for key, expected in sorted(expected_receipt.items()):
        if receipt.get(key) != expected:
            mismatch('/receipt/receipt.json/' + key)
    evidence = record('evidence/public/evidence.json', evidence_wire)
    j = s2.value('J')
    model = src.values.get(dig(src.role_values['X'], 'model', 'sha256'))
    baseline = src.values.get(dig(model, 'baseline_evidence', 'sha256'))
    if evidence.get('schema') != KIND['evidence']:
        mismatch('/evidence/public/evidence.json/schema')
    if evidence.get('id') != 'E-t1-' + s2.digests['J'][:59]:
        mismatch('/evidence/public/evidence.json/id')
    question = evidence.get('question')
    if not isinstance(question, dict) or j.get('question_as_of') is None or \
            question.get('as_of') != j['question_as_of']:
        mismatch('/evidence/public/evidence.json/question/as_of')
    if not isinstance(baseline, dict) or 'binding' not in baseline or evidence.get('binding') != baseline['binding']:
        mismatch('/evidence/public/evidence.json/binding')
    scalar = dig(src.role_values['R'], 'result', 'observation', 'scalar')
    if not isinstance(receipt.get('r'), str) or receipt['r'] != scalar:
        mismatch('/receipt/receipt.json/r')
    labels = src.targets()
    if any(not attestation_text(pointer, is_key)
           for pointer, _, is_key, _, _ in prefix_hits(evidence, sorted((d[:12], d) for d in labels))):
        mismatch('/evidence/public/evidence.json')
    return {'evidence': evidence_wire, 'files': files}


# ------------------------------------------------------------------ output

class Plan:
    """Planned output files with their review rows."""

    def __init__(self):
        self.rows, self.data = [], {}

    def add(self, path, data, kind, disposition, origin, role=None):
        if path in self.data:
            refuse('REBIND_INTERNAL', '/out/' + path)
        self.data[path] = data
        row = {'path': path, 'sha256': sha(data), 'bytes': len(data), 'kind': kind,
               'disposition': disposition, 'source': origin}
        if role is not None:
            row['role'] = role
        self.rows.append(row)


def _write_fd(fd, data):
    view = memoryview(data)
    while view:
        view = view[os.write(fd, view):]


def check_out(out, inputs):
    """--out must be new, under a symlink-free real parent, outside inputs and the repository."""
    absolute = os.path.abspath(out)
    if os.path.lexists(absolute):
        refuse('REBIND_OUTPUT_UNSAFE', '/out')
    parent = os.path.dirname(absolute)
    walked = os.sep
    for part in [p for p in parent.split(os.sep) if p]:
        walked = os.path.join(walked, part)
        try:
            info = os.lstat(walked)
        except OSError:
            refuse('REBIND_OUTPUT_UNSAFE', '/out')
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            refuse('REBIND_OUTPUT_UNSAFE', '/out')
    resolved = os.path.join(os.path.realpath(parent), os.path.basename(absolute))
    repository = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    for forbidden in [repository] + [os.path.realpath(p) for p in inputs]:
        if resolved == forbidden or resolved.startswith(forbidden.rstrip(os.sep) + os.sep):
            refuse('REBIND_OUTPUT_UNSAFE', '/out')
    return absolute


class Writer:
    """Exclusive creation under a PARTIAL marker; nothing is ever deleted on failure."""

    def __init__(self, out):
        self.out, self.dirs = out, ['']
        try:
            os.mkdir(out, 0o700)
        except OSError:
            refuse('REBIND_OUTPUT_UNSAFE', '/out')
        self._create(PARTIAL, b'', 0o600)

    def _create(self, relative, data, mode=0o644):
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_CLOEXEC', 0)
        try:
            fd = os.open(os.path.join(self.out, *relative.split('/')), flags, mode)
            try:
                _write_fd(fd, data)
                os.fsync(fd)
            finally:
                os.close(fd)
        except OSError:
            refuse('REBIND_PARTIAL', '/out/' + relative)

    def put(self, relative, data):
        parts = relative.split('/')
        for i in range(1, len(parts)):
            directory = '/'.join(parts[:i])
            if directory not in self.dirs:
                try:
                    os.mkdir(os.path.join(self.out, *parts[:i]), 0o700)
                except OSError:
                    refuse('REBIND_PARTIAL', '/out/' + directory)
                self.dirs.append(directory)
        self._create(relative, data)

    def readback(self, relative, data):
        """A missing, unreadable, oversized or differing file after creation is partial output (§5.4)."""
        try:
            again = read_capped(os.path.join(self.out, *relative.split('/')), len(data), '/out/' + relative)
        except Refusal:
            refuse('REBIND_PARTIAL', '/out/' + relative)
        if again != data:
            refuse('REBIND_PARTIAL', '/out/' + relative)
        return again

    def finish(self):
        try:
            for directory in sorted(self.dirs, key=len, reverse=True):
                fd = os.open(os.path.join(self.out, *directory.split('/')) if directory else self.out,
                             os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
            os.unlink(os.path.join(self.out, PARTIAL))
            fd = os.open(self.out, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        except OSError:
            if not os.path.lexists(os.path.join(self.out, PARTIAL)):
                try:
                    self._create(PARTIAL, b'', 0o600)   # restore the marker where possible
                except Refusal:
                    pass
            refuse('REBIND_PARTIAL', '/out/' + PARTIAL)


def scan_outputs(plan, src, rendered_paths):
    """Output diagnostic scan (specification §4.3): disclosure, never repair."""
    labels = src.targets()
    prefixes = sorted((digest[:12], digest) for digest in labels)
    hits = []
    for row in plan.rows:
        if row['kind'] == OPAQUE:
            continue
        value = parse_strict(plan.data[row['path']], '/out/' + row['path'])
        for pointer, _text, is_key, digest, full in prefix_hits(value, prefixes):
            if not attestation_text(pointer, is_key):
                refuse('REBIND_INTERNAL', '/out/' + row['path'] + pointer)
            hits.append({'path': row['path'], 'pointer': pointer, 'historical': labels[digest],
                         'match': 'full' if full else 'prefix', 'classification': 'in_attestation_text',
                         'record': 'rendered' if row['path'] in rendered_paths else 'copied'})
    return hits


def emit(stage, out, src, attestation, tool_wire, build, inputs, plan, rendered, earlier, next_operation,
         tool_rendered_paths):
    """Packet and review in memory, caps checked, then exclusive writes, readback and finish."""
    records = attestation[0]
    flags = {}
    for role in STAGE_ROLES[stage]:
        flags[role] = {'label': records[role]['label'] == HISTORICAL_TEXT['label'],
                       'basis': records[role]['basis'] == HISTORICAL_TEXT['basis']}
    hits = scan_outputs(plan, src, tool_rendered_paths)
    diagnostics = {'output_scan': hits,
                   'in_lineage': {'paths': [PACKET_PATH, REVIEW_PATH],
                                  'note': 'lineage files record every old to new pair by design and are not scanned'},
                   'matches_historical_text': {role: f['label'] or f['basis'] for role, f in sorted(flags.items())}}
    packet = {
        'schema': PACKET_SCHEMA, 'stage': stage, 'approval_point': APPROVAL_POINT[stage],
        'tool_edition': TOOL_EDITION, 'build': build, 'source_pins_sha256': sha(src.pins_wire),
        'attestations_sha256': sha(attestation[1]), 'earlier_stage_reviews': earlier,
        'earlier_stage_approval_records': (
            'EX-0 for this stage must cite the approval-record digest of every earlier stage; this tool neither '
            'reads nor verifies approval records' if earlier else None),
        'records': [{
            'role': r.role, 'kind': KIND[r.role], 'sha256': r.digest, 'bytes': len(r.wire),
            'old_sha256': r.old_digest, 'candidate_text': r.wire.decode('utf-8'), 'changes': r.changes,
            'dependencies': r.dependencies, 'attestation': dict(records[r.role]),
            'matches_historical_text': flags[r.role]['label'] or flags[r.role]['basis'],
            'matches_historical_label': flags[r.role]['label'], 'matches_historical_basis': flags[r.role]['basis'],
            'provenance_role': r.value['provenance']['role'], 'approval_id': APPROVAL_IDS[r.role],
            'approval_subject': APPROVAL_SUBJECT[r.role], 'declared_times': declared_times(r.role, r.value),
            'declared_times_interpretation': TIMES_NOTE, 'synthetic_scope': SCOPE_NOTE}
            for r in rendered],
        'approval_authorizes': AUTHORIZES[stage], 'approval_excludes': EXCLUDES[stage],
        'approval_record_required': {
            'schema': APPROVAL_SCHEMA, 'approval_point': APPROVAL_POINT[stage],
            'written_by': 'the owner, or a delegate on explicit owner instruction, as a separate file; never by '
                          'this tool and never inside an objects directory or application record',
            'fields': ['approval_point', 'stage_review_sha256', 'packet_sha256', 'candidates',
                       'attestations_sha256', 'decision', 'authorizes', 'excludes',
                       'next_operation_requires_separate_grant', 'recorded_on'],
            'must_cover': [{'role': r.role, 'kind': KIND[r.role], 'sha256': r.digest, 'bytes': len(r.wire)}
                           for r in rendered],
            'partial_approval_supported': False,
            'read_by': 'neither this tool nor the application; the operator of a later execution grant compares '
                       'its pins with the candidates'},
        'blocked_next_operation': {'status': NOT_AUTHORIZED, 'grant_required': NEXT_GRANT[stage],
                                   'command': next_operation},
        'approval_state': 'not_approved', 'statement': STATEMENT}
    packet_wire = pretty(packet)
    edges = [edge for r in rendered for edge in r.edges]
    review = {
        'schema': REVIEW_SCHEMA, 'stage': stage, 'tool_edition': TOOL_EDITION, 'tool_sha256': sha(tool_wire),
        'source_pins_sha256': sha(src.pins_wire), 'attestations_sha256': sha(attestation[1]), 'build': build,
        'inputs': inputs, 'outputs': sorted(plan.rows, key=lambda row: row['path']),
        'packet': {'path': PACKET_PATH, 'sha256': sha(packet_wire), 'bytes': len(packet_wire)},
        'rendered': {r.role: {'kind': KIND[r.role], 'old_sha256': r.old_digest, 'new_sha256': r.digest,
                              'bytes': len(r.wire), 'path': next(row['path'] for row in plan.rows
                                                                 if row.get('role') == r.role)}
                     for r in rendered},
        'changes': {r.role: r.changes for r in rendered}, 'edges': edges, 'diagnostics': diagnostics,
        'approval_state': 'not_approved', 'statement': STATEMENT}
    review_wire = pretty(review)
    count, total = len(plan.rows) + 2, sum(map(len, plan.data.values())) + len(packet_wire) + len(review_wire)
    if count > OUTPUT_CAPS[stage][0] or total > OUTPUT_CAPS[stage][1]:
        refuse('REBIND_RESOURCE_LIMIT', '/out')
    writer = Writer(out)
    for row in plan.rows:
        writer.put(row['path'], plan.data[row['path']])
    for row in plan.rows:
        writer.readback(row['path'], plan.data[row['path']])
    if scan_outputs(plan, src, tool_rendered_paths) != hits:
        refuse('REBIND_INTERNAL', '/out')
    writer.put(PACKET_PATH, packet_wire)
    writer.put(REVIEW_PATH, review_wire)
    writer.readback(PACKET_PATH, packet_wire)
    writer.readback(REVIEW_PATH, review_wire)
    writer.finish()
    return sha(review_wire)


# ------------------------------------------------------------------ stages

def tool_bytes():
    return read_capped(os.path.realpath(__file__), CAPS['tool'], '/tool')


def base_inputs(src, attestation):
    inputs = {'source_pins': {'sha256': sha(src.pins_wire), 'bytes': len(src.pins_wire)},
              'attestations': {'sha256': sha(attestation[1]), 'bytes': len(attestation[1])},
              'source/historical_build': {'sha256': src.historical_build, 'bytes': None}}
    for role in ROLES:
        inputs['source/' + role] = {'sha256': src.roles[role], 'bytes': len(src.objects[src.roles[role]])}
    for name in BUNDLE_NAMES:
        inputs['source/prior/' + name] = {'sha256': sha(src.prior[name]), 'bytes': len(src.prior[name])}
    return inputs


def stage1(a):
    out = check_out(a['out'], [a['source-dir']])
    tool = tool_bytes()
    src = Source(a['source-dir'], a['source-pins'], a['expected-source-pins-sha256'])
    build = a['build-digest']
    if build == src.historical_build or build in src.objects or build in src.pins['prior_bundle'].values():
        refuse('REBIND_INPUT_INVALID', '/argv/build-digest')
    attestation = load_attestations(a['attestations'], a['expected-attestations-sha256'], 'stage1')
    new, rendered = {'B': build}, []
    for role in STAGE_ROLES['stage1']:
        rendered.append(render(role, src, new, attestation[0][role]))
        new[role] = rendered[-1].digest
    by_role = {r.role: r for r in rendered}
    plan = Plan()
    plan.add(REQUEST_PATH, by_role['P'].wire, KIND['P'], 'rendered', 'stage1', 'P')
    for digest in src.pins['unchanged']['selection_objects']:
        plan.add('selection/objects/' + digest, src.objects[digest], src.kind_of(digest), 'copied_unchanged',
                 'source')
    for role in ('policy', 'A0'):
        plan.add('selection/objects/' + by_role[role].digest, by_role[role].wire, KIND[role], 'rendered',
                 'stage1', role)
    inputs = dict(base_inputs(src, attestation), build_digest={'sha256': build, 'bytes': None})
    command = ['checked-selection-evaluate', '--request', '<stage1-out>/' + REQUEST_PATH,
               '--objects-dir', '<stage1-out>/selection/objects', '--expected-request-pin', new['P'],
               '--expected-authority-pin', new['A0'], '--output-dir', '<new-selection-bundle-dir>',
               '(on the target build ' + build + ' only)']
    paths = {row['path'] for row in plan.rows if row['disposition'] == 'rendered'}
    return emit('stage1', out, src, attestation, tool, build, inputs, plan, rendered, {}, command, paths)


def stage2(a):
    out = check_out(a['out'], [a['source-dir'], a['stage1-dir'], a['prior-bundle']])
    tool = tool_bytes()
    src = Source(a['source-dir'], a['source-pins'], a['expected-source-pins-sha256'])
    s1 = StageInput(a['stage1-dir'], a['expected-stage1-review-sha256'], 'stage1', src)
    attestation = load_attestations(a['attestations'], a['expected-attestations-sha256'], 'stage2')
    build = s1.build
    new = dict(s1.digests, B=build)
    bundle = check_prior_bundle(a['prior-bundle'], a['expected-prior-manifest-sha256'], build, new,
                                s1.wires['policy'], src)
    new['B0.manifest'], new['B0.result'] = sha(bundle['manifest.json']), sha(bundle['result.json'])
    rendered = []
    for role in STAGE_ROLES['stage2']:
        rendered.append(render(role, src, new, attestation[0][role]))
        new[role] = rendered[-1].digest
    plan = Plan()
    for digest in src.pins['unchanged']['simulation_input']:
        plan.add('simulation-input/' + digest, src.objects[digest], src.kind_of(digest), 'copied_unchanged', 'source')
    for r in rendered:
        plan.add('simulation-input/' + r.digest, r.wire, KIND[r.role], 'rendered', 'stage2', r.role)
    inputs = dict(base_inputs(src, attestation), stage1_review={'sha256': sha(s1.wire), 'bytes': len(s1.wire)})
    for name in BUNDLE_NAMES:
        inputs['prior_bundle/' + name] = {'sha256': sha(bundle[name]), 'bytes': len(bundle[name])}
    for role in STAGE_ROLES['stage1']:
        inputs['stage1/' + role] = {'sha256': s1.digests[role], 'bytes': len(s1.wires[role])}
    command = ['t1-simulation-run', '--objects-dir', '<stage2-out>/simulation-input', '--prior-bundle',
               '<selection-bundle-dir with manifest ' + new['B0.manifest'] + '>', '--expected-target-pin', new['J'],
               '--expected-execution-authority-pin', new['E'], '--expected-permission-pin', new['G'],
               '--expected-prior-request-pin', new['P'], '--expected-prior-authority-pin', new['A0'],
               '--output-dir', '<new-producer-package-dir>']
    paths = {row['path'] for row in plan.rows if row['disposition'] == 'rendered'}
    return emit('stage2', out, src, attestation, tool, build, inputs, plan, rendered,
                {'stage1': sha(s1.wire)}, command, paths)


def stage3(a):
    out = check_out(a['out'], [a['source-dir'], a['stage1-dir'], a['stage2-dir'], a['producer-package']])
    tool = tool_bytes()
    src = Source(a['source-dir'], a['source-pins'], a['expected-source-pins-sha256'])
    s1 = StageInput(a['stage1-dir'], a['expected-stage1-review-sha256'], 'stage1', src)
    s2 = StageInput(a['stage2-dir'], a['expected-stage2-review-sha256'], 'stage2', src)
    if dig(s2.review, 'inputs', 'stage1_review', 'sha256') != sha(s1.wire) or s2.build != s1.build:
        refuse('REBIND_PIN_MISMATCH', '/stage2-dir/inputs/stage1_review')
    attestation = load_attestations(a['attestations'], a['expected-attestations-sha256'], 'stage3')
    build = s1.build
    produced = check_producer(a['producer-package'], a['expected-producer-manifest-sha256'], s1, s2, src)
    j = s2.value('J')
    for key, expected in (('started', dig(j, 'window', 'from')), ('ended', dig(j, 'window', 'to')),
                          ('instrument_id', j.get('instrument_id'))):
        if expected is None or dig(src.role_values['R'], 'result', 'acquisition', key) != expected:
            refuse('REBIND_DEPENDENCY_MISMATCH', '/source/roles/R/result/acquisition/' + key)
    new = dict(s1.digests, **s2.digests, B=build, evidence=sha(produced['evidence']))
    new['B0.manifest'] = dig(s2.review, 'inputs', 'prior_bundle/manifest.json', 'sha256')
    new['B0.result'] = dig(s2.review, 'inputs', 'prior_bundle/result.json', 'sha256')
    x2 = dig(s2.value('X'), 'prior_selection')
    if not is_hex(new['B0.manifest']) or not is_hex(new['B0.result']) or \
            x2 != {'manifest': ref(KIND['B0.manifest'], new['B0.manifest']),
                   'selection': ref(KIND['B0.result'], new['B0.result'])}:
        refuse('REBIND_INPUT_INVALID', '/stage2-dir/inputs/prior_bundle')
    rendered = [render('R', src, new, attestation[0]['R'])]
    plan = Plan()
    for digest in src.pins['unchanged']['request_input']:
        plan.add('request-input/' + digest, src.objects[digest], src.kind_of(digest), 'copied_unchanged', 'source')
    plan.add('request-input/' + s1.digests['policy'], s1.wires['policy'], KIND['policy'], 'copied_generated',
             'stage1')
    for role in ('X', 'E'):
        plan.add('request-input/' + s2.digests[role], s2.wires[role], KIND[role], 'copied_generated', 'stage2')
    plan.add('request-input/' + new['evidence'], produced['evidence'], KIND['evidence'], 'copied_generated',
             'producer')
    plan.add('request-input/' + rendered[0].digest, rendered[0].wire, KIND['R'], 'rendered', 'stage3', 'R')
    inputs = dict(base_inputs(src, attestation), stage1_review={'sha256': sha(s1.wire), 'bytes': len(s1.wire)},
                  stage2_review={'sha256': sha(s2.wire), 'bytes': len(s2.wire)})
    for relative, data in produced['files'].items():
        inputs['producer/' + relative] = {'sha256': sha(data), 'bytes': len(data)}
    for role in STAGE_ROLES['stage1'] + STAGE_ROLES['stage2']:
        stage_input = s1 if role in STAGE_ROLES['stage1'] else s2
        inputs['stage/' + role] = {'sha256': stage_input.digests[role], 'bytes': len(stage_input.wires[role])}
    manifest_pin = sha(produced['files']['manifest.json'])
    command = ['t1-reassessment-prepare', '--producer-package', '<producer-package-dir>',
               '--expected-producer-manifest-pin', manifest_pin, '--objects-dir', '<stage3-out>/request-input',
               '--expected-target-pin', new['J'], '--expected-execution-authority-pin', new['E'],
               '--expected-permission-pin', new['G'], '--expected-prior-request-pin', new['P'],
               '--expected-prior-authority-pin', new['A0'], '--prior-bundle',
               '<selection-bundle-dir with manifest ' + new['B0.manifest'] + '>', '--scratch-dir',
               '<new-scratch-dir>', '--output-dir', '<new-handoff-dir>',
               '(then A-prime is prepared outside this tool and approved at AP-S4)']
    paths = {row['path'] for row in plan.rows if row['source'] in ('stage1', 'stage2', 'stage3')}
    return emit('stage3', out, src, attestation, tool, build, inputs, plan, rendered,
                {'stage1': sha(s1.wire), 'stage2': sha(s2.wire)}, command, paths)


STAGES = {'stage1': stage1, 'stage2': stage2, 'stage3': stage3}


def parse_argv(argv):
    """Exactly one stage, then every required --flag exactly once with one value."""
    if not argv or argv[0] not in FLAGS:
        refuse('REBIND_USAGE', '/argv')
    stage, rest = argv[0], argv[1:]
    if len(rest) % 2:
        refuse('REBIND_USAGE', '/argv')
    values = {}
    for flag, value in zip(rest[0::2], rest[1::2]):
        name = flag[2:] if flag.startswith('--') else None
        if name not in FLAGS[stage] or name in values:
            refuse('REBIND_USAGE', '/argv')
        if not value or value.startswith('--') or '\x00' in value:
            refuse('REBIND_USAGE', '/argv/' + name)
        values[name] = value
    if set(values) != set(FLAGS[stage]):
        refuse('REBIND_USAGE', '/argv')
    for name in HEX_FLAGS:
        if name in values and not is_hex(values[name]):
            refuse('REBIND_USAGE', '/argv/' + name)
    if values.get('build-digest') == ZERO:
        refuse('REBIND_USAGE', '/argv/build-digest')
    return stage, values


def main(argv=None, *, out=None, err=None):
    out = sys.stdout if out is None else out
    err = sys.stderr if err is None else err
    try:
        stage, values = parse_argv(list(sys.argv[1:] if argv is None else argv))
        review_sha = STAGES[stage](values)
        out.write(canon({'outcome': 'rendered', 'stage': stage, 'review_sha256': review_sha,
                         'out': values['out']}).decode('utf-8') + '\n')
        return 0
    except Refusal as refusal:
        err.write(canon({'code': refusal.code, 'target': refusal.target}).decode('utf-8') + '\n')
        return EXIT[refusal.code]
    except Exception:  # never a traceback or an absolute path
        err.write(canon({'code': 'REBIND_INTERNAL', 'target': '/'}).decode('utf-8') + '\n')
        return EXIT['REBIND_INTERNAL']


if __name__ == '__main__':
    sys.exit(main())
