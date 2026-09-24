"""Versioned governed file boundary. Verification is integrity, never permission.

Reuse Linux no-follow, exclusive rename and fsync primitives without changing
legacy file budgets or formats. No auto-restore, migration, overwrite or cleanup.
"""
from datetime import UTC, datetime
import json
import os
import re
from types import MappingProxyType

from . import retention, governed_review, governed_build
from .governed_closure import CAPS, FILES, validate_carried, schemas, shape, decode_file, incompatible
from .governed_resources import Budget, bounded_json, problem
from .governed_admission import H
from .input import canonical_json_bytes as C
from .build import LOCK,PUBLIC
from .errors import refusal


def _build_edition(edition):
    if edition=='governed-executable-build.v1':
        return 'application_source_sha256',governed_build.V1_SCHEMA,governed_build.CONTRACTS_V1
    if edition=='governed-executable-build.v2':
        return 'application_source_inventory_sha256',governed_build.V2_SCHEMA,governed_build.CONTRACTS
    raise incompatible()


def _build_record(wire,budget):
    """Historical record shape/policy, NOT availability of that executable."""
    v1_path=governed_build.V1_SCHEMA;v2_path=governed_build.V2_SCHEMA
    try:
        with (governed_build.ROOT/v1_path).open('rb') as f:v1_wire=f.read(65537)
        with (governed_build.ROOT/v2_path).open('rb') as f:v2_wire=f.read(65537)
        with (governed_build.ROOT/LOCK).open('rb') as f:lock=f.read(4097)
    except OSError as e:raise governed_build.unavailable() from e
    if (H(v1_wire)!=governed_build.CONTRACTS_V1[v1_path] or
        H(v2_wire)!=governed_build.CONTRACTS[v2_path] or
        H(lock)!='7c87f0d7a3f12c271311cc0c33e59025e0161c37f16336901a0764b4330c0817'):
        raise governed_build.unavailable()
    v=decode_file(wire,'build.json',budget,schemas(),extra=True)
    source_field,schema_path,expected_contracts=_build_edition(v.get('schema'))
    schema_wire=v1_wire if schema_path==v1_path else v2_wire
    if not shape(v,json.loads(schema_wire),{}):raise retention._error('MANIFEST_INVALID')
    if (v['contract_source_sha256']!=expected_contracts or
        v['policy_file_sha256']!=governed_build.POLICY_SHA or
        v['limit_policy_sha256']!=H(C(dict(budget.caps))) or
        v['dependency_lock_sha256']!=H(lock) or
        v['dependencies']!=dict(line.split('==') for line in lock.decode().splitlines()) or
        set(v['public_module_sha256'])!=set(PUBLIC)):
        raise governed_build.unavailable()
    if source_field=='application_source_sha256':
        for p in v[source_field]:
            if not p.startswith('applications/') or any(x in ('','.','..') for x in p.split('/')):
                raise retention._error('MANIFEST_INVALID')
    if budget.observer:
        try:budget.observer({'phase':'retained_build_contract','files':3,'bytes':len(v1_wire)+len(v2_wire)+len(lock),
                            'coverage':'edition_dispatched_record_shape_and_pinned_contract_not_executable_availability'})
        except Exception as e:
            raise refusal('INTERNAL_ERROR',stage='internal_failure',target='instrumentation',retry='investigate',exit_code=7) from e


def output_parent(path):
    absolute,parts=retention._parts(path)
    if re.fullmatch(r'[a-z0-9][a-z0-9._-]{0,127}',parts[-1]) is None:
        raise retention._error('OUTPUT_BASENAME_INVALID')
    with retention._directory(absolute,parts[:-1]) as fd:retention._filesystem(fd)
    return absolute,parts


def stable_inventory(fd,expected,cap,fault=None):
    """A bounded second snapshot: timestamps can alias within one clock tick.

    This does not promise continuous monitoring after capture. The fixed file
    count bounds each scan independently; no recursive directory traversal.
    """
    retention._event(fault,'inventory_recheck','captured_directory')
    final=set()
    with os.scandir(fd) as it:
        for e in it:
            if len(final)>=cap:raise retention._error('INPUT_CHANGED_DURING_READ')
            final.add(e.name)
    if final!=set(expected):raise retention._error('INPUT_CHANGED_DURING_READ')


