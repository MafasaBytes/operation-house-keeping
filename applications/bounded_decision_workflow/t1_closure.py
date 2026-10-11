"""Content-derived producer closure; provenance requires independent reconstruction.

Pure frozen-byte interfaces. Callers supply an already bounded, symlink-free
closed file inventory. A manifest assertion never grants reachability or a role.
"""
from dataclasses import dataclass
import json

from .t1_contracts import PROFILE, refuse, sha
from .t1_package import manifest_bytes, member_path
from .t1_records import parse
from .t1_oracle import evidence_identity_check

OPAQUE = 'ct.t1-opaque-bytes'
from .checked_runtime import BUNDLE_NAMES
PRIOR_NAMES = frozenset(BUNDLE_NAMES)
ROOT_LETTERS = {'target': 'J', 'execution_authority': 'E', 'permission': 'G',
                'receipt': 'receipt'}


@dataclass
class Closure:
    manifest: dict
    files: dict
    records: dict
    by_digest: dict
    prior_files: dict

    def get(self, reference):
        digest = reference['sha256']
        if digest not in self.records:
            refuse('SIM_REFERENCE_MISSING', 1, '/objects/' + digest)
        value = self.records[digest]
        if value.get('schema') != reference['kind']:
            refuse('SIM_REFERENCE_INVALID', 1, '/objects/' + digest)
        return value


def _json(wire, target):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                refuse('SIM_SCHEMA_INVALID', 0, target)
            result[key] = value
        return result
    try:
        return json.loads(wire, object_pairs_hook=pairs,
                          parse_constant=lambda _v: refuse('SIM_SCHEMA_INVALID', 0, target))
    except (ValueError, UnicodeError, TypeError, RecursionError):
        refuse('SIM_SCHEMA_INVALID', 0, target)


