"""Independent disposable public-builder/store FC witnesses; no demo writes."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import BaseModel

import backend.model_kernel as kernel
from backend.model_kernel.canonical import canonical_bytes
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.fc001_slice_a_helpers import (
    INDEX_NAMES, declaration, membership, replace, withdrawal, world,
)
from tests.model_kernel.test_flow_measurement_slice_a import withdrawal as fm_withdrawal


def _plain(value):
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return value


def _index_rows(loaded):
    # Capture ACTUAL mapping iteration, including body/subject keys. Sorting
    # these rows would erase precisely the ordering defects this witnesses.
    return {name: [[_plain(key), _plain(value)] for key, value in
                   getattr(loaded, "flow_operating_criterion_" + name).items()]
            for name in INDEX_NAMES}


def witness_bytes(reverse=False):
    """Rebuild records and a fresh ModelStore on every call, then serialize facts.

    Dependency order is retained for append; only independent sibling batches
    reverse. Collection membership and replay inputs reverse in their entirety.
    Evidence and convergence-parent input order also reverse before builders.
    """
    base, witness, crg, vcn = world()

    def ordered(items):
        return tuple(reversed(items)) if reverse else tuple(items)

    evidence = ordered((kernel.OwnerDeclarationEvidence(kind="owner_declaration", statement="disposable alpha"),
                        kernel.OwnerDeclarationEvidence(kind="owner_declaration", statement="disposable beta")))
    equal = replace(witness, note="independent equal witness")
    opposite = replace(witness, orientation="opposite")
    renewed_vcn = replace(vcn, supersedes=(vcn.record_id,))
    root = declaration(witness, crg, vcn, evidence=evidence)
    peer = declaration(equal, crg, vcn, evidence=evidence)
    other_subject = declaration(opposite, crg, vcn, evidence=evidence)
    inactive = declaration(witness, crg, renewed_vcn, evidence=evidence)
    a = replace(root, supersedes=(root.record_id,), note="fork a")
    b = replace(root, supersedes=(root.record_id,), note="fork b")
    merged = declaration(witness, crg, renewed_vcn, evidence=evidence,
                         supersedes=ordered((a.record_id, b.record_id)))
    batches = (base, ordered((equal, opposite, renewed_vcn)),
               ordered((root, peer, other_subject, inactive)), ordered((a, b)),
               (merged,), ordered((withdrawal(inactive), fm_withdrawal(witness))))
    appended = tuple(record for batch in batches for record in batch)
    selected = ordered(appended)
    collection = validate_record_collection("fc001-disposable", membership(*selected))
    with TemporaryDirectory(prefix="fc001-witness-") as temporary:
        store = kernel.ModelStore(Path(temporary) / "fc001-disposable")
        for record in appended:
            store.append(record)
        loaded = store.load()
        replay = store.replay(tuple(record.record_id for record in selected))
        assert collection.revision == loaded.revision == replay.revision
        result = {
            "revision": loaded.revision.model_dump(mode="json"),
            "canonical_records": [[record_id, canonical_bytes(loaded.records[record_id]).hex()]
                                  for record_id in loaded.revision.record_ids],
            "stored_records": [[record_id, (store.records_dir / (record_id + ".json")).read_bytes().hex()]
                               for record_id in loaded.revision.record_ids],
            "collection_index_rows": _index_rows(collection),
            "loaded_index_rows": _index_rows(loaded),
            "replayed_index_rows": _index_rows(replay),
        }
    return json.dumps(result, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")
