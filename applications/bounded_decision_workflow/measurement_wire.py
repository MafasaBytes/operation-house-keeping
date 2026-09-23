"""Closed captured measurement graph. No file discovery or caller matrices.

Delivery uses the approved I/Q/E carriage, with guards before capture/traversal.
The public snapshot remains owned by the public StateClassificationResult.
"""
import hashlib
import json
import re
from fractions import Fraction
from .measurement_contracts import (PROFILE, APPROVED_LIMITS, APPROVED_POLICY_SHA,
    MeasurementContractError, canonical_json_bytes, parse_document, _ref)

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


def sha(wire): return hashlib.sha256(wire).hexdigest()
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

    def guard(self,k,n):
        if n>self.limits[k]:
            fail('RESOURCE_LIMIT_EXCEEDED',k,'phase_2',dimension=k,attempted=n,limit=self.limits[k])

    def charge(self,k,n=1):
        amount=self.logical.get(k,0)+n
        if k in self.limits:self.guard(k,amount)
        self.logical[k]=amount

    def high(self,k,n):
        self.guard(k,n);self.logical[k]=max(self.logical.get(k,0),n)


def decode(wire, work, *, transport=False):
    work.guard('closure_bytes' if transport else 'object_bytes',len(wire))
    # Lexical depth guard before json.loads; quotes/escapes do not add depth.
    depth=0; string=False;escape=False
    for c in wire:
        if string:
            if escape:escape=False
            elif c==92:escape=True
            elif c==34:string=False
        elif c==34:string=True
        elif c in (91,123):depth+=1;work.guard('json_depth',depth)
        elif c in (93,125):depth-=1
    value=parse_document(wire,allow_opaque=True)
    todo=[value];nodes=0
    while todo:
        v=todo.pop();nodes+=1;work.guard('json_nodes',nodes)
        if isinstance(v,dict):
            todo.extend(v.values())
            for k in v:work.guard('string_bytes',len(k.encode()))
        elif isinstance(v,list):todo.extend(v)
        elif isinstance(v,str):
            # Transport base64 has a separate pre-decoding byte guard.
            work.guard('closure_bytes' if transport else 'string_bytes',len(v.encode()))
    return value,nodes


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
    values=[x['id'] for x in xs] if ids else xs
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
            for i,r in enumerate(v['uncertainty']['basis']):found.append((f'/uncertainty/basis/{i}',key(r,'nm.basis')))
        if kind=='nm.procedure.v1':
            for i,c in enumerate(v['conditions']):
                for j,r in enumerate(c.get('basis',[])):found.append((f'/conditions/{i}/basis/{j}',key(r,'nm.basis')))
    elif kind=='nm.evidence.v1':
        for i,r in enumerate(v['token_roles']['basis']):found.append((f'/token_roles/basis/{i}',key(r,'nm.basis')))
    return sorted(found)


