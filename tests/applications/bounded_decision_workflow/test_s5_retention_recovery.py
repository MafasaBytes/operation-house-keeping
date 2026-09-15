"""S5 real filesystem tests; no module CLI or replay-computation claim."""
import json
from dataclasses import asdict
import hashlib
import multiprocessing
import os
from pathlib import Path
import signal
import subprocess

import pytest

import applications.bounded_decision_workflow as workflow
from tests.applications.bounded_decision_workflow.test_s1_input_public_admission import (
    PACKAGE_PATH, BASE_REQUEST, BASE_SNAPSHOT, object_bytes,
)
from tests.applications.bounded_decision_workflow.test_s4_fixture_correction import variant
from applications.bounded_decision_workflow import retention


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


@pytest.fixture
def files():
    p = json.loads(PACKAGE_PATH.read_bytes())
    v = variant(p, "REV-1-omitted-prior")
    request, snapshot = object_bytes(p, BASE_REQUEST), object_bytes(p, BASE_SNAPSHOT)
    # Exact prepared examples test byte retention, not production evaluation.
    return {"request.json": request, "snapshot.json": snapshot,
            "resolved-input.json": canonical({"request": json.loads(request), "snapshot": json.loads(snapshot), "prior": None}),
            "result.json": object_bytes(p, v["expected"]["result_ref"]),
            "trace.json": object_bytes(p, v["expected"]["trace_ref"]),
            "build.json": canonical({"preparation_example": True, "not_executable_authentication": True})}


def test_real_publish_verify_and_capture(tmp_path, files):
    dest = tmp_path / "result"
    receipt = workflow.publish_bundle(dest, files)
    assert receipt.integrity_state == "complete_bundle"
    assert receipt.durability == "fsync_sequence_returned"
    verified = workflow.verify_bundle(dest)
    assert verified.integrity_state == "complete_bundle"
    assert verified.durability == "not_established_by_verification"
    assert verified.captured["result.json"] == files["result.json"]
    assert workflow.capture_file(dest / "request.json", kind="request").data == files["request.json"]
    assert (dest.stat().st_mode & 0o777) == 0o700
    assert all((p.stat().st_mode & 0o777) == 0o600 for p in dest.iterdir())


@pytest.mark.parametrize("kind", ["file", "directory", "symlink"])
def test_output_collision_is_preserved(tmp_path, files, kind):
    dest = tmp_path / "occupied"
    if kind == "file": dest.write_bytes(b"existing")
    elif kind == "directory": dest.mkdir(); (dest / "owner.txt").write_bytes(b"existing")
    else: dest.symlink_to(tmp_path / "missing")
    with pytest.raises(workflow.WorkflowInputError) as exc:
        workflow.publish_bundle(dest, files)
    assert exc.value.diagnostic.code == "OUTPUT_COLLISION"
    assert dest.is_symlink() if kind == "symlink" else dest.exists()


def test_incomplete_is_read_only(tmp_path):
    bundle = tmp_path / "unfinished"; bundle.mkdir()
    (bundle / "request.json").write_bytes(b"{}")
    inspected = workflow.verify_bundle(bundle)
    assert inspected.integrity_state == "incomplete_bundle"
    assert inspected.diagnostic.code == "BUNDLE_INCOMPLETE"
    assert list(bundle.iterdir()) == [bundle / "request.json"]


def diagnostic(code):
    p = json.loads(PACKAGE_PATH.read_bytes())
    return next(d for d in p["diagnostic_catalogue"] if d["code"] == code)


def expect(call, code):
    with pytest.raises(workflow.WorkflowInputError) as exc:
        call()
    assert asdict(exc.value.diagnostic) == diagnostic(code)
    return exc.value


