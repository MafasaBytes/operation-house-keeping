#!/usr/bin/env python3
"""RELEASE-MANIFEST.json (ohk-bdw.release-manifest.v1): package integrity for one L2 release.

Stdlib only; runs with the target's system python3 at installation or with the release's
own interpreter. Design: L2 proposal 74a39d87... sections 3.4 and 4.5, as amended by the
scope addendum 6bca403b...

    release_manifest.py create  --root DIR --release-root R_REL --commit C --source-set D --sonames FILE
    release_manifest.py verify  --root DIR --expect-sha256 D [--release-root R_REL] [--symlink-owner-uid N]
    release_manifest.py publish --partial R_REL.partial --final R_REL
    release_manifest.py record  --data-root DR --name install-<id>.json --json TEXT
    release_manifest.py portability --root DIR --release-root R_REL --ldd FILE --readelf FILE
    release_manifest.py elf-objects --root DIR --release-root R_REL
    release_manifest.py source-set --root DIR
    release_manifest.py check-archive --tarball T
    release_manifest.py extract --tarball T --dest DIR
    release_manifest.py sonames --root DIR --expect-sha256 D
    release_manifest.py config --template FILE --out PATH --release-root R_REL --data-root DR --account NAME

A matching manifest digest establishes integrity relative to whoever delivered the expected
digest. It does not authenticate the builder, the build host or the source origin; there is
no signature (ID-2 open) and no provenance claim (D-P open).

Exit 0 on success, 1 on a mismatch or refusal (one line of JSON on stderr), 2 on usage.
"""
import hashlib
import json
import os
import re
import stat
import sys
import tarfile

SCHEMA = 'ohk-bdw.release-manifest.v1'
NAME = 'RELEASE-MANIFEST.json'
PYTHON_VERSION = '3.13.11'
PLATFORM = 'linux-x86_64'
# The L1 tested source-set digest (proposal 1.3): sorted [path, sha256, bytes] of the 246
# non-__pycache__ files of applications/ and backend/, compact JSON, SHA-256.
L1_TESTED_SOURCE_SET = 'e6c9f2a342c70b2aace64315442707b3cb1783cc18a5e54f5f95ccf205ed47c0'
FIELDS = {'schema', 'release_root', 'commit', 'source_set', 'l1_tested_source_set', 'python_version',
          'platform', 'required_sonames', 'entries'}
CONFIG_KEYS = {'schema', 'release_root', 'runtime_account', 'data_root'}
HEX40 = re.compile('[0-9a-f]{40}\\Z')
HEX64 = re.compile('[0-9a-f]{64}\\Z')
ROOT_PATH = re.compile('/[A-Za-z0-9/._-]{1,4095}\\Z')
ACCOUNT = re.compile('[a-z_][a-z0-9_-]{0,31}\\Z')
SONAME = re.compile('[A-Za-z0-9._+-]{1,255}\\Z')
MANIFEST_BYTES = 67108864
CONFIG_BYTES = 65536
MAX_ENTRIES = 262144
MAX_DEPTH = 64
MAX_MEMBER_BYTES = 1073741824
MAX_ARCHIVE_BYTES = 4294967296
REPORT_LIMIT = 20
SYMLINK_TOP = 'python'      # symlinks are allowed under python/ only
FORBIDDEN_NAMES = ('__pycache__',)


class Refused(Exception):
    def __init__(self, code, **detail):
        super().__init__(code)
        self.code, self.detail = code, detail


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def sha_file(path):
    digest, size = hashlib.sha256(), 0
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise Refused('NOT_REGULAR', path=path)
        while True:
            chunk = stream.read(1048576)
            if not chunk:
                break
            size += len(chunk)
            digest.update(chunk)
    return digest.hexdigest(), size


def _name_ok(relative):
    parts = relative.split('/')
    return all(p not in ('', '.', '..') and '\0' not in p and not any(ord(c) < 0x20 or c == '\x7f' for c in p)
               for p in parts)


def _target_inside(relative, target):
    """A symlink target must be relative, without '..', and resolve lexically inside the release root.

    Refusing '..' means no chain of symlink members can climb out of the tree or into app/
    (for example s -> .., t -> s/..). The interpreter's own links (python3 -> python3.13) need none.
    """
    if not target or target.startswith('/') or '\0' in target or '..' in target.split('/'):
        return False
    joined = os.path.normpath(os.path.join(os.path.dirname(relative), target))
    return joined != '..' and not joined.startswith('../') and not joined.startswith('/')


