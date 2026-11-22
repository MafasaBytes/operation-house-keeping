# C05 scoped Product Owner acceptance

Date: 2026-11-22 (Europe/Amsterdam). Recorded at 2026-11-22T20:46:00Z. This is the recording time, not a reconstructed timestamp for the owner's message or any historical synthetic event.

## 1. Owner decision and status

**C05 is accepted and closed within the tested companion guarantee boundary.** The Product Owner approved this exact administrative action:

> Approved: record scoped C05 acceptance, retaining the companion guarantee boundary and derived_not_adopted. Preserve evidence and R1/L1; keep L2 frozen. No further runs, repairs, K, commits or merge.

Acceptance applies to the retained four-case native validation at source checkpoint `f1e054cd4d5ed3e17c7c31e3532b16960e3c090c`, captured build `f4f7c57ffdb673a709f1f36963515b71b7c335cb1575779a31351c76734895ef`, and the exact fixture and evidence pins below. The checkpoint's recorded parent remains `0a39c4d8f86c3e996aa97adc9d0afb2eed4faca3`. This recording did not inspect Git history or create a new checkpoint.

This is acceptance of the scoped workflow correction and its retained validation evidence. It does not adopt an engineering conclusion. Both delegated assessments retain `derived_not_adopted`. Both false-calibration cases retain owning status `not_run` and no owning bundle; no new owning adoption status is invented for them.

The prior run receipt correctly states that owner acceptance was still pending when that receipt was written. This subsequent record supplies the owner decision without rewriting that history.

## 2. Accepted four-case behavior

| Case | Carried synthetic premise / review | Accepted observed result |
|---|---|---|
| false_support | 60, qualified calibration predicate false; supportive review | Completed `blocked_calibration_counterexample`; admissibility blocked, no owning assessment or owning bundle. |
| false_opposition | Same false producer; opposing review | Same completed calibration block, with the opposing-review reason retained; no owning assessment or owning bundle. |
| positive_support | 60.1, qualified calibration predicate true; supportive review | `delegated_assessment`, `permitted_under_declared_conditions`, `one_compatible`; H1 `compatible_under_declared_model`, H2 `conditionally_incompatible`. |
| positive_opposition | Same positive producer; opposing review | Gate permits delegation, but owning assessment remains `applicability_blocked`; both hypotheses `not_assessed`. |

The scoped C05 defect is closed: a deliberately supportive review cannot bypass the qualified calibration counterexample in the carried acquisition. The positive-support control demonstrates that the gate permits assessment in the corresponding non-counterexample case. Positive-opposition demonstrates that gate delegation preserves the existing applicability block.

All four cases completed evaluation, verification, replay and verification of replay. The original and replayed false cases retained completed companion blocks without fabricating owning bundles. Both positive cases retained byte-identical owning result and trace across replay and the required replay lineage.

## 3. Companion guarantee and retained limits

The accepted rule is `ct.t1-calibration-primary-gate.v2`. Its guarantee name remains `producer-checked-primary-calibration-gated-v1`; the v1 record-kind and guarantee names are intentionally retained by the v2 contract.

The guarantee requires the complete companion package together with its bound carried acquisition, handoff and prior inputs. It does not attach to a detached owning bundle, a direct owning-evaluator invocation, or an older historical receipt. Producer/prior policy and assessment policy remain distinct and must be inspected separately. There is no blanket precedence rule making every producer diagnostic authoritative over every review.

Correction release remains disabled. No factual correction authority was issued, and no block was released by this acceptance. A positive point check permits delegation under the declared conditions; it does not establish interval continuity, physical calibration validity or the truth of a hypothesis.

The scope does not include arbitrary historical or multiple-source evidence adjudication, unselected native negative/correspondence cases, a full native-module or repository-suite pass, empirical validity, automatic conclusion adoption, frontend readiness, automatic source-change detection, packaging, installation, VM validation or enterprise readiness. It closes this C05 companion milestone, not every item in a broader challenge set.