@pytest.mark.parametrize("attack,code", [
    ("component", "PATH_COMPONENT_UNSAFE"), ("final", "PATH_FINAL_SYMLINK"),
    ("traversal", "PATH_COMPONENT_UNSAFE"), ("dot", "PATH_COMPONENT_UNSAFE"),
    ("fifo", "PATH_SPECIAL_FILE"), ("directory", "PATH_SPECIAL_FILE"),
])
def test_real_hostile_paths_and_valid_twin(tmp_path, attack, code):
    good = tmp_path / "input.json"; good.write_bytes(b"{}")
    bad = tmp_path / "bad"
    if attack == "component":
        bad.symlink_to(tmp_path, target_is_directory=True); path = bad / good.name
    elif attack == "final": bad.symlink_to(good); path = bad
    elif attack == "traversal": path = str(tmp_path) + "/../" + tmp_path.name + "/input.json"
    elif attack == "dot": path = str(tmp_path) + "/./input.json"
    elif attack == "fifo": os.mkfifo(bad); path = bad
    else: bad.mkdir(); path = bad
    expect(lambda: workflow.capture_file(path, kind="request"), code)
    assert workflow.capture_file(good, kind="request").data == b"{}"


def test_actual_drvfs_refused_and_ext4_accepted(tmp_path):
    # A clean S7 checkout may itself be on ext4. Nominate a read-only file on an
    # actual unsupported mount; never infer filesystem type from checkout role.
    nominated = os.environ.get("BDW_UNSUPPORTED_FILE")
    probe = Path(nominated) if nominated else PACKAGE_PATH
    kind = subprocess.check_output(['findmnt', '-T', str(probe), '-n', '-o', 'FSTYPE'], text=True).strip()
    if kind in {'ext4', 'xfs'}:
        if nominated: pytest.fail('BDW_UNSUPPORTED_FILE must be on an unsupported filesystem')
        pytest.skip('nominate BDW_UNSUPPORTED_FILE to exercise a real unsupported mount')
    expect(lambda: workflow.capture_file(probe, kind="request"), "FILESYSTEM_UNSUPPORTED")
    good = tmp_path / "small.json"; good.write_bytes(b"{}")
    assert workflow.capture_file(good, kind="request").data == b"{}"


@pytest.mark.parametrize("name", ["UPPER", "_leading", "a" * 129])
def test_output_basename_rejected_before_creation(tmp_path, files, name):
    expect(lambda: workflow.publish_bundle(tmp_path / name, files), "OUTPUT_BASENAME_INVALID")
    assert not (tmp_path / name).exists()


def test_actual_input_mutation_and_read_once_capture(tmp_path):
    path = tmp_path / "input.json"; path.write_bytes(b"{}")
    def mutate(stage, name):
        if stage == "after_read": path.write_bytes(b'{"changed":true}')
    expect(lambda: workflow.capture_file(path, kind="request", fault=mutate), "INPUT_CHANGED_DURING_READ")
    captured = workflow.capture_file(path, kind="request")
    path.write_bytes(b"{}"); assert captured.data == b'{"changed":true}'
    assert captured.sha256 == hashlib.sha256(captured.data).hexdigest()


def test_wire_limit_plus_one_and_hardlink_identity(tmp_path, monkeypatch):
    path = tmp_path / "large.json"
    cap = workflow.BUILD_LIMITS["request_wire_bytes"]
    path.write_bytes(b"x" * cap)
    twin = tmp_path / "hardlink.json"; os.link(path, twin)
    assert workflow.capture_file(path, kind="request").metadata[-1] == 2
    assert workflow.capture_file(twin, kind="request").data == b"x" * cap
    path.write_bytes(b"x" * (cap + 10))
    original, reads = os.read, []
    def tracked(fd, n):
        b = original(fd, n); reads.append(len(b)); return b
    monkeypatch.setattr(retention.os, "read", tracked)
    expect(lambda: workflow.capture_file(path, kind="request"), "INPUT_WIRE_LIMIT_EXCEEDED")
    assert sum(reads) == cap + 1


EVENTS = [(name, stage) for name in retention.COMPLETE_FILES + ("manifest.json",)
          for stage in ("create", "write", "flush", "file_fsync",
                        "manifest_before_rename" if name == "manifest.json" else "rename")]
