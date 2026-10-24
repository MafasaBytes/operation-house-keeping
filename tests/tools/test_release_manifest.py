"""L2 release manifest, archive validation, extraction, publication and installer/builder refusals.

Temporary trees and archives only; no root, no network, no interpreter build, no installation.
The publication tests need a filesystem supporting renameat2 RENAME_NOREPLACE (ext4, not 9p/drvfs).
The builder and installer are executed only up to refusals that precede any work (missing or
unverified inputs; non-root). Manifest digests establish integrity relative to the supplied
expected digest, never provenance; nothing here tests signing, which is deferred (ID-2).
"""
from contextlib import contextmanager
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile

import pytest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / 'tools' / 'release'


def _load():
    spec = importlib.util.spec_from_file_location('release_manifest_under_test', TOOLS / 'release_manifest.py')
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


rm = _load()
COMMIT = '1' * 40
SOURCE_SET = '2' * 64


@contextmanager
def umask(value):
    previous = os.umask(value)
    try:
        yield
    finally:
        os.umask(previous)


def stage(base):
    """A small staged release: app tree, interpreter files, wrapper, one python/ symlink."""
    root = Path(base) / 'release'
    files = {'app/RELEASE-IDENTITY.json': (b'{}\n', 0o644), 'app/applications/a.py': (b'A = 1\n', 0o644),
             'app/backend/b.py': (b'B = 2\n', 0o644), 'python/bin/python3.13': (b'\x7fELF fixture', 0o755),
             'python/lib/libpython3.13.so.1.0': (b'fixture library', 0o755),
             'python/lib/python3.13/os.py': (b'# stdlib\n', 0o644), 'bin/ohk-bdw-check': (b'#!/bin/sh\n', 0o755)}
    for name, (data, mode) in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        os.chmod(path, mode)
    for directory in [root] + [p for p in root.rglob('*') if p.is_dir()]:
        os.chmod(directory, 0o755)
    (root / 'python/bin/python3').symlink_to('python3.13')
    sonames = Path(base) / 'sonames.txt'
    sonames.write_text('libc.so.6\nlibssl.so.3\nlibc.so.6\n')
    return root, sonames


def created(base):
    root, sonames = stage(base)
    digest = rm.create(str(root), str(root), COMMIT, SOURCE_SET, str(sonames))
    return root, digest


def refused(code, call, *args, **kwargs):
    with pytest.raises(rm.Refused) as caught:
        call(*args, **kwargs)
    assert caught.value.code == code, caught.value.detail
    return caught.value


# ------------------------------------------------------------------ manifest

def test_create_then_verify_round_trip_with_symlink_mode_ignored(tmp_path):
    root, digest = created(tmp_path)
    data = (root / rm.NAME).read_bytes()
    assert hashlib.sha256(data).hexdigest() == digest
    value = json.loads(data)
    assert data == json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    assert value['commit'] == COMMIT and value['source_set'] == SOURCE_SET and value['l1_tested_source_set'] is None
    assert value['required_sonames'] == ['libc.so.6', 'libssl.so.3']
    entries = {e['path']: e for e in value['entries']}
    assert rm.NAME not in entries and len(entries) == 16   # 8 directories, 7 files, 1 symlink
    assert entries['python/bin/python3'] == {'path': 'python/bin/python3', 'type': 'l', 'target': 'python3.13'}
    assert entries['python/bin/python3.13']['mode'] == '0755' and entries['app/applications/a.py']['mode'] == '0644'
    result = rm.verify(str(root), digest, str(root), root_uid=os.getuid())
    assert result['result'] == 'verified' and result['entries'] == 16
    assert oct((root / rm.NAME).stat().st_mode & 0o777) == '0o644'


def test_l1_tested_source_set_is_recorded_only_on_exact_equality(tmp_path):
    root, sonames = stage(tmp_path)
    rm.create(str(root), str(root), COMMIT, rm.L1_TESTED_SOURCE_SET, str(sonames))
    assert json.loads((root / rm.NAME).read_bytes())['l1_tested_source_set'] == rm.L1_TESTED_SOURCE_SET


def test_the_expected_digest_is_checked_before_the_manifest_is_parsed(tmp_path):
    root, digest = created(tmp_path)
    refused('MANIFEST_DIGEST_MISMATCH', rm.verify, str(root), '0' * 64, root_uid=os.getuid())
    path = root / rm.NAME
    path.write_bytes(b'not json')
    refused('MANIFEST_DIGEST_MISMATCH', rm.verify, str(root), digest, root_uid=os.getuid())
    refused('MANIFEST_INVALID', rm.verify, str(root), hashlib.sha256(b'not json').hexdigest(), root_uid=os.getuid())
    refused('EXPECTED_DIGEST_INVALID', rm.verify, str(root), 'A' * 64)