D1's accepted interpretation is retained: `source_editions/equal` means the required edition, permission and reference checks succeeded. It does not mean captured/prior and assessment policy bytes are equal. The wording limitation remains open. D-P remains open.

Contract reference: /mnt/d/operation-house-keeping/docs/superpowers/specs/2026-11-20-c05-companion-gate-v2/CONTRACT.md, incorporating its preserved edition-1 predecessor. The present acceptance records later validation and does not revise earlier implementation-state prose.

## 4. Evidence and exact attribution

The accepted native attempt collected exactly four cases and reported **4 passed in 94.21 seconds**. All sixteen native command captures completed with exit 0 and empty stderr. Admission, driver, capture, finalization and outer invocation also exited 0. Scientific agreement, capture, preservation and accounting were checked separately.

The earlier component evidence remains **107 of 107 cases across attempts 03 and 04**, with 92 recorded passes in the timed-out attempt and 15 in its separate continuation. This is not relabeled as a clean single-process suite pass. The four native cases are a separate later result.

The following byte counts and SHA-256 identities were rechecked from retained files before recording acceptance:

| Exact retained path | Bytes | SHA-256 |
|---|---:|---|
| /mnt/d/operation-house-keeping/docs/superpowers/reports/2026-11-22-c05-native-four-case-validation-attempt-01-RECEIPT.md | 18883 | 3dfc0b40406f23d91f39130d5b46c34951dc6a6bc541a59f2ff7abf201d772e1 |
| /mnt/d/operation-house-keeping/docs/superpowers/reports/2026-11-22-c05-native-four-case-validation-attempt-01-TRANSCRIPT.txt | 5066 | b76a4dc129ebc19aa79cafda13d30a21087e238bf973049d7987a70733ae185d |
| /mnt/d/operation-house-keeping/docs/superpowers/reports/2026-11-22-c05-native-four-case-validation-PREPARATION/MANIFEST.tsv | 1002 | 14603130eff634863fb2f66004430fda7b85d818558137b7919a08bb22f15f46 |
| /mnt/d/operation-house-keeping/docs/superpowers/reports/2026-11-22-c05-native-FIXTURE-ACCEPTANCE.json | 2636 | 02a1a861b1374c2971fef634428b804385ffe845100e498be132a49216291377 |
| /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-fixtures-20261121-01/native-manifest.json | 6503 | 1c0a7307c91fbd6f801cfe0c7f15d0ed76b15bede5db5cc0071fc1d973421bdd |
| /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/provider.wire | 31575 | f4f7c57ffdb673a709f1f36963515b71b7c335cb1575779a31351c76734895ef |
| /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-four-case-validation-20261122-attempt-01/after.json | 41887 | 634662d464109bb936c66eca75a96feb409dd1d8d3cbccc5cb9e779b70328aec |
| /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-four-case-validation-20261122-attempt-01/junit.xml | 1041 | 2009d55a9c0478b63d6a998e60e6628c2cc1a1d44429bb63cac244394bbb9168 |

Evaluated companion workflow receipts are under /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-four-case-20261121-01/c05-native0/<case>/evaluation/workflow-receipt.json:

| Case | Bytes | SHA-256 |
|---|---:|---|
| false_support | 23376 | d9849b59507333951953d1923da5dbfa32d40e72fc945abf5d3dbb0adacbbf67 |
| false_opposition | 23400 | bcd392e8d7e08b1559c4df3e758b1d5c2a67746c59b406647590a6893993f8ef |
| positive_support | 23629 | 471955f14bca4f5f17507e5b52a103cfd5e0b76bca7efd0d25fa22d8df88f63a |
| positive_opposition | 23646 | 543f626820699463bd6d0e1588499a6541019817c7a4d403d42865779e6b59e5 |

All sixteen evaluation/replay receipts and verification/reverification reports were re-hashed against the pins retained by the run. Their full paths and identities are in section 4 of the pinned run receipt. The exact executed command, all four pytest node IDs, complete captures and invocation bindings remain in that receipt, transcript and runtime records. They are historical reproduction instructions, not permission to run again.