def capture_bundle(path, *, fault=None, observer=None, _budget=None):
    """Capture fixed files once, bounded before reads. No semantic evaluation."""
    budget=_budget if _budget is not None else Budget(observer=observer);absolute,parts=retention._parts(path)
    files={};digests={};total=0
    with retention._directory(absolute,parts) as fd:
        retention._filesystem(fd);entries=set();before=retention._metadata(os.fstat(fd))
        with os.scandir(fd) as it:
            for e in it:
                if len(entries)>=budget.caps['files_per_bundle']:raise retention._error('MANIFEST_INVALID')
                entries.add(e.name)
        if entries!=set(CAPS):raise retention._error('BUNDLE_INCOMPLETE')
        for name in ['manifest.json']+sorted(FILES):
            cap=min(budget.caps[CAPS[name]],budget.caps['retention_bytes']-total)
            try:captured=retention._read_at(fd,name,cap,fault)
            except FileNotFoundError as e:raise retention._error('BUNDLE_INCOMPLETE') from e
            files[name]=captured.data;digests[name]=captured.sha256;total+=len(captured.data)
        stable_inventory(fd,entries,budget.caps['files_per_bundle'],fault)
        if retention._metadata(os.fstat(fd))!=before:raise retention._error('INPUT_CHANGED_DURING_READ')
    # Owning closure validation decodes payloads once later. This adapter only
    # inspects the bounded manifest and fixed inventory; never a validated flag.
    defs=schemas();m=decode_file(files['manifest.json'],'manifest.json',budget,defs,extra=True)
    for name,entry in m['files'].items():
        if entry!={'bytes':len(files[name]),'sha256':digests[name]}:raise retention._error('MANIFEST_INVALID')
    if m['build_identity']!=digests['build.json'] or m['semantic_commitments']!={n:digests[n] for n in ('result.json','trace.json')}:
        raise retention._error('MANIFEST_INVALID')
    _build_record(files['build.json'],budget)
    try:
        if datetime.fromisoformat(m['run_metadata']['created_at_utc']).utcoffset()!=UTC.utcoffset(None):raise ValueError()
    except ValueError as e:raise retention._error('MANIFEST_INVALID') from e
    return retention.BundleInspection('complete_bundle','complete','not_established_by_verification',
        MappingProxyType(files),None,digests['manifest.json'])


def verify(path, *, fault=None, observer=None):
    budget=Budget(observer=observer)
    checked=capture_bundle(path,fault=fault,observer=observer,_budget=budget)
    validate_carried(dict(checked.captured),expected_manifest=checked.manifest_sha256,
        expected_build=checked.captured['build.json'],budget=budget,replay_root=True)
    return checked