def _mutations(root):
    def setmode(name, mode):
        return lambda: os.chmod(root / name, mode)

    def replace(name, data):
        def act():
            new = not (root / name).exists()
            (root / name).write_bytes(data)
            if new:
                os.chmod(root / name, 0o644)   # independent of the test process umask
        return act

    def retarget(target):
        def act():
            (root / 'python/bin/python3').unlink()
            (root / 'python/bin/python3').symlink_to(target)
        return act

    def typechange():
        (root / 'app/backend/b.py').unlink()
        (root / 'app/backend/b.py').mkdir()
        os.chmod(root / 'app/backend/b.py', 0o755)

    return {
        'extra-file': ('MANIFEST_MISMATCH', replace('python/lib/extra.py', b'')),
        'missing-file': ('MANIFEST_MISMATCH', lambda: (root / 'app/backend/b.py').unlink()),
        'changed-byte': ('MANIFEST_MISMATCH', replace('app/applications/a.py', b'A = 2\n')),
        'changed-mode': ('MANIFEST_MISMATCH', setmode('app/applications/a.py', 0o600)),
        'exec-bit-removed': ('MANIFEST_MISMATCH', setmode('python/bin/python3.13', 0o644)),
        'exec-bit-added': ('MANIFEST_MISMATCH', setmode('app/backend/b.py', 0o755)),
        'directory-mode': ('MODE_UNSUPPORTED', setmode('python/lib', 0o700)),
        'file-without-owner-write': ('MODE_UNSUPPORTED', setmode('app/applications/a.py', 0o444)),
        'type-change': ('MANIFEST_MISMATCH', typechange),
        'symlink-retargeted-inside': ('MANIFEST_MISMATCH', retarget('python3.13-other')),
        'symlink-climbs': ('SYMLINK_UNSAFE', retarget('../lib/libpython3.13.so.1.0')),
        'symlink-escapes': ('SYMLINK_UNSAFE', retarget('../../../outside')),
        'symlink-absolute': ('SYMLINK_UNSAFE', retarget('/etc/passwd')),
        'group-writable-file': ('MODE_UNSAFE', setmode('app/applications/a.py', 0o664)),
        'other-writable-directory': ('MODE_UNSAFE', setmode('python/bin', 0o757)),
        'setuid-file': ('MODE_UNSAFE', setmode('python/bin/python3.13', 0o4755)),
        'bytecode-in-app': ('BYTECODE_IN_APP', replace('app/applications/__pycache__/a.cpython-313.pyc', b'x')),
        'direct-url': ('DIRECT_URL_PRESENT', replace('python/lib/python3.13/direct_url.json', b'{}')),
    }


@pytest.mark.parametrize('name', sorted(_mutations(Path('/'))))
def test_any_post_creation_change_refuses(tmp_path, name):
    root, digest = created(tmp_path)
    code, mutate = _mutations(root)[name]
    if name == 'bytecode-in-app':
        (root / 'app/applications/__pycache__').mkdir()
    mutate()
    refused(code, rm.verify, str(root), digest, str(root), root_uid=os.getuid())


def test_symlink_ownership_release_root_and_manifest_mode(tmp_path):
    root, digest = created(tmp_path)
    refused('MANIFEST_MISMATCH', rm.verify, str(root), digest, root_uid=os.getuid() + 1)   # symlink not root-owned
    refused('RELEASE_ROOT_MISMATCH', rm.verify, str(root), digest, str(root) + '-other', root_uid=os.getuid())
    os.chmod(root / rm.NAME, 0o664)
    refused('MANIFEST_UNSAFE', rm.verify, str(root), digest, root_uid=os.getuid())


def test_special_files_and_app_symlinks_are_refused_at_creation(tmp_path):
    root, sonames = stage(tmp_path / 'a')
    os.mkfifo(root / 'python/fifo')
    refused('TYPE_UNSUPPORTED', rm.create, str(root), str(root), COMMIT, SOURCE_SET, str(sonames))
    root, sonames = stage(tmp_path / 'b')
    (root / 'app/applications/link.py').symlink_to('a.py')
    refused('SYMLINK_UNSAFE', rm.create, str(root), str(root), COMMIT, SOURCE_SET, str(sonames))
    root, sonames = stage(tmp_path / 'c')
    refused('IDENTITY_INVALID', rm.create, str(root), str(root), 'HEAD', SOURCE_SET, str(sonames))
    refused('RELEASE_ROOT_INVALID', rm.create, str(root), 'relative/root', COMMIT, SOURCE_SET, str(sonames))
    assert not (root / rm.NAME).exists()


def test_source_set_follows_the_l1_rule_and_ignores_bytecode(tmp_path):
    files = {'applications/x.py': b'X = 1\n', 'applications/sub/data.json': b'{}\n', 'backend/y.py': b''}
    for name, data in files.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_bytes(data)
    (tmp_path / 'applications/__pycache__').mkdir()
    (tmp_path / 'applications/__pycache__/x.cpython-313.pyc').write_bytes(b'ignored')
    (tmp_path / 'docs').mkdir()
    (tmp_path / 'docs/outside.md').write_bytes(b'not part of the set')
    rows = sorted([name, hashlib.sha256(data).hexdigest(), len(data)] for name, data in files.items())
    expected = hashlib.sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()
    assert rm.source_set(str(tmp_path)) == expected


# --------------------------------------------------------------- archives

def tarball(path, members):
    """members: (name, kind, data_or_target, mode)."""
    with tarfile.open(path, 'w', format=tarfile.GNU_FORMAT) as archive:
        for name, kind, payload, mode in members:
            info = tarfile.TarInfo(name)
            info.mode = mode
            if kind == 'f':
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))
                continue
            info.type = {'d': tarfile.DIRTYPE, 'l': tarfile.SYMTYPE, 'h': tarfile.LNKTYPE, 'p': tarfile.FIFOTYPE,
                         'c': tarfile.CHRTYPE}[kind]
            if kind in ('l', 'h'):
                info.linkname = payload
            archive.addfile(info)
    return path


def archive_of(root, path):
    with tarfile.open(path, 'w', format=tarfile.GNU_FORMAT) as archive:
        archive.add(root, arcname='.')
    return path


BASE = [('./', 'd', None, 0o755), ('./app/', 'd', None, 0o755), ('./app/a.py', 'f', b'A\n', 0o644),
        ('./python/', 'd', None, 0o755), ('./RELEASE-MANIFEST.json', 'f', b'{}', 0o644)]


def test_valid_archive_extracts_and_verifies_like_the_staged_tree(tmp_path):
    root, digest = created(tmp_path / 'build')
    archive = archive_of(root, tmp_path / 'release.tar')
    destination = tmp_path / 'install' / 'release.partial'
    destination.parent.mkdir()
    with umask(0o022):
        assert rm.extract(str(archive), str(destination)) == 17   # the 16 entries and the manifest
    result = rm.verify(str(destination), digest, str(root), root_uid=os.getuid())
    assert result['result'] == 'verified'


