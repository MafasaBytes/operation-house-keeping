"""L2 deployment admission A1-A7 (scope addendum 6bca403b..., section 3.1).

In-process unit tests with temporary trees and an injected Host: the account database,
platform, mount metadata and running release are simulated, so no root and no real
installation are needed. The test uid stands in for root as the owner of the release and
configuration, which therefore carry read-only modes (the owner cannot write them either).
Run as a non-root user. These tests establish admission logic only; a real installation,
interpreter and VM are later evidence.
"""
from contextlib import contextmanager
import ast
import dataclasses
import json
import os
from pathlib import Path
import signal
from types import SimpleNamespace

import pytest

from applications.bounded_decision_workflow import deployment
from applications.bounded_decision_workflow.deployment import DeploymentRefusal, Host

ACCOUNT = 'ohk-bdw'
PLATFORM = ('linux', 'x86_64', 'CPython', '3.13.11')
SOURCE = Path(deployment.__file__)


def freeze(root):
    """Read-only release modes: directories 0555, files 0444 or 0555 by their owner-exec bit."""
    for directory, dirs, files in os.walk(root, topdown=False):
        for name in files:
            path = Path(directory) / name
            if not path.is_symlink():
                os.chmod(path, 0o555 if path.stat().st_mode & 0o100 else 0o444)
        os.chmod(directory, 0o555)


@contextmanager
def opened(directory):
    os.chmod(directory, 0o755)
    try:
        yield Path(directory)
    finally:
        os.chmod(directory, 0o555)


def write_config(path, value=None, *, raw=None, mode=0o444):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        os.chmod(path.parent, 0o755)
        path.unlink()
    path.write_bytes(raw if raw is not None else json.dumps(value).encode())
    os.chmod(path, mode)
    return path


def accounts(table):
    def getpwnam(name):
        if name not in table:
            raise KeyError(name)
        return SimpleNamespace(pw_name=name, pw_uid=table[name])
    return getpwnam


def make_site(base):
    """A minimal installed layout, data root and configuration, with a host that admits them."""
    base = Path(base).resolve()
    release = base / 'release'
    (release / 'app/applications/bounded_decision_workflow').mkdir(parents=True)
    (release / 'python/bin').mkdir(parents=True)
    (release / 'app/applications/bounded_decision_workflow/deployment.py').write_bytes(b'# fixture\n')
    (release / 'python/bin/python3.13').write_bytes(b'fixture interpreter bytes')
    os.chmod(release / 'python/bin/python3.13', 0o755)
    (release / 'python/bin/python3').symlink_to('python3.13')   # lstat mode 0777, which must be ignored
    freeze(release)
    data = base / 'data'
    for directory in (data, data / 'tmp', data / 'evidence'):
        directory.mkdir()
        os.chmod(directory, 0o700)
    value = {'schema': 'ohk-bdw.deployment.v1', 'release_root': str(release), 'runtime_account': ACCOUNT,
             'data_root': str(data)}
    config = write_config(base / 'etc/deployment.json', value)
    host = Host(root_uid=os.getuid(), getpwnam=accounts({ACCOUNT: os.geteuid()}), platform=lambda: PLATFORM,
                environ={'TMPDIR': str(data / 'tmp')}, mount_of_fd=lambda fd: ('ext4', 'rw,relatime', 'rw'),
                running_release=lambda: str(release), application_root=lambda: str(release / 'app'),
                read_text=lambda path, cap=4096: 'observed ' + path)
    return SimpleNamespace(base=base, release=release, data=data, config=config, value=value, host=host)


@pytest.fixture
def site(tmp_path):
    return make_site(tmp_path)


def refused(code, host, path):
    with pytest.raises(DeploymentRefusal) as caught:
        deployment.admit_path(str(path), host)
    assert (caught.value.code, caught.value.exit_class, caught.value.stage) == (code, 5, 0), caught.value.target
    return caught.value


def test_valid_site_admits_and_records_the_observed_facts(site):
    config, record = deployment.admit_path(str(site.config), site.host)
    assert config == deployment.Config(release_root=str(site.release), runtime_account=ACCOUNT,
                                       data_root=str(site.data))
    assert record['euid'] == os.geteuid() and record['runtime_account'] == ACCOUNT
    assert record['data_root_mount'] == {'fstype': 'ext4', 'mount_options': 'rw,relatime', 'super_options': 'rw'}
    # app, applications, the package, its module, python, bin, the interpreter and its symlink
    assert record['release_entries_checked'] == 8
    assert record['core_pattern_observed'] == 'observed /proc/sys/kernel/core_pattern'   # recorded, never a gate