def _rule(relative, kind, mode, target=None):
    """Release rules shared by create, verify and archive checks."""
    parts = relative.split('/')
    if not _name_ok(relative):
        raise Refused('PATH_UNSAFE', path=relative)
    if parts[0] == 'app' and any(p in FORBIDDEN_NAMES for p in parts):
        raise Refused('BYTECODE_IN_APP', path=relative)
    if parts[-1] == 'direct_url.json':
        raise Refused('DIRECT_URL_PRESENT', path=relative)
    if kind == 'l':
        if parts[0] != SYMLINK_TOP or not _target_inside(relative, target):
            raise Refused('SYMLINK_UNSAFE', path=relative)
        return
    if kind not in ('f', 'd'):
        raise Refused('TYPE_UNSUPPORTED', path=relative)
    if mode & 0o022 or mode & 0o7000:
        raise Refused('MODE_UNSAFE', path=relative)
    # The installer's stdlib 'data' extraction filter adds owner read/write to files, clears
    # group/other execute when the owner lacks it, and creates directories with the umask-022
    # default 0755; refuse every mode it would change, at build time rather than at install.
    if (kind == 'f' and (mode & 0o600 != 0o600 or (not mode & 0o100 and mode & 0o011))) or \
            (kind == 'd' and mode != 0o755):
        raise Refused('MODE_UNSUPPORTED', path=relative)


def scan(root):
    """Entries for every file, directory and symlink under root except the manifest; never follows links."""
    entries, pending, count = [], [('', 0)], 0
    while pending:
        relative_dir, depth = pending.pop()
        directory = os.path.join(root, relative_dir) if relative_dir else root
        for name in sorted(os.listdir(directory)):
            relative = relative_dir + '/' + name if relative_dir else name
            if relative == NAME:
                continue
            count += 1
            if count > MAX_ENTRIES:
                raise Refused('TOO_MANY_ENTRIES')
            path = os.path.join(root, relative)
            info = os.lstat(path)
            mode = stat.S_IMODE(info.st_mode)
            if stat.S_ISLNK(info.st_mode):
                target = os.readlink(path)
                _rule(relative, 'l', 0, target)
                entries.append({'path': relative, 'type': 'l', 'target': target})
            elif stat.S_ISDIR(info.st_mode):
                _rule(relative, 'd', mode)
                if depth + 1 > MAX_DEPTH:
                    raise Refused('TOO_DEEP', path=relative)
                entries.append({'path': relative, 'type': 'd', 'mode': '%04o' % mode})
                pending.append((relative, depth + 1))
            elif stat.S_ISREG(info.st_mode):
                _rule(relative, 'f', mode)
                digest, size = sha_file(path)
                entries.append({'path': relative, 'type': 'f', 'mode': '%04o' % mode, 'bytes': size,
                                'sha256': digest})
            else:
                raise Refused('TYPE_UNSUPPORTED', path=relative)
    return sorted(entries, key=lambda e: e['path'])


def source_set(root):
    """The proposal 1.3 rule over root/applications and root/backend, __pycache__ excluded."""
    rows = []
    for top in ('applications', 'backend'):
        for directory, dirs, files in os.walk(os.path.join(root, top)):
            dirs[:] = sorted(d for d in dirs if d != '__pycache__')
            for name in dirs:
                if os.path.islink(os.path.join(directory, name)):
                    raise Refused('SYMLINK_UNSAFE', path=os.path.relpath(os.path.join(directory, name), root))
            for name in files:
                path = os.path.join(directory, name)
                if os.path.islink(path):
                    raise Refused('SYMLINK_UNSAFE', path=os.path.relpath(path, root))
                digest, size = sha_file(path)
                rows.append([os.path.relpath(path, root).replace(os.sep, '/'), digest, size])
    if not rows:
        raise Refused('SOURCE_SET_EMPTY')
    return hashlib.sha256(json.dumps(sorted(rows), separators=(',', ':')).encode()).hexdigest()


def _sonames(path):
    with open(path, encoding='ascii') as stream:
        names = sorted({line.strip() for line in stream if line.strip()})
    if not names or not all(SONAME.fullmatch(n) for n in names):
        raise Refused('SONAMES_INVALID')
    return names


def _exclusive_write(path, data, mode, dir_fd=None):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, mode, dir_fd=dir_fd)
    try:
        os.fchmod(fd, mode)   # on the descriptor: independent of the umask, never through a swapped path
        view = memoryview(data)
        while view:
            view = view[os.write(fd, view):]
        os.fsync(fd)
    finally:
        os.close(fd)


