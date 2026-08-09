"""MK-001 committed demo model: golden revision, honest authority, the
root → subsystem → extruder chain, the non-hierarchical instance_of edge,
and committed-record hygiene."""

import json
from pathlib import Path

from backend.model_kernel.queries import ModelQueries
from backend.model_kernel.store import ModelStore

DEMO_MODEL = Path("models/demo-printer")
GOLDEN_REVISION = ("mrv_25afc0ebf17ed12bd6ef0a95795798a53ef2"
                   "731983410136d3da15c4d0f98093")  # 11 records (VS-001)
PRE_SPECIFICATION_REVISION = ("mrv_105658072294bad92f83e3d536863cb46d6d7ae83"
                              "f271fb59d5026839d002686")  # 10 records (VM-001)
PRE_VARIABLE_REVISION = ("mrv_c28b6301f712f94249e6ccea87f1cfd4f9c04c1cc00fef3"
                         "ae3d023e3da83227f")  # 9 records (MK-001)
ROOT = "ent_0f1e2d3c4b5a69788796a5b4c3d2e1f0"
SUBSYSTEM = "ent_1a2b3c4d5e6f708192a3b4c5d6e7f809"
EXTRUDER = "ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50"
UNIT_TYPE = "ent_2b3c4d5e6f70819a2b3c4d5e6f708192"


def demo_queries():
    return ModelQueries(ModelStore(DEMO_MODEL).load())


class TestCommittedLedger:
    def test_golden_revision_and_membership(self):
        loaded = ModelStore(DEMO_MODEL).load()
        assert loaded.revision.revision_id == GOLDEN_REVISION
        assert loaded.revision.record_count == 11
        assert len(loaded.variable_registrations_by_anchor) == 1
        assert len(loaded.specifications) == 1
        assert len(loaded.types) == 2
        assert len(loaded.assertions) == 3
        assert len(loaded.registrations_by_anchor) == 4

    def test_fixture_authority_never_human_owner(self):
        for path in (DEMO_MODEL / "records").glob("*.json"):
            record = json.loads(path.read_text())
            assert record["authority"]["kind"] == "test_fixture", path.name
            assert record["authority"]["agent"] == "mk001_demo_fixture"
        for path in Path("bindings/demo-printer-model/records").glob("*.json"):
            record = json.loads(path.read_text())
            assert record["authority"]["kind"] == "test_fixture", path.name

    def test_no_secrets_or_absolute_paths_committed(self):
        roots = (DEMO_MODEL / "records",
                 Path("bindings/demo-printer-model/records"))
        for root in roots:
            for path in root.glob("*.json"):
                text = path.read_text()
                for needle in ("/home/", "/mnt/", "C:\\", "password",
                               "secret", "Bearer", "api_key"):
                    assert needle not in text, f"{needle!r} in {path.name}"


class TestDemoQueries:
    def test_hierarchy_chain_root_subsystem_extruder(self):
        queries = demo_queries()
        parents = queries.parents(EXTRUDER, "contains", view="as_built")
        assert parents.status == "resolved"
        assert parents.parent.anchor_id == SUBSYSTEM
        ancestors = queries.ancestors(EXTRUDER, "contains", view="as_built")
        assert ancestors.status == "complete"
        assert [s.anchor.anchor_id for s in ancestors.steps] == [SUBSYSTEM,
                                                                 ROOT]
        assert queries.parents(ROOT, "contains", view="as_built").status == (
            "no_declared_parent")
        descendants = queries.descendants(ROOT, "contains", view="as_built")
        assert [s.anchor.anchor_id for s in descendants.steps] == [SUBSYSTEM,
                                                                   EXTRUDER]
        health = queries.hierarchy_health("contains", view="as_built")
        assert health.cycles == () and health.parent_conflicts == ()
        assert health.stale_type_assertions == ()

    def test_non_hierarchical_instance_of_edge(self):
        from backend.model_kernel.contracts import ViewIndependentContext

        queries = demo_queries()
        context = ViewIndependentContext(kind="view_independent")
        outgoing = queries.relationships(EXTRUDER, direction="outgoing",
                                         type_name="instance_of",
                                         context=context)
        assert len(outgoing.active) == 1
        summary = outgoing.active[0]
        assert summary.target_anchor_id == UNIT_TYPE
        assert summary.forward_label == "is an instance of"
        # the type lattice never bleeds into containment ancestry
        ancestors = queries.ancestors(EXTRUDER, "contains", view="as_built")
        assert UNIT_TYPE not in [s.anchor.anchor_id for s in ancestors.steps]

    def test_provenance_chain_to_identity_declaration(self):
        """Every edge explains itself; the extruder edges carry a declared
        reference to the extruder's committed AnchorDeclaration."""
        queries = demo_queries()
        parents = queries.parents(EXTRUDER, "contains", view="as_built")
        evidence = parents.supporting[0].evidence
        kinds = {d.ref.kind: d for d in evidence}
        assert kinds["owner_declaration"].verification == "declared_reference"
        binding_ref = kinds["identity_binding_record"]
        assert binding_ref.verification == "declared_reference"
        assert binding_ref.ref.binding_set_id == "demo-printer"
        assert binding_ref.ref.record_id.startswith("anc_e7bd0b35")

    def test_replay_of_committed_membership_is_identical(self):
        store = ModelStore(DEMO_MODEL)
        loaded = store.load()
        replayed = store.replay(loaded.revision.record_ids)
        assert replayed.revision == loaded.revision
        assert ModelQueries(replayed).parents(
            EXTRUDER, "contains", view="as_built").parent.anchor_id == (
            SUBSYSTEM)


