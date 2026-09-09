"""FM-001 Slice B support reachability and hostile reconstruction probes."""

import copy
from datetime import datetime, timedelta, timezone, tzinfo
import hashlib
import os
import subprocess
import sys
from unittest.mock import patch

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
import backend.model_kernel.flow_measurement_results as fm_results_module
import backend.model_kernel.result_revalidation as revalidation_module
from backend.model_kernel.store import validate_record_collection
from backend.model_kernel.flow_measurement_results import (
    _reject_scalar_subclasses,
)
from backend.model_kernel.result_revalidation import inspect_supplied_graph
from tests.model_kernel.fl001_slice_a_helpers import (
    AS_DESIGNED, FLOW_A, PORT_A, flow_withdrawal,
)
from tests.model_kernel.builders import VAR_A
from tests.model_kernel.test_flow_measurement_slice_a import (
    association, foundation, semantic, variable_port_withdrawal,
)
from tests.model_kernel.fm001_slice_b_reproduction import witness_bytes


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
    ("vsm", "current", "healthy", "unaligned"),
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
    unrelated_support = copy.deepcopy(valid)
    unrelated_support["effective_body_groups"][0]["support_rows"][0][
        "record_index"] = 0
    attacks.append(unrelated_support)
    duplicate_root = copy.deepcopy(valid)
    duplicate_root["roots"] = (*duplicate_root["roots"],
                               duplicate_root["roots"][0])
    attacks.append(duplicate_root)

    for attack in attacks:
        with pytest.raises(ValidationError):
            contract.model_validate(attack)

    constructed = contract.model_construct(**{
        **valid, "declaration_conclusion": "inactive"})
    with pytest.raises(ValidationError):
        contract.model_validate(constructed)


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


def test_hostile_repr_at_every_query_scalar_boundary_remains_typed():
    records, _ = foundation()
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in records})
    queries = kernel.ModelQueries(loaded)

    class Hostile:
        def __repr__(self):
            raise RuntimeError("secret repr executed")

    class HostileContext(type(AS_DESIGNED)):
        def model_dump(self, *args, **kwargs):
            raise RuntimeError("context callback executed")

    hostile_context = HostileContext.model_validate(
        AS_DESIGNED.model_dump(mode="python"))

    calls = (
        lambda: queries.flow_measurement_association(
            Hostile(), VAR_A, PORT_A, AS_DESIGNED, "aligned"),
        lambda: queries.flow_measurement_association(
            FLOW_A, Hostile(), PORT_A, AS_DESIGNED, "aligned"),
        lambda: queries.flow_measurement_association(
            FLOW_A, VAR_A, Hostile(), AS_DESIGNED, "aligned"),
        lambda: queries.flow_measurement_association(
            FLOW_A, VAR_A, PORT_A, AS_DESIGNED, Hostile()),
        lambda: queries.flow_measurement_association(
            FLOW_A, VAR_A, PORT_A, hostile_context, "aligned"),
        lambda: queries.flow_measurement_associations_for_flow(
            Hostile(), context=AS_DESIGNED),
        lambda: queries.flow_measurement_associations_for_variable(
            Hostile(), context=AS_DESIGNED),
        lambda: queries.flow_measurement_associations_at_port(
            Hostile(), context=AS_DESIGNED),
        lambda: queries.flow_measurement_assertion(Hostile()),
    )
    for call in calls:
        with pytest.raises(kernel.ModelQueryError):
            call()

    malformed_calls = (
        lambda: queries.flow_measurement_association(
            "flow", VAR_A, PORT_A, AS_DESIGNED, "aligned"),
        lambda: queries.flow_measurement_association(
            FLOW_A, "variable", PORT_A, AS_DESIGNED, "aligned"),
        lambda: queries.flow_measurement_association(
            FLOW_A, VAR_A, "port", AS_DESIGNED, "aligned"),
        lambda: queries.flow_measurement_association(
            FLOW_A, VAR_A, PORT_A, {"kind": "unknown"}, "aligned"),
        lambda: queries.flow_measurement_association(
            FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "sideways"),
        lambda: queries.flow_measurement_associations_for_flow(
            "flow", context=AS_DESIGNED),
        lambda: queries.flow_measurement_associations_for_variable(
            "variable", context=AS_DESIGNED),
        lambda: queries.flow_measurement_associations_at_port(
            "port", context=AS_DESIGNED),
        lambda: queries.flow_measurement_associations_for_flow(
            FLOW_A, context=None),
        lambda: queries.flow_measurement_assertion("fma_invalid"),
    )
    for call in malformed_calls:
        with pytest.raises(kernel.ModelQueryError):
            call()


