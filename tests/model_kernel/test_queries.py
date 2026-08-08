"""MK-001 query surface: strict context equality, typed misuse errors,
direction filters, determinism, revision embedding."""

import pytest

from backend.model_kernel.contracts import ModelQueryError
from backend.model_kernel.queries import ModelQueries

from tests.model_kernel.builders import (
    AS_BUILT,
    AS_DESIGNED,
    ENT_A,
    ENT_B,
    ENT_C,
    VIEW_FREE,
    assertion,
    contains_type,
    containment_world,
    instance_of_type,
    registration,
    store_with,
)


def mixed_world(tmp_path):
    """contains A→B (as_built) plus instance_of B→C (view-independent)."""
    contains = contains_type()
    instance_of = instance_of_type()
    store = store_with(
        tmp_path, contains, instance_of, registration(ENT_A),
        registration(ENT_B), registration(ENT_C, kind="type_definition"),
        assertion(contains, source=ENT_A, target=ENT_B),
        assertion(instance_of, source=ENT_B, target=ENT_C, context=VIEW_FREE))
    return ModelQueries(store.load())


class TestEntity:
    def test_registered_and_not_registered(self, tmp_path):
        queries = ModelQueries(containment_world(tmp_path).load())
        hit = queries.entity(ENT_A)
        assert hit.status == "registered"
        assert hit.registration.anchor.anchor_id == ENT_A
        miss = queries.entity(ENT_C)
        assert miss.status == "not_registered"
        assert miss.registration is None
        with pytest.raises(ModelQueryError):
            queries.entity("extruder")


class TestStrictContextEquality:
    def test_no_union_across_context_arms(self, tmp_path):
        queries = mixed_world(tmp_path)
        built = queries.relationships(ENT_B, direction="both",
                                      context=AS_BUILT)
        assert [s.type_name for s in built.active] == ["contains"]
        free = queries.relationships(ENT_B, direction="both",
                                     context=VIEW_FREE)
        assert [s.type_name for s in free.active] == ["instance_of"]

    def test_views_partition_lifecycle_assertions(self, tmp_path):
        kind = contains_type()
        store = containment_world(
            tmp_path,
            assertion(kind, source=ENT_A, target=ENT_B, context=AS_DESIGNED),
            assertion(kind, source=ENT_A, target=ENT_B, context=AS_BUILT))
        queries = ModelQueries(store.load())
        for context in (AS_DESIGNED, AS_BUILT):
            result = queries.relationships(ENT_B, direction="incoming",
                                           context=context)
            assert len(result.active) == 1
            assert result.active[0].context == context

    def test_all_five_lifecycle_views_are_separate_partitions(self, tmp_path):
        """Acceptance case: the five views are five partitions, not a
        spectrum — one edge asserted in every view is answered by exactly
        one assertion per view, with no bleed between them."""
        from backend.model_kernel.contracts import LifecycleViewContext

        views = ("as_designed", "as_built", "as_configured", "as_operated",
                 "as_maintained")
        contexts = [LifecycleViewContext(kind="lifecycle_view", view=view)
                    for view in views]
        kind = contains_type()
        store = containment_world(
            tmp_path,
            *[assertion(kind, source=ENT_A, target=ENT_B, context=context)
              for context in contexts])
        queries = ModelQueries(store.load())
        seen = set()
        for context in contexts:
            result = queries.relationships(ENT_B, direction="incoming",
                                           context=context)
            assert len(result.active) == 1, context.view
            assert result.active[0].context == context
            seen.add(result.active[0].record_id)
        assert len(seen) == 5  # five distinct assertions, never shared

    def test_type_context_mismatch_is_typed_error_not_empty(self, tmp_path):
        queries = mixed_world(tmp_path)
        with pytest.raises(ModelQueryError) as excinfo:
            queries.relationships(ENT_B, direction="both",
                                  type_name="instance_of", context=AS_BUILT)
        assert excinfo.value.error_code == "MODEL_CONTEXT_MISMATCH"
        with pytest.raises(ModelQueryError) as excinfo:
            queries.relationships(ENT_B, direction="both",
                                  type_name="contains", context=VIEW_FREE)
        assert excinfo.value.error_code == "MODEL_CONTEXT_MISMATCH"
        with pytest.raises(ModelQueryError) as excinfo:
            queries.relationships(ENT_B, direction="both",
                                  type_name="no_such", context=AS_BUILT)
        assert excinfo.value.error_code == "MODEL_UNKNOWN_TYPE"


class TestDirectionsAndDisclosure:
    def test_direction_filters_and_inverse_labels(self, tmp_path):
        queries = mixed_world(tmp_path)
        outgoing = queries.relationships(ENT_A, direction="outgoing",
                                         context=AS_BUILT)
        incoming = queries.relationships(ENT_B, direction="incoming",
                                         context=AS_BUILT)
        assert len(outgoing.active) == len(incoming.active) == 1
        summary = incoming.active[0]
        assert summary.forward_label == "contains"
        assert summary.inverse_label == "is contained in"
        none_here = queries.relationships(ENT_A, direction="incoming",
                                          context=AS_BUILT)
        assert none_here.active == ()

    def test_evidence_verification_labels(self, tmp_path):
        from backend.model_kernel.contracts import (
            IdentityBindingRecordEvidence,
            ModelRecordEvidence,
        )

        kind = contains_type()
        reg_a = registration(ENT_A)
        evidence = (
            ModelRecordEvidence(kind="model_record",
                                record_id=reg_a.record_id),
            IdentityBindingRecordEvidence(
                kind="identity_binding_record", binding_set_id="demo-printer",
                record_id="anc_" + "e" * 64),
        )
        store = store_with(tmp_path, kind, reg_a, registration(ENT_B),
                           assertion(kind, evidence=evidence))
        result = ModelQueries(store.load()).relationships(
            ENT_A, direction="outgoing", context=AS_BUILT)
        labels = {d.ref.kind: d.verification
                  for d in result.active[0].evidence}
        assert labels["model_record"] == "verified_in_revision"
        assert labels["identity_binding_record"] == "declared_reference"

    def test_repeated_calls_are_deterministic(self, tmp_path):
        queries = mixed_world(tmp_path)
        first = queries.relationships(ENT_B, direction="both",
                                      context=AS_BUILT)
        second = queries.relationships(ENT_B, direction="both",
                                       context=AS_BUILT)
        assert first == second
        assert first.revision.record_count == 7
