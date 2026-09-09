"""FM-001 Slice B support reachability and hostile reconstruction probes."""

import copy

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.fl001_slice_a_helpers import (
    AS_DESIGNED, FLOW_A, PORT_A, flow_withdrawal,
)
from tests.model_kernel.builders import VAR_A
from tests.model_kernel.test_flow_measurement_slice_a import (
    association, foundation, semantic, variable_port_withdrawal,
)


def _successor(record, *, supersedes, note, **changes):
    values = record.model_dump(mode="python", exclude={
        "record_kind", "schema_version", "record_id"})
    values.update(supersedes=supersedes, note=note, **changes)
    return kernel.build_record(type(record), **values)


def _wrong_observation_role():
    return kernel.ObservationRoleDeclaration(
        dimension="observation_role",
        observation_role=kernel.ObservationRoleReference(
            system_id="project_local",
            system_edition="ohk-observation-roles-1",
            code="command_target"))


def _claim_support_row(family, mode):
    records, support_value = foundation()
    support = list(support_value)
    position = {"fld": 3, "vpa": 4}[family]
    root = support[position]
    additions = []
    if mode == "current_healthy":
        pass
    elif mode == "current_conflicted":
        pinned = _successor(
            root, supersedes=(root.record_id,), note="pinned current fork")
        sibling = _successor(
            root, supersedes=(root.record_id,), note="sibling current fork")
        support[position] = pinned
        additions.extend((pinned, sibling))
    elif mode == "superseded_healthy":
        child = _successor(
            root, supersedes=(root.record_id,), note="one child")
        additions.append(child)
    elif mode == "superseded_conflicted":
        additions.extend((
            _successor(root, supersedes=(root.record_id,), note="left child"),
            _successor(root, supersedes=(root.record_id,), note="right child"),
        ))
    elif mode == "superseded_inactive":
        child = _successor(
            root, supersedes=(root.record_id,), note="withdrawn child")
        event = (flow_withdrawal(child) if family == "fld"
                 else variable_port_withdrawal(child))
        additions.extend((child, event))
    elif mode in {"withdrawn_healthy", "withdrawn_conflicted"}:
        pinned = _successor(
            root, supersedes=(root.record_id,), note="withdrawn fork tip")
        siblings = tuple(
            _successor(
                root, supersedes=(root.record_id,), note=f"active sibling {i}")
            for i in range(1 if mode == "withdrawn_healthy" else 2))
        event = (flow_withdrawal(pinned) if family == "fld"
                 else variable_port_withdrawal(pinned))
        support[position] = pinned
        additions.extend((pinned, *siblings, event))
    elif mode == "withdrawn_inactive":
        event = (flow_withdrawal(root) if family == "fld"
                 else variable_port_withdrawal(root))
        additions.append(event)
    else:  # pragma: no cover - test helper misuse
        raise AssertionError(mode)
    claim = association(tuple(support), note=f"{family} {mode}")
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (
            *records, *additions, claim)})
    result = kernel.ModelQueries(loaded).flow_measurement_assertion(
        claim.record_id)
    return next(row for row in result.support_rows
                if row.support_kind == family)


@pytest.mark.parametrize("family", ["fld", "vpa"])
def test_fld_and_vpa_reachable_support_states_have_valid_worlds(family):
    expected = {
        "current_healthy": ("current", "healthy", "exact"),
        "current_conflicted": ("current", "conflicted", "exact"),
        "superseded_healthy": ("superseded", "healthy", "exact"),
        "superseded_conflicted": ("superseded", "conflicted", "exact"),
        "superseded_inactive": ("superseded", "inactive", "unaligned"),
        "withdrawn_healthy": ("withdrawn", "healthy", "exact"),
        "withdrawn_conflicted": ("withdrawn", "conflicted", "exact"),
        "withdrawn_inactive": ("withdrawn", "inactive", "unaligned"),
    }
    for mode, values in expected.items():
        row = _claim_support_row(family, mode)
        assert (row.activity, row.containing_lineage_health,
                row.current_alignment) == values


def _vsm_support_row(mode):
    records, support_value = foundation()
    support = list(support_value)
    pinned = support[5]
    additions = []
    exact = lambda note: _successor(
        pinned, supersedes=(pinned.record_id,), note=note)
    wrong = lambda note: _successor(
        pinned, supersedes=(pinned.record_id,), note=note,
        declaration=_wrong_observation_role())
    if mode == "current_healthy_exact":
        pass
    elif mode == "current_conflicted_exact":
        additions.append(semantic(note="independent exact root"))
    elif mode == "current_conflicted_unaligned":
        values = pinned.model_dump(mode="python", exclude={
            "record_kind", "schema_version", "record_id"})
        values.update(
            declaration=_wrong_observation_role(),
            note="independent unaligned root")
        additions.append(kernel.build_record(
            kernel.VariableSemanticDeclaration, **values))
    elif mode == "superseded_healthy_exact":
        additions.append(exact("one exact child"))
    elif mode == "superseded_healthy_unaligned":
        additions.append(wrong("one unaligned child"))
    elif mode == "superseded_conflicted_exact":
        additions.extend((exact("left exact child"), exact("right exact child")))
    elif mode == "superseded_conflicted_unaligned":
        additions.extend((exact("exact child"), wrong("unaligned child")))
    else:  # pragma: no cover - test helper misuse
        raise AssertionError(mode)
    claim = association(tuple(support), note=f"vsm {mode}")
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (
            *records, *additions, claim)})
    result = kernel.ModelQueries(loaded).flow_measurement_assertion(
        claim.record_id)
    return result.support_rows[-1]


