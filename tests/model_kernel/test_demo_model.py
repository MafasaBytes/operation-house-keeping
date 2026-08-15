"""MK-001 committed demo model: golden revision, honest authority, the
root → subsystem → extruder chain, the non-hierarchical instance_of edge,
and committed-record hygiene."""

import json
from pathlib import Path

from backend.model_kernel.queries import ModelQueries
from backend.model_kernel.store import ModelStore

DEMO_MODEL = Path("models/demo-printer")
# Every HISTORICAL revision is pinned by replay over an explicit id list;
# only the current membership is pinned by load(). A prefix filter is
# never an acceptable membership selector.
CURRENT_REVISION = ("mrv_23631989f98b678aaf1c556c345ac57a320ec266c2f712a4"
                    "0099e8032ca8135b")  # 16 records (ES-001)
PRE_ES001_REVISION = ("mrv_702c840f7da00617feb1be252838105d8b001b2e19978842"
                      "bdcbec56996c99ff")  # 14 records (SN-001)
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
ASSEMBLY_TYPE = "ent_5a6b7c8d9e0f1a2b3c4d5e6f70819203"  # SN-001, O2

SN001_MODEL_RECORDS = (
    "reg_c17de916b41ab5f6bcdf4165f47da1d604689e1eafa9afc31ea99092eacbcc90",
    "rel_2978509392132152b2d74beb139d2f85e8508f6c50e6ebfea996cd7c78fcf0d5",
    "rtd_04b8da45255190340e7366ce2a373a9b402dc32eb86b6312f382f5e37a4e81b7",
)

ES001_MODEL_RECORDS = (
    "vsm_053882a4714f51a0e9d358b5a8598cfca856482d9af9acd0117313a9ab8d1c40",
    "vsm_3b4b829006033604f088f2ff0e2727f4b2a1987f7d0edc5be54327562ef8791b",
)

VS001_MEMBERSHIP = (
    "reg_5776a541a04b428f35af40203294a34a8a9978f0bdf3572a8745e6febddd5941",
    "reg_9b5491aaa131b0df070cee792c83e002bdc4232cbbaba443f967cd3e5b780451",
    "reg_a502243be0cb229ab386f20db6803e01329dcdd5a22f8e922f1a92555a7ba0ba",
    "reg_c7ad4c326425439d5e2bff4d0a3dc42cf26540514ecc015d060c711943ff92c5",
    "rel_12a2812d151da28579784518b619a2a577318a977911bcaf27093d9263d044fa",
    "rel_3c5a723282c6fc05cd694e5a98e208840e1d897f80dc29a524c0b8d35ff34d5a",
    "rel_a1fef969809045884d29a981df43bce332b9a8871bd2236cd1d430fd53e31a47",
    "rtd_5330e9966910b66a2a64380a39c190e12bc3649e8192f47b2358c6a13331f2f9",
    "rtd_a21999304a0a5458eef47b82cd06a8c055aa83d2aa90bb8b17d93590c3487f06",
    "vrg_40c8c6b984345af33de6913ca9025d60d22b0e627b110e974c78270eb941dca7",
    "vsp_c8e5d91d38c5e3f36d0d592737aac5ce26c03eb5d169365c38953f971ff62ba0",
)

PRE_SPECIFICATION_MEMBERSHIP = (
    "reg_5776a541a04b428f35af40203294a34a8a9978f0bdf3572a8745e6febddd5941",
    "reg_9b5491aaa131b0df070cee792c83e002bdc4232cbbaba443f967cd3e5b780451",
    "reg_a502243be0cb229ab386f20db6803e01329dcdd5a22f8e922f1a92555a7ba0ba",
    "reg_c7ad4c326425439d5e2bff4d0a3dc42cf26540514ecc015d060c711943ff92c5",
    "rel_12a2812d151da28579784518b619a2a577318a977911bcaf27093d9263d044fa",
    "rel_3c5a723282c6fc05cd694e5a98e208840e1d897f80dc29a524c0b8d35ff34d5a",
    "rel_a1fef969809045884d29a981df43bce332b9a8871bd2236cd1d430fd53e31a47",
    "rtd_5330e9966910b66a2a64380a39c190e12bc3649e8192f47b2358c6a13331f2f9",
    "rtd_a21999304a0a5458eef47b82cd06a8c055aa83d2aa90bb8b17d93590c3487f06",
    "vrg_40c8c6b984345af33de6913ca9025d60d22b0e627b110e974c78270eb941dca7",
)

