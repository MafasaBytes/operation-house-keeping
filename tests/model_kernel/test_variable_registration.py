"""VM-001 Part A: explicit variable membership in the model kernel.

Matrix sections A (record/identity integrity), B (revision/replay,
synthetic), C (kernel queries). Demo-fixture rows live in
test_demo_model.py. A variable registration is membership — never state,
semantic enrichment, or a relationship edge."""

import hashlib
import json

import pytest
from pydantic import ValidationError

from backend.model_kernel import (
    AuthorityRef,
    EntityVariablesResult,
    ModelKernelError,
    ModelQueries,
    ModelRecordEvidence,
    ModelStore,
    VariableRegistration,
    VariableRegistrationSummary,
    VariableResult,
    build_record,
)
from backend.model_kernel.canonical import (
    canonical_bytes,
    compute_revision_id,
    verify_record_id,
)
from backend.model_kernel.store import validate_record_collection
from backend.system_identity import EntityAnchor

from tests.model_kernel.builders import (
    AS_BUILT,
    AUTHORITY,
    ENT_A,
    ENT_B,
    ENT_C,
    T0,
    VAR_A,
    VAR_B,
    VAR_C,
    assertion,
    containment_world,
    contains_type,
    registration,
    store_with,
    variable_anchor,
    variable_registration,
)


def snapshot(store):
    return {path.name: path.read_bytes()
            for path in sorted(store.records_dir.iterdir())}


def corrupt(record, rehash=True, **overrides):
    import warnings

    forged = record.model_copy(update=overrides)
    if rehash:
        from backend.model_kernel.canonical import compute_record_id

        with warnings.catch_warnings():  # forging is a test-side act; the
            warnings.simplefilter("ignore")  # kernel path stays warning-free
            forged = forged.model_copy(update={
                "record_id": compute_record_id(forged)})
    return forged


# ---------------------------------------------------------------- A. record


