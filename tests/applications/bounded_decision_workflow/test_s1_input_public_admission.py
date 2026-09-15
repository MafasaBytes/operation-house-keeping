import base64
import copy
import hashlib
import inspect
import json
from pathlib import Path
import zlib

import pytest

import applications.bounded_decision_workflow as workflow
from applications.bounded_decision_workflow.admission import (
    _defensive_decimal_check,
)
from applications.bounded_decision_workflow.input import canonical_json_bytes


ROOT = Path(__file__).parents[3]
PACKAGE_PATH = (
    ROOT / "docs/superpowers/reports/"
    "2026-09-15-bounded-decision-workflow-candidate-package.json")
BASE_REQUEST = "24635e493d371a5e05f9b61e729457fde7397ddfb0f31bc3dbb7f14ebe19c125"
BASE_SNAPSHOT = "782332fd8dd350d6852f57d0497c2c152a031caf08ee2dfc2cb040cdde8f326f"
UNAVAILABLE_REQUEST = "20839102e285d056bc486bcfeef1bd3597e18cbe317736b12f7bbeb9335b9d14"
UNAVAILABLE_SNAPSHOT = "72c057d8707f4904cf2dfb658937a4610c56b364217ec073239530756f128ea6"


@pytest.fixture(scope="module")
def package():
    return json.loads(PACKAGE_PATH.read_bytes())


def object_bytes(package, reference):
    entry = package["objects"][reference]
    raw = zlib.decompress(base64.b64decode(entry["payload"]))
    assert len(raw) == entry["canonical_bytes"]
    assert hashlib.sha256(raw).hexdigest() == reference == entry["sha256"]
    return raw


def object_value(package, reference):
    return json.loads(object_bytes(package, reference))


def mutate(value, pointer, replacement):
    result = copy.deepcopy(value)
    parts = pointer.strip("/").split("/")
    if parts[0] in {"request", "snapshot"}:
        parts = parts[1:]
    target = result
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    if isinstance(target, list):
        target[int(parts[-1])] = replacement
    else:
        target[parts[-1]] = replacement
    return result


def diagnostic(call):
    with pytest.raises(workflow.WorkflowInputError) as error:
        call()
    return error.value.diagnostic


def test_s1_public_surface_is_narrow_and_has_eleven_request_fields():
    assert workflow.__all__ == [
        "AdmissionReview", "BUILD_LIMITS", "CurrentConditionAssessment",
        "ObservedValueAdmission", "ParsedInput", "ResourceCounts",
        "WorkflowDiagnostic", "WorkflowInputError", "WorkflowRequest",
        "admit_request_and_snapshot", "canonical_example_pair",
        "parse_request_wire", "parse_snapshot_wire",
        "RawProjectionReview", "project_request_and_snapshot",
        "PolicyReview", "assess_request_and_snapshot",
        "DecisionReview", "PriorDecisionInput", "review_request_and_snapshot",
    ]
    assert tuple(workflow.WorkflowRequest.model_fields) == (
        "actor_assertion", "application_identity",
        "current_condition_question", "observed_input_binding", "premises",
        "request_id", "requested_limits", "schema_version",
        "snapshot_commitment", "target_policy", "workflow_profile")
    assert not (ROOT / "applications/bounded_decision_workflow/__main__.py").exists()


def test_obs_1_public_result_is_admitted_and_exactly_reserializes(package):
    request = object_bytes(package, BASE_REQUEST)
    snapshot = object_bytes(package, BASE_SNAPSHOT)
    review = workflow.admit_request_and_snapshot(request, snapshot)

    assert review.current_condition.disposition == "matches"
    assert review.observed_value.status == "admitted"
    assert review.observed_value.canonical_decimal == "40"
    assert review.request_input.counts.nodes == 550
    assert review.request_input.counts.reference_occurrences == 104
    assert review.snapshot_input.counts.nodes == 2679
    assert review.snapshot_input.counts.reference_occurrences == 587
    assert workflow.canonical_example_pair(review) == (request, snapshot)


def test_obs_2_public_unavailability_never_receives_a_fallback(package):
    review = workflow.admit_request_and_snapshot(
        object_bytes(package, UNAVAILABLE_REQUEST),
        object_bytes(package, UNAVAILABLE_SNAPSHOT))
    assert review.current_condition.disposition == "unavailable"
    assert review.observed_value.status == "unavailable"
    assert review.observed_value.canonical_decimal is None
    assert review.observed_value.unavailable_reason == "observation_absent"


