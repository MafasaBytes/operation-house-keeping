"""Closed D/S/A/T/I contracts from the approved prose; not a rule interpreter."""
import json
import re
from .input import canonical_json_bytes, _pairs, BUILD_LIMITS
from .preflight import scan
from .projection_profile import bounded_fraction
from .governed_resources import problem

D='finite-declaration.v1'; S='governed-scenario.v1'; A='local-authority-selection.v1'
T='local-working-adoption.v1'; I='governed-invocation.v1'; Q='bdw001.1'; B='public-snapshot'
SHA=re.compile(r'[0-9a-f]{64}\Z'); ID=re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z')
FIELDS={D:'schema declaration_id revision predecessor membership_profile template_request template_snapshot pairs provenance',
 S:'schema scenario_id revision predecessor change_kind request snapshot declaration',
 A:'schema declaration scenario purpose attestation', T:'schema declaration scenario selection attestation',
 I:'schema scenario selection adoption comparison build_identity'}
EDGES={D:{'predecessor':D,'template_request':Q,'template_snapshot':B},
 S:{'predecessor':S,'request':Q,'snapshot':B,'declaration':D},
 A:{'declaration':D,'scenario':S},T:{'declaration':D,'scenario':S,'selection':A},
 I:{'scenario':S,'selection':A,'adoption':T,'comparison':'prior-bundle-manifest'}}

def exact(x,keys,code):
    if type(x) is not dict or set(x)!=set(keys.split()):raise problem(code,profile=code=='DECLARATION_SCHEMA_INVALID')

def reference(x,kind):
    exact(x,'kind sha256','AUTHORITY_REFERENCE_MISMATCH')
    if x['kind']!=kind or type(x['sha256']) is not str or not SHA.fullmatch(x['sha256']):
        raise problem('AUTHORITY_REFERENCE_MISMATCH')

def decode(wire,cap=32768,limits=None):
    if type(wire) is not bytes or len(wire)>cap:
        raise problem('INPUT_WIRE_LIMIT_EXCEEDED',resource=True)
    lexical=dict(BUILD_LIMITS)
    if limits:
        lexical.update(input_json_nodes_per_file=limits['lower_nodes_per_file'],
                       input_json_depth=limits['input_json_depth'],input_max_string_bytes=limits['input_max_string_bytes'])
    scan(wire,lexical)
    def integer(s):
        if len(s.lstrip('-'))>(limits['integer_digits'] if limits else 128):raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target='integer_digits')
        return int(s)
    try:raw=json.loads(wire,object_pairs_hook=_pairs,parse_int=integer)
    except (ValueError,UnicodeError) as e:raise problem('REQUEST_SCHEMA_INVALID') from e
    if canonical_json_bytes(raw)!=wire:raise problem('REQUEST_CANONICAL_FORM_REQUIRED')
    return raw

def validate(kind,x):
    code='DECLARATION_SCHEMA_INVALID' if kind==D else 'AUTHORITY_REFERENCE_MISMATCH'
    if kind not in FIELDS:raise problem('GOVERNED_PROFILE_UNSUPPORTED',profile=True)
    exact(x,FIELDS[kind],code)
    if x['schema']!=kind:raise problem('GOVERNED_PROFILE_UNSUPPORTED',profile=True)
    for field,k in EDGES[kind].items():
        if x[field] is None and field in ('predecessor','adoption','comparison'):continue
        reference(x[field],k)
    if kind in (D,S):
        name='declaration_id' if kind==D else 'scenario_id'
        if type(x[name]) is not str or not ID.fullmatch(x[name]):raise problem(code)
        if type(x['revision']) is not int or x['revision']<1:raise problem('HISTORY_INCOMPATIBLE')
        if (x['revision']==1)!=(x['predecessor'] is None):raise problem('HISTORY_INCOMPATIBLE')
    if kind==D:
        if x['membership_profile']!='singleton-gamma-beta.v1':raise problem('GOVERNED_PROFILE_UNSUPPORTED',profile=True)
        p=x['pairs']
        if type(p) is not list or not 1<=len(p)<=4:raise problem(code,profile=True)
        order=[]
        for pair in p:
            exact(pair,'gamma beta',code)
            try:order.append(tuple(bounded_fraction(pair[k],128) for k in ('gamma','beta')))
            except Exception as e:
                if getattr(getattr(e,'diagnostic',None),'exit_code',None)==4:raise
                raise problem(code,profile=True) from e
        if order!=sorted(set(order)):raise problem(code,profile=True)
        exact(x['provenance'],'kind basis basis_artifacts',code)
        v=x['provenance']
        if v['kind']!='owner_declared_synthetic' or type(v['basis']) is not str or type(v['basis_artifacts']) is not list:raise problem(code)
        for ref in v['basis_artifacts']:reference(ref,'captured-basis')
    if kind==S and x['change_kind'] not in ('initial','premise','policy','context','evidence','declaration','presentation','mixed'):
        raise problem(code)
    if kind in (A,T):
        keys='issuer_label authenticated basis '+('declaration_approved purpose_approved' if kind==A else 'adopted_as_working')
        v=x['attestation'];exact(v,keys,code)
        if any(type(v[k]) is not str for k in ('issuer_label','basis')) or v['authenticated'] is not False:raise problem(code)
        if any(v[k] is not True for k in (['declaration_approved','purpose_approved'] if kind==A else ['adopted_as_working'])):raise problem(code)
        if kind==A and x['purpose'] not in ('hypothetical_evaluation','accepted_working_evaluation'):raise problem(code)
    if kind==I and (type(x['build_identity']) is not str or not SHA.fullmatch(x['build_identity'])):raise problem(code)
    return x

def outline(kind,x):
    """Only the shape needed to locate Q/B; semantic validation follows Q/B guards."""
    code='DECLARATION_SCHEMA_INVALID' if kind==D else 'AUTHORITY_REFERENCE_MISMATCH'
    exact(x,FIELDS[kind],code)
    if x['schema']!=kind:raise problem('GOVERNED_PROFILE_UNSUPPORTED',profile=True)
    for field,role in EDGES[kind].items():
        if x[field] is None and field in ('predecessor','comparison','adoption'):continue
        reference(x[field],role)
    if kind==D:
        exact(x['provenance'],'kind basis basis_artifacts',code)
        if type(x['provenance']['basis_artifacts']) is not list:raise problem(code)
        for ref in x['provenance']['basis_artifacts']:reference(ref,'captured-basis')

def edges(kind,x):
    result=[(k,v,EDGES[kind][k]) for k,v in sorted(x.items()) if k in EDGES[kind] and v is not None]
    if kind==D:
        result += [('provenance.basis_artifacts.'+str(i),v,'captured-basis') for i,v in enumerate(x['provenance']['basis_artifacts'])]
    # Field order is canonical, but an array retains numerical index order.
    return sorted(result,key=lambda e:tuple(int(p) if p.isdigit() else p for p in e[0].split('.')))
