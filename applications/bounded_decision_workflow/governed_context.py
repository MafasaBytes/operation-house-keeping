"""In-memory closure assembly and deterministic scoped accounting; no publication."""
import base64
import json
from .governed_admission import _keys,_nodes,H
from .governed_contracts import I,Q,B
from .governed_resources import bounded_json,problem
from .input import canonical_json_bytes as C,parse_request_wire,parse_snapshot_wire
from .decision_review import _admission_lookup_plan,_validator_rows

def refs(v):
    if type(v) is dict:
        if set(v)=={'kind','sha256'}:yield v
        else:
            for k in sorted(v):yield from refs(v[k])
    elif type(v) is list:
        for x in v:yield from refs(x)

def make_closure(iv_wire,entries,pin,build_wire,prior,caps):
    table={};bodies={}
    def add(kind,wire):
        h=H(wire)
        if h not in table and len(table)>=caps['unique_objects']:raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target='unique_objects')
        if kind=='captured-basis':
            try:value=json.loads(wire)
            except (ValueError,UnicodeError):value=None
            if type(value) is dict and C(value)==wire:e={'kind':kind,'canonical_json':value}
            else:
                b=base64.b64encode(wire).decode();e={'kind':kind,'opaque_chunks':[b[i:i+256] for i in range(0,len(b),256)]}
        else:e={'kind':kind,'canonical_json':json.loads(wire)}
        if h in table and table[h]!=e:raise problem('AUTHORITY_REFERENCE_MISMATCH')
        table[h]=e;bodies[h]=wire
    worlds=[]
    if prior:
        z=prior.worlds[-1].closure
        table.update(z['objects'])
        for w in prior.worlds:
            worlds.append(json.loads(w.files['request.json']))
        from .governed_closure import FILES
        for name,kind in FILES.items():
            wire=prior.files[name]
            if name=='resolved-input.json':
                table[H(wire)]={'kind':kind,'recipe':{'schema':'closure-table-recipe.v1','invocation':z['invocation'],
                    'expected_authority_pin':z['expected_authority_pin'],'members':sorted(z['objects']),'world_witnesses':z['world_witnesses']}}
                bodies[H(wire)]=wire
            else:add(kind,wire)
        add('governed-manifest.v2',prior.files['manifest.json'])
    for kind,wire in entries:add(kind,wire)
    add(I,iv_wire);add('build-witness',build_wire)
    iv=json.loads(iv_wire);worlds.append(iv)
    def body(ref):
        if ref['sha256'] not in table:raise problem('AUTHORITY_UNAVAILABLE')
        return table[ref['sha256']]['canonical_json']
    witnesses=[]
    for world in worlds:
        qref=body(world['scenario'])['request'];q=body(qref)
        parse_request_wire(C(q))
        # Fixed-width sizing only. Owning public reconstruction must precede
        # representation/membership diagnostics. The kernel replaces these
        # hashes with validated gate witnesses before returning any closure.
        witnesses.append({'recipe':'approved-W-F.v1','request':qref,'world_sha256':'0'*64,'fixed_sha256':'0'*64})
    z={'schema':'governed-closure.v2','invocation':{'kind':I,'sha256':H(iv_wire)},'expected_authority_pin':pin,'objects':table,'world_witnesses':witnesses}
    if _nodes(z)>caps['resolved_container_nodes']:raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target='resolved_container_nodes')
    wire=bounded_json(z,caps['resolved_container_bytes'],'resolved_container_bytes')
    return z,wire,worlds