def test_root_is_refused_before_the_configuration_is_opened(site):
    host = dataclasses.replace(site.host, geteuid=lambda: 0, platform=lambda: ('darwin', 'arm64', 'PyPy', '3.10'))
    assert refused('RUNTIME_ACCOUNT_INVALID', host, site.base / 'absent.json').target == '/euid'


@pytest.mark.parametrize('platform', [('linux', 'aarch64', 'CPython', '3.13.11'),
                                      ('darwin', 'x86_64', 'CPython', '3.13.11'),
                                      ('linux', 'x86_64', 'PyPy', '3.13.11'),
                                      ('linux', 'x86_64', 'CPython', '3.13.10'),
                                      ('linux', 'x86_64', 'CPython', '3.14.0')])
def test_platform_is_refused_before_the_configuration(site, platform):
    host = dataclasses.replace(site.host, platform=lambda: platform)
    refused('PLATFORM_UNSUPPORTED', host, site.base / 'absent.json')


CONFIG_EDITS = {
    'unknown-key': lambda v: dict(v, core_pattern_ack='|/usr/share/apport/apport'),   # withdrawn by OD-L2-A
    'missing-key': lambda v: {k: x for k, x in v.items() if k != 'data_root'},
    'wrong-schema': lambda v: dict(v, schema='ohk-bdw.deployment.v2'),
    'not-an-object': lambda v: [v],
    'relative-release-root': lambda v: dict(v, release_root='opt/ohk-bdw/releases/x'),
    'dotdot-data-root': lambda v: dict(v, data_root=v['data_root'] + '/../data'),
    'double-slash': lambda v: dict(v, data_root='/' + v['data_root']),
    'trailing-slash': lambda v: dict(v, release_root=v['release_root'] + '/'),
    'space-in-path': lambda v: dict(v, release_root=v['release_root'] + ' x'),
    'quote-in-path': lambda v: dict(v, release_root=v['release_root'] + '"'),
    'account-uppercase': lambda v: dict(v, runtime_account='Ohk'),
    'account-not-string': lambda v: dict(v, runtime_account=1000),
    'root-path': lambda v: dict(v, data_root='/'),
}


@pytest.mark.parametrize('name', sorted(CONFIG_EDITS))
def test_configuration_content_refusals(site, name):
    write_config(site.config, CONFIG_EDITS[name](dict(site.value)))
    refused('CONFIG_INVALID', site.host, site.config)


@pytest.mark.parametrize('raw', [b'{"schema":"ohk-bdw.deployment.v1","schema":"ohk-bdw.deployment.v1"}',
                                 b'\xff\xfe{}', b'{"schema": NaN}', b'{' * 2000 + b'}' * 2000,
                                 b'{}' + b' ' * 65536])
def test_configuration_syntax_and_size_refusals(site, raw):
    write_config(site.config, raw=raw)
    refused('CONFIG_INVALID', site.host, site.config)


def test_configuration_file_must_be_root_owned_and_unwritable(site):
    for mode in (0o644, 0o464, 0o446):   # euid-writable (owner), group-writable, other-writable
        os.chmod(site.config, mode)
        refused('CONFIG_INVALID', site.host, site.config)
    os.chmod(site.config, 0o444)
    refused('CONFIG_INVALID', dataclasses.replace(site.host, root_uid=os.getuid() + 1), site.config)
    deployment.admit_path(str(site.config), site.host)   # twin: the same file admits once restored


def test_configuration_path_must_be_absolute_regular_and_symlink_free(site):
    link = site.base / 'link.json'
    link.symlink_to(site.config)
    refused('CONFIG_INVALID', site.host, link)
    (site.base / 'etc-link').symlink_to(site.base / 'etc', target_is_directory=True)
    refused('CONFIG_INVALID', site.host, site.base / 'etc-link/deployment.json')
    refused('CONFIG_INVALID', site.host, site.base / 'etc')                    # a directory
    with pytest.raises(DeploymentRefusal):
        deployment.admit_path('etc/deployment.json', site.host)              # relative


@contextmanager
def deadline(seconds):
    """A blocking call fails the test instead of hanging it; the previous handler and timer are restored.

    pytest.fail raises a BaseException, so the loader's `except OSError` cannot turn it into a refusal."""
    def expired(signum, frame):
        pytest.fail('the call blocked', pytrace=False)
    previous = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def test_a_configuration_fifo_refuses_promptly_without_a_writer(site):
    os.unlink(site.config)
    os.mkfifo(site.config, 0o444)
    with deadline(5):
        refused('CONFIG_INVALID', site.host, site.config)