FAULT_CODES = {"create": "RETENTION_CREATE_FAILED", "write": "RETENTION_WRITE_FAILED",
               "flush": "RETENTION_FLUSH_FAILED", "file_fsync": "RETENTION_FILE_FSYNC_FAILED",
               "rename": "RETENTION_RENAME_FAILED", "manifest_before_rename": "RETENTION_MANIFEST_FAILED"}


@pytest.mark.parametrize("name,stage", EVENTS)
def test_each_pre_manifest_io_failure_preserves_incomplete(tmp_path, files, name, stage):
    output = tmp_path / "interrupted"
    def fail(event, filename):
        if event == stage and filename == name: raise OSError("injected storage failure")
    expect(lambda: workflow.publish_bundle(output, files, fault=fail), FAULT_CODES[stage])
    assert output.is_dir() and not (output / "manifest.json").exists()
    before = sorted(p.name for p in output.iterdir())
    inspected = workflow.verify_bundle(output)
    assert inspected.integrity_state == "incomplete_bundle"
    assert sorted(p.name for p in output.iterdir()) == before
    expect(lambda: workflow.publish_bundle(output, files), "OUTPUT_COLLISION")
    assert workflow.publish_bundle(tmp_path / "valid-twin", files).integrity_state == "complete_bundle"


def _kill_at(output, files, name, stage):
    def kill(event, filename):
        if event == stage and filename == name: os.kill(os.getpid(), signal.SIGKILL)
    workflow.publish_bundle(output, files, fault=kill)


@pytest.mark.parametrize("name,stage", EVENTS)
def test_real_process_interruption_at_every_publication_boundary(tmp_path, files, name, stage):
    output = tmp_path / "killed"
    process = multiprocessing.get_context("fork").Process(target=_kill_at, args=(output, files, name, stage))
    process.start(); process.join(10)
    if process.is_alive(): process.kill(); process.join(); pytest.fail("child did not reach fault seam")
    assert process.exitcode == -signal.SIGKILL
    assert output.exists() and not (output / "manifest.json").exists()
    assert workflow.verify_bundle(output).integrity_state == "incomplete_bundle"


@pytest.mark.parametrize("stage,code", [("directory_fsync", "RETENTION_DIR_FSYNC_FAILED"),
                                       ("parent_fsync", "RETENTION_PARENT_FSYNC_FAILED")])
def test_post_manifest_failures_are_complete_visible_not_durable(tmp_path, files, stage, code):
    path = tmp_path / "uncertain"
    def fail(event, name):
        if event == stage: raise OSError("fsync failure")
    expect(lambda: workflow.publish_bundle(path, files, fault=fail), code)
    checked = workflow.verify_bundle(path)
    assert checked.integrity_state == "complete_bundle"
    assert checked.durability == "not_established_by_verification"
    # S5 recovery primitive: republish captured bytes to a NEW path. Not S6 replay.
    payload = {n: b for n, b in checked.captured.items() if n != "manifest.json"}
    fresh = workflow.publish_bundle(tmp_path / "new-output", payload)
    assert fresh.captured["result.json"] == checked.captured["result.json"]


def _race(output, files, barrier, queue):
    barrier.wait(10)
    try:
        result = workflow.publish_bundle(output, files)
        queue.put(result.integrity_state)
    except workflow.WorkflowInputError as e: queue.put(e.diagnostic.code)


def test_real_concurrent_publishers_have_one_owner(tmp_path, files):
    context = multiprocessing.get_context("fork")
    barrier, queue = context.Barrier(2), context.Queue()
    path = tmp_path / "contended"
    processes = [context.Process(target=_race, args=(path, files, barrier, queue)) for _ in range(2)]
    for p in processes: p.start()
    for p in processes:
        p.join(10)
        if p.is_alive(): p.kill(); p.join(); pytest.fail("publisher hung")
        assert p.exitcode == 0
    assert sorted(queue.get(timeout=2) for _ in range(2)) == ["OUTPUT_COLLISION", "complete_bundle"]
    queue.close(); queue.join_thread()
    assert workflow.verify_bundle(path).captured["result.json"] == files["result.json"]


