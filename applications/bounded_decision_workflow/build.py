"""Local build witnesses for exact replay, not executable authentication."""
import hashlib
from importlib.metadata import version
from pathlib import Path
import platform
import subprocess

from applications.bounded_decision_workflow.errors import WorkflowDiagnostic, WorkflowInputError
from applications.bounded_decision_workflow.input import BUILD_LIMITS, canonical_json_bytes

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ("backend/constraint_evaluation/__init__.py", "backend/constraint_evaluation/decimal.py",
          "backend/model_kernel/contracts.py", "backend/state_classification/__init__.py",
          "backend/state_classification/contracts.py")
LOCK = "applications/bounded_decision_workflow/requirements.lock"


def unavailable():
    return WorkflowInputError(WorkflowDiagnostic("REPLAY_BUILD_UNAVAILABLE", "commitment_public_reconstruction",
        "build_identity", "replay_build_unavailable", "restore_matching_build", 3, "absent"))


def identity():
    """Commit plus actual source/contracts/interpreter/lock; dirty code refuses.

    Existing unrelated untracked evidence is not a dirty executable. S7 separately
    proves clean-checkout recreation; this does not install or fetch anything.
    """
    def git(*args):
        return subprocess.check_output(["git", "--no-optional-locks", "-C", str(ROOT), *args],
                                       stderr=subprocess.DEVNULL, timeout=10).decode().strip()
    try:
        if platform.python_implementation() != "CPython" or platform.python_version_tuple()[:2] != ("3", "13"):
            raise unavailable()
        if git("status", "--porcelain", "--untracked-files=all", "--", "applications", "backend"):
            raise unavailable()
        commit = git("rev-parse", "HEAD")
        lock = (ROOT / LOCK).read_bytes()
        if hashlib.sha256(lock).hexdigest() != "7c87f0d7a3f12c271311cc0c33e59025e0161c37f16336901a0764b4330c0817":
            raise unavailable()
        dependencies = {}
        for line in lock.decode().splitlines():
            name, pinned = line.split("==")
            if version(name) != pinned: raise unavailable()
            dependencies[name] = pinned
        def digest(path):
            with (ROOT / path).open("rb") as stream: return hashlib.file_digest(stream, "sha256").hexdigest()
        sources = git("ls-files", "applications").splitlines()
        result = {"git_commit": commit, "application_semantic_version": "0.1.0",
            "schema_version": "bdw001.1", "workflow_profile": "hypothetical_enclosure_one_step.v1",
            "build_policy_id": "bdw-build-policy.v1", "implementation_id": "bdw.application.v1",
            "application_source_sha256": {p: digest(p) for p in sources},
            "public_module_sha256": {p: digest(p) for p in PUBLIC},
            "python": {"implementation": "CPython", "version": platform.python_version()},
            "dependencies": dependencies, "dependency_lock_sha256": hashlib.sha256(lock).hexdigest(),
            "limit_policy_sha256": hashlib.sha256(canonical_json_bytes(dict(BUILD_LIMITS))).hexdigest()}
        wire = canonical_json_bytes(result)
        return wire, hashlib.sha256(wire).hexdigest()
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        if isinstance(e, WorkflowInputError): raise
        raise unavailable() from e