# ------------------------------------------------------- VM-001 fixtures
OLD_GOLDEN_REVISION = PRE_VARIABLE_REVISION
HOTEND_VARIABLE = "var_b7e2d3c4f5a6172839405a6b7c8d9e0f"

# byte-freeze: the nine MK-001 records are immutable forever; VM-001 adds
# exactly one vrg_ file and changes nothing else
FROZEN_MK001_RECORDS = {
    "reg_5776a541a04b428f35af40203294a34a8a9978f0bdf3572a8745e6febddd5941.json":
    "9849b3b20817dd4c62de211a315b5439c8ab440184d1b0c24a10087afec14e70",
    "reg_9b5491aaa131b0df070cee792c83e002bdc4232cbbaba443f967cd3e5b780451.json":
    "07e34aa1a5c54d28e367854a9dbbb52cd3313652d4e8b205ce855e3361d91def",
    "reg_a502243be0cb229ab386f20db6803e01329dcdd5a22f8e922f1a92555a7ba0ba.json":
    "0d71377da4e7254c701fd3f2ce4e709d3f53d78ff2b00387680114eb64173be2",
    "reg_c7ad4c326425439d5e2bff4d0a3dc42cf26540514ecc015d060c711943ff92c5.json":
    "91fb6c8d8e58c278d82c7f43df506457b09bf872884e76014cc0d7af286e9c8d",
    "rel_12a2812d151da28579784518b619a2a577318a977911bcaf27093d9263d044fa.json":
    "cf94d69aaa501823fcbf21be1b541f62e675faf92b79c5d01afa002b026aa82e",
    "rel_3c5a723282c6fc05cd694e5a98e208840e1d897f80dc29a524c0b8d35ff34d5a.json":
    "6260c83eced9d32436756772966604ca1e522f574ccec32e7a5189d25776aac1",
    "rel_a1fef969809045884d29a981df43bce332b9a8871bd2236cd1d430fd53e31a47.json":
    "5600c600d6911d2468813035feb877775d306732d62d20ae7faf70d5f172a7c6",
    "rtd_5330e9966910b66a2a64380a39c190e12bc3649e8192f47b2358c6a13331f2f9.json":
    "e5ecbd1eb887efb1f852261c40e46565898e3be055ebdb2e13a93a76078881b8",
    "rtd_a21999304a0a5458eef47b82cd06a8c055aa83d2aa90bb8b17d93590c3487f06.json":
    "56e688d7a29a0d518ffbcbb1e776d229ec4a0419be4ceb6db021741b40b5e008",
}

FROZEN_VS001_RECORD = {
    "vsp_c8e5d91d38c5e3f36d0d592737aac5ce26c03eb5d169365c38953f971ff62ba0.json":
    "f190ec2437f5e3cee40e0e8a74ca27e0608866ae818f5b351dd8f8a1f48a06e5",
}

