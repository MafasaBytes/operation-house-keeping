import json
import subprocess
import sys
import pytest

from applications.bounded_decision_workflow.measurement_delivery import (
    FILES, PAYLOAD_FILES, MeasurementDeliveryError,
    publish_measurement_bundle, replay_measurement_bundle,
    verify_measurement_bundle,
)


def payloads():
    return {name: json.dumps({"name": name}, sort_keys=True,
                             separators=(",", ":")).encode() for name in PAYLOAD_FILES}


def test_publish_verify_replay_is_seven_file_no_overwrite(tmp_path):
    values = payloads()
    bundle = publish_measurement_bundle(tmp_path / "bundle", values)
    assert tuple(sorted(p.name for p in bundle.path.iterdir())) == tuple(sorted(FILES))
    assert verify_measurement_bundle(bundle.path).manifest_sha256 == bundle.manifest_sha256
    with pytest.raises(MeasurementDeliveryError) as error:
        publish_measurement_bundle(bundle.path, values)
    assert error.value.code == "OUTPUT_COLLISION"
    assert replay_measurement_bundle(bundle.path, build=values["build.json"],
                                     policy=values["policy.json"],
                                     result=values["result.json"],
                                     trace=values["trace.json"]).path == bundle.path
    command = subprocess.run(
        [sys.executable, "-m", "applications.bounded_decision_workflow.measurement_cli",
         "verify", "--bundle", str(bundle.path)], capture_output=True, text=True,
        check=False)
    assert command.returncode == 0
    assert command.stdout.strip() == bundle.manifest_sha256


def test_manifest_last_and_incomplete_bundle_are_honest(tmp_path):
    values = payloads()
    incomplete = tmp_path / "incomplete"
    incomplete.mkdir()
    for name in PAYLOAD_FILES[:2]:
        (incomplete / name).write_bytes(values[name])
    with pytest.raises(MeasurementDeliveryError) as error:
        verify_measurement_bundle(incomplete)
    assert error.value.code == "BUNDLE_INCOMPLETE"


def test_replay_recomputes_semantics_and_rejects_cross_profile_substitution(tmp_path):
    values = payloads()
    bundle = publish_measurement_bundle(tmp_path / "bundle", values)
    changed = values["result.json"].replace(b"result.json", b"other.json")
    with pytest.raises(MeasurementDeliveryError) as error:
        replay_measurement_bundle(bundle.path, build=values["build.json"],
                                  policy=values["policy.json"], result=changed,
                                  trace=values["trace.json"])
    assert error.value.code == "REPLAY_SEMANTIC_MISMATCH"
