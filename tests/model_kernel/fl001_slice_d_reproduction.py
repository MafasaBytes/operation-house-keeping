"""Minter-free reproduction of the owner-approved FL-001 Slice D fixture.

This tests-only module has no command-line entry point and never targets the
authoritative store.  It reconstructs the frozen records from semantic inputs,
copies only the explicit 34-record predecessor to a caller-supplied disposable
root, and regenerates the approved disclosure through public APIs.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil
from tempfile import gettempdir

from pydantic import TypeAdapter

import backend.model_kernel as kernel
from backend.model_kernel.canonical import (
    canonical_bytes,
    canonical_payload,
    compute_record_id,
    verify_record_id,
)
from backend.system_identity import FlowAnchor
from tests.model_kernel.bh001_slice_d_rehearsal import (
    authoritative_reproduction as bh_authoritative_reproduction,
)
from tests.model_kernel.test_demo_pt001 import (
    ARTIFACT_BYTES as PT_ARTIFACT_BYTES,
    ARTIFACT_SHA256 as PT_ARTIFACT_SHA256,
    _artifact_bytes as pt_artifact_bytes,
)
from tests.model_state.test_demo_vp001 import (
    ARTIFACT_BYTES as VP_ARTIFACT_BYTES,
    ARTIFACT_SHA256 as VP_ARTIFACT_SHA256,
    _artifact_bytes as vp_artifact_bytes,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
AUTHORITATIVE_MODEL = REPO_ROOT / "models/demo-printer"
MANIFEST_PATH = REPO_ROOT / (
    "docs/superpowers/reports/"
    "2026-09-03-fl001-slice-d-candidate-identities.json")
DISCLOSURE_PATH = REPO_ROOT / (
    "docs/superpowers/reports/"
    "2026-09-03-fl001-slice-d-candidate-disclosure.json")

MANIFEST_BYTES = 67634
MANIFEST_SHA256 = (
    "f5d8937442cec596910e994c0552e2c3315164915235b1f4c64a1650e1e3c4be")
DISCLOSURE_BYTES = 660516
DISCLOSURE_SHA256 = (
    "096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b")
ACCEPTED_SOURCE_HEAD = "81052bc06867c043f0d4bb72e38d1f58cdaa182f"
FLOW_ANCHOR_ID = "flo_ddefa85855ff4dc19f8ecfd022033883"
FRG_ID = (
    "frg_9b76a51bd6a1165572fad2dcf344dad90f17c68c0f5a6e1977874bd6224d7cd7")
FLD_ID = (
    "fld_f5a192053bc42c53ce9e4d3bd49b011589d17191bdb97f9bac93fcc359872192")
APPEND_ORDER = (FRG_ID, FLD_ID)
PREDECESSOR_REVISION = (
    "mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41")
INTERMEDIATE_REVISION = (
    "mrv_6b43b1002740094d84a9a7826df57b84ed0abd89e8e921a4be75e1a694ade8a2")
PROPOSED_REVISION = (
    "mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee")
PREDECESSOR_AGGREGATE = (
    "cf3a534b4b7d13a85fb1f23a3e81881b03e084fc508145950cbc8618f247d6cd")

_SEMANTIC_BOUNDARY = {
    "aligned_means": (
        "The exact pinned PT assertions are current in one healthy lineage "
        "and their current model declarations compare consistently; this is "
        "not physical validation."),
    "current_means": (
        "Current is membership-relative assertion DAG activity, not physical "
        "flow activity or temporal freshness."),
    "declared_means": (
        "The selected membership contains one healthy model declaration root "
        "for the exact context and pins."),
    "healthy_means": (
        "Healthy means one current tip in a model correction lineage, not "
        "physical-system health."),
    "registered_means": (
        "The selected membership contains the admitted permanent logical "
        "directed flow registration."),
}


class FrozenContractError(AssertionError):
    """The owner-approved byte or semantic contract does not reproduce."""


@dataclass(frozen=True)
class ReproductionResult:
    artifact: bytes
    artifact_bytes: int
    artifact_sha256: str
    record_ids: tuple[str, str]
    record_file_sha256: tuple[str, str]
    intermediate_revision_id: str
    revision_id: str
    predecessor_aggregate_sha256: str


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def _strict_json(raw: bytes):
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise FrozenContractError("duplicate JSON object key")
            result[key] = value
        return result

    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs)
    except (UnicodeError, ValueError, TypeError) as error:
        raise FrozenContractError("frozen JSON is invalid") from error


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FrozenContractError(message)


def validate_disclosure_bytes(raw: bytes | None = None) -> dict:
    raw = DISCLOSURE_PATH.read_bytes() if raw is None else raw
    _require(len(raw) == DISCLOSURE_BYTES, "disclosure byte count changed")
    _require(sha256_bytes(raw) == DISCLOSURE_SHA256,
             "disclosure whole-file digest changed")
    value = _strict_json(raw)
    _require(canonical_json_bytes(value) == raw,
             "disclosure is not canonical JSON plus one newline")
    _require(value.get("artifact") ==
             "FL-001 synthetic flow declaration candidate",
             "disclosure artifact name changed")
    _require(value.get("schema_version") == "1",
             "disclosure schema changed")
    checksum = value.get("artifact_checksum", {})
    _require(checksum.get("algorithm") == "sha256" and
             checksum.get("scope") == "content" and
             checksum.get("value") == sha256_bytes(
                 canonical_json_bytes(value.get("content"))),
             "disclosure embedded checksum changed")
    return value


def load_frozen_contract(*, manifest_bytes: bytes | None = None) -> dict:
    raw = MANIFEST_PATH.read_bytes() if manifest_bytes is None else manifest_bytes
    _require(len(raw) == MANIFEST_BYTES, "manifest byte count changed")
    _require(sha256_bytes(raw) == MANIFEST_SHA256,
             "manifest whole-file digest changed")
    value = _strict_json(raw)
    _require(canonical_json_bytes(value) == raw,
             "manifest is not canonical JSON plus one newline")
    _require(value.get("manifest") == "FL-001 Slice D candidate identities",
             "manifest name changed")
    _require(value.get("schema_version") == "1" and
             value.get("status") == "non_authoritative_candidate",
             "manifest schema or status changed")
    content = value.get("content")
    checksum = value.get("manifest_checksum", {})
    _require(checksum.get("algorithm") == "sha256" and
             checksum.get("scope") == "content" and
             checksum.get("value") == sha256_bytes(
                 canonical_json_bytes(content)),
             "manifest embedded checksum changed")
    _require(content.get("accepted_source_head") == ACCEPTED_SOURCE_HEAD,
             "manifest accepted source HEAD changed")
    _require(content.get("flow_anchor", {}).get("anchor_id") == FLOW_ANCHOR_ID,
             "manifest FlowAnchor changed")
    disclosure = validate_disclosure_bytes()
    binding = content.get("candidate_contract", {}).get(
        "disclosure_artifact", {})
    _require(binding == {
        "bytes": DISCLOSURE_BYTES,
        "path": (
            "docs/superpowers/reports/"
            "2026-09-03-fl001-slice-d-candidate-disclosure.json"),
        "sha256": DISCLOSURE_SHA256,
    }, "manifest disclosure binding changed")
    _require(disclosure.get("disclaimer") == content.get("disclaimer") and
             disclosure.get("warnings") == content.get("warnings"),
             "manifest/disclosure semantic boundary differs")
    return value


def _evidence(specification: dict) -> tuple:
    return tuple([
        *(kernel.ModelRecordEvidence(kind="model_record", record_id=record_id)
          for record_id in specification["model_record_ids"]),
        kernel.OwnerDeclarationEvidence(
            kind="owner_declaration",
            statement=specification["owner_declaration"]),
    ])


def _stored_bytes(record) -> bytes:
    payload = {**canonical_payload(record), "record_id": record.record_id}
    return (json.dumps(payload, sort_keys=True, indent=2,
                       ensure_ascii=False) + "\n").encode("utf-8")


def _record_contract(record, stored: bytes) -> dict:
    raw = canonical_bytes(record)
    return {
        "canonical_bytes": raw.decode("utf-8"),
        "canonical_payload": canonical_payload(record),
        "canonical_payload_bytes": len(raw),
        "canonical_payload_sha256": sha256_bytes(raw),
        "identity_verification": {
            "computed_record_id": compute_record_id(record),
            "record_id_suffix_equals_canonical_sha256": (
                record.record_id.split("_", 1)[1] == sha256_bytes(raw)),
            "verify_record_id": verify_record_id(record),
        },
        "record": record.model_dump(mode="json"),
        "record_id": record.record_id,
        "stored_file": {
            "bytes": len(stored),
            "filename": f"{record.record_id}.json",
            "sha256": sha256_bytes(stored),
            "stored_json": stored.decode("utf-8"),
        },
    }


def candidate_records(frozen: dict | None = None):
    frozen = load_frozen_contract() if frozen is None else frozen
    content = frozen["content"]
    semantics = content["semantic_inputs"]
    registration = semantics["registration"]
    declaration = semantics["declaration"]
    anchor = FlowAnchor.model_validate(registration["anchor"])
    context = TypeAdapter(kernel.AssertionContext).validate_python(
        declaration["context"])

    frg = kernel.build_record(
        kernel.FlowRegistration,
        anchor=anchor,
        source_port_anchor_ids=tuple(registration["source_port_anchor_ids"]),
        sink_port_anchor_ids=tuple(registration["sink_port_anchor_ids"]),
        flow_kind=kernel.FlowKindToken.model_validate(
            registration["flow_kind"]),
        evidence=_evidence(registration["evidence"]),
        recorded_at=registration["recorded_at"],
        authority=kernel.AuthorityRef.model_validate(
            registration["authority"]),
        note=registration["note"],
    )
    fld = kernel.build_record(
        kernel.FlowDeclaration,
        flow_anchor_id=declaration["flow_anchor_id"],
        context=context,
        connection_assertion_record_id=(
            declaration["connection_assertion_record_id"]),
        source_direction_pins=tuple(
            kernel.FlowDirectionDeclarationPin.model_validate(value)
            for value in declaration["source_direction_pins"]),
        sink_direction_pins=tuple(
            kernel.FlowDirectionDeclarationPin.model_validate(value)
            for value in declaration["sink_direction_pins"]),
        evidence=_evidence(declaration["evidence"]),
        supersedes=tuple(declaration["supersedes"]),
        recorded_at=declaration["recorded_at"],
        authority=kernel.AuthorityRef.model_validate(
            declaration["authority"]),
        note=declaration["note"],
    )
    records = (frg, fld)
    expected = content["candidate_contract"]
    _require(tuple(record.record_id for record in records) == APPEND_ORDER ==
             tuple(expected["append_order"]), "candidate IDs/order changed")
    for record, contract in zip(records, expected["record_contracts"],
                                strict=True):
        computed = _record_contract(record, _stored_bytes(record))
        _require(computed == contract,
                 f"frozen contract changed for {record.record_id}")
    return records


def _record_inventory(record_ids: tuple[str, ...] | list[str]) -> dict:
    return {
        f"{record_id}.json": sha256_bytes(
            (AUTHORITATIVE_MODEL / "records" /
             f"{record_id}.json").read_bytes())
        for record_id in record_ids
    }


def _inventory_digest(inventory: dict[str, str]) -> str:
    return sha256_bytes(canonical_json_bytes(dict(sorted(inventory.items()))))


def authoritative_snapshot() -> tuple:
    paths = sorted((AUTHORITATIVE_MODEL / "records").glob("*.json"))
    return tuple((path.name, len(path.read_bytes()),
                  sha256_bytes(path.read_bytes())) for path in paths)


def verify_authoritative_ledger(expected: str = "proposed"):
    frozen = load_frozen_contract()
    content = frozen["content"]
    predecessor = content["predecessor"]
    candidate = content["candidate_contract"]
    _require(expected in {"predecessor", "proposed"},
             "unknown authoritative gate")
    membership = (predecessor["membership"] if expected == "predecessor"
                  else candidate["proposed_membership"])
    revision = (predecessor["revision"] if expected == "predecessor"
                else candidate["proposed_revision"]["revision_id"])
    records_dir = AUTHORITATIVE_MODEL / "records"
    _require(not AUTHORITATIVE_MODEL.is_symlink() and
             not records_dir.is_symlink(), "authoritative path is a symlink")
    paths = sorted(records_dir.glob("*.json"))
    _require(all(not path.is_symlink() for path in paths),
             "authoritative record is a symlink")
    _require(tuple(path.stem for path in paths) == tuple(membership),
             "authoritative membership changed")
    loaded = kernel.ModelStore(AUTHORITATIVE_MODEL).load()
    _require(loaded.revision.record_count == len(membership) and
             loaded.revision.revision_id == revision and
             tuple(loaded.revision.record_ids) == tuple(membership),
             "authoritative revision changed")
    actual_predecessor = _record_inventory(predecessor["membership"])
    _require(actual_predecessor == predecessor["record_file_sha256"] and
             _inventory_digest(actual_predecessor) == PREDECESSOR_AGGREGATE,
             "authoritative predecessor bytes changed")
    _require(all(verify_record_id(record)
                 for record in loaded.records.values()),
             "authoritative record identity failed")
    counts = (len(loaded.flow_registrations), len(loaded.flow_declarations),
              len(loaded.flow_declaration_withdrawals))
    _require(counts == ((0, 0, 0) if expected == "predecessor"
                        else (1, 1, 0)), "authoritative flow counts changed")
    if expected == "proposed":
        records = candidate_records(frozen)
        for record, contract in zip(records, candidate["record_contracts"],
                                    strict=True):
            raw = (records_dir / f"{record.record_id}.json").read_bytes()
            _require(raw.decode("utf-8") ==
                     contract["stored_file"]["stored_json"] and
                     sha256_bytes(raw) == contract["stored_file"]["sha256"],
                     "authoritative candidate stored bytes changed")
    return loaded


def _safe_root(root: Path) -> Path:
    resolved = root.resolve()
    authoritative = AUTHORITATIVE_MODEL.resolve()
    repository = REPO_ROOT.resolve()
    system_temporary = Path(gettempdir()).resolve()
    _require(resolved != authoritative and
             authoritative not in resolved.parents and
             resolved not in authoritative.parents,
             "disposable root overlaps authoritative model")
    _require(resolved != repository and repository not in resolved.parents,
             "disposable root overlaps repository")
    _require(resolved != system_temporary and
             system_temporary in resolved.parents,
             "disposable root must be below system temporary directory")
    if resolved.exists():
        _require(not any(resolved.iterdir()),
                 "disposable root must be absent or empty")
    return resolved


def _compact(result) -> dict:
    return result.model_dump(mode="json", exclude={"material"})


def _full(result) -> dict:
    return result.model_dump(mode="json")


def _historical_replay(source_store, rows, anchor_id, source_port, context,
                       frg_id, fld_id):
    values = []
    for expected in rows:
        loaded = source_store.replay(tuple(expected["membership"]))
        queries = kernel.ModelQueries(loaded)
        row = {
            "declaration_assertion": _compact(
                queries.flow_assertion(fld_id)),
            "flow": _compact(queries.flow(anchor_id)),
            "flow_declaration": _compact(
                queries.flow_declaration(anchor_id, context=context)),
            # Historical memberships are frozen explicit replay inputs.  A
            # revision normalizes them internally, but the artifact preserves
            # the accepted input ordering (notably the 18-record CN boundary).
            "membership": list(expected["membership"]),
            "record_count": loaded.revision.record_count,
            "registration_assertion": _compact(
                queries.flow_assertion(frg_id)),
            "revision_id": loaded.revision.revision_id,
            "source_port_flows": _compact(
                queries.flows_involving_port(source_port, context=context)),
        }
        _require(row == expected, "historical flow replay changed")
        values.append(row)
    return values


def _accepted_artifacts(root: Path, expected: dict) -> dict:
    pt = pt_artifact_bytes()
    vp = vp_artifact_bytes(root / "vp")
    bh = bh_authoritative_reproduction(root / "bh")
    result = {
        "bh": {"bytes": bh["artifact_bytes"],
               "sha256": bh["artifact_sha256"]},
        "fl_slice_a_report": expected["fl_slice_a_report"],
        "fl_slice_b_report": expected["fl_slice_b_report"],
        "pt": {"bytes": len(pt), "sha256": sha256_bytes(pt)},
        "st_candidate_disclosure": expected["st_candidate_disclosure"],
        "st_candidate_manifest": expected["st_candidate_manifest"],
        "st_completion_report": expected["st_completion_report"],
        "vp": {"bytes": len(vp), "sha256": sha256_bytes(vp)},
    }
    _require((len(pt), sha256_bytes(pt)) ==
             (PT_ARTIFACT_BYTES, PT_ARTIFACT_SHA256),
             "accepted PT artifact changed")
    _require((len(vp), sha256_bytes(vp)) ==
             (VP_ARTIFACT_BYTES, VP_ARTIFACT_SHA256),
             "accepted VP artifact changed")
    for value in expected.values():
        if "path" in value:
            raw = (REPO_ROOT / value["path"]).read_bytes()
            _require((len(raw), sha256_bytes(raw)) ==
                     (value["bytes"], value["sha256"]),
                     "accepted filesystem artifact changed")
    _require(result == expected, "accepted artifact inventory changed")
    return result


def _tree_inventory(*roots: Path) -> dict[str, str]:
    result = {}
    for root in roots:
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            key = f"{root.relative_to(REPO_ROOT).as_posix()}/" \
                  f"{path.relative_to(root).as_posix()}"
            result[key] = sha256_bytes(path.read_bytes())
    return result


def run_reproduction(root: Path, *, reverse_copy_order: bool = False,
                     expected_authoritative: str = "proposed") -> \
        ReproductionResult:
    root = _safe_root(root)
    frozen = load_frozen_contract()
    disclosure = validate_disclosure_bytes()
    content = frozen["content"]
    predecessor = content["predecessor"]
    candidate = content["candidate_contract"]
    semantics = content["semantic_inputs"]
    records = candidate_records(frozen)
    verify_authoritative_ledger(expected_authoritative)

    protected_roots = (
        AUTHORITATIVE_MODEL,
        REPO_ROOT / "bindings/demo-printer",
        REPO_ROOT / "bindings/demo-printer-model",
        REPO_ROOT / "interpretations/demo-printer",
        REPO_ROOT / "showcases/demo-printer",
    )
    protected_before = _tree_inventory(*protected_roots)
    raw_before = _tree_inventory(REPO_ROOT / "var/raw_store")

    model_root = root / "demo-printer"
    records_dir = model_root / "records"
    records_dir.mkdir(parents=True)
    copy_ids = list(predecessor["membership"])
    if reverse_copy_order:
        copy_ids.reverse()
    for record_id in copy_ids:
        shutil.copyfile(
            AUTHORITATIVE_MODEL / "records" / f"{record_id}.json",
            records_dir / f"{record_id}.json")
    store = kernel.ModelStore(model_root)
    base = store.load()
    _require(base.revision.record_count == 34 and
             base.revision.revision_id == PREDECESSOR_REVISION,
             "disposable predecessor differs")
    source_port = semantics["registration"]["source_port_anchor_ids"][0]
    sink_port = semantics["registration"]["sink_port_anchor_ids"][0]
    context = TypeAdapter(kernel.AssertionContext).validate_python(
        semantics["declaration"]["context"])
    other_context = kernel.LifecycleViewContext(
        kind="lifecycle_view", view="as_operated")
    anchor_id = content["flow_anchor"]["anchor_id"]
    base_queries = kernel.ModelQueries(base)
    predecessor_queries = {
        "declaration_assertion": _compact(
            base_queries.flow_assertion(FLD_ID)),
        "flow": _compact(base_queries.flow(anchor_id)),
        "flow_declaration": _compact(base_queries.flow_declaration(
            anchor_id, context=context)),
        "registration_assertion": _compact(
            base_queries.flow_assertion(FRG_ID)),
        "sink_port_flows": _compact(base_queries.flows_involving_port(
            sink_port, context=context)),
        "source_port_flows": _compact(base_queries.flows_involving_port(
            source_port, context=context)),
    }

    store.append(records[0])
    middle = store.load()
    _require(middle.revision.record_count == 35 and
             middle.revision.revision_id == INTERMEDIATE_REVISION,
             "35-record intermediate changed")
    middle_queries = kernel.ModelQueries(middle)
    after_registration = {
        "flow": _compact(middle_queries.flow(anchor_id)),
        "flow_declaration": _compact(middle_queries.flow_declaration(
            anchor_id, context=context)),
        "registration_assertion": _compact(
            middle_queries.flow_assertion(FRG_ID)),
        "revision": middle.revision.model_dump(mode="json"),
        "sink_port_flows": _compact(middle_queries.flows_involving_port(
            sink_port, context=context)),
        "source_port_flows": _compact(middle_queries.flows_involving_port(
            source_port, context=context)),
    }

    store.append(records[1])
    final = store.load()
    _require(final.revision.record_count == 36 and
             final.revision.revision_id == PROPOSED_REVISION and
             tuple(final.revision.record_ids) ==
             tuple(candidate["proposed_membership"]),
             "36-record candidate changed")
    final_queries = kernel.ModelQueries(final)
    final_flow_queries = {
        "declaration_assertion": _full(
            final_queries.flow_assertion(FLD_ID)),
        "flow": _full(final_queries.flow(anchor_id)),
        "flow_declaration": _full(final_queries.flow_declaration(
            anchor_id, context=context)),
        "other_context_declaration": _full(
            final_queries.flow_declaration(anchor_id, context=other_context)),
        "other_context_sink_port_flows": _full(
            final_queries.flows_involving_port(
                sink_port, context=other_context)),
        "other_context_source_port_flows": _full(
            final_queries.flows_involving_port(
                source_port, context=other_context)),
        "registration_assertion": _full(
            final_queries.flow_assertion(FRG_ID)),
        "sink_port_flows": _full(final_queries.flows_involving_port(
            sink_port, context=context)),
        "source_port_flows": _full(final_queries.flows_involving_port(
            source_port, context=context)),
    }
    pcn_id = semantics["declaration"]["connection_assertion_record_id"]
    source_pif = semantics["declaration"]["source_direction_pins"][0][
        "declaration_record_id"]
    sink_pif = semantics["declaration"]["sink_direction_pins"][0][
        "declaration_record_id"]
    pt_queries = {
        "connection_assertion": _full(
            final_queries.port_assertion(pcn_id)),
        "exact_connection": _full(final_queries.connections_exact(
            (source_port, sink_port), context=context)),
        "sink_direction_assertion": _full(
            final_queries.port_assertion(sink_pif)),
        "sink_interface": _full(
            final_queries.port_interface(sink_port, context=context)),
        "source_direction_assertion": _full(
            final_queries.port_assertion(source_pif)),
        "source_interface": _full(
            final_queries.port_interface(source_port, context=context)),
    }
    public_queries = {
        "after_registration_35": after_registration,
        "final_36": final_flow_queries,
        "predecessor_34_structured_absence": predecessor_queries,
        "pt_support_36": pt_queries,
    }
    _require(public_queries == disclosure["content"]["public_queries"],
             "public query serialization changed")

    histories = _historical_replay(
        kernel.ModelStore(AUTHORITATIVE_MODEL),
        predecessor["historical_replay"], anchor_id, source_port,
        context, FRG_ID, FLD_ID)
    accepted = _accepted_artifacts(
        root / "accepted-artifacts",
        content["preservation"]["accepted_artifacts"])
    stored = tuple((store.records_dir / f"{record.record_id}.json").read_bytes()
                   for record in records)
    record_contracts = [
        _record_contract(record, raw)
        for record, raw in zip(records, stored, strict=True)
    ]
    _require(record_contracts == candidate["record_contracts"],
             "stored candidate records changed")
    predecessor_inventory = {
        f"{record_id}.json": sha256_bytes(
            (store.records_dir / f"{record_id}.json").read_bytes())
        for record_id in predecessor["membership"]
    }
    _require(predecessor_inventory == predecessor["record_file_sha256"] and
             _inventory_digest(predecessor_inventory) ==
             PREDECESSOR_AGGREGATE,
             "disposable predecessor bytes changed")

    artifact_content = {
        "authority": semantics["registration"]["authority"],
        "context": semantics["declaration"]["context"],
        "flow_anchor": content["flow_anchor"],
        "flow_kind": semantics["registration"]["flow_kind"],
        "historical_replay": histories,
        "model": {
            "candidate_append_order": list(APPEND_ORDER),
            "candidate_records": record_contracts,
            "predecessor_aggregate_sha256": PREDECESSOR_AGGREGATE,
            "predecessor_file_sha256": predecessor_inventory,
            "predecessor_membership": list(predecessor["membership"]),
            "predecessor_revision": PREDECESSOR_REVISION,
            "proposed_membership": list(final.revision.record_ids),
            "proposed_revision": final.revision.model_dump(mode="json"),
        },
        "preservation": {
            "accepted_artifacts": accepted,
            "protected_tree_aggregate_sha256": content["preservation"][
                "protected_tree_aggregate_sha256"],
            "runtime_evidence_aggregate_sha256": content["preservation"][
                "runtime_evidence_aggregate_sha256"],
        },
        "public_queries": public_queries,
        "raw_authenticity_limitation": content[
            "raw_authenticity_limitation"],
        "scope": {
            "authoritative_append_performed": False,
            "candidate_record_counts": {
                "correction": 0,
                "flow_declaration": 1,
                "flow_declaration_withdrawal": 0,
                "flow_registration": 1,
                "other": 0,
                "second_root": 0,
            },
            "statement": (
                "This owner-gate artifact was generated only from disposable "
                "ledgers. No authoritative fixture was mutated."),
        },
        "semantic_boundary": _SEMANTIC_BOUNDARY,
    }
    artifact = canonical_json_bytes({
        "artifact": "FL-001 synthetic flow declaration candidate",
        "artifact_checksum": {
            "algorithm": "sha256",
            "scope": "content",
            "value": sha256_bytes(canonical_json_bytes(artifact_content)),
        },
        "content": artifact_content,
        "disclaimer": content["disclaimer"],
        "schema_version": "1",
        "status": "non_authoritative_candidate",
        "warnings": content["warnings"],
    })
    _require(artifact == DISCLOSURE_PATH.read_bytes() and
             len(artifact) == DISCLOSURE_BYTES and
             sha256_bytes(artifact) == DISCLOSURE_SHA256,
             "disclosure reproduction changed")
    _require(_tree_inventory(*protected_roots) == protected_before and
             _tree_inventory(REPO_ROOT / "var/raw_store") == raw_before,
             "reproduction mutated protected repository content")
    return ReproductionResult(
        artifact=artifact,
        artifact_bytes=len(artifact),
        artifact_sha256=sha256_bytes(artifact),
        record_ids=APPEND_ORDER,
        record_file_sha256=tuple(sha256_bytes(raw) for raw in stored),
        intermediate_revision_id=middle.revision.revision_id,
        revision_id=final.revision.revision_id,
        predecessor_aggregate_sha256=_inventory_digest(
            predecessor_inventory),
    )
