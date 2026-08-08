"""MK-001 store: validating append, staging atomicity, replay, loaded-model
immutability, and path-leakage-safe errors."""

import json

import pytest

from backend.model_kernel.contracts import (
    ModelConfigurationError,
    ModelIntegrityError,
)
from backend.model_kernel.store import ModelStore

from tests.model_kernel.builders import (
    AS_BUILT,
    ENT_A,
    ENT_B,
    ENT_C,
    VIEW_FREE,
    assertion,
    contains_type,
    containment_world,
    registration,
    store_with,
)

MAPPING_FIELDS = (
    "records", "registrations_by_anchor", "types", "current_type_by_name",
    "type_name_by_id", "assertions", "withdrawals", "superseded_by",
    "withdrawn_by",
)


class TestValidatingAppend:
    def test_identical_reappend_is_validated_noop(self, tmp_path):
        store = ModelStore(tmp_path / "demo-printer")
        record = registration()
        store.append(record)
        store.append(record)
        assert [p.name for p in store.records_dir.iterdir()] == [
            f"{record.record_id}.json"]

    def test_noop_refused_when_another_member_is_corrupted(self, tmp_path):
        """Amendment-4 case: the complete current set is validated before
        EVERY append result — an identical re-append must fail, and write
        nothing, when a different stored member is tampered."""
        store = containment_world(tmp_path)
        target = sorted(store.records_dir.iterdir())[1]
        data = json.loads(target.read_text())
        data["note"] = "tampered"
        target.write_text(json.dumps(data))
        untouched = sorted(store.records_dir.iterdir())[0]
        reappend = json.loads(untouched.read_text())
        before = sorted(p.name for p in store.records_dir.iterdir())
        # re-append the untouched member's record
        from pydantic import TypeAdapter

        from backend.model_kernel.contracts import ModelRecord

        record = TypeAdapter(ModelRecord).validate_python(reappend)
        with pytest.raises(ModelIntegrityError) as excinfo:
            store.append(record)
        assert excinfo.value.error_code == "MODEL_RECORD_HASH_MISMATCH"
        assert sorted(p.name for p in store.records_dir.iterdir()) == before

    def test_tampered_existing_target_detected_not_overwritten(self, tmp_path):
        store = ModelStore(tmp_path / "demo-printer")
        record = registration()
        store.append(record)
        path = store.records_dir / f"{record.record_id}.json"
        data = json.loads(path.read_text())
        data["note"] = "tampered in place"
        path.write_text(json.dumps(data))
        with pytest.raises(ModelIntegrityError):
            store.append(record)
        assert json.loads(path.read_text())["note"] == "tampered in place"

    @pytest.mark.parametrize("bad_records,code", [
        # dangling relationship (type + endpoints exist, target missing)
        (lambda k: [assertion(k, target=ENT_C)], "MODEL_REFERENCE_INVALID"),
        # duplicate registration
        (lambda k: [registration(ENT_A, note="again")],
         "MODEL_DUPLICATE_REGISTRATION"),
        # incompatible endpoint kind
        (lambda k: [registration(ENT_C, kind="type_definition"),
                    assertion(k, source=ENT_C)], "MODEL_ENDPOINT_KIND_INVALID"),
        # context mismatch
        (lambda k: [assertion(k, context=VIEW_FREE)], "MODEL_CONTEXT_INVALID"),
        # duplicate current type name
        (lambda k: [contains_type(note="duplicate")],
         "MODEL_DUPLICATE_TYPE_NAME"),
    ])
    def test_prospective_validation_rejects_and_writes_nothing(
        self, tmp_path, bad_records, code
    ):
        kind = contains_type()
        store = store_with(tmp_path, kind, registration(ENT_A),
                           registration(ENT_B))
        records = bad_records(kind)
        for record in records[:-1]:
            store.append(record)  # legitimate setup members
        before_files = {p.name: p.read_bytes()
                        for p in store.records_dir.iterdir()}
        before_revision = store.load().revision
        with pytest.raises(ModelIntegrityError) as excinfo:
            store.append(records[-1])
        assert excinfo.value.error_code == code
        after_files = {p.name: p.read_bytes()
                       for p in store.records_dir.iterdir()}
        assert after_files == before_files  # prior revision byte-identical
        assert store.load().revision == before_revision
        assert list(store.staging_dir.glob("*")) == []  # staging cleaned

    def test_staging_outside_scanned_dir_and_residue_harmless(self, tmp_path):
        store = containment_world(tmp_path)
        assert store.staging_dir != store.records_dir
        assert store.records_dir not in store.staging_dir.parents
        store.staging_dir.mkdir(exist_ok=True)
        (store.staging_dir / "crashed.tmp").write_text("partial")
        assert store.load().revision.record_count == 3

    def test_failed_promotion_typed_clean_and_path_free(self, tmp_path,
                                                        monkeypatch):
        """Environment failures surface through the typed error contract
        with no absolute path in the message, and leave the ledger holding
        only complete final records."""
        import backend.model_kernel.store as store_module

        store = containment_world(tmp_path)

        def broken_replace(src, dst):
            raise OSError(f"promotion failed for {dst}")

        monkeypatch.setattr(store_module.os, "replace", broken_replace)
        with pytest.raises(ModelIntegrityError) as excinfo:
            store.append(registration(ENT_C))
        monkeypatch.undo()
        assert excinfo.value.error_code == "MODEL_STORAGE_FAILURE"
        assert str(tmp_path) not in str(excinfo.value)
        assert all(p.suffix == ".json" for p in store.records_dir.iterdir())
        assert list(store.staging_dir.glob("*")) == []
        assert store.load().revision.record_count == 3

    def test_model_id_pattern_enforced(self, tmp_path):
        with pytest.raises(ModelConfigurationError):
            ModelStore(tmp_path / "Demo Printer!")


