"""Pure finite-world admission, not a governed workflow or recommendation API.

No projection/policy execution, CLI, comparison/replay adapter or file publication.
Complete governed workflow integration remains a separately authorized slice.
"""
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, UTC
import hashlib
import json
import re

from . import admission, governed_build
from .input import canonical_json_bytes as C, parse_request_wire, parse_snapshot_wire, effective_limits
from .projection_profile import validate_profile
from .policy_profile import validate_policy_structure, policy_values
from .decision_review import _admission_lookup_plan, _validator_rows
from .governed_contracts import D,S,A,T,I,Q,B,FIELDS,decode,validate,outline,reference,edges,SHA
from .governed_resources import Budget,Traversal,problem

H=lambda b:hashlib.sha256(b).hexdigest()

def _nodes(value):
    return 1+sum(_nodes(v) for v in (value.values() if isinstance(value,dict) else value if isinstance(value,list) else []))

def _instant(s):
    pattern=r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)'
    try:
        if not re.fullmatch(pattern,s) or s.endswith('-00:00'):raise ValueError()
        t=datetime.fromisoformat(s).astimezone(UTC)
        return t.isoformat(timespec='microseconds').replace('+00:00','Z')
    except (ValueError,OverflowError,TypeError) as e:
        raise problem('WORLD_REPRESENTATION_UNSUPPORTED',profile=True) from e

def _keys(q):
    w=deepcopy(q)
    for name in ('actor_assertion','request_id','requested_limits'):del w[name]
    w['current_condition_question']['as_of']=_instant(w['current_condition_question']['as_of'])
    world={'membership_schema':'singleton-world-key.v1','request':w}
    fixed=deepcopy(world)
    for k in ('gamma','beta'):
        p=fixed['request']['premises']['coordinates'][k]
        if p['value'] is not None:
            for endpoint in ('lower','upper'):p['value'][endpoint]={'var':k}
        p['canonical_commitment']={'derived':'coordinate_envelope_commitment'}
    return C(world),C(fixed)

class _Captured:
    def __init__(self,entries,budget):
        self.b=budget;self.items={};self.walker=Traversal(budget)
        for entry in entries:
            if type(entry) not in (tuple,list) or len(entry)!=2 or type(entry[0]) is not str or type(entry[1]) is not bytes:
                raise problem('AUTHORITY_REFERENCE_MISMATCH')
            kind,wire=entry
            # A captured occurrence has actual validation/dispatch work even when
            # its opaque body is empty or its bytes were already seen. This is
            # physical positive excess, not a refund against logical edge work.
            budget.work('context_nodes',1,scope='capture_record',extra=True)
            budget.work('capture_bytes',len(wire),scope='capture')
            if kind not in (*FIELDS,Q,B,'captured-basis'):raise problem('AUTHORITY_REFERENCE_MISMATCH')
            cap=budget.caps['snapshot_wire_bytes' if kind==B else 'request_wire_bytes']
            if len(wire)>cap:raise problem('INPUT_WIRE_LIMIT_EXCEEDED',resource=True)
            digest=H(wire)
            if digest not in self.items:
                budget.work('unique_objects',1,scope='capture')
                budget.work('unique_bytes',len(wire),scope='capture')
            with budget.operation('decode_object'):
                raw=wire if kind=='captured-basis' else decode(wire,cap,budget.caps)
            if digest in self.items and (kind,wire)!=self.items[digest][:2]:raise problem('AUTHORITY_AMBIGUOUS')
            if kind in FIELDS:
                outline(kind,raw)
                for _ in edges(kind,raw):budget.work('supplied_references',1,scope='capture')
            self.items[digest]=(kind,wire,raw,_nodes(raw) if kind!='captured-basis' else 1)

    def get(self,ref,kind):
        reference(ref,kind)
        try:v=self.items[ref['sha256']]
        except KeyError as e:raise problem('AUTHORITY_UNAVAILABLE') from e
        # Capture indexed immutable bytes by their actual hash; no repeated hash
        # work is hidden ahead of a per-edge reservation.
        if v[0]!=kind:raise problem('AUTHORITY_REFERENCE_MISMATCH')
        return v

    def visit(self,ref,kind,*,shallow=False,source=None):
        if source is not None:
            self.b.work('edge_visits',1,scope='reference')
        v=self.get(ref,kind)
        if source is not None:
            self.b.work('context_nodes',source[3]+v[3]+2,scope='reference')
            self.b.work('context_bytes',len(source[1])+len(v[1])+66,scope='reference')
        with self.walker.enter(ref['sha256'],(kind,'parent' if shallow else 'full')) as fresh:
            if fresh and not shallow and kind in FIELDS:
                for field,child,role in edges(kind,v[2]):
                    self.visit(child,role,shallow=field=='predecessor',source=v)
            if kind in (D,S) and not shallow and v[2]['predecessor'] is not None:
                parent=self.get(v[2]['predecessor'],kind)[2];idkey='declaration_id' if kind==D else 'scenario_id'
                if parent[idkey]!=v[2][idkey] or parent['revision']!=v[2]['revision']-1:raise problem('HISTORY_INCOMPATIBLE')
        return v[2]

