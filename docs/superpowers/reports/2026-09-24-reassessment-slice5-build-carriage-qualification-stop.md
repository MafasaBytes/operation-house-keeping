# Slice 5 qualification stop after affected legacy regressions

Status: incomplete; Slice 5 acceptance and final milestone acceptance remain pending.

## Authority and revisions

The approved decision package remains bound to archive SHA-256 `ca49082eb39973ca8b93d0036ec6bfe22ca7786a4c97980611b8b5c3d8293111` and manifest SHA-256 `ec780e61018f99fc1bd5f66f5bb0876f39139a518b999236fe14bd5773283084`. The separate approval record is `2026-09-24-reassessment-slice5-build-carriage-owner-approval.json` (SHA-256 `eac3c8d323607bef55b4261619bc1e72190202d69fb2e6d020377e101e3163a9`).

The approved original candidate was `40fbb7b0a5ea5251179a9661c782a41cf7356ed6`; original administrative checkpoint was `358d2867db478494ca8b6e6475b83fdd53a9750c`. The implementation/test HEAD used for the runs below was `c321f2e096a71a43bf65787f6f1605c4031266e7`, also the repository HEAD at report preparation. It is not a fully qualified replacement candidate: the matrix, controls, delivery, recovery and final suite were not run against it.

## Recorded qualification launches

The two allocated red launches remain failed setup evidence: each used the sparse retained source checkout, pytest exited 4 because the requested target test files were absent, and no target node started. These do not establish test results.

The single targeted fixed launch `T-fixed` ran against `c321f2e096a71a43bf65787f6f1605c4031266e7` and reported 35 passed, exit 0. Its repair growth was 7,224,717 bytes, 216 files and 54 directories. The controller's declared local allowance was 8 files and 2 directories; its closure check failed after the run, and the measured-bound violation was retained explicitly. No retry was made.

The single affected legacy launch `T-legacy` ran the 774-node `tests/applications/bounded_decision_workflow` selection against the same HEAD. Pytest reported 771 passed, 1 skipped, 2 failed, exit 1, in 515.41 seconds. The bounded reporter recorded 774 started nodes and 774 teardown reports, with no pending reports or recorder errors. The failures were:

* `test_two_clean_roots_twelve_constructions_and_exact_replay`: its `git clone --no-checkout --no-hardlinks` subprocess died with `SIGXFSZ`.
* `test_accepted_s6_archive_recovers_in_clean_matching_build`: its source-clone subprocess died with `SIGXFSZ`.

Both failures occurred with the runner's `RLIMIT_FSIZE` set to 1,048,576 bytes. They are harness/resource failures in clone writes; they do not establish a product failure. The run's stdout was 12,998 bytes (SHA-256 `76982228745872eb4050369d4bf3a3e7fc927adeb2562f7fd4d505278c6617e8`), stderr was empty (SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`), collection JSONL was 122,251 bytes and phase-results JSONL was 662,539 bytes.

The durable reservation charged 25,165,824 repair bytes, 262,144 log bytes, 16,384 index bytes, 3,000 file slots and 1,000 directory slots. Compared with the reservation baseline, measured repair growth was 60,368,472 bytes: an overrun of 35,202,648 bytes. The inventory at close was 1,011,685,672 logical retained bytes, 1,088,245,772 combined bytes including the fixed 76,560,100-byte parent, 1,158,643,712 physical bytes, 36,884 files and 9,386 directories. The original T-legacy transaction could not close because the actual category growth exceeded its reservation. The launch result and outputs remain retained; no capacity was released or recycled.

## Retained corpus accounting

At report preparation the measured categories were: outputs 37,993,222; inputs 29,056,969; repairs 126,816,792; regressions 119,447,074; checkouts 612,016,995; recovery 1,703,784; logs 145,814; indexes 1,580,066; exports 82,924,956 bytes. Total logical use was 1,011,685,672 bytes; combined use was 1,088,245,772; physical use was 1,158,643,712 bytes; files 36,884; directories 9,386. These remain under the amended aggregate ceilings, but the T-legacy reservation was exceeded and its two failed regressions are unresolved.

The original product failure, reporting-hook abort, incomplete-node account, original candidate's 72/72 core evidence, earlier retry results, historical evidence, package and all prior reports retain their original attribution. They are not relabeled as replacement-candidate results. No one of the 180 replacement matrix identities is claimed executed by this continuation.

## Stop and remaining work

The approved finite schedule has no retry allowance. Do not repeat `T-legacy`, the completed controls, or any earlier completed delivery/recovery work. Before any future requalification, an owner must approve a bounded change to the harness's per-file limit and a revised repair reservation sufficient for the measured legacy growth, plus a new finite allocation for the two failed legacy cases and the remaining schedule. Preserve the current failed outputs and reservation anomaly. No matrix, controls, clean delivery, recovery or final full-suite launch occurred after this failure.

The earlier consolidated diagnosis remains at `2026-09-24-reassessment-slice5-consolidated-qualification.md` (original retained report SHA-256 `31baff260236f0d319dfb7a1a0a301d07006fa1e94aa8f9d99427b9ae65c761d`).
