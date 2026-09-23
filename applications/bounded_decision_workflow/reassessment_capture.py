"""Slice 1 capture and historical recovery. No admission, assessment or delivery.

The public capture function derives the executable itself. The internal graph
accepts only a byte resolver; that is an I/O mechanism, not an authority or a
result-computation callback. No caller flag skips executable verification.
"""
import base64
import os

from . import retention, reassessment_build, measurement_build
from .measurement_contracts import canonical_json_bytes, APPROVED_POLICY_SHA, MeasurementContractError
from .measurement_wire import Work, Graph, decode, sha, ref, key, shape, fail, DIAGNOSTIC_CEILING
from .measurement_runtime import _read, _validate_retained_envelopes
from .reassessment_contracts import PROFILE, FILES, CAPS, typed, validate, edges, checked_limits


class _HistoricalWork(Work):
    """Original effective ceilings plus charges for repeated, in-memory work."""
    def __init__(self,overrides,outer):
        token=DIAGNOSTIC_CEILING.set(DIAGNOSTIC_CEILING.get())
        try:super().__init__(overrides)
        finally:DIAGNOSTIC_CEILING.reset(token)
        self.limits={k:min(v,outer.limits[k]) for k,v in self.limits.items()}
        self.outer=outer

    def charge(self,k,n=1):
        super().charge(k,n)
        if k in ('reference_occurrences','edge_visits','context_scan_bytes','scoped_expansions','scoped_edge_checks','rational_operations','decoder_comparisons','hash_bytes','json_decode_bytes'):
            self.outer.charge(k,n)
        elif k=='json_nodes':self.outer.charge('reparsed_json_nodes',n)
        elif k=='capture_bytes':self.outer.charge('historical_reconstructed_input_bytes',n)

    def high(self,k,n):
        super().high(k,n)
        self.outer.high(k,n)


def _walk(root, enter, outgoing, work):
    """One actual traversal implementation; synthetic graphs belong only in tests."""
    active=set();complete=set();stack=[(root,False,1,None,None)]
    while stack:
        k,done,depth,parent,path=stack.pop()
        if done:
            active.remove(k);complete.add(k);continue
        work.high('active_depth',depth)
        if parent is not None:
            work.charge('reference_occurrences');work.charge('edge_visits')
        # Required bytes/type/digest are checked before active-path detection.
        enter(k,parent,path)
        if k in active:fail('REFERENCE_CYCLE',path,'phase_2')
        if k in complete:continue
        active.add(k);stack.append((k,True,depth,parent,path))
        for p,c in reversed(outgoing(k)):stack.append((c,False,depth+1,k,p))
    return complete


