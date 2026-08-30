# PT-001 synthetic port demonstration

This directory's `records/` ledger contains the original eighteen-record
synthetic demo-printer model plus the bounded PT-001 Slice C append. The append
uses two already-registered synthetic owners and adds exactly two port
registrations, six interface declarations, one positive connection assertion,
and one explicit compatibility declaration. It adds no entity, variable,
constraint, relationship, withdrawal, or correction.

The selected owners and frozen port identities are:

- extrusion subsystem `ent_1a2b3c4d5e6f708192a3b4c5d6e7f809` owns
  `prt_c1d68d104a73405a950556b55f6a4d34`;
- extruder unit `ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50` owns
  `prt_91a3d6db9df440e1a09dbdb185c7b182`.

These owner choices and names are illustrative only. Both ports declare the
same project-local `synthetic-exchange` interface-domain token and
`synthetic-interface` interface-type token under the exact `as_designed`
context. The subsystem port declares `output`; the extruder-unit port declares
`input`. One positive `pcn_` asserts common synthetic connection participation,
and one `pcm_` explicitly declares compatibility using all six current `pif_`
citations. The resulting exact token comparisons and bounded direction-table
finding do not supply engineering truth.

> This is an illustrative synthetic PT-001 fixture. It does not describe or claim any real printer wiring, connector, protocol, pinout, electrical design, behavior, operating activity, flow, influence, causality, safety property, correctness, or operating condition.

In particular:

- geometry does not create these ports;
- CAD does not establish this connection;
- Moonraker does not establish this connection;
- token equality does not establish compatibility;
- direction admissibility does not establish flow;
- explicit compatibility remains a declared synthetic claim.

The pre-PT membership remains an explicit eighteen-record historical revision,
`mrv_919e1b36216243fd211e38a9d36556afa0d46e3660c381302d271ec1fb258c51`.
The PT-001 membership is an explicit twenty-eight-record revision,
`mrv_c6244b6dc41de599de9894b55f4064e41ba5260e7d00f50bffc1e1e63da560a2`.
Historical replay never derives membership by enumerating this directory.

## VP-001 synthetic variable-to-port association demonstration

VP-001 complete, owner accepted, adversarially reviewed, and
dual-clean-checkout verified. The final implementation HEAD before the
administrative acceptance commit is
`82fcb93b233db180d5d2d6c54d465dad390f08a5`.

VP-001 Slice D appended exactly one parentless
`VariablePortAssociation`,
`vpa_f6443787fc9665e24cae80a5ba0650d0bda8abefe87cb60427c8b39068932e49`.
It explicitly associates the existing synthetic hotend-temperature variable
`var_b7e2d3c4f5a6172839405a6b7c8d9e0f` with the existing synthetic
extruder-unit port `prt_91a3d6db9df440e1a09dbdb185c7b182` in the exact
`lifecycle_view/as_designed` context. Both are owned by the exact registered
entity `ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50`.

The VPA is a role-free positive claim made by fixture authority
`test_fixture / vp001_demo_fixture / manual_declaration`. It cites the exact
variable and port registrations plus one claim-specific synthetic owner
declaration. It has no parents, successor, withdrawal, second root, or negative
meaning. Its stored file is 1,184 bytes with SHA-256
`95f9390f784600b2f7a17e74a540d6874722039be5d093614c15a716ff08034e`.

The VP-001 membership is the explicit twenty-nine-record revision
`mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652`.
The 28-record PT-001 membership above remains an unchanged historical boundary
where the endpoints are registered and same-owner but the association is
`not_declared`.

> This is an illustrative synthetic VP-001 association fixture. It does not describe or claim any real printer wiring, signal routing, connector, protocol, sensing location, measurement location, data path, flow, command, control, influence, causality, behavior, compatibility, safety, correctness, activity, or operating condition.

In particular:

- shared ownership did not create the association;
- names did not create the association;
- Moonraker data did not create the association;
- CAD or geometry did not create the association;
- PIF tokens did not create the association;
- PCN topology did not create the association;
- existing observations did not create the association;
- displaying variable state beside a port does not mean the observation
  occurred at, originated at, travelled through, or describes the port.

The deterministic VP-001 disclosure artifact is 17,824 bytes with SHA-256
`a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3`.
It keeps model revision, binding revision, and temporal cutoff as separate
provenance axes, discloses the exact binding declaration and resolution that
attach the observation to the variable, and makes no clock-synchronization
claim. The accepted PT-001 artifact remains byte-identical at SHA-256
`53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`
and is regenerated from the explicit 28-record membership.

## BH-001 synthetic exact-numeric-equality declaration

BH-001 Slice D is implemented and adversarially reviewed from the owner-
approved pre-append contract at `0905de0`. It appends exactly
the neutral variable registration
`vrg_399bbea96bc27689ecab5b6162967b7d7320978117bfe7acddeb05c5ab9aeac6`,
behavior registration
`brg_1fd13b69377257d987775c56f7abf9eedd466d4ca6555ff33ba6b8cf6e815d5e`,
and parentless declaration
`bhd_fd567f57a0ac6a48309b6d04bb4585ed453a143c7789acc18469525f3536be7e`.
The registered unordered, role-free pair is
`var_ab2d312466054c20b0ac764e9bc0114e` and
`var_b7e2d3c4f5a6172839405a6b7c8d9e0f` under behavior anchor
`bhv_80e21f1682e449ca9c65a5e2ee051ea0`.

The explicit 29-record VP membership remains the historical predecessor at
`mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652`.
The current explicit 32-record membership is
`mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`.
The three files retain the approved SHA-256 values
`0652fd7ca32de43d3e21c5a41a5117eb3c19d2a469ffa30f37b407f91937e285`,
`19068707d3bb5423eab4db189208d85749ef18cc3447135d8cfa4ea7f0e89edb`,
and `fa1a40272d100eb81cc15e64cff782a654b3369a91da62bc36b1f26a2cf655cf`.

The declaration has one healthy current root and no BHW, successor,
correction, fork, or second root. The new variable is the sole pinned
registered-anchor exception without a binding `AnchorDeclaration`; shared
ownership did not create or corroborate the behavior. The evaluator therefore
reports `not_executed`, `computed_relation=None`, and
`cohort_admission=not_evaluated`. It preserves the existing variable's 60.4
observation while honestly reporting the new variable's missing observation,
numeric specification, quantity kind, and observation role.

> This is an illustrative synthetic BH-001 exact-numeric-equality declaration. It does not describe or claim any real printer physics, target, command, response, control loop, wiring, signal path, flow, causality, simultaneity, correctness, safety, health, real-machine behavior, or operating condition. Shared ownership, names, topology, VPA associations, semantic compatibility, constraints, and observed correlation did not create this declaration.

The deterministic owner-approved pre-append candidate disclosure artifact is
122406 bytes with SHA-256
`4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3`.
The `not_executed` result is an honest admission result, not evidence that the
declared relation is false. Its `authoritative_append_performed=false` and
`records_proposed` fields describe the frozen rehearsal scope, not the current
repository state. BH-001 complete, owner accepted, adversarially reviewed,
full-suite verified, and dual-clean-checkout verified. Final acceptance does
not convert `not_executed` into observed equality or real-machine truth.