class TestRecordIntegrity:
    def test_round_trip_byte_level(self, tmp_path):
        record = variable_registration(role="hotend-temperature")
        store = store_with(tmp_path, registration(ENT_A), record)
        loaded = store.load()
        reloaded = loaded.records[record.record_id]
        assert reloaded == record
        assert reloaded.anchor == variable_anchor(role="hotend-temperature")
        assert canonical_bytes(reloaded) == canonical_bytes(record)
        on_disk = (store.records_dir / f"{record.record_id}.json").read_text()
        assert on_disk.endswith("\n")
        assert json.loads(on_disk)["record_id"] == record.record_id

    def test_append_owner_missing(self, tmp_path):
        store = store_with(tmp_path, registration(ENT_B))  # not the owner
        before = snapshot(store)
        with pytest.raises(ModelKernelError) as excinfo:
            store.append(variable_registration(owner=ENT_A))
        assert excinfo.value.error_code == "MODEL_REFERENCE_INVALID"
        assert str(tmp_path) not in str(excinfo.value)
        assert snapshot(store) == before

    def test_crafted_file_owner_missing_fails_load(self, tmp_path):
        store = store_with(tmp_path, registration(ENT_A))
        record = variable_registration(owner=ENT_A)
        good = store.append(record)
        # remove the owner file directly: the set is now invalid at load
        (store.records_dir / f"{registration(ENT_A).record_id}.json").unlink()
        with pytest.raises(ModelKernelError) as excinfo:
            store.load()
        assert excinfo.value.error_code == "MODEL_REFERENCE_INVALID"
        assert good in str(excinfo.value)

    def test_replay_reference_closure(self, tmp_path):
        owner = registration(ENT_A)
        record = variable_registration()
        other = registration(ENT_B)
        store = store_with(tmp_path, owner, other, record)
        with pytest.raises(ModelKernelError) as excinfo:
            store.replay([record.record_id])
        assert excinfo.value.error_code == "MODEL_REFERENCE_INVALID"
        both = store.replay([owner.record_id, record.record_id])
        assert set(both.records) == {owner.record_id, record.record_id}
        old = store.replay([owner.record_id, other.record_id])
        assert record.record_id not in old.records

    def test_idempotent_reappend(self, tmp_path):
        """Correction 8 case 1: byte-identical re-append is the accepted
        no-op — nothing written, revision unchanged."""
        record = variable_registration()
        store = store_with(tmp_path, registration(ENT_A), record)
        before = snapshot(store)
        revision = store.load().revision
        assert store.append(record) == record.record_id
        assert snapshot(store) == before
        assert store.load().revision == revision

    def test_duplicate_distinct_record_agreeing_anchor(self, tmp_path):
        """Correction 8 case 2: same anchor_id, agreeing anchor fields,
        different record (note differs) — rejected, never tie-broken."""
        store = store_with(tmp_path, registration(ENT_A),
                           variable_registration(note="first"))
        with pytest.raises(ModelKernelError) as excinfo:
            store.append(variable_registration(note="second"))
        assert excinfo.value.error_code == "MODEL_DUPLICATE_REGISTRATION"

    def test_duplicate_divergent_anchor_fields_names_both_records(
            self, tmp_path):
        """Correction 8 case 3: divergent embedded fields — structural
        rejection surfacing BOTH conflicting record ids, path-free."""
        first = variable_registration(name="Hotend temperature")
        second = variable_registration(name="Renamed temperature")
        store = store_with(tmp_path, registration(ENT_A), first)
        with pytest.raises(ModelKernelError) as excinfo:
            store.append(second)
        assert excinfo.value.error_code == "MODEL_DUPLICATE_REGISTRATION"
        assert first.record_id in str(excinfo.value)
        assert second.record_id in str(excinfo.value)
        assert str(tmp_path) not in str(excinfo.value)

    def test_wrong_prefix_rejected(self, tmp_path):
        record = variable_registration()
        forged = record.model_copy(update={
            "record_id": "reg_" + record.record_id.split("_")[1]})
        store = store_with(tmp_path, registration(ENT_A))
        with pytest.raises(ModelKernelError) as excinfo:
            store.append(forged)
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"

    @pytest.mark.parametrize("bad_id", [
        pytest.param("vrg_" + "a" * 63, id="short_tail"),
        pytest.param("vrg_" + "A" * 64, id="uppercase_tail"),
        pytest.param("vrg" + "a" * 64, id="no_underscore"),
    ])
    def test_bad_id_shapes_rejected(self, tmp_path, bad_id):
        record = variable_registration()
        forged = record.model_copy(update={"record_id": bad_id})
        store = store_with(tmp_path, registration(ENT_A))
        with pytest.raises(ModelKernelError) as excinfo:
            store.append(forged)
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"

    def test_wrong_digest_rejected(self, tmp_path):
        record = variable_registration()
        forged = record.model_copy(update={"record_id": "vrg_" + "0" * 64})
        store = store_with(tmp_path, registration(ENT_A))
        with pytest.raises(ModelKernelError) as excinfo:
            store.append(forged)
        assert excinfo.value.error_code == "MODEL_RECORD_HASH_MISMATCH"

    def test_golden_vector_and_id_exclusion(self):
        """Canonical bytes pinned literally; the id is the sha256 of those
        bytes (record_id excluded from its own digest)."""
        record = variable_registration(role="hotend-temperature")
        expected = (
            '{"anchor":{"anchor_id":"var_11111111111111111111111111111111",'
            '"display_name":"Demo variable",'
            '"entity_anchor_id":"ent_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",'
            '"namespace":"demo-printer","role_name":"hotend-temperature"},'
            '"authority":{"agent":"mk001_demo_fixture","kind":"test_fixture",'
            '"method":"manual_declaration"},"note":"",'
            '"record_kind":"variable_registration",'
            '"recorded_at":"2026-08-08T12:00:00+00:00","schema_version":"1"}'
        ).encode("utf-8")
        assert canonical_bytes(record) == expected
        assert record.record_id == (
            "vrg_" + hashlib.sha256(expected).hexdigest())
        assert verify_record_id(record)

    def test_offset_normalization(self):
        from datetime import datetime, timedelta, timezone

        offset = timezone(timedelta(hours=2))
        shifted = build_record(
            VariableRegistration, anchor=variable_anchor(),
            recorded_at=T0.astimezone(offset), authority=AUTHORITY)
        assert shifted.record_id == variable_registration().record_id

    def test_schema_version_participates_in_digest(self):
        record = variable_registration()
        moved = corrupt(record, schema_version="2", rehash=False)
        assert canonical_bytes(moved) != canonical_bytes(record)

    def test_prefix_table_and_patterns_complete(self, tmp_path):
        """Every union member builds with its prefix; every prefix passes
        the shared id and filename gates."""
        import re
        import typing

        from backend.model_kernel.canonical import _PREFIX_BY_KIND
        from backend.model_kernel.contracts import (
            MODEL_RECORD_ID_PATTERN,
            ModelRecord,
        )
        from backend.model_kernel.store import _FILENAME

        members = typing.get_args(ModelRecord)
        assert VariableRegistration in members
        # 7 pre-CN-001 + crg/vcn (CN-001) = 9
        assert len(_PREFIX_BY_KIND) == len(members) == 9
        for prefix in _PREFIX_BY_KIND.values():
            sample = f"{prefix}_{'0' * 64}"
            assert re.fullmatch(MODEL_RECORD_ID_PATTERN, sample)
            assert _FILENAME.fullmatch(sample + ".json")

    def test_ib_canonicalizer_parity(self):
        from backend.identity_binding import canonical as ib_canonical

        record = variable_registration(role="hotend-temperature")
        assert ib_canonical.canonical_bytes(record) == canonical_bytes(record)
        assert ib_canonical.canonical_bytes(record.anchor) == canonical_bytes(
            record.anchor)

    def test_shape_is_closed(self):
        with pytest.raises(ModelKernelError):
            build_record(VariableRegistration, anchor=variable_anchor(),
                         recorded_at=T0, authority=AUTHORITY,
                         supersedes=None)
        with pytest.raises(ValidationError):
            VariableRegistration(record_id="vrg_" + "0" * 64,
                                 anchor=variable_anchor(), recorded_at=T0,
                                 authority=AUTHORITY, evidence=())
        with pytest.raises(ModelKernelError):
            # an ENTITY anchor payload has referent_kind and no owner
            build_record(VariableRegistration,
                         anchor=EntityAnchor(
                             anchor_id=ENT_A, namespace="demo-printer",
                             display_name="not a variable",
                             referent_kind="physical_instance"),
                         recorded_at=T0, authority=AUTHORITY)

    def test_collection_validator_separate_mapping(self):
        owner = registration(ENT_A)
        record = variable_registration()
        loaded = validate_record_collection(
            "demo-printer",
            {owner.record_id: owner, record.record_id: record})
        assert loaded.variable_registrations_by_anchor == {VAR_A: record}
        assert VAR_A not in loaded.registrations_by_anchor
        assert ENT_A not in loaded.variable_registrations_by_anchor
        with pytest.raises(TypeError):
            loaded.variable_registrations_by_anchor[VAR_A] = record

    def test_lone_surrogate_note_typed(self, tmp_path):
        hostile = json.loads('"note \\ud800 from untrusted json"')
        forged = corrupt(variable_registration(), note=hostile, rehash=False)
        store = store_with(tmp_path, registration(ENT_A))
        before = snapshot(store)
        with pytest.raises(ModelKernelError) as excinfo:
            store.append(forged)
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"
        assert snapshot(store) == before

    @pytest.mark.parametrize("forge", [
        pytest.param(lambda r: corrupt(r, note=123), id="copy_bad_note"),
        pytest.param(lambda r: corrupt(r, anchor={"anchor_id": VAR_A}),
                     id="copy_gutted_anchor"),
        pytest.param(
            lambda r: VariableRegistration.model_construct(
                **{**r.model_dump(), "note": 123}),
            id="construct_bad_note"),
    ])
    def test_forgery_matrix(self, tmp_path, forge):
        store = store_with(tmp_path, registration(ENT_A))
        before = snapshot(store)
        with pytest.raises(ModelKernelError) as excinfo:
            store.append(forge(variable_registration()))
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"
        assert snapshot(store) == before

    def test_loaded_model_backcompat_default(self):
        loaded = validate_record_collection("demo-printer", {})
        assert loaded.variable_registrations_by_anchor == {}
        result = ModelQueries(loaded).variable(VAR_A)
        assert result.status == "not_registered"


