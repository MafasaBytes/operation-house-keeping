"""Installed-release source witness: the Git object chain recomputed from installed bytes.

Used only when the application root has no .git and carries RELEASE-IDENTITY.json.
It establishes the same two facts as the maintained Git path (the checkpoint, and
that applications/ and backend/ equal that commit exactly) without a mutable
checkout. It is not a signature or provenance check: release authenticity is
verified separately at installation. Ignored files are refused, not ignored.
File modes are compared by the owner-execute bit, as Git records them.
"""
import base64
import hashlib
import json
import os
import re
import stat

from . import build

NAME = 'RELEASE-IDENTITY.json'
SCHEMA = 'bdw.release-identity.v1'
TOPS = ('applications', 'backend')
RECORD_BYTES = 1048576
FILE_BYTES = 67108864
MAX_ENTRIES = 4096
MAX_PARTS = 16
MAX_PATH = 240
HEX40 = re.compile('[0-9a-f]{40}\\Z')
PART = re.compile('[A-Za-z0-9_.-]+\\Z')
MODES = ('100644', '100755')
FIELDS = {'schema', 'install_root', 'commit', 'commit_object', 'root_tree_object', 'entries'}


def present(root):
    return os.path.lexists(root / NAME)


def _object_id(kind, data):
    return hashlib.sha1(b'%s %d\0' % (kind, len(data)) + data).hexdigest()


def _read(path, cap, work=None, executable=None):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    with os.fdopen(fd, 'rb') as stream:
        mode = os.fstat(stream.fileno()).st_mode
        if not stat.S_ISREG(mode):
            raise build.unavailable()
        if executable is not None and bool(mode & stat.S_IXUSR) != executable:
            raise build.unavailable()
        data = stream.read(cap + 1)
    if len(data) > cap:
        raise build.unavailable()
    if work is not None:
        # One operation per file. build_hash_bytes keeps its SHA-256-only meaning;
        # the SHA-1 witness work is visible as bytes read.
        work.physical['build_bytes_read'] = work.physical.get('build_bytes_read', 0) + len(data)
        work.physical['build_read_operations'] = work.physical.get('build_read_operations', 0) + 1
    return data


def _tree(entries):
    """Git tree id of {name: (mode, blob) | {...}} in Git's name order."""
    body = b''
    def order(name):
        return name.encode() + (b'/' if isinstance(entries[name], dict) else b'')
    for name in sorted(entries, key=order):
        value = entries[name]
        if isinstance(value, dict):
            mode, oid = b'40000', _tree(value)
        else:
            mode, oid = value[0].encode(), value[1]
        body += mode + b' ' + name.encode() + b'\0' + bytes.fromhex(oid)
    return _object_id(b'tree', body)


def _tree_entries(data):
    found = {}
    at = 0
    while at < len(data):
        space = data.index(b' ', at)
        nul = data.index(b'\0', space)
        if nul + 21 > len(data):
            raise build.unavailable()
        found[data[space + 1:nul]] = (data[at:space], data[nul + 1:nul + 21].hex())
        at = nul + 21
    return found


def verified_source(root, work=None):
    """Return (checkpoint, sorted paths) or refuse REPLAY_BUILD_UNAVAILABLE."""
    try:
        return _verified(root, work)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError) as e:
        if isinstance(e, build.WorkflowInputError):
            raise
        raise build.unavailable() from e


def _verified(root, work):
    if os.path.lexists(root / '.git'):
        raise build.unavailable()
    record = json.loads(_read(root / NAME, RECORD_BYTES, work))
    if type(record) is not dict or set(record) != FIELDS or record['schema'] != SCHEMA:
        raise build.unavailable()
    if record['install_root'] != str(root):
        raise build.unavailable()
    commit = record['commit']
    if type(commit) is not str or not HEX40.fullmatch(commit):
        raise build.unavailable()
    commit_object = base64.b64decode(record['commit_object'], validate=True)
    root_tree = base64.b64decode(record['root_tree_object'], validate=True)
    head = re.match(rb'tree ([0-9a-f]{40})\n', commit_object)
    if _object_id(b'commit', commit_object) != commit or head is None:
        raise build.unavailable()
    if _object_id(b'tree', root_tree) != head.group(1).decode():
        raise build.unavailable()
    top = _tree_entries(root_tree)
    entries = record['entries']
    if type(entries) is not list or not 0 < len(entries) <= MAX_ENTRIES:
        raise build.unavailable()
    nested = {name: {} for name in TOPS}
    paths = []
    for item in entries:
        if type(item) is not list or len(item) != 3 or not all(type(v) is str for v in item):
            raise build.unavailable()
        path, mode, blob = item
        parts = path.split('/')
        if not 2 <= len(parts) <= MAX_PARTS or len(path) > MAX_PATH or parts[0] not in TOPS \
                or mode not in MODES or not HEX40.fullmatch(blob) \
                or any(p in ('.', '..') or not PART.fullmatch(p) for p in parts):
            raise build.unavailable()
        node = nested[parts[0]]
        for part in parts[1:-1]:
            node = node.setdefault(part, {})
            if not isinstance(node, dict):
                raise build.unavailable()
        if parts[-1] in node:
            raise build.unavailable()
        node[parts[-1]] = (mode, blob)
        paths.append(path)
    if paths != sorted(paths):
        raise build.unavailable()
    for name in TOPS:
        if top.get(name.encode()) != (b'40000', _tree(nested[name])):
            raise build.unavailable()
    installed = []
    def walk(relative, depth):
        if depth >= MAX_PARTS:
            raise build.unavailable()
        with os.scandir(root / relative) as listing:
            for entry in listing:
                name = relative + '/' + entry.name
                if entry.is_dir(follow_symlinks=False):
                    walk(name, depth + 1)
                elif entry.is_file(follow_symlinks=False):
                    installed.append(name)
                else:
                    raise build.unavailable()
    for name in TOPS:
        if not stat.S_ISDIR(os.lstat(root / name).st_mode):
            raise build.unavailable()
        walk(name, 1)
    if sorted(installed) != paths:
        raise build.unavailable()
    for path, mode, blob in entries:
        if _object_id(b'blob', _read(root / path, FILE_BYTES, work, mode == '100755')) != blob:
            raise build.unavailable()
    return commit, paths
