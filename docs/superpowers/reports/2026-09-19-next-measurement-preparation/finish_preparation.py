"""Write static demand/coverage documentation; no application invocation."""
from pathlib import Path
import json,hashlib,ast
P=Path(__file__).parent;ROOT=P.parents[3]
C=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def read(n):return json.loads((P/n).read_bytes())
def write(n,x):
 p=P/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(x if isinstance(x,bytes) else C(x))
m=read('measurements.json');d=read('resource-detail.json');policy=read('resource-policy.json');cases=read('cases.json')
completed={x['id'] for x in cases if x['kind']=='completed'}
good=[r for r in m['per_case'] if r['case'] in completed]
maxgood={k:max(r[k] for r in good) for k in good[0] if k!='case'}
write('completed-resource-maxima.json',maxgood)
# Read literal legacy limits without importing application entry points.
tree=ast.parse((ROOT/'applications/bounded_decision_workflow/input.py').read_text())
legacy=next(ast.literal_eval(n.value.args[0]) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='BUILD_LIMITS' for t in n.targets))
write('legacy-limits-readonly.json',legacy)
write('source-context/manifest.json',[dict(path=str(f.relative_to(P/'source-context')),bytes=len(f.read_bytes()),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted((P/'source-context').rglob('*.py'))])
gp=ROOT/'docs/superpowers/reports/2026-09-16-maintained-admissibility-amendment/policy.json';write('frozen/existing-governed-policy.json',gp.read_bytes())
def stats(x):
 pending=[(x,1,None)];nodes=depth=refs=string=0
 def leaves(v):return sum(leaves(z) for z in v) if isinstance(v,list) else 0 if isinstance(v,dict) else 1
 while pending:
  v,n,k=pending.pop();nodes+=1;depth=max(depth,n)
  ref=k is not None and (k.endswith(('_id','_ids','_reference','_commitment')) or k in ('record_ids','supersedes','via_assertion_ids'))
  if ref:refs+=leaves(v)
  if isinstance(v,str):string=max(string,len(v.encode()))
  if isinstance(v,dict):
   for kk,z in v.items():string=max(string,len(kk.encode()));pending.append((z,n+1,kk))
  elif isinstance(v,list):
   pending.extend((z,n+1,None if ref else k) for z in v)
 return dict(nodes=nodes,depth=depth,reference_occurrences=refs,max_string_bytes=string)
public=[]
for n in ['snapshot-60.1.json','snapshot-unavailable.json']:
 b=(P/'public'/n).read_bytes();x=json.loads(b);s=stats(x)
 s.update(file=n,wire_bytes=len(b),state_model_records=len(x['state']['material']['records']),conditions=len(x['conditions']),constraint_evaluations=len(x['constraint_evaluations']),max_candidates=max(len(z['candidates']) for z in x['constraint_evaluations']))
 assert s['wire_bytes']<=legacy['snapshot_wire_bytes'] and s['nodes']<=legacy['input_json_nodes_per_file'] and s['depth']<=legacy['input_json_depth'] and s['reference_occurrences']<=legacy['input_reference_occurrences'] and s['max_string_bytes']<=legacy['input_max_string_bytes']
 assert s['state_model_records']<=legacy['model_records_per_snapshot'] and s['conditions']<=legacy['conditions_per_snapshot'] and s['constraint_evaluations']<=legacy['constraint_evaluations_per_snapshot'] and s['max_candidates']<=legacy['candidates_per_evaluation']
 public.append(s)
write('public/structural-demand.json',dict(method='Static accounting against unchanged literal lower guard values, no application parser executed.',objects=public))
rows=[]
for k,limit in policy['limits'].items():
 val=m['corpus_maxima'].get(k)
 if k=='scoped_expansions':val=d['maxima'][k]
 if k=='public_reconstruction_nodes':val=m['corpus_maxima']['public_reconstruction_context_nodes']
 if k=='json_depth':val=d['maxima']['object_max_json_depth']
 if k=='string_bytes':val=d['maxima']['object_max_string_bytes']
 if k=='integer_digits':val=d['maxima']['rational_max_digits']
 if k=='build_bytes':val=len((P/'build-placeholder.json').read_bytes())
 rows.append(f'| `{k}` | {val if val is not None else "see static detail"} | {limit} |')
text='''# Measured demand and proposed resource policy

These are exact static byte/structure measurements of the retained corpus, not a measured future runtime. `measurements.json` separates complete input graph/capture, output, trace, diagnostic and seven-file retained-bundle sizes. `resource-detail.json` separates unique objects, repeated reference occurrences, per-Q scoped expansion, repeated contextual scans/reconstruction, matrix/condition/check/source demands and recovery writes. `completed-resource-maxima.json` separates completed cases from intentionally rejected input maxima. Policy bytes are proposed, not approved; no existing application/backend limit changed.

| Dimension | Corpus maximum (including negative inputs) | Proposed immutable ceiling |
| --- | ---: | ---: |
'''+ '\n'.join(rows)+'''

The request-chain maximum of 5 belongs to the deliberate over-budget case; the proposed supported history envelope is **at most four complete revisions per declared chain**, and at most eight distinct Q contexts overall, still subject to every byte/object/work/output guard. A revision-4 request with excessive basis material may refuse; “four revisions” is not a capacity guarantee for arbitrary content. Every accepted chain reaches revision 1 with complete required dependencies. No terminal witness, history truncation or automatic rebasing. Longer growth requires a separately approved policy and measured build, or an explicitly new request/lineage whose limited claims are honest; starting a new ID must not pretend the omitted lineage was validated. Sharing lowers unique storage but does not erase edge/context work.

Accounting definitions and headroom:

* Unique objects/bytes count exact `(kind,sha256)` members once, including required ancestors, basis, invocation and witnesses. Physical supplied copies and complete base64 closure transport are separate. An absent negative member is absent from the case capture, although its valid twin may exist elsewhere in the package. Recovery is case-isolated.
* `reference_occurrences` and `edge_visits` in the main measurement file are first intrinsic-graph DFS listing demand, not measured runtime visits. The supplemental scoped counts charge Q-local revisits; guards must cover both actual incoming checks and scoped expansions. The 4,096-edge and 1,024-expansion proposals exceed the measured 109 intrinsic and 279 scoped occurrences, and 70 scoped objects, respectively. Never refund actual repeated work based on a unique-object count.
* `context_scan_bytes` in the first report is a conservative edge endpoint scan reserve (source bytes + target bytes + 66 bytes per edge), distinct from supplemental per-Q unique-scope scan bytes. The larger reserve is 1,713,266 bytes; the measured per-Q scope scan sum is 506,039. Both are below the proposed 16 MiB scan guard; neither is physical disk I/O. Public reconstruction unique nodes versus contextual nodes are reported separately. Public reconstruction may be repeated by its owning validators; actual internal work still needs runtime instrumentation.
* The largest current matrix demand is 10 cells in this corpus; the semantic general maximum is 2 H × 2 M × 3 outcomes = 12. At most two sources per row implies at most 24 cell contributions. Five required conditions plus one ceiling per P imply at most 12 condition checks. Requirement count is separately bounded by input nodes/bytes, and must be reserved before dispatch; the corpus has four checks. Scalar interval endpoints use rational input bounds before conversion; a product of two 128-digit integers can need 256 digits. Decoder partition checks reserve all endpoint/pair comparisons before arithmetic. No claim that small corpus rationals establish worst-case arithmetic speed.
* JSON nodes/depth/string/key bytes and raw basis bytes are distinct from base64 transport. The largest parsed input string is 148 bytes; opaque basis is bounded by raw object size, not interpreted. Transport members reserve decoded object size and encoded size before allocating. `public/structural-demand.json` verifies both public examples fit unchanged lower structural guards. Existing legacy and governed ceilings are retained for review, not modified or inherited as measurement capacity.
* Full output reservation covers result 65,536 + trace 131,072 + closure 524,288 + build 65,536 + manifest 16,384 + invocation 16,384 + exact immutable policy bytes, within the proposed 1,048,576-byte bundle guard. The closure duplicates invocation/build/policy bytes deliberately; all copies count. Per-component limits do not guarantee that arbitrary simultaneous maxima fit: the aggregate guard wins. Refusals reserve 2,048 diagnostic bytes and empty stdout before work; receipts reserve 1,024 bytes. Bounded construction must refuse before exceeding a reservation, not serialize and truncate later.
* Prepared manifests and receipts are fully measured, including refusal forms. Runtime physical-counter digit growth and the real build witness are not measured here; their ceiling reserves must be validated in later qualification. The current NONEXECUTABLE build placeholder is not capacity evidence for a complete executable witness.

General bounds are independent checks, not extrapolations from these corpus maxima. The proposed 30-second command watchdog, 512 MiB address-space ceiling and 64 MiB retained-corpus ceiling are safety proposals **without runtime feasibility evidence**. Preparation process timings/RSS are recorded as preparation only. They cannot validate a per-command runtime budget. Future measurement must separately record bytes/read calls, decoding/reconstruction and scoped expansions, actual writes including refused prefixes, allocation/peak RSS, CPU/wall time, output reserve use and supported-filesystem failure behavior. Physical counts go in a fresh manifest, not deterministic semantic result equality.

Future boundary obligations: under separately scoped execution authorization, exercise every guard immediately below required work, sufficient-budget twins, caller tightening versus attempted enlargement, four-revision accepted and five-revision refused histories, repeated sharing, output/diagnostic exhaustion, and standalone recovery/replay. Observe refusal before the guarded operation and absence of a successful partial manifest. A missing deeper ancestor may be hidden by an earlier legitimate guard refusal; do not claim that unvisited content was checked. Measure both full successful work and refused prefixes. Do not infer crash durability, XFS support, empirical prediction accuracy or lower-limit amendments.

No resource contradiction has been established by static preparation. There is also no runtime feasibility claim. Exact package/resource-policy approval and actual executable binding remain owner gates before implementation/proof acceptance.
'''
write('RESOURCES.md',text.encode())
coverage=['# Exact fixture and command accounting','','All entries are expected, not application runs. The matrix contains 68 invocation cases: 36 completed dispositions and 32 technical/resource refusals. Each completed case has evaluate/verify/replay expectations (108 commands); each refusal has evaluate only (32): **140 planned measurement commands, zero executed**. There are 36 prepared seven-file bundles (252 bundle files); stdout/stderr expectations and invocation/capture/oracle fixtures are additional preparation artifacts, not retained-bundle members. Two further exact cross-profile commands are in compatibility-commands.json: 142 total planned CLI invocations. Six future harness-only controls and one manual C dossier have zero CLI commands. Remaining delivery/environment controls in delivery-obligations.json are obligations outside this finite command count.','','| Case | Expected exit | Expected disposition/code | Commands |','| --- | ---: | --- | ---: |']
for c in cases:
 outcome=c['disposition'] if c['kind']=='completed' else read('expected/'+c['id']+'/stderr.jsonl')['code']
 coverage.append(f"| {c['id']} | {c['expected_exit']} | `{outcome}` | {3 if c['kind']=='completed' else 1} |")
write('CASES.md','\n'.join(coverage).encode())
readme='''# Bounded next-measurement preparation package

2026-09-19. Owner-approved semantics; **prepared for exact-package/resource-policy approval, not authorized implementation or executed proof**. Local checkpoint `6351750b3cacad288cb99d9d11a8b61b6fe85b71`; no remote verification. The exact frozen semantic candidate and independent confirmation are retained under `frozen/` and verified against the owner's hashes.

Read `IMPLEMENTATION-PLAN.md`, `CONTRACTS.md`, `ORACLE.md`, `CASES.md`, then `RESOURCES.md`. `cases.json` binds each canonical input capture, explicit oracle and expected result/refusal. `command-matrix.json` gives exact future argv templates; `commands.json` is the compact operation index. These are 68 measurement invocation cases, 36 complete expected dispositions, 32 refusals, and 140 planned measurement commands. compatibility-commands.json adds two exact cross-endpoint refusals: 70 CLI case inputs and 142 planned commands total. Six harness-only cases and manual C are separate. No application command, future-runtime test or experiment was executed.

The public 60.1/upper-50 fixture was constructible using in-memory owning public model/result producers and passed public reconstruction; the unavailable fixture likewise reconstructs with `observation_absent`. All exact input bytes, synthetic raw payload, public schema, selected source context and frozen semantic documents are retained. Recoverability does not depend on a digest-only ancestor, old loose archive or current store. This is synthetic conditional evidence, not physical acquisition or empirical calibration.

Static consistency independently checked canonical bytes/hashes, case-isolated captures, 216 manifest payload commitments, hand-derived finite bitset expectations for 17 rankable cases, preserved empty/repeated branches, rehashed stale semantic joins/valid twins, four canonical-construction permutations and all explicitly missing/tampered controls. `static-verification.json` gives scope and measured preparation work. It is not passing application proof. The oracle and checker have the same lead author and shared approved assumptions; no independent reviewer endorsed this package.

Measured maxima: input object 86,310 bytes; required decoded unique inputs 114,717; closure 157,107; result 11,782; trace 29,979; complete prepared bundle 200,591; diagnostic 704. Unique objects 26, intrinsic edges 109, scoped occurrences 279, scoped expansions 70. Negative history maximum is five revisions; the proposed accepted envelope is four complete revisions. Per-case values and completed-only maxima are separate JSON artifacts. Proposed ceilings are not approved; physical runtime capacity remains unmeasured.

Important delivery qualification: `build-placeholder.json` is deliberately NONEXECUTABLE. The exact prepared results/receipts commit to that witness and prepared physical manifests. They must not be accepted by a production command. A separately authorized implementation must supply the real executable/environment witness, retain its recovery prerequisites, rebind dependent commitments without changing oracle premises, and obtain approval of that exact derived package before proof execution. No future executable can be truthfully archived now. Physical manifests/receipt bundle digests are freshly bound at runtime; semantic comparisons are explicitly specified in CONTRACTS.md.

No missing semantic rule or need for a backend extension was found. Remaining gates are exact wire/CLI/retention/build-binding approval, proposed numerical resource/history policy approval, independently scoped implementation and later runtime/failure/filesystem qualification. The approved supplied-prediction, minimax/no-cost, whole-set withholding, local-attestation/manual-C, unique-ID and complete-closure choices are not pending again. IN-001 and CI-001 remain open and unselected.

Preservation: `starting-inventory.json` records the actual 1,207-file initial nonignored inventory and its aggregate hash. `preservation.json` verifies those bytes and unchanged tracked/index state. Ignored runtime/cache trees were not inventoried and were not targeted for writes. Only this new package directory is produced.

Recovery: `package.zip` retains every package payload listed in `MANIFEST.json`, plus the manifest. Both use safe relative paths; ZIP metadata is deterministic. `recovery.json` is the external archive/manifest commitment and in-memory extraction verification receipt, intentionally outside the archive to avoid a self-hash cycle. Hash the archive, read its manifest, decode each member and verify exact size/SHA before use. The archive is a data package, never an application bundle or an instruction to execute scripts. Per-case capture bytes, including deliberate omissions/tampering, take precedence over the package's shared object union when preparing a future isolated input directory.

Owner next gate: approve the exact archive/manifest and proposed measurement-only resource/history policy, or request bounded amendments; then explicitly scope implementation slices. This package grants no implementation, proof execution, physical acquisition, ledger change, dependency acquisition, backend extension or remote operation.
'''
write('README.md',readme.encode())
print(json.dumps(dict(completed_maxima=maxgood,public=public)))
