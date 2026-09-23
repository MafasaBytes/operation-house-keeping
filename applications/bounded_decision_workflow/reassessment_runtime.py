"""Reassessment delivery from captured bytes, with independent semantic replay.

No supplied computation, callback, discovery, build assertion or synthetic seam.
Historical selector bundles remain inputs, never claims of old-build execution.
"""
import base64
import json
import os
import re
import resource
import time
from datetime import datetime
from . import retention, reassessment_build
from .measurement_contracts import canonical_json_bytes, APPROVED_POLICY_SHA
from .measurement_wire import Work, decode, sha, ref, fail, shape, bounded_json, BUNDLE_STATE
from .measurement_runtime import _read
from .reassessment_capture import capture, _Captured
from .reassessment_contracts import PROFILE, FILES, CAPS, typed, validate
from .reassessment_admission import admit
from .reassessment_compute import compute
from .reassessment_output_shapes import SCHEMAS


def _filesystem(fd):
    if retention._filesystem(fd)!='ext4':raise retention._error('FILESYSTEM_UNSUPPORTED')


def _stable(path, inode):
    # Internal parent of a valid single-component relative filename.
    absolute,parts=(False,[]) if path=='.' else retention._parts(path)
    with retention._directory(absolute,parts) as fd:
        now=os.fstat(fd)
        if (inode.st_dev,inode.st_ino)!=(now.st_dev,now.st_ino):
            fail('INPUT_CHANGED_DURING_READ','/directory','path')


def overrides(path,work):
    if path is None:return None
    absolute,parts=retention._parts(path)
    with retention._directory(absolute,parts[:-1]) as fd:
        _filesystem(fd);before=os.fstat(fd)
        raw=_read(fd,parts[-1],work.limits['invocation_bytes'],work,'invocation_bytes')
        _stable(os.path.dirname(os.fspath(path)) or '.',before)
    value,_=decode(raw,work);Work(value)
    return value