class TestReplay:
    def test_earlier_membership_replays_after_later_appends(self, tmp_path):
        store = containment_world(tmp_path)
        earlier = store.load().revision
        store.append(registration(ENT_C))
        assert store.load().revision.record_count == 4
        replayed = store.replay(earlier.record_ids)
        assert replayed.revision == earlier

    def test_members_pattern_checked_before_paths(self, tmp_path):
        store = containment_world(tmp_path)
        (tmp_path / "outside.json").write_text("{}")
        for bad in ("../../outside", "not-a-record-id", "mrv_" + "0" * 64):
            with pytest.raises(ModelIntegrityError) as excinfo:
                store.replay((bad,))
            assert excinfo.value.error_code == "MODEL_REVISION_INVALID"

    def test_duplicates_and_missing_members_rejected(self, tmp_path):
        store = containment_world(tmp_path)
        member = store.load().revision.record_ids[0]
        with pytest.raises(ModelIntegrityError):
            store.replay((member, member))
        with pytest.raises(ModelIntegrityError):
            store.replay(("reg_" + "9" * 64,))

    def test_subset_must_be_reference_closed(self, tmp_path):
        kind = contains_type()
        reg_a, reg_b = registration(ENT_A), registration(ENT_B)
        edge = assertion(kind)
        store = store_with(tmp_path, kind, reg_a, reg_b, edge)
        with pytest.raises(ModelIntegrityError):
            store.replay((edge.record_id, reg_a.record_id, reg_b.record_id))

    def test_currentness_is_membership_relative(self, tmp_path):
        original = contains_type()
        corrected = contains_type(forward_label="physically contains",
                                  supersedes=original.record_id)
        store = store_with(tmp_path, original, corrected)
        full = store.load()
        assert full.current_type_by_name["contains"] == corrected.record_id
        replayed = store.replay((original.record_id,))
        assert replayed.current_type_by_name["contains"] == original.record_id


class TestLoadedModelImmutability:
    def test_every_exposed_mapping_rejects_mutation(self, tmp_path):
        loaded = containment_world(tmp_path).load()
        for name in MAPPING_FIELDS:
            mapping = getattr(loaded, name)
            with pytest.raises((TypeError, AttributeError)):
                mapping["forged"] = None
            with pytest.raises((TypeError, AttributeError)):
                mapping.clear()

    def test_no_mutable_container_fields_on_any_contract(self):
        """pydantic frozen blocks attribute assignment only — list/set/dict
        typed fields would stay mutable in place; none may exist."""
        import typing

        import backend.model_kernel.contracts as contracts
        from pydantic import BaseModel

        for name in dir(contracts):
            model = getattr(contracts, name)
            if (isinstance(model, type) and issubclass(model, BaseModel)
                    and model is not BaseModel):
                for field_name, field in model.model_fields.items():
                    rendered = str(field.annotation)
                    for banned in ("list[", "set[", "dict[", "List[",
                                   "Set[", "Dict["):
                        assert banned not in rendered, (
                            f"{name}.{field_name}: mutable container")

    def test_insertion_order_independence(self, tmp_path):
        kind = contains_type()
        records = [kind, registration(ENT_A), registration(ENT_B),
                   assertion(kind)]
        orders = [records, records[::-1],
                  [records[1], records[0], records[2], records[3]]]
        loaded_models = []
        for index, order in enumerate(orders):
            store = ModelStore(tmp_path / f"world-{index}" / "demo-printer")
            for record in sorted(
                order, key=lambda r: 0 if r.record_kind in (
                    "entity_registration",
                    "relationship_type_definition") else 1):
                store.append(record)
            loaded_models.append(store.load())
        first, second, third = loaded_models
        assert first.revision == second.revision == third.revision
        # derived state, not just the (order-free by construction) revision
        assert (dict(first.records).keys() == dict(second.records).keys()
                == dict(third.records).keys())
        assert (dict(first.current_type_by_name)
                == dict(second.current_type_by_name)
                == dict(third.current_type_by_name))
        from backend.model_kernel.queries import ModelQueries

        answers = [ModelQueries(m).parents(ENT_B, "contains", view="as_built")
                   for m in loaded_models]
        assert answers[0] == answers[1] == answers[2]


class TestPathLeakage:
    def test_error_messages_never_contain_absolute_paths(self, tmp_path):
        """Amendment 5: errors expose model ids, record ids, file names, and
        stable codes — never the tmp dir, store root, or other locations."""
        errors = []
        with pytest.raises(ModelConfigurationError) as e1:
            ModelStore(tmp_path / "Bad Name")
        errors.append(e1.value)

        store = containment_world(tmp_path)
        (store.records_dir / "junk.txt").write_text("x")
        with pytest.raises(ModelIntegrityError) as e2:
            store.load()
        errors.append(e2.value)
        (store.records_dir / "junk.txt").unlink()

        target = sorted(store.records_dir.iterdir())[0]
        data = json.loads(target.read_text())
        data["note"] = "tampered"
        target.write_text(json.dumps(data))
        with pytest.raises(ModelIntegrityError) as e3:
            store.load()
        errors.append(e3.value)

        with pytest.raises(ModelIntegrityError) as e4:
            store.replay(("../escape",))
        errors.append(e4.value)

        for error in errors:
            message = str(error)
            assert str(tmp_path) not in message
            assert "/tmp/" not in message and "/mnt/" not in message
            assert "C:\\" not in message