@pytest.mark.parametrize("mutation", ["extra_name", "traversal", "absolute", "duplicate_key", "digest", "length_bool", "build", "semantic", "missing", "extra_file", "noncanonical"])
def test_manifest_attacks_and_valid_twin(tmp_path, files, mutation):
    path = tmp_path / "attack"
    workflow.publish_bundle(path, files)
    original = (path / "manifest.json").read_bytes(); manifest = json.loads(original)
    if mutation in ("extra_name", "traversal", "absolute"):
        name = {"extra_name": "evil.json", "traversal": "../outside.json", "absolute": "/outside.json"}[mutation]
        manifest["files"][name] = {"bytes": 2, "sha256": hashlib.sha256(b"{}").hexdigest()}
    elif mutation == "digest": manifest["files"]["result.json"]["sha256"] = "0" * 64
    elif mutation == "length_bool": manifest["files"]["result.json"]["bytes"] = True
    elif mutation == "build": manifest["build_identity"] = "0" * 64
    elif mutation == "semantic": manifest["semantic_commitments"]["result.json"] = "0" * 64
    elif mutation == "missing": (path / "result.json").unlink()
    elif mutation == "extra_file": (path / "extra.json").write_bytes(b"{}")
    data = canonical(manifest)
    if mutation == "duplicate_key": data = data[:-1] + b',"schema_version":"bdw001.1"}'
    if mutation == "noncanonical": data += b"\n"
    (path / "manifest.json").write_bytes(data)
    checked = workflow.verify_bundle(path)
    assert checked.integrity_state == "incomplete_bundle"
    assert asdict(checked.diagnostic) == diagnostic("MANIFEST_INVALID")
    assert workflow.publish_bundle(tmp_path / "twin", files).integrity_state == "complete_bundle"


def test_verifier_never_follows_member_symlink(tmp_path, files):
    path = tmp_path / "bundle"; workflow.publish_bundle(path, files)
    (path / "result.json").unlink(); (path / "result.json").symlink_to(PACKAGE_PATH)
    expect(lambda: workflow.verify_bundle(path), "PATH_FINAL_SYMLINK")


def test_refusal_bundle_contains_no_partial_conclusion(tmp_path):
    payload = {"diagnostic.json": canonical(diagnostic("MANIFEST_INVALID")),
               "input-metadata.json": canonical({"wire_bytes_at_least": 32769, "full_digest": None}),
               "build.json": canonical({"preparation_example": True})}
    published = workflow.publish_bundle(tmp_path / "refusal", payload, bundle_kind="refusal")
    assert published.bundle_kind == "refusal"
    verified = workflow.verify_bundle(tmp_path / "refusal")
    assert verified.integrity_state == "complete_bundle" and verified.bundle_kind == "refusal"
    assert "result.json" not in verified.captured and "trace.json" not in verified.captured


def test_bad_or_oversized_output_never_creates_directory(tmp_path, files):
    bad = dict(files, **{"result.json": b"x" * (workflow.BUILD_LIMITS["output_result_bytes"] + 1)})
    expect(lambda: workflow.publish_bundle(tmp_path / "oversized", bad), "OUTPUT_LIMIT_EXCEEDED")
    assert not (tmp_path / "oversized").exists()
    bad = dict(files, **{"result.json": b'{"x":0,"x":1}'})
    expect(lambda: workflow.publish_bundle(tmp_path / "duplicate", bad), "MANIFEST_INVALID")
    assert not (tmp_path / "duplicate").exists()


def test_directory_creation_failure_has_no_bundle(tmp_path, files):
    def fail(stage, name):
        if stage == "directory_create": raise PermissionError("denied")
    with pytest.raises(workflow.WorkflowInputError) as caught:
        workflow.publish_bundle(tmp_path / "absent", files, fault=fail)
    expected = dict(diagnostic("RETENTION_CREATE_FAILED"), bundle_state="absent")
    assert asdict(caught.value.diagnostic) == expected
    assert not (tmp_path / "absent").exists()