RECORD_NAME = re.compile('install-[0-9a-z-]{1,64}\\.json\\Z')


def record(data_root, name, text):
    """Write the root install record into the account-owned <data_root>/evidence without following
    any symlink the account could plant there: the data root (whose parent the installer requires
    to be root-owned) and evidence are opened with O_NOFOLLOW|O_DIRECTORY, the file with
    O_EXCL|O_NOFOLLOW."""
    if not RECORD_NAME.fullmatch(name) or not ROOT_PATH.fullmatch(data_root):
        raise Refused('RECORD_INVALID')
    value = _strict(text.encode('utf-8'))
    if type(value) is not dict:
        raise Refused('RECORD_INVALID')
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    root_fd = os.open(data_root, flags)
    try:
        evidence_fd = os.open('evidence', flags, dir_fd=root_fd)
        try:
            data = canonical(value) + b'\n'
            _exclusive_write(name, data, 0o644, dir_fd=evidence_fd)
            os.fsync(evidence_fd)
        finally:
            os.close(evidence_fd)
    finally:
        os.close(root_fd)
    return hashlib.sha256(data).hexdigest()


def create(root, release_root, commit, source_set_digest, sonames_path):
    if not ROOT_PATH.fullmatch(release_root) or os.path.normpath(release_root) != release_root:
        raise Refused('RELEASE_ROOT_INVALID')
    if not HEX40.fullmatch(commit) or not HEX64.fullmatch(source_set_digest):
        raise Refused('IDENTITY_INVALID')
    value = {'schema': SCHEMA, 'release_root': release_root, 'commit': commit, 'source_set': source_set_digest,
             'l1_tested_source_set': source_set_digest if source_set_digest == L1_TESTED_SOURCE_SET else None,
             'python_version': PYTHON_VERSION, 'platform': PLATFORM, 'required_sonames': _sonames(sonames_path),
             'entries': scan(root)}
    data = canonical(value)
    _exclusive_write(os.path.join(root, NAME), data, 0o644)
    return hashlib.sha256(data).hexdigest()


def _strict(data):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise Refused('MANIFEST_INVALID')
            value[key] = item
        return value

    def constant(_):
        raise Refused('MANIFEST_INVALID')

    try:
        return json.loads(data.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant)
    except (UnicodeError, ValueError, RecursionError):
        raise Refused('MANIFEST_INVALID')


def load(root, expect_sha256):
    """The manifest whose bytes hash to the externally supplied digest, checked before parsing."""
    if not HEX64.fullmatch(expect_sha256):
        raise Refused('EXPECTED_DIGEST_INVALID')
    path = os.path.join(root, NAME)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o022:
            raise Refused('MANIFEST_UNSAFE')
        data = stream.read(MANIFEST_BYTES + 1)
    if len(data) > MANIFEST_BYTES:
        raise Refused('MANIFEST_TOO_LARGE')
    if hashlib.sha256(data).hexdigest() != expect_sha256:
        raise Refused('MANIFEST_DIGEST_MISMATCH')
    value = _strict(data)
    if type(value) is not dict or set(value) != FIELDS or value['schema'] != SCHEMA or \
            value['python_version'] != PYTHON_VERSION or value['platform'] != PLATFORM or \
            type(value['entries']) is not list or type(value['required_sonames']) is not list or \
            not all(type(n) is str and SONAME.fullmatch(n) for n in value['required_sonames']):
        raise Refused('MANIFEST_INVALID')
    return value


def verify(root, expect_sha256, release_root=None, root_uid=0):
    """Exact file set, types, modes, sizes, hashes and link targets; symlinks root-owned and inside."""
    value = load(root, expect_sha256)
    if release_root is not None and value['release_root'] != release_root:
        raise Refused('RELEASE_ROOT_MISMATCH')
    expected = {e.get('path'): e for e in value['entries'] if type(e) is dict}
    if len(expected) != len(value['entries']):
        raise Refused('MANIFEST_INVALID')
    actual = {e['path']: e for e in scan(root)}
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    mismatched = sorted(p for p in set(expected) & set(actual) if expected[p] != actual[p])
    real_root = os.path.realpath(root)
    for path, entry in actual.items():
        if entry['type'] == 'l':
            full = os.path.join(root, path)
            resolved = os.path.realpath(full)
            if os.lstat(full).st_uid != root_uid or not resolved.startswith(real_root + os.sep):
                mismatched.append(path)
    if missing or extra or mismatched:
        raise Refused('MANIFEST_MISMATCH', missing=missing[:REPORT_LIMIT], extra=extra[:REPORT_LIMIT],
                      mismatched=sorted(set(mismatched))[:REPORT_LIMIT],
                      counts=[len(missing), len(extra), len(set(mismatched))])
    return {'result': 'verified', 'manifest_sha256': expect_sha256, 'entries': len(expected),
            'commit': value['commit'], 'release_root': value['release_root']}