@pytest.mark.parametrize('code,members', [
    ('PATH_UNSAFE', BASE + [('../evil', 'f', b'x', 0o644)]),
    ('PATH_UNSAFE', BASE + [('./app/../../evil', 'f', b'x', 0o644)]),
    ('PATH_UNSAFE', BASE + [('/etc/evil', 'f', b'x', 0o644)]),
    ('PATH_UNSAFE', BASE + [('./app/a.py', 'f', b'again', 0o644)]),
    ('TYPE_UNSUPPORTED', BASE + [('./app/hard', 'h', 'app/a.py', 0o644)]),
    ('TYPE_UNSUPPORTED', BASE + [('./python/fifo', 'p', None, 0o644)]),
    ('TYPE_UNSUPPORTED', BASE + [('./python/tty', 'c', None, 0o644)]),
    ('SYMLINK_UNSAFE', BASE + [('./python/up', 'l', '../../outside', 0o777)]),
    ('SYMLINK_UNSAFE', BASE + [('./python/abs', 'l', '/etc/passwd', 0o777)]),
    ('SYMLINK_UNSAFE', BASE + [('./app/link', 'l', 'a.py', 0o777)]),
    ('MODE_UNSAFE', BASE + [('./app/w.py', 'f', b'', 0o664)]),
    ('MODE_UNSAFE', BASE + [('./app/s', 'f', b'', 0o4755)]),
    ('PARENT_MISSING', BASE + [('./backend/b.py', 'f', b'', 0o644)]),
    # Chains of symlink members: s -> .. then t -> s/.. would climb out; t -> ../app would land in app/.
    ('SYMLINK_UNSAFE', BASE + [('./python/s', 'l', '..', 0o777), ('./python/t', 'l', 's/..', 0o777)]),
    ('SYMLINK_UNSAFE', BASE + [('./python/t', 'l', '../app', 0o777),
                               ('./python/t/__pycache__/x.pyc', 'f', b'', 0o644)]),
    # A member below a symlink member is never written through it.
    ('PARENT_MISSING', BASE + [('./python/sub/', 'd', None, 0o755), ('./python/lnk', 'l', 'sub', 0o777),
                               ('./python/lnk/evil', 'f', b'', 0o644)]),
    ('MODE_UNSUPPORTED', BASE + [('./app/ro.py', 'f', b'', 0o444)]),
    ('MODE_UNSUPPORTED', BASE + [('./app/private/', 'd', None, 0o700)]),
    ('MANIFEST_ABSENT', BASE[:-1]),
    ('BYTECODE_IN_APP', BASE + [('./app/__pycache__/', 'd', None, 0o755)]),
])
def test_unsafe_archives_are_refused_before_anything_is_created(tmp_path, code, members):
    archive = tarball(tmp_path / 'bad.tar', members)
    destination = tmp_path / 'release.partial'
    refused(code, rm.extract, str(archive), str(destination))
    assert not os.path.lexists(destination)


def test_extraction_never_overwrites_an_existing_destination(tmp_path):
    archive = tarball(tmp_path / 'ok.tar', BASE)
    occupied = tmp_path / 'occupied'
    occupied.mkdir()
    (occupied / 'keep').write_bytes(b'unrelated installation')
    with pytest.raises(FileExistsError):
        rm.extract(str(archive), str(occupied))
    assert sorted(p.name for p in occupied.iterdir()) == ['keep']
    target = tmp_path / 'elsewhere'
    (tmp_path / 'link.partial').symlink_to(target, target_is_directory=True)
    with pytest.raises(FileExistsError):
        rm.extract(str(archive), str(tmp_path / 'link.partial'))
    assert not target.exists()


def test_a_failed_verification_retains_the_partial_extraction(tmp_path):
    root, digest = created(tmp_path / 'build')
    archive = archive_of(root, tmp_path / 'release.tar')
    destination = tmp_path / 'release.partial'
    with umask(0o022):
        rm.extract(str(archive), str(destination))
    refused('MANIFEST_DIGEST_MISMATCH', rm.verify, str(destination), 'f' * 64, root_uid=os.getuid())
    assert (destination / 'app/applications/a.py').read_bytes() == b'A = 1\n'   # evidence kept, nothing deleted


# ------------------------------------------------------------- publication

def test_publish_renames_only_onto_an_absent_target(tmp_path):
    partial = tmp_path / 'r1.partial'
    partial.mkdir()
    (partial / 'f').write_bytes(b'release')
    assert rm.publish(str(partial), str(tmp_path / 'r1')) == str(tmp_path / 'r1')
    assert (tmp_path / 'r1/f').read_bytes() == b'release' and not partial.exists()


def test_publish_refuses_to_replace_and_keeps_both_trees(tmp_path):
    partial, final = tmp_path / 'r2.partial', tmp_path / 'r2'
    partial.mkdir()
    (partial / 'f').write_bytes(b'new')
    final.mkdir()   # an empty directory: plain rename(2) would silently replace it
    refused('PUBLISH_TARGET_EXISTS', rm.publish, str(partial), str(final))
    assert (partial / 'f').read_bytes() == b'new' and list(final.iterdir()) == []
    final.rmdir()
    final.symlink_to(tmp_path / 'nowhere')
    refused('PUBLISH_TARGET_EXISTS', rm.publish, str(partial), str(final))
    refused('PUBLISH_PATHS_INVALID', rm.publish, str(partial), str(tmp_path / 'sub' / 'r2'))
    (tmp_path / 'file.partial').write_bytes(b'')
    refused('PUBLISH_PARTIAL_INVALID', rm.publish, str(tmp_path / 'file.partial'), str(tmp_path / 'r3'))


def test_the_kernel_no_replace_rename_itself_refuses_an_existing_target(tmp_path, monkeypatch):
    """Past the lexists pre-check (a target appearing in the race window): renameat2 must refuse."""
    partial, final = tmp_path / 'r4.partial', tmp_path / 'r4'
    partial.mkdir()
    (partial / 'f').write_bytes(b'new')
    final.mkdir()
    real = os.path.lexists
    monkeypatch.setattr(rm.os.path, 'lexists', lambda path: False if path == str(final) else real(path))
    refused('PUBLISH_TARGET_EXISTS', rm.publish, str(partial), str(final))
    monkeypatch.undo()
    assert (partial / 'f').read_bytes() == b'new' and list(final.iterdir()) == []