@dataclass(frozen=True)
class GateAssessment:
    evaluation_permitted: bool
    disposition: str
    reason: str
    world_key: bytes
    fixed_key: bytes
    semantic_bytes: bytes
    physical_bytes: bytes
    scope: str='pure_nomination_not_workflow'

def assess(invocation_wire,objects,*,expected_authority_pin,limits=None,observer=None):
    """Captured bytes in, internal assessment out. No caller-provided admission flag.

    Comparison-bearing invocations intentionally refuse in this pure slice:
    their complete historical adapter is not implemented or authorized here.
    """
    budget=Budget(limits,observer)
    budget.work('capture_bytes',len(invocation_wire),scope='invocation')
    iv=validate(I,decode(invocation_wire,budget.caps['request_wire_bytes'],budget.caps))
    budget.world=H(invocation_wire)
    # Startup source inspection is separate from request/lower reconstruction units.
    def build_event(record):
        if observer:
            try:observer(dict(record,phase='startup_build',world=budget.world))
            except Exception as e:
                from .errors import refusal
                raise refusal('INTERNAL_ERROR',stage='internal_failure',target='instrumentation',retry='investigate',exit_code=7) from e
    build_wire,build_id=governed_build.identity(observer=build_event)
    if iv['build_identity']!=build_id:raise governed_build.unavailable()
    if len(build_wire)>budget.caps['build_bytes']:raise problem('OUTPUT_LIMIT_EXCEEDED',resource=True,target='build_bytes')
    budget.work('capture_bytes',len(build_wire),scope='build')
    budget.work('unique_objects',1,scope='build');budget.work('unique_bytes',len(build_wire),scope='build')
    if iv['comparison'] is not None:raise problem('HISTORY_INCOMPATIBLE')
    store=_Captured(objects,budget)
    # I is also a captured unique object; root references are not free metadata.
    ir={'kind':I,'sha256':H(invocation_wire)}
    if ir['sha256'] not in store.items:
        budget.work('unique_objects',1,scope='invocation');budget.work('unique_bytes',len(invocation_wire),scope='invocation')
    # Supplied I occurrences count even when a duplicate copy was captured.
    for _ in edges(I,iv):budget.work('supplied_references',1,scope='invocation')
    store.items[ir['sha256']]=(I,invocation_wire,iv,_nodes(iv))
    sc=store.get(iv['scenario'],S)[2];decl=store.get(sc['declaration'],D)[2]
    current_q=store.get(sc['request'],Q);current_b=store.get(sc['snapshot'],B)
    template_q=store.get(decl['template_request'],Q);template_b=store.get(decl['template_snapshot'],B)
    # Q/B public integrity and all present malformed support win over epistemic unknown.
    pairs=[(current_q,current_b)]
    if (current_q[1],current_b[1])!=(template_q[1],template_b[1]):pairs.append((template_q,template_b))
    for qi,bi in pairs:
        q,qp=parse_request_wire(qi[1]);bp=parse_snapshot_wire(bi[1]);lower=effective_limits(q)
        # Preserve every lower per-call cap. Only the separate application aggregate
        # uses the explicitly approved governed ceilings.
        refs=qp.counts.reference_occurrences+bp.counts.reference_occurrences
        charges=qp.counts.nodes+bp.counts.nodes+refs+_admission_lookup_plan(q,bp.raw)+_validator_rows(bp.raw)
        for dimension,delta in [('review_resolved_bytes',len(qi[1])+len(bi[1])),('review_reference_occurrences',refs),('review_resolution_charges',charges)]:
            budget.work(dimension,delta,scope='public_reconstruction')
        if charges>lower['input_resolution_charges']:raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target='input_resolution_charges')
        with budget.operation('public_reconstruction'):
            admission._admit_parsed(q,qp,bp)
        with budget.operation('profile_validation'):
            supports=validate_profile(q,lower);validate_policy_structure(q);policy_values(q,lower)
        if any(pair is not None and pair[0]!=pair[1] for pair in supports.values()):raise problem('GOVERNED_PROFILE_UNSUPPORTED',profile=True)
        _instant(qi[2]['current_condition_question']['as_of'])
    # Reference traversal is scoped. A completed node never replaces contextual joins.
    # Complete envelope checks occur after existing public Q/B guards. No omitted
    # present fields are converted to epistemic unknowns.
    for kind in (D,S,A,T,I):
        for stored_kind,wire,raw,nodes in store.items.values():
            if stored_kind==kind:
                validate(kind,raw)
                if kind==D and len(raw['pairs'])>budget.caps['membership_rows']:
                    raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target='membership_rows')
    if expected_authority_pin is None:raise problem('AUTHORITY_UNAVAILABLE')
    if type(expected_authority_pin) is not str or not SHA.fullmatch(expected_authority_pin) or iv['selection']['sha256']!=expected_authority_pin:
        raise problem('AUTHORITY_REFERENCE_MISMATCH')
    store.visit(ir,I)
    authority=store.get(iv['selection'],A)[2]
    if authority['scenario']!=iv['scenario'] or authority['declaration']!=sc['declaration']:raise problem('AUTHORITY_REFERENCE_MISMATCH')
    if authority['purpose']=='accepted_working_evaluation':
        if iv['adoption'] is None:raise problem('WORKING_ADOPTION_REQUIRED')
        adoption=store.get(iv['adoption'],T)[2]
        if any(adoption[k]!=v for k,v in [('scenario',iv['scenario']),('declaration',sc['declaration']),('selection',iv['selection'])]):raise problem('AUTHORITY_REFERENCE_MISMATCH')
    elif iv['adoption'] is not None:raise problem('AUTHORITY_REFERENCE_MISMATCH')
    envelopes=[iv,sc,decl,authority]+([store.get(iv['adoption'],T)[2]] if iv['adoption'] else [])
    budget.work('context_nodes',2*(current_q[3]+template_q[3])+sum(_nodes(x) for x in envelopes)+_nodes(decl['pairs']),scope='membership_join')
    budget.work('context_bytes',2*(len(current_q[1])+len(template_q[1]))+sum(len(C(x)) for x in envelopes)+len(C(decl['pairs'])),scope='membership_join')
    q=current_q[2];template=template_q[2]
    tw,tf=_keys(template);w,f=_keys(q)
    def complete(raw):
        g=raw['premises']['global_applicability']
        return g['availability']=='present' and g['value']['status'] is True and all(v['availability']=='present' for v in raw['premises']['coordinates'].values())
    if not complete(template):raise problem('DECLARATION_SCHEMA_INVALID',profile=True)
    ga=q['premises']['global_applicability']
    if ga['availability']!='present':disposition,reason='applicability_unknown','global_applicability_unknown'
    elif ga['value']['status'] is False:disposition,reason='declaration_not_applicable','fixed_scope_mismatch'
    elif any(v['availability']!='present' for v in q['premises']['coordinates'].values()):disposition,reason='admissibility_unknown','missing_or_unknown_premise'
    elif f!=tf:disposition,reason='declaration_not_applicable','fixed_scope_mismatch'
    else:
        pair={k:q['premises']['coordinates'][k]['value']['lower'] for k in ('gamma','beta')}
        # Entire table cost reserved; no favorable early-match accounting refund.
        member=any(pair==p for p in decl['pairs'])
        disposition,reason=('admissible','finite_pair_member') if member else ('inadmissible','outside_declared_pairs')
    permit=disposition=='admissible'
    sem=C({'scope':'pure_nomination_not_workflow','invocation':H(invocation_wire),'evaluation_permitted':permit,
           'disposition':disposition,'reason':reason,'world_sha256':H(w),'fixed_sha256':H(f),'logical':budget.logical})
    return GateAssessment(permit,disposition,reason,w,f,sem,budget.summary())