The native output inventory remains 329 entries with SHA-256 `a7e4f0301c190d8e24b7ba38914f8b7414df5239399788f41f1881af576f9c2b`. Its readback convention includes absolute paths, entry types, modes, logical file sizes, allocated blocks, content digests and symlink targets without following links.

## 5. Disclosures retained with acceptance

The run's independent review found no material discrepancy. Its finalization recorded matching preservation across 147 scopes / 25,877 entries, counting overlap, and checked 698 input/environment pins. These are retained run observations, not claims that the entire host was verified.

The prospective 69 provider measurements and 207 read-only Git children remain source-derived counts without individual subprocess telemetry. All sixteen direct native command captures are observed. CPU and peak memory were not measured.

The three launcher phase readings sum to 138.03 seconds, while the caller stopwatch recorded 134.8429871 seconds: an unexplained difference of 3.1870129 seconds. No cause is inferred, no value is corrected, and both records remain preserved. Pytest's 94.21 seconds is its own timing observation.

The owner-accepted containment limitations remain: per-process rather than hard aggregate memory/process/thread limits, sampled storage rather than continuous peak enforcement, bounded capture, and best-effort detached-child cleanup after controller loss. No controller loss, timeout or overflow was observed in this successful attempt. Historical allocation uncertainty and unmeasured overhead remain unresolved.

## 6. Administrative preservation and readback

This action authorizes one new acceptance document and administrative file readback only. It changes no candidate, authority, fixture, source, result, review, receipt, transcript or prior acceptance record. No new application execution, tests, native verification/replay, provider measurement, authority issuance, repair, retry, K or Git operation is part of this recording.

Before publication, 30 explicitly pinned files matched their expected byte counts and hashes. A finite preservation snapshot covered 18 scopes / 10,499 entries, counting overlap, at 2026-11-22T20:45:47.772235+00:00. Its canonical scope-map SHA-256 was `d5a7589e0d090033552921db9213de12d01738f3a8fd33ba821b990beed88c9b`. The destination did not exist.

For each listed path, administrative readback records entry type, mode, logical regular-file size, allocated blocks, and content digest or symlink target; directory membership is included and links are not followed. Sorted compact UTF-8 JSON is hashed with SHA-256. This is a file-only check, not execution of a repository verifier.

