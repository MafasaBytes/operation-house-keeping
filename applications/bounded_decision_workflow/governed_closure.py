"""Bounded in-memory carried-file integrity. No filesystem or replay execution.

Integrity is not gate permission: the workflow must re-admit every returned world
and recompute its result. All bytes are supplied, never resolved through paths.
"""
import base64
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

from .governed_resources import Budget, problem, bounded_json
from .governed_contracts import I,Q,B,S,validate,reference,outline
from .governed_admission import _keys,_nodes
from .input import BUILD_LIMITS,canonical_json_bytes as C,_pairs,parse_request_wire
from .preflight import scan

H=lambda b:hashlib.sha256(b).hexdigest()
FILES={'request.json':I,'snapshot.json':B,'resolved-input.json':'governed-closure.v2',
       'result.json':'governed-result.v2','trace.json':'governed-trace.v2','build.json':'build-witness'}
CAPS={'request.json':'request_wire_bytes','snapshot.json':'snapshot_wire_bytes',
      'resolved-input.json':'resolved_container_bytes','result.json':'result_bytes',
      'trace.json':'trace_bytes','build.json':'build_bytes','manifest.json':'manifest_bytes'}
SCHEMAS={'resolved-input.json':'closure','result.json':'result','trace.json':'trace','manifest.json':'manifest'}
SCHEMA_PATH=Path(__file__).resolve().parents[2]/'docs/superpowers/reports/2026-09-16-maintained-admissibility-amendment/schemas.json'
SCHEMA_SHA='2485ccc25ac50379886a1a6a8819441991555d2ff8c36a0c2cca8032f2259069'

def incompatible():return problem('HISTORY_INCOMPATIBLE')

def schemas():
    try:
        with SCHEMA_PATH.open('rb') as f:wire=f.read(60656)
    except OSError as e:raise incompatible() from e
    if len(wire)!=60655 or H(wire)!=SCHEMA_SHA:raise incompatible()
    return json.loads(wire)['$defs']

def shape(value,schema,defs):
    """Closed frozen wire-shape predicates, not an admissibility rule language."""
    if type(schema) is bool:return schema
    if '$ref' in schema:return shape(value,defs[schema['$ref'].split('/')[-1]],defs)
    if 'allOf' in schema and not all(shape(value,s,defs) for s in schema['allOf']):return False
    for key in ('oneOf','anyOf'):
        if key in schema:
            n=sum(shape(value,s,defs) for s in schema[key])
            if not (n==1 if key=='oneOf' else n>0):return False
    if 'const' in schema and (type(value)!=type(schema['const']) or value!=schema['const']):return False
    if 'enum' in schema and not any(type(value)==type(x) and value==x for x in schema['enum']):return False
    types={'object':dict,'array':list,'integer':int,'boolean':bool,'string':str,'null':type(None)}
    if 'type' in schema and type(value)!=types[schema['type']]:return False
    if type(value) is dict:
        if not set(schema.get('required',()))<=value.keys():return False
        if not schema.get('minProperties',0)<=len(value)<=schema.get('maxProperties',10**9):return False
        for k,v in value.items():
            if 'propertyNames' in schema and not shape(k,schema['propertyNames'],defs):return False
            sub=schema.get('properties',{}).get(k,schema.get('additionalProperties',{}))
            if sub is False or (type(sub) is dict and not shape(v,sub,defs)):return False
    if type(value) is list:
        if not schema.get('minItems',0)<=len(value)<=schema.get('maxItems',10**9):return False
        prefix=schema.get('prefixItems',[])
        if any(not shape(v,prefix[i] if i<len(prefix) else schema.get('items',{}),defs) for i,v in enumerate(value)):return False
    if type(value) is int and not schema.get('minimum',value)<=value<=schema.get('maximum',value):return False
    if type(value) is str:
        if len(value)>schema.get('maxLength',len(value)):return False
        if 'pattern' in schema and re.search(schema['pattern'],value) is None:return False
    return True