class _Captured:
    """Internal structural graph; not evidence of production build admission."""
    def __init__(self, invocation, load, pin, work):
        work._wire_high_water=True
        self.work=work;self.objects={};self.values={};self.nodes={};self.paths={};self.occurrences=[]
        self.root=ref('nr.invocation.v2',sha(invocation,work));root=key(self.root)
        self.prior_bundles={};identities={}
        work.high('invocation_bytes',len(invocation))
        iv,_=decode(invocation,work)
        if iv.get('schema')!='nr.invocation.v2' or iv.get('profile')!=PROFILE:
            fail('PROFILE_MISMATCH','/profile','phase_1')
        validate(iv,root[0],invocation,work)
        typed(iv['authority'],'nr.authority.v2')
        if pin!=iv['authority']['sha256']:fail('AUTHORITY_PIN_REQUIRED','/authority_pin','phase_1')
        def enter(k,parent,path):
            if k not in self.objects:
                work.charge('unique_objects')
                try:raw=invocation if k==root else load(k)
                except KeyError:fail('REQUIRED_REFERENCE_MISSING',path or '/closure','phase_2')
                work.high('object_bytes',len(raw));work.charge('capture_bytes',len(raw))
                if sha(raw,work)!=k[1]:fail('REFERENCE_DIGEST_MISMATCH',path or '/closure','phase_2')
                if k[0]=='nm.basis':v=None;n=0
                else:
                    v,n=decode(raw,work,node_base=work.logical.get('json_nodes',0))
                    validate(v,k[0],raw,work)
                    if k[0]=='nm.resource-policy.v1' and k[1]!=APPROVED_POLICY_SHA:
                        fail('RESOURCE_POLICY_IDENTITY_MISMATCH','/resource_policy','phase_1')
                    identity=(k[0],v['id'],v['revision'])
                    if identity in identities and identities[identity]!=k[1]:
                        fail('IDENTITY_VERSION_COLLISION',path or '/id','phase_2')
                    identities[identity]=k[1]
                    if k[0] in ('nm.request.v1','nr.request.v2'):work.charge('request_contexts')
                    if k[0].startswith('nr.') or k[0]=='nm.request.v1':work.high('request_chain',v['revision'])
                    if k[0]=='nm.build.v1':
                        work.high('build_bytes',len(raw))
                        if v['contract_sha256']!=measurement_build.CONTRACT_SHA:
                            fail('ORIGINAL_CONTRACT_UNSUPPORTED','/contract_sha256','phase_2')
                    if k[0]=='nr.build.v2':work.high('build_bytes',len(raw))
                self.objects[k]=raw;self.values[k]=v;self.nodes[k]=n
                work.charge('json_nodes',n)
                self.paths[k]=self.paths.get(parent,'')+(path or '')
            if parent is not None:
                self.occurrences.append(dict(source=ref(*parent),path=path,target=ref(*k)))
                work.charge('context_scan_bytes',len(self.objects[parent])+len(self.objects[k])+66)
                if path=='/predecessor':
                    current=self.values[parent];previous=self.values[k]
                    if k[0]!=parent[0] or previous['id']!=current['id'] or previous['revision']!=current['revision']-1:
                        fail('PREDECESSOR_VERSION_MISMATCH',path,'phase_2')
        _walk(root,enter,lambda k:edges(self.values[k]),work)
        self.invocation=iv
        if self.get(iv['authority'])['request']!=iv['request']:
            fail('AUTHORITY_REFERENCE_MISMATCH','/authority/request','phase_2')
        # Owning selector integrity is reused without public evidence admission,
        # support qualification or minimax computation. Scope each original I.
        for k in sorted(self.values):
            if k[0]=='nm.invocation.v1':self._original_integrity(k,joins=False)
            if k[0]=='nr.request.v2':self._scope(k, skip_predecessor=True)
        for k,v in sorted(self.values.items()):
            if k[0]=='nr.retained-bundle.v2':self.prior_bundles[k]=self._recover(v)
        # All phase-2 retained roles must precede phase-3 nomination joins.
        for k in sorted(self.values):
            if k[0]=='nm.invocation.v1':self._original_integrity(k,decoders=False)
        for k,v in sorted(self.values.items()):
            if k[0]=='nr.retained-bundle.v2':self._historical_integrity(v['closure'])

    def get(self,r):return self.values[typed(r)]

    def _scope(self,root,skip_predecessor=False):
        found=set();todo=[root]
        while todo:
            k=todo.pop()
            if k in found:continue
            found.add(k);self.work.charge('scoped_expansions')
            self.work.charge('context_scan_bytes',len(self.objects[k]))
            for p,c in edges(self.values[k]):
                if skip_predecessor and k==root and p=='/predecessor':continue
                self.work.charge('edge_visits');self.work.charge('scoped_edge_checks');todo.append(c)
        return found

    def _original_integrity(self,k,*,joins=True,decoders=True):
        scope=self._scope(k)
        g=Graph.__new__(Graph)
        for f in ('objects','values','nodes','paths'):setattr(g,f,{r:getattr(self,f)[r] for r in scope})
        g.work=self.work;g.root=ref(*k);g.invocation=self.values[k]
        g.requests=sorted(r for r in scope if r[0]=='nm.request.v1')
        if not joins:
            iv=g.invocation;a=g.get(iv['selection'])
            if a['request']!=iv['request'] or (iv['adoption'] is None)!=(a['purpose']=='hypothetical_evaluation'):
                fail('AUTHORITY_REFERENCE_MISMATCH','/original/selection','phase_2')
            if iv['adoption'] is not None:
                adopted=g.get(iv['adoption'])
                if adopted['request']!=iv['request'] or adopted['selection']!=iv['selection'] or adopted['declaration']!=a['declaration']:
                    fail('AUTHORITY_REFERENCE_MISMATCH','/original/adoption','phase_2')
        # Decoder grammar is phase 2 in the reassessment profile, before later
        # semantic joins. The original selector's internal rules are unchanged.
        decoder_errors=[]
        for r in sorted(scope):
            if decoders and r[0]=='nm.decoder.v1':
                try:g._decoder(g.values[r])
                except MeasurementContractError as e:
                    if e.code=='RESOURCE_LIMIT_EXCEEDED':raise
                    # Preserve the owning selector's semantic coordinates while
                    # performing this profile's earlier decoder-integrity phase.
                    paths=[g.request_path(qk)+f'/measurements/{i}/decoder'
                           for qk in g.requests
                           for i,pr in enumerate(g.values[qk]['measurements'])
                           if typed(g.get(pr)['decoder'])==r]
                    for path in paths or [g.paths[r]]:
                        decoder_errors.append(MeasurementContractError(
                            'DECODER_INVALID',target=path,stage='phase_2',
                            details=dict(request=g.invocation['request'],references=[ref(*r)])))
        if decoder_errors:
            raise min(decoder_errors,key=lambda e:(e.code,e.target,canonical_json_bytes(e.details)))
        if joins:g._integrity()

    def _historical_integrity(self,c):
        w=self.work
        historical=_HistoricalWork(c['limits_override'],w)
        def old_load(k,unused):
            return self.objects[k]
        original=self.objects[typed(c['invocation'])]
        Graph(original,old_load,c['authority_pin'],historical)

    def closure(self,pin,limits=None):
        return _serialize_closure(dict(schema='nr.closure.v2',profile=PROFILE,
            invocation=self.root,authority_pin=pin,limits_override=limits),sorted(self.objects),self.objects,self.work)

    def _recover(self,d):
        w=self.work;c=d['closure'];members=[typed(r) for r in c['members']]
        reached=self._scope(typed(c['invocation']))
        if reached!=set(members):fail('SCHEMA_INVALID','/closure/members','phase_2')
        iv=self.get(c['invocation'])
        if c['authority_pin']!=iv['selection']['sha256']:
            fail('AUTHORITY_REFERENCE_MISMATCH','/closure/authority_pin','phase_2')
        effective=checked_limits(c['limits_override'])
        effective.limits={k:min(v,w.limits[k]) for k,v in effective.limits.items()}
        # A shared original input still has to fit its original effective policy.
        effective.guard('unique_objects',len(members))
        effective.guard('capture_bytes',sum(len(self.objects[k]) for k in members))
        for k in members:effective.guard('object_bytes',len(self.objects[k]))
        header={k:v for k,v in c.items() if k!='members'}
        skeleton=dict(header,members=[dict(reference=ref(*k),encoding='base64',bytes='') for k in members])
        estimate=len(canonical_json_bytes(skeleton))+sum(4*((len(self.objects[k])+2)//3) for k in members)
        effective.guard('closure_bytes',estimate)
        aggregate=estimate
        for row in d['files']:
            if row['name']!='closure.json':
                w.charge('reference_occurrences');w.charge('edge_visits')
                aggregate+=len(self.objects[typed(row['source']['reference'])])
        effective.guard('bundle_bytes',aggregate);w.high('bundle_bytes',aggregate)
        files={}
        for row in d['files']:
            name=row['name'];w.charge('role_checks')
            if name=='closure.json':raw=_serialize_closure(header,members,self.objects,w)
            else:
                k=typed(row['source']['reference']);raw=self.objects[k]
                effective.guard(CAPS[name],len(raw));w.guard(CAPS[name],len(raw))
                w.charge('reference_occurrences');w.charge('edge_visits')
                # Reserve newly interpreted opaque-role nodes against the
                # complete captured JSON total, before the parser allocates.
                node_base=w.logical.get('json_nodes',0) if not self.nodes[k] else 0
                v,n=decode(raw,w,node_base=node_base)
                w.charge('role_json_nodes',n)
                w.charge('context_scan_bytes',len(raw))
                if k[0]=='nm.basis' and not self.nodes[k]:
                    w.charge('json_nodes',n);self.nodes[k]=n
                expected={'manifest.json':'nm.bundle.v1','result.json':'nm.result.v1','trace.json':'nm.trace.v1'}.get(name,k[0])
                if v.get('schema')!=expected or v.get('profile')!='bdw.measurement.supplied.v1':
                    fail('REFERENCE_ROLE_MISMATCH','/files/'+name,'phase_2')
            effective.guard(CAPS[name],len(raw));w.guard(CAPS[name],len(raw))
            files[name]=raw
        effective.guard('bundle_bytes',sum(map(len,files.values())))
        w.high('bundle_bytes',sum(map(len,files.values())))
        w.charge('reconstructed_file_bytes',sum(map(len,files.values())))
        if files['invocation.json']!=self.objects[typed(c['invocation'])]:fail('REFERENCE_DIGEST_MISMATCH','/files/invocation.json','phase_2')
        for name,field in [('build.json','build_identity'),('policy.json','resource_policy')]:
            if sha(files[name],w)!=iv[field]:fail('REFERENCE_DIGEST_MISMATCH','/files/'+name,'phase_2')
        manifest,_=decode(files['manifest.json'],w)
        shape(manifest,'schema profile completeness files physical','/manifest')
        if manifest['completeness']!='complete' or type(manifest['files']) is not list or len(manifest['files'])!=6:
            fail('MANIFEST_INVALID','/manifest','phase_2')
        physical=manifest['physical']
        shape(physical,'bytes_read read_operations bytes_written write_operations elapsed_ns peak_rss_bytes status','/manifest/physical')
        if physical['status']!='observed_before_manifest_write' or any(type(v) is not int or v<0 for k,v in physical.items() if k!='status'):
            fail('MANIFEST_INVALID','/manifest/physical','phase_2')
        for row,name in zip(manifest['files'],FILES[:-1]):
            shape(row,'name bytes sha256','/manifest/files')
            if row['name']!=name or type(row['bytes']) is not int or row['bytes']!=len(files[name]) or row['sha256']!=sha(files[name],w):
                fail('MANIFEST_COMMITMENT_MISMATCH','/files/'+name,'phase_2')
        _validate_retained_envelopes(files,w,role_work=w)
        trace,_=decode(files['trace.json'],w)
        if trace['required_closure']!=[ref(*k) for k in members]:fail('REFERENCE_ROLE_MISMATCH','/trace/required_closure','phase_2')
        result,_=decode(files['result.json'],w)
        if result['authority']['selection']!=iv['selection'] or result['authority']['request']!=iv['request']:
            fail('AUTHORITY_REFERENCE_MISMATCH','/result/authority','phase_2')
        # Retained output references are checked against the already complete
        # original closure. They never nominate or discover additional inputs.
        for name,v in [('result.json',result),('trace.json',trace)]:
            pending=[(v,'/'+name)]
            while pending:
                x,path=pending.pop()
                if type(x) is dict:
                    if set(x)=={'kind','sha256'}:
                        w.charge('reference_occurrences');w.charge('edge_visits')
                        if typed(x) not in reached:fail('REFERENCE_ROLE_MISMATCH',path,'phase_2')
                    else:pending.extend((child,path+'/'+field) for field,child in x.items())
                elif type(x) is list:pending.extend((child,path+'/'+str(i)) for i,child in enumerate(x))
        return files


def _serialize_closure(header,members,objects,work):
    skeleton=dict(header,members=[dict(reference=ref(*k),encoding='base64',bytes='') for k in members])
    size=len(canonical_json_bytes(skeleton))+sum(4*((len(objects[k])+2)//3) for k in members)
    work.high('closure_bytes',size) # reserve before base64 allocation
    rows=[]
    for k in members:
        work.charge('reference_occurrences');work.charge('edge_visits')
        work.charge('encode_input_bytes',len(objects[k]))
        encoded=base64.b64encode(objects[k]).decode('ascii');work.charge('encoded_bytes',len(encoded))
        rows.append(dict(reference=ref(*k),encoding='base64',bytes=encoded))
    wire=canonical_json_bytes(dict(header,members=rows));work.charge('serialized_bytes',len(wire))
    return wire


def capture(invocation_file,objects_dir,authority_pin,limits=None):
    """Safe production capture. No qualification/result/CLI or build override."""
    work=Work(limits)
    absolute,parts=retention._parts(invocation_file)
    with retention._directory(absolute,parts[:-1]) as fd:
        if retention._filesystem(fd)!='ext4':raise retention._error('FILESYSTEM_UNSUPPORTED')
        pinned=os.fstat(fd)
        dimension=min(('invocation_bytes','capture_bytes'),key=lambda k:work.limits[k])
        raw=_read(fd,parts[-1],work.limits[dimension],work,dimension)
        with retention._directory(absolute,parts[:-1]) as again:
            current=os.fstat(again)
            if (pinned.st_dev,pinned.st_ino)!=(current.st_dev,current.st_ino):
                fail('INPUT_CHANGED_DURING_READ','/invocation','path')
    iv,_=decode(raw,work)
    if iv.get('schema')!='nr.invocation.v2' or iv.get('profile')!=PROFILE:
        fail('PROFILE_MISMATCH','/profile','phase_1')
    validate(iv,'nr.invocation.v2',raw,work)
    if authority_pin!=typed(iv['authority'],'nr.authority.v2')[1]:fail('AUTHORITY_PIN_REQUIRED','/authority_pin','phase_1')
    if typed(iv['resource_policy'],'nm.resource-policy.v1')[1]!=APPROVED_POLICY_SHA:
        fail('RESOURCE_POLICY_IDENTITY_MISMATCH','/resource_policy','phase_1')
    absolute,parts=retention._parts(objects_dir);pool={};total=len(raw)
    with retention._directory(absolute,parts) as fd:
        if retention._filesystem(fd)!='ext4':raise retention._error('FILESYSTEM_UNSUPPORTED')
        pinned=os.fstat(fd)
        def load(k):
            nonlocal total
            kind,digest=typed(ref(*k))
            if k not in pool:
                work.guard('unique_objects',len(pool)+2) # root plus new member
                member_dimension='build_bytes' if kind.endswith('build.v2') or kind=='nm.build.v1' else 'object_bytes'
                cap=min(work.limits[member_dimension],work.limits['capture_bytes']-total)
                work.guard('capture_bytes',total)
                dimension='capture_bytes' if cap<work.limits[member_dimension] else member_dimension
                pool[k]=_read(fd,digest+'.'+kind,cap,work,dimension,total if dimension=='capture_bytes' else 0)
                total+=len(pool[k])
            return pool[k]
        bk=typed(iv['build'],'nr.build.v2');supplied=load(bk)
        value,_=decode(supplied,work)
        if value.get('schema')=='nr.prepared-build.v2':fail('NONEXECUTABLE_BUILD_WITNESS','/build','phase_1')
        work.high('build_bytes',len(supplied))
        actual=reassessment_build.identity(work)
        if supplied!=actual:fail('BUILD_IDENTITY_MISMATCH','/build','phase_1')
        if sha(actual,work)!=bk[1]:fail('BUILD_IDENTITY_MISMATCH','/build','phase_1')
        graph=_Captured(raw,load,authority_pin,work)
        graph.closure_bytes=graph.closure(authority_pin,limits)
        with retention._directory(absolute,parts) as again:
            current=os.fstat(again)
            if (pinned.st_dev,pinned.st_ino)!=(current.st_dev,current.st_ino):
                fail('INPUT_CHANGED_DURING_READ','/objects_dir','path')
    return graph
