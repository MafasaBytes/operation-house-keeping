"""MK-001 repair series: trust-boundary revalidation, validated query
inputs, unambiguous relationship absence, and a deliberate public surface.

Four owner-confirmed findings, each encoded as observable behavior at a
public boundary:

F1  a successful ``append`` could write a record the ledger cannot read
    back — both trust boundaries must structurally revalidate every
    supplied record from plain field data, never trusting that the
    object's Python class implies validity.
F2  query arguments reached evaluation unvalidated — a bad view leaked a
    raw ValidationError and a plain-mapping context silently answered
    "nothing" instead of matching.
F3  ``relationships`` answered identically for "registered, no edges" and
    "never registered".
F4  the package exported nothing, so callers had to reach into modules.
"""

import hashlib
import warnings

import pytest

from backend.model_kernel.canonical import compute_record_id
from backend.model_kernel.contracts import (
    ModelIntegrityError,
    ModelKernelError,
    ModelQueryError,
)
from backend.model_kernel.queries import ModelQueries
from backend.model_kernel.store import validate_record_collection

from tests.model_kernel.builders import (
    AS_BUILT,
    ENT_A,
    ENT_B,
    ENT_C,
    ENT_D,
    VIEW_FREE,
    assertion,
    contains_type,
    containment_world,
    instance_of_type,
    registration,
    store_with,
    withdrawal,
)


