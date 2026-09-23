"""Closed captured measurement graph. No file discovery or caller matrices.

Delivery uses the approved I/Q/E carriage, with guards before capture/traversal.
The public snapshot remains owned by the public StateClassificationResult.
"""
from contextvars import ContextVar
import hashlib
import json
import re
from fractions import Fraction
from .measurement_contracts import (PROFILE, APPROVED_LIMITS, APPROVED_POLICY_SHA,
    MeasurementContractError, canonical_json_bytes, parse_document, _ref)

DIAGNOSTIC_CEILING = ContextVar('measurement_diagnostic_ceiling', default=APPROVED_LIMITS['diagnostic_bytes'])

BUNDLE_STATE = ContextVar('measurement_bundle_state', default='absent')

HEADER = {'schema','profile','id','revision'}
BODIES = {
 'nm.invocation.v1':'request selection adoption build_identity resource_policy',
 'nm.request.v1':'context evidence hypotheses measurements support policy predecessor',
 'nm.evidence.v1':'snapshot question binding token_roles',
 'nm.hypothesis.v1':'account_kind context evidence requirements provenance',
 'nm.procedure.v1':'context evidence method method_edition decoder conditions provenance',
 'nm.decoder.v1':'domain outcomes',
 'nm.support.v1':'hypothesis procedure decoder evidence context origin coverage permits excludes uncertainty qualification basis exclusion_basis provenance',
 'nm.policy.v1':'algorithm secondary coverage_rule tie_rule authority',
 'nm.declaration.v1':'requests scope_state attestation',
 'nm.selection.v1':'declaration request purpose attestation',
 'nm.adoption.v1':'declaration request selection attestation',
 'nm.build.v1':'checkpoint source_manifest environment_manifest entrypoint contract_sha256 resource_policy_sha256',
}


def fail(code, target, stage='phase_3', **details):
    raise MeasurementContractError(code, target=target, stage=stage, details=details)


def shape(x, fields, path):
    if type(x) is not dict or set(x) != set(fields.split() if isinstance(fields,str) else fields):
        fail('SCHEMA_INVALID',path,'phase_1')


def local_id(x):
    if type(x) is not str or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}',x):
        fail('IDENTITY_INVALID','id')


def sha(wire, work=None):
    if work is not None:work.charge('hash_bytes',len(wire))
    return hashlib.sha256(wire).hexdigest()
def ref(kind, digest): return {'kind':kind,'sha256':digest}
def key(r,kind=None): return _ref(r,expected_kind=kind)


class Work:
    def __init__(self, overrides=None):
        self.limits = dict(APPROVED_LIMITS)
        self.logical = {}; self.physical = {'bytes_read':0,'read_operations':0,'bytes_written':0,'write_operations':0}
        if overrides is not None:
            if type(overrides) is not dict: fail('RESOURCE_LIMIT_REQUEST_INVALID','limits','phase_1')
            for k,v in overrides.items():
                if k not in self.limits or type(v) is not int or not 0<v<=self.limits[k]:
                    fail('RESOURCE_LIMIT_REQUEST_INVALID',k,'phase_1')
                self.limits[k]=v
        DIAGNOSTIC_CEILING.set(self.limits['diagnostic_bytes'])

    def io(self,k,n):
        self.physical[k]+=n

    def guard(self,k,n):
        if n>self.limits[k]:
            fail('RESOURCE_LIMIT_EXCEEDED',k,'phase_2',dimension=k,attempted=n,limit=self.limits[k])

    def charge(self,k,n=1):
        amount=self.logical.get(k,0)+n
        if k in self.limits:self.guard(k,amount)
        self.logical[k]=amount

    def high(self,k,n):
        self.guard(k,n);self.logical[k]=max(self.logical.get(k,0),n)


