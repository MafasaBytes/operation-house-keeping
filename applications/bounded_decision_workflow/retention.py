"""S5 Linux local-file boundary. Integrity is not authenticity or computation.

Paths come from the application caller, never from retained JSON. Verification
captures fixed files once and does not run S1–S4 or trust them as admitted results.
No CLI, automatic deletion/resume, source access or replay engine lives here.
"""
from contextlib import contextmanager
import ctypes
import errno
from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json
import os
import re
import stat
import sys
from types import MappingProxyType

from applications.bounded_decision_workflow.errors import WorkflowDiagnostic, WorkflowInputError
from applications.bounded_decision_workflow.input import BUILD_LIMITS, canonical_json_bytes, _count, _pairs

COMPLETE_FILES = ("request.json", "snapshot.json", "resolved-input.json", "result.json", "trace.json", "build.json")
REFUSAL_FILES = ("diagnostic.json", "input-metadata.json", "build.json")
KNOWN_FILES = frozenset(COMPLETE_FILES + REFUSAL_FILES + ("manifest.json",))
MANIFEST_FIELDS = frozenset(("schema_version", "bundle_kind", "operation", "build_identity",
                             "files", "semantic_commitments", "run_metadata"))

_DIAGNOSTICS = {
    "PATH_COMPONENT_UNSAFE": (5, "path_file_safety", "cli_path", "choose_safe_path", "absent"),
    "PATH_FINAL_SYMLINK": (5, "path_file_safety", "cli_path", "replace_with_regular_file", "absent"),
    "PATH_SPECIAL_FILE": (5, "path_file_safety", "cli_path", "replace_with_regular_file", "absent"),
    "FILESYSTEM_UNSUPPORTED": (5, "path_file_safety", "filesystem", "choose_supported_ext4_xfs", "absent"),
    "OUTPUT_BASENAME_INVALID": (5, "path_file_safety", "output_dir", "choose_valid_basename", "absent"),
    "INPUT_CHANGED_DURING_READ": (3, "path_file_safety", "input_file", "retry_with_stable_file", "absent"),
    "INPUT_WIRE_LIMIT_EXCEEDED": (4, "wire_resource", "input_file", "reduce_input", "optional_refusal"),
    "OUTPUT_COLLISION": (5, "collision", "output_dir", "choose_new_output", "absent"),
    "RETENTION_CREATE_FAILED": (6, "retention_io", "bundle", "choose_writable_supported_parent", "incomplete"),
    "RETENTION_WRITE_FAILED": (6, "retention_io", "bundle_file", "repair_storage_and_use_new_output", "incomplete"),
    "RETENTION_FLUSH_FAILED": (6, "retention_io", "bundle_file", "repair_storage_and_use_new_output", "incomplete"),
    "RETENTION_FILE_FSYNC_FAILED": (6, "retention_io", "bundle_file", "repair_storage_and_use_new_output", "incomplete"),
    "RETENTION_RENAME_FAILED": (6, "retention_io", "bundle_file", "repair_storage_and_use_new_output", "incomplete"),
    "RETENTION_MANIFEST_FAILED": (6, "retention_io", "manifest.json", "repair_storage_and_use_new_output", "incomplete"),
    "RETENTION_DIR_FSYNC_FAILED": (6, "retention_io", "bundle", "verify_or_replay_to_new_output", "complete_visible_durability_unknown"),
    "RETENTION_PARENT_FSYNC_FAILED": (6, "retention_io", "output_parent", "verify_or_replay_to_new_output", "complete_visible_durability_unknown"),
    "BUNDLE_INCOMPLETE": (3, "commitment_public_reconstruction", "bundle", "inspect_or_resubmit_to_new_output", "absent"),
    "MANIFEST_INVALID": (3, "commitment_public_reconstruction", "manifest.json", "restore_authentic_bundle", "absent"),
    "OUTPUT_LIMIT_EXCEEDED": (4, "output_resource", "result_or_trace", "reduce_input", "optional_refusal"),
}


def _error(code, *, state=None):
    exit_code, stage, target, retry, bundle = _DIAGNOSTICS[code]
    return WorkflowInputError(WorkflowDiagnostic(code, stage, target, code.lower(), retry,
                                                exit_code, bundle if state is None else state))


def _event(hook, stage, name):
    if hook is not None:
        hook(stage, name)


@dataclass(frozen=True, slots=True)
class CapturedFile:
    data: bytes
    sha256: str
    metadata: tuple


@dataclass(frozen=True, slots=True)
class BundleInspection:
    integrity_state: str
    bundle_kind: str | None
    durability: str
    captured: object
    diagnostic: WorkflowDiagnostic | None
    manifest_sha256: str | None