def test_post_manifest_process_death_does_not_establish_durability(tmp_path, files):
    dest = tmp_path / "visible"
    child = multiprocessing.get_context("fork").Process(
        target=_kill_at, args=(dest, files, "manifest.json", "published"))
    child.start(); child.join(10)
    if child.is_alive(): child.kill(); child.join(); pytest.fail("child hung")
    assert child.exitcode == -signal.SIGKILL
    verified = workflow.verify_bundle(dest)
    assert verified.integrity_state == "complete_bundle"
    assert verified.durability == "not_established_by_verification"


def test_injected_final_file_is_not_overwritten(tmp_path, files):
    path = tmp_path / "raced"
    def insert(stage, name):
        if stage == "rename" and name == "result.json":
            (path / name).write_bytes(b"do not overwrite")
    expect(lambda: workflow.publish_bundle(path, files, fault=insert), "RETENTION_RENAME_FAILED")
    assert (path / "result.json").read_bytes() == b"do not overwrite"
    assert workflow.verify_bundle(path).integrity_state == "incomplete_bundle"


def test_symlink_parent_and_unsupported_output_parent(tmp_path, files):
    link = tmp_path / "link"; link.symlink_to(tmp_path)
    expect(lambda: workflow.publish_bundle(link / "bad", files), "PATH_COMPONENT_UNSAFE")
    # The checkout can be ext4. Never infer an unsupported output parent from it
    # or risk creating a failed-probe bundle among source/evidence files.
    parent = os.environ.get('BDW_UNSUPPORTED_OUTPUT_PARENT')
    if parent is None:
        pytest.skip('nominate an isolated BDW_UNSUPPORTED_OUTPUT_PARENT')
    kind = subprocess.check_output(['findmnt', '-T', parent, '-n', '-o', 'FSTYPE'], text=True).strip()
    assert kind not in {'ext4', 'xfs'}, 'output probe must use an actual unsupported mount'
    output = Path(parent) / "must-not-create-s5-test-output"
    assert not output.exists()
    expect(lambda: workflow.publish_bundle(output, files), "FILESYSTEM_UNSUPPORTED")
    assert not output.exists()


@pytest.mark.parametrize("metadata", [
    {}, {"created_at_utc": "bad", "filesystem": "ext4"},
    {"created_at_utc": "2026-09-15T00:00:00", "filesystem": "ext4"},
    {"created_at_utc": "2026-09-15T00:00:00+01:00", "filesystem": "ext4"},
    {"created_at_utc": "2026-09-15T00:00:00+00:00", "filesystem": "9p"},
])
def test_manifest_metadata_is_typed_not_trusted(tmp_path, files, metadata):
    path = tmp_path / "bad-meta"; workflow.publish_bundle(path, files)
    manifest = json.loads((path / "manifest.json").read_bytes())
    manifest["run_metadata"] = metadata
    (path / "manifest.json").write_bytes(canonical(manifest))
    assert workflow.verify_bundle(path).diagnostic.code == "MANIFEST_INVALID"


@pytest.mark.parametrize("boundary", ["nodes", "depth", "trace_rows", "string"])
def test_complete_output_boundaries_with_valid_twins(tmp_path, files, boundary):
    name = "result.json"
    if boundary == "nodes":
        # Object + array + 1022 scalars = 1024 nodes (keys are not nodes).
        good, bad = {"v": [0] * 1022}, {"v": [0] * 1023}
    elif boundary == "depth":
        good = 0
        for _ in range(31): good = {"v": good}
        bad = {"v": good}
    elif boundary == "trace_rows":
        name = "trace.json"
        good, bad = {"decision_rows": [None] * 64}, {"decision_rows": [None] * 65}
    else:
        good, bad = {"v": "x" * 256}, {"v": "x" * 257}
    assert workflow.publish_bundle(tmp_path / "twin", dict(files, **{name: canonical(good)})).integrity_state == "complete_bundle"
    expect(lambda: workflow.publish_bundle(tmp_path / "too-large", dict(files, **{name: canonical(bad)})), "OUTPUT_LIMIT_EXCEEDED")
    assert not (tmp_path / "too-large").exists()