FROZEN_VM001_RECORD = {
    "vrg_40c8c6b984345af33de6913ca9025d60d22b0e627b110e974c78270eb941dca7.json":
    "dc16507a5f0aeec36ead054ff68dce4ac5d639e0d58cf30eb60315b8d41deefc",
}


class TestVm001Fixture:
    def test_nine_mk001_records_byte_frozen(self):
        import hashlib

        for name, digest in {**FROZEN_MK001_RECORDS,
                             **FROZEN_VM001_RECORD,
                             **FROZEN_VS001_RECORD}.items():
            path = DEMO_MODEL / "records" / name
            assert hashlib.sha256(
                path.read_bytes()).hexdigest() == digest, name

    def test_old_revision_replays_without_the_variable(self):
        """Append-only history: the pre-variable revision is intact, and a
        model at that revision honestly cannot see the variable."""
        store = ModelStore(DEMO_MODEL)
        old_ids = [name[:-5] for name in FROZEN_MK001_RECORDS]
        replayed = store.replay(old_ids)
        assert replayed.revision.revision_id == OLD_GOLDEN_REVISION
        assert replayed.revision.record_count == 9
        result = ModelQueries(replayed).variable(HOTEND_VARIABLE)
        assert result.status == "not_registered"
        assert result.revision.revision_id == OLD_GOLDEN_REVISION

    def test_variable_registered_with_exact_declared_anchor(self):
        """The new revision registers the EXACT anchor declared in
        bindings/demo-printer (field-for-field, ownership included)."""
        from backend.identity_binding.store import BindingStore

        queries = demo_queries()
        result = queries.variable(HOTEND_VARIABLE)
        assert result.status == "registered"
        declared = BindingStore(
            Path("bindings/demo-printer")).load().anchors_by_id[
            HOTEND_VARIABLE]
        assert result.registration.anchor == declared
        assert result.registration.anchor.entity_anchor_id == EXTRUDER
        owned = queries.variables_of(EXTRUDER)
        assert [e.anchor.anchor_id for e in owned.entries] == [
            HOTEND_VARIABLE]


class TestVs001Fixture:
    HOTEND = HOTEND_VARIABLE
    SPECIFICATION_ID = "vsp_c8e5d91d38c5e3f36d0d592737aac5ce26c03eb5d169365c38953f971ff62ba0"

    def test_specification_governs_with_the_approved_content(self):
        result = demo_queries().variable_value_specification(self.HOTEND)
        assert result.status == "specified"
        record = result.specification
        assert record.record_id == self.SPECIFICATION_ID
        assert record.variable_anchor_id == self.HOTEND
        assert record.value_shape == "number"
        assert record.nullable is False
        assert record.unit.kind == "declared"
        assert (record.unit.unit.system_id, record.unit.unit.system_edition,
                record.unit.unit.code) == ("project_local", "ohk-units-1",
                                           "degree_celsius")
        assert record.supersedes == ()
        assert record.authority.agent == "mk001_demo_fixture"
        assert len(record.evidence) == 1
        assert record.evidence[0].kind == "owner_declaration"

    def test_permanent_evidence_is_model_only(self):
        """The ledger record makes no claim about any source. Naming a
        specific device or its absent unit would be source knowledge in the
        model ledger."""
        statement = demo_queries().variable_value_specification(
            self.HOTEND).specification.evidence[0].statement
        for banned in ("moonraker", "klipper", "printer", "extruder",
                       "hotend", "json_pointer", "declared_unit",
                       "adapter_id", "source_id", "60.4"):
            assert banned not in statement.lower(), banned
        assert "makes no claim about any source" in statement
        assert "identity token, not a unit definition" in statement

    def test_pre_specification_revision_replays_without_it(self):
        store = ModelStore(DEMO_MODEL)
        old_ids = [record_id for record_id
                   in store.load().revision.record_ids
                   if not record_id.startswith("vsp_")]
        replayed = store.replay(old_ids)
        assert replayed.revision.revision_id == PRE_SPECIFICATION_REVISION
        assert replayed.revision.record_count == 10
        result = ModelQueries(replayed).variable_value_specification(
            self.HOTEND)
        assert result.status == "not_specified"
        assert result.specification is None