def _libc():
    if sys.platform != "linux":
        raise _error("FILESYSTEM_UNSUPPORTED")
    return ctypes.CDLL(None, use_errno=True)


def _filesystem(fd):
    # Resolve the open descriptor's mount, not a caller path or ext-family magic
    # (ext2/ext3/ext4 share a statfs magic). Fixed kernel metadata, no input paths.
    if sys.platform != "linux": raise _error("FILESYSTEM_UNSUPPORTED")
    try:
        metadata = []
        for path in (f"/proc/self/fdinfo/{fd}", "/proc/self/mountinfo"):
            with open(path, "rb") as stream:
                data = stream.read(BUILD_LIMITS["resolved_input_bytes"] + 1)
            if len(data) > BUILD_LIMITS["resolved_input_bytes"]: raise ValueError("mount metadata too large")
            metadata.append(data.decode("ascii"))
        mount = next(line.split()[1] for line in metadata[0].splitlines() if line.startswith("mnt_id:"))
        row = next(line for line in metadata[1].splitlines() if line.split()[0] == mount)
        kind = row.split(" - ", 1)[1].split()[0]
        if kind not in ("ext4", "xfs"): raise ValueError("unsupported mount")
        return kind
    except (OSError, ValueError, IndexError, StopIteration) as e:
        raise _error("FILESYSTEM_UNSUPPORTED") from e


def _parts(path):
    value = os.fspath(path)
    if not isinstance(value, str) or not value or "\0" in value:
        raise _error("PATH_COMPONENT_UNSAFE")
    pieces = value.split("/")
    absolute = value.startswith("/")
    if absolute: pieces = pieces[1:]
    if not pieces or any(p in ("", ".", "..") for p in pieces):
        raise _error("PATH_COMPONENT_UNSAFE")
    return absolute, pieces


@contextmanager
def _directory(absolute, pieces):
    fd = os.open("/" if absolute else ".", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for piece in pieces:
            try:
                child = os.open(piece, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
            except OSError as e:
                raise _error("PATH_COMPONENT_UNSAFE") from e
            os.close(fd); fd = child
        yield fd
    finally:
        os.close(fd)


def _metadata(s):
    return (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_nlink)


def _read_at(parent, name, cap, hook=None):
    try:
        before = os.stat(name, dir_fd=parent, follow_symlinks=False)
        if stat.S_ISLNK(before.st_mode): raise _error("PATH_FINAL_SYMLINK")
        if not stat.S_ISREG(before.st_mode): raise _error("PATH_SPECIAL_FILE")
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=parent)
    except FileNotFoundError:
        raise
    except OSError as e:
        if e.errno == errno.ELOOP: raise _error("PATH_FINAL_SYMLINK") from e
        raise _error("PATH_COMPONENT_UNSAFE") from e
    try:
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode): raise _error("PATH_SPECIAL_FILE")
        if _metadata(opened) != _metadata(before): raise _error("INPUT_CHANGED_DURING_READ")
        _filesystem(fd)
        chunks, count = [], 0
        while count <= cap:
            _event(hook, "read", name)
            chunk = os.read(fd, min(8192, cap + 1 - count))
            if not chunk: break
            chunks.append(chunk); count += len(chunk)
        _event(hook, "after_read", name)
        if _metadata(os.fstat(fd)) != _metadata(opened): raise _error("INPUT_CHANGED_DURING_READ")
        if count > cap: raise _error("INPUT_WIRE_LIMIT_EXCEEDED")
        data = b"".join(chunks)
        return CapturedFile(data, hashlib.sha256(data).hexdigest(), _metadata(opened))
    except OSError as e:
        raise _error("PATH_COMPONENT_UNSAFE") from e
    finally:
        os.close(fd)


def capture_file(path, *, kind, fault=None):
    """Read once from a supported regular input; no JSON parsing or admission."""
    if kind not in ("request", "snapshot"):
        raise ValueError("kind must be request or snapshot")
    absolute, parts = _parts(path)
    with _directory(absolute, parts[:-1]) as parent:
        try:
            return _read_at(parent, parts[-1], BUILD_LIMITS[kind + "_wire_bytes"], fault)
        except FileNotFoundError as e:
            raise _error("PATH_COMPONENT_UNSAFE") from e


def _cap(name):
    return BUILD_LIMITS[{
        "request.json": "request_wire_bytes", "snapshot.json": "snapshot_wire_bytes",
        "resolved-input.json": "resolved_input_bytes", "result.json": "output_result_bytes",
        "trace.json": "output_trace_bytes", "diagnostic.json": "output_diagnostic_bytes",
        "input-metadata.json": "output_result_bytes", "build.json": "request_wire_bytes",
        "manifest.json": "output_result_bytes",
    }[name]]


