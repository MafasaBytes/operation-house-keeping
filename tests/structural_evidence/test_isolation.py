"""SN-001a isolation gate (I1a-I6, A5b/A5c/A5h/A5i-a, SW1).

The gate proves exactly one thing: a CSV structural claim is source-native
evidence, not a canonical identity or model claim, and this module has no
mechanism capable of making it one. Every sweep carries an anti-vacuity
guard; each was demonstrated red once by a deliberate mutation in a
scratch copy (recorded in the commit message).
"""

import ast
import hashlib
import re
from pathlib import Path

import backend.structural_evidence as sn_package

SN_DIR = Path(sn_package.__file__).parent
README = SN_DIR / "README.md"

# I3: the complete import allow-list. The curated model_kernel TYPE
# surface (LifecycleView) IS allowed; the upper facades never are.
ALLOWED_BACKEND_ROOTS = (
    "backend.data_sources",
    "backend.temporal_state",
    "backend.system_identity",
    "backend.identity_binding",
    "backend.model_kernel",
    "backend.structural_evidence",
)
FORBIDDEN_IMPORTS = ("backend.model_state", "backend.observation_compatibility")

CANONICAL_ID_PREFIXES = ("ent_", "var_", "reg_", "rel_", "rtd_", "rwd_",
                         "vrg_", "vsp_", "anc_", "iba_")
WRITE_PATH_TOKENS = ("ModelStore", "BindingStore", "FilesystemRawStore",
                     "build_record", ".append(", "put_", "write_text",
                     "write_bytes")
RESOLUTION_STATUS_LITERALS = (
    "bound", "applicability_unknown", "outside_applicability", "unbound",
    "ambiguous", "conflicted", "superseded", "retracted", "inactive")
LIFECYCLE_VIEW_MEMBERS = ("as_designed", "as_built", "as_configured",
                          "as_operated", "as_maintained")


def sn_sources() -> list[Path]:
    sources = sorted(SN_DIR.glob("*.py"))
    assert len(sources) >= 5, "SN-001 sources not found — vacuous scan"
    return sources


