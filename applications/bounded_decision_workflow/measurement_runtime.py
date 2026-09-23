"""Approved measurement command carriage and standalone semantic replay.

Only captured bytes enter the graph. All I/O is descriptor-relative, no-follow,
regular-file admitted on the maintained local filesystem boundary. No test hook,
caller computation, candidate discovery or synthetic witness is a public input.
"""
import base64
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import resource
import time
from . import retention
from .errors import WorkflowInputError
from .measurement_contracts import canonical_json_bytes, PROFILE
from .measurement_wire import Work, Graph, decode, fail, key, ref, sha, shape
from .measurement_compute import compute
from .measurement_build import identity

FILES=('invocation.json','closure.json','result.json','trace.json','build.json','policy.json','manifest.json')
CAPS=dict(zip(FILES,('invocation_bytes','closure_bytes','result_bytes','trace_bytes','build_bytes','object_bytes','manifest_bytes')))


def _read(fd,name,cap,work):
    def observe(event,unused):
        if event=='read':work.physical['read_operations']+=1
    try:
        item=retention._read_at(fd,name,cap,observe)
    except FileNotFoundError:fail('REQUIRED_REFERENCE_MISSING',name,'phase_2')
    # Check the pathname still names the captured inode, without reopening it.
    try:after=os.stat(name,dir_fd=fd,follow_symlinks=False)
    except FileNotFoundError:fail('INPUT_CHANGED_DURING_READ',name,'path')
    if retention._metadata(after)!=item.metadata:fail('INPUT_CHANGED_DURING_READ',name,'path')
    work.physical['bytes_read']+=len(item.data)
    return item.data


def read_path(path,dimension,work):
    absolute,parts=retention._parts(path)
    with retention._directory(absolute,parts[:-1]) as fd:
        retention._filesystem(fd)
        return _read(fd,parts[-1],work.limits[dimension],work)


def overrides(path,work):
    if path is None:return None
    wire=read_path(path,'invocation_bytes',work)
    value,_=decode(wire,work);Work(value)
    return value


def closure_wire(g,pin,limits):
    return canonical_json_bytes(dict(schema='nm.closure.v1',profile=PROFILE,invocation=g.root,
        authority_pin=pin,limits_override=limits,members=[dict(reference=ref(*k),encoding='base64',bytes=base64.b64encode(g.objects[k]).decode()) for k in sorted(g.objects)]))


def _build_check(iv,load,work):
    if iv.get('schema')!='nm.invocation.v1' or iv.get('profile')!=PROFILE:fail('PROFILE_MISMATCH','invocation','phase_1')
    build_ref=key(ref('nm.build.v1',iv.get('build_identity')))
    supplied=load(build_ref,work)
    actual=identity(work)
    if supplied!=actual or sha(actual)!=build_ref[1]:fail('BUILD_IDENTITY_MISMATCH','build_identity','phase_1')
    return actual


def _payloads(invocation,load,pin,limits,work):
    iv,_=decode(invocation,work)
    build_wire=_build_check(iv,load,work)
    graph=Graph(invocation,load,pin,work)
    closure=closure_wire(graph,pin,limits);work.high('closure_bytes',len(closure))
    result,trace=compute(graph)
    payloads={'invocation.json':invocation,'closure.json':closure,
              'result.json':canonical_json_bytes(result),'trace.json':canonical_json_bytes(trace),
              'build.json':build_wire,'policy.json':graph.objects[('nm.resource-policy.v1',iv['resource_policy'])]}
    for name,wire in payloads.items():work.guard(CAPS[name],len(wire))
    return payloads


def _preflight_output(output_dir):
    absolute,parts=retention._parts(output_dir)
    if not re.fullmatch(r'[a-z0-9][a-z0-9._-]{0,127}',parts[-1]):raise retention._error('OUTPUT_BASENAME_INVALID')
    with retention._directory(absolute,parts[:-1]) as fd:
        retention._filesystem(fd)
        try:os.stat(parts[-1],dir_fd=fd,follow_symlinks=False)
        except FileNotFoundError:pass
        else:raise retention._error('OUTPUT_COLLISION')