def test_obs_2_remaining_unavailable_forms_are_publicly_produced(
        package, tmp_path):
    from backend.constraint_evaluation import ConstraintEvaluationQueries
    from backend.source_interpretation import (
        InterpretationResolver, InterpretationStore)
    from backend.state_classification import StateClassificationQueries
    from tests.behavior_evaluation.helpers import (
        E1, PROP_TARGET, PROP_TEMP, VAR_A, VAR_B, model_store,
        semantic_queries)
    from tests.constraint_evaluation.helpers import craft_value
    from tests.model_state.helpers import (
        entity_declaration, observed_stack, prop_assertion, var_declaration)
    from tests.state_classification.helpers import (
        AS_OF, AS_OPERATED, STATE_A, condition_records, condition_sources,
        state_model)
    from tests.model_kernel.st001_slice_a_helpers import (
        pins, state_declaration, state_registration)

    baseline_request = object_value(package, BASE_REQUEST)

    def classify_at(root, *, model=None, temporal=None, bindings=None,
                    interpretations=None):
        model = model or state_model(root)[0]
        semantic = semantic_queries(
            root, model=model, temporal=temporal,
            binding_records=bindings, interpretations=interpretations)
        facade = StateClassificationQueries(ConstraintEvaluationQueries(semantic))
        return facade.state_classification(
            STATE_A, context=AS_OPERATED, as_of=AS_OF,
            condition_sources=condition_sources())

    cases = []

    unattached_root = tmp_path / "unattached"
    unattached_bindings = (
        entity_declaration(E1, "Demo entity"),
        var_declaration(VAR_A, E1, "Variable A"),
        var_declaration(VAR_B, E1, "Variable B"),
        prop_assertion(VAR_A, PROP_TEMP),
        prop_assertion(VAR_B, PROP_TEMP),
        prop_assertion(VAR_B, PROP_TARGET),
    )
    cases.append((
        "observation_not_attached",
        classify_at(unattached_root, bindings=unattached_bindings)))

    inconsistent_root = tmp_path / "inconsistent"
    inconsistent_temporal = observed_stack(inconsistent_root)
    craft_value(
        inconsistent_temporal, value_json="NaN", json_type="number")
    cases.append((
        "evidence_not_assessable",
        classify_at(inconsistent_root, temporal=inconsistent_temporal)))

    null_root = tmp_path / "null"
    null_temporal = observed_stack(null_root)
    craft_value(null_temporal, value_json="null", json_type="null")
    constraints, declarations = condition_records()
    registration = state_registration(
        subject=E1, constraints=(
            "con_" + "a" * 32, "con_" + "b" * 32), second_owner=E1)
    declaration = state_declaration(
        registration, context=AS_OPERATED,
        condition_pins=pins(declarations=declarations))
    nullable_model = model_store(
        null_root, specification_overrides={VAR_A: {"nullable": True}},
        extra_records=(*constraints, registration, declaration))
    cases.append((
        "numeric_value_absent",
        classify_at(
            null_root, model=nullable_model, temporal=null_temporal)))

    semantic_root = tmp_path / "semantic"
    empty = InterpretationResolver(InterpretationStore(
        semantic_root / "empty-interpretations").load())
    cases.append((
        "declared_semantics_not_compatible",
        classify_at(semantic_root, interpretations=empty)))

    for expected_reason, result in cases:
        assert result.constraint_evaluations[0].candidates[
            0].not_evaluated_reason == expected_reason
        snapshot = canonical_json_bytes(result.model_dump(mode="json"))
        request = copy.deepcopy(baseline_request)
        request["snapshot_commitment"] = hashlib.sha256(snapshot).hexdigest()
        review = workflow.admit_request_and_snapshot(
            canonical_json_bytes(request), snapshot)
        assert review.observed_value.status == "unavailable"
        assert review.observed_value.unavailable_reason == expected_reason
        assert review.observed_value.canonical_decimal is None