def test_vsm_reachable_support_states_have_valid_worlds():
    expected = {
        "current_healthy_exact": ("current", "healthy", "exact"),
        "current_conflicted_exact": ("current", "conflicted", "exact"),
        "current_conflicted_unaligned": (
            "current", "conflicted", "unaligned"),
        "superseded_healthy_exact": ("superseded", "healthy", "exact"),
        "superseded_healthy_unaligned": (
            "superseded", "healthy", "unaligned"),
        "superseded_conflicted_exact": (
            "superseded", "conflicted", "exact"),
        "superseded_conflicted_unaligned": (
            "superseded", "conflicted", "unaligned"),
    }
    for mode, values in expected.items():
        row = _vsm_support_row(mode)
        assert row.support_kind == "vsm"
        assert (row.activity, row.containing_lineage_health,
                row.current_alignment) == values


@pytest.mark.parametrize("values", [
    ("frg", "current", "not_applicable", "exact"),
    ("fld", "current", "inactive", "unaligned"),
    ("fld", "withdrawn", "healthy", "unaligned"),
    ("vsm", "withdrawn", "healthy", "exact"),
    ("vsm", "current", "inactive", "unaligned"),
])
def test_unreachable_support_products_reject(values):
    with pytest.raises(ValidationError):
        kernel.FlowMeasurementSupportRow(
            support_kind=values[0], record_index=0, activity=values[1],
            containing_lineage_health=values[2],
            current_alignment=values[3])


def test_public_nested_rows_enforce_local_cardinality_without_outer_material():
    with pytest.raises(ValidationError):
        kernel.FlowMeasurementEffectiveBodyGroupRow(
            group_index=0,
            representative_current_tip_index=1,
            current_tip_indices=(1,),
            participating_root_indices=(0,),
            participant_role="source",
            orientation="aligned",
            support_rows=(),
        )
    with pytest.raises(ValidationError):
        kernel.FlowMeasurementRootRow(
            root_index=0,
            root_record_index=1,
            lineage_record_indices=(1,),
            current_tip_indices=(),
            withdrawal_indices=(),
            lineage_health="healthy",
            effective_body_group_indices=(),
        )


def test_missing_duplicate_extra_reordered_and_substituted_rows_reject():
    records, support = foundation()
    claim = association(support)
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (*records, claim)})
    result = kernel.ModelQueries(loaded).flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    contract = kernel.FlowMeasurementAssociationResult
    valid = result.model_dump(mode="python")

    attacks = []
    for operation in ("missing", "duplicate", "reordered", "extra"):
        attack = copy.deepcopy(valid)
        rows = list(attack["effective_body_groups"][0]["support_rows"])
        if operation == "missing":
            rows.pop()
        elif operation == "duplicate":
            rows[-1] = rows[0]
        elif operation == "reordered":
            rows[0], rows[1] = rows[1], rows[0]
        else:
            rows.append(rows[-1])
        attack["effective_body_groups"][0]["support_rows"] = rows
        attacks.append(attack)
    substituted = copy.deepcopy(valid)
    substituted["roots"][0]["root_record_index"] = \
        substituted["effective_body_groups"][0]["support_rows"][0][
            "record_index"]
    attacks.append(substituted)
    duplicate_root = copy.deepcopy(valid)
    duplicate_root["roots"] = (*duplicate_root["roots"],
                               duplicate_root["roots"][0])
    attacks.append(duplicate_root)

    for attack in attacks:
        with pytest.raises(ValidationError):
            contract.model_validate(attack)


def test_material_revision_wrong_union_cycle_and_reordered_records_reject():
    records, support = foundation()
    claim = association(support)
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (*records, claim)})
    result = kernel.ModelQueries(loaded).flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    contract = kernel.FlowMeasurementAssociationResult
    valid = result.model_dump(mode="python")

    changed_revision = copy.deepcopy(valid)
    changed_revision["material"]["revision"]["revision_id"] = \
        "mrv_" + "0" * 64
    reordered = copy.deepcopy(valid)
    reordered_records = list(reordered["material"]["records"])
    reordered_records[0], reordered_records[1] = (
        reordered_records[1], reordered_records[0])
    reordered["material"]["records"] = reordered_records
    wrong_union = copy.deepcopy(valid)
    wrong_union["material"]["records"][0]["record_kind"] = \
        "flow_measurement_association"
    for attack in (changed_revision, reordered, wrong_union):
        with pytest.raises(ValidationError):
            contract.model_validate(attack)

    cycle = copy.deepcopy(valid)
    cycle["cycle"] = cycle
    with pytest.raises((ValidationError, ValueError), match="cycle"):
        contract.model_validate(cycle)


@pytest.mark.parametrize("bad", [True, -1, 10**9])
def test_assertion_indices_are_strict_nonboolean_and_bounded(bad):
    records, support = foundation()
    claim = association(support)
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (*records, claim)})
    result = kernel.ModelQueries(loaded).flow_measurement_assertion(
        claim.record_id)
    attack = result.model_dump(mode="python")
    attack["record_index"] = bad
    with pytest.raises(ValidationError):
        kernel.FlowMeasurementAssertionResult.model_validate(attack)
