"""MK-001 committed demo model: golden revision, honest authority, the
root → subsystem → extruder chain, the non-hierarchical instance_of edge,
and committed-record hygiene."""

import json
from pathlib import Path

from backend.model_kernel.queries import ModelQueries
from backend.model_kernel.store import ModelStore

DEMO_MODEL = Path("models/demo-printer")
GOLDEN_REVISION = ("mrv_c28b6301f712f94249e6ccea87f1cfd4f9c04c1cc00fef3ae3d0"
                   "23e3da83227f")
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
        assert loaded.revision.record_count == 9
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