@pytest.mark.parametrize(
    ("variant_id", "expected"),
    [
        ("OBS-3-retarget", "OBSERVATION_BINDING_MISMATCH"),
        ("OBS-3-wrong-context", "OBSERVATION_BINDING_MISMATCH"),
        ("OBS-3-wrong-cutoff", "OBSERVATION_BINDING_MISMATCH"),
        ("OBS-3-wrong-revision", "PUBLIC_RECONSTRUCTION_REFUSED"),
        ("OBS-3-wrong-unit", "OBSERVATION_BINDING_MISMATCH"),
        ("OBS-3-index", "OBSERVATION_BINDING_MISMATCH"),
        ("OBS-3-forged-result", "PUBLIC_RECONSTRUCTION_REFUSED"),
        ("OBS-3-decimal-reconstruction", "PUBLIC_RECONSTRUCTION_REFUSED"),
        ("OBS-3-decimal-stale-commitment", "SNAPSHOT_COMMITMENT_MISMATCH"),
    ],
)
def test_obs_3_variants_follow_the_frozen_precedence(
        package, variant_id, expected):
    case = next(c for c in package["acceptance_cases"]
                if c["acceptance_id"] == "OBS-3")
    variant = next(v for v in case["variants"]
                   if v["variant_id"] == variant_id)
    input_ = variant["input"]
    request = object_value(package, input_["request_ref"])
    snapshot = object_value(package, input_["snapshot_ref"])
    recipe = input_.get("filesystem_setup_or_mutation", {}).get(
        "exact_mutation")
    if recipe:
        if recipe["path"].startswith("/request/"):
            request = mutate(request, recipe["path"], recipe["value"])
        else:
            snapshot = mutate(snapshot, recipe["path"], recipe["value"])

    actual = diagnostic(lambda: workflow.admit_request_and_snapshot(
        canonical_json_bytes(request), canonical_json_bytes(snapshot)))
    assert actual.code == expected
    frozen = variant["expected"]["stderr_line"]
    assert {
        "bundle_state": actual.bundle_state,
        "code": actual.code,
        "exit_code": actual.exit_code,
        "message_key": actual.message_key,
        "retry_class": actual.retry_class,
        "stage": actual.stage,
        "target": actual.target,
    } == frozen


def test_obs_3_split_cases_share_the_untouched_valid_twin(package):
    review = workflow.admit_request_and_snapshot(
        object_bytes(package, BASE_REQUEST), object_bytes(package, BASE_SNAPSHOT))
    assert review.observed_value.canonical_decimal == "40"
    case = next(c for c in package["acceptance_cases"]
                if c["acceptance_id"] == "OBS-3")
    for variant_id in (
            "OBS-3-decimal-reconstruction",
            "OBS-3-decimal-stale-commitment"):
        input_ = next(v for v in case["variants"]
                      if v["variant_id"] == variant_id)["input"]
        assert input_["nearest_valid_request_ref"] == BASE_REQUEST
        assert input_["nearest_valid_snapshot_ref"] == BASE_SNAPSHOT


def test_decimal_defense_is_subsequent_and_directly_scoped():
    assert _defensive_decimal_check("40.0", "40") == "40"
    error = diagnostic(lambda: _defensive_decimal_check("41", "40"))
    assert error.code == "OBSERVATION_DECIMAL_MISMATCH"
    assert error.target == "observed_candidate"


def test_obs_4_known_conversion_is_profile_refusal_and_twin_admits(package):
    request = object_value(package, BASE_REQUEST)
    request["observed_input_binding"]["conversion"] = {
        "kind": "caller_supplied"}
    error = diagnostic(lambda: workflow.admit_request_and_snapshot(
        canonical_json_bytes(request), object_bytes(package, BASE_SNAPSHOT)))
    assert error.code == "PROFILE_UNSUPPORTED"
    assert error.stage == "profile_cardinality_edition"

    twin = workflow.admit_request_and_snapshot(
        object_bytes(package, BASE_REQUEST), object_bytes(package, BASE_SNAPSHOT))
    assert twin.observed_value.status == "admitted"


def test_hostile_request_forms_and_valid_twins(package):
    baseline = object_value(package, BASE_REQUEST)
    snapshot = object_bytes(package, BASE_SNAPSHOT)

    extra = copy.deepcopy(baseline)
    extra["unexpected"] = True
    assert diagnostic(lambda: workflow.admit_request_and_snapshot(
        canonical_json_bytes(extra), snapshot)).code == "REQUEST_SCHEMA_INVALID"

    bool_index = copy.deepcopy(baseline)
    bool_index["observed_input_binding"]["condition_index"] = True
    assert diagnostic(lambda: workflow.admit_request_and_snapshot(
        canonical_json_bytes(bool_index), snapshot)).code == "REQUEST_SCHEMA_INVALID"

    stale_premise = copy.deepcopy(baseline)
    stale_premise["premises"]["law"]["basis"] += " altered"
    assert diagnostic(lambda: workflow.admit_request_and_snapshot(
        canonical_json_bytes(stale_premise), snapshot)).code == "REQUEST_SCHEMA_INVALID"

    relaxation = copy.deepcopy(baseline)
    relaxation["requested_limits"] = dict(workflow.BUILD_LIMITS)
    relaxation["requested_limits"]["request_wire_bytes"] += 1
    assert diagnostic(lambda: workflow.admit_request_and_snapshot(
        canonical_json_bytes(relaxation), snapshot)).code == "REQUESTED_LIMIT_RELAXATION"

    duplicate = object_bytes(package, BASE_REQUEST)
    duplicate = duplicate[:-1] + b',"schema_version":"bdw001.1"}'
    assert diagnostic(lambda: workflow.admit_request_and_snapshot(
        duplicate, snapshot)).code == "REQUEST_JSON_INVALID"

    noncanonical = object_bytes(package, BASE_REQUEST) + b"\n"
    assert diagnostic(lambda: workflow.admit_request_and_snapshot(
        noncanonical, snapshot)).code == "REQUEST_CANONICAL_FORM_REQUIRED"

    assert workflow.admit_request_and_snapshot(
        object_bytes(package, BASE_REQUEST), snapshot).observed_value.status == "admitted"