def test_hostile_container_model_and_datetime_subclasses_reject_before_callbacks():
    records, support = foundation()
    claim = association(support)
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (*records, claim)})
    result = kernel.ModelQueries(loaded).flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    valid = result.model_dump(mode="python")
    contract = kernel.FlowMeasurementAssociationResult

    class HostileDict(dict):
        def get(self, *args, **kwargs):
            raise RuntimeError("caller mapping executed")

    class HostileMaterial(kernel.ModelQueryMaterial):
        __module__ = "backend.hostile"

        def model_dump(self, *args, **kwargs):
            raise RuntimeError("caller model executed")

    class DynamicallyHostileMaterial(kernel.ModelQueryMaterial):
        def __getattribute__(self, name):
            if name == "model_dump":
                raise RuntimeError("caller dynamic dump executed")
            return super().__getattribute__(name)

    armed = [False]

    class HostileModelMetaclass(type(kernel.ModelQueryMaterial)):
        def __getattribute__(cls, name):
            if armed[0] and name in {"__module__", "__name__"}:
                raise RuntimeError("caller metaclass executed")
            return super().__getattribute__(name)

    class MetaclassHostileMaterial(
            kernel.ModelQueryMaterial, metaclass=HostileModelMetaclass):
        pass

    class HostileDatetime(datetime):
        def astimezone(self, *args, **kwargs):
            raise RuntimeError("caller time executed")

    hostile_material = HostileMaterial.model_validate(valid["material"])
    dynamically_hostile_material = DynamicallyHostileMaterial.model_validate(
        valid["material"])
    metaclass_hostile_material = MetaclassHostileMaterial.model_validate(
        valid["material"])
    raw_time = valid["material"]["records"][0]["recorded_at"]
    hostile_time = HostileDatetime(
        raw_time.year, raw_time.month, raw_time.day, raw_time.hour,
        raw_time.minute, raw_time.second, raw_time.microsecond,
        tzinfo=raw_time.tzinfo, fold=raw_time.fold)
    hostile_time_payload = copy.deepcopy(valid)
    hostile_time_payload["material"]["records"][0]["recorded_at"] = hostile_time

    for attack in (
        HostileDict(valid),
        {**valid, "material": hostile_material},
        {**valid, "material": dynamically_hostile_material},
        hostile_time_payload,
    ):
        with pytest.raises((ValidationError, ValueError)):
            contract.model_validate(attack)
    armed[0] = True
    try:
        with pytest.raises((ValidationError, ValueError)):
            contract.model_validate({
                **valid, "material": metaclass_hostile_material})
    finally:
        armed[0] = False

    missing_fields_set = object.__new__(kernel.ModelQueryMaterial)
    object.__setattr__(missing_fields_set, "__dict__", {})
    with pytest.raises((ValidationError, ValueError)):
        contract.model_validate({"material": missing_fields_set})

    timezone_callbacks = []

    class HostileTimezone(tzinfo):
        def utcoffset(self, value):
            timezone_callbacks.append("utcoffset")
            return timedelta(0)

        def dst(self, value):
            timezone_callbacks.append("dst")
            return timedelta(0)

        def tzname(self, value):
            timezone_callbacks.append("tzname")
            return "UTC"

    raw_time = valid["material"]["records"][0]["recorded_at"]
    hostile_timezone_payload = copy.deepcopy(valid)
    hostile_timezone_payload["material"]["records"][0]["recorded_at"] = datetime(
        raw_time.year, raw_time.month, raw_time.day, raw_time.hour,
        raw_time.minute, raw_time.second, raw_time.microsecond,
        tzinfo=HostileTimezone(), fold=raw_time.fold)
    with pytest.raises((ValidationError, ValueError)):
        contract.model_validate(hostile_timezone_payload)
    assert timezone_callbacks == []

    class HostileTimedelta(timedelta):
        pass

    class HostileTimezoneName(str):
        pass

    for embedded_timezone in (
        timezone(HostileTimedelta(hours=1)),
        timezone(timedelta(hours=1), HostileTimezoneName("caller name")),
    ):
        embedded_payload = copy.deepcopy(valid)
        embedded_payload["material"]["records"][0]["recorded_at"] = datetime(
            raw_time.year, raw_time.month, raw_time.day, raw_time.hour,
            raw_time.minute, raw_time.second, raw_time.microsecond,
            tzinfo=embedded_timezone, fold=raw_time.fold)
        with pytest.raises((ValidationError, ValueError)):
            contract.model_validate(embedded_payload)