@pytest.mark.parametrize('case', ['directory', 'fifo', 'group-writable', 'admitted'])
def test_the_configuration_descriptor_is_closed_after_every_outcome(site, monkeypatch, case):
    if case in ('directory', 'fifo'):
        os.unlink(site.config)
        if case == 'directory':
            os.mkdir(site.config)
        else:
            os.mkfifo(site.config, 0o444)
    elif case == 'group-writable':
        os.chmod(site.config, 0o464)
    target, real_open, real_close = str(site.config), os.open, os.close
    opened, closed, live = [], [], set()

    def tracking_open(path, flags, *args, **kwargs):   # the real call; only the loader's descriptor is noted
        fd = real_open(path, flags, *args, **kwargs)
        if os.fspath(path) == target:
            opened.append(fd)
            live.add(fd)
        return fd

    def tracking_close(fd):
        real_close(fd)
        if fd in live:
            live.discard(fd)
            closed.append(fd)

    monkeypatch.setattr(deployment.os, 'open', tracking_open)
    monkeypatch.setattr(deployment.os, 'close', tracking_close)
    with deadline(5):
        if case == 'admitted':
            deployment.admit_path(target, site.host)
        else:
            refused('CONFIG_INVALID', site.host, site.config)
    monkeypatch.undo()
    assert len(opened) == 1 and closed == opened and not live
    with pytest.raises(OSError):
        os.fstat(opened[0])


def test_unknown_account_is_a_configuration_refusal(site):
    host = dataclasses.replace(site.host, getpwnam=accounts({}))
    assert refused('CONFIG_INVALID', host, site.config).target == '/config/runtime_account'


def test_account_mismatch_precedes_release_and_data_root_checks(site):
    host = dataclasses.replace(site.host, getpwnam=accounts({ACCOUNT: os.geteuid() + 1}),
                               running_release=lambda: '/elsewhere', mount_of_fd=lambda fd: ('xfs', 'rw', 'rw'))
    assert refused('RUNTIME_ACCOUNT_INVALID', host, site.config).target == '/euid'


def test_release_root_must_be_the_running_release_without_symlinks(site):
    for running, application in ((lambda: str(site.release) + '-other', lambda: str(site.release / 'app')),
                                 (lambda: None, lambda: str(site.release / 'app')),
                                 (lambda: str(site.release), lambda: '/srv/checkout')):
        host = dataclasses.replace(site.host, running_release=running, application_root=application)
        assert refused('CONFIG_INVALID', host, site.config).target.startswith('/config/release_root')
    alias = site.base / 'alias'
    alias.symlink_to(site.release, target_is_directory=True)
    write_config(site.config, dict(site.value, release_root=str(alias)))
    host = dataclasses.replace(site.host, running_release=lambda: str(alias),
                               application_root=lambda: str(alias / 'app'))
    refused('CONFIG_INVALID', host, site.config)


@pytest.mark.parametrize('fstype', ['xfs', 'tmpfs', 'ext3', 'btrfs'])
def test_data_root_must_be_exactly_ext4_before_owner_and_mode(site, fstype):
    os.chmod(site.data, 0o750)   # also wrong, but the filesystem is checked first
    host = dataclasses.replace(site.host, mount_of_fd=lambda fd: (fstype, 'rw', 'rw'))
    assert refused('FILESYSTEM_UNSUPPORTED', host, site.config).target == '/config/data_root'


def test_unreadable_mount_metadata_is_unsupported(site):
    def broken(fd):
        raise ValueError('mount metadata too large')
    refused('FILESYSTEM_UNSUPPORTED', dataclasses.replace(site.host, mount_of_fd=broken), site.config)


def test_a_separately_mounted_subdirectory_is_refused(site):
    tmp_inode = (site.data / 'tmp').stat().st_ino
    host = dataclasses.replace(site.host, mount_of_fd=lambda fd: (
        'tmpfs' if os.fstat(fd).st_ino == tmp_inode else 'ext4', 'rw', 'rw'))
    assert refused('FILESYSTEM_UNSUPPORTED', host, site.config).target == '/config/data_root/tmp'