def _json(data, name):
    """Bounded canonical file-set syntax, not duplicated public/domain validation."""
    if type(data) is not bytes or len(data) > _cap(name):
        raise _error("OUTPUT_LIMIT_EXCEEDED")
    # Bound nesting before json.loads; escaped quotes do not change nesting.
    depth, string, escape = 0, False, False
    for c in data:
        if string:
            if escape: escape = False
            elif c == 92: escape = True
            elif c == 34: string = False
        elif c == 34: string = True
        elif c in (91, 123):
            depth += 1
            if depth > BUILD_LIMITS["input_json_depth"]: raise _error("OUTPUT_LIMIT_EXCEEDED")
        elif c in (93, 125): depth -= 1
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
        if type(value) is not dict or canonical_json_bytes(value) != data:
            raise ValueError("noncanonical file")
    except (ValueError, UnicodeError, RecursionError) as e:
        raise _error("MANIFEST_INVALID") from e
    counts = _count(value, wire_bytes=len(data), canonical_bytes=len(data))
    cap = BUILD_LIMITS["output_result_nodes" if name == "result.json" else "input_json_nodes_per_file"]
    if (counts.nodes > cap or counts.depth > BUILD_LIMITS["input_json_depth"]
            or counts.max_string_bytes > BUILD_LIMITS["input_max_string_bytes"]):
        raise _error("OUTPUT_LIMIT_EXCEEDED")
    if name == "trace.json":
        rows = [value.get(k, []) for k in ("decision_rows", "projection_rows")]
        if any(type(v) is not list for v in rows): raise _error("MANIFEST_INVALID")
        if sum(map(len, rows)) > BUILD_LIMITS["output_trace_rows"]: raise _error("OUTPUT_LIMIT_EXCEEDED")
    return value


def _rename_exclusive(fd, old, new):
    # Same-directory atomic rename without replacing an unexpectedly inserted file.
    libc = _libc()
    call = libc.renameat2
    call.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    call.restype = ctypes.c_int
    if call(fd, old.encode(), fd, new.encode(), 1):  # Linux RENAME_NOREPLACE
        e = ctypes.get_errno()
        raise OSError(e, os.strerror(e))


def _write_file(fd, name, data, hook):
    stage = "create"
    temp = "." + name + ".tmp"
    try:
        _event(hook, stage, name)
        out = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=fd)
        with os.fdopen(out, "wb") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stage = "write"; _event(hook, stage, name)
            stream.write(data)
            stage = "flush"; _event(hook, stage, name); stream.flush()
            stage = "file_fsync"; _event(hook, stage, name); os.fsync(stream.fileno())
        stage = "manifest_before_rename" if name == "manifest.json" else "rename"
        _event(hook, stage, name)
        _rename_exclusive(fd, temp, name)
    except OSError as e:
        code = {"create": "CREATE", "write": "WRITE", "flush": "FLUSH",
                "file_fsync": "FILE_FSYNC", "rename": "RENAME",
                "manifest_before_rename": "MANIFEST"}[stage]
        raise _error("RETENTION_" + code + "_FAILED") from e
    _event(hook, "published", name)


def publish_bundle(output_dir, files, *, bundle_kind="complete", operation="evaluate", fault=None):
    """Publish supplied canonical slice output; never claims its semantic validity.

    S6 owns final result/build assembly and replay. Fault hooks are trusted test
    code, not serialized requests. No failed operation deletes its evidence.
    """
    absolute, parts = _parts(output_dir)
    if re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", parts[-1]) is None:
        raise _error("OUTPUT_BASENAME_INVALID")
    names = COMPLETE_FILES if bundle_kind == "complete" else REFUSAL_FILES if bundle_kind == "refusal" else ()
    if not names or operation not in ("evaluate", "replay") or set(files) != set(names):
        raise _error("MANIFEST_INVALID")
    payloads = {n: files[n] for n in names}
    with _directory(absolute, parts[:-1]) as parent:
        filesystem = _filesystem(parent)
        for name, data in payloads.items(): _json(data, name)
        inventory = {n: {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()} for n, b in payloads.items()}
        manifest = {"schema_version": "bdw001.1", "bundle_kind": bundle_kind, "operation": operation,
                    "build_identity": inventory["build.json"]["sha256"], "files": inventory,
                    "semantic_commitments": {n: inventory[n]["sha256"] for n in ("result.json", "trace.json") if n in inventory},
                    "run_metadata": {"created_at_utc": datetime.now(UTC).isoformat(), "filesystem": filesystem}}
        manifest_wire = canonical_json_bytes(manifest)
        _json(manifest_wire, "manifest.json")
        if sum(len(b) for b in payloads.values()) + len(manifest_wire) > BUILD_LIMITS["retention_bundle_bytes"]:
            raise _error("OUTPUT_LIMIT_EXCEEDED")
        try:
            _event(fault, "directory_create", parts[-1])
            os.mkdir(parts[-1], 0o700, dir_fd=parent)
        except FileExistsError as e:
            raise _error("OUTPUT_COLLISION") from e
        except OSError as e:
            raise _error("RETENTION_CREATE_FAILED", state="absent") from e
        fd = None
        try:
            fd = os.open(parts[-1], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent)
            os.fchmod(fd, 0o700)
            for name in names: _write_file(fd, name, payloads[name], fault)
            _write_file(fd, "manifest.json", manifest_wire, fault)
            for event, descriptor, code in (("directory_fsync", fd, "RETENTION_DIR_FSYNC_FAILED"),
                                             ("parent_fsync", parent, "RETENTION_PARENT_FSYNC_FAILED")):
                try:
                    _event(fault, event, parts[-1]); os.fsync(descriptor)
                except OSError as e: raise _error(code) from e
        except OSError as e:
            raise _error("RETENTION_CREATE_FAILED") from e
        finally:
            if fd is not None: os.close(fd)
    return BundleInspection("complete_bundle", bundle_kind, "fsync_sequence_returned",
                            MappingProxyType(dict(payloads, **{"manifest.json": manifest_wire})), None,
                            hashlib.sha256(manifest_wire).hexdigest())


