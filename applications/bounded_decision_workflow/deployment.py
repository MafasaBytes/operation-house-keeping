"""L2 deployment configuration and startup admission for an installed release.

Admission runs before the checked and T1 contract, pinned-schema and build-identity
modules are imported, in the fixed order A1-A7 of the L2 scope addendum
(docs/superpowers/reports/2026-10-22-t1-linux-ext4-l2-scope-finalization-ADDENDUM.md,
section 3.1). Every refusal exits 5 through the caller. The package `__init__` (the S1-S7
contracts, pydantic and backend modules) is necessarily imported first by the wrapper's
import of this package; it reads no pinned schema, runs no Git and, under `-B`, writes nothing.

Host facts (account database, effective uid, mount metadata, the running release,
the clock) are read through an injectable `Host`, so tests need neither root nor a
real installation; the process entry points always use the real host. Admission is
not containment, signature verification or provenance, and it never reads
`core_pattern` as a gate: the observed value is recorded only (OD-L2-A).
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import os
import platform as _platform_module
from pathlib import Path
import pwd
import re
import stat
import sys

SCHEMA = 'ohk-bdw.deployment.v1'
KEYS = frozenset({'schema', 'release_root', 'runtime_account', 'data_root'})
CONFIG_BYTES = 65536
METADATA_BYTES = 1048576
TEXT_BYTES = 4096
PYTHON_VERSION = '3.13.11'
PATH_CHARS = re.compile('/[A-Za-z0-9/._-]{1,4095}\\Z')   # the builder's R_REL character set
ACCOUNT = re.compile('[a-z_][a-z0-9_-]{0,31}\\Z')
SUBDIRS = ('tmp', 'evidence')
INTERPRETER = ('python', 'bin', 'python3.13')
WALK_ENTRIES = 262144
WALK_DEPTH = 64
EXIT_REFUSED = 5


class DeploymentRefusal(Exception):
    """The attributes of checked_contracts.CheckedRefusal, without importing it before admission."""

    def __init__(self, code, target='/', stage=0, exit_class=EXIT_REFUSED):
        super().__init__(code)
        self.code, self.target, self.stage, self.exit_class = code, target, stage, exit_class


def refuse(code, target='/'):
    raise DeploymentRefusal(code, target)


# ------------------------------------------------------------------ host

def _platform():
    return (sys.platform, _platform_module.machine(), _platform_module.python_implementation(),
            _platform_module.python_version())


def _running_release():
    """The release root of the executing interpreter: realpath(sys.executable) minus python/bin/python3.13."""
    executable = Path(os.path.realpath(sys.executable))
    if executable.parts[-3:] != INTERPRETER:
        return None
    return str(executable.parents[2])


def _application_root():
    """R_REL/app as seen by this module (applications/bounded_decision_workflow/deployment.py)."""
    return str(Path(__file__).resolve().parents[2])


def read_text(path, cap=TEXT_BYTES):
    """Bounded text read for record-only facts; None when absent, unreadable or over the cap."""
    try:
        fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
        with os.fdopen(fd, 'rb') as stream:
            data = stream.read(cap + 1)
        return None if len(data) > cap else data.decode('utf-8')
    except (OSError, UnicodeError):
        return None


def parse_mount(fdinfo, mountinfo):
    """(fstype, mount options, super options) of the mount named by an fdinfo mnt_id."""
    mount = next(line.split()[1] for line in fdinfo.splitlines() if line.startswith('mnt_id:'))
    row = next(line for line in mountinfo.splitlines() if line.split() and line.split()[0] == mount)
    left, right = row.split(' - ', 1)
    fields, rest = left.split(), right.split()
    return rest[0], fields[5], rest[2] if len(rest) > 2 else ''


def _mount_of_fd(fd):
    # The open descriptor's mount (as retention._filesystem), not a caller path or a
    # statfs magic shared by ext2/ext3/ext4.
    texts = []
    for path in ('/proc/self/fdinfo/%d' % fd, '/proc/self/mountinfo'):
        with open(path, 'rb') as stream:
            data = stream.read(METADATA_BYTES + 1)
        if len(data) > METADATA_BYTES:
            raise ValueError('mount metadata too large')
        texts.append(data.decode('ascii'))
    return parse_mount(*texts)


def _utcnow():
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Host:
    geteuid: object = os.geteuid
    getpwnam: object = pwd.getpwnam
    root_uid: int = 0
    platform: object = _platform
    environ: object = field(default_factory=lambda: os.environ)
    mount_of_fd: object = _mount_of_fd
    running_release: object = _running_release
    application_root: object = _application_root
    lstat: object = os.lstat
    read_text: object = read_text
    utcnow: object = _utcnow
    getpid: object = os.getpid


@dataclass(frozen=True)
class Config:
    release_root: str
    runtime_account: str
    data_root: str


def _writable(path):
    effective = os.access in os.supports_effective_ids
    return os.access(path, os.W_OK, effective_ids=effective)


# ------------------------------------------------------------- admission

def preflight(host):
    """A1 (euid 0, before any configuration is opened), then A2 (platform)."""
    if host.geteuid() == 0:
        refuse('RUNTIME_ACCOUNT_INVALID', '/euid')
    system, machine, implementation, version = host.platform()
    if system != 'linux' or machine != 'x86_64' or implementation != 'CPython' or version != PYTHON_VERSION:
        refuse('PLATFORM_UNSUPPORTED', '/platform')


def _path(value, target):
    """Absolute, normalized, builder character set, no '..'; existence is checked separately."""
    if type(value) is not str or not PATH_CHARS.fullmatch(value) or os.path.normpath(value) != value \
            or value.startswith('//') or '..' in value.split('/'):
        refuse('CONFIG_INVALID', target)
    return value


def _no_symlink_component(path, host, target):
    """lstat walk of every prefix, including the final component, which must exist."""
    walked = ''
    for part in path.split('/')[1:]:
        walked += '/' + part
        try:
            info = host.lstat(walked)
        except OSError:
            refuse('CONFIG_INVALID', target)
        if stat.S_ISLNK(info.st_mode):
            refuse('CONFIG_INVALID', target)
    return info


def load_config(path, host):
    """A3: the file (regular, root-owned, not group/other/euid-writable, at most 64 KiB) and its closed keys."""
    target = '/config'
    _path(path, target)
    _no_symlink_component(path, host, target)
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
    except OSError:
        refuse('CONFIG_INVALID', target)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != host.root_uid or info.st_mode & 0o022 \
                or info.st_size > CONFIG_BYTES or _writable(path):
            refuse('CONFIG_INVALID', target)
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            data = stream.read(CONFIG_BYTES + 1)
    except OSError:
        refuse('CONFIG_INVALID', target)
    finally:
        os.close(fd)
    if len(data) > CONFIG_BYTES:
        refuse('CONFIG_INVALID', target)

    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                refuse('CONFIG_INVALID', target)
            value[key] = item
        return value

    def constant(_):
        refuse('CONFIG_INVALID', target)

    try:
        value = json.loads(data.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant)
    except (UnicodeError, ValueError, RecursionError):
        refuse('CONFIG_INVALID', target)
    if type(value) is not dict or set(value) != KEYS or value['schema'] != SCHEMA:
        refuse('CONFIG_INVALID', target)
    account = value['runtime_account']
    if type(account) is not str or not ACCOUNT.fullmatch(account):
        refuse('CONFIG_INVALID', target + '/runtime_account')
    return Config(release_root=_path(value['release_root'], target + '/release_root'),
                  runtime_account=account, data_root=_path(value['data_root'], target + '/data_root'))


def _owner_only_dir(fd, euid, target):
    info = os.fstat(fd)
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != euid or stat.S_IMODE(info.st_mode) != 0o700:
        refuse('CONFIG_INVALID', target)


def _ext4(fd, host, target):
    try:
        fstype, options, super_options = host.mount_of_fd(fd)
    except (OSError, ValueError, IndexError, StopIteration, UnicodeError):
        refuse('FILESYSTEM_UNSUPPORTED', target)
    if fstype != 'ext4':   # exactly ext4: retention._filesystem also admits xfs
        refuse('FILESYSTEM_UNSUPPORTED', target)
    return {'fstype': fstype, 'mount_options': options, 'super_options': super_options}


def _data_root(config, host, euid):
    """A6: ext4 (FILESYSTEM_UNSUPPORTED) first, then owner and mode 0700, the fixed subdirectories and TMPDIR."""
    target = '/config/data_root'
    _no_symlink_component(config.data_root, host, target)
    try:
        fd = os.open(config.data_root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    except OSError:
        refuse('CONFIG_INVALID', target)
    try:
        mount = _ext4(fd, host, target)
        _owner_only_dir(fd, euid, target)
        for name in SUBDIRS:
            try:
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
            except OSError:
                refuse('CONFIG_INVALID', target + '/' + name)
            try:
                _ext4(child, host, target + '/' + name)   # a separate mount here would escape the check
                _owner_only_dir(child, euid, target + '/' + name)
            finally:
                os.close(child)
    finally:
        os.close(fd)
    if host.environ.get('TMPDIR') != config.data_root + '/tmp':
        refuse('CONFIG_INVALID', '/environment/TMPDIR')
    return mount


def _release_tree(root, host):
    """A7: every entry root-owned; files and directories neither group/other- nor euid-writable;
    symlinks (whose mode is always 0777) only owner- and target-checked; no other types."""
    target = '/release_root'

    def check(path, info):
        if info.st_uid != host.root_uid:
            refuse('RELEASE_TREE_UNSAFE', target)
        if stat.S_ISLNK(info.st_mode):
            resolved = os.path.realpath(path)
            if resolved != root and not resolved.startswith(root + '/'):
                refuse('RELEASE_TREE_UNSAFE', target)
            return False
        if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)) or info.st_mode & 0o022 \
                or _writable(path):
            refuse('RELEASE_TREE_UNSAFE', target)
        return stat.S_ISDIR(info.st_mode)

    try:
        check(root, host.lstat(root))
        pending, count = [(root, 0)], 0
        while pending:
            directory, depth = pending.pop()
            for name in sorted(os.listdir(directory)):
                count += 1
                if count > WALK_ENTRIES:
                    refuse('RELEASE_TREE_UNSAFE', target)
                path = directory + '/' + name
                if check(path, host.lstat(path)):
                    if depth + 1 > WALK_DEPTH:
                        refuse('RELEASE_TREE_UNSAFE', target)
                    pending.append((path, depth + 1))
    except OSError:
        refuse('RELEASE_TREE_UNSAFE', target)
    return count


def admit(config, host):
    """A3 (account exists), A4, A5, A6 and A7 in order; returns the admission record."""
    try:
        account = host.getpwnam(config.runtime_account)
    except KeyError:
        refuse('CONFIG_INVALID', '/config/runtime_account')
    euid = host.geteuid()
    if euid == 0 or euid != account.pw_uid:
        refuse('RUNTIME_ACCOUNT_INVALID', '/euid')
    _no_symlink_component(config.release_root, host, '/config/release_root')
    if host.running_release() != config.release_root:
        refuse('CONFIG_INVALID', '/config/release_root')
    if host.application_root() != config.release_root + '/app':
        refuse('CONFIG_INVALID', '/config/release_root/app')
    mount = _data_root(config, host, euid)
    entries = _release_tree(config.release_root, host)
    return {'runtime_account': config.runtime_account, 'euid': euid, 'release_root': config.release_root,
            'data_root': config.data_root, 'data_root_mount': mount, 'release_entries_checked': entries,
            'core_pattern_observed': host.read_text('/proc/sys/kernel/core_pattern')}


def admit_path(path, host):
    """A1-A7 for a configuration path: preflight, load_config, admit."""
    preflight(host)
    config = load_config(path, host)
    return config, admit(config, host)