def test_data_root_owner_mode_subdirectories_and_tmpdir(site):
    os.chmod(site.data, 0o750)
    refused('CONFIG_INVALID', site.host, site.config)
    os.chmod(site.data, 0o700)
    os.chmod(site.data / 'evidence', 0o755)
    assert refused('CONFIG_INVALID', site.host, site.config).target == '/config/data_root/evidence'
    os.chmod(site.data / 'evidence', 0o700)
    other = os.geteuid() + 1   # admitted account, but the data root belongs to someone else
    host = dataclasses.replace(site.host, geteuid=lambda: other, getpwnam=accounts({ACCOUNT: other}))
    assert refused('CONFIG_INVALID', host, site.config).target == '/config/data_root'
    for environ in ({}, {'TMPDIR': '/tmp'}, {'TMPDIR': str(site.data / 'tmp') + '/'}):
        host = dataclasses.replace(site.host, environ=environ)
        assert refused('CONFIG_INVALID', host, site.config).target == '/environment/TMPDIR'
    (site.data / 'tmp').rmdir()
    assert refused('CONFIG_INVALID', site.host, site.config).target == '/config/data_root/tmp'


def test_data_root_with_a_symlink_component_is_refused(site):
    (site.base / 'data-link').symlink_to(site.data, target_is_directory=True)
    write_config(site.config, dict(site.value, data_root=str(site.base / 'data-link')))
    refused('CONFIG_INVALID', dataclasses.replace(site.host, environ={'TMPDIR': str(site.base / 'data-link/tmp')}),
            site.config)


def test_release_tree_refuses_a_writable_file(site):
    package = site.release / 'app/applications/bounded_decision_workflow'
    with opened(package):
        os.chmod(package / 'deployment.py', 0o644)   # writable by the euid that owns it
    assert refused('RELEASE_TREE_UNSAFE', site.host, site.config).target == '/release_root'
    with opened(package):
        os.chmod(package / 'deployment.py', 0o444)
    deployment.admit_path(str(site.config), site.host)   # twin


def test_release_tree_refuses_group_writable_directories_and_a_writable_root(site):
    os.chmod(site.release / 'python', 0o575)
    refused('RELEASE_TREE_UNSAFE', site.host, site.config)
    os.chmod(site.release / 'python', 0o555)
    os.chmod(site.release, 0o755)
    refused('RELEASE_TREE_UNSAFE', site.host, site.config)


def test_release_tree_checks_symlink_targets_not_symlink_modes(site):
    with opened(site.release / 'python/bin') as directory:
        (directory / 'escape').symlink_to('/etc/passwd')
    refused('RELEASE_TREE_UNSAFE', site.host, site.config)
    with opened(site.release / 'python/bin') as directory:
        (directory / 'escape').unlink()
        (directory / 'relative-escape').symlink_to('../../../outside')
    refused('RELEASE_TREE_UNSAFE', site.host, site.config)


def test_release_tree_refuses_special_files_and_foreign_owners(site):
    with opened(site.release / 'python') as directory:
        os.mkfifo(directory / 'fifo')
    refused('RELEASE_TREE_UNSAFE', site.host, site.config)
    with opened(site.release / 'python') as directory:
        (directory / 'fifo').unlink()
    target = str(site.release / 'python/bin/python3.13')

    def lstat(path):
        info = os.lstat(path)
        if str(path) != target:
            return info
        return os.stat_result((info.st_mode, info.st_ino, info.st_dev, info.st_nlink, os.getuid() + 1,
                               info.st_gid, info.st_size, info.st_atime, info.st_mtime, info.st_ctime))
    refused('RELEASE_TREE_UNSAFE', dataclasses.replace(site.host, lstat=lstat), site.config)


def test_mount_rows_are_parsed_from_the_descriptors_mount_id():
    fdinfo = 'pos:\t0\nflags:\t02100000\nmnt_id:\t36\nino:\t2\n'
    mountinfo = ('22 1 8:1 / / rw,relatime shared:1 - ext4 /dev/sda1 rw,errors=remount-ro\n'
                 '36 22 0:40 / /var/lib/ohk-bdw rw,nosuid,nodev shared:9 - xfs /dev/sdb1 rw,attr2\n')
    assert deployment.parse_mount(fdinfo, mountinfo) == ('xfs', 'rw,nosuid,nodev', 'rw,attr2')
    assert deployment.parse_mount(fdinfo.replace('36', '22'), mountinfo)[0] == 'ext4'
    with pytest.raises(StopIteration):
        deployment.parse_mount('pos:\t0\n', mountinfo)


def test_admission_is_stdlib_only_and_runs_no_git():
    text = SOURCE.read_text('utf-8')
    assert 'subprocess' not in text and "'git'" not in text
    imported = set()
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split('.')[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, 'admission must not import maintained package modules'
            imported.add(node.module.split('.')[0])
    # No maintained contract module is imported before admission completes.
    assert imported == {'dataclasses', 'datetime', 'json', 'os', 'platform', 'pathlib', 'pwd', 're', 'stat', 'sys'}
