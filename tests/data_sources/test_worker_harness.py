"""Tests for the crash-isolation worker harness.

Uses fake worker scripts, so no CAD toolchain is required.
"""

import json
import sys
import time

import pytest

from backend.data_sources.contracts import ExtractionError
from backend.data_sources.extractors.worker_harness import (
    WorkerLimits,
    invoke_worker,
)
from backend.data_sources.provenance import payload_checksum

PAYLOAD = b"ISO-10303-21;\nfake step content\n"


def write_fake_worker(tmp_path, body: str):
    script = tmp_path / "fake_worker.py"
    script.write_text(
        "import json, os, pathlib, sys, time\n"
        "input_path = pathlib.Path(sys.argv[1])\n"
        "output_dir = pathlib.Path(sys.argv[2])\n" + body,
        "utf-8",
    )
    return script


def argv_for(script):
    def build(input_path, output_dir):
        return [sys.executable, str(script), str(input_path), str(output_dir)]

    return build


SMALL_LIMITS = WorkerLimits(timeout_seconds=15.0, max_payload_bytes=1_000_000)


class TestHappyPath:
    def test_outputs_collected_and_scratch_cleaned(self, tmp_path):
        script = write_fake_worker(
            tmp_path,
            "data = input_path.read_bytes()\n"
            "(output_dir / 'result.json').write_text(json.dumps({'n': len(data)}))\n"
            "(output_dir / 'scene.glb').write_bytes(b'GLB' + data[:4])\n",
        )
        scratch_root = tmp_path / "scratch"
        outcome = invoke_worker(
            argv_for(script),
            payload=PAYLOAD,
            expected_checksum=payload_checksum(PAYLOAD),
            limits=SMALL_LIMITS,
            scratch_root=scratch_root,
        )
        assert outcome.status == "ok"
        assert json.loads(outcome.outputs["result.json"]) == {"n": len(PAYLOAD)}
        assert outcome.outputs["scene.glb"].startswith(b"GLB")
        assert not any(scratch_root.iterdir())  # temp fully cleaned

    def test_payload_materialized_under_sanitized_name(self, tmp_path):
        script = write_fake_worker(
            tmp_path,
            "(output_dir / 'name.txt').write_text(input_path.name)\n",
        )
        outcome = invoke_worker(
            argv_for(script),
            payload=PAYLOAD,
            expected_checksum=payload_checksum(PAYLOAD),
            limits=SMALL_LIMITS,
            scratch_root=tmp_path / "scratch",
            payload_filename="../../evil name!!.step",
        )
        materialized = outcome.outputs["name.txt"].decode()
        assert "/" not in materialized and ".." not in materialized
        assert materialized.endswith(".step")


class TestGuards:
    def test_checksum_mismatch_refuses_to_spawn(self, tmp_path):
        script = write_fake_worker(tmp_path, "raise SystemExit(0)\n")
        with pytest.raises(ExtractionError) as excinfo:
            invoke_worker(
                argv_for(script),
                payload=PAYLOAD,
                expected_checksum="sha256:" + "0" * 64,
                limits=SMALL_LIMITS,
                scratch_root=tmp_path / "scratch",
            )
        assert excinfo.value.error_code == "EXTRACT_PAYLOAD_INTEGRITY"

    def test_oversized_payload_refuses_to_spawn(self, tmp_path):
        script = write_fake_worker(tmp_path, "raise SystemExit(0)\n")
        limits = WorkerLimits(timeout_seconds=5.0, max_payload_bytes=8)
        with pytest.raises(ExtractionError) as excinfo:
            invoke_worker(
                argv_for(script),
                payload=PAYLOAD,
                expected_checksum=payload_checksum(PAYLOAD),
                limits=limits,
                scratch_root=tmp_path / "scratch",
            )
        assert excinfo.value.error_code == "EXTRACT_PAYLOAD_TOO_LARGE"


class TestFailureIsolation:
    def test_crash_is_reported_not_raised(self, tmp_path):
        script = write_fake_worker(
            tmp_path, "print('meltdown detail', file=sys.stderr)\nsys.exit(3)\n"
        )
        outcome = invoke_worker(
            argv_for(script),
            payload=PAYLOAD,
            expected_checksum=payload_checksum(PAYLOAD),
            limits=SMALL_LIMITS,
            scratch_root=tmp_path / "scratch",
        )
        assert outcome.status == "crashed"
        assert outcome.returncode == 3
        assert "meltdown detail" in outcome.stderr_tail

    def test_timeout_kills_the_worker(self, tmp_path):
        script = write_fake_worker(tmp_path, "time.sleep(30)\n")
        limits = WorkerLimits(timeout_seconds=1.0, max_payload_bytes=1_000_000)
        started = time.monotonic()
        outcome = invoke_worker(
            argv_for(script),
            payload=PAYLOAD,
            expected_checksum=payload_checksum(PAYLOAD),
            limits=limits,
            scratch_root=tmp_path / "scratch",
        )
        elapsed = time.monotonic() - started
        assert outcome.status == "timeout"
        assert elapsed < 10  # the process tree was terminated, not awaited

    def test_scratch_cleaned_even_after_crash(self, tmp_path):
        script = write_fake_worker(tmp_path, "sys.exit(1)\n")
        scratch_root = tmp_path / "scratch"
        invoke_worker(
            argv_for(script),
            payload=PAYLOAD,
            expected_checksum=payload_checksum(PAYLOAD),
            limits=SMALL_LIMITS,
            scratch_root=scratch_root,
        )
        assert not any(scratch_root.iterdir())


class TestEnvironmentHygiene:
    def test_minimal_env_without_secrets(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SECRET_TOKEN", "hunter2")
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "hunter2")
        script = write_fake_worker(
            tmp_path,
            "(output_dir / 'env.json').write_text(json.dumps(sorted(os.environ)))\n",
        )
        outcome = invoke_worker(
            argv_for(script),
            payload=PAYLOAD,
            expected_checksum=payload_checksum(PAYLOAD),
            limits=SMALL_LIMITS,
            scratch_root=tmp_path / "scratch",
        )
        env_keys = json.loads(outcome.outputs["env.json"])
        assert "SECRET_TOKEN" not in env_keys
        assert "AWS_SECRET_ACCESS_KEY" not in env_keys
        assert "PATH" in env_keys
