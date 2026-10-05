"""Checked-temperature contracts: canonical bytes, refusals, pinned schemas, numbers.

The approved v4 schemas are vendored byte-identically and pinned by SHA-256;
no preparation directory is consulted at run time. JSON Schema annotations
(`x-target`, `x-allowed-roles`) are collected here and enforced by the
semantic reference stage, never treated as enforcement by themselves.
"""
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from math import gcd
from pathlib import Path
import re

PROFILE = 'bdw.checked-temperature.v1'
SCHEMAS_SHA256 = '43c2af0b7bc3be137a0576e51b281be1ea53854c5e13d5d0a2c807f7611ac570'
POLICY_EDITION_SHA256 = '46df039bff18ab0ccb8a31262e42f1f0d40a828ede6e797953b769ecb49e8c15'
POLICY_EDITION = 'ct.policy-edition.v4'   # schema const and CONTRACT §12.1 agree (v4)
CATALOGUE = 'ct.conditions.v2'
CALCULATOR = 'ct.calculator.v1'
T1, T2 = 'ct.procedure.T1.v1', 'ct.procedure.T2.v1'

EDITION_LIMITS = {
    'applicability_bytes': 131072, 'build_bytes': 65536, 'bundle_bytes_reassessment': 4194304,
    'bundle_bytes_selection': 2097152, 'claims': 24, 'condition_declarations': 32,
    'declarations_per_claim': 8, 'derivation_bytes': 65536, 'derivation_cells': 10,
    'diagnostic_bytes': 2048, 'evidence_items': 32, 'evidence_items_per_claim': 8,
    'fractional_digits': 6, 'hypotheses': 2, 'integer_digits': 32, 'invocation_bytes': 16384,
    'json_depth': 24, 'json_nodes': 65536, 'manifest_bytes': 16384, 'object_bytes': 196608,
    'outcomes_per_procedure': 3, 'policy_bytes': 16384, 'procedures': 2, 'rational_operations': 1024,
    'reassessment_closure_decoded_bytes': 2621440, 'reassessment_closure_file_bytes': 3670016,
    'reassessment_unique_objects': 400, 'receipt_bytes': 1024, 'result_bytes': 65536,
    'retained_selection_bytes': 32768, 'reviews': 64, 'reviews_per_item': 4,
    'selection_closure_decoded_bytes': 1048576, 'selection_closure_file_bytes': 1474560,
    'selection_unique_objects': 192, 'string_bytes': 4096, 'successor_chain': 4,
    'trace_bytes': 131072, 'trace_entries': 512,
}

# Edition conditions per procedure (policy.json#/editions/procedures).
PROCEDURE_CONDITIONS = {
    T1: ('reference_calibration', 'reference_mapping', 'state_hold', 'observation_error_bound'),
    T2: ('state_hold', 'indicator_fidelity'),
}
T1_REGIONS = (  # ct.decoder.T1.v1: (id, lo, lo_closed, hi, hi_closed); None = unbounded
    ('low', None, False, Fraction(56), True),
    ('gap', Fraction(56), False, Fraction(59), True),
    ('high', Fraction(59), False, None, False),
)
T2_CODES = ('heater_off', 'heater_on')
HALF_WIDTH_MAX = Fraction(5)
B_REF_BOUND = Fraction(10)
H2_MAX = Fraction(50)
SCALAR_DOMAIN = (Fraction(-200), Fraction(1000))
OPAQUE_KIND = 'ct.evidence-content'
LEGACY_EVIDENCE_KIND = 'nm.evidence.v1'

EXIT_INTEGRITY, EXIT_USAGE, EXIT_RESOURCE, EXIT_FILESYSTEM, EXIT_RETENTION, EXIT_OUTPUT = 3, 2, 4, 5, 6, 7


class CheckedRefusal(Exception):
    """A refusal with a policy refusal code, validation stage and target path."""

    def __init__(self, code, *, stage, target='/', exit_class=None):
        super().__init__(code)
        self.code = code
        self.stage = stage
        self.target = target
        if exit_class is None:
            exit_class = EXIT_RESOURCE if code == 'RESOURCE_LIMIT_EXCEEDED' else EXIT_INTEGRITY
        self.exit_class = exit_class


def refuse(code, stage, target='/', exit_class=None):
    raise CheckedRefusal(code, stage=stage, target=target, exit_class=exit_class)


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(kind, digest):
    return {'kind': kind, 'sha256': digest}


def ref_of(kind, value):
    return ref(kind, sha(canonical_bytes(value)))