def _member_relative(name):
    """Archive names are './x' or 'x', never absolute, never with '..'."""
    relative = name[2:] if name.startswith('./') else name
    relative = relative.rstrip('/') if relative not in ('.', './') else '.'
    return relative


def check_archive(tarball):
    """Validate every member before anything is extracted: names, types, modes, links, sizes."""
    seen, directories, total = set(), set(), 0
    with tarfile.open(tarball, 'r:') as archive:
        members = []
        for member in archive:
            if len(members) >= MAX_ENTRIES:
                raise Refused('TOO_MANY_ENTRIES')
            relative = _member_relative(member.name)
            if relative == '.':
                if not member.isdir():
                    raise Refused('TYPE_UNSUPPORTED', path=member.name)
                continue
            if member.name.startswith('/') or relative in seen or relative == NAME and not member.isreg():
                raise Refused('PATH_UNSAFE', path=member.name)
            if member.isreg():
                kind = 'f'
            elif member.isdir():
                kind = 'd'
            elif member.issym():
                kind = 'l'
            else:   # hard links, devices, FIFOs and anything else
                raise Refused('TYPE_UNSUPPORTED', path=member.name)
            if relative != NAME:
                _rule(relative, kind, member.mode, member.linkname if kind == 'l' else None)
            if member.size > MAX_MEMBER_BYTES:
                raise Refused('MEMBER_TOO_LARGE', path=member.name)
            total += member.size
            if total > MAX_ARCHIVE_BYTES:
                raise Refused('ARCHIVE_TOO_LARGE')
            seen.add(relative)
            if kind == 'd':
                directories.add(relative)
            members.append(member)
    if NAME not in seen:
        raise Refused('MANIFEST_ABSENT')
    for relative in seen:   # every parent must be a directory member, never a symlink member
        parent = relative.rpartition('/')[0]
        while parent:
            if parent not in directories:
                raise Refused('PARENT_MISSING', path=relative)
            parent = parent.rpartition('/')[0]
    return len(seen)


def extract(tarball, dest):
    """Exclusive destination, validated members only, then the stdlib 'data' filter as a second defence."""
    count = check_archive(tarball)
    os.mkdir(dest, 0o700)   # refuses an existing path, including a symlink
    with tarfile.open(tarball, 'r:') as archive:
        members = [m for m in archive if _member_relative(m.name) != '.']
        if len(members) != count:
            raise Refused('ARCHIVE_CHANGED')
        archive.extractall(dest, members=members, filter='data')
    return count


PERSONAL_PREFIXES = ('/home/', '/mnt/')
PERSONAL_BYTES = tuple(p.encode() for p in PERSONAL_PREFIXES)
SYSTEM_INTERPRETERS = ('/bin/sh', '/bin/bash', '/usr/bin/sh', '/usr/bin/bash')
ENV_INTERPRETERS = ('/usr/bin/env', '/bin/env')   # their first argument is checked as the interpreter
SYSTEM_LIBRARY_DIRS = ('/lib/', '/lib64/', '/usr/lib/', '/usr/lib64/')
ELF_DYNAMIC_TYPES = (2, 3)   # ET_EXEC and ET_DYN; relocatable objects (python.o) are not loaded
PKGCONFIG_FLAG = re.compile('-[LI](/\\S*)')
# sysconfig keys the installed interpreter uses at run time; each must lie under the prefix.
RUNTIME_SYSCONFIG_KEYS = ('prefix', 'exec_prefix', 'BINDIR', 'LIBDIR', 'LIBPL', 'LIBDEST', 'BINLIBDEST',
                          'DESTSHARED', 'INCLUDEPY', 'CONFINCLUDEPY')
LDD_LINE = (re.compile('\t(\\S+) => (/\\S+) \\(0x[0-9a-f]+\\)\\Z'), re.compile('\t(\\S+) \\(0x[0-9a-f]+\\)\\Z'),
            re.compile('\tstatically linked\\Z'))