def test_build_owned_and_caller_tightened_s1_limits(package):
    snapshot = object_bytes(package, BASE_SNAPSHOT)
    wire_error = diagnostic(lambda: workflow.parse_request_wire(
        b"x" * (workflow.BUILD_LIMITS["request_wire_bytes"] + 1)))
    assert wire_error.code == "REQUEST_WIRE_LIMIT_EXCEEDED"
    assert wire_error.exit_code == 4

    long_string = object_value(package, BASE_REQUEST)
    long_string["actor_assertion"]["purpose"] = "x" * 257
    string_error = diagnostic(lambda: workflow.admit_request_and_snapshot(
        canonical_json_bytes(long_string), snapshot))
    assert string_error.code == "INPUT_RESOURCE_LIMIT_EXCEEDED"
    assert string_error.target == "input_max_string_bytes"

    tighter = object_value(package, BASE_REQUEST)
    tighter["requested_limits"] = dict(workflow.BUILD_LIMITS)
    tighter["requested_limits"]["snapshot_wire_bytes"] = len(snapshot) - 1
    tighter_error = diagnostic(lambda: workflow.admit_request_and_snapshot(
        canonical_json_bytes(tighter), snapshot))
    assert tighter_error.code == "INPUT_RESOURCE_LIMIT_EXCEEDED"
    assert tighter_error.target == "snapshot_wire_bytes"


def test_corrected_package_objects_and_s1_valid_twins_are_recoverable(package):
    assert package["measured_preparation_corpus"]["runtime_corpus_variants"] == 69
    assert len(package["objects"]) == 68
    for reference in package["objects"]:
        object_bytes(package, reference)
    for case in package["acceptance_cases"]:
        if case["implementation_slice"] != "S1":
            continue
        for variant in case["variants"]:
            recipe = variant["input"].get("public_producer_recipe")
            if recipe is not None:
                assert recipe["must_use_public_facade"] is True
                assert recipe["nearest_valid_snapshot_ref"] == BASE_SNAPSHOT

    historical_package = PACKAGE_PATH.with_name(
        "2026-09-15-bounded-decision-workflow-"
        "candidate-package-pre-obs3-decimal-correction.json")
    historical_manifest = PACKAGE_PATH.with_name(
        "2026-09-15-bounded-decision-workflow-"
        "candidate-manifest-pre-obs3-decimal-correction.json")
    assert hashlib.sha256(historical_package.read_bytes()).hexdigest() == (
        "0d3b3a6f53c465dc45a3fc44b79523bc7d51131c42b342e9f4afa62795d29365")
    assert hashlib.sha256(historical_manifest.read_bytes()).hexdigest() == (
        "6ac24d274ac5f898876a0ab28f7c250ae1413b909260e1a48eb6d3f00aa55959")


def test_s1_imports_only_public_backend_surfaces():
    admission_source = inspect.getsource(
        __import__(
            "applications.bounded_decision_workflow.admission",
            fromlist=["admission"]))
    contracts_source = inspect.getsource(
        __import__(
            "applications.bounded_decision_workflow.contracts",
            fromlist=["contracts"]))
    assert "backend.state_classification import" in admission_source
    assert "backend.constraint_evaluation import" in admission_source
    assert "backend.model_kernel import" in contracts_source
    for source in (admission_source, contracts_source):
        assert "backend.state_classification.contracts import" not in source
        assert "backend.constraint_evaluation.contracts import" not in source
        assert "backend.constraint_evaluation.decimal import" not in source
        assert "backend.state_classification.derivation import" not in source
