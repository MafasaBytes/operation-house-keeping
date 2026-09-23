# Slice 6 approved cross-profile correction

Owner authorization approves only the proposed replacement, subject to inspection. This record applies that correction; Slice 6 remains unaccepted. Historical reports, proposal and package remain unchanged.

Verified starting administrative HEAD: `3c5a8a45b071f311dd1ab6464971759038d1f85f`; prior tested implementation `c06395859019bead8cb7cc6491fde3efd04f1524`; Slice 5 acceptance `c914d13ea887d3f7b2951a2db493f1fec1bab353`. Historical qualification report SHA-256 is `ce417f3b9ea69b9106b3e681544ba1105b6e1fdd5133d4cc24e18b3c781e3ae2`.

Exact proposal: `2026-09-23-next-measurement-slice6-qualification-evidence/proposed-cross-profile-correction/proposal.json`, SHA-256 `edccbb50a2b50c2b8400652ea44148fcf6b275872ecf5d4d051478c35f350c61`. Replacement bytes remain at that directory's `legacy-request.json`.

| Commitment | Bytes | SHA-256 |
| --- | ---: | --- |
| Frozen `public/legacy-request.json` | 16460 | `24635e493d371a5e05f9b61e729457fde7397ddfb0f31bc3dbb7f14ebe19c125` |
| Approved replacement | 16382 | `170d3ced7bfec018ddc63b03687edcb3716661b7f9f824c8715a6eaa954456c9` |

Only `/request_id`, `/actor_assertion/actor_label`, and `/actor_assertion/purpose` become `x`. The original strings are respectively `bdw-case-baseline`, `local_project_owner`, and `bounded synthetic supplied-alternative review`. This removes 78 bytes. Parsed equality after replacing those three fields proves every other field, including foreign schema, public snapshot, exact bindings and unauthenticated authority assertion, is preserved. These descriptive strings do not determine profile dispatch. The maintained thermal `parse_request_wire` accepts the replacement.

CONTRACTS.md final dispatch clause requires bounded lexical capture before foreign-profile refusal; compatibility commands explicitly assume no earlier resource failure. At the starting administrative HEAD the actual production command counted the complete 16382-byte invocation, returned exit 3 with the byte-exact frozen PROFILE_MISMATCH diagnostic, empty stdout and no output directory. No object was needed or discovered. The real P request, rebound to that actual build, returned exit 0 and byte-exact independently bound frozen result. The unchanged oversized original returned exit 4, empty stdout, no output; that observation is a resource control only.

The base package/manifest/recovery commitments remain unchanged. The revised harness verifies both input commitments and this exact three-field delta before substituting the compatibility input. No semantic oracle is changed. Accounting remains 68 evaluations + 36 verifies + 36 replays + two cross-profile commands = 142. The additional oversized-input control is outside those 142; the six harness controls and manual unresolved C remain separately accounted. Future build/I/trace bindings remain mechanical and are recorded per run.

This is not Slice 6 acceptance or a resource-policy amendment. Initial qualification artifacts are retained at `/tmp/nm-slice6-correction-20260923`; the final qualification report must retain recoverable copies and distinguish subsequent-head evidence.