# -------------------------------------------------------------- install record

def test_install_record_is_exclusive_and_never_follows_an_account_planted_link(tmp_path):
    data = tmp_path / 'data'
    (data / 'evidence').mkdir(parents=True)
    digest = rm.record(str(data), 'install-20261023t120000z-1.json', '{"schema":"ohk-bdw.install-record.v1"}')
    written = data / 'evidence/install-20261023t120000z-1.json'
    assert hashlib.sha256(written.read_bytes()).hexdigest() == digest
    assert oct(written.stat().st_mode & 0o777) == '0o644'
    with pytest.raises(FileExistsError):
        rm.record(str(data), 'install-20261023t120000z-1.json', '{}')
    victim = tmp_path / 'victim'
    victim.write_bytes(b'unchanged')
    os.chmod(victim, 0o600)
    (data / 'evidence/install-planted.json').symlink_to(victim)
    with pytest.raises(OSError):
        rm.record(str(data), 'install-planted.json', '{}')
    elsewhere = tmp_path / 'elsewhere'
    elsewhere.mkdir()
    (data / 'evidence').rename(data / 'evidence-real')
    (data / 'evidence').symlink_to(elsewhere, target_is_directory=True)
    with pytest.raises(OSError):
        rm.record(str(data), 'install-20261023t120000z-2.json', '{}')
    assert victim.read_bytes() == b'unchanged' and oct(victim.stat().st_mode & 0o777) == '0o600'
    assert list(elsewhere.iterdir()) == []
    refused('RECORD_INVALID', rm.record, str(data), '../escape.json', '{}')


# ---------------------------------------------------- personal-path dependencies

REL = '/opt/ohk-bdw/releases/test'   # the declared prefix; the staged tree itself lives in tmp
SYSCONFIG = 'python/lib/python3.13/_sysconfigdata__linux_x86_64-linux-gnu.py'
SITE = 'python/lib/python3.13/site-packages'   # where site.py reads .pth files
SYSCONFIG_VARS = {'prefix': REL + '/python', 'exec_prefix': REL + '/python', 'LIBDIR': REL + '/python/lib',
                  'BINDIR': REL + '/python/bin', 'LIBPL': REL + '/python/lib/python3.13/config-3.13-x86_64-linux-gnu',
                  'LIBDEST': REL + '/python/lib/python3.13', 'BINLIBDEST': REL + '/python/lib/python3.13',
                  'DESTSHARED': REL + '/python/lib/python3.13/lib-dynload',
                  'INCLUDEPY': REL + '/python/include/python3.13', 'CONFINCLUDEPY': REL + '/python/include/python3.13',
                  'abs_builddir': '/home/builder/work/Python-3.13.11',
                  'CONFIG_ARGS': "'--prefix=%s/python' '--disable-test-modules'" % REL}


def elf(kind):
    """An ELF64 little-endian header prefix with e_type: 2 executable, 3 shared object, 1 relocatable."""
    return b'\x7fELF\x02\x01\x01' + bytes(9) + kind.to_bytes(2, 'little') + b'fixture'
LDD = ('== {r}/python/bin/python3.13\n\tlinux-vdso.so.1 (0x00007ffc1000)\n'
       '\tlibpython3.13.so.1.0 => {r}/python/lib/libpython3.13.so.1.0 (0x00007f0000001000)\n'
       '\tlibc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f0000002000)\n'
       '\t/lib64/ld-linux-x86-64.so.2 (0x00007f0000003000)\n'
       '== {r}/python/lib/libpython3.13.so.1.0\n\tlibm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007f0000004000)\n')
READELF = ('== {r}/python/bin/python3.13\n\nDynamic section at offset 0x2d00 contains 30 entries:\n'
           '  Tag        Type                         Name/Value\n'
           ' 0x0000000000000001 (NEEDED)             Shared library: [libpython3.13.so.1.0]\n'
           ' 0x000000000000001d (RUNPATH)            Library runpath: [{r}/python/lib]\n'
           '== {r}/python/lib/libpython3.13.so.1.0\n\nDynamic section at offset 0x1000 contains 2 entries:\n'
           ' 0x000000000000000e (SONAME)             Library soname: [libpython3.13.so.1.0]\n')


def portable(base, *, files=None, ldd=None, readelf=None, sysconfig=None):
    """A staged interpreter layout for prefix REL with ldd/readelf evidence; overrides per test."""
    root = Path(base) / 'staged'
    content = {'python/bin/python3.13': (elf(2), 0o755),
               'python/bin/pydoc3.13': (('#!%s/python/bin/python3.13\nimport pydoc\n' % REL).encode(), 0o755),
               'python/bin/python3.13-config': (b'#!/bin/sh\necho config\n', 0o755),
               'bin/ohk-bdw-check': (('#!/bin/sh\nexec %s/python/bin/python3.13 -I -B -c pass\n' % REL).encode(), 0o755),
               'python/lib/libpython3.13.so.1.0': (elf(3), 0o755),
               'python/lib/pkgconfig/python-3.13.pc': (('prefix=%s/python\nlibdir=${prefix}/lib\n' % REL).encode(), 0o644),
               # A harmless literal: documentation text, not a path the release uses.
               'python/lib/python3.13/os.py': (b'# for example ~ expands to /home/user\n', 0o644),
               SITE + '/README.txt': (b'This directory exists so that packages can be placed here.\n', 0o644),
               SYSCONFIG: (('# generated\nbuild_time_vars = %r\n' % ((sysconfig or SYSCONFIG_VARS),)).encode(), 0o644)}
    content.update(files or {})
    for name, (data, mode) in content.items():
        if data is None:
            continue
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        os.chmod(path, mode)
    for directory in [root] + [p for p in root.rglob('*') if p.is_dir()]:
        os.chmod(directory, 0o755)
    evidence = {}
    for name, text in (('ldd.txt', LDD if ldd is None else ldd), ('readelf.txt', READELF if readelf is None else readelf)):
        evidence[name] = Path(base) / name
        evidence[name].write_text(text.format(r=REL))
    return root, evidence['ldd.txt'], evidence['readelf.txt']