class Graph:
    def __init__(self, invocation, load, pin, work):
        self.work=work;self.objects={};self.values={};self.nodes={};self.occurrences=[]
        self.root=ref('nm.invocation.v1',sha(invocation))
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
                wire=invocation if k==key(self.root) else load(k,work)
                work.high('object_bytes',len(wire));work.charge('capture_bytes',len(wire))
                if sha(wire)!=k[1]:fail('REFERENCE_DIGEST_MISMATCH',path,'phase_2')
                if k[0]=='nm.basis':v=None;nodes=0
                else:
                    v,nodes=decode(wire,work)
                    if v.get('schema')=='nm.prepared-build.v1':fail('NONEXECUTABLE_BUILD_WITNESS',path,'phase_1')
                    parse_document(wire,expected_schema=k[0])
                    if k[0]=='nm.resource-policy.v1':
                        if sha(wire)!=APPROVED_POLICY_SHA:fail('RESOURCE_POLICY_IDENTITY_MISMATCH',path,'phase_1')
                    else:
                        if k[0] not in BODIES:fail('PROFILE_MISMATCH',path,'phase_1')
                        shape(v,HEADER|set(BODIES[k[0]].split()),path)
                    ident=(k[0],v['id'],v['revision'])
                    if ident in identities and identities[ident]!=k[1]:fail('IDENTITY_VERSION_COLLISION',path,'phase_2')
                    identities[ident]=k[1]
                self.objects[k]=wire;self.values[k]=v;self.nodes[k]=nodes
                work.charge('json_nodes',nodes)
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
        work.charge('request_contexts',len(self.requests))
        self._integrity()

    def get(self,r):return self.values[key(r)]

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
                fail('AUTHORITY_REFERENCE_MISMATCH','adoption','phase_2')
        for qk in self.requests:
            q=self.values[qk];w.high('request_chain',q['revision'])
            previous=q['predecessor']
            if q['revision']==1:
                if previous is not None:fail('PREDECESSOR_VERSION_MISMATCH','predecessor','phase_2')
            else:
                if previous is None:fail('REQUIRED_REFERENCE_MISSING','predecessor','phase_2')
                p=self.get(previous)
                if p['id']!=q['id'] or p['revision']!=q['revision']-1:fail('PREDECESSOR_VERSION_MISMATCH','predecessor','phase_2')
            for field,code in [('hypotheses','HYPOTHESIS_SET_EMPTY'),('measurements','MEASUREMENT_SET_EMPTY')]:
                xs=q[field]
                if not xs:fail(code,field)
                if len(xs)>2:fail('NOMINATION_CARDINALITY_INVALID',field)
                ks=[key(r) for r in xs];ids=[self.get(r)['id'] for r in xs]
                if len(set(ks))!=len(ks):fail('DUPLICATE_NOMINATION_REFERENCE',field)
                if len(set(ids))!=len(ids):fail('DUPLICATE_NOMINATION_ID',field)
                if ids!=sorted(ids):fail('NOMINATION_ORDER_INVALID',field)
            ss=[(self.get(r)['id'],self.get(r)['revision']) for r in q['support']]
            if ss!=sorted(set(ss)):fail('ORDER_INVALID','support')
            # Scope is each Q, including ancestors. Sharing never inherits eligibility.
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
            self._joins(q)
        for v in self.values.values():
            if v:self._intrinsic(v)

    def _joins(self,q):
        shape(q['context'],'subject_entity_anchor_id variable_anchor_id assertion_context as_of scenario_label','context')
        local_id(q['context']['scenario_label'])
        for r in q['hypotheses']+q['measurements']+q['support']:
            v=self.get(r)
            if v['evidence']!=q['evidence'] or v['context']!=q['context']:fail('SUPPORT_SUBJECT_MISMATCH','context/evidence')
        for sr in q['support']:
            s=self.get(sr)
            if s['hypothesis'] not in q['hypotheses'] or s['procedure'] not in q['measurements'] or s['decoder']!=self.get(s['procedure'])['decoder']:
                fail('SUPPORT_SUBJECT_MISMATCH','support')
        for hr in q['hypotheses']:
            for pr in q['measurements']:
                if sum(self.get(s)['hypothesis']==hr and self.get(s)['procedure']==pr for s in q['support'])>2:
                    fail('SCHEMA_INVALID','support')
        hs=[self.get(r)['account_kind'] for r in q['hypotheses']]
        if len(set(hs))!=len(hs):fail('SEMANTIC_ALIAS','hypotheses')
        meanings=[]
        for r in q['measurements']:
            p=self.get(r);o=self.get(p['decoder'])
            meaning=[p['context'],p['method'],p['method_edition'],o['domain'],sorted([x['region'] for x in o['outcomes']],key=canonical_json_bytes),
                     [{k:v for k,v in c.items() if k!='id'} for c in p['conditions']]]
            encoded=canonical_json_bytes(meaning)
            if encoded in meanings:fail('SEMANTIC_ALIAS','measurements')
            meanings.append(encoded)

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
            if (v['method'],d['kind'],d['unit']) not in [('reference_scalar','scalar_finite_decimal','degree_celsius'),('nonspecific_code','literal_codes','code')]:fail('DECODER_INVALID','method')
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
        if kind=='nm.decoder.v1':self._decoder(v)
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
