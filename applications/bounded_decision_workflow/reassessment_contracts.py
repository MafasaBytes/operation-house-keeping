"""Closed reassessment v2 input grammar, without admission or interpretation."""
import re
from datetime import datetime

from .measurement_wire import (BODIES as NM_BODIES, HEADER as NM_HEADER,
    edges as nm_edges, shape, key, local_id, basis, rational, fail, Work, DIAGNOSTIC_CEILING)
from .measurement_contracts import PROFILE as NM_PROFILE, parse_document, canonical_json_bytes
from .measurement_wire import sha

PROFILE = 'measurement-reassessment/v2'
HEADER = {'schema', 'profile', 'id', 'revision', 'predecessor'}
BODIES = {
    'nr.invocation.v2': 'request authority build resource_policy',
    'nr.request.v2': 'original_invocation original_selection_pin procedure decoder observation execution exposure interpretation policy',
    'nr.observation.v2': 'evidence procedure decoder provenance',
    'nr.execution.v2': 'observation original_context result_context acquisition conditions',
    'nr.exposure.v2': 'original_invocation observation prior_bundle declared_relation declared_prediction_commitment_at declared_first_learned_at basis',
    'nr.authority.v2': 'request purpose permission attestor_label basis',
    'nr.policy.v2': 'qualification envelope_rule baseline_rule adoption exposure_rule',
    'nr.build.v2': 'checkpoint source_manifest environment_manifest entrypoint contract_sha256 resource_policy_sha256 supported_nm_contract_sha256',
    'nr.retained-bundle.v2': 'files closure',
}
KINDS = set(BODIES) | set(NM_BODIES) | {'nm.basis', 'nm.resource-policy.v1'}
FILES = ('invocation.json','closure.json','result.json','trace.json','build.json','policy.json','manifest.json')
ROLES = dict(zip(FILES, ('nm.invocation.v1',None,'nm.basis','nm.basis','nm.build.v1','nm.resource-policy.v1','nm.basis')))
CAPS = dict(zip(FILES, ('invocation_bytes','closure_bytes','result_bytes','trace_bytes','build_bytes','object_bytes','manifest_bytes')))


def checked_limits(overrides):
    """Validate historical policy without replacing the caller's error budget."""
    token=DIAGNOSTIC_CEILING.set(DIAGNOSTIC_CEILING.get())
    try:return Work(overrides)
    finally:DIAGNOSTIC_CEILING.reset(token)


def typed(r, kind=None):
    k = key(r, kind)
    if k[0] not in KINDS:
        fail('REFERENCE_ROLE_MISMATCH', '/reference', 'phase_2')
    return k


def digest(value, path):
    if type(value) is not str or not re.fullmatch('[0-9a-f]{64}', value):
        fail('SCHEMA_INVALID', path, 'phase_1')


def text(value, path):
    if type(value) is not str:
        fail('SCHEMA_INVALID', path, 'phase_1')


def timestamp(value, path):
    if value is None:
        return
    text(value, path)
    try:
        if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt][0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:[Zz]|\+00:00)',value):
            raise ValueError()
        if datetime.fromisoformat(value[:-1]+'Z' if value.endswith('z') else value).utcoffset().total_seconds()!=0:raise ValueError()
    except ValueError:
        fail('SCHEMA_INVALID', path, 'phase_1')


def context(value):
    shape(value, 'subject_entity_anchor_id variable_anchor_id assertion_context as_of scenario_label', '/context')
    for field in ('subject_entity_anchor_id','variable_anchor_id','scenario_label'):
        text(value[field], '/context/'+field)
    local_id(value['scenario_label'])
    shape(value['assertion_context'], 'kind view', '/context/assertion_context')
    if value['assertion_context']['kind'] != 'lifecycle_view':
        fail('SCHEMA_INVALID', '/context/assertion_context', 'phase_1')
    text(value['assertion_context']['view'], '/context/assertion_context/view')
    timestamp(value['as_of'], '/context/as_of')
    if value['as_of'] is None:fail('SCHEMA_INVALID','/context/as_of','phase_1')