def verify_bundle(path, *, fault=None):
    """Fixed-name byte/inventory verification only. Never repairs or recomputes."""
    absolute, parts = _parts(path)
    with _directory(absolute, parts) as directory:
        _filesystem(directory)
        captured, total = {}, 0
        code = "BUNDLE_INCOMPLETE"
        # Listing is bounded, never an unbounded os.listdir on hostile content.
        entries = set()
        with os.scandir(directory) as iterator:
            for item in iterator:
                entries.add(item.name)
                if len(entries) > 2 * len(KNOWN_FILES):
                    raise _error("MANIFEST_INVALID")
        for name in sorted(entries & KNOWN_FILES):
            try:
                captured_file = _read_at(directory, name, _cap(name), fault)
            except FileNotFoundError:
                # A vanished entry is not a complete bundle; do not retry/open
                # a replacement, and do not present a partial successful result.
                continue
            total += len(captured_file.data)
            if total > BUILD_LIMITS["retention_bundle_bytes"]: raise _error("INPUT_WIRE_LIMIT_EXCEEDED")
            captured[name] = captured_file.data
        valid, kind = False, None
        if "manifest.json" in captured:
            code = "MANIFEST_INVALID"
            try:
                m = _json(captured["manifest.json"], "manifest.json")
                kind = m.get("bundle_kind")
                names = COMPLETE_FILES if kind == "complete" else REFUSAL_FILES if kind == "refusal" else ()
                valid = (bool(names) and set(m) == MANIFEST_FIELDS and m["schema_version"] == "bdw001.1"
                         and m["operation"] in ("evaluate", "replay") and type(m["files"]) is dict
                         and set(m["files"]) == set(names) and entries == set(names) | {"manifest.json"})
                if valid:
                    for name in names:
                        data = captured[name]; _json(data, name)
                        record = m["files"][name]
                        if (type(record) is not dict or set(record) != {"bytes", "sha256"}
                                or type(record["bytes"]) is not int or record["bytes"] != len(data)
                                or record["sha256"] != hashlib.sha256(data).hexdigest()):
                            valid = False; break
                    valid = valid and m["build_identity"] == hashlib.sha256(captured["build.json"]).hexdigest()
                    valid = valid and m["semantic_commitments"] == {n: hashlib.sha256(captured[n]).hexdigest()
                        for n in ("result.json", "trace.json") if n in names}
                    valid = valid and type(m["run_metadata"]) is dict and set(m["run_metadata"]) == {"created_at_utc", "filesystem"}
                    if valid:
                        meta = m["run_metadata"]
                        valid = (type(meta["created_at_utc"]) is str and meta["filesystem"] in ("ext4", "xfs")
                                 and datetime.fromisoformat(meta["created_at_utc"]).utcoffset() == UTC.utcoffset(None))
            except WorkflowInputError as e:
                if e.diagnostic.exit_code == 4: raise
                valid = False
            except (ValueError, TypeError, KeyError):
                valid = False
        return BundleInspection("complete_bundle" if valid else "incomplete_bundle", kind if valid else None,
                                "not_established_by_verification", MappingProxyType(captured),
                                None if valid else _error(code).diagnostic,
                                hashlib.sha256(captured["manifest.json"]).hexdigest() if "manifest.json" in captured else None)