def decode_file(wire,name,budget,defs):
    if type(wire) is not bytes:raise incompatible()
    if len(wire)>budget.caps[CAPS[name]]:raise problem('INPUT_WIRE_LIMIT_EXCEEDED',resource=True,target=CAPS[name])
    limits=dict(BUILD_LIMITS)
    limits.update(input_json_nodes_per_file=budget.caps['resolved_container_nodes'] if name=='resolved-input.json' else
                  budget.caps['result_nodes'] if name=='result.json' else budget.caps['lower_nodes_per_file'],
                  input_json_depth=budget.caps['input_json_depth'],input_max_string_bytes=budget.caps['input_max_string_bytes'])
    counts=scan(wire,limits)
    budget.work('context_nodes',counts['nodes'],scope='carried_decode')
    def integer(s):
        if len(s.lstrip('-'))>budget.caps['integer_digits']:raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target='integer_digits')
        return int(s)
    try:v=json.loads(wire,object_pairs_hook=_pairs,parse_int=integer)
    except (ValueError,UnicodeError) as e:raise incompatible() from e
    if C(v)!=wire:raise incompatible()
    if name in SCHEMAS and not shape(v,defs[SCHEMAS[name]],defs):raise incompatible()
    return v

@dataclass(frozen=True)
class CarriedWorld:
    files: dict
    closure: dict
    result: dict
    trace: dict

@dataclass(frozen=True)
class Carried:
    files: dict
    worlds: tuple
    reconstructed_bytes: int