def test_exact_models_reject_hostile_stored_dict_and_forged_fields_set():
    records, support = foundation()
    claim = association(support)
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (*records, claim)})
    result = kernel.ModelQueries(loaded).flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    contract = kernel.FlowMeasurementAssociationResult

    # Valid twin: ordinary exact public instances reconstruct successfully.
    assert contract.model_validate(result) == result

    class HostileDict(dict):
        def values(self):
            raise RuntimeError("caller stored values executed")

    hostile_material = result.material.model_copy()
    object.__setattr__(
        hostile_material, "__dict__", HostileDict(vars(hostile_material)))
    with pytest.raises((ValidationError, ValueError)):
        contract.model_validate({
            **result.model_dump(mode="python"),
            "material": hostile_material,
        })

    forged_fields = result.model_copy()
    object.__setattr__(
        forged_fields, "__pydantic_fields_set__",
        {*type(forged_fields).model_fields, "hidden"})
    with pytest.raises((ValidationError, ValueError)):
        contract.model_validate(forged_fields)

    class HostileSet(set):
        pass

    hostile_fields = result.model_copy()
    object.__setattr__(
        hostile_fields, "__pydantic_fields_set__",
        HostileSet(type(hostile_fields).model_fields))
    with pytest.raises((ValidationError, ValueError)):
        contract.model_validate(hostile_fields)

    armed = [False]

    class HostileFieldName(str):
        __hash__ = str.__hash__

        def __eq__(self, other):
            if armed[0]:
                raise RuntimeError("caller field-name equality executed")
            return super().__eq__(other)

    field_names = set(type(result).model_fields)
    field_names.remove("material")
    field_names.add(HostileFieldName("material"))
    hostile_name = result.model_copy()
    object.__setattr__(
        hostile_name, "__pydantic_fields_set__", field_names)
    armed[0] = True
    try:
        with pytest.raises((ValidationError, ValueError)):
            contract.model_validate(hostile_name)
    finally:
        armed[0] = False


@pytest.mark.parametrize("module, inspector", [
    (fm_results_module, _reject_scalar_subclasses),
    (revalidation_module, inspect_supplied_graph),
])
def test_shared_container_preflight_cost_is_bounded_by_unique_graph(
        monkeypatch, module, inspector):
    built_in_tuple = tuple
    calls = []

    class CountingTupleMeta(type):
        def __call__(cls, value=()):
            calls.append(value)
            return built_in_tuple(value)

    class CountingTuple(tuple, metaclass=CountingTupleMeta):
        pass

    monkeypatch.setattr(module, "tuple", CountingTuple, raising=False)
    shared = [None] * 1_000
    inspector([shared] * 1_000)
    assert len(calls) == 2


def test_malformed_material_rejects_before_fm_derivation_is_attempted():
    records, support = foundation()
    claim = association(support)
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in (*records, claim)})
    result = kernel.ModelQueries(loaded).flow_measurement_association(
        FLOW_A, VAR_A, PORT_A, AS_DESIGNED, "aligned")
    assert kernel.FlowMeasurementAssociationResult.model_validate(result) == result

    attack = result.model_dump(mode="python")
    attack["material"]["revision"]["revision_id"] = "mrv_" + "0" * 64

    def forbidden(*args, **kwargs):
        raise AssertionError("FM derivation ran before material reconstruction")

    with patch.object(fm_results_module, "_exact_payload", forbidden):
        with pytest.raises(ValidationError):
            kernel.FlowMeasurementAssociationResult.model_validate(attack)


def test_deterministic_witness_is_stable_across_order_and_five_hash_seeds():
    expected = witness_bytes(reverse=False)
    assert len(expected) == 245_676
    assert hashlib.sha256(expected).hexdigest() == \
        "b65567aae97c7dc3c6913a12ab52c78e329a99fedcb40bfa1b9bc36f69a40839"
    assert witness_bytes(reverse=True) == expected
    for index, seed in enumerate(("0", "1", "7", "41", "random")):
        environment = dict(os.environ)
        environment["PYTHONHASHSEED"] = seed
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        command = [
            sys.executable, "-m",
            "tests.model_kernel.fm001_slice_b_reproduction"]
        if index % 2:
            command.append("--reverse")
        completed = subprocess.run(
            command, check=True, capture_output=True, env=environment)
        assert completed.stdout.rstrip(b"\n") == expected
        assert completed.stderr == b""