def validate(value, kind, wire, work):
    """Closed shapes and intrinsic numerical grammar, never lo <= x <= hi."""
    if kind == 'nm.basis':return
    if value.get('schema') in ('nr.prepared-build.v2', 'nm.prepared-build.v1'):
        fail('NONEXECUTABLE_BUILD_WITNESS', '/build', 'phase_1')
    if value.get('schema') != kind:
        fail('REFERENCE_ROLE_MISMATCH', '/schema', 'phase_2')
    if kind.startswith('nm.'):
        parse_document(wire, expected_schema=kind, work=work)
        if kind in NM_BODIES:
            required = NM_HEADER | set(NM_BODIES[kind].split())
            if kind != 'nm.request.v1' or not required <= set(value):shape(value,required,'/object')
        if kind=='nm.request.v1':
            if value['revision']==1 and value['predecessor'] is not None:fail('PREDECESSOR_VERSION_MISMATCH','/predecessor','phase_2')
            if value['revision']>1 and value['predecessor'] is None:fail('REQUIRED_REFERENCE_MISSING','/predecessor','phase_2')
        return
    if value.get('profile') != PROFILE:fail('PROFILE_MISMATCH','/profile','phase_1')
    shape(value, HEADER | set(BODIES[kind].split()), '/object')
    local_id(value['id'])
    revision = value['revision']
    if type(revision) is not int or revision < 1:fail('REVISION_INVALID','/revision','phase_1')
    if revision == 1 and value['predecessor'] is not None:
        fail('PREDECESSOR_VERSION_MISMATCH','/predecessor','phase_2')
    if revision > 1 and value['predecessor'] is None:
        fail('REQUIRED_REFERENCE_MISSING','/predecessor','phase_2')
    if value['predecessor'] is not None:typed(value['predecessor'],kind)
    if kind == 'nr.request.v2':
        digest(value['original_selection_pin'],'/original_selection_pin')
        u=value['interpretation'];shape(u,'kind lo hi unit basis','/interpretation')
        if u['kind'] not in ('declared_point','hard_interval','unknown','confidence_only'):
            fail('SCHEMA_INVALID','/interpretation/kind','phase_1')
        basis(u['basis'], 1 if u['kind'] in ('declared_point','hard_interval') else 0)
        shape(u['unit'],'system_id system_edition code','/interpretation/unit')
        for item in u['unit'].values():text(item,'/interpretation/unit')
        for f in ('lo','hi'):
            if u['kind']=='hard_interval':rational(u[f],work)
            elif u[f] is not None:fail('SCHEMA_INVALID','/interpretation/'+f,'phase_1')
    elif kind == 'nr.observation.v2':basis(value['provenance'],1)
    elif kind == 'nr.authority.v2':
        if value['purpose']!='result_reassessment' or value['permission'] not in ('true','false','unknown'):
            fail('SCHEMA_INVALID','/authority','phase_1')
        text(value['attestor_label'],'/attestor_label');basis(value['basis'],1)
    elif kind == 'nr.execution.v2':
        context(value['original_context']);context(value['result_context'])
        a=value['acquisition'];shape(a,'state start end basis','/acquisition')
        if a['state'] not in ('known','unknown'):fail('SCHEMA_INVALID','/acquisition/state','phase_1')
        timestamp(a['start'],'/acquisition/start');timestamp(a['end'],'/acquisition/end');basis(a['basis'])
        cs=value['conditions']
        if type(cs) is not list or len(cs)!=5:fail('SCHEMA_INVALID','/conditions','phase_1')
        for c,expected in zip(cs,('applicability','availability','calibration','fidelity','hold')):
            shape(c,'id state basis','/conditions')
            if c['id']!=expected or c['state'] not in ('true','false','unknown'):fail('SCHEMA_INVALID','/conditions','phase_1')
            basis(c['basis'],1 if c['state']!='unknown' else 0)
    elif kind == 'nr.exposure.v2':
        if value['declared_relation'] not in ('unknown','predictions_before_learning_result','predictions_after_learning_result'):
            fail('SCHEMA_INVALID','/declared_relation','phase_1')
        basis(value['basis'],0 if value['declared_relation']=='unknown' else 1)
        for f in ('declared_prediction_commitment_at','declared_first_learned_at'):timestamp(value[f],'/'+f)
    elif kind == 'nr.policy.v2':
        expected=dict(qualification='supplied_support/v1',envelope_rule='all_intersecting_branches/v1',baseline_rule='frozen_baseline_first/v1',adoption='manual_only',exposure_rule='local_declarations_not_custody/v1')
        if any(value[k]!=v for k,v in expected.items()):fail('SCHEMA_INVALID','/policy','phase_1')
    elif kind == 'nr.build.v2':
        body={k:value[k] for k in BODIES[kind].split()}
        body_digest=sha(canonical_json_bytes(body),work)
        if value['revision']!=1 or value['id']!=body_digest:
            fail('BUILD_IDENTITY_MISMATCH','/build/id','phase_1')
        if type(value['checkpoint']) is not str or not re.fullmatch('[0-9a-f]{40}',value['checkpoint']):
            fail('SCHEMA_INVALID','/build/checkpoint','phase_1')
        for f in ('contract_sha256','resource_policy_sha256','supported_nm_contract_sha256'):digest(value[f],'/build/'+f)
        text(value['entrypoint'],'/build/entrypoint')
        if type(value['source_manifest']) is not list:fail('SCHEMA_INVALID','/build/source_manifest','phase_1')
        for row in value['source_manifest']:
            shape(row,'path bytes sha256','/build/source_manifest');text(row['path'],'/build/source_manifest/path');digest(row['sha256'],'/build/source_manifest/sha256')
            if type(row['bytes']) is not int or row['bytes']<0:fail('SCHEMA_INVALID','/build/source_manifest/bytes','phase_1')
        env=value['environment_manifest'];shape(env,'python platform distributions dependency_lock_sha256','/build/environment_manifest')
        shape(env['python'],'implementation version executable_sha256 executable_bytes','/build/python')
        shape(env['platform'],'system machine libc','/build/platform')
        for f in ('implementation','version'):text(env['python'][f],'/build/python/'+f)
        digest(env['python']['executable_sha256'],'/build/python/executable_sha256')
        if type(env['python']['executable_bytes']) is not int or env['python']['executable_bytes']<0:fail('SCHEMA_INVALID','/build/python/executable_bytes','phase_1')
        for f in ('system','machine'):text(env['platform'][f],'/build/platform/'+f)
        if type(env['platform']['libc']) is not list or len(env['platform']['libc'])!=2:fail('SCHEMA_INVALID','/build/platform/libc','phase_1')
        for item in env['platform']['libc']:text(item,'/build/platform/libc')
        digest(env['dependency_lock_sha256'],'/build/dependency_lock_sha256')
        if type(env['distributions']) is not list:fail('SCHEMA_INVALID','/build/distributions','phase_1')
        for row in env['distributions']:
            shape(row,'name version artifact_count artifact_manifest_sha256','/build/distributions')
            text(row['name'],'/build/distributions/name');text(row['version'],'/build/distributions/version')
            digest(row['artifact_manifest_sha256'],'/build/distributions/artifact_manifest_sha256')
            if type(row['artifact_count']) is not int or row['artifact_count']<1:fail('SCHEMA_INVALID','/build/distributions/artifact_count','phase_1')
    elif kind == 'nr.retained-bundle.v2':
        rows=value['files']
        if type(rows) is not list or len(rows)!=7:fail('PRIOR_BUNDLE_INCOMPLETE','/files','phase_2')
        for row,name in zip(rows,sorted(FILES)):
            shape(row,'name source','/files')
            if row['name']!=name:fail('SCHEMA_INVALID','/files','phase_2')
            if name=='closure.json':
                if row['source']!={'recipe':'original_closure'}:fail('PRIOR_RECIPE_INVALID','/files/closure.json','phase_2')
            else:
                shape(row['source'],'reference','/files/source');typed(row['source']['reference'],ROLES[name])
        c=value['closure']
        if type(c) is not dict or set(c)!=set('schema profile invocation authority_pin limits_override members'.split()):
            fail('PRIOR_RECIPE_INVALID','/closure','phase_2')
        if c['schema']!='nm.closure.v1' or c['profile']!=NM_PROFILE:fail('PROFILE_MISMATCH','/closure','phase_2')
        typed(c['invocation'],'nm.invocation.v1');digest(c['authority_pin'],'/closure/authority_pin')
        checked_limits(c['limits_override'])
        if type(c['members']) is not list:fail('SCHEMA_INVALID','/closure/members','phase_2')
        ks=[typed(r) for r in c['members']]
        if ks!=sorted(set(ks)) or any(not k[0].startswith('nm.') for k in ks):
            fail('PRIOR_RECIPE_INVALID','/closure/members','phase_2')