def corrupt(record, *, rehash=True, **updates):
    """Forge a record pydantic never validated.

    ``model_copy(update=...)`` writes fields without validation, so the
    result is an instance of the right class carrying impossible data —
    exactly what a caller can hand a public boundary. Unless the record
    kind itself is broken, the content-derived id is recomputed so the
    forgery is hash-self-consistent and only STRUCTURAL revalidation can
    catch it. Serializer warnings raised while forging belong to the test,
    not to the boundary under test.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        forged = record.model_copy(update=updates)
        if rehash:
            forged = forged.model_copy(
                update={"record_id": compute_record_id(forged)})
    return forged


def construct_unvalidated(record, **updates):
    """Forge via ``model_construct``, which skips validation entirely
    instead of overwriting validated fields, then rehash so the forgery is
    self-consistent."""
    fields = {name: getattr(record, name)
              for name in type(record).model_fields}
    fields.update(updates)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        forged = type(record).model_construct(**fields)
        return type(record).model_construct(
            **{**fields, "record_id": compute_record_id(forged)})


def snapshot(store) -> dict[str, str]:
    """path name -> sha256 of every ledger member."""
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(store.records_dir.iterdir())}


def repair_world(tmp_path):
    """contains type + registrations A and B + one active A→B edge."""
    kind = contains_type()
    edge = assertion(kind, source=ENT_A, target=ENT_B)
    return containment_world(tmp_path, edge), kind, edge


def query_world(tmp_path):
    """contains A→B (as_built) plus instance_of B→C (view-independent)."""
    contains = contains_type()
    instance_of = instance_of_type()
    store = store_with(
        tmp_path, contains, instance_of, registration(ENT_A),
        registration(ENT_B), registration(ENT_C, kind="type_definition"),
        assertion(contains, source=ENT_A, target=ENT_B),
        assertion(instance_of, source=ENT_B, target=ENT_C, context=VIEW_FREE))
    return ModelQueries(store.load())


# --------------------------------------------------------------- finding 1
CORRUPTIONS = [
    pytest.param(lambda kind, edge: corrupt(registration(ENT_C), note=123),
                 id="registration_note_not_a_string"),
    pytest.param(lambda kind, edge: corrupt(registration(ENT_C),
                                            anchor={"anchor_id": ENT_C}),
                 id="registration_anchor_payload_broken"),
    pytest.param(lambda kind, edge: corrupt(
        contains_type(type_name="feeds", hierarchy_semantics="none"),
        hierarchy_semantics="sometimes"),
        id="type_definition_invalid_literal"),
    pytest.param(lambda kind, edge: corrupt(
        contains_type(type_name="feeds", hierarchy_semantics="none"),
        source_referent_kinds=("widget",)),
        id="type_definition_broken_endpoint_kinds"),
    pytest.param(lambda kind, edge: corrupt(
        assertion(kind, source=ENT_B, target=ENT_A),
        context={"kind": "lifecycle_view"}),
        id="assertion_malformed_context"),
    pytest.param(lambda kind, edge: corrupt(
        assertion(kind, source=ENT_B, target=ENT_A), evidence=()),
        id="assertion_evidence_emptied"),
    pytest.param(lambda kind, edge: corrupt(withdrawal(edge), note=123),
                 id="withdrawal_note_not_a_string"),
    pytest.param(lambda kind, edge: corrupt(withdrawal(edge),
                                            withdraws="not-a-record-id"),
                 id="withdrawal_target_malformed"),
    pytest.param(lambda kind, edge: corrupt(registration(ENT_C), rehash=False,
                                            record_kind="not_a_kind"),
                 id="record_kind_unknown"),
    # model_construct skips validation entirely rather than overwriting
    # validated fields — the other half of the bypass surface
    pytest.param(lambda kind, edge: construct_unvalidated(registration(ENT_C),
                                                          note=123),
                 id="registration_model_construct_bad_note"),
    pytest.param(lambda kind, edge: construct_unvalidated(
        registration(ENT_C), anchor={"anchor_id": "not-an-anchor"}),
        id="registration_model_construct_broken_anchor"),
]


class TestAppendRevalidatesStructurally:
    @pytest.mark.parametrize("forge", CORRUPTIONS)
    def test_forged_record_rejected_and_ledger_untouched(self, tmp_path, forge):
        """A record whose Python class says "valid" but whose field data is
        not may never reach the ledger: an append that would poison the
        next load is refused, typed, and writes nothing."""
        store, kind, edge = repair_world(tmp_path)
        bad = forge(kind, edge)
        before_files = snapshot(store)
        before_revision = store.load().revision

        with pytest.raises(ModelIntegrityError) as excinfo:
            store.append(bad)

        assert set(snapshot(store)) == set(before_files)  # no member written
        assert snapshot(store) == before_files            # byte-for-byte
        assert store.load().revision == before_revision   # still loads
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"
        message = str(excinfo.value)
        assert str(tmp_path) not in message
        assert "/tmp/" not in message

    def test_rejected_append_leaks_no_serializer_warning(self, tmp_path):
        """The rejection is the whole public outcome: no pydantic
        UserWarning escapes on the way to it."""
        store, kind, edge = repair_world(tmp_path)
        bad = corrupt(registration(ENT_C), note=123)
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            with pytest.raises(ModelIntegrityError) as excinfo:
                store.append(bad)
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"

    def test_valid_append_still_succeeds(self, tmp_path):
        """Revalidation is a gate, not a wall — honest records still land."""
        store, kind, edge = repair_world(tmp_path)
        record = registration(ENT_C)
        assert store.append(record) == record.record_id
        assert record.record_id in store.load().records


class TestCollectionValidatorRevalidatesStructurally:
    @pytest.mark.parametrize("forge", [
        pytest.param(lambda: corrupt(registration(ENT_C), note=123),
                     id="registration_note_not_a_string"),
        pytest.param(lambda: corrupt(registration(ENT_C), rehash=False,
                                     record_kind="not_a_kind"),
                     id="record_kind_unknown"),
    ])
    def test_supplied_records_are_revalidated_from_field_data(self, forge):
        """``validate_record_collection`` is itself a public boundary: it
        may not assume a supplied object was ever validated."""
        bad = forge()
        with pytest.raises(ModelIntegrityError) as excinfo:
            validate_record_collection("demo-printer", {bad.record_id: bad},
                                       verify_hashes=False)
        assert excinfo.value.error_code == "MODEL_RECORD_INVALID"


# --------------------------------------------------------------- finding 2
INVALID_VIEW_CALLS = [
    pytest.param(lambda q: q.parents(ENT_B, "contains", view="as_imagined"),
                 id="parents"),
    pytest.param(lambda q: q.children(ENT_A, "contains", view="as_imagined"),
                 id="children"),
    pytest.param(lambda q: q.ancestors(ENT_B, "contains", view="as_imagined"),
                 id="ancestors"),
    pytest.param(lambda q: q.descendants(ENT_A, "contains",
                                         view="as_imagined"),
                 id="descendants"),
    pytest.param(lambda q: q.hierarchy_health("contains", view="as_imagined"),
                 id="hierarchy_health"),
]

MALFORMED_CONTEXTS = [
    pytest.param({"kind": "lifecycle_view"}, id="lifecycle_view_missing_view"),
    pytest.param({"kind": "nonsense"}, id="unknown_context_kind"),
    pytest.param("as_built", id="bare_view_string"),
    pytest.param(None, id="none"),
]


class TestQueryInputValidation:
    @pytest.mark.parametrize("call", INVALID_VIEW_CALLS)
    def test_invalid_view_literal_is_a_typed_query_error(self, tmp_path, call):
        queries = query_world(tmp_path)
        with pytest.raises(ModelQueryError) as excinfo:
            call(queries)
        assert excinfo.value.error_code == "MODEL_VIEW_INVALID"

    @pytest.mark.parametrize("context,mapping", [
        pytest.param(AS_BUILT, {"kind": "lifecycle_view", "view": "as_built"},
                     id="lifecycle_view"),
        pytest.param(VIEW_FREE, {"kind": "view_independent"},
                     id="view_independent"),
    ])
    def test_mapping_context_is_normalized_and_matches(self, tmp_path,
                                                       context, mapping):
        """A well-formed context MAPPING is normalized into the
        discriminated model and answers identically — never silently
        emptied."""
        queries = query_world(tmp_path)
        expected = queries.relationships(ENT_B, direction="both",
                                         context=context)
        actual = queries.relationships(ENT_B, direction="both",
                                       context=mapping)
        assert tuple(s.record_id for s in actual.active) == tuple(
            s.record_id for s in expected.active)
        assert actual.active != ()
        assert actual.context == context

    @pytest.mark.parametrize("context", MALFORMED_CONTEXTS)
    def test_malformed_context_is_a_typed_query_error(self, tmp_path, context):
        queries = query_world(tmp_path)
        with pytest.raises(ModelQueryError) as excinfo:
            queries.relationships(ENT_B, direction="both", context=context)
        assert excinfo.value.error_code == "MODEL_CONTEXT_INVALID"

    @pytest.mark.parametrize("direction", ["sideways", None, 3, ""])
    def test_invalid_direction_is_a_typed_query_error(self, tmp_path,
                                                      direction):
        queries = query_world(tmp_path)
        with pytest.raises(ModelQueryError) as excinfo:
            queries.relationships(ENT_B, direction=direction, context=AS_BUILT)
        assert excinfo.value.error_code == "MODEL_DIRECTION_INVALID"

    def test_no_public_query_leaks_an_untyped_exception(self, tmp_path):
        """Every public query method, fed a deliberately malformed
        argument, fails through the kernel's own error contract."""
        queries = query_world(tmp_path)
        calls = [
            ("entity(anchor)", lambda q: q.entity(None)),
            ("relationships(anchor)",
             lambda q: q.relationships(None, direction="both",
                                       context=AS_BUILT)),
            ("relationships(direction)",
             lambda q: q.relationships(ENT_A, direction="sideways",
                                       context=AS_BUILT)),
            ("relationships(context)",
             lambda q: q.relationships(ENT_A, direction="both",
                                       context="as_built")),
            ("relationships(type_name)",
             lambda q: q.relationships(ENT_A, direction="both", type_name=17,
                                       context=AS_BUILT)),
            ("parents(view)",
             lambda q: q.parents(ENT_B, "contains", view="as_imagined")),
            ("parents(type_name)",
             lambda q: q.parents(ENT_B, 17, view="as_built")),
            ("parents(anchor)",
             lambda q: q.parents(None, "contains", view="as_built")),
            ("children(view)",
             lambda q: q.children(ENT_A, "contains", view="as_imagined")),
            ("ancestors(view)",
             lambda q: q.ancestors(ENT_B, "contains", view="as_imagined")),
            ("descendants(view)",
             lambda q: q.descendants(ENT_A, "contains", view="as_imagined")),
            ("hierarchy_health(view)",
             lambda q: q.hierarchy_health("contains", view="as_imagined")),
            ("hierarchy_health(type_name)",
             lambda q: q.hierarchy_health(None, view="as_built")),
            # unhashable type names: a dict-key lookup on the caller's value
            # leaked a raw TypeError past the whole error contract
            ("relationships(unhashable type_name)",
             lambda q: q.relationships(ENT_A, direction="both", type_name=[],
                                       context=AS_BUILT)),
            ("parents(unhashable type_name)",
             lambda q: q.parents(ENT_B, [], view="as_built")),
            ("children(unhashable type_name)",
             lambda q: q.children(ENT_A, {}, view="as_built")),
            ("ancestors(unhashable type_name)",
             lambda q: q.ancestors(ENT_B, [], view="as_built")),
            ("descendants(unhashable type_name)",
             lambda q: q.descendants(ENT_A, [], view="as_built")),
            ("hierarchy_health(unhashable type_name)",
             lambda q: q.hierarchy_health({}, view="as_built")),
        ]
        leaked = []
        for label, call in calls:
            try:
                call(queries)
            except ModelKernelError:
                continue
            except BaseException as error:  # noqa: BLE001 - the finding
                leaked.append(f"{label}: {type(error).__name__}")
            else:
                leaked.append(f"{label}: no error raised")
        assert leaked == []