| Preserved scope | Entries | Inventory SHA-256 |
|---|---:|---|
| /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-four-case-validation-20261122-attempt-01 | 9 | 0015fd5aea584c582e51ea3cc6964179c9129e4757bd768a0f5f24e4b1106e47 |
| /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-fixture-approvals-20261121-01 | 5948 | b9f7b1af96f4810d0b3eec8a167d16ac804998b843344154cb44e464e6c0de9f |
| /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-fixtures-20261121-01 | 605 | f05fee0836e543a80459fc0fb2fbf02ed059bc9ba2e75083090b90921f6dbdf9 |
| /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-four-case-20261121-01 | 329 | a7e4f0301c190d8e24b7ba38914f8b7414df5239399788f41f1881af576f9c2b |
| /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/t1-linux-ext4-l1-validation-20261022-1 | 7 | 5e675d4608212d8100f4aa3759845f36a97dd3964a1589c87b29111b02733fbc |
| /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/t1-linux-ext4-l1-validation-20261022-2 | 10 | 0cf7ad173c99b9500c6499a73b84f57aea94e072a24e8871a5bac084f45e0d8e |
| /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/t1-linux-ext4-l1-validation-20261022-3 | 3528 | 5dcc08eb5320cc7943b74a873a13f8e8a4d99e77961ff5632504bab7d7128e97 |
| /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/temperature-c05-paired-20261111-attempt-01/evaluation-only-c05-v1 | 19 | aaafbc41234e178948d65a9361618b123b6e6f5cde8c443f049f298acfca2571 |
| /mnt/d/operation-house-keeping/docs/superpowers/reports/2026-10-21-t1-r1-acceptance-and-r2-proposal | 22 | 4f38deed8f30a1887b71dee7ec29ef2984cf7ecef0176cd18a032a122d478d02 |
| /mnt/d/operation-house-keeping/docs/superpowers/reports/2026-10-22-t1-linux-ext4-l2-packaging-fresh-install-PROPOSAL.md | 1 | 1145b62fd46b9b7df640eab7974d42fc2c1f92e194cfa6742e37e7eafae61f61 |
| /mnt/d/operation-house-keeping/docs/superpowers/reports/2026-10-22-t1-linux-ext4-l2-scope-finalization-ADDENDUM.md | 1 | fdc6019f47eb02cc8f961681e706c9000b1802a403f48c81836f99f17da71470 |
| /mnt/d/operation-house-keeping/docs/superpowers/reports/2026-11-06-temperature-trial-PRODUCT-OWNER-ACCEPTANCE.md | 1 | c3338161975323e49359b6502c3cdb34bdc61a15c2c950c4a99356f758516adc |
| /mnt/d/operation-house-keeping/docs/superpowers/reports/2026-11-19-c05-companion-gate-IMPLEMENTATION-PLAN.md | 1 | 3083c8e488487658a8fb23bdbf4a324ffc2b2c46e5c4283d109edc0c234f9c4e |
| /mnt/d/operation-house-keeping/docs/superpowers/reports/2026-11-22-c05-native-FIXTURE-ACCEPTANCE.json | 1 | 91d3b2dce97665d886deb416ff8c7e2e202a4855282d5f4eb8726c62b33849c6 |
| /mnt/d/operation-house-keeping/docs/superpowers/reports/2026-11-22-c05-native-four-case-validation-PREPARATION | 13 | 09d69ab51e7bcc87872a7c39f02766ff28291d1b9c77bdf060b529727645fad9 |
| /mnt/d/operation-house-keeping/docs/superpowers/reports/2026-11-22-c05-native-four-case-validation-attempt-01-RECEIPT.md | 1 | f94a13ee1468f8ee7550dd5fdb4d2ac11a2a33b4578625cb01738252bba456e7 |
| /mnt/d/operation-house-keeping/docs/superpowers/reports/2026-11-22-c05-native-four-case-validation-attempt-01-TRANSCRIPT.txt | 1 | b326d064a6e00754c7e6b91a200bad978ec74a6d3ce19df81bc1ae4690093cfb |
| /mnt/d/operation-house-keeping/docs/superpowers/specs/2026-11-20-c05-companion-gate-v2 | 2 | 0ee11fc838d9d8624f93468f0339c4b082f5005b0734e58daddeef72e7efb1c1 |

Post-publication administrative comparison at 2026-11-22T20:47:19.478380+00:00 matched all 18 scopes / 10,499 entries and all 30 explicit pins. The scope-map digest was unchanged. Exact text readback passed. A separate independent read-only reviewer found no material factual or scope issue in this acceptance record. This completion note was then added to the new document before its final exact readback and hash publication; no preserved file was edited. The document does not recursively embed its own hash. This finite check does not claim a new whole-host or full historical revalidation.

R1's 141 results retain their original attribution; the three deferred cases remain deferred. Scoped L1 and the accepted temperature trial retain their original evidence and limitations. Session 70642 remains incomplete with its existing membership and missing terminal records. The stopped A5 and fixture-sealing attempts remain stopped; their later successful readbacks remain separate. Earlier scientific failures and operational failures retain their original outcomes.

## 7. Stop and return boundary

Scoped C05 acceptance is now recorded. This removes this specific C05 acceptance gate from the return to application-workflow work. It does not authorize another run, source change, frontend implementation, deployment or release action.

L2 and VM work remain frozen. COOMET remains parked. No repairs, retries, K, commits or merge are authorized by this acceptance. Existing evidence and R1/L1 remain preserved. The record is uncommitted.

END SCOPED C05 PRODUCT OWNER ACCEPTANCE