def validate_carried(files,*,expected_manifest,expected_build,budget):
    """Recover and verify complete seven-file ancestors, oldest first.

    Callers cannot supply validation status. This function establishes byte and
    shape integrity only, not numerical truth or admissibility.
    """
    if type(files) is not dict or set(files)!=set(CAPS) or any(type(v) is not bytes for v in files.values()):raise incompatible()
    total=sum(map(len,files.values()))
    budget.work('prior_capture_bytes',total,scope='prior_capture')
    budget.work('capture_bytes',total,scope='prior_capture')
    defs=schemas();worlds=[];active=set();reconstructed=0
    def inspect(f,expected):
        nonlocal reconstructed
        if H(f['manifest.json'])!=expected or expected in active:raise incompatible()
        budget.depth(len(active)+1);active.add(expected)
        total=sum(map(len,f.values()))
        if total>budget.caps['retention_bytes']:raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target='retention_bytes')
        budget.work('reconstruction_bytes',total,scope='prior_reconstruction')
        budget.work('context_bytes',total,scope='prior_reconstruction')
        decoded={name:decode_file(wire,name,budget,defs) for name,wire in f.items()}
        m=decoded['manifest.json'];z=decoded['resolved-input.json'];r=decoded['result.json'];t=decoded['trace.json'];iv=decoded['request.json']
        validate(I,iv)
        if f['build.json']!=expected_build or m['build_identity']!=H(expected_build) or iv['build_identity']!=H(expected_build):raise incompatible()
        for name,entry in m['files'].items():
            if entry!={'bytes':len(f[name]),'sha256':H(f[name])}:raise incompatible()
        if m['semantic_commitments']!={name:H(f[name]) for name in ('result.json','trace.json')}:raise incompatible()
        if r['build_identity']!=H(expected_build) or r['invocation']!=z['invocation'] or t['invocation']!=z['invocation']:raise incompatible()
        if z['invocation']!={'kind':I,'sha256':H(f['request.json'])} or z['expected_authority_pin']!=iv['selection']['sha256']:raise incompatible()
        if r['decision_review']['rows']!=t['rows']:raise incompatible()
        work=m['run_metadata']['operation_work'];logical=r['resource_accounting']
        if H(C(logical))!=work['logical_commitment']:raise incompatible()
        if len(C(work))>budget.caps['physical_evidence_bytes']:raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target='physical_evidence_bytes')
        for k in work['charged']:
            if work['charged'][k]!=logical[k]+work['extra'][k] or work['actual'][k]>work['charged'][k]:raise incompatible()
        table=z['objects'];expanding=set();cache={}
        def recover(h,kind):
            if h in expanding or h not in table:raise incompatible()
            e=table[h]
            if e['kind']!=kind:raise incompatible()
            if h in cache:return cache[h]
            expanding.add(h);budget.depth(len(active)+len(expanding))
            if 'canonical_json' in e:wire=bounded_json(e['canonical_json'],budget.caps['resolved_container_bytes'],'resolved_container_bytes')
            elif 'opaque_chunks' in e:
                try:wire=base64.b64decode(''.join(e['opaque_chunks']),validate=True)
                except ValueError as exc:raise incompatible() from exc
            else:
                if kind!='governed-closure.v2':raise incompatible()
                p=e['recipe'];members=p['members']
                if members!=sorted(set(members)) or any(x not in table for x in members):raise incompatible()
                # A recipe preserves entries, including nested recipes, exactly;
                # it does not flatten or substitute their reconstructed values.
                v={'schema':'governed-closure.v2','invocation':p['invocation'],'expected_authority_pin':p['expected_authority_pin'],
                   'objects':{x:table[x] for x in members},'world_witnesses':p['world_witnesses']}
                wire=bounded_json(v,budget.caps['resolved_container_bytes'],'resolved_container_bytes')
            if H(wire)!=h:raise incompatible()
            expanding.remove(h);cache[h]=wire;return wire
        for h,e in table.items():recover(h,e['kind'])
        allowed={I,Q,B,'finite-declaration.v1','governed-scenario.v1','local-authority-selection.v1',
                 'local-working-adoption.v1','captured-basis','governed-closure.v2','governed-manifest.v2',
                 'governed-result.v2','governed-trace.v2','build-witness'}
        for h,e in table.items():
            if e['kind'] not in allowed:raise incompatible()
            if e['kind']=='build-witness' and recover(h,e['kind'])!=expected_build:raise incompatible()
            if e['kind'] in ('governed-manifest.v2','governed-result.v2','governed-trace.v2'):
                key={'governed-manifest.v2':'manifest','governed-result.v2':'result','governed-trace.v2':'trace'}[e['kind']]
                if not shape(json.loads(recover(h,e['kind'])),defs[key],defs):raise incompatible()
        if recover(z['invocation']['sha256'],I)!=f['request.json']:raise incompatible()
        scenario=json.loads(recover(iv['scenario']['sha256'],'governed-scenario.v1'))
        outline(S,scenario)
        if recover(scenario['snapshot']['sha256'],B)!=f['snapshot.json']:raise incompatible()
        payload_bytes=len(recover(scenario['request']['sha256'],Q))+len(f['snapshot.json'])+len(f['result.json'])+len(f['trace.json'])
        budget.work('prior_reconstruction_payload_bytes',payload_bytes,scope='prior_callable_payload')
        for witness in z['world_witnesses']:
            reference(witness['request'],Q)
            qw=recover(witness['request']['sha256'],Q);parse_request_wire(qw)
            q=json.loads(qw);w,fx=_keys(q)
            if H(w)!=witness['world_sha256'] or H(fx)!=witness['fixed_sha256']:raise incompatible()
        if iv['comparison'] is not None:
            mr=iv['comparison'];reference(mr,'prior-bundle-manifest')
            mw=recover(mr['sha256'],'governed-manifest.v2');pm=decode_file(mw,'manifest.json',budget,defs)
            pf={name:recover(v['sha256'],FILES[name]) for name,v in pm['files'].items()};pf['manifest.json']=mw
            inspect(pf,mr['sha256'])
        expected_witnesses=[]
        for old in worlds:
            expected_witnesses.append(old.closure['world_witnesses'][-1])
        qr=scenario['request'];w,fx=_keys(json.loads(recover(qr['sha256'],Q)))
        expected_witnesses.append({'recipe':'approved-W-F.v1','request':qr,'world_sha256':H(w),'fixed_sha256':H(fx)})
        if z['world_witnesses']!=expected_witnesses:raise incompatible()
        reconstructed+=total;worlds.append(CarriedWorld(dict(f),z,r,t));active.remove(expected)
    inspect(files,expected_manifest)
    return Carried(dict(files),tuple(worlds),reconstructed)
