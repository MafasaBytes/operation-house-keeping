"""Crash-isolation harness for extraction worker subprocesses.

The subprocess boundary is a **crash-isolation boundary, not a complete
security sandbox**: it protects the service from parser crashes, hangs, and
runaway memory, and it narrows what the worker can see (fresh scratch dir,
minimal environment, no store access). It does not defend against a
deliberately malicious parser payload escaping the OS user.

Guarantees provided here:

- the payload is materialized as a controlled temporary copy with a
  sanitized filename and its checksum re-verified before parsing;
- the worker is invoked without a shell, with a minimal environment
  (no inherited secrets), cwd inside the scratch dir;
- payload size and wall-clock limits are enforced (configurable; defaults
  120 s / 100 MB per spec), plus RLIMIT_AS on Linux when configured;
- on timeout the whole process tree is terminated (process group on POSIX;
  on Windows only the direct child is killed and no memory cap exists —
  documented gap);
- scratch files are always cleaned up; outputs are returned as bytes so the
  worker never touches the raw store.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from backend.data_sources.contracts import ExtractionError
from backend.data_sources.provenance import payload_checksum

_SAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]")
_TAIL_BYTES = 4096
_MAX_OUTPUT_BYTES = 256 * 1024 * 1024


class WorkerLimits(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    timeout_seconds: float = Field(default=120.0, gt=0)
    max_payload_bytes: int = Field(default=100_000_000, gt=0)
    max_memory_bytes: int | None = Field(default=None)  # POSIX RLIMIT_AS only


class WorkerOutcome(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: Literal["ok", "crashed", "timeout"]
    returncode: int | None
    stdout_tail: str
    stderr_tail: str
    outputs: dict[str, bytes] = Field(default_factory=dict)


def _sanitize_filename(name: str) -> str:
    candidate = _SAFE_CHARS.sub("_", Path(name).name)
    return candidate.strip("._") or "payload.bin"


def _minimal_env(scratch_home: Path) -> dict[str, str]:
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(scratch_home),
        "LANG": "C.UTF-8",
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
    }
    if sys.platform == "win32":  # pragma: no cover - exercised on Windows only
        for key in ("SYSTEMROOT", "TEMP", "TMP", "PATHEXT"):
            if key in os.environ:
                env[key] = os.environ[key]
    return env


def invoke_worker(
    build_argv: Callable[[Path, Path], list[str]],
    payload: bytes,
    expected_checksum: str,
    limits: WorkerLimits,
    scratch_root: Path | None = None,
    payload_filename: str = "payload.bin",
) -> WorkerOutcome:
    if len(payload) > limits.max_payload_bytes:
        raise ExtractionError(
            "EXTRACT_PAYLOAD_TOO_LARGE",
            f"payload of {len(payload)} bytes exceeds the configured limit "
            f"of {limits.max_payload_bytes} bytes",
        )

    if scratch_root is not None:
        scratch_root.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="worker-", dir=scratch_root))
    try:
        input_path = scratch / _sanitize_filename(payload_filename)
        input_path.write_bytes(payload)
        if payload_checksum(input_path.read_bytes()) != expected_checksum:
            raise ExtractionError(
                "EXTRACT_PAYLOAD_INTEGRITY",
                "materialized payload copy does not match the expected "
                "checksum; refusing to parse",
            )
        output_dir = scratch / "out"
        output_dir.mkdir()

        argv = build_argv(input_path, output_dir)
        popen_kwargs: dict = dict(
            args=argv,
            cwd=scratch,
            env=_minimal_env(scratch),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
        if sys.platform != "win32":
            popen_kwargs["start_new_session"] = True
            if limits.max_memory_bytes is not None:
                import resource

                cap = limits.max_memory_bytes

                def _cap_memory():  # pragma: no cover - runs in the child
                    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

                popen_kwargs["preexec_fn"] = _cap_memory

        process = subprocess.Popen(**popen_kwargs)
        try:
            stdout, stderr = process.communicate(timeout=limits.timeout_seconds)
        except subprocess.TimeoutExpired:
            _terminate_tree(process)
            stdout, stderr = process.communicate()
            return WorkerOutcome(
                status="timeout",
                returncode=process.returncode,
                stdout_tail=_tail(stdout),
                stderr_tail=_tail(stderr),
                outputs={},
            )

        if process.returncode != 0:
            return WorkerOutcome(
                status="crashed",
                returncode=process.returncode,
                stdout_tail=_tail(stdout),
                stderr_tail=_tail(stderr),
                outputs={},
            )

        return WorkerOutcome(
            status="ok",
            returncode=0,
            stdout_tail=_tail(stdout),
            stderr_tail=_tail(stderr),
            outputs=_collect_outputs(output_dir),
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def _terminate_tree(process: subprocess.Popen) -> None:
    if sys.platform != "win32":
        import signal

        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:  # pragma: no cover - already gone
            pass
    else:  # pragma: no cover - exercised on Windows only
        process.kill()  # direct child only; documented Windows gap


def _tail(data: bytes | None) -> str:
    if not data:
        return ""
    return data[-_TAIL_BYTES:].decode("utf-8", errors="replace")


def _collect_outputs(output_dir: Path) -> dict[str, bytes]:
    outputs: dict[str, bytes] = {}
    total = 0
    for path in sorted(output_dir.rglob("*")):
        if not path.is_file():
            continue
        data = path.read_bytes()
        total += len(data)
        if total > _MAX_OUTPUT_BYTES:
            raise ExtractionError(
                "EXTRACT_WORKER_OUTPUT_TOO_LARGE",
                "worker produced more output than the harness is willing to "
                "collect",
            )
        outputs[str(path.relative_to(output_dir))] = data
    return outputs