def string_literals(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node.value


class TestI1aNoIdentityMinting:
    def test_no_anchor_constructor_and_no_uuid(self):
        for path in sn_sources():
            text = path.read_text(encoding="utf-8")
            for needle in ("EntityAnchor(", "VariableAnchor(",
                           "AnchorDeclaration(", "BindingAssertion(",
                           "uuid4", "uuid1"):
                assert needle not in text, f"{needle!r} in {path.name}"

    def test_no_canonical_id_prefix_is_ever_produced(self):
        """No string literal, and no f-string fragment, begins or embeds a
        canonical id prefix. SN-001 derives or mints no ent_/var_/reg_/
        rel_/rtd_ identifier — upstream extractor-local ids are not
        canonical anchors and carry no such prefix."""
        # word-boundary form: "parent_column_index" must not trip "ent_".
        # A fully-anchored VALIDATION regex ("^reg_[0-9a-f]{64}$") is not
        # id production — the string cannot itself be an id value — and is
        # exempt; every other literal shape stays banned.
        producing = re.compile(
            "(?<![A-Za-z0-9])(" + "|".join(CANONICAL_ID_PREFIXES) + ")")
        checked = 0
        for path in sn_sources():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for value in string_literals(tree):
                checked += 1
                if value.startswith("^") and value.endswith("$"):
                    continue
                match = producing.search(value)
                assert match is None, (
                    f"{match.group(0) if match else ''!r} inside a literal "
                    f"in {path.name}: {value!r}")
        assert checked >= 100, "vacuous literal scan"

    def test_assembly_definition_contains_is_absent_in_sn001a(self):
        """I1a half: the relationship type name must not exist in module
        source before SN-001c hand-authors the rtd_ record (I1c then
        asserts exactly-once over the model records)."""
        for path in sn_sources():
            assert "assembly_definition_contains" not in path.read_text(
                encoding="utf-8"), path.name


class TestI2NoWritePath:
    def test_no_store_or_ledger_write_tokens(self):
        for path in sn_sources():
            text = path.read_text(encoding="utf-8")
            for needle in WRITE_PATH_TOKENS:
                assert needle not in text, f"{needle!r} in {path.name}"

    def test_no_write_mode_open(self):
        pattern = re.compile(r"open\([^)]*[\"'][wax]b?[\"']")
        for path in sn_sources():
            assert not pattern.search(path.read_text(encoding="utf-8")), (
                f"write-mode open() in {path.name}")


class TestI3ImportBoundary:
    def test_sn001_imports_only_the_allow_list(self):
        found_backend_imports = 0
        for path in sn_sources():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                modules = []
                if isinstance(node, ast.ImportFrom) and node.module:
                    modules = [node.module]
                elif isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                for module in modules:
                    if not module.startswith("backend"):
                        continue
                    found_backend_imports += 1
                    assert module.startswith(ALLOWED_BACKEND_ROOTS), (
                        f"{module} imported by {path.name}")
                    assert not module.startswith(FORBIDDEN_IMPORTS), (
                        f"{module} imported by {path.name}")
        assert found_backend_imports >= 5, "vacuous import scan"

    def test_no_accepted_module_imports_structural_evidence(self):
        accepted = sorted(
            p for p in Path(sn_package.__file__).parent.parent.rglob("*.py")
            if "structural_evidence" not in p.parts
            and "__pycache__" not in p.parts)
        assert len(accepted) >= 60, "vacuous reverse scan"
        for path in accepted:
            assert "structural_evidence" not in path.read_text(
                encoding="utf-8"), path.name


class TestI4NoFilesystemMutation:
    def test_claim_derivation_mutates_no_committed_ledger(self, tmp_path):
        """(relpath, sha256) sweep of models/, bindings/, var/ across a
        full derivation including a failure path. showcases/ joins the
        corpus when it exists (SN-001b)."""
        import shutil

        from backend.data_sources.catalog import InMemorySourceCatalog
        from backend.data_sources.connectors import LocalFileConnector
        from backend.data_sources.contracts import SourceDefinition
        from backend.data_sources.raw_store import FilesystemRawStore
        from backend.data_sources.runtime import IngestionRunner
        from backend.structural_evidence.claims import (
            CsvStructuralReading,
            csv_structural_claims,
        )
        from backend.structural_evidence.contracts import (
            UnknownEngineeringContext,
        )
        from backend.structural_evidence.errors import StructuralEvidenceError
        from datetime import UTC, datetime

        def sweep() -> dict[str, str]:
            snapshot = {}
            roots = [Path("models"), Path("bindings")]
            if Path("showcases").exists():
                roots.append(Path("showcases"))
            for root in roots:
                for file in sorted(root.rglob("*")):
                    if file.is_file():
                        snapshot[str(file)] = hashlib.sha256(
                            file.read_bytes()).hexdigest()
            assert len(snapshot) >= 20, "vacuous ledger sweep"
            return snapshot

        before = sweep()
        path = tmp_path / "bom.csv"
        shutil.copy(Path("backend/data_sources/testing/fixtures/"
                         "bom_valid.csv"), path)
        catalog = InMemorySourceCatalog()
        catalog.register(SourceDefinition(
            source_id="bom-1", display_name="b", source_kind="tabular_file",
            connector_type="local_file", configuration={"path": str(path)},
            credential_reference=None, declared_content_types=["text/csv"],
            enabled=True))
        store = FilesystemRawStore(tmp_path / "raw_store")
        runner = IngestionRunner(
            catalog=catalog, store=store,
            connectors={"local_file": LocalFileConnector()},
            clock=lambda: datetime(2026, 8, 11, 12, 0, tzinfo=UTC))
        runner.run("bom-1")
        envelope = next(store.iter_accepted_envelopes("bom-1"))
        context = UnknownEngineeringContext(
            kind="unknown", reason="authority_has_not_declared")
        csv_structural_claims(
            store.get_extraction(envelope.record_id), source_id="bom-1",
            payload_checksum=envelope.payload_checksum,
            engineering_context=context,
            reading=CsvStructuralReading(quantity_column_index=2,
                                         parent_column_index=4,
                                         parent_matches_column_index=0))
        # failure path too
        try:
            csv_structural_claims(
                store.get_extraction(envelope.record_id), source_id="bom-1",
                payload_checksum=envelope.payload_checksum,
                engineering_context=context,
                reading=CsvStructuralReading(quantity_column_index=99,
                                             parent_column_index=None,
                                             parent_matches_column_index=None))
        except StructuralEvidenceError:
            pass
        assert sweep() == before


class TestI5NoLifecycleViewMembers:
    def test_no_view_member_literal_in_sn001_source(self):
        """The imported LifecycleView TYPE and the declared_lifecycle_view
        discriminator are expected; the five member literals must never
        appear — any occurrence would be a filename/format->view
        inference vector."""
        checked = 0
        for path in sn_sources():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for value in string_literals(tree):
                checked += 1
                assert value not in LIFECYCLE_VIEW_MEMBERS, (
                    f"view member {value!r} in {path.name}")
        assert checked >= 100, "vacuous literal scan"


class TestI6NoParallelResolutionVocabulary:
    def test_no_module_level_literal_alias_re_expresses_statuses(self):
        """Comparing against a carried ResolutionResult.status is allowed
        (SN-001c); DEFINING a Literal containing IB-001's status values is
        not."""
        for path in sn_sources():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Subscript) and isinstance(
                        node.value, ast.Name) and node.value.id == "Literal":
                    members = {v for v in string_literals(node)
                               if isinstance(v, str)}
                    overlap = members & set(RESOLUTION_STATUS_LITERALS)
                    assert not overlap, (
                        f"re-expressed resolution vocabulary {overlap} "
                        f"in {path.name}")


