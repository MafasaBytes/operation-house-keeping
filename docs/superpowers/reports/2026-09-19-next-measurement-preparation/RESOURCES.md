# Measured demand and proposed resource policy

These are exact static byte/structure measurements of the retained corpus, not a measured future runtime. `measurements.json` separates complete input graph/capture, output, trace, diagnostic and seven-file retained-bundle sizes. `resource-detail.json` separates unique objects, repeated reference occurrences, per-Q scoped expansion, repeated contextual scans/reconstruction, matrix/condition/check/source demands and recovery writes. `completed-resource-maxima.json` separates completed cases from intentionally rejected input maxima. Policy bytes are proposed, not approved; no existing application/backend limit changed.

| Dimension | Corpus maximum (including negative inputs) | Proposed immutable ceiling |
| --- | ---: | ---: |
| `active_depth` | 8 | 32 |
| `build_bytes` | 463 | 65536 |
| `bundle_bytes` | 200591 | 1048576 |
| `capture_bytes` | 114717 | 1048576 |
| `closure_bytes` | 157107 | 524288 |
| `context_scan_bytes` | 1713266 | 16777216 |
| `diagnostic_bytes` | 704 | 2048 |
| `edge_visits` | 109 | 4096 |
| `integer_digits` | 3 | 128 |
| `invocation_bytes` | 614 | 16384 |
| `json_depth` | 16 | 40 |
| `json_nodes` | 3693 | 65536 |
| `manifest_bytes` | 954 | 16384 |
| `object_bytes` | 86310 | 262144 |
| `public_reconstruction_nodes` | 13395 | 131072 |
| `receipt_bytes` | 312 | 1024 |
| `reference_occurrences` | 109 | 4096 |
| `request_chain` | 5 | 4 |
| `request_contexts` | 5 | 8 |
| `result_bytes` | 11782 | 65536 |
| `scoped_expansions` | 70 | 1024 |
| `string_bytes` | 148 | 4096 |
| `trace_bytes` | 29979 | 131072 |
| `unique_objects` | 26 | 128 |

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