RUNPATH_LINE = re.compile('.*\\((?:RUNPATH|RPATH)\\)\\s+Library r(?:un)?path: \\[(.*)\\]\\Z')
FINDING_LIMIT = 200
# site.py reads every *.pth file in this directory at each start: absolute lines extend sys.path
# and 'import' lines execute. The first release delivers none, so any *.pth entry refuses. This rule
# covers the .pth mechanism only; a sitecustomize or usercustomize module is not covered by it.
SITE_PACKAGES = 'python/lib/python3.13/site-packages'


def _personal(path):
    return any(path.startswith(p) for p in PERSONAL_PREFIXES)


def elf_objects(root, release_root):
    """Release paths of every dynamic ELF object (ET_EXEC or ET_DYN) under root, by content, not name."""
    found = []
    for entry in scan(root):
        if entry['type'] != 'f':
            continue
        with open(os.path.join(root, entry['path']), 'rb') as stream:
            head = stream.read(18)
        if head[:4] == b'\x7fELF' and len(head) == 18 and int.from_bytes(head[16:18], 'little') in ELF_DYNAMIC_TYPES:
            found.append(release_root + '/' + entry['path'])
    return sorted(found)


def _evidence_blocks(path, expected):
    """'== FILE' headed blocks written by the builder: exactly one non-empty block per dynamic ELF
    object of the release, and none for anything else; missing or malformed evidence fails closed."""
    with open(path, encoding='utf-8') as stream:
        text = stream.read()
    blocks, current = {}, None
    for line in text.splitlines():
        if line.startswith('== '):
            current = line[3:]
            if not current.startswith('/') or current in blocks:
                raise Refused('EVIDENCE_MALFORMED', evidence=path, line=line[:200])
            blocks[current] = []
        elif current is None:
            raise Refused('EVIDENCE_MALFORMED', evidence=path, line=line[:200])
        elif line.strip():
            blocks[current].append(line)
    missing = sorted(set(expected) - set(blocks)) or sorted(f for f, lines in blocks.items() if not lines)
    if missing:
        raise Refused('EVIDENCE_MISSING', evidence=path, file=missing[0], count=len(missing))
    extra = sorted(set(blocks) - set(expected))
    if extra:
        raise Refused('EVIDENCE_MALFORMED', evidence=path, file=extra[0])
    return blocks


def _sysconfig(root, prefix):
    """build_time_vars from the single _sysconfigdata file, as a literal: never executed."""
    import ast
    directory = os.path.join(root, 'python/lib/python3.13')
    names = [n for n in os.listdir(directory) if n.startswith('_sysconfigdata_') and n.endswith('.py')]
    if len(names) != 1:
        raise Refused('EVIDENCE_MISSING', file='python/lib/python3.13/_sysconfigdata_*.py')
    with open(os.path.join(directory, names[0]), encoding='utf-8') as stream:
        source = stream.read()
    try:
        tree = ast.parse(source)
        found = [node.value for node in tree.body if isinstance(node, ast.Assign) and len(node.targets) == 1
                 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == 'build_time_vars']
        values = ast.literal_eval(found[0]) if len(found) == 1 else None
    except (SyntaxError, ValueError, TypeError, RecursionError):
        values = None
    if type(values) is not dict or values.get('prefix') != prefix or values.get('exec_prefix') != prefix or \
            not all(isinstance(values.get(key), str) and values[key] for key in RUNTIME_SYSCONFIG_KEYS):
        raise Refused('EVIDENCE_MALFORMED', file=names[0])
    return 'python/lib/python3.13/' + names[0], values