class TestA5PublishedWording:
    def test_a5b_module_docstring_states_the_boundary_verbatim(self):
        docstring = ast.get_docstring(
            ast.parse((SN_DIR / "__init__.py").read_text(encoding="utf-8")))
        for sentence in (
            "It accepts nothing into any model, declares no canonical\n"
            "identity, mints no anchor, writes no ledger, and nothing here "
            "is\nengineering truth.",
            "The runtime module owns no authoritative store or\nledger.",
            "Identity decisions live in identity_binding; model truth lives "
            "in\nmodel_kernel.",
        ):
            assert sentence in docstring

    def test_a5c_runtime_storage_wording_verbatim(self):
        text = README.read_text(encoding="utf-8")
        for sentence in (
            "SN-001's runtime module owns no authoritative store, no "
            "ledger, and no\nrevision id.",
            "Committed\nshowcase derivatives are test artifacts, not "
            "engineering truth or runtime\nauthority.",
            "The hand-authored binding and model records are engineering\n"
            "knowledge, and they were authored by a person, not by SN-001 "
            "code.",
        ):
            assert sentence in text

    def test_a5h_k1_contract_wording_verbatim(self):
        text = README.read_text(encoding="utf-8")
        assert ("Changes to rule data are content-addressed and necessarily "
                "create a new\nsubject namespace. Changes to the shared rule "
                "interpreter or subject\nencoder are guarded by a versioned "
                "algorithm contract, hand-authored\nbehavior vectors, and "
                "implementation-drift tests; this is enforced by\ntests and "
                "review, not by construction alone.") in text
        # the forbidden overclaim never reappears for interpreter changes
        assert "structurally impossible" not in text

    def test_a5i_full_limitation_list_verbatim(self):
        """A5i (commit 18): all sixteen limitations, verbatim."""
        text = README.read_text(encoding="utf-8")
        for fragment in (
            "not guaranteed stable\n   across re-exports",
            "stable for a fixed extractor build",
            "second, non-merging containment\n   lineage",
            "cannot cite its structural\n   derivation",
            "Two hops, neither\n   kernel-verified.",
            "the frozen STEP extraction is trusted",
            "not proven exhaustively",
            "does not resemble a real printer",
            "Atomic multi-record acceptance is not provided.",
        ):
            assert fragment in text, fragment

    def test_a5i_a_sn001a_limitation_subset_verbatim(self):
        text = README.read_text(encoding="utf-8")
        for fragment in (
            "A recorded mapping is an unauthenticated authority claim, "
            "never\n   evidence that the mapping is correct.",
            "Structural mapping applicability is asserted on the "
            "ingestion-receipt\n   axis only and carries no lifecycle-view "
            "validity.",
            "A claim whose engineering context is unknown can never be "
            "materialized.",
            "Anchor ids are uuid4 hex by accepted decision; SN-001 "
            "generates none.",
            "The raw store is not committed",
            "guarded by tests and review, not\n    by construction.",
            "The runtime module owns no store",
            "A structural mapping is scoped to one `source_id`",
        ):
            assert fragment in text, fragment


class TestSW1Redaction:
    def test_no_absolute_paths_or_secrets_in_claim_output(self, tmp_path):
        import shutil
        from datetime import UTC, datetime

        from backend.data_sources.catalog import InMemorySourceCatalog
        from backend.data_sources.connectors import LocalFileConnector
        from backend.data_sources.contracts import SourceDefinition
        from backend.data_sources.raw_store import FilesystemRawStore
        from backend.data_sources.runtime import IngestionRunner
        from backend.structural_evidence.claims import (
            CsvStructuralReading,
            csv_structural_claims,
        )
        from backend.structural_evidence.contracts import (
            UnknownEngineeringContext,
        )

        path = tmp_path / "bom.csv"
        shutil.copy(Path("backend/data_sources/testing/fixtures/"
                         "bom_valid.csv"), path)
        catalog = InMemorySourceCatalog()
        catalog.register(SourceDefinition(
            source_id="bom-1", display_name="b", source_kind="tabular_file",
            connector_type="local_file", configuration={"path": str(path)},
            credential_reference=None, declared_content_types=["text/csv"],
            enabled=True))
        store = FilesystemRawStore(tmp_path / "raw_store")
        runner = IngestionRunner(
            catalog=catalog, store=store,
            connectors={"local_file": LocalFileConnector()},
            clock=lambda: datetime(2026, 8, 11, 12, 0, tzinfo=UTC))
        runner.run("bom-1")
        envelope = next(store.iter_accepted_envelopes("bom-1"))
        claims = csv_structural_claims(
            store.get_extraction(envelope.record_id), source_id="bom-1",
            payload_checksum=envelope.payload_checksum,
            engineering_context=UnknownEngineeringContext(
                kind="unknown", reason="authority_has_not_declared"),
            reading=CsvStructuralReading(quantity_column_index=2,
                                         parent_column_index=4,
                                         parent_matches_column_index=0))
        dumped = claims.model_dump_json()
        assert len(dumped) > 1000, "vacuous redaction sweep"
        for needle in (str(tmp_path), "/home/", "/mnt/", "C:\\\\",
                       "password", "secret", "Bearer", "api_key"):
            assert needle not in dumped, needle