# ------------------------------------------------------------- B. revision


class TestRevisionAndReplay:
    def test_revision_changes_deterministically(self, tmp_path):
        owner = registration(ENT_A)
        record = variable_registration()
        store = store_with(tmp_path, owner)
        before = store.load().revision
        store.append(record)
        after = store.load().revision
        assert after.record_count == before.record_count + 1
        assert after.revision_id == compute_revision_id(
            "demo-printer", sorted([*before.record_ids, record.record_id]))
        twin = store_with(tmp_path / "twin", owner, record)
        assert twin.load().revision == after

    def test_load_is_file_order_independent(self, tmp_path):
        owner = registration(ENT_A)
        record = variable_registration()
        ordered = store_with(tmp_path / "one", owner, record)
        reversed_dir = ModelStore(tmp_path / "two" / "demo-printer")
        for source in (record, owner):  # written in reverse order
            name = f"{source.record_id}.json"
            (reversed_dir.records_dir / name).write_bytes(
                (ordered.records_dir / name).read_bytes())
        assert reversed_dir.load().revision == ordered.load().revision

    def test_tampered_variable_file_detected(self, tmp_path):
        record = variable_registration()
        store = store_with(tmp_path, registration(ENT_A), record)
        path = store.records_dir / f"{record.record_id}.json"
        payload = json.loads(path.read_text())
        payload["anchor"]["display_name"] = "tampered"
        path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
        with pytest.raises(ModelKernelError) as excinfo:
            store.load()
        assert excinfo.value.error_code == "MODEL_RECORD_HASH_MISMATCH"

    @pytest.mark.parametrize("name", [
        pytest.param("vrg_" + "a" * 63 + ".json", id="short"),
        pytest.param("vrg_x.json", id="junk_tail"),
        pytest.param("mrv_" + "a" * 64 + ".json", id="revision_prefix"),
    ])
    def test_stray_vrg_like_files_rejected(self, tmp_path, name):
        store = store_with(tmp_path, registration(ENT_A))
        (store.records_dir / name).write_text("{}")
        with pytest.raises(ModelKernelError) as excinfo:
            store.load()
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"