def portability(root, release_root, ldd_path, readelf_path):
    """Actual personal-path dependencies refuse; other literal matches are findings only.

    Refused (PERSONAL_PATH_DEPENDENCY, or UNEXPECTED_DEPENDENCY for a non-system path outside the
    release), every path compared after lexical normalization: a personal release root; a shebang
    interpreter (or env's argument) of a script in python/bin or bin outside the release and the
    system shells; a run-time sysconfig path outside the prefix; an absolute pkg-config value or
    -L/-I flag outside the prefix; a library resolved or loaded by absolute path (ldd), or searched
    (RUNPATH/RPATH, with $ORIGIN expanded), outside the release and the system library
    directories. Refused as TEST_MODULES_PRESENT: the optional CPython test package, which
    --disable-test-modules must have excluded. Missing or malformed evidence refuses
    (EVIDENCE_MISSING, EVIDENCE_MALFORMED): every dynamic ELF object found by content needs exactly
    one ldd and one readelf block, and every run-time sysconfig key must be present. Refused as
    PTH_FILE_PRESENT: any entry named *.pth anywhere in the scanned release tree (no allowlist in
    the first release; nothing is interpreted or deleted); an absent site-packages directory is
    EVIDENCE_MISSING. Release-rule refusals raised by scan() keep their own codes, so an unreadable
    or unexpected entry cannot be skipped. Every '/home/' or '/mnt/' byte string not
    refused above (examples, docstrings, build-directory metadata) is recorded as a finding for
    review, not treated as proof of a dependency.
    """
    if not ROOT_PATH.fullmatch(release_root) or os.path.normpath(release_root) != release_root:
        raise Refused('RELEASE_ROOT_INVALID')
    if _personal(release_root + '/'):
        raise Refused('PERSONAL_PATH_DEPENDENCY', where='release_root')
    prefix = release_root + '/python'
    if os.path.lexists(os.path.join(root, 'python/lib/python3.13/test')):
        raise Refused('TEST_MODULES_PRESENT', path='python/lib/python3.13/test')
    entries = scan(root)   # the actual tree, once: the .pth rule here and the literal findings below
    site_packages = os.path.join(root, SITE_PACKAGES)
    if os.path.islink(site_packages) or not os.path.isdir(site_packages):
        raise Refused('EVIDENCE_MISSING', file=SITE_PACKAGES)
    for entry in entries:
        if entry['path'].rpartition('/')[2].endswith('.pth'):
            raise Refused('PTH_FILE_PRESENT', path=entry['path'], type=entry['type'])

    def dependency(candidate_path, where, **detail):
        if _personal(candidate_path):
            raise Refused('PERSONAL_PATH_DEPENDENCY', where=where, value=candidate_path, **detail)
        raise Refused('UNEXPECTED_DEPENDENCY', where=where, value=candidate_path, **detail)

    def located(candidate_path, where, system=False, **detail):
        """Classify after lexical normalization, so '..' cannot carry a path out of a prefix."""
        if not candidate_path.startswith('/'):
            dependency(candidate_path, where, **detail)
        normal = os.path.normpath(candidate_path)
        if normal == prefix or normal.startswith(release_root + '/'):
            return
        if system and normal.startswith(SYSTEM_LIBRARY_DIRS):
            return
        dependency(normal, where, **detail)

    checked = set()
    for directory in ('python/bin', 'bin'):   # shebang interpreters of the release's scripts
        for name in sorted(os.listdir(os.path.join(root, directory))):
            relative = directory + '/' + name
            path = os.path.join(root, relative)
            if os.path.islink(path) or not os.path.isfile(path):
                continue
            with open(path, 'rb') as stream:
                head = stream.read(256)
            if head.startswith(b'#!'):
                words = head[2:].split(b'\n', 1)[0].decode('utf-8', 'replace').split()
                interpreter = words[0] if words else ''
                if interpreter in ENV_INTERPRETERS:   # env resolves its argument: check that instead
                    interpreter = words[1] if len(words) > 1 else ''
                if interpreter not in SYSTEM_INTERPRETERS:
                    located(interpreter, 'shebang', path=relative)
                checked.add(relative)
    relative, values = _sysconfig(root, prefix)   # installed configuration
    checked.add(relative)
    for key in RUNTIME_SYSCONFIG_KEYS:
        located(values[key], 'sysconfig', key=key)
    pkgconfig = os.path.join(root, 'python/lib/pkgconfig')
    for name in sorted(os.listdir(pkgconfig)) if os.path.isdir(pkgconfig) else ():
        path = os.path.join(pkgconfig, name)
        if name.endswith('.pc') and not os.path.islink(path):
            where = 'python/lib/pkgconfig/' + name
            with open(path, encoding='utf-8') as stream:
                lines = stream.read().splitlines()
            if [line[7:].strip() for line in lines if line.startswith('prefix=')] != [prefix]:
                raise Refused('EVIDENCE_MALFORMED', file=where)
            for line in lines:   # every absolute variable value and -L/-I flag
                key, equals, value = line.partition('=')
                if equals and ':' not in key and value.strip().startswith('/'):
                    located(value.strip(), 'pkg-config', path=where)
                for flag in PKGCONFIG_FLAG.findall(line):
                    located(flag, 'pkg-config', path=where)
            checked.add(where)
    expected = elf_objects(root, release_root)
    for required in (prefix + '/bin/python3.13', prefix + '/lib/libpython3.13.so.1.0'):
        if required not in expected:
            raise Refused('EVIDENCE_MISSING', file=required)
    resolved = 0
    for file, lines in _evidence_blocks(ldd_path, expected).items():   # library resolution
        for line in lines:
            match = next((m for m in (p.fullmatch(line) for p in LDD_LINE) if m), None)
            if match is None:
                raise Refused('EVIDENCE_MALFORMED', evidence=ldd_path, line=line[:200])
            if match.re is LDD_LINE[0]:
                located(match.group(2), 'ldd', system=True, file=file, soname=match.group(1))
                resolved += 1
            elif match.re is LDD_LINE[1] and match.group(1).startswith('/'):   # slash DT_NEEDED or PT_INTERP
                located(match.group(1), 'ldd', system=True, file=file)
    if resolved == 0:
        raise Refused('EVIDENCE_MISSING', evidence=ldd_path)
    runpaths = 0
    for file, lines in _evidence_blocks(readelf_path, expected).items():   # search paths
        if not any('Dynamic section' in line for line in lines):
            raise Refused('EVIDENCE_MALFORMED', evidence=readelf_path, file=file)
        for line in lines:
            match = RUNPATH_LINE.fullmatch(line)
            if match is None:
                if '(RUNPATH)' in line or '(RPATH)' in line:
                    raise Refused('EVIDENCE_MALFORMED', evidence=readelf_path, line=line[:200])
                continue
            for entry in match.group(1).split(':'):
                runpaths += 1
                if entry.startswith('$ORIGIN'):   # relative to the object: must stay inside the release
                    located(os.path.dirname(file) + entry[len('$ORIGIN'):], 'runpath', file=file)
                else:
                    located(entry, 'runpath', system=True, file=file)
    # Remaining literal strings, including non-run-time metadata in the checked files (for
    # example a build directory recorded in sysconfig): review findings only.
    findings, total = [], 0
    for entry in entries:
        if entry['type'] != 'f':
            continue
        with open(os.path.join(root, entry['path']), 'rb') as stream:
            data = stream.read()
        count = sum(data.count(needle) for needle in PERSONAL_BYTES)
        if count:
            total += 1
            if len(findings) < FINDING_LIMIT:
                findings.append({'path': entry['path'], 'matches': count})
    return {'result': 'portable', 'release_root': release_root, 'checked_dependency_files': sorted(checked),
            'resolved_libraries': resolved, 'runpath_entries': runpaths, 'literal_findings': findings,
            'literal_finding_files': total,
            'finding_meaning': 'literal /home/ or /mnt/ strings outside the dependency checks; review only'}