def test_a_portable_interpreter_passes_and_harmless_literals_are_findings(tmp_path):
    root, ldd, readelf = portable(tmp_path)
    result = rm.portability(str(root), REL, str(ldd), str(readelf))
    assert result['result'] == 'portable'
    assert {'python/bin/pydoc3.13', 'python/bin/python3.13-config', 'bin/ohk-bdw-check', SYSCONFIG,
            'python/lib/pkgconfig/python-3.13.pc'} <= set(result['checked_dependency_files'])
    assert (result['resolved_libraries'], result['runpath_entries']) == (3, 1)
    found = {f['path']: f['matches'] for f in result['literal_findings']}
    # The example in documentation and the build directory in sysconfig metadata are reported, not refused.
    assert found == {'python/lib/python3.13/os.py': 1, SYSCONFIG: 1} and result['literal_finding_files'] == 2


@pytest.mark.parametrize('code,where,setup', [
    ('PERSONAL_PATH_DEPENDENCY', 'shebang', dict(files={'python/bin/tool': (b'#!/home/dev/venv/bin/python\n', 0o755)})),
    ('UNEXPECTED_DEPENDENCY', 'shebang', dict(files={'python/bin/tool': (b'#!/opt/other/bin/python3\n', 0o755)})),
    ('PERSONAL_PATH_DEPENDENCY', 'sysconfig', dict(sysconfig=dict(SYSCONFIG_VARS, LIBDIR='/home/dev/py/lib'))),
    ('PERSONAL_PATH_DEPENDENCY', 'pkg-config', dict(files={'python/lib/pkgconfig/python-3.13.pc': (
        ('prefix=%s/python\nlibdir=/home/dev/py/lib\n' % REL).encode(), 0o644)})),
    ('PERSONAL_PATH_DEPENDENCY', 'pkg-config', dict(files={'python/lib/pkgconfig/python-3.13.pc': (
        ('prefix=%s/python\nLibs: -L/home/dev/py/lib -lpython3.13\n' % REL).encode(), 0o644)})),
    ('PERSONAL_PATH_DEPENDENCY', 'ldd', dict(ldd=LDD + '\tlibfoo.so.1 => /home/dev/lib/libfoo.so.1 (0x00007f0000005000)\n')),
    ('UNEXPECTED_DEPENDENCY', 'ldd', dict(ldd=LDD + '\tlibbar.so.2 => /opt/vendor/lib/libbar.so.2 (0x00007f0000006000)\n')),
    ('PERSONAL_PATH_DEPENDENCY', 'ldd', dict(ldd=LDD + '\t/home/dev/lib/libx.so (0x00007f0000007000)\n')),   # no soname
    ('PERSONAL_PATH_DEPENDENCY', 'ldd', dict(ldd=LDD + '\tlibfoo.so.1 => {r}/python/lib' + '/..' * 8
                                         + '/home/dev/lib/libfoo.so.1 (0x7f00)\n')),
    ('PERSONAL_PATH_DEPENDENCY', 'runpath', dict(readelf=READELF + ' 0x000000000000001d (RUNPATH)            '
                                                 'Library runpath: [/home/dev/lib]\n')),
    ('PERSONAL_PATH_DEPENDENCY', 'runpath', dict(readelf=READELF + ' 0x000000000000000f (RPATH)              '
                                                 'Library rpath: [/home/dev/lib]\n')),
    ('PERSONAL_PATH_DEPENDENCY', 'runpath', dict(readelf=READELF + ' 0x000000000000001d (RUNPATH)            '
                                                 'Library runpath: [{r}/python/lib' + '/..' * 8 + '/home/dev/lib]\n')),
    ('PERSONAL_PATH_DEPENDENCY', 'runpath', dict(readelf=READELF + ' 0x000000000000001d (RUNPATH)            '
                                                 'Library runpath: [$ORIGIN' + '/..' * 8 + '/home/dev/lib]\n')),
    ('PERSONAL_PATH_DEPENDENCY', 'shebang', dict(files={'python/bin/tool': (b'#!/usr/bin/env /home/dev/py/bin/python\n',
                                                                           0o755)})),
    ('UNEXPECTED_DEPENDENCY', 'shebang', dict(files={'python/bin/tool': (b'#!/usr/bin/env python3\n', 0o755)})),
])
def test_a_real_personal_or_foreign_path_dependency_refuses(tmp_path, code, where, setup):
    root, ldd, readelf = portable(tmp_path, **setup)
    assert refused(code, rm.portability, str(root), REL, str(ldd), str(readelf)).detail['where'] == where


@pytest.mark.parametrize('where,path,value,files', [
    ('shebang', 'python/bin/tool', '/home/dev/venv/bin/python',
     {'python/bin/tool': (b'#!/home/dev/venv/bin/python\n', 0o755)}),
    ('shebang', 'bin/tool', '/home/dev/py/bin/python', {'bin/tool': (b'#!/usr/bin/env /home/dev/py/bin/python\n', 0o755)}),
    ('pkg-config', 'python/lib/pkgconfig/python-3.13.pc', '/home/dev/py/lib', {'python/lib/pkgconfig/python-3.13.pc': (
        ('prefix=%s/python\nlibdir=/home/dev/py/lib\n' % REL).encode(), 0o644)}),
    ('pkg-config', 'python/lib/pkgconfig/python-3.13.pc', '/home/dev/py/lib', {'python/lib/pkgconfig/python-3.13.pc': (
        ('prefix=%s/python\nLibs: -L/home/dev/py/lib -lpython3.13\n' % REL).encode(), 0o644)}),
])
def test_dependency_refusals_name_the_file_that_carries_them(tmp_path, where, path, value, files):
    root, ldd, readelf = portable(tmp_path, files=files)
    detail = refused('PERSONAL_PATH_DEPENDENCY', rm.portability, str(root), REL, str(ldd), str(readelf)).detail
    assert (detail['where'], detail['path'], detail['value']) == (where, path, value)