# -------------------------------------------------------------- C. queries


def world(tmp_path):
    return store_with(
        tmp_path, contains_type(), registration(ENT_A), registration(ENT_B),
        variable_registration(VAR_A, owner=ENT_A, name="Temperature"))


class TestKernelQueries:
    def test_variable_registered(self, tmp_path):
        loaded = world(tmp_path).load()
        result = ModelQueries(loaded).variable(VAR_A)
        assert result.status == "registered"
        assert result.registration.anchor == variable_anchor(
            VAR_A, owner=ENT_A, name="Temperature")
        assert result.registration.record_id.startswith("vrg_")
        assert result.revision == loaded.revision

    def test_variable_not_registered(self, tmp_path):
        loaded = world(tmp_path).load()
        result = ModelQueries(loaded).variable(VAR_B)
        assert result.status == "not_registered"
        assert result.registration is None
        assert result.revision == loaded.revision

    def test_variable_rejects_entity_ids_typed(self, tmp_path):
        queries = ModelQueries(world(tmp_path).load())
        with pytest.raises(ModelKernelError) as excinfo:
            queries.variable(ENT_A)
        assert excinfo.value.error_code == "MODEL_ANCHOR_ID_INVALID"
        assert "variable" in str(excinfo.value)

    def test_variables_of_three_distinct_outcomes(self, tmp_path):
        queries = ModelQueries(world(tmp_path).load())
        with_vars = queries.variables_of(ENT_A)
        assert (with_vars.status, len(with_vars.entries)) == ("registered", 1)
        zero_vars = queries.variables_of(ENT_B)
        assert (zero_vars.status, zero_vars.entries) == ("registered", ())
        absent = queries.variables_of(ENT_C)
        assert (absent.status, absent.entries) == ("not_registered", ())

    def test_variables_of_rejects_variable_ids_typed(self, tmp_path):
        queries = ModelQueries(world(tmp_path).load())
        with pytest.raises(ModelKernelError) as excinfo:
            queries.variables_of(VAR_A)
        assert excinfo.value.error_code == "MODEL_ANCHOR_ID_INVALID"

    def test_variables_of_deterministic_ordering(self, tmp_path):
        store = store_with(
            tmp_path, registration(ENT_A),
            variable_registration(VAR_C, name="Gamma"),
            variable_registration(VAR_A, name="Alpha"),
            variable_registration(VAR_B, name="Beta"))
        entries = ModelQueries(store.load()).variables_of(ENT_A).entries
        assert [e.anchor.anchor_id for e in entries] == [VAR_A, VAR_B, VAR_C]
        again = ModelQueries(store.load()).variables_of(ENT_A).entries
        assert again == entries

    def test_result_contract_invariants(self, tmp_path):
        loaded = world(tmp_path).load()
        summary = ModelQueries(loaded).variable(VAR_A).registration
        with pytest.raises(ValidationError):
            VariableResult(status="registered", anchor_id=VAR_A,
                           registration=None, revision=loaded.revision)
        with pytest.raises(ValidationError):
            VariableResult(status="not_registered", anchor_id=VAR_A,
                           registration=summary, revision=loaded.revision)
        with pytest.raises(ValidationError):
            EntityVariablesResult(status="not_registered",
                                  entity_anchor_id=ENT_A,
                                  entries=(summary,),
                                  revision=loaded.revision)

    def test_variables_never_in_hierarchy(self, tmp_path):
        store = world(tmp_path)
        store.append(assertion(contains_type(), source=ENT_A, target=ENT_B,
                               context=AS_BUILT))
        queries = ModelQueries(store.load())
        children = queries.children(ENT_A, "contains", view="as_built")
        assert all(not entry.anchor.anchor_id.startswith("var_")
                   for entry in children.entries)
        parents = queries.parents(ENT_B, "contains", view="as_built")
        assert not parents.parent.anchor_id.startswith("var_")
        ancestors = queries.ancestors(ENT_B, "contains", view="as_built")
        assert all(not step.anchor.anchor_id.startswith("var_")
                   for step in ancestors.steps)
        descendants = queries.descendants(ENT_A, "contains", view="as_built")
        assert all(not step.anchor.anchor_id.startswith("var_")
                   for step in descendants.steps)
        health = queries.hierarchy_health("contains", view="as_built")
        bare = ModelQueries(store_with(
            tmp_path / "bare", contains_type(), registration(ENT_A),
            registration(ENT_B),
            assertion(contains_type(), source=ENT_A, target=ENT_B,
                      context=AS_BUILT)).load())
        assert health.cycles == bare.hierarchy_health(
            "contains", view="as_built").cycles

    @pytest.mark.parametrize("hostile", [
        pytest.param(None, id="none"), pytest.param(123, id="int"),
        pytest.param([], id="unhashable"), pytest.param("", id="empty"),
        pytest.param("var_" + "g" * 32, id="nonhex"),
    ])
    def test_leakage_sweep_extension(self, tmp_path, hostile):
        queries = ModelQueries(world(tmp_path).load())
        for call in (lambda: queries.variable(hostile),
                     lambda: queries.variables_of(hostile)):
            with pytest.raises(ModelKernelError):
                call()

    def test_public_surface_name_count(self):
        # 62 (pre-CN-001) + 4 CN-001 value contracts (CanonicalDecimal,
        # ScalarComparisonOperator, ScalarComparisonPredicate,
        # ConstraintPredicate) + 2 CN-001 records (ConstraintRegistration,
        # VariableConstraintDeclaration) = 68
        import backend.model_kernel as kernel

        assert len(kernel.__all__) == 68
        for name in ("VariableRegistration", "VariableRegistrationSummary",
                     "VariableResult", "EntityVariablesResult",
                     "StructuralSourceLocatorEvidence"):
            assert name in kernel.__all__


class TestVariableAsEvidence:
    def test_relationship_may_cite_variable_membership(self, tmp_path):
        record = variable_registration()
        cited = (ModelRecordEvidence(kind="model_record",
                                     record_id=record.record_id),)
        store = store_with(
            tmp_path, contains_type(), registration(ENT_A),
            registration(ENT_B), record,
            assertion(contains_type(), source=ENT_A, target=ENT_B,
                      context=AS_BUILT, evidence=cited))
        assert store.load().revision.record_count == 5

    def test_cited_variable_must_be_in_revision(self, tmp_path):
        record = variable_registration()
        cited = (ModelRecordEvidence(kind="model_record",
                                     record_id=record.record_id),)
        store = store_with(tmp_path, contains_type(), registration(ENT_A),
                           registration(ENT_B))
        with pytest.raises(ModelKernelError) as excinfo:
            store.append(assertion(contains_type(), source=ENT_A,
                                   target=ENT_B, context=AS_BUILT,
                                   evidence=cited))
        assert excinfo.value.error_code == "MODEL_REFERENCE_INVALID"

    def test_withdrawals_stay_uncitable(self):
        with pytest.raises(ValidationError):
            ModelRecordEvidence(kind="model_record",
                                record_id="rwd_" + "0" * 64)