def _derive(files, roots):
    """Recompute closure without consulting submitted edges/roles/kinds."""
    paths = sorted(files)
    by_digest, values, kinds, annotations = {}, {}, {}, {}
    for path in paths:
        member_path(path)
        wire = files[path]
        if not isinstance(wire, bytes):
            raise TypeError('closure requires frozen bytes')
        digest = sha(wire)
        if digest in by_digest:
            refuse('SIM_REFERENCE_INVALID', 1, '/M/members')
        if path.startswith('objects/') and path != 'objects/' + digest:
            refuse('SIM_REFERENCE_INVALID', 1, '/M/members')
        by_digest[digest] = path
        if path.startswith('objects/') or path == 'receipt/receipt.json':
            value = _json(wire, '/' + path)
            if not isinstance(value, dict) or not isinstance(value.get('schema'), str):
                refuse('SIM_SCHEMA_INVALID', 0, '/' + path)
            kinds[digest] = value['schema']
            values[digest] = value
        elif path.startswith('evidence/public/'):
            value = _json(wire, '/' + path)
            if isinstance(value, dict) and value.get('schema') == 'nm.evidence.v1':
                kinds[digest], values[digest] = 'nm.evidence.v1', value
            else:
                kinds[digest] = OPAQUE
        else:
            kinds[digest] = OPAQUE
    for name in ('target', 'execution_authority', 'permission', 'receipt'):
        rr = roots[name]
        digest = rr['sha256']
        if digest not in by_digest:
            refuse('SIM_REFERENCE_MISSING', 1, '/' + ROOT_LETTERS[name])
        if kinds[digest] != rr['kind']:
            refuse('SIM_REFERENCE_INVALID', 1, '/' + ROOT_LETTERS[name])
    # Identify the prior exception through actual execution-target content,
    # never by submitted member roles or every manifest-shaped object present.
    target = values[roots['target']['sha256']]
    x_digest = target['execution_target']['sha256']
    if x_digest not in values:
        refuse('SIM_REFERENCE_MISSING', 1, '/J/execution_target')
    prior_digest = values[x_digest]['prior_selection']['manifest']['sha256']
    if prior_digest not in values:
        refuse('SIM_REFERENCE_MISSING', 1, '/X/prior_selection/manifest')
    prior = values[prior_digest]
    if prior.get('schema') != 'ct.bundle-manifest.v1':
        refuse('SIM_REFERENCE_INVALID', 1, '/X/prior_selection/manifest')
    entries = prior.get('files', [])
    if len(entries) != 8 or {item.get('name') for item in entries} != PRIOR_NAMES - {'manifest.json'}:
        refuse('SIM_REFERENCE_INVALID', 1, '/prior/manifest.json')
    prior_files = {'manifest.json': files[by_digest[prior_digest]]}
    prior_digests = {prior_digest}
    edges = set()
    for i, item in enumerate(entries):
        digest = item['sha256']
        if digest not in by_digest:
            refuse('SIM_REFERENCE_MISSING', 1, '/prior/' + item['name'])
        wire = files[by_digest[digest]]
        if len(wire) != item['bytes']:
            refuse('SIM_REFERENCE_INVALID', 1, '/prior/' + item['name'])
        prior_files[item['name']] = wire
        prior_digests.add(digest)
        edges.add((prior_digest, '/files/' + str(i) + '/sha256', digest))
    if len(prior_digests) != 9:
        refuse('SIM_REFERENCE_INVALID', 1, '/prior/manifest.json')
    # Every remaining schema-defined typed field is enumerated independently.
    missing = []
    for digest, path in sorted(by_digest.items(), key=lambda row: row[1]):
        if digest in prior_digests or kinds[digest] == OPAQUE:
            continue
        value, found = parse(files[path], kinds[digest], '/' + path)
        values[digest] = value
        annotations[digest] = found
        if not found:
            continue
        for pointer, rr, allowed, _edge_annotation in found.refs:
            if rr['kind'] not in allowed:
                refuse('SIM_REFERENCE_INVALID', 1, '/' + path + pointer)
            to = rr['sha256']
            edges.add((digest, pointer, to))
            if to not in by_digest:
                missing.append('/' + path + pointer)
            elif kinds[to] != rr['kind']:
                refuse('SIM_REFERENCE_INVALID', 1, '/' + path + pointer)
        for pointer, provenance, allowed in found.roles:
            if provenance['role'] not in allowed:
                refuse('SIM_REFERENCE_INVALID', 1, '/' + path + pointer + '/role')
    receipt_digest = roots['receipt']['sha256']
    receipt = values[receipt_digest]
    for key in ('server_info', 'printer_objects'):
        to = receipt['raw_response_digests'][key]
        edges.add((receipt_digest, '/raw_response_digests/' + key, to))
        if to not in by_digest:
            missing.append('/receipt/raw_response_digests/' + key)
        elif kinds[to] != OPAQUE:
            refuse('SIM_REFERENCE_INVALID', 1, '/receipt/raw_response_digests/' + key)
    if missing:
        refuse('SIM_REFERENCE_MISSING', 1, sorted(missing)[0])
    adjacency = {}
    for source, _pointer, destination in edges:
        adjacency.setdefault(source, set()).add(destination)
    reached, pending = set(), [rr['sha256'] for rr in roots.values()]
    while pending:
        digest = pending.pop()
        if digest in reached:
            continue
        reached.add(digest)
        pending.extend(adjacency.get(digest, ()))
    free = sorted(set(by_digest) - reached)
    if free:
        refuse('SIM_REFERENCE_INVALID', 1, '/objects/' + free[0])
    for key, root_name in (('target', 'target'), ('permission', 'permission'),
                           ('execution_authority', 'execution_authority')):
        if receipt[key] != roots[root_name]:
            refuse('SIM_REFERENCE_INVALID', 1, '/receipt/' + key)
    for key in ('world', 'context', 'execution_target', 'rule', 'simulator_policy',
                'captured_policy', 'producer_build'):
        if receipt[key] != target[key]:
            refuse('SIM_REFERENCE_INVALID', 1, '/receipt/' + key)
    # Classify outputs by their prescribed retained path and intrinsic record
    # identity, then independently compare inventory/digest arrays at order 7.6.
    expected_roles = {}
    reference_roles = [('public_evidence', receipt['public_evidence'], 'evidence/public/'),
                       ('snapshot', receipt['evidence']['snapshot'], 'evidence/public/'),
                       ('run_result', receipt['evidence']['run_result'], 'evidence/run/'),
                       ('projection_report', receipt['evidence']['projection_report'], 'evidence/projection/')]
    for role, rr, prefix in reference_roles:
        digest = rr['sha256']
        if not by_digest[digest].startswith(prefix):
            refuse('SIM_REFERENCE_INVALID', 1, '/M/members')
        expected_roles[digest] = role
    for key in ('wall_clock', 'monotonic', 'transport'):
        digest = receipt['transcripts'][key]['sha256']
        if by_digest[digest] != 'evidence/transcripts/' + key:
            refuse('SIM_REFERENCE_INVALID', 1, '/M/members')
        expected_roles[digest] = 'transcript'
    for key in ('server_info', 'printer_objects'):
        digest = receipt['raw_response_digests'][key]
        if not by_digest[digest].startswith('evidence/raw/'):
            refuse('SIM_REFERENCE_INVALID', 1, '/M/members')
        expected_roles[digest] = 'raw_body'
    for digest, path in by_digest.items():
        if digest in prior_digests:
            role = 'prior_bundle_file'
        elif path.startswith('objects/'):
            role = 'baseline_evidence' if kinds[digest] == 'nm.evidence.v1' else 'input_record'
        elif path == 'receipt/receipt.json':
            if digest != receipt_digest:
                refuse('SIM_REFERENCE_INVALID', 1, '/receipt')
            role = 'producer_receipt'
        elif digest in expected_roles:
            role = expected_roles[digest]
        elif path.startswith('evidence/raw/envelope-') and path.endswith('.json'):
            value = _json(files[path], '/' + path)
            if path != 'evidence/raw/envelope-' + value.get('record_id', '') + '.json':
                refuse('SIM_REFERENCE_INVALID', 1, '/M/members')
            role = 'raw_envelope'
        elif path.startswith('evidence/attempts/') and path.endswith('.json'):
            value = _json(files[path], '/' + path)
            if path != 'evidence/attempts/' + value.get('attempt_id', '') + '.json':
                refuse('SIM_REFERENCE_INVALID', 1, '/M/members')
            role = 'attempt_record'
        elif path.startswith('evidence/extraction/') and path.endswith('.json'):
            value = _json(files[path], '/' + path)
            if path != 'evidence/extraction/' + value.get('raw_record_id', '') + '.json':
                refuse('SIM_REFERENCE_INVALID', 1, '/M/members')
            role = 'extraction_result'
        elif path.startswith('evidence/query/'):
            role = 'logical_query_result'
        elif path.startswith('evidence/db/'):
            role = 'temporal_db_diagnostic'
        else:
            refuse('SIM_REFERENCE_INVALID', 1, '/M/members')
        expected_roles[digest] = role
    members = [{'bytes': len(files[path]), 'kind': kinds[digest], 'path': path,
                'role': expected_roles[digest], 'sha256': digest}
               for digest, path in sorted(by_digest.items(), key=lambda row: row[1])]
    edge_records = [{'from': a, 'field': b, 'to': c} for a, b, c in sorted(edges)]
    return members, edge_records, values, by_digest, prior_files