# --------------------------------------------------------------- finding 3
class TestRelationshipAbsenceIsUnambiguous:
    def test_registered_without_edges_differs_from_unregistered(self,
                                                                tmp_path):
        """Two different facts must not share one answer: "registered, no
        matching edges" and "never registered" both answer empty, and the
        result says which."""
        queries = ModelQueries(containment_world(tmp_path).load())
        registered = queries.relationships(ENT_A, direction="both",
                                           context=AS_BUILT)
        unregistered = queries.relationships(ENT_D, direction="both",
                                             context=AS_BUILT)
        assert registered.active == unregistered.active == ()
        assert registered.status == "registered"
        assert unregistered.status == "not_registered"
        assert registered.revision == unregistered.revision
        assert registered.revision == queries.loaded.revision
        assert unregistered.context == AS_BUILT

    def test_registered_with_edges_is_registered(self, tmp_path):
        queries = query_world(tmp_path)
        result = queries.relationships(ENT_B, direction="both",
                                       context=AS_BUILT)
        assert result.status == "registered"
        assert len(result.active) == 1


# --------------------------------------------------------------- finding 4
SUPPORTED_EXPORTS = (
    # ledger record contracts
    "EntityRegistration", "RelationshipTypeDefinition",
    "RelationshipAssertion", "RelationshipWithdrawal", "ModelRecord",
    # query/assertion context contracts
    "AssertionContext", "LifecycleViewContext", "ViewIndependentContext",
    "LifecycleView", "ReferentKind",
    # authority and evidence contracts
    "AuthorityRef", "EvidenceRef", "OwnerDeclarationEvidence",
    "ModelRecordEvidence", "IdentityBindingRecordEvidence",
    "SourceRawRecordEvidence", "TemporalOccurrenceEvidence",
    # typed errors
    "ModelKernelError", "ModelConfigurationError", "ModelIntegrityError",
    "ModelQueryError",
    # result contracts
    "ModelRevision", "EvidenceDisclosure", "RelationshipSummary",
    "LineageConflict", "RelationshipsResult", "RegistrationSummary",
    "EntityResult", "ParentResult", "ParentStatus", "TraversalAnnotation",
    "ChildEntry", "ChildrenResult", "TraversalStep", "TraversalBlock",
    "TraversalResult", "CycleReport", "ParentConflictReport",
    "HierarchyHealth",
    # operations
    "build_record", "ModelStore", "LoadedModel", "ModelQueries",
)

