"""Versioned application-only reservations. No legacy limit mutation or event log."""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
from types import MappingProxyType

from .errors import refusal, WorkflowDiagnostic, WorkflowInputError
from .input import canonical_json_bytes

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = 'docs/superpowers/reports/2026-09-16-maintained-admissibility-amendment/policy.json'
POLICY_SHA = '5ae1abf84ad474020d11de6e1eb22e58aef96fddf8d942caca2eb98ace6b17d2'

def policy():
    from .build import unavailable
    try:
        with (ROOT / POLICY_PATH).open('rb') as f:wire=f.read(1319)
    except OSError as e:raise unavailable() from e
    if len(wire)!=1318 or hashlib.sha256(wire).hexdigest() != POLICY_SHA:raise unavailable()
    return json.loads(wire)['limits']

def problem(code, *, resource=False, target='invocation', profile=False):
    stage=('output_resource' if code=='OUTPUT_LIMIT_EXCEEDED' else 'wire_resource' if resource else
                   'profile_cardinality_edition' if profile else 'commitment_public_reconstruction')
    return WorkflowInputError(WorkflowDiagnostic(code,stage,target,code.lower(),
                              'reduce_input' if resource else 'correct_input',4 if resource else 3,'absent'))

def bounded_json(value,cap,target):
    """Fixed closed summary/output objects, bounded before each encoded append."""
    out=bytearray()
    for piece in json.JSONEncoder(sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).iterencode(value):
        wire=piece.encode()
        if len(out)+len(wire)>cap:raise problem('OUTPUT_LIMIT_EXCEEDED',resource=True,target=target)
        out.extend(wire)
    return bytes(out)

class Budget:
    """Per-call counters; observer is a trusted test seam, not supplied authority.

    No caching refund. An extra physical unit reserves its own positive charge.
    This pure-slice summary is NOT a complete workflow physical-work.v1 record.
    """
    def __init__(self, limits=None, observer=None):
        caps=policy()
        if limits is not None and type(limits) is not dict:
            raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target='requested_limits')
        for k,v in (limits or {}).items():
            if k not in caps or type(v) is not int or not 0 <= v <= caps[k]:
                raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target='requested_limits')
            caps[k]=v
        self.caps=MappingProxyType(caps)
        self.logical={k:0 for k in caps}
        self.actual={k:0 for k in caps}
        self.extra={k:0 for k in caps}
        self.minimum={}
        self.physical={'cache_hits':0}
        self.operations={}
        self.world=None
        self.observer=observer

    def _event(self,k,delta,before,after,scope,outcome):
        if self.observer:
            try:
                self.observer({'phase':'reservation','scope':scope,'dimension':k,
                               'world':self.world,
                               'delta':delta,'before':before,'after':after,
                               'cap':self.caps[k],'outcome':outcome})
            except Exception as e:
                raise refusal('INTERNAL_ERROR',stage='internal_failure',target='instrumentation',
                              retry='investigate',exit_code=7) from e

    def work(self,k,delta,*,scope,extra=False):
        if k not in self.caps or type(delta) is not int or delta<0:
            raise ValueError('invalid internal reservation')
        before=self.logical[k]+self.extra[k];after=before+delta
        reserved=max(self.logical[k]+(0 if extra else delta),self.minimum.get(k,0))+self.extra[k]+(delta if extra else 0)
        if reserved>self.caps[k]:
            self._event(k,delta,before,before,scope,'refused')
            code='GRAPH_REFERENCE_LIMIT_EXCEEDED' if k=='supplied_references' else 'INPUT_RESOURCE_LIMIT_EXCEEDED'
            raise problem(code,resource=True,target=k)
        self._event(k,delta,before,after,scope,'reserved')
        (self.extra if extra else self.logical)[k]+=delta
        self.actual[k]+=delta
        self._event(k,delta,before,after,scope,'completed')

    def require_floor(self,minimum):
        """Trusted deterministic schedule floor; never offsets positive excess."""
        for k,v in minimum.items():
            if k not in self.caps or type(v) is not int or v<0:raise ValueError('invalid internal floor')
            if max(v,self.logical[k])+self.extra[k]>self.caps[k]:
                self._event(k,v,self.logical[k]+self.extra[k],self.logical[k]+self.extra[k],'required_schedule','refused')
                raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target=k)
        self.minimum.update({k:max(v,self.minimum.get(k,0)) for k,v in minimum.items()})

    def depth(self,n):
        if n>self.caps['active_depth']:
            raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target='active_depth')
        self.logical['active_depth']=max(n,self.logical['active_depth'])
        self.actual['active_depth']=max(n,self.actual['active_depth'])

    def summary(self):
        wire=bounded_json({'schema':'pure-admission-work.v1','coverage':'reservations_and_pure_admission_only',
            'actual':self.actual,'extra':self.extra,
            'charged':{k:self.logical[k]+self.extra[k] for k in self.caps},
            'cache_hits':self.physical['cache_hits'],'operations':self.operations},
            self.caps['physical_evidence_bytes'],'physical_evidence_bytes')
        return wire

    @contextmanager
    def operation(self,name):
        # Fixed internal inventory; never accepts an input-supplied operation name.
        if name not in ('decode_object','public_reconstruction','profile_validation','membership',
                        'envelope_validation','graph_validation','projection_plan','policy_assessment',
                        'row_review','output_construction'):
            raise ValueError('unknown internal operation')
        counts=self.operations.setdefault(name,{'started':0,'completed':0,'failed':0})
        def emit(outcome):
            if self.observer:
                try:self.observer({'phase':'operation','scope':name,'world':self.world,'outcome':outcome})
                except Exception as e:
                    raise refusal('INTERNAL_ERROR',stage='internal_failure',target='instrumentation',retry='investigate',exit_code=7) from e
        emit('started');counts['started']+=1
        try:yield
        except BaseException:
            counts['failed']+=1;emit('failed');raise
        else:
            counts['completed']+=1;emit('completed')

class Traversal:
    """Active-path identity is separate from completed, scope-qualified reuse."""
    def __init__(self,budget):
        self.budget=budget;self.active=set();self.complete=set()

    @contextmanager
    def enter(self,digest,scope):
        if digest in self.active:raise problem('HISTORY_INCOMPATIBLE')
        key=(digest,scope)
        if key in self.complete:
            self.budget.physical['cache_hits']+=1
            yield False
            return
        self.budget.depth(len(self.active)+1)
        self.budget.work('scope_expansions',1,scope=str(scope))
        self.active.add(digest)
        try:
            yield True
        except BaseException:
            raise
        else:
            self.complete.add(key)
        finally:
            self.active.remove(digest)
