"""ES-001 Group 3: the uniform model-record evidence-reference closure
(acceptance rows EC1-EC6).

For every evidence-bearing model claim (relationship assertion, variable
value specification, and — from Group 4 — variable semantic declaration),
each EvidenceRef of kind model_record must name a member of the supplied
collection, at load, prospective append, and explicit replay subsets
alike (MODEL_REFERENCE_INVALID). Foreign evidence arms remain declared
references and are never validated against foreign ledgers.

EC1's failing-before state is recorded in
docs/superpowers/plans/2026-08-13-es001-integrity-red-baseline.md: at
25b7da6 the specification collection below LOADED with no error.
"""

from pathlib import Path

import pytest

from backend.model_kernel import ModelStore
from backend.model_kernel.contracts import (
    IdentityBindingRecordEvidence,
    ModelIntegrityError,
    ModelRecordEvidence,
    OwnerDeclarationEvidence,
)
from backend.model_kernel.canonical import verify_record_id
from backend.model_kernel.store import validate_record_collection

from tests.model_kernel.builders import (
    ENT_A,
    ENT_B,
    EVIDENCE,
    assertion,
    contains_type,
    registration,
    specification,
    store_with,
    variable_registration,
)

DANGLING = "vrg_" + "f" * 64
DEMO_MODEL = Path("models/demo-printer")


def collection(*records):
    return {record.record_id: record for record in records}


def model_record_evidence(record_id):
    return (OwnerDeclarationEvidence(
        kind="owner_declaration", statement="synthetic closure fixture"),
        ModelRecordEvidence(kind="model_record", record_id=record_id))


class TestEC1SpecificationEvidenceClosure:
    def test_the_group2_reproduction_now_fails_typed(self):
        """The exact failing-before collection: reg + vrg + vsp whose
        evidence cites an ABSENT vrg_. Loaded fine at 25b7da6; now
        MODEL_REFERENCE_INVALID."""
        records = collection(
            registration(ENT_A), variable_registration(),
            specification(evidence=model_record_evidence(DANGLING)))
        with pytest.raises(ModelIntegrityError) as err:
            validate_record_collection("repro-model", records)
        assert err.value.error_code == "MODEL_REFERENCE_INVALID"
        assert DANGLING in err.value.message

    def test_append_refuses_a_dangling_citation(self, tmp_path):
        store = store_with(tmp_path, registration(ENT_A),
                           variable_registration())
        with pytest.raises(ModelIntegrityError) as err:
            store.append(
                specification(evidence=model_record_evidence(DANGLING)))
        assert err.value.error_code == "MODEL_REFERENCE_INVALID"
        # nothing was written
        assert store.load().revision.record_count == 2

    def test_append_accepts_a_present_citation(self, tmp_path):
        vrg = variable_registration()
        store = store_with(tmp_path, registration(ENT_A), vrg)
        store.append(
            specification(evidence=model_record_evidence(vrg.record_id)))
        assert store.load().revision.record_count == 3


class TestEC2UniformAcrossKinds:
    def test_assertion_closure_unchanged(self, tmp_path):
        """The pre-existing assertion rule holds through the shared
        helper: same code, same behavior."""
        rtd = contains_type()
        store = store_with(tmp_path, rtd, registration(ENT_A),
                           registration(ENT_B))
        bad = assertion(rtd, evidence=(
            OwnerDeclarationEvidence(kind="owner_declaration",
                                     statement="synthetic"),
            ModelRecordEvidence(kind="model_record",
                                record_id="rel_" + "e" * 64)))
        with pytest.raises(ModelIntegrityError) as err:
            store.append(bad)
        assert err.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_crafted_on_disk_dangling_specification_fails_load(
            self, tmp_path):
        """The rule holds at load for records that bypassed append."""
        import json

        from backend.model_kernel.canonical import canonical_payload

        store = store_with(tmp_path, registration(ENT_A),
                           variable_registration())
        bad = specification(evidence=model_record_evidence(DANGLING))
        payload = {**canonical_payload(bad), "record_id": bad.record_id}
        (store.records_dir / f"{bad.record_id}.json").write_text(
            json.dumps(payload, sort_keys=True, indent=2,
                       ensure_ascii=False) + "\n", encoding="utf-8")
        with pytest.raises(ModelIntegrityError) as err:
            store.load()
        assert err.value.error_code == "MODEL_REFERENCE_INVALID"


class TestEC3ReplaySubsetClosure:
    def test_omitting_cited_evidence_invalidates_the_replay(
            self, tmp_path):
        """A specification citing a SECOND registration (not its owner):
        the full set loads; a replay subset omitting the cited record is
        invalid via evidence closure specifically."""
        cited = registration(ENT_B)
        vrg = variable_registration()
        spec = specification(
            evidence=model_record_evidence(cited.record_id))
        store = store_with(tmp_path, registration(ENT_A), cited, vrg, spec)
        full = store.load()
        assert full.revision.record_count == 4
        subset = [record_id for record_id in full.revision.record_ids
                  if record_id != cited.record_id]
        with pytest.raises(ModelIntegrityError) as err:
            store.replay(subset)
        assert err.value.error_code == "MODEL_REFERENCE_INVALID"
        assert cited.record_id in err.value.message
        # the honest counterpart: the full explicit membership replays
        replayed = store.replay(full.revision.record_ids)
        assert replayed.revision.revision_id == full.revision.revision_id


class TestEC5ForeignArmsStayDeclared:
    def test_foreign_evidence_is_never_dereferenced(self, tmp_path):
        """A binding-record citation matching nothing anywhere still
        loads: foreign arms are declared references, not closures."""
        store = store_with(tmp_path, registration(ENT_A),
                           variable_registration())
        spec = specification(evidence=(
            OwnerDeclarationEvidence(kind="owner_declaration",
                                     statement="synthetic"),
            IdentityBindingRecordEvidence(
                kind="identity_binding_record",
                binding_set_id="no-such-set",
                record_id="iba_" + "d" * 64)))
        store.append(spec)
        assert store.load().revision.record_count == 3


class TestEC4CommittedLedgerUnaffected:
    def test_committed_model_loads_and_every_id_verifies(self):
        loaded = ModelStore(DEMO_MODEL).load()
        assert loaded.revision.record_count >= 14
        for record in loaded.records.values():
            assert verify_record_id(record), record.record_id
