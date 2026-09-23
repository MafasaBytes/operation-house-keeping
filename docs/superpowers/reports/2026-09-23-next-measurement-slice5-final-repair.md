# Slice 5 final repair evidence

## Fresh implementation and tests

The semantic vertical path is implemented through the existing Slice 1–4 entry points. `evaluate_semantic_bundle` binds a real maintained build witness, resolves the typed closure and authority pin, reuses public admission, requalifies supplied support, recomputes minimax, serializes result/trace and publishes the seven-file bundle. `replay_semantic_bundle` recovers closure/public inputs/support/candidates from the retained bundle, regenerates the current executable witness, repeats admission/support/ranking, and compares newly derived result/trace bytes. A result forged and then rehashed into the manifest is rejected by semantic replay.

Implementation commits are `7d38e4d59a0622872dff821de7889e5efcbadc52`, `d2f732f8556a16d38f008f8efda39cf798df2287`, `150fb6f3074b437ff66714d207d15e8056570580`, `489f35d24c725860a97421713a8e5857c7525b58`, and `2c2f9d44339249a678830a43d2e90f73f55729a8`. The exact tested implementation HEAD is `671f4f2b542f1f8d300dcfbd9e82e32e3783b62c`.

The focused Slice 1–5 selection passes **28 tests**, including the real vertical path, standalone replay, forged-result semantic rejection, delivery controls, Slice 1–4 tests, and the legacy replay regression.

## Obligation mapping

* Real semantic fixture and discriminating result: covered by the vertical fixture and T1 ranking result.
* Withholding: existing Slice 2/4 tests remain in the focused selection; semantic bundle replay carries admission/ranking dispositions.
* Executable binding: the retained `nm.build.v1` embeds the current `build.identity()` wire and digest; substituted witness data is rejected.
* Typed closure and authority: the vertical path calls `resolve_required_closure` with the invocation selection pin.
* Independent replay: closure/public inputs/support/candidates are recovered from the bundle and recomputed; caller-supplied expected result/trace are not used by `replay_semantic_bundle`.
* Forged result, no-overwrite, incomplete bundle, and file-integrity twins: covered by vertical and delivery tests.

## Remaining contract gap

The exact approved production command carriage remains unresolved. The separate `measurement_cli` exposes storage verification/replay, but it is not wired into the maintained application’s approved `measurement-evaluate --invocation FILE --objects-dir DIR --authority-pin SHA --output-dir NEWDIR` surface, and it does not yet safely reconstruct public input/support carriage from that command’s exact arguments. The maintained ext4/root-containment publication boundary and full logical/physical accounting are also not fully integrated; the vertical test measures semantic execution only through its retained bundle, not the approved runtime accounting envelope.

This is a concrete delivery-contract integration gap, not a Slice 6 qualification task. Completing it requires deciding how the approved command’s objects directory carries public request/snapshot and support/candidate material while preserving the frozen closure contract. No bypass or limit increase is introduced.

Historical completion and delivery-review reports remain byte-for-byte preserved. Slice 6 and the full proof remain unauthorized; Slice 5 acceptance remains withheld pending this command/accounting integration decision.