RENAME_NOREPLACE, AT_FDCWD = 1, -100


def publish(partial, final):
    """Rename the verified partial directory to the final release root, never replacing anything.

    renameat2(RENAME_NOREPLACE) gives the property the design asks of `mv -T -n` plus a result
    check, with an exit status that cannot silently report a skipped move as success.
    """
    import ctypes
    import errno
    if os.path.dirname(partial) != os.path.dirname(final) or partial == final:
        raise Refused('PUBLISH_PATHS_INVALID')
    if os.path.lexists(final):
        raise Refused('PUBLISH_TARGET_EXISTS')
    info = os.lstat(partial)
    if not stat.S_ISDIR(info.st_mode):
        raise Refused('PUBLISH_PARTIAL_INVALID')
    libc = ctypes.CDLL(None, use_errno=True)
    renameat2 = getattr(libc, 'renameat2', None)
    if renameat2 is None:
        raise Refused('PUBLISH_UNSUPPORTED')
    renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    renameat2.restype = ctypes.c_int
    if renameat2(AT_FDCWD, os.fsencode(partial), AT_FDCWD, os.fsencode(final), RENAME_NOREPLACE) != 0:
        code = ctypes.get_errno()
        raise Refused('PUBLISH_TARGET_EXISTS' if code == errno.EEXIST else 'PUBLISH_FAILED',
                      errno=errno.errorcode.get(code, str(code)))
    fd = os.open(os.path.dirname(final), os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    if os.path.lexists(partial) or os.path.islink(final) or not os.path.isdir(final):
        raise Refused('PUBLISH_RESULT_UNEXPECTED')
    return final


def config(template, out, release_root, data_root, account):
    """Validate an administrator template against the install arguments; write it exclusively, 0644."""
    fd = os.open(template, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    with os.fdopen(fd, 'rb') as stream:
        data = stream.read(CONFIG_BYTES + 1)
    if len(data) > CONFIG_BYTES:
        raise Refused('CONFIG_INVALID')
    value = _strict(data)
    if type(value) is not dict or set(value) != CONFIG_KEYS or value != {
            'schema': 'ohk-bdw.deployment.v1', 'release_root': release_root, 'runtime_account': account,
            'data_root': data_root}:
        raise Refused('CONFIG_INVALID')
    for path in (release_root, data_root):
        if not ROOT_PATH.fullmatch(path) or os.path.normpath(path) != path:
            raise Refused('CONFIG_INVALID')
    if not ACCOUNT.fullmatch(account):
        raise Refused('CONFIG_INVALID')
    _exclusive_write(out, canonical(value) + b'\n', 0o644)
    return hashlib.sha256(canonical(value) + b'\n').hexdigest()


USAGE = {'create': ('root', 'release-root', 'commit', 'source-set', 'sonames'),
         'verify': ('root', 'expect-sha256'), 'source-set': ('root',), 'check-archive': ('tarball',),
         'extract': ('tarball', 'dest'), 'sonames': ('root', 'expect-sha256'), 'publish': ('partial', 'final'),
         'record': ('data-root', 'name', 'json'), 'portability': ('root', 'release-root', 'ldd', 'readelf'),
         'elf-objects': ('root', 'release-root'),
         'config': ('template', 'out', 'release-root', 'data-root', 'account')}
OPTIONAL = {'verify': ('release-root', 'symlink-owner-uid')}   # the uid defaults to 0 (root) at install


def _arguments(argv):
    if not argv or argv[0] not in USAGE:
        return None
    command, rest = argv[0], argv[1:]
    if len(rest) % 2:
        return None
    values = {}
    for flag, value in zip(rest[0::2], rest[1::2]):
        name = flag[2:] if flag.startswith('--') else None
        if name not in USAGE[command] + OPTIONAL.get(command, ()) or name in values or not value:
            return None
        values[name] = value
    if not set(USAGE[command]) <= set(values):
        return None
    return command, values


def main(argv=None, out=None, err=None):
    out = sys.stdout if out is None else out
    err = sys.stderr if err is None else err
    parsed = _arguments(list(sys.argv[1:] if argv is None else argv))
    if parsed is None:
        err.write(json.dumps({'result': 'usage'}) + '\n')
        return 2
    command, a = parsed
    try:
        if command == 'create':
            result = {'result': 'created', 'manifest_sha256': create(a['root'], a['release-root'], a['commit'],
                                                                     a['source-set'], a['sonames'])}
        elif command == 'verify':
            owner = a.get('symlink-owner-uid', '0')
            if not owner.isdigit():
                err.write(json.dumps({'result': 'usage'}) + '\n')
                return 2
            result = verify(a['root'], a['expect-sha256'], a.get('release-root'), int(owner))
        elif command == 'source-set':
            result = {'result': 'source-set', 'sha256': source_set(a['root'])}
        elif command == 'check-archive':
            result = {'result': 'archive-valid', 'members': check_archive(a['tarball'])}
        elif command == 'extract':
            result = {'result': 'extracted', 'members': extract(a['tarball'], a['dest'])}
        elif command == 'elf-objects':
            for path in elf_objects(a['root'], a['release-root']):
                out.write(path + '\n')
            return 0
        elif command == 'portability':
            result = portability(a['root'], a['release-root'], a['ldd'], a['readelf'])
        elif command == 'record':
            result = {'result': 'recorded', 'sha256': record(a['data-root'], a['name'], a['json'])}
        elif command == 'publish':
            result = {'result': 'published', 'release_root': publish(a['partial'], a['final'])}
        elif command == 'sonames':
            for name in load(a['root'], a['expect-sha256'])['required_sonames']:
                out.write(name + '\n')
            return 0
        else:
            result = {'result': 'config-written', 'sha256': config(a['template'], a['out'], a['release-root'],
                                                                   a['data-root'], a['account'])}
    except Refused as refusal:
        err.write(json.dumps(dict(refusal.detail, result='refused', code=refusal.code), sort_keys=True) + '\n')
        return 1
    except (OSError, tarfile.TarError, UnicodeError, ValueError) as error:
        err.write(json.dumps({'result': 'refused', 'code': 'IO_ERROR', 'error': type(error).__name__}) + '\n')
        return 1
    out.write(json.dumps(result, sort_keys=True) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