@pytest.mark.parametrize('name,data', [
    (SITE + '/vendor.pth', b'/home/dev/lib/python3.13/site-packages\n'),        # absolute sys.path entry
    (SITE + '/hook.pth', b'import os; os.environ.setdefault("X", "1")\n'),     # executed at every start
    (SITE + '/relative.pth', b'vendor\n'),                                       # a harmless-looking entry
    ('python/lib/python3.13/.hidden.pth', b''),                                  # anywhere in the tree
])
def test_any_pth_file_in_the_release_refuses(tmp_path, name, data):
    root, ldd, readelf = portable(tmp_path, files={name: (data, 0o644)})
    detail = refused('PTH_FILE_PRESENT', rm.portability, str(root), REL, str(ldd), str(readelf)).detail
    assert detail == {'path': name, 'type': 'f'}


def test_pth_coverage_cannot_be_skipped(tmp_path):
    root, ldd, readelf = portable(tmp_path / 'absent')
    (root / SITE / 'README.txt').unlink()
    (root / SITE).rmdir()
    assert refused('EVIDENCE_MISSING', rm.portability, str(root), REL, str(ldd), str(readelf)).detail == {'file': SITE}
    root, ldd, readelf = portable(tmp_path / 'mode')
    os.chmod(root / SITE, 0o700)   # a non-0755 directory: the scan's directory rule refuses it, never skips it
    refused('MODE_UNSUPPORTED', rm.portability, str(root), REL, str(ldd), str(readelf))
    root, ldd, readelf = portable(tmp_path / 'link')
    (root / SITE / 'link.pth').symlink_to('README.txt')   # a symlink scan admits under python/: the .pth rule refuses it
    detail = refused('PTH_FILE_PRESENT', rm.portability, str(root), REL, str(ldd), str(readelf)).detail
    assert detail == {'path': SITE + '/link.pth', 'type': 'l'}
    root, ldd, readelf = portable(tmp_path / 'text', files={SITE + '/notes.txt': (b'see vendor.pth in /home/dev\n', 0o644)})
    result = rm.portability(str(root), REL, str(ldd), str(readelf))   # a name or literal mentioning .pth is not one
    assert result['result'] == 'portable' and {'path': SITE + '/notes.txt', 'matches': 1} in result['literal_findings']


def test_origin_runpaths_inside_and_relocatable_objects_are_accepted(tmp_path):
    readelf = READELF + ' 0x000000000000001d (RUNPATH)            Library runpath: [$ORIGIN/../lib:$ORIGIN]\n'
    files = {'python/lib/python3.13/config-3.13-x86_64-linux-gnu/python.o': (elf(1), 0o644)}   # never loaded
    root, ldd, readelf_path = portable(tmp_path, files=files, readelf=readelf)
    result = rm.portability(str(root), REL, str(ldd), str(readelf_path))
    assert result['result'] == 'portable' and result['runpath_entries'] == 3
    assert rm.elf_objects(str(root), REL) == [REL + '/python/bin/python3.13', REL + '/python/lib/libpython3.13.so.1.0']


def test_the_same_string_refuses_as_an_interpreter_but_not_as_text(tmp_path):
    text = b'# see /home/dev/venv/bin/python for the old layout\n'
    root, ldd, readelf = portable(tmp_path / 'text', files={'python/lib/python3.13/notes.py': (text, 0o644)})
    assert rm.portability(str(root), REL, str(ldd), str(readelf))['result'] == 'portable'
    root, ldd, readelf = portable(tmp_path / 'shebang', files={'python/bin/notes': (b'#!/home/dev/venv/bin/python\n',
                                                                                 0o755)})
    refused('PERSONAL_PATH_DEPENDENCY', rm.portability, str(root), REL, str(ldd), str(readelf))


def test_a_personal_release_root_refuses_before_any_evidence_is_read(tmp_path):
    root, ldd, readelf = portable(tmp_path)
    assert refused('PERSONAL_PATH_DEPENDENCY', rm.portability, str(root), '/home/dev/release', '/absent',
                   '/absent').detail['where'] == 'release_root'
    refused('RELEASE_ROOT_INVALID', rm.portability, str(root), 'relative/root', str(ldd), str(readelf))


@pytest.mark.parametrize('code,setup', [
    ('EVIDENCE_MISSING', dict(ldd='')),
    ('EVIDENCE_MISSING', dict(ldd=LDD.split('== {r}/python/lib/')[0])),                 # no libpython block
    ('EVIDENCE_MISSING', dict(ldd=LDD + '== {r}/python/lib/python3.13/lib-dynload/_ssl.so\n')),   # empty block
    ('EVIDENCE_MALFORMED', dict(ldd='\tlibc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x1)\n' + LDD)),  # before header
    ('EVIDENCE_MALFORMED', dict(ldd=LDD + '\tlibfoo.so.1 => not found\n')),
    ('EVIDENCE_MALFORMED', dict(ldd=LDD + '== {r}/python/bin/python3.13\n\tlinux-vdso.so.1 (0x1)\n')),  # duplicate block
    ('EVIDENCE_MALFORMED', dict(readelf=READELF.replace('Dynamic section at offset 0x1000 contains 2 entries:',
                                                        'There is no dynamic section in this file.'))),
    ('EVIDENCE_MISSING', dict(files={'python/lib/python3.13/lib-dynload/_x.cpython-313-x86_64-linux-gnu.so': (
        elf(3), 0o755)})),                                                           # a loaded object without evidence
    ('EVIDENCE_MALFORMED', dict(ldd=LDD + '== {r}/python/lib/python3.13/os.py\n'
                                '\tlibc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x1)\n')),   # a block for a non-ELF
    ('EVIDENCE_MALFORMED', dict(readelf=READELF + ' 0x000000000000001d (RUNPATH)            unparsable\n')),
    ('EVIDENCE_MALFORMED', dict(sysconfig={k: v for k, v in SYSCONFIG_VARS.items() if k != 'INCLUDEPY'})),
    ('EVIDENCE_MALFORMED', dict(files={'python/lib/pkgconfig/python-3.13.pc': (b'prefix=/opt/elsewhere\n', 0o644)})),
    ('EVIDENCE_MISSING', dict(files={SYSCONFIG: (None, 0)})),
    ('EVIDENCE_MALFORMED', dict(files={SYSCONFIG: (b"build_time_vars = dict(prefix='x')\n", 0o644)})),  # not a literal
    ('EVIDENCE_MALFORMED', dict(sysconfig=dict(SYSCONFIG_VARS, prefix='/opt/elsewhere/python'))),
])
def test_missing_or_malformed_dependency_evidence_fails_closed(tmp_path, code, setup):
    root, ldd, readelf = portable(tmp_path, **setup)
    refused(code, rm.portability, str(root), REL, str(ldd), str(readelf))


