"""Private deterministic TA serialization evidence."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from datetime import timedelta, timezone

from backend.transition_assessment import (
    DeclaredTransitionAssessmentRequest,
    assess_declared_transition_endpoints,
)
from backend.transition_assessment.preflight import _canonical_json_bytes

from tests.transition_assessment.helpers import build_world


def test_reverse_mapping_order_and_equivalent_offsets_are_byte_identical(tmp_path):
    world = build_world(tmp_path)
    first = assess_declared_transition_endpoints(world.request)
    raw = world.request.model_dump(mode="python", warnings=False)
    raw = dict(reversed(tuple(raw.items())))
    offset = timezone(timedelta(hours=2))
    raw["from_as_of"] = world.request.from_as_of.astimezone(offset)
    raw["to_as_of"] = world.request.to_as_of.astimezone(offset)
    equivalent = DeclaredTransitionAssessmentRequest.model_validate(raw)
    second = assess_declared_transition_endpoints(equivalent)
    assert _canonical_json_bytes(first) == _canonical_json_bytes(second)


def test_independent_disposable_roots_produce_identical_bytes(tmp_path):
    first = assess_declared_transition_endpoints(
        build_world(tmp_path / "first").request,
    )
    second = assess_declared_transition_endpoints(
        build_world(tmp_path / "second").request,
    )
    assert _canonical_json_bytes(first) == _canonical_json_bytes(second)


def test_hash_seeds_produce_identical_private_bytes(tmp_path):
    script = (
        "import hashlib,tempfile; from pathlib import Path; "
        "from tests.transition_assessment.helpers import build_world; "
        "from backend.transition_assessment import assess_declared_transition_endpoints; "
        "from backend.transition_assessment.preflight import _canonical_json_bytes; "
        "result=assess_declared_transition_endpoints("
        "build_world(Path(tempfile.mkdtemp(prefix='ta-seed-'))).request); "
        "data=_canonical_json_bytes(result); "
        "print(len(data),hashlib.sha256(data).hexdigest())"
    )
    outputs = []
    for seed in ("1", "7", "19", "101", "12345"):
        environment = dict(os.environ, PYTHONHASHSEED=seed,
                           PYTHONDONTWRITEBYTECODE="1")
        completed = subprocess.run(
            [sys.executable, "-c", script],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
        outputs.append(completed.stdout.strip())
    assert outputs[0] == outputs[1] == outputs[2]
    assert len(set(outputs)) == 1


def test_t74_all_admitted_float_representatives_are_seed_stable():
    script = (
        "from backend.transition_assessment.preflight import _canonical_json_bytes; "
        "print(_canonical_json_bytes([0.0,-0.0,1794.0,1.25,1e-20,1e20]).decode())"
    )
    outputs = []
    for seed in ("1", "7", "19", "101", "12345"):
        completed = subprocess.run(
            [sys.executable, "-c", script],
            check=True,
            capture_output=True,
            text=True,
            env=dict(os.environ, PYTHONHASHSEED=seed,
                     PYTHONDONTWRITEBYTECODE="1"),
        )
        outputs.append(completed.stdout.strip())
    assert outputs == [
        "[0.0,-0.0,1794.0,1.25,1e-20,1e+20]",
    ] * 5


def test_t57_invalid_alignment_permutation_refuses_across_hash_seeds():
    script = (
        "import tempfile; from pathlib import Path; "
        "from tests.transition_assessment.helpers import build_world; "
        "from backend.transition_assessment import ("
        "DeclaredTransitionAssessmentRequest,TransitionAssessmentInputError,"
        "assess_declared_transition_endpoints); "
        "w=build_world(Path(tempfile.mkdtemp(prefix='ta-invalid-seed-'))); "
        "raw=w.request.model_dump(mode='python',warnings=False); "
        "raw['evidence_alignments']=tuple(reversed(raw['evidence_alignments'])); "
        "q=DeclaredTransitionAssessmentRequest.model_validate(raw); "
        "\ntry: assess_declared_transition_endpoints(q)"
        "\nexcept TransitionAssessmentInputError as e: print(e.error_code)"
    )
    outputs = []
    for seed in ("1", "7", "19", "101", "12345"):
        completed = subprocess.run(
            [sys.executable, "-c", script], check=True,
            capture_output=True, text=True,
            env=dict(os.environ, PYTHONHASHSEED=seed,
                     PYTHONDONTWRITEBYTECODE="1"),
        )
        outputs.append(completed.stdout.strip())
    assert outputs == ["TRANSITION_ASSESSMENT_INPUT_INVALID"] * 5


def test_private_bytes_are_not_public_identity_and_have_no_newline(tmp_path):
    import backend.transition_assessment as package

    result = assess_declared_transition_endpoints(build_world(tmp_path).request)
    data = _canonical_json_bytes(result)
    assert not data.endswith(b"\n")
    assert "_canonical_json_bytes" not in package.__all__
    assert len(hashlib.sha256(data).hexdigest()) == 64


def test_recursive_nested_mapping_order_does_not_change_bytes(tmp_path):
    world = build_world(tmp_path)
    original = assess_declared_transition_endpoints(world.request)

    def reverse(value):
        if type(value) is dict:
            return {
                key: reverse(item)
                for key, item in reversed(tuple(value.items()))
            }
        if type(value) in (tuple, list):
            return type(value)(reverse(item) for item in value)
        return value

    raw = reverse(world.request.model_dump(mode="python", warnings=False))
    rebuilt = DeclaredTransitionAssessmentRequest.model_validate(raw)
    permuted = assess_declared_transition_endpoints(rebuilt)
    assert _canonical_json_bytes(permuted) == _canonical_json_bytes(original)
