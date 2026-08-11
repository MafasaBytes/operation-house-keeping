"""IB-001 end-to-end validation slice over the committed demo-printer
binding set: bound resolution inside the declared hour, the complete
provenance chain to raw checksums, honest non-binding/conflict/correction
behavior, and byte-for-byte immutability of both upstream stores."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from backend.identity_binding.canonical import build_record
from backend.identity_binding.contracts import (
    AnchorDeclaration,
    AppliesScope,
    AuthorityRef,
    BindingAssertion,
    DeclaredBoundary,
)
from backend.identity_binding.facade import BoundTemporalQueries
from backend.identity_binding.resolver import BindingResolver
from backend.identity_binding.store import BindingStore
from backend.system_identity import EntityAnchor, VariableAnchor
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef
from backend.temporal_state.projector import TemporalProjector
from backend.temporal_state.queries import TemporalQueries
from backend.temporal_state.store import TemporalStore

from tests.data_sources.test_ingestion_runner_api import happy_script, make_runner

DEMO_SET = Path("bindings/demo-printer")
ENT = "ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50"
VAR = "var_b7e2d3c4f5a6172839405a6b7c8d9e0f"
E2 = "ent_" + "9" * 32
V2 = "var_" + "8" * 32
AS_OF = datetime(2026, 8, 7, 23, 0, 0, tzinfo=UTC)
IN_HOUR = datetime(2026, 8, 7, 20, 30, 0, tzinfo=UTC)
PAST_HOUR = datetime(2026, 8, 7, 21, 30, 0, tzinfo=UTC)
AUTHORITY = AuthorityRef(kind="test_fixture", agent="ib001_demo_fixture",
                         method="manual_declaration")
SUBJECT = SourceSubjectRef(source_id="printer-1", adapter_id="moonraker",
                           subject_identifier="extruder")
PROP = SourcePropertyRef(extraction_route="api:moonraker:v1",
                         item_key="printer_objects",
                         json_pointer="/result/status/extruder/temperature")


def temporal_stack(tmp_path):
    runner, ds_store, _ = make_runner(tmp_path / "ds", happy_script())
    temporal = TemporalStore(tmp_path / "temporal.db",
                             evidence_root=ds_store.base_dir)
    TemporalProjector(ds_store, temporal)  # constructed lazily below
    return runner, ds_store, temporal


def sweep(*roots: Path) -> dict[str, str]:
    """Every file, except SQLite -wal/-shm sidecars: ADR-0005 explicitly
    excludes WAL/SHM bytes from the temporal determinism claim (SQLite
    checkpoints and deletes them when the last connection closes); the
    main temporal.db and every evidence file are compared strictly."""
    hashes = {}
    for root in roots:
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            if path.name.endswith(("-wal", "-shm")):
                continue
            hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def demo_facade(queries):
    return BoundTemporalQueries(
        BindingResolver(BindingStore(DEMO_SET).load()), queries)


# IB-001's original four-record revision, pinned by explicit membership
# and replayed via load_revision (RP4). Never a prefix filter.
ORIGINAL_FOUR = (
    "anc_81d43569d1b093c1b52247bdfb8039ae6e4777eecd3918c498a85655fec9bbdc",
    "anc_e7bd0b35b97ee920384ac5791c90e3ae34889b642b54608cf3293a5174cb5ae3",
    "iba_b1b86a4fd0c56f36aafb4574176429c0edab530dbbd5d1da954a54f2533fd90c",
    "iba_ba80b9e561b564a465b19109e2576d79d93b10e5b87e9917bf7ed45558c3a90a",
)
ORIGINAL_REVISION = ("rev_8605f52c345eeabf08bfde235090f1ad1c6cf39f45e617c"
                     "7dd0070535a7fa754")
# SN-001's two structural mappings (commit 15 append)
SN001_RECORDS = (
    "iba_2061f4017a7f2355a36d30ee69a6ebc24a94de2e1db8866b4216916678b4d5aa",
    "iba_22a8eef16595ec5d38f9135b04499c76f358055a6e5ea4dba9c62f7d9b9d3a43",
)
# AU1: exhaustive per-record authority map — an unlisted record FAILS,
# so this is strictly STRONGER than the old blanket assertion.
EXPECTED_AGENT_BY_RECORD = {
    **{record_id: "ib001_demo_fixture" for record_id in ORIGINAL_FOUR},
    **{record_id: "sn001_showcase_fixture" for record_id in SN001_RECORDS},
}


class TestCommittedSet:
    def test_loads_valid_with_expected_membership(self):
        loaded = BindingStore(DEMO_SET).load()
        assert loaded.revision.record_count == 6
        assert loaded.revision.binding_set_id == "demo-printer"
        assert set(loaded.anchors_by_id) == {ENT, VAR}
        assert set(loaded.revision.record_ids) == \
            set(ORIGINAL_FOUR) | set(SN001_RECORDS)

    def test_fixture_authority_never_human_owner(self):
        """Mandatory regression, per-record form (AU1): fixture authority
        is test_fixture, never human_owner; the original four records stay
        attributed to ib001_demo_fixture and the SN-001 mappings to
        sn001_showcase_fixture. Every record id must appear in exactly one
        expectation group — an unlisted record fails."""
        paths = sorted((DEMO_SET / "records").glob("*.json"))
        assert len(paths) == len(EXPECTED_AGENT_BY_RECORD)
        for path in paths:
            record = json.loads(path.read_text())
            assert record["authority"]["kind"] == "test_fixture", path.name
            assert record["record_id"] in EXPECTED_AGENT_BY_RECORD, path.name
            assert record["authority"]["agent"] == \
                EXPECTED_AGENT_BY_RECORD[record["record_id"]], path.name

    def test_rp4_original_revision_replays_and_still_binds(self):
        """RP4 (D5): the original four-record revision stays provable by
        explicit-membership replay, and the Moonraker subject still
        resolves bound inside it."""
        loaded = BindingStore(DEMO_SET).load_revision(ORIGINAL_FOUR)
        assert loaded.revision.revision_id == ORIGINAL_REVISION
        assert loaded.revision.record_count == 4
        result = BindingResolver(loaded).resolve_subject(SUBJECT,
                                                         at=IN_HOUR)
        assert result.status == "bound"
        assert result.resolved_target.anchor_id == ENT

    def test_rp5_model_set_original_revision_replays(self):
        original_three = (
            "anc_037d327111553c3410f162dbb8ffccf475fd0b1a15b4134e30"
            "4d6ade99141c21",
            "anc_69ebd49c67eb6b5ab775dbf0866efbbdfeaf625005bc50d2848"
            "d98a044014a22",
            "anc_c6aa3f3f3e03cc689a40ecd5d70d04828cbd1143bb107e85c2d"
            "d55268c2312d8",
        )
        loaded = BindingStore(Path("bindings/demo-printer-model")
                              ).load_revision(original_three)
        assert loaded.revision.revision_id == (
            "rev_b4878a692ed628e60c6e70fe321add50bda52fb15eca216f3c9c8"
            "a6e1c7b1a6f")
        assert loaded.revision.record_count == 3

    def test_no_secrets_or_absolute_paths_committed(self):
        for path in (DEMO_SET / "records").glob("*.json"):
            text = path.read_text()
            for needle in ("/home/", "/mnt/", "C:\\", "password", "secret",
                           "Bearer", "api_key"):
                assert needle not in text, f"{needle!r} in {path.name}"


class TestEndToEndChain:
    def test_bound_resolution_and_complete_provenance_chain(self, tmp_path):
        runner, ds_store, temporal = temporal_stack(tmp_path)
        runner.run("printer-1")
        TemporalProjector(ds_store, temporal).project("printer-1")
        queries = TemporalQueries(temporal)

        result = demo_facade(queries).latest_observed(SUBJECT, PROP, AS_OF)
        # bound inside the declared hour, on declared evidence only
        assert result.resolution.status == "bound"
        assert result.resolution.resolved_target.anchor_id == VAR
        assert result.resolution.applicability_basis == "declared_interval"
        received = result.observed.occurrence.received_at
        assert (datetime(2026, 8, 7, 20, 0, 0, tzinfo=UTC) <= received
                < datetime(2026, 8, 7, 21, 0, 0, tzinfo=UTC))

        # canonical anchor ← assertion + revision
        variable = result.resolution.resolved_target
        entity = BindingStore(DEMO_SET).load().anchors_by_id[
            variable.entity_anchor_id]
        assert entity.anchor_id == ENT
        citing = [s for s in result.resolution.via_assertions
                  if s.membership_at == "in"]
        assert citing and citing[0].record_id.startswith("iba_")
        assert result.resolution.revision.record_count == 6

        # ← SourceSubjectRef + SourcePropertyRef ← TemporalOccurrence
        occurrence = result.observed.occurrence
        assert occurrence.subject == SUBJECT and occurrence.property == PROP

        # ← attempt ← extraction ← raw record and checksum
        chain = queries.provenance(occurrence.occurrence_id)
        assert chain.attempt_id == occurrence.attempt_id
        envelope = ds_store.get_envelope(chain.raw_record_id)
        assert envelope.payload_checksum == chain.payload_checksum
        payload = ds_store.get_payload(envelope.immutable_payload_reference)
        digest = "sha256:" + hashlib.sha256(payload).hexdigest()
        assert digest == chain.payload_checksum  # bytes verify end-to-end

    def test_outside_declared_hour_is_outside_applicability(self):
        """Mandatory regression: fixture results outside the declared hour
        are outside_applicability."""
        resolver = BindingResolver(BindingStore(DEMO_SET).load())
        assert resolver.resolve_property(
            SUBJECT, PROP, at=PAST_HOUR).status == "outside_applicability"
        assert resolver.resolve_subject(
            SUBJECT, at=PAST_HOUR).status == "outside_applicability"

    def test_same_word_elsewhere_stays_unbound(self):
        resolver = BindingResolver(BindingStore(DEMO_SET).load())
        other_adapter = SourceSubjectRef(
            source_id="printer-1", adapter_id="other_adapter",
            subject_identifier="extruder")
        other_source = SourceSubjectRef(
            source_id="bench-2", adapter_id="moonraker",
            subject_identifier="extruder")
        assert resolver.resolve_subject(other_adapter, at=IN_HOUR).status == (
            "unbound")
        assert resolver.resolve_subject(other_source, at=IN_HOUR).status == (
            "unbound")
        other_route = SourcePropertyRef(
            extraction_route="api:moonraker:v2", item_key="printer_objects",
            json_pointer="/result/status/extruder/temperature")
        # a changed route leaves the SUBJECT bound and the new property
        # locator unbound — never silently inherited
        assert resolver.resolve_subject(SUBJECT, at=IN_HOUR).status == "bound"
        assert resolver.resolve_property(
            SUBJECT, other_route, at=IN_HOUR).status == "unbound"


class TestConflictAndCorrection:
    def _copy_demo(self, tmp_path) -> BindingStore:
        store = BindingStore(tmp_path / "demo-printer")
        for path in (DEMO_SET / "records").glob("*.json"):
            (store.records_dir / path.name).write_text(path.read_text())
        return store

    def _second_anchor_records(self, variable_owner=E2):
        return [
            build_record(AnchorDeclaration, anchor_kind="entity",
                         anchor=EntityAnchor(anchor_id=E2,
                                             namespace="demo-printer",
                                             display_name="Second unit",
                                             referent_kind="physical_instance"),
                         recorded_at=AS_OF, authority=AUTHORITY),
            build_record(AnchorDeclaration, anchor_kind="variable",
                         anchor=VariableAnchor(anchor_id=V2,
                                               entity_anchor_id=variable_owner,
                                               namespace="demo-printer",
                                               display_name="Other temp"),
                         recorded_at=AS_OF, authority=AUTHORITY),
        ]

    def _hour_scope(self):
        return AppliesScope(
            axis="ingestion_received_at",
            start_boundary=DeclaredBoundary(
                kind="declared", at=datetime(2026, 8, 7, 20, 0, 0, tzinfo=UTC)),
            end_boundary=DeclaredBoundary(
                kind="declared", at=datetime(2026, 8, 7, 21, 0, 0, tzinfo=UTC)),
            interval_semantics="half_open")

    def test_conflict_is_surfaced_never_guessed(self, tmp_path):
        store = self._copy_demo(tmp_path)
        for record in self._second_anchor_records():
            store.append(record)
        store.append(build_record(
            BindingAssertion, binding_kind="property", subject=SUBJECT,
            property=PROP, target_anchor_id=V2, applies=self._hour_scope(),
            recorded_at=AS_OF, authority=AUTHORITY, note="competing"))
        result = BindingResolver(store.load()).resolve_property(
            SUBJECT, PROP, at=IN_HOUR)
        assert result.status == "conflicted"
        assert result.resolved_target is None
        assert {a.anchor_id for a in result.candidate_targets} == {VAR, V2}

    def test_correction_preserves_the_prior_assertion(self, tmp_path):
        store = self._copy_demo(tmp_path)
        loaded = store.load()
        original_id = next(
            record_id for record_id, a in loaded.assertions.items()
            if a.binding_kind == "property")
        # the corrected variable still belongs to the SAME demo entity —
        # a correction fixes the variable, not the subject's entity
        for record in self._second_anchor_records(variable_owner=ENT):
            store.append(record)
        successor = build_record(
            BindingAssertion, binding_kind="property", subject=SUBJECT,
            property=PROP, target_anchor_id=V2, applies=self._hour_scope(),
            recorded_at=AS_OF, authority=AUTHORITY, supersedes=original_id,
            note="correction: the original decision was wrong")
        store.append(successor)
        result = BindingResolver(store.load()).resolve_property(
            SUBJECT, PROP, at=IN_HOUR)
        assert result.status == "bound"
        assert result.resolved_target.anchor_id == V2
        by_id = {s.record_id: s for s in result.via_assertions}
        prior = by_id[original_id]  # still present, fully explained
        assert prior.superseded_by == (successor.record_id,)
        assert prior.active is False
        assert (store.records_dir / f"{original_id}.json").exists()


class TestUpstreamImmutability:
    def test_evidence_and_temporal_stores_unchanged_byte_for_byte(
        self, tmp_path
    ):
        """Mandatory regression: all IB-001 operations leave both upstream
        stores byte-for-byte identical — same files, same hashes."""
        runner, ds_store, temporal = temporal_stack(tmp_path)
        runner.run("printer-1")
        TemporalProjector(ds_store, temporal).project("printer-1")
        queries = TemporalQueries(temporal)
        before = sweep(ds_store.base_dir, tmp_path)
        logical_before = temporal.ordered_logical_dump()

        facade = demo_facade(queries)
        facade.latest_observed(SUBJECT, PROP, AS_OF)
        facade.history(SUBJECT, PROP)
        resolver = BindingResolver(BindingStore(DEMO_SET).load())
        resolver.resolve_subject(SUBJECT, at=IN_HOUR)
        resolver.resolve_property(SUBJECT, PROP, at=PAST_HOUR)

        assert sweep(ds_store.base_dir, tmp_path) == before
        assert temporal.ordered_logical_dump() == logical_before