PRE_ES001_MEMBERSHIP = tuple(sorted((*VS001_MEMBERSHIP,
                                     *SN001_MODEL_RECORDS)))


def eleven_ids(loaded):
    """The explicit VS-001 membership; ``loaded`` is API compatibility."""
    del loaded
    return tuple(sorted(VS001_MEMBERSHIP))


def demo_queries():
    return ModelQueries(ModelStore(DEMO_MODEL).load())


class TestCommittedLedger:
    def test_golden_revision_and_membership(self):
        store = ModelStore(DEMO_MODEL)
        loaded = store.load()
        assert loaded.revision.revision_id == CURRENT_REVISION
        assert loaded.revision.record_count == 16
        assert len(loaded.variable_registrations_by_anchor) == 1
        assert len(loaded.specifications) == 1
        assert len(loaded.types) == 3
        assert len(loaded.assertions) == 4
        assert len(loaded.registrations_by_anchor) == 5
        # RP1: the VS-001 revision replays from its explicit 11-id list
        replayed = store.replay(eleven_ids(loaded))
        assert replayed.revision.revision_id == GOLDEN_REVISION
        assert replayed.revision.record_count == 11
        pre_es001 = store.replay(PRE_ES001_MEMBERSHIP)
        assert pre_es001.revision.revision_id == PRE_ES001_REVISION
        assert pre_es001.revision.record_count == 14

    def test_fixture_authority_never_human_owner(self):
        """Mandatory regression, per-record form (AU2): every record is
        test_fixture; the eleven pre-SN-001 records stay attributed to
        mk001_demo_fixture and the three SN-001 records to
        sn001_showcase_fixture. An unlisted record fails."""
        loaded = ModelStore(DEMO_MODEL).load()
        expected = {
            **{record_id: "mk001_demo_fixture"
               for record_id in VS001_MEMBERSHIP},
            **{record_id: "sn001_showcase_fixture"
               for record_id in SN001_MODEL_RECORDS},
            **{record_id: "es001_demo_fixture"
               for record_id in ES001_MODEL_RECORDS},
        }
        paths = sorted((DEMO_MODEL / "records").glob("*.json"))
        assert len(paths) == len(expected) == 16
        for path in paths:
            record = json.loads(path.read_text())
            assert record["authority"]["kind"] == "test_fixture", path.name
            assert record["record_id"] in expected, path.name
            assert record["authority"]["agent"] == \
                expected[record["record_id"]], path.name
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

# RP6 (SN-001): the seven pre-SN-001 binding records are byte-frozen too;
# an SN-001c append may only ADD files, never touch these.
FROZEN_PRE_SN001_BINDING_RECORDS = {
    "bindings/demo-printer/records/anc_81d43569d1b093c1b52247bdfb8039ae6e4777eecd3918c498a85655fec9bbdc.json":
    "0d16b20f768b3e14f8137c42d1cfd03c0825070aeffc699303ed4d1e5cb1cbfa",
    "bindings/demo-printer/records/anc_e7bd0b35b97ee920384ac5791c90e3ae34889b642b54608cf3293a5174cb5ae3.json":
    "6254e0486741235483fc079c29a1fd9dce9d77bc1596c397719bb5530694a36a",
    "bindings/demo-printer/records/iba_b1b86a4fd0c56f36aafb4574176429c0edab530dbbd5d1da954a54f2533fd90c.json":
    "08cdf0f23d2938f4419421eaec6f9a79e7507db427195367700c1d174b59bd8a",
    "bindings/demo-printer/records/iba_ba80b9e561b564a465b19109e2576d79d93b10e5b87e9917bf7ed45558c3a90a.json":
    "bf13714a1094e13944b0a6d4d3ebf3639b928ea411d694e8f9f1c6348eaa068f",
    "bindings/demo-printer-model/records/anc_037d327111553c3410f162dbb8ffccf475fd0b1a15b4134e304d6ade99141c21.json":
    "f648fd2e25b3594905da44343e197675186ab814f9735e0fd899bfeadfb3af40",
    "bindings/demo-printer-model/records/anc_69ebd49c67eb6b5ab775dbf0866efbbdfeaf625005bc50d2848d98a044014a22.json":
    "37dc5639a2bfbcf1122bf6c2b1ae2a81d8dd390e2cb0d1cfac77c08eb369720e",
    "bindings/demo-printer-model/records/anc_c6aa3f3f3e03cc689a40ecd5d70d04828cbd1143bb107e85c2dd55268c2312d8.json":
    "40e99c14da3ebcbfb30e26a2761c991d9990aac503053ec1fb193d046a89a3c5",
}