def publish(path,review,*,operation='evaluate',fault=None,observer=None):
    """Publish a completed kernel assessment; publication itself grants no permission."""
    absolute,parts=output_parent(path);budget=Budget(observer=observer)
    if operation not in ('evaluate','replay'):raise retention._error('MANIFEST_INVALID')
    # Reservation includes all future file construction and manifest publication.
    budget.work('retention_bytes',budget.caps['retention_bytes'],scope='publication_reservation')
    z=json.loads(review.closure_bytes);table=z['objects']
    iv=table[z['invocation']['sha256']]['canonical_json'];s=table[iv['scenario']['sha256']]['canonical_json']
    requested=table[s['request']['sha256']]['canonical_json']['requested_limits'] or {}
    retention_cap=min(budget.caps['retention_bytes'],requested.get('retention_bundle_bytes',budget.caps['retention_bytes']))
    files={'request.json':bounded_json(iv,budget.caps['request_wire_bytes'],'request_wire_bytes'),
           'snapshot.json':bounded_json(table[s['snapshot']['sha256']]['canonical_json'],budget.caps['snapshot_wire_bytes'],'snapshot_wire_bytes'),
           'resolved-input.json':review.closure_bytes,'result.json':review.result_bytes,'trace.json':review.trace_bytes,
           'build.json':bounded_json(table[iv['build_identity']]['canonical_json'],budget.caps['build_bytes'],'build_bytes')}
    raw=json.loads(review.physical_bytes)
    logical=json.loads(review.result_bytes)['resource_accounting']
    aliases={'lower_charges':'review_resolution_charges','lower_references':'review_reference_occurrences',
             'lower_resolved_bytes':'review_resolved_bytes'}
    # Additional publication checks are positive work in the same operation,
    # not an independent allowance that can conceal an aggregate overflow.
    for n,v in raw['charged'].items():
        k=aliases.get(n,n)
        budget.logical[k]=logical[n];budget.actual[k]=raw['actual'][n];budget.extra[k]=raw['extra'][n]
        if v!=logical[n]+raw['extra'][n] or raw['actual'][n]>v or v>budget.caps[k]:
            raise problem('HISTORY_INCOMPATIBLE')
    budget.work('context_bytes',sum(map(len,files.values())),scope='publication_validation',extra=True)
    defs=schemas()
    for n,b in files.items():decode_file(b,n,budget,defs,extra=True)
    for n in raw['charged']:
        k=aliases.get(n,n)
        raw['actual'][n]=budget.actual[k];raw['extra'][n]=budget.extra[k];raw['charged'][n]=budget.logical[k]+budget.extra[k]
    work={'schema':'physical-work.v1','observed':True,'logical_commitment':raw['logical_commitment'],
          'actual':raw['actual'],'extra':raw['extra'],'charged':raw['charged'],'cache_hits':raw['cache_hits'],
          'output_reserved_bytes':retention_cap,
          'coverage':'through_payloads_manifest_publication_reserved','checks':'all_effective_limits_checked_before_work'}
    bounded_json(work,budget.caps['physical_evidence_bytes'],'physical_evidence_bytes')
    with retention._directory(absolute,parts[:-1]) as parent:
        fs=retention._filesystem(parent)
        m={'schema_version':'governed-bundle.v2','bundle_kind':'complete','operation':operation,
           'build_identity':H(files['build.json']),'files':{n:{'bytes':len(b),'sha256':H(b)} for n,b in files.items()},
           'semantic_commitments':{n:H(files[n]) for n in ('result.json','trace.json')},
           'run_metadata':{'created_at_utc':datetime.now(UTC).isoformat(),'filesystem':fs,'operation_work':work}}
        mw=bounded_json(m,budget.caps['manifest_bytes'],'manifest_bytes')
        if not shape(m,defs['manifest'],defs):raise retention._error('MANIFEST_INVALID')
        if sum(map(len,files.values()))+len(mw)>retention_cap:raise retention._error('OUTPUT_LIMIT_EXCEEDED')
        try:
            retention._event(fault,'directory_create',parts[-1]);os.mkdir(parts[-1],0o700,dir_fd=parent)
        except FileExistsError as e:raise retention._error('OUTPUT_COLLISION') from e
        except OSError as e:raise retention._error('RETENTION_CREATE_FAILED',state='absent') from e
        fd=None
        try:
            fd=os.open(parts[-1],os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
            os.fchmod(fd,0o700)
            for n in FILES:retention._write_file(fd,n,files[n],fault)
            retention._write_file(fd,'manifest.json',mw,fault)
            for event,descriptor,code in [('directory_fsync',fd,'RETENTION_DIR_FSYNC_FAILED'),('parent_fsync',parent,'RETENTION_PARENT_FSYNC_FAILED')]:
                try:retention._event(fault,event,parts[-1]);os.fsync(descriptor)
                except OSError as e:raise retention._error(code) from e
        except OSError as e:raise retention._error('RETENTION_CREATE_FAILED') from e
        finally:
            if fd is not None:os.close(fd)
    files['manifest.json']=mw
    return retention.BundleInspection('complete_bundle','complete','fsync_sequence_returned',MappingProxyType(files),None,H(mw))


def replay(path,output,*,fault=None,observer=None):
    output_parent(output)
    budget=governed_review._ReplayBudget(observer=observer)
    checked=capture_bundle(path,fault=fault,observer=observer,_budget=budget)
    review=governed_review._replay(dict(checked.captured),budget,observer)
    return publish(output,review,operation='replay',fault=fault,observer=observer)