def _load_schemas():
    path = Path(__file__).with_name('checked_temperature_schemas.json')
    data = path.read_bytes()
    if sha(data) != SCHEMAS_SHA256:
        refuse('EDITION_CONTENT_MISMATCH', 4, '/schemas')
    return json.loads(data)


SCHEMAS = _load_schemas()
KINDS = tuple(SCHEMAS['typed_reference_kinds'])


# ---------------------------------------------------------------- stage 1: wire

def _no_duplicates(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            refuse('SCHEMA_INVALID', 1, '/duplicate_key')
        seen[k] = v
    return seen


def _reject_constant(name):
    refuse('SCHEMA_INVALID', 1, '/non_finite_number')


class Ops:
    """Rational-operation accounting (CONTRACT §12.9): one unit per exact rational
    addition, subtraction or comparison; a decoder-region intersection test is 4."""

    def __init__(self):
        self.count = 0

    def add(self, n=1):
        self.count += n


def scan(value, limits, target, *, base64_data=False):
    """Depth, node, string and integer-digit limits over a parsed value.

    `base64_data` exempts only the designated payload field
    ct.closure.v1 members[*].data from string_bytes (CONTRACT §12.5).
    """
    nodes = 0
    stack = [(value, 1, ())]
    while stack:
        v, depth, path = stack.pop()
        nodes += 1
        if depth > limits['json_depth'] or nodes > limits['json_nodes']:
            refuse('RESOURCE_LIMIT_EXCEEDED', 1, target)
        if isinstance(v, dict):
            for k, x in v.items():
                if k in ('numerator', 'denominator') and isinstance(x, str) and \
                        len(x.lstrip('-')) > limits['integer_digits']:
                    refuse('RESOURCE_LIMIT_EXCEEDED', 1, target + '/' + k)
                stack.append((x, depth + 1, path + (k,)))
        elif isinstance(v, list):
            stack.extend((x, depth + 1, path + (i,)) for i, x in enumerate(v))
        elif isinstance(v, str) and len(v.encode('utf-8')) > limits['string_bytes']:
            designated = base64_data and len(path) == 3 and path[0] == 'members' and \
                isinstance(path[1], int) and path[2] == 'data'
            if not designated:
                refuse('RESOURCE_LIMIT_EXCEEDED', 1, target)


def parse_canonical(wire, limits, *, cap_name='object_bytes', target='/', base64_data=False):
    """Stage 1: size cap, strict JSON, resource scans, then canonical form."""
    if len(wire) > limits[cap_name]:
        refuse('RESOURCE_LIMIT_EXCEEDED', 1, target)
    try:
        text = wire.decode('utf-8')
        value = json.loads(text, object_pairs_hook=_no_duplicates, parse_constant=_reject_constant)
    except CheckedRefusal:
        raise
    except RecursionError:
        refuse('RESOURCE_LIMIT_EXCEEDED', 1, target)   # review I4: nesting beyond the parser
    except (UnicodeDecodeError, ValueError):
        refuse('SCHEMA_INVALID', 1, target)
    scan(value, limits, target, base64_data=base64_data)
    # Finite floats are not refused here: the contract forbids only NaN/Infinity
    # (handled by parse_constant) and the legacy public evidence carries finite
    # floats. Closed ct.* schemas admit integers only.
    if canonical_bytes(value) != wire:
        refuse('SCHEMA_INVALID', 1, target + '#non_canonical')
    return value


# ---------------------------------------------------------- stage 2: structure

class Found:
    """Annotations collected during structural validation (not enforcement)."""

    def __init__(self):
        self.refs = []    # (path, ref, allowed_kinds, is_edge)
        self.roles = []   # (path, attestation, allowed_roles)

    def extend(self, other):
        self.refs.extend(other.refs)
        self.roles.extend(other.roles)


def _resolve(pointer):
    node = SCHEMAS
    for part in pointer[2:].split('/'):
        node = node[part]
    return node


_TYPES = {
    'object': lambda v: isinstance(v, dict),
    'array': lambda v: isinstance(v, list),
    'string': lambda v: isinstance(v, str),
    'integer': lambda v: isinstance(v, int) and not isinstance(v, bool),
    'boolean': lambda v: isinstance(v, bool),
    'null': lambda v: v is None,
}
_PATTERNS = {}


def _pattern(p):
    if p not in _PATTERNS:
        _PATTERNS[p] = re.compile(p[:-1] + r'\Z' if p.endswith('$') else p)
    return _PATTERNS[p]


def _same(a, b):
    return type(a) is type(b) and a == b


def _check(value, node, path, found):
    def bad():
        refuse('SCHEMA_INVALID', 2, path or '/')
    if '$ref' in node:
        _check(value, _resolve(node['$ref']), path, found)
    if 'allOf' in node:
        for sub in node['allOf']:
            _check(value, sub, path, found)
    if 'oneOf' in node:
        matches = []
        for sub in node['oneOf']:
            local = Found()
            try:
                _check(value, sub, path, local)
            except CheckedRefusal as e:
                if e.code != 'SCHEMA_INVALID':
                    raise
                continue
            matches.append(local)
        if len(matches) != 1:
            bad()
        found.extend(matches[0])
    if 'type' in node and not _TYPES[node['type']](value):
        bad()
    if 'const' in node and not _same(value, node['const']):
        bad()
    if 'enum' in node and not any(_same(value, e) for e in node['enum']):
        bad()
    if isinstance(value, str):
        if 'pattern' in node and not _pattern(node['pattern']).search(value):
            bad()
        if 'minLength' in node and len(value) < node['minLength']:
            bad()
        if 'maxLength' in node and len(value) > node['maxLength']:
            bad()
    if _TYPES['integer'](value):
        if 'minimum' in node and value < node['minimum']:
            bad()
        if 'maximum' in node and value > node['maximum']:
            bad()
    if isinstance(value, dict) and ('properties' in node or 'required' in node):
        props = node.get('properties', {})
        for key in node.get('required', []):
            if key not in value:
                bad()
        if node.get('additionalProperties') is False and set(value) - set(props):
            bad()
        for key, sub in props.items():
            if key in value:
                _check(value[key], sub, path + '/' + key, found)
    if isinstance(value, list):
        if 'minItems' in node and len(value) < node['minItems']:
            bad()
        if 'maxItems' in node and len(value) > node['maxItems']:
            bad()
        if node.get('uniqueItems') and len({canonical_bytes(v) for v in value}) != len(value):
            bad()
        if 'items' in node:
            for i, item in enumerate(value):
                _check(item, node['items'], f'{path}/{i}', found)
    if 'x-target' in node and isinstance(value, dict):
        found.refs.append((path, value, tuple(node['x-target']), node.get('x-edge', True) is not False))
    if 'x-allowed-roles' in node and isinstance(value, dict):
        found.roles.append((path, value, tuple(node['x-allowed-roles'])))


def validate(value, kind):
    """Stage 2 closed-schema check of a record of `kind`; returns annotations."""
    if kind not in SCHEMAS['records']:
        refuse('SCHEMA_INVALID', 2, '/schema')
    found = Found()
    _check(value, SCHEMAS['records'][kind], '', found)
    return found


def enforce_roles(found, target):
    """Stage 3: issuer-role enforcement from the per-kind allowed roles."""
    for path, attestation, allowed in found.roles:
        if attestation.get('role') not in allowed:
            refuse('ROLE_MISMATCH', 3, target + path + '/role')


# ------------------------------------------------------------------ numbers

def frac(r, target='/'):
    """Admit a canonical reduced rational whose denominator divides 10^6."""
    n, d = int(r['numerator']), int(r['denominator'])
    if gcd(abs(n), d) != 1 or 10 ** 6 % d != 0:
        refuse('RATIONAL_INVALID', 4, target)
    return Fraction(n, d)


def as_rational(x):
    x = Fraction(x)
    return {'numerator': str(x.numerator), 'denominator': str(x.denominator)}


def interval(i, target='/'):
    lo, hi = frac(i['lo'], target + '/lo'), frac(i['hi'], target + '/hi')
    if lo > hi:
        refuse('SCHEMA_INVALID', 4, target)
    return lo, hi


def decimal(s, target='/'):
    if s.startswith('-0') and Fraction(s) == 0:
        refuse('RATIONAL_INVALID', 4, target)
    value = Fraction(s)
    if not SCALAR_DOMAIN[0] <= value <= SCALAR_DOMAIN[1]:
        refuse('SCALAR_OUT_OF_ADMISSION_DOMAIN', 4, target)
    return value


def instant(s, target='/'):
    try:
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except ValueError:
        refuse('SCHEMA_INVALID', 4, target)


def window(w, target='/'):
    a, b = instant(w['from'], target + '/from'), instant(w['to'], target + '/to')
    if a > b:
        refuse('SCHEMA_INVALID', 4, target)
    return a, b