def decode(wire, work, *, transport=False, node_base=0):
    work.guard('closure_bytes' if transport else 'object_bytes',len(wire))
    # Preflight tokens before constructing the document. The authoritative
    # parser below still rejects invalid grammar, duplicate keys and noncanonical
    # bytes. Keys are string work but not value nodes, as in the frozen oracle.
    depth=0;nodes=0;i=0
    while i<len(wire):
        c=wire[i]
        if c==34:
            start=i;i+=1;size=0
            while i<len(wire) and wire[i]!=34:
                if wire[i]==92:
                    i+=1
                    if i<len(wire) and wire[i]==117:
                        try:cp=int(wire[i+1:i+5],16)
                        except ValueError:fail('JSON_INVALID','wire','phase_1')
                        i+=4
                        size+=1 if cp<128 else 2 if cp<2048 else 3
                        if 0xD800<=cp<=0xDBFF and wire[i+1:i+3]==b'\\u':
                            try:low=int(wire[i+3:i+7],16)
                            except ValueError:low=0
                            if 0xDC00<=low<=0xDFFF:size+=1;i+=6
                    else:size+=1
                else:size+=1
                # Transport values may be base64; keys retain the ordinary cap.
                work.guard('closure_bytes' if transport else 'string_bytes',size)
                i+=1
            i+=1;j=i
            while j<len(wire) and wire[j] in b' \t\r\n':j+=1
            is_key=j<len(wire) and wire[j]==58
            if is_key:work.guard('string_bytes',size)
            else:nodes+=1;work.guard('json_nodes',node_base+nodes)
            continue
        if c in (91,123):
            depth+=1;work.guard('json_depth',depth);nodes+=1
            work.guard('json_nodes',node_base+nodes)
        elif c in (93,125):depth-=1
        elif c not in b' \t\r\n,:':
            nodes+=1;work.guard('json_nodes',node_base+nodes)
            while i+1<len(wire) and wire[i+1] not in b' \t\r\n,]}':i+=1
        i+=1
    value=parse_document(wire,allow_opaque=True,work=work)
    return value,nodes