def test_unreadable_evidence_fails_closed_through_the_cli(tmp_path):
    root, ldd, readelf = portable(tmp_path)
    err = io.StringIO()
    assert rm.main(['portability', '--root', str(root), '--release-root', REL, '--ldd', str(tmp_path / 'absent.txt'),
                    '--readelf', str(readelf)], io.StringIO(), err) == 1
    assert json.loads(err.getvalue())['code'] == 'IO_ERROR'


def test_the_cpython_test_package_must_be_excluded(tmp_path):
    root, ldd, readelf = portable(tmp_path, files={'python/lib/python3.13/test/__init__.py': (b'', 0o644)})
    refused('TEST_MODULES_PRESENT', rm.portability, str(root), REL, str(ldd), str(readelf))


# ------------------------------------------------------------ configuration

def test_config_template_must_match_the_install_arguments_and_is_written_exclusively(tmp_path):
    value = {'schema': 'ohk-bdw.deployment.v1', 'release_root': '/opt/ohk-bdw/releases/x', 'runtime_account': 'ohk-bdw',
             'data_root': '/var/lib/ohk-bdw'}
    template = tmp_path / 'template.json'
    template.write_text(json.dumps(value))
    out = tmp_path / 'deployment.json'
    args = ('/opt/ohk-bdw/releases/x', '/var/lib/ohk-bdw', 'ohk-bdw')
    digest = rm.config(str(template), str(out), *args)
    assert out.read_bytes() == rm.canonical(value) + b'\n' and hashlib.sha256(out.read_bytes()).hexdigest() == digest
    assert oct(out.stat().st_mode & 0o777) == '0o644'
    with pytest.raises(FileExistsError):
        rm.config(str(template), str(out), *args)
    refused('CONFIG_INVALID', rm.config, str(template), str(tmp_path / 'b.json'), '/opt/other', *args[1:])
    template.write_text(json.dumps(dict(value, core_pattern_ack='|x')))
    refused('CONFIG_INVALID', rm.config, str(template), str(tmp_path / 'c.json'), *args)


# ---------------------------------------------------------------- the CLI

def test_cli_exit_codes_and_one_line_diagnostics(tmp_path):
    root, digest = created(tmp_path)
    out, err = io.StringIO(), io.StringIO()
    assert rm.main(['verify', '--root', str(root), '--expect-sha256', digest, '--symlink-owner-uid',
                    str(os.getuid())], out, err) == 0
    assert json.loads(out.getvalue())['result'] == 'verified'
    out, err = io.StringIO(), io.StringIO()
    assert rm.main(['verify', '--root', str(root), '--expect-sha256', '0' * 64], out, err) == 1
    line = err.getvalue()
    assert line.count('\n') == 1 and json.loads(line)['code'] == 'MANIFEST_DIGEST_MISMATCH'
    for argv in ([], ['verify'], ['verify', '--root', str(root)], ['frobnicate', '--root', 'x'],
                 ['verify', '--root', str(root), '--expect-sha256', digest, '--root', 'again'],
                 ['verify', '--root', str(root), '--expect-sha256', digest, '--symlink-owner-uid', 'root']):
        assert rm.main(argv, io.StringIO(), io.StringIO()) == 2


def test_manifest_tool_is_stdlib_only():
    text = (TOOLS / 'release_manifest.py').read_text('utf-8')
    imported = {line.split()[1].split('.')[0] for line in text.splitlines()
                if line.strip().startswith(('import ', 'from '))}
    assert imported <= {'hashlib', 'json', 'os', 're', 'stat', 'sys', 'tarfile', 'ctypes', 'errno', 'ast'}


# ------------------------------------------------------ builder and installer

BUILD = TOOLS / 'build_release.sh'
INSTALL = TOOLS / 'install_release.sh'


def _no_root():
    if os.geteuid() == 0:
        pytest.fail('these script tests must never run as root')


def build_args(tmp_path, **override):
    tarball_path = tmp_path / 'Python-3.13.11.tar.xz'
    tarball_path.write_bytes(b'not the real tarball')
    pip = tmp_path / 'pip.pyz'
    pip.write_bytes(b'not a zipapp')
    requirements = tmp_path / 'requirements-hashed.txt'
    requirements.write_bytes(b'pytest==9.1.1 --hash=sha256:' + b'0' * 64 + b'\n')
    wheelhouse = tmp_path / 'wheelhouse'
    wheelhouse.mkdir(exist_ok=True)
    (wheelhouse / 'x-1-py3-none-any.whl').write_bytes(b'w')
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    args = {'repository': str(tmp_path), 'commit': '3' * 40, 'release-root': '/nonexistent-ohk-bdw-test/release',
            'cpython-tarball': str(tarball_path), 'cpython-sha256': sha(tarball_path), 'pip-zipapp': str(pip),
            'pip-zipapp-sha256': sha(pip), 'wheelhouse': str(wheelhouse), 'requirements-hashed': str(requirements),
            'requirements-hashed-sha256': sha(requirements), 'expected-source-set': '4' * 64,
            'out': '/nonexistent-ohk-bdw-test/out'}
    args.update(override)
    argv = ['bash', str(BUILD)]
    for key, value in args.items():
        if value is not None:
            argv += ['--' + key, value]
    return argv