def _preflight_output(output_dir):
    absolute,parts=retention._parts(output_dir)
    if not re.fullmatch(r'[a-z0-9][a-z0-9._-]{0,127}',parts[-1]):raise retention._error('OUTPUT_BASENAME_INVALID')
    with retention._directory(absolute,parts[:-1]) as fd:
        _filesystem(fd)
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
        _filesystem(parent)
        parent_inode=os.fstat(parent)
        try:os.mkdir(parts[-1],0o700,dir_fd=parent)
        except FileExistsError:raise retention._error('OUTPUT_COLLISION')
        except OSError:raise retention._error('RETENTION_CREATE_FAILED')
        BUNDLE_STATE.set('incomplete')
        fd=os.open(parts[-1],os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
        try:
            inode=os.fstat(fd)
            def stable():
                _stable(os.path.dirname(os.fspath(output_dir)) or '.',parent_inode)
                current=os.stat(parts[-1],dir_fd=parent,follow_symlinks=False)
                if (current.st_dev,current.st_ino)!=(inode.st_dev,inode.st_ino):fail('INPUT_CHANGED_DURING_READ','output_dir','retention')
            stable()
            for name in FILES[:-1]:
                retention._write_file(fd,name,payloads[name],None,io=work.io)
                stable()
            physical=dict(bytes_read=work.physical['bytes_read']+work.physical.get('build_bytes_read',0),
                          read_operations=work.physical['read_operations']+work.physical.get('build_read_operations',0),
                          bytes_written=work.physical['bytes_written'],write_operations=work.physical['write_operations'],
                          elapsed_ns=time.monotonic_ns()-started,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                          status='observed_before_manifest_write')
            manifest=bounded_json(dict(schema='nr.bundle.v2',profile=PROFILE,completeness='complete',files=[dict(name=n,bytes=len(payloads[n]),sha256=sha(payloads[n],work)) for n in FILES[:-1]],physical=physical),work,'manifest_bytes')
            work.guard('manifest_bytes',len(manifest));work.guard('bundle_bytes',total+len(manifest))
            retention._write_file(fd,'manifest.json',manifest,None,io=work.io);stable()
            BUNDLE_STATE.set('complete_visible_durability_unknown')
            try:os.fsync(fd)
            except OSError:raise retention._error('RETENTION_DIR_FSYNC_FAILED')
            try:os.fsync(parent)
            except OSError:raise retention._error('RETENTION_PARENT_FSYNC_FAILED')
        finally:os.close(fd)
    return sha(manifest,work)


def inspect_bundle(bundle_dir,work):
    absolute,parts=retention._parts(bundle_dir)
    payloads={}
    with retention._directory(absolute,parts) as directory:
        _filesystem(directory)
        inode=os.fstat(directory)
        names=set()
        with os.scandir(directory) as iterator:
            for entry in iterator:
                names.add(entry.name)
                if len(names)>7:fail('BUNDLE_INCOMPLETE','bundle','phase_1')
        if names!=set(FILES):fail('BUNDLE_INCOMPLETE','bundle','phase_1')
        total=0
        for name in ('manifest.json',)+FILES[:-1]:
            cap=min(work.limits[CAPS[name]],work.limits['bundle_bytes']-total)
            dimension='bundle_bytes' if cap<work.limits[CAPS[name]] else CAPS[name]
            payloads[name]=_read(directory,name,cap,work,dimension,total if dimension=='bundle_bytes' else 0)
            total+=len(payloads[name]);work.guard('bundle_bytes',total)
        _stable(bundle_dir,inode)
    manifest,_=decode(payloads['manifest.json'],work)
    _output(manifest,'nr.bundle.v2')
    shape(manifest,'schema profile completeness files physical','manifest')
    if manifest['schema']!='nr.bundle.v2' or manifest['profile']!=PROFILE or manifest['completeness']!='complete':fail('MANIFEST_INVALID','manifest','phase_1')
    if type(manifest['files']) is not list or [x.get('name') for x in manifest['files']]!=list(FILES[:-1]):fail('MANIFEST_INVALID','files','phase_1')
    for row in manifest['files']:
        shape(row,'name bytes sha256','manifest.files')
        wire=payloads[row['name']]
        if type(row['bytes']) is not int or row['bytes']!=len(wire) or row['sha256']!=sha(wire,work):fail('MANIFEST_COMMITMENT_MISMATCH',row['name'],'phase_1')
    return payloads


def _matches(v,s):
    if 'anyOf' in s:return any(_matches(v,x) for x in s['anyOf'])
    types=dict(object=dict,array=list,string=str,integer=int,boolean=bool,null=type(None))
    if 'type' in s and type(v) is not types[s['type']]:return False
    if 'const' in s and v!=s['const']:return False
    if 'enum' in s and v not in s['enum']:return False
    if 'pattern' in s and re.search(s['pattern'],v) is None:return False
    if 'minimum' in s and v<s['minimum']:return False
    if 'maximum' in s and v>s['maximum']:return False
    if s.get('format')=='date-time':
        try:
            if datetime.fromisoformat(v).utcoffset() is None:return False
        except (ValueError,TypeError):return False
    if type(v) is dict:
        if not set(s.get('required',[]))<=set(v):return False
        if s.get('additionalProperties') is False and not set(v)<=set(s['properties']):return False
        return all(_matches(x,s.get('properties',{}).get(k,{})) for k,x in v.items())
    if type(v) is list:return all(_matches(x,s.get('items',{})) for x in v)
    return True


def _output(v,kind):
    if type(v) is not dict:fail('SCHEMA_INVALID','/retained/'+kind,'phase_1')
    if v.get('schema')!=kind or v.get('profile')!=PROFILE:fail('PROFILE_MISMATCH','/retained/'+kind,'phase_1')
    if not _matches(v,SCHEMAS[kind]):fail('SCHEMA_INVALID','/retained/'+kind,'phase_1')


def _receipt(operation,payloads,manifest):
    r=json.loads(payloads['result.json'])
    return dict(schema='nr.receipt.v2',operation=operation,evaluation_permitted=r['authority']['permission']=='true',
        disposition=r['summary']['disposition'],result_sha256=sha(payloads['result.json']),bundle_sha256=manifest)


def _payloads(g):
    result,trace=compute(g);w=g.work
    payloads={'invocation.json':g.objects[typed(g.root)],'closure.json':g.closure_bytes,
        'result.json':bounded_json(result,w,'result_bytes'),'trace.json':bounded_json(trace,w,'trace_bytes'),
        'build.json':g.objects[typed(g.invocation['build'])],'policy.json':g.objects[typed(g.invocation['resource_policy'])]}
    for n,b in payloads.items():w.guard(CAPS[n],len(b))
    return payloads


def _deliver(operation,payloads,output_dir,work,started):
    answer=_receipt(operation,payloads,'0'*64)
    work.guard('receipt_bytes',len(canonical_json_bytes(answer))+1)
    answer['bundle_sha256']=publish(output_dir,payloads,work,started)
    return answer


def evaluate(invocation_file,objects_dir,authority_pin,output_dir,limits_file=None):
    started=time.monotonic_ns();pre=Work();limits=overrides(limits_file,pre)
    _preflight_output(output_dir)
    g=capture(invocation_file,objects_dir,authority_pin,limits)
    for k,v in pre.physical.items():g.work.physical[k]=g.work.physical.get(k,0)+v
    return _deliver('reassessment-evaluate',_payloads(g),output_dir,g.work,started)


class _SemanticWork(Work):
    """Canonical evaluation counts, with recovery work also charged to total guards."""
    def __init__(self,limits,total):
        super().__init__(limits);self.total=total;self.physical=total.physical
    def charge(self,k,n=1):
        self.total.charge(k,n);super().charge(k,n)
    def high(self,k,n):
        self.total.high(k,n);super().high(k,n)


def _retained(bundle_dir,limits_file=None):
    pre=Work();extra=overrides(limits_file,pre);initial=Work(extra);initial.physical.update(pre.physical)
    payloads=inspect_bundle(bundle_dir,initial)
    c,_=decode(payloads['closure.json'],initial,transport=True)
    shape(c,'schema profile invocation authority_pin limits_override members','/closure')
    if c['schema']!='nr.closure.v2' or c['profile']!=PROFILE:fail('PROFILE_MISMATCH','/closure','phase_1')
    limits=dict(c['limits_override'] or {});retained=Work(c['limits_override'])
    for k,v in (extra or {}).items():limits[k]=min(v,retained.limits[k])
    total=Work(limits);total.physical.update(initial.physical)
    # Initial parse/read work is retained separately and its full guarded wire is
    # checked again under the conjunction of retained and caller ceilings.
    total.logical.update(initial.logical)
    for n,b in payloads.items():total.guard(CAPS[n],len(b))
    total.guard('bundle_bytes',sum(map(len,payloads.values())))
    c,_=decode(payloads['closure.json'],total,transport=True)
    if type(c['members']) is not list:fail('SCHEMA_INVALID','/members','phase_1')
    total.guard('unique_objects',len(c['members']));objects={};ordered=[];size=0
    for m in c['members']:
        shape(m,'reference encoding bytes','/members');k=typed(m['reference']);ordered.append(k)
        total.charge('reference_occurrences');total.charge('edge_visits')
        if m['encoding']!='base64' or type(m['bytes']) is not str:fail('SCHEMA_INVALID','/members','phase_1')
        encoded=m['bytes'];padding=len(encoded)-len(encoded.rstrip('='))
        if len(encoded)%4 or padding>2:fail('WIRE_INVALID','/members','phase_1')
        amount=len(encoded)//4*3-padding
        total.guard('build_bytes' if k[0] in ('nr.build.v2','nm.build.v1') else 'object_bytes',amount)
        total.guard('capture_bytes',size+amount)
        try:raw=base64.b64decode(encoded,validate=True)
        except ValueError:fail('WIRE_INVALID','/members','phase_1')
        total.charge('decode_input_bytes',len(encoded));total.charge('decoded_bytes',len(raw))
        total.charge('encode_input_bytes',len(raw));total.charge('encoded_bytes',len(encoded))
        if base64.b64encode(raw).decode()!=encoded:fail('CANONICAL_FORM_REQUIRED','/members','phase_1')
        if sha(raw,total)!=k[1]:fail('REFERENCE_DIGEST_MISMATCH','/members','phase_2')
        objects[k]=raw;size+=len(raw)
    if ordered!=sorted(set(ordered)):fail('SCHEMA_INVALID','/members','phase_1')
    if objects.get(typed(c['invocation'],'nr.invocation.v2'))!=payloads['invocation.json']:
        fail('REFERENCE_DIGEST_MISMATCH','/invocation','phase_2')
    # Reproduce the owning capture's deterministic validation/count schedule;
    # prior transport/recovery operations remain charged by the total Work.
    w=_SemanticWork(limits,total);raw=payloads['invocation.json'];iv,_=decode(raw,w)
    validate(iv,'nr.invocation.v2',raw,w)
    if c['authority_pin']!=typed(iv['authority'],'nr.authority.v2')[1]:fail('AUTHORITY_PIN_REQUIRED','/authority_pin','phase_1')
    if typed(iv['resource_policy'],'nm.resource-policy.v1')[1]!=APPROVED_POLICY_SHA:fail('RESOURCE_POLICY_IDENTITY_MISMATCH','/resource_policy','phase_1')
    bk=typed(iv['build'],'nr.build.v2')
    for n,k in [('build.json',bk),('policy.json',typed(iv['resource_policy']))]:
        if objects.get(k)!=payloads[n]:fail('REFERENCE_DIGEST_MISMATCH','/'+n,'phase_2')
    build,_=decode(payloads['build.json'],w)
    if build.get('schema')=='nr.prepared-build.v2':fail('NONEXECUTABLE_BUILD_WITNESS','/build','phase_1')
    w.high('build_bytes',len(payloads['build.json']));actual=reassessment_build.identity(w)
    if actual!=payloads['build.json'] or sha(actual,w)!=bk[1]:fail('BUILD_IDENTITY_MISMATCH','/build','phase_1')
    g=_Captured(raw,objects.__getitem__,c['authority_pin'],w)
    if set(g.objects)!=set(objects):fail('EXTRANEOUS_CLOSURE_MEMBER','/extraneous_closure_member','phase_2')
    g.closure_bytes=g.closure(c['authority_pin'],c['limits_override'])
    if g.closure_bytes!=payloads['closure.json']:fail('SCHEMA_INVALID','/closure','phase_2')
    for name,kind in [('result.json','nr.result.v2'),('trace.json','nr.trace.v2')]:
        value,_=decode(payloads[name],total);_output(value,kind)
        if value['invocation']!=g.root:fail('REFERENCE_DIGEST_MISMATCH','/'+name+'/invocation','phase_2')
        pending=[value]
        while pending:
            x=pending.pop()
            if type(x) is dict:
                if set(x)=={'kind','sha256'}:
                    total.charge('reference_occurrences');total.charge('edge_visits')
                    if typed(x) not in objects:fail('REFERENCE_ROLE_MISMATCH','/'+name,'phase_2')
                else:pending.extend(x.values())
            elif type(x) is list:pending.extend(x)
    r=json.loads(payloads['result.json']);t=json.loads(payloads['trace.json'])
    if r['authority']!={'reference':iv['authority'],'pin':c['authority_pin'],'permission':g.get(iv['authority'])['permission']}:
        fail('AUTHORITY_REFERENCE_MISMATCH','/result/authority','phase_2')
    if t['required_closure']!=[ref(*k) for k in sorted(objects)]:fail('REFERENCE_ROLE_MISMATCH','/trace/required_closure','phase_2')
    return payloads,g,total


def verify(bundle_dir):
    payloads,g,total=_retained(bundle_dir);admit(g)
    return _receipt('reassessment-verify',payloads,sha(payloads['manifest.json'],total))


def replay(bundle_dir,output_dir,limits_file=None):
    started=time.monotonic_ns();_preflight_output(output_dir)
    stored,g,total=_retained(bundle_dir,limits_file);fresh=_payloads(g)
    for name in ('result.json','trace.json'):
        if fresh[name]!=stored[name]:fail('REPLAY_SEMANTIC_MISMATCH','/'+name,'phase_8')
    return _deliver('reassessment-replay',fresh,output_dir,total,started)