def build_manifest(files, roots):
    """Return cap-bound M bytes; successful publication is a separate operation."""
    members, edges, _values, _index, _prior = _derive(files, roots)
    value = {'schema': 'ct.t1-producer-manifest.v1', 'profile': PROFILE,
             'roots': roots, 'members': members, 'edges': edges}
    wire = manifest_bytes(value)
    parse(wire, value['schema'], '/M')
    return wire


def inspect_package(manifest_wire, files, *, manifest_pin):
    """Order-1 closure; caller retains external J/E/G pins and checks orders 2–9.

    This does not claim operating-system publication history, semantic raw
    reconstruction, independent owning validation, or scratch reconstruction.
    """
    if 'PARTIAL' in files:
        refuse('SIM_PUBLICATION_INCOMPLETE', 1, '/M', 5)
    manifest, _found = parse(manifest_wire, 'ct.t1-producer-manifest.v1', '/M')
    if sha(manifest_wire) != manifest_pin:
        refuse('SIM_PIN_MISMATCH', 1, '/M')
    retained = dict(files)
    if 'manifest.json' in retained:
        if retained.pop('manifest.json') != manifest_wire:
            refuse('SIM_REFERENCE_INVALID', 1, '/M')
    members, edges, values, index, prior = _derive(retained, manifest['roots'])
    actual = manifest['members']
    if len(actual) != len(members):
        refuse('SIM_REFERENCE_INVALID', 1, '/M/members')
    for i, (submitted, expected) in enumerate(zip(actual, members)):
        for key in ('path', 'sha256', 'bytes', 'kind'):
            if submitted[key] != expected[key]:
                refuse('SIM_REFERENCE_INVALID', 1, '/M/members/' + str(i))
    if len(manifest['edges']) != len(edges):
        refuse('SIM_REFERENCE_INVALID', 1, '/M/edges')
    for i, (submitted, expected) in enumerate(zip(manifest['edges'], edges)):
        if submitted != expected:
            refuse('SIM_REFERENCE_INVALID', 1, '/M/edges/' + str(i))
    for i, (submitted, expected) in enumerate(zip(actual, members)):
        if submitted['role'] != expected['role']:
            refuse('SIM_REFERENCE_INVALID', 1, '/M/members/' + str(i) + '/role')
    evidence_identity_check([('/O' if member['role'] == 'public_evidence' else '/' + member['path'],
                              retained[member['path']])
                             for member in members if member['kind'] == 'nm.evidence.v1'],
                            receipt_digest=manifest['roots']['receipt']['sha256'])
    return Closure(manifest, retained, values, index, prior)