def run_script(argv):
    _no_root()
    return subprocess.run(argv, capture_output=True, timeout=60, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})


@pytest.mark.parametrize('override,code', [
    ({'cpython-sha256': '5' * 64}, 'CPYTHON_DIGEST_MISMATCH'),
    ({'pip-zipapp-sha256': '5' * 64}, 'PIP_ZIPAPP_DIGEST_MISMATCH'),
    ({'requirements-hashed-sha256': '5' * 64}, 'REQUIREMENTS_DIGEST_MISMATCH'),
    ({'cpython-tarball': '/nonexistent-ohk-bdw-test/Python.tar.xz'}, 'INPUT_MISSING cpython-tarball'),
    ({'wheelhouse': '/nonexistent-ohk-bdw-test/wheels'}, 'INPUT_MISSING wheelhouse'),
    ({'cpython-sha256': 'latest'}, 'DIGEST_ARGUMENT_INVALID --cpython-sha256'),
    ({'expected-source-set': 'e6c9f2a3'}, 'DIGEST_ARGUMENT_INVALID --expected-source-set'),
    ({'commit': 'HEAD'}, 'COMMIT_INVALID'),
    ({'release-root': '/opt/ohk bdw'}, 'RELEASE_ROOT_INVALID'),
    ({'out': '/home/someone/out'}, 'OUT_UNDER_PERSONAL_PATH'),
])
def test_builder_refuses_absent_or_unverified_inputs_before_any_work(tmp_path, override, code):
    done = run_script(build_args(tmp_path, **override))
    assert done.returncode == 1, done.stderr.decode(errors='replace')
    assert ('build_release: REFUSED ' + code).encode() in done.stderr
    assert not os.path.lexists('/nonexistent-ohk-bdw-test')


def test_builder_refuses_unexpected_wheelhouse_entries_and_missing_arguments(tmp_path):
    argv = build_args(tmp_path)
    (tmp_path / 'wheelhouse/notes.txt').write_bytes(b'')
    done = run_script(argv)
    assert done.returncode == 1 and b'WHEELHOUSE_UNEXPECTED_ENTRY notes.txt' in done.stderr
    assert run_script(build_args(tmp_path, **{'cpython-sha256': None})).returncode == 2
    assert run_script(build_args(tmp_path) + ['--commit', '3' * 40]).returncode == 2   # duplicate flag


def test_builder_has_no_network_path_and_no_embedded_external_identity():
    text = BUILD.read_text('utf-8')
    for forbidden in ('curl', 'wget', 'http://', 'https://', '--index-url', 'pip download', 'apt-get', 'git clone',
                      'git fetch'):
        assert forbidden not in text, forbidden
    # The only 64-hex literal is the L1 tested source-set digest; every external digest is an argument.
    assert set(re.findall(r'\b[0-9a-f]{64}\b', text)) == {rm.L1_TESTED_SOURCE_SET}
    for required in ('--no-index', '--require-hashes', '--only-binary=:all:', '--no-compile', '--with-ensurepip=no',
                     '--enable-shared', 'tar.umask=022', 'DIRECT_URL_PRESENT', 'DISTRIBUTION_SET_DIFFERS_FROM_LOCK',
                     'SOURCE_SET_MISMATCH', 'APP_TREE_DIFFERS_FROM_EXPORT', 'PORTABILITY_CHECK_FAILED',
                     'SYSCONFIG_PREFIX_MISMATCH', 'TOOLS_DIFFER_FROM_COMMIT', '--hard-dereference',
                     '--disable-test-modules', 'DEPENDENCY_EVIDENCE_FAILED'):
        assert required in text, required
    # The blanket "any /home/ or /mnt/ byte refuses" rule is replaced by the bounded dependency check.
    assert 'grep -rlF' not in text and 'PERSONAL_PATH_IN_RELEASE' not in text
    configure = text[text.index('./configure'):text.index('> "$OUT/configure.log"')]
    assert '--disable-test-modules' in configure
    # Inputs are verified before the first directory is created.
    assert text.index('CPYTHON_DIGEST_MISMATCH') < text.index('mkdir "$OUT"')


def install_args(tmp_path, *extra):
    template = tmp_path / 'template.json'
    template.write_text('{}')
    return ['sh', str(INSTALL), '--tarball', str(tmp_path / 'release.tar'), '--manifest-sha256', '6' * 64,
            '--release-root', '/nonexistent-ohk-bdw-test/release', '--config-template', str(template),
            '--data-root', '/nonexistent-ohk-bdw-test/data', '--account', 'ohk-bdw', *extra]


def test_installer_refuses_non_root_signatures_and_bad_usage_before_any_change(tmp_path):
    done = run_script(install_args(tmp_path))
    assert done.returncode == 1 and b'install_release: REFUSED NOT_ROOT' in done.stderr
    done = run_script(install_args(tmp_path, '--signature', str(tmp_path / 'sig')))
    assert done.returncode == 1 and b'SIGNATURE_POLICY_UNDEFINED' in done.stderr
    assert run_script(install_args(tmp_path)[:-2]).returncode == 2                 # account missing
    assert run_script(install_args(tmp_path, '--account', 'x')).returncode == 2    # duplicate flag
    assert not os.path.lexists('/nonexistent-ohk-bdw-test')


def test_installer_sequence_verifies_before_publishing_and_keeps_partials():
    text = INSTALL.read_text('utf-8')
    order = [text.index(marker) for marker in (
        'refuse NOT_ROOT', 'RELEASE_ROOT_EXISTS', 'manifest extract', 'manifest verify --root "$PARTIAL"',
        'SONAME_MISSING', 'adduser --system', 'manifest config', 'manifest publish',
        'manifest verify --root "$R_REL"', 'manifest record')]
    assert order == sorted(order)
    assert 'umask 022' in text and 'chown -R -h root:root "$PARTIAL"' in text
    assert 'chmod 0644' not in text   # nothing root-run follows a path inside the account's data root
    for forbidden in ('rm -', 'git', 'curl', 'wget', 'core_pattern'):
        assert forbidden not in text, forbidden