def edges(value):
    if value is None:return []
    kind=value['schema']
    if kind.startswith('nm.'):return nm_edges(value)
    out=[]
    def one(path,r,k,nullable=False):
        if r is None and nullable:return
        out.append((path,typed(r,k)))
    def many(path,rs):
        for i,r in enumerate(rs):one(path+'/'+str(i),r,'nm.basis')
    one('/predecessor',value['predecessor'],kind,nullable=True)
    fields={
        'nr.invocation.v2': [('request','nr.request.v2'),('authority','nr.authority.v2'),('build','nr.build.v2'),('resource_policy','nm.resource-policy.v1')],
        'nr.request.v2': [('original_invocation','nm.invocation.v1'),('procedure','nm.procedure.v1'),('decoder','nm.decoder.v1'),('observation','nr.observation.v2'),('execution','nr.execution.v2'),('exposure','nr.exposure.v2'),('policy','nr.policy.v2')],
        'nr.observation.v2': [('evidence','nm.evidence.v1'),('procedure','nm.procedure.v1'),('decoder','nm.decoder.v1')],
        'nr.execution.v2': [('observation','nr.observation.v2')],
        'nr.exposure.v2': [('original_invocation','nm.invocation.v1'),('observation','nr.observation.v2'),('prior_bundle','nr.retained-bundle.v2')],
        'nr.authority.v2': [('request','nr.request.v2')],
    }
    for f,k in fields.get(kind,[]):one('/'+f,value[f],k,nullable=f=='prior_bundle')
    if kind=='nr.request.v2':many('/interpretation/basis',value['interpretation']['basis'])
    if kind=='nr.observation.v2':many('/provenance',value['provenance'])
    if kind in ('nr.authority.v2','nr.exposure.v2'):many('/basis',value['basis'])
    if kind=='nr.execution.v2':
        many('/acquisition/basis',value['acquisition']['basis'])
        for i,c in enumerate(value['conditions']):many('/conditions/'+str(i)+'/basis',c['basis'])
    if kind=='nr.retained-bundle.v2':
        c=value['closure'];one('/closure/invocation',c['invocation'],'nm.invocation.v1')
        for i,r in enumerate(c['members']):out.append(('/closure/members/'+str(i),typed(r)))
        for i,r in enumerate(value['files']):
            if 'reference' in r['source']:one('/files/'+str(i)+'/source/reference',r['source']['reference'],ROLES[r['name']])
    return sorted(out)