def bounded_json(value,work,dimension):
    # Bound each emitted chunk before retaining it; never allocate the complete
    # oversized encoded document and then call that a pre-allocation guard.
    chunks=[];size=0
    encoder=json.JSONEncoder(sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
    for chunk in encoder.iterencode(value):
        part=chunk.encode('utf-8');size+=len(part);work.guard(dimension,size)
        chunks.append(part)
    return b''.join(chunks)


def rational(v,work):
    shape(v,'numerator denominator','rational')
    n,d=v['numerator'],v['denominator']
    if type(n) is not str or type(d) is not str:fail('RATIONAL_INVALID','rational')
    work.guard('integer_digits',len(n.lstrip('-')));work.guard('integer_digits',len(d))
    if not re.fullmatch(r'0|-?[1-9][0-9]*',n) or not re.fullmatch(r'[1-9][0-9]*',d):
        fail('RATIONAL_INVALID','rational')
    work.charge('rational_operations')
    r=Fraction(int(n),int(d))
    if str(r.numerator)!=n or str(r.denominator)!=d:fail('RATIONAL_INVALID','rational')
    return r


def attestation(v):
    shape(v,'issuer_label authenticated basis','attestation')
    if v['authenticated'] is not False or any(type(v[k]) is not str for k in ['issuer_label','basis']):
        fail('SCHEMA_INVALID','attestation')


def ordered(xs, *, ids=False, minimum=0):
    if type(xs) is not list or len(xs)<minimum:fail('SCHEMA_INVALID','array')
    if ids and any(type(x) is not dict or 'id' not in x for x in xs):fail('SCHEMA_INVALID','array')
    values=[x['id'] for x in xs] if ids else xs
    if any(type(x) is not str for x in values):fail('SCHEMA_INVALID','array')
    if ids:
        for x in values:local_id(x)
    if values!=sorted(values) or len(set(values))!=len(values):fail('ORDER_INVALID','array')


def basis(xs, minimum=0):
    if type(xs) is not list or len(xs)<minimum:fail('SCHEMA_INVALID','basis')
    ks=[key(x,'nm.basis') for x in xs]
    if ks!=sorted(set(ks)):fail('ORDER_INVALID','basis')


def edges(v):
    """Declared roles only. Snapshot/custody/attestation text has no edges."""
    kind=v['schema']; found=[]
    def one(field,kind):
        if v[field] is not None:found.append(('/'+field,key(v[field],kind)))
    def many(field,kind):
        if type(v[field]) is not list:fail('SCHEMA_INVALID',field,'phase_1')
        for i,r in enumerate(v[field]):found.append((f'/{field}/{i}',key(r,kind)))
    if kind=='nm.invocation.v1':
        for field,k in [('request','nm.request.v1'),('selection','nm.selection.v1'),('adoption','nm.adoption.v1')]:one(field,k)
        for field,k in [('build_identity','nm.build.v1'),('resource_policy','nm.resource-policy.v1')]:
            found.append(('/'+field,key(ref(k,v[field]),k)))
    elif kind=='nm.request.v1':
        for f,k in [('evidence','nm.evidence.v1'),('policy','nm.policy.v1'),('predecessor','nm.request.v1')]:one(f,k)
        for f,k in [('hypotheses','nm.hypothesis.v1'),('measurements','nm.procedure.v1'),('support','nm.support.v1')]:many(f,k)
    elif kind in ('nm.selection.v1','nm.adoption.v1'):
        for f,k in [('declaration','nm.declaration.v1'),('request','nm.request.v1')]:one(f,k)
        if kind=='nm.adoption.v1':one('selection','nm.selection.v1')
    elif kind=='nm.declaration.v1':many('requests','nm.request.v1')
    elif kind in ('nm.hypothesis.v1','nm.procedure.v1','nm.support.v1'):
        one('evidence','nm.evidence.v1')
        if kind!='nm.hypothesis.v1':one('decoder','nm.decoder.v1')
        if kind=='nm.support.v1':
            one('hypothesis','nm.hypothesis.v1');one('procedure','nm.procedure.v1')
            many('basis','nm.basis');many('exclusion_basis','nm.basis')
            shape(v['uncertainty'],'kind statement basis','uncertainty')
            basis(v['uncertainty']['basis'])
            for i,r in enumerate(v['uncertainty']['basis']):found.append((f'/uncertainty/basis/{i}',key(r,'nm.basis')))
        if kind=='nm.procedure.v1':
            if type(v['conditions']) is not list:fail('SCHEMA_INVALID','conditions')
            for i,c in enumerate(v['conditions']):
                if type(c) is not dict:fail('SCHEMA_INVALID','conditions')
                if 'basis' in c:basis(c['basis'])
                for j,r in enumerate(c.get('basis',[])):found.append((f'/conditions/{i}/basis/{j}',key(r,'nm.basis')))
    elif kind=='nm.evidence.v1':
        shape(v['token_roles'],'quantity observation_role unit basis','token_roles')
        basis(v['token_roles']['basis'],1)
        for i,r in enumerate(v['token_roles']['basis']):found.append((f'/token_roles/basis/{i}',key(r,'nm.basis')))
    return sorted(found)


class Graph:
    def __init__(self, invocation, load, pin, work):
        self.work=work;self.objects={};self.values={};self.nodes={};self.occurrences=[]
        self.root=ref('nm.invocation.v1',sha(invocation,work));self.paths={key(self.root):''}
        iv,n=decode(invocation,work)
        if iv.get('schema')!='nm.invocation.v1' or iv.get('profile')!=PROFILE:
            fail('PROFILE_MISMATCH','invocation','phase_1')
        if not isinstance(pin,str) or not re.fullmatch('[0-9a-f]{64}',pin) or iv.get('selection',{}).get('sha256')!=pin:
            fail('AUTHORITY_PIN_REQUIRED','authority_pin','phase_2')
        active=set();complete=set();identities={}
        # Frames: entry followed by exit; hash/type checks precede cycle logic.
        stack=[(key(self.root),False,1,None,None)]
        while stack:
            k,exit_frame,depth,parent,path=stack.pop()
            if exit_frame:active.remove(k);complete.add(k);continue
            work.high('active_depth',depth)
            if parent is not None:
                work.charge('reference_occurrences');work.charge('edge_visits')
                self.occurrences.append({'source':ref(*parent),'path':path,'target':ref(*k)})
            if k not in self.objects:
                work.charge('unique_objects')
                try:
                    wire=invocation if k==key(self.root) else load(k,work)
                except MeasurementContractError as error:
                    if error.code=='REQUIRED_REFERENCE_MISSING' and parent is not None:
                        error.target='/closure/'+parent[1]+path
                        error.details.update(request=iv['request'],references=sorted([ref(*parent),ref(*k)],key=key))
                    raise
                self.paths[k]=self.paths.get(parent,'')+(path or '')
                work.high('object_bytes',len(wire));work.charge('capture_bytes',len(wire))
                if sha(wire,work)!=k[1]:fail('REFERENCE_DIGEST_MISMATCH',path,'phase_2',request=iv['request'],references=[ref(*k)])
                if k[0]=='nm.basis':v=None;nodes=0
                else:
                    v,nodes=decode(wire,work,node_base=work.logical.get('json_nodes',0))
                    if v.get('schema')=='nm.prepared-build.v1':fail('NONEXECUTABLE_BUILD_WITNESS',path,'phase_1')
                    try:parse_document(wire,expected_schema=k[0],work=work)
                    except MeasurementContractError as error:
                        error.stage='phase_2';error.target=self.paths[k]+'/'+error.target
                        error.details['request']=iv['request'];raise
                    if k[0]=='nm.resource-policy.v1':
                        if sha(wire,work)!=APPROVED_POLICY_SHA:fail('RESOURCE_POLICY_IDENTITY_MISMATCH',path,'phase_1')
                    else:
                        if k[0] not in BODIES:fail('PROFILE_MISMATCH',path,'phase_1')
                        required=HEADER|set(BODIES[k[0]].split())
                        # Q extension fields are rejected at the frozen phase-3
                        # request boundary. They never generate traversal edges.
                        if k[0]=='nm.request.v1' and required<=set(v):pass
                        else:shape(v,required,path)
                    ident=(k[0],v['id'],v['revision'])
                    if ident in identities and identities[ident]!=k[1]:
                        fail('IDENTITY_VERSION_COLLISION',path.rsplit('/',1)[0],'phase_2',request=iv['request'],logical_id=v['id'],references=sorted([ref(k[0],identities[ident]),ref(*k)],key=key))
                    identities[ident]=k[1]
                    if k[0]=='nm.request.v1':
                        # Refuse an unsupported context/history before following
                        # any dependency of that newly captured request.
                        work.charge('request_contexts')
                        work.high('request_chain',v['revision'])
                self.objects[k]=wire;self.values[k]=v;self.nodes[k]=nodes
                work.charge('json_nodes',nodes)
            if parent is not None and parent[0]=='nm.request.v1' and path=='/predecessor':
                current=self.values[parent];previous=self.values[k]
                if previous['id']!=current['id'] or previous['revision']!=current['revision']-1:
                    fail('PREDECESSOR_VERSION_MISMATCH','/predecessor','phase_2',request=iv['request'],references=[ref(*k)])
            if parent is not None:
                work.charge('context_scan_bytes',len(self.objects[parent])+len(self.objects[k])+66)
            if k in active:fail('REFERENCE_CYCLE',path,'phase_2')
            if k in complete:continue
            active.add(k);stack.append((k,True,depth,parent,path))
            v=self.values[k]
            outgoing=[] if v is None else edges(v)
            for edge,child in reversed(outgoing):stack.append((child,False,depth+1,k,edge))
        self.invocation=self.get(self.root)
        self.requests=sorted(k for k,v in self.values.items() if v and k[0]=='nm.request.v1')
        self._integrity()

    def get(self,r):return self.values[key(r)]

    def reject(self,code,field,stage='phase_3',request=None,references=(),logical_id=None,occurrence_count=None):
        fail(code,field,stage,request=request or self.invocation['request'],references=sorted(references,key=key),logical_id=logical_id,occurrence_count=occurrence_count)

    def request_path(self,qk):
        current=key(self.invocation['request']);path=''
        while True:
            if current==qk:return path
            previous=self.values[current]['predecessor']
            if previous is None:return '/declared_requests/'+qk[1]
            current=key(previous);path+='/predecessor'


    def requirements(self, closure_bytes):
        # Frozen logical_required is full deterministic input demand, not an
        # assertion that gated mapping/scoring work was executed.
        def count(v):
            pending=[v];n=0
            while pending:
                x=pending.pop();n+=1
                if isinstance(x,dict):pending.extend(x.values())
                elif isinstance(x,list):pending.extend(x)
            return n
        es=[v for k,v in self.values.items() if k[0]=='nm.evidence.v1']
        public_unique=sum(count(e['snapshot']) for e in es)
        public_context=sum(count(self.get(self.values[k]['evidence'])['snapshot']) for k in self.requests)
        scan=sum(len(self.objects[key(e['source'])])+len(self.objects[key(e['target'])])+66 for e in self.occurrences)
        return dict(unique_objects=len(self.objects),unique_bytes=sum(map(len,self.objects.values())),
                    capture_bytes=sum(map(len,self.objects.values())),reference_occurrences=len(self.occurrences),
                    edge_visits=len(self.occurrences),active_depth=self.work.logical['active_depth'],
                    request_contexts=len(self.requests),request_chain=max(self.values[k]['revision'] for k in self.requests),
                    json_nodes=sum(self.nodes.values()),public_reconstruction_unique_nodes=public_unique,
                    public_reconstruction_context_nodes=public_context,context_scan_bytes=scan,closure_bytes=closure_bytes,
                    object_bytes=max(map(len,self.objects.values())),invocation_bytes=len(self.objects[key(self.root)]))

    def _integrity(self):
        w=self.work;iv=self.invocation;a=self.get(iv['selection'])
        if a['request']!=iv['request']:fail('AUTHORITY_REFERENCE_MISMATCH','selection.request','phase_2')
        if a['purpose'] not in ('hypothetical_evaluation','accepted_working_evaluation'):fail('SCHEMA_INVALID','purpose')
        if (iv['adoption'] is None)!=(a['purpose']=='hypothetical_evaluation'):fail('AUTHORITY_REFERENCE_MISMATCH','adoption','phase_2')
        if iv['adoption'] is not None:
            t=self.get(iv['adoption'])
            if t['request']!=iv['request'] or t['selection']!=iv['selection'] or t['declaration']!=a['declaration']:
                self.reject('AUTHORITY_REFERENCE_MISMATCH','/adoption/request','phase_2',references=[iv['adoption']])
        for qk in self.requests:
            q=self.values[qk];w.high('request_chain',q['revision'])
            previous=q['predecessor']
            if q['revision']==1:
                if previous is not None:fail('PREDECESSOR_VERSION_MISMATCH','predecessor','phase_2')
            else:
                if previous is None:fail('REQUIRED_REFERENCE_MISSING','predecessor','phase_2')
                p=self.get(previous)
                if p['id']!=q['id'] or p['revision']!=q['revision']-1:self.reject('PREDECESSOR_VERSION_MISMATCH','/predecessor','phase_2',references=[previous])
        # Complete phase-2 lineage before any phase-3 nomination checks.
        # Frozen nomination subchecks are global in subcheck/Q/field order.
        for subcheck in ('reference','identity','order'):
            for qk in self.requests:
                q=self.values[qk]
                for field in ('hypotheses','measurements'):
                    xs=q[field]
                    if len(xs)>2:fail('NOMINATION_CARDINALITY_INVALID',field)
                    ks=[key(r) for r in xs];ids=[self.get(r)['id'] for r in xs]
                    if subcheck=='reference' and len(set(ks))!=len(ks):
                        self.reject('DUPLICATE_NOMINATION_REFERENCE','/'+field,request=ref(*qk),references=xs,logical_id=ids[0],occurrence_count=len(xs))
                    if subcheck=='identity' and len(set(ids))!=len(ids):
                        self.reject('DUPLICATE_NOMINATION_ID','/'+field,request=ref(*qk),references=xs,logical_id=ids[0],occurrence_count=len(xs))
                    if subcheck=='order' and ids!=sorted(ids):
                        self.reject('NOMINATION_ORDER_INVALID','/'+field,request=ref(*qk),references=xs,logical_id=ids[0])
        errors=[]
        self._checked_decoders=set();self._checked_methods=set()
        def capture(call):
            try:call()
            except MeasurementContractError as error:
                if error.code=='RESOURCE_LIMIT_EXCEEDED':raise
                error.stage='phase_3'
                if not error.target.startswith('/'):error.target='/'+error.target
                errors.append(error)
        for qk in self.requests:
            q=self.values[qk]
            def request_checks():
                extras=set(q)-(HEADER|set(BODIES['nm.request.v1'].split()))
                if extras:self.reject('REQUEST_SCHEMA_INVALID','/'+sorted(extras)[0],request=ref(*qk))
                for field,code in [('hypotheses','HYPOTHESIS_SET_EMPTY'),('measurements','MEASUREMENT_SET_EMPTY')]:
                    if not q[field]:self.reject(code,'/'+field,request=ref(*qk))
                ss=[(self.get(r)['id'],self.get(r)['revision']) for r in q['support']]
                if ss!=sorted(set(ss)):fail('ORDER_INVALID','support')
            before=len(errors);capture(request_checks)
            if len(errors)!=before:continue
            # Charge each context even at shared completed objects. Resource
            # refusal is immediate; it never searches beyond its approved bound.
            scope=set();todo=[qk]
            while todo:
                k=todo.pop()
                if k in scope:continue
                scope.add(k);w.charge('scoped_expansions');w.charge('context_scan_bytes',len(self.objects[k]))
                v=self.values[k]
                if v:
                    for path,child in edges(v):
                        if k==qk and path=='/predecessor':continue
                        w.charge('edge_visits');w.charge('scoped_edge_checks');todo.append(child)
            capture(lambda:self._joins(q,ref(*qk)))
        for v in self.values.values():
            if v:capture(lambda:self._intrinsic(v))
        if errors:
            raise min(errors,key=lambda e:(e.code,e.target,canonical_json_bytes(e.details)))

    def _joins(self,q,qr):
        shape(q['context'],'subject_entity_anchor_id variable_anchor_id assertion_context as_of scenario_label','context')
        local_id(q['context']['scenario_label'])
        decoder_errors=[]
        for i,pr in enumerate(q['measurements']):
            p=self.get(pr);o=self.get(p['decoder']);d=o['domain']
            path=self.request_path(key(qr))+f'/measurements/{i}/decoder'
            self._checked_methods.add(id(p));self._checked_decoders.add(id(o))
            if (p['method'],d['kind'],d['unit']) not in [('reference_scalar','scalar_finite_decimal','degree_celsius'),('nonspecific_code','literal_codes','code')]:
                decoder_errors.append(MeasurementContractError('PROCEDURE_DOMAIN_MISMATCH',target=path,stage='phase_3',details=dict(request=self.invocation['request'],references=[p['decoder']])))
                continue
            try:self._decoder(o)
            except MeasurementContractError as error:
                if error.code=='RESOURCE_LIMIT_EXCEEDED':raise
                decoder_errors.append(MeasurementContractError('DECODER_INVALID',target=path,stage='phase_3',details=dict(request=self.invocation['request'],references=[p['decoder']])))
        if decoder_errors:raise min(decoder_errors,key=lambda e:(e.code,e.target))
        for hr in q['hypotheses']:
            for pr in q['measurements']:
                if sum(self.get(s)['hypothesis']==hr and self.get(s)['procedure']==pr for s in q['support'])>2:
                    fail('SCHEMA_INVALID','support')
        hs=[self.get(r)['account_kind'] for r in q['hypotheses']]
        if len(set(hs))!=len(hs):self.reject('SEMANTIC_ALIAS','/hypotheses',request=qr,references=q['hypotheses'],logical_id=self.get(q['hypotheses'][0])['id'])
        meanings=[]
        for r in q['measurements']:
            p=self.get(r);o=self.get(p['decoder'])
            meaning=[p['context'],p['method'],p['method_edition'],o['domain'],sorted([x['region'] for x in o['outcomes']],key=canonical_json_bytes),
                     [{k:v for k,v in c.items() if k!='id'} for c in p['conditions']]]
            encoded=canonical_json_bytes(meaning)
            if encoded in meanings:self.reject('SEMANTIC_ALIAS','/measurements',request=qr,references=q['measurements'],logical_id=self.get(q['measurements'][0])['id'])
            meanings.append(encoded)
        for r in q['hypotheses']+q['measurements']+q['support']:
            v=self.get(r)
            if v['evidence']!=q['evidence'] or v['context']!=q['context']:fail('SUPPORT_SUBJECT_MISMATCH','context/evidence')
        for i,sr in enumerate(q['support']):
            s=self.get(sr)
            for field,nomination in [('hypothesis','hypotheses'),('procedure','measurements')]:
                if s[field] not in q[nomination]:
                    same=[r for r in q[nomination] if self.get(r)['id']==self.get(s[field])['id']]
                    self.reject('SUPPORT_SUBJECT_MISMATCH',f'/support/{i}/{field}',request=qr,references=[sr,s[field],*same])
            if s['decoder']!=self.get(s['procedure'])['decoder']:
                self.reject('SUPPORT_SUBJECT_MISMATCH',f'/support/{i}/decoder',request=qr,references=[sr,s['decoder'],self.get(s['procedure'])['decoder']])

    def _intrinsic(self,v):
        kind=v['schema'];w=self.work
        for f in ['attestation','provenance','authority']:
            if f in v:attestation(v[f])
        if kind=='nm.declaration.v1':
            rs=[key(x,'nm.request.v1') for x in v['requests']]
            if not rs or rs!=sorted(set(rs)) or v['scope_state'] not in ('true','false','unknown'):fail('SCHEMA_INVALID','declaration')
        if kind=='nm.policy.v1':
            if [v[k] for k in ['algorithm','secondary','coverage_rule','tie_rule']]!=['finite_compatibility_minimax/v1','none','whole_nominated_matrix','preserve_all_best']:fail('RANKING_POLICY_INVALID','policy')
        if kind=='nm.evidence.v1':
            shape(v['question'],'state_anchor_id assertion_context as_of declared_state_label','question')
            shape(v['binding'],'condition_index constraint_evaluation_index semantic_candidate_index constraint_anchor_id variable_anchor_id subject_entity_anchor_id expected_quantity_kind expected_observation_role expected_unit','binding')
            shape(v['token_roles'],'quantity observation_role unit basis','token_roles');basis(v['token_roles']['basis'],1)
        if kind=='nm.hypothesis.v1':
            if v['account_kind'] not in ('high_underlying_faithful_baseline','low_underlying_positive_offset'):fail('SCHEMA_INVALID','account_kind')
            ordered(v['requirements'],ids=True,minimum=1)
            for row in v['requirements']:
                shape(row,'id kind expected','requirement')
                if row['kind']=='baseline_decimal_equals':rational(row['expected'],w)
                elif row['kind']!='baseline_cn_verdict_equals' or row['expected'] not in ('satisfied','violated'):fail('SCHEMA_INVALID','requirement')
        if kind=='nm.procedure.v1':
            if type(v['method_edition']) is not int or v['method_edition']<1:fail('SCHEMA_INVALID','method_edition')
            d=self.get(v['decoder'])['domain']
            if id(v) not in getattr(self,'_checked_methods',set()) and (v['method'],d['kind'],d['unit']) not in [('reference_scalar','scalar_finite_decimal','degree_celsius'),('nonspecific_code','literal_codes','code')]:fail('DECODER_INVALID','method')
            ordered(v['conditions'],ids=True)
            ids={c['id'] for c in v['conditions']}
            required={'applicability','availability','calibration','fidelity','hold'}
            if ids not in (required,required|{'baseline_ceiling'}):fail('SCHEMA_INVALID','conditions')
            for c in v['conditions']:
                if c['id']=='baseline_ceiling':
                    shape(c,'id kind threshold','condition')
                    if c['kind']!='baseline_le':fail('SCHEMA_INVALID','condition')
                    rational(c['threshold'],w)
                else:
                    shape(c,'id kind state basis','condition')
                    if c['kind']!='local_assumption' or c['state'] not in ('true','false','unknown'):fail('SCHEMA_INVALID','condition')
                    basis(c['basis'],int(c['state']!='unknown'))
        if kind=='nm.decoder.v1' and id(v) not in getattr(self,'_checked_decoders',set()):self._decoder(v)
        if kind=='nm.support.v1':
            for f in ['permits','excludes']:ordered(v[f])
            outcomes={o['id'] for o in self.get(v['decoder'])['outcomes']}
            if set(v['permits'])&set(v['excludes']) or not set(v['permits']+v['excludes'])<=outcomes:fail('SUPPORT_INVALID','outcomes')
            basis(v['basis']);basis(v['exclusion_basis'])
            shape(v['qualification'],'status reason','qualification');shape(v['uncertainty'],'kind statement basis','uncertainty');basis(v['uncertainty']['basis'])
            status=v['qualification']['status'];reason=v['qualification']['reason']
            if v['origin'] not in ('supplied_synthetic','supplied_unverified_derivation'):fail('SUPPORT_INVALID','origin')
            if status=='qualified_conditional':
                if v['origin']!='supplied_synthetic' or reason!='explicit_synthetic_premise' or v['uncertainty']['kind']!='declared_hard_outcome_support' or not v['basis']:fail('SUPPORT_INVALID','qualification')
            elif status!='unavailable' or reason not in ('missing_support','unknown_applicability','unverified_derivation'):fail('SUPPORT_INVALID','qualification')
            if v['origin']=='supplied_unverified_derivation' and (status!='unavailable' or reason!='unverified_derivation'):fail('SUPPORT_INVALID','origin')
            if v['uncertainty']['kind'] not in ('unknown','declared_hard_outcome_support') or type(v['uncertainty']['statement']) is not str:fail('SUPPORT_INVALID','uncertainty')
            coverage=v['coverage']
            valid=(coverage=='partial_positive' and v['permits'] and not v['excludes'] and not v['exclusion_basis'] or
                   coverage=='explicit_exclusions' and v['excludes'] and v['exclusion_basis'] or
                   coverage=='complete_envelope' and v['permits'] and not v['excludes'] and v['exclusion_basis'])
            if not valid:fail('SUPPORT_INVALID','coverage')

    def _decoder(self,o):
        d=o['domain'];shape(d,'kind unit values','domain');ordered(o['outcomes'],ids=True,minimum=1)
        if len(o['outcomes'])>3:fail('DECODER_INVALID','outcomes')
        for row in o['outcomes']:shape(row,'id region','outcome')
        if d['kind']=='literal_codes' and d['unit']=='code':
            ordered(d['values'],minimum=1);union=[]
            for code in d['values']:local_id(code)
            for row in o['outcomes']:
                r=row['region'];shape(r,'kind values','region');ordered(r['values'],minimum=1)
                if r['kind']!='literal_set':fail('DECODER_INVALID','region')
                union+=r['values']
            if sorted(union)!=d['values']:fail('DECODER_INVALID','partition')
        elif d=={'kind':'scalar_finite_decimal','unit':'degree_celsius','values':None}:
            intervals=[]
            for row in o['outcomes']:
                r=row['region'];shape(r,'kind lower lower_closed upper upper_closed','region')
                if r['kind']!='interval' or type(r['lower_closed']) is not bool or type(r['upper_closed']) is not bool:fail('DECODER_INVALID','region')
                lo=None if r['lower'] is None else rational(r['lower'],self.work)
                hi=None if r['upper'] is None else rational(r['upper'],self.work)
                if lo is None and r['lower_closed'] or hi is None and r['upper_closed']:fail('DECODER_INVALID','unbounded')
                if lo is not None and hi is not None and (lo>hi or lo==hi and not (r['lower_closed'] and r['upper_closed'])):fail('DECODER_INVALID','empty')
                intervals.append((lo,hi,r['lower_closed'],r['upper_closed']))
            intervals.sort(key=lambda x:(x[0] is not None,x[0] or 0))
            if intervals[0][0] is not None or intervals[-1][1] is not None:fail('DECODER_INVALID','coverage')
            for left,right in zip(intervals,intervals[1:]):
                self.work.charge('decoder_comparisons')
                if left[1] is None or left[1]!=right[0] or left[3]==right[2]:fail('DECODER_INVALID','partition')
        else:fail('DECODER_INVALID','domain')