def test_verified_bytes_can_feed_accepted_admission_and_review(tmp_path, files):
    path = tmp_path / "source"; workflow.publish_bundle(path, files)
    before = {p.name: p.read_bytes() for p in path.iterdir()}
    captured = workflow.verify_bundle(path).captured
    build = "1" * 64  # Same-author synthetic assertion, not executable authenticity.
    original = workflow.review_request_and_snapshot(files["request.json"], files["snapshot.json"], build_identity=build)
    restored = workflow.review_request_and_snapshot(captured["request.json"], captured["snapshot.json"], build_identity=build)
    assert restored.review_bytes == original.review_bytes
    assert restored.trace_bytes == original.trace_bytes
    assert len(restored.reevaluation["decision_rows"]) == 22
    assert {p.name: p.read_bytes() for p in path.iterdir()} == before
    with pytest.raises(TypeError): captured["result.json"] = b"{}"


def test_integrity_does_not_authenticate_or_recompute(tmp_path, files, monkeypatch):
    # A self-consistent caller-created result is retained bytes, not S4 admission.
    altered = dict(files, **{"result.json": canonical({"not_an_admitted_result": True})})
    path = tmp_path / "self-consistent"; workflow.publish_bundle(path, altered)
    def prohibited(*args, **kwargs): raise AssertionError("S5 cannot recompute")
    monkeypatch.setattr(workflow, "review_request_and_snapshot", prohibited)
    verified = workflow.verify_bundle(path)
    assert verified.captured["result.json"] == altered["result.json"]
    assert verified.integrity_state == "complete_bundle"


def test_file_descriptors_close_on_success_and_refusal(tmp_path, files):
    before = set(os.listdir("/proc/self/fd"))
    for i in range(4):
        dest = tmp_path / f"bundle-{i}"; workflow.publish_bundle(dest, files)
        workflow.verify_bundle(dest)
        expect(lambda: workflow.publish_bundle(dest, files), "OUTPUT_COLLISION")
    assert set(os.listdir("/proc/self/fd")) == before


def padded_object(size):
    values = []
    # Bounded short strings, independently size the canonical object exactly.
    while len(canonical({"v": values + ["x" * 250, ""]})) <= size:
        values.append("x" * 250)
    values.append("")
    values[-1] = "x" * (size - len(canonical({"v": values})))
    data = canonical({"v": values})
    assert len(data) == size and max(map(len, values)) <= 256
    return data


def test_per_file_and_total_bundle_bytes_are_separate(tmp_path, files):
    cap = workflow.BUILD_LIMITS["output_result_bytes"]
    good = dict(files, **{"result.json": padded_object(cap)})
    assert workflow.publish_bundle(tmp_path / "exact", good).integrity_state == "complete_bundle"
    bad = dict(good, **{"result.json": padded_object(cap + 1)})
    expect(lambda: workflow.publish_bundle(tmp_path / "over", bad), "OUTPUT_LIMIT_EXCEEDED")
    aggregate = dict(files)
    for name, limit in (("request.json", "request_wire_bytes"), ("snapshot.json", "snapshot_wire_bytes"),
                        ("resolved-input.json", "resolved_input_bytes")):
        aggregate[name] = padded_object(workflow.BUILD_LIMITS[limit])
    assert sum(map(len, aggregate.values())) > workflow.BUILD_LIMITS["retention_bundle_bytes"]
    expect(lambda: workflow.publish_bundle(tmp_path / "aggregate", aggregate), "OUTPUT_LIMIT_EXCEEDED")
    assert not (tmp_path / "aggregate").exists()


def test_input_read_fault_closes_descriptor_and_returns_path_diagnostic(tmp_path):
    path = tmp_path / "io.json"; path.write_bytes(b"{}")
    before = set(os.listdir("/proc/self/fd"))
    def fail(stage, name):
        if stage == "read": raise OSError("read fault")
    expect(lambda: workflow.capture_file(path, kind="request", fault=fail), "PATH_COMPONENT_UNSAFE")
    assert set(os.listdir("/proc/self/fd")) == before
    assert workflow.capture_file(path, kind="request").data == b"{}"