def accounting(z,wire,worlds,prior,caps):
    """Required schedule, not cached physical work. Values checked before dispatch."""
    table=z['objects'];values={};wires={};active=set()
    def recover(h):
        if h in active:raise problem('HISTORY_INCOMPATIBLE')
        if h in wires:return wires[h]
        if h not in table:raise problem('AUTHORITY_UNAVAILABLE')
        active.add(h);e=table[h]
        if 'recipe' in e:
            p=e['recipe'];v={'schema':'governed-closure.v2','invocation':p['invocation'],'expected_authority_pin':p['expected_authority_pin'],
               'objects':{x:table[x] for x in p['members']},'world_witnesses':p['world_witnesses']}
            raw=bounded_json(v,caps['resolved_container_bytes'],'resolved_container_bytes')
        elif 'canonical_json' in e:v=e['canonical_json'];raw=bounded_json(v,caps['resolved_container_bytes'],'resolved_container_bytes')
        else:raw=base64.b64decode(''.join(e['opaque_chunks']),validate=True);v=None
        if H(raw)!=h:raise problem('HISTORY_INCOMPATIBLE')
        values[h]=v;wires[h]=raw;active.remove(h);return raw
    for h in table:recover(h)
    def body(ref):return values[ref['sha256']]
    es=[];children={h:[] for h in table}
    for h,e in table.items():
        if e['kind']=='captured-basis':continue
        src=e.get('recipe',values[h]);out=list(refs(src))
        if 'recipe' in e:out += [{'kind':table[x]['kind'],'sha256':x} for x in e['recipe']['members']]
        if e['kind']=='governed-manifest.v2':out += [{'kind':table[x['sha256']]['kind'],'sha256':x['sha256']} for x in values[h]['files'].values()]
        for ref in out:
            if len(es)>=caps['supplied_references']:raise problem('GRAPH_REFERENCE_LIMIT_EXCEEDED',resource=True,target='supplied_references')
            k=ref['sha256']
            if k not in table:raise problem('AUTHORITY_UNAVAILABLE')
            if table[k]['kind']!=('governed-manifest.v2' if ref['kind']=='prior-bundle-manifest' else ref['kind']):raise problem('AUTHORITY_REFERENCE_MISMATCH')
            es.append((src,k));children[h].append(k)
    heights={}
    def depth(h,path=()):
        if h in path:raise problem('HISTORY_INCOMPATIBLE')
        if len(path)>=caps['active_depth']:raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target='active_depth')
        if h not in heights:heights[h]=1+max((depth(k,path+(h,)) for k in children[h]),default=0)
        if len(path)+heights[h]>caps['active_depth']:raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target='active_depth')
        return heights[h]
    cn=sum(_nodes(src)+_nodes(values[h])+2 for src,h in es)
    cb=sum(len(C(src))+len(wires[h])+66 for src,h in es)
    lower=[];known=set();templates={}
    for iv in worlds:
        s=body(iv['scenario']);d=body(s['declaration']);q=body(s['request']);t=body(d['template_request'])
        known.add((s['request']['sha256'],s['snapshot']['sha256']));lower.append((s['request'],s['snapshot']))
        templates[(d['template_request']['sha256'],d['template_snapshot']['sha256'])]=(d['template_request'],d['template_snapshot'])
        env=[iv,s,d,body(iv['selection'])]+([body(iv['adoption'])] if iv['adoption'] else [])
        cn+=2*(_nodes(q)+_nodes(t))+sum(_nodes(x) for x in env)+_nodes(d['pairs'])
        cb+=2*(len(C(q))+len(C(t)))+sum(len(C(x)) for x in env)+len(C(d['pairs']))
    lower += [v for k,v in templates.items() if k not in known]
    charges=references=resolved=0
    for qr,br in lower:
        q,qp=parse_request_wire(wires[qr['sha256']]);bp=parse_snapshot_wire(wires[br['sha256']])
        n=qp.counts.reference_occurrences+bp.counts.reference_occurrences
        charges+=qp.counts.nodes+bp.counts.nodes+n+_admission_lookup_plan(q,bp.raw)+_validator_rows(bp.raw)
        references+=n;resolved+=len(wires[qr['sha256']])+len(wires[br['sha256']])
    rec=prior.reconstructed_bytes if prior else 0
    if prior:cn+=sum(sum(_nodes(json.loads(b)) for b in w.files.values()) for w in prior.worlds)
    cb+=rec;iv=worlds[-1];s=body(iv['scenario'])
    priorbytes=sum(map(len,prior.files.values())) if prior else 0
    result={'schema':'governed-accounting.v2','unique_objects':len(table),'unique_bytes':sum(len(wires[h]) for h,e in table.items() if 'recipe' not in e),
            'reference_occurrences':len(es),'active_depth':depth(z['invocation']['sha256']),'scope_expansions':len(table)+len(lower),
            'edge_visits':len(es),'context_nodes':cn,'context_bytes':cb,'lower_reconstructions':len(lower),'lower_charges':charges,
            'lower_references':references,'lower_resolved_bytes':resolved,'prior_capture_bytes':priorbytes,'reconstruction_bytes':rec,
            'corner_evaluations':0,'decision_slots':23,'capture_bytes':len(C(iv))+len(wires[s['snapshot']['sha256']])+len(wire)+priorbytes}
    mapping={'reference_occurrences':'supplied_references','lower_charges':'review_resolution_charges','lower_references':'review_reference_occurrences',
             'lower_resolved_bytes':'review_resolved_bytes','lower_reconstructions':'scope_expansions','decision_slots':'decision_rows'}
    for k,v in result.items():
        if k!='schema' and v>caps[mapping.get(k,k)]:raise problem('INPUT_RESOURCE_LIMIT_EXCEEDED',resource=True,target=mapping.get(k,k))
    return result