def publish(output_dir,payloads,work,started):
    absolute,parts=retention._parts(output_dir)
    _preflight_output(output_dir)
    # Reserve complete payloads plus the entire allowed manifest before create.
    total=sum(map(len,payloads.values()))
    work.guard('bundle_bytes',total+work.limits['manifest_bytes'])
    with retention._directory(absolute,parts[:-1]) as parent:
        retention._filesystem(parent)
        try:os.mkdir(parts[-1],0o700,dir_fd=parent)
        except FileExistsError:raise retention._error('OUTPUT_COLLISION')
        except OSError:raise retention._error('RETENTION_CREATE_FAILED')
        fd=os.open(parts[-1],os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
        try:
            inode=os.fstat(fd)
            def stable():
                current=os.stat(parts[-1],dir_fd=parent,follow_symlinks=False)
                if (current.st_dev,current.st_ino)!=(inode.st_dev,inode.st_ino):fail('INPUT_CHANGED_DURING_READ','output_dir','retention')
            stable()
            for name in FILES[:-1]:
                retention._write_file(fd,name,payloads[name],None)
                work.physical['write_operations']+=1;work.physical['bytes_written']+=len(payloads[name]);stable()
            physical=dict(bytes_read=work.physical['bytes_read']+work.physical.get('build_bytes_read',0),
                          read_operations=work.physical['read_operations']+work.physical.get('build_read_operations',0),
                          bytes_written=work.physical['bytes_written'],write_operations=work.physical['write_operations'],
                          elapsed_ns=time.monotonic_ns()-started,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                          status='observed_before_manifest_write')
            manifest=canonical_json_bytes(dict(schema='nm.bundle.v1',profile=PROFILE,completeness='complete',files=[dict(name=n,bytes=len(payloads[n]),sha256=sha(payloads[n])) for n in FILES[:-1]],physical=physical))
            work.guard('manifest_bytes',len(manifest));work.guard('bundle_bytes',total+len(manifest))
            retention._write_file(fd,'manifest.json',manifest,None);stable()
            os.fsync(fd);os.fsync(parent)
        finally:os.close(fd)
    return sha(manifest)


def receipt(operation,payloads,manifest):
    result=json.loads(payloads['result.json'])
    return dict(schema='nm.receipt.v1',operation=operation,evaluation_permitted=result['authority']['evaluation_permitted'],
                disposition=result['ranking']['disposition'],result_sha256=sha(payloads['result.json']),bundle_sha256=manifest)


def evaluate(invocation_file,objects_dir,authority_pin,output_dir,limits_file=None):
    started=time.monotonic_ns();pre=Work();limits=overrides(limits_file,pre);work=Work(limits);work.physical.update(pre.physical)
    _preflight_output(output_dir)
    invocation=read_path(invocation_file,'invocation_bytes',work)
    absolute,parts=retention._parts(objects_dir);captured={}
    with retention._directory(absolute,parts) as directory:
        retention._filesystem(directory)
        def load(k,w):
            if k not in captured:
                # Exact typed filename, never directory enumeration or fallback.
                kind,digest=key(ref(*k))
                if not re.fullmatch(r'nm\.[a-z-]+(?:\.v1)?',kind):fail('REFERENCE_ROLE_MISMATCH','kind','phase_2')
                cap=min(w.limits['object_bytes'],w.limits['capture_bytes']-sum(map(len,captured.values()))-len(invocation))
                if cap<0:fail('RESOURCE_LIMIT_EXCEEDED','capture_bytes','phase_2')
                captured[k]=_read(directory,digest+'.'+kind,cap,w)
            return captured[k]
        payloads=_payloads(invocation,load,authority_pin,limits,work)
    manifest=publish(output_dir,payloads,work,started)
    answer=receipt('measurement-evaluate',payloads,manifest);work.guard('receipt_bytes',len(canonical_json_bytes(answer))+1)
    return answer


def inspect_bundle(bundle_dir,work):
    absolute,parts=retention._parts(bundle_dir)
    payloads={}
    with retention._directory(absolute,parts) as directory:
        retention._filesystem(directory)
        names=set()
        with os.scandir(directory) as iterator:
            for entry in iterator:
                names.add(entry.name)
                if len(names)>7:fail('BUNDLE_INCOMPLETE','bundle','retention')
        if names!=set(FILES):fail('BUNDLE_INCOMPLETE','bundle','retention')
        total=0
        for name in ('manifest.json',)+FILES[:-1]:
            payloads[name]=_read(directory,name,min(work.limits[CAPS[name]],work.limits['bundle_bytes']-total),work)
            total+=len(payloads[name]);work.guard('bundle_bytes',total)
    manifest,_=decode(payloads['manifest.json'],work)
    shape(manifest,'schema profile completeness files physical','manifest')
    if manifest['schema']!='nm.bundle.v1' or manifest['profile']!=PROFILE or manifest['completeness']!='complete':fail('MANIFEST_INVALID','manifest','phase_1')
    if type(manifest['files']) is not list or [x.get('name') for x in manifest['files']]!=list(FILES[:-1]):fail('MANIFEST_INVALID','files','phase_1')
    for row in manifest['files']:
        shape(row,'name bytes sha256','manifest.files')
        wire=payloads[row['name']]
        if type(row['bytes']) is not int or row['bytes']!=len(wire) or row['sha256']!=sha(wire):fail('MANIFEST_COMMITMENT_MISMATCH',row['name'],'phase_1')
    return payloads


def recover(payloads,work):
    value,_=decode(payloads['closure.json'],work,transport=True)
    shape(value,'schema profile invocation authority_pin limits_override members','closure')
    if value['schema']!='nm.closure.v1' or value['profile']!=PROFILE:fail('PROFILE_MISMATCH','closure','phase_1')
    if type(value['members']) is not list:fail('SCHEMA_INVALID','members','phase_1')
    work.guard('unique_objects',len(value['members']))
    objects={};ordered=[];total=0
    for m in value['members']:
        shape(m,'reference encoding bytes','member');k=key(m['reference']);ordered.append(k)
        if m['encoding']!='base64' or type(m['bytes']) is not str:fail('SCHEMA_INVALID','member','phase_1')
        if len(m['bytes'])>4*((work.limits['object_bytes']+2)//3):fail('RESOURCE_LIMIT_EXCEEDED','object_bytes','phase_2')
        try:wire=base64.b64decode(m['bytes'],validate=True)
        except ValueError:fail('WIRE_INVALID','member','phase_1')
        if base64.b64encode(wire).decode()!=m['bytes']:fail('CANONICAL_FORM_REQUIRED','member','phase_1')
        total+=len(wire);work.guard('capture_bytes',total);work.guard('object_bytes',len(wire))
        if sha(wire)!=k[1]:fail('REFERENCE_DIGEST_MISMATCH','member','phase_2')
        objects[k]=wire;work.charge('recovery_bytes',len(wire))
    if ordered!=sorted(set(ordered)):fail('SCHEMA_INVALID','members','phase_1')
    if objects.get(key(value['invocation']))!=payloads['invocation.json']:fail('REFERENCE_DIGEST_MISMATCH','invocation','phase_2')
    iv,_=decode(payloads['invocation.json'],work)
    for name,k in [('build.json',('nm.build.v1',iv['build_identity'])),('policy.json',('nm.resource-policy.v1',iv['resource_policy']))]:
        if objects.get(k)!=payloads[name]:fail('REFERENCE_DIGEST_MISMATCH',name,'phase_2')
    return value,objects


def _retained(bundle_dir,limits_file=None):
    initial=Work();extra=overrides(limits_file,initial)
    payloads=inspect_bundle(bundle_dir,initial)
    closure,objects=recover(payloads,initial)
    retained=Work(closure['limits_override']);effective={k:min(v,retained.limits[k]) for k,v in (extra or {}).items()}
    # Preserve exact original override for semantic replay; stricter limits only
    # restrict work, never rewrite the retained invocation's policy context.
    merged=dict(closure['limits_override'] or {});merged.update(effective)
    work=Work(merged);work.physical.update(initial.physical)
    work.guard('bundle_bytes',sum(map(len,payloads.values())))
    def load(k,w):
        if k not in objects:fail('REQUIRED_REFERENCE_MISSING','required_closure','phase_2')
        return objects[k]
    return payloads,closure,objects,work,load


def verify(bundle_dir):
    payloads,closure,objects,work,load=_retained(bundle_dir)
    iv,_=decode(payloads['invocation.json'],work);_build_check(iv,load,work)
    graph=Graph(payloads['invocation.json'],load,closure['authority_pin'],work)
    if set(graph.objects)!=set(objects):fail('SCHEMA_INVALID','extraneous_closure_member','phase_2')
    # Public reconstruction/joins are integrity checks, not a fresh selection.
    from .measurement_compute import public_evidence
    for qk in graph.requests:
        q=graph.values[qk];public_evidence(graph.get(q['evidence']),q['context'],work)
    for name in ['result.json','trace.json']:decode(payloads[name],work)
    return receipt('measurement-verify',payloads,sha(payloads['manifest.json']))


def replay(bundle_dir,output_dir,limits_file=None):
    started=time.monotonic_ns();_preflight_output(output_dir)
    retained,closure,objects,work,load=_retained(bundle_dir,limits_file)
    computed=_payloads(retained['invocation.json'],load,closure['authority_pin'],closure['limits_override'],work)
    if computed['closure.json']!=retained['closure.json']:fail('SCHEMA_INVALID','required_closure','phase_2')
    for name in ['result.json','trace.json']:
        if computed[name]!=retained[name]:fail('REPLAY_SEMANTIC_MISMATCH',name,'phase_8')
    manifest=publish(output_dir,computed,work,started)
    answer=receipt('measurement-replay',computed,manifest);work.guard('receipt_bytes',len(canonical_json_bytes(answer))+1)
    return answer
