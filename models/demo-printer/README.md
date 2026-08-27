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
