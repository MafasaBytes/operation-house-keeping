"""Closed v3 schemas with whole-string patterns and typed annotations.

No JSON Schema annotation is mistaken for a semantic permission check.
"""
import re
from math import gcd
from .t1_contracts import SCHEMAS, canonical_bytes, refuse, SimRefusal


class Found:
    def __init__(self):
        self.refs, self.roles = [], []

    def extend(self, other):
        self.refs.extend(other.refs)
        self.roles.extend(other.roles)


def _resolve(pointer, schema_pack):
    node = schema_pack
    for part in pointer[2:].split('/'):
        node = node[part]
    return node


def _same(a, b):
    # JSON semantic equality except Boolean must not masquerade as integer.
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    return a == b


def _check(value, node, path, found, schema_pack):
    def bad(target=None):
        refuse('SIM_SCHEMA_INVALID', 0, path if target is None else target)
    if '$ref' in node:
        _check(value, _resolve(node['$ref'], schema_pack), path, found, schema_pack)
    for sub in node.get('allOf', []):
        _check(value, sub, path, found, schema_pack)
    for combinator in ('oneOf', 'anyOf'):
        if combinator not in node:
            continue
        matches = []
        for sub in node[combinator]:
            local = Found()
            try:
                _check(value, sub, path, local, schema_pack)
            except SimRefusal as error:
                if error.code != 'SIM_SCHEMA_INVALID':
                    raise
            else:
                matches.append(local)
        if not matches or (combinator == 'oneOf' and len(matches) != 1):
            if isinstance(value, dict) and 'same_referent' in value and 'theta_in_interval' in value:
                bad(path + '/theta_in_interval')
            bad()
        found.extend(matches[0])
    types = {'object': isinstance(value, dict), 'array': isinstance(value, list),
             'integer': type(value) is int, 'number': type(value) in (int, float),
             'string': isinstance(value, str), 'boolean': type(value) is bool, 'null': value is None}
    if 'type' in node:
        choices = node['type'] if isinstance(node['type'], list) else [node['type']]
        if not any(types[choice] for choice in choices):
            bad()
    if 'const' in node and not _same(value, node['const']):
        bad()
    if 'enum' in node and not any(_same(value, x) for x in node['enum']):
        bad()
    if isinstance(value, str):
        if 'pattern' in node and re.fullmatch(node['pattern'], value) is None:
            bad()
        if len(value) < node.get('minLength', 0) or len(value) > node.get('maxLength', len(value)):
            bad()
    if type(value) in (int, float):
        if value < node.get('minimum', value) or value > node.get('maximum', value):
            bad()
    if isinstance(value, dict):
        props = node.get('properties', {})
        if any(k not in value for k in node.get('required', [])):
            bad()
        extra = sorted(set(value) - set(props))
        if node.get('additionalProperties') is False and extra:
            bad(path + '/' + extra[0])
        for key, child in props.items():
            if key in value:
                _check(value[key], child, path + '/' + key, found, schema_pack)
        if isinstance(node.get('additionalProperties'), dict):
            for key in extra:
                _check(value[key], node['additionalProperties'], path + '/' + key, found, schema_pack)
        if node.get('x-semantic') == 'reduced; denominator divides 1000000':
            numerator, denominator = int(value['numerator']), int(value['denominator'])
            if gcd(abs(numerator), denominator) != 1 or 1000000 % denominator:
                bad()
    if isinstance(value, list):
        if len(value) < node.get('minItems', 0) or len(value) > node.get('maxItems', len(value)):
            bad()
        if node.get('uniqueItems') and len({canonical_bytes(x) for x in value}) != len(value):
            bad()
        for i, item in enumerate(value):
            if 'items' in node:
                _check(item, node['items'], f'{path}/{i}', found, schema_pack)
    if 'x-target' in node and isinstance(value, dict):
        found.refs.append((path, value, tuple(node['x-target']), node.get('x-edge', True)))
    if 'x-allowed-roles' in node and isinstance(value, dict):
        found.roles.append((path, value, tuple(node['x-allowed-roles'])))


def validate(value, kind, target='/', *, schema_pack=SCHEMAS):
    if kind not in schema_pack['records']:
        refuse('SIM_SCHEMA_INVALID', 0, target + '/schema')
    found = Found()
    _check(value, schema_pack['records'][kind], target.rstrip('/'), found, schema_pack)
    return found