INTERNAL_NAMES = (
    "canonical_bytes", "canonical_payload", "canonical_sort_key",
    "compute_record_id", "compute_revision_id", "verify_record_id",
    "build_projection", "HierarchyProjection", "validate_record_collection",
)


class TestPublicPackageSurface:
    def test_supported_api_is_importable_from_the_package(self):
        """Callers import from ``backend.model_kernel``; the module layout
        below it is an implementation detail."""
        import backend.model_kernel as kernel

        assert hasattr(kernel, "__all__"), "the package declares no __all__"
        declared = set(kernel.__all__)
        missing = [name for name in SUPPORTED_EXPORTS
                   if not hasattr(kernel, name)]
        undeclared = [name for name in SUPPORTED_EXPORTS
                      if name not in declared]
        assert missing == [], f"not importable from the package: {missing}"
        assert undeclared == [], f"importable but not in __all__: {undeclared}"

    def test_internals_stay_private(self):
        """Canonicalization and hierarchy mechanics are not API: exporting
        them would make every future change a breaking one."""
        import backend.model_kernel as kernel

        declared = set(getattr(kernel, "__all__", ()))
        leaked = [name for name in INTERNAL_NAMES
                  if name in declared or hasattr(kernel, name)]
        assert leaked == [], f"internal names on the public surface: {leaked}"