# ES-001 Group 3 (acceptance row RP5): the SN-001 records are byte-frozen
# too — completing the freeze maps BEFORE any ES-001 append lands, so a
# mutation of accepted history is mechanically detectable. Measured
# digests recorded in
# docs/superpowers/plans/2026-08-13-es001-integrity-red-baseline.md.
FROZEN_SN001_MODEL_RECORDS = {
    "reg_c17de916b41ab5f6bcdf4165f47da1d604689e1eafa9afc31ea99092eacbcc90.json":
    "6c572dd6d1af044bb3bc45937bdedfc5b1308a926684b19ece0145bd80587dd8",
    "rel_2978509392132152b2d74beb139d2f85e8508f6c50e6ebfea996cd7c78fcf0d5.json":
    "53242190bb0d3bc840aeb6507207c7ab586a277ee2a88f4fc750bb3493dec7fe",
    "rtd_04b8da45255190340e7366ce2a373a9b402dc32eb86b6312f382f5e37a4e81b7.json":
    "b57a7afda3627f1e7ebcfc82c7baecc951610a7e0379642c63ce403e39c123e0",
}

FROZEN_ES001_MODEL_RECORDS = {
    "vsm_053882a4714f51a0e9d358b5a8598cfca856482d9af9acd0117313a9ab8d1c40.json":
    "371527c7bd45c3118043b3da3ab2f17bb34769eacea4dd48e84eb148c71ea33a",
    "vsm_3b4b829006033604f088f2ff0e2727f4b2a1987f7d0edc5be54327562ef8791b.json":
    "b04377e1a5385a2a301ef288a0a211fcf06602914a36a2da334615915659730f",
}

FROZEN_SN001_BINDING_RECORDS = {
    "bindings/demo-printer/records/iba_2061f4017a7f2355a36d30ee69a6ebc24a94de2e1db8866b4216916678b4d5aa.json":
    "2eec748ec43373b1c0bd5aa2744466f94db9c0f0d19503754077b6277c3d7a82",
    "bindings/demo-printer/records/iba_22a8eef16595ec5d38f9135b04499c76f358055a6e5ea4dba9c62f7d9b9d3a43.json":
    "df6c955a834121493966b509a4c67da73d22bcee2a4271b62976bfa90256e615",
    "bindings/demo-printer-model/records/anc_4a576f8b7630176969e2c3186ae5c8233e71311cfbac7c071d7c125b32e0bfdb.json":
    "972a8407582523836250898f0961e7dc412e9e0e07d3d3a9375aee5f7d1799b1",
    "bindings/demo-printer-model/records/iba_162f634fe39b38369db141c76718140340773f0080bca628503090eac445fa08.json":
    "e782c90f413dc9de49a9242be97580e834fc1fc1ed2824457dddaacad3d281b1",
}


class TestVm001Fixture:
    def test_nine_mk001_records_byte_frozen(self):
        import hashlib

        for name, digest in {**FROZEN_MK001_RECORDS,
                             **FROZEN_VM001_RECORD,
                             **FROZEN_VS001_RECORD,
                             **FROZEN_SN001_MODEL_RECORDS,
                             **FROZEN_ES001_MODEL_RECORDS}.items():
            path = DEMO_MODEL / "records" / name
            assert hashlib.sha256(
                path.read_bytes()).hexdigest() == digest, name
        # RP6 + ES-001 RP5: ALL eleven committed binding records stay
        # byte-identical (seven pre-SN-001 + four SN-001)
        for relpath, digest in {**FROZEN_PRE_SN001_BINDING_RECORDS,
                                **FROZEN_SN001_BINDING_RECORDS}.items():
            assert hashlib.sha256(
                Path(relpath).read_bytes()).hexdigest() == digest, relpath

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
        """RP2: explicit membership, never a prefix filter — after the
        SN-001 appends a `vsp_` filter would silently select 13 records
        while claiming the pre-specification revision."""
        store = ModelStore(DEMO_MODEL)
        replayed = store.replay(PRE_SPECIFICATION_MEMBERSHIP)
        assert replayed.revision.revision_id == PRE_SPECIFICATION_REVISION
        assert replayed.revision.record_count == 10
        result = ModelQueries(replayed).variable_value_specification(
            self.HOTEND)
        assert result.status == "not_specified"
        assert result.specification is None
