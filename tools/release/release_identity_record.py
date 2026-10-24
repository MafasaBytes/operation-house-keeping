"""Write RELEASE-IDENTITY.json for one commit (build host only; reads Git, creates one new file).

Usage: release_identity_record.py REPOSITORY COMMIT INSTALL_ROOT OUTPUT
INSTALL_ROOT must be the absolute, normalized, symlink-free prefix of app/ on the
target, because the verifier compares it with the resolved root. The file records
Git objects only. Release authenticity is the separately signed
RELEASE-MANIFEST.json; this file proves nothing about who built the release.
"""
import base64
import json
import os
import re
import subprocess
import sys


def git(repository, *args):
    return subprocess.check_output(['git', '--no-optional-locks', '-C', repository, *args], timeout=60)


def main(argv=None):
    repository, commit, install_root, output = sys.argv[1:] if argv is None else argv
    if not os.path.isabs(install_root) or os.path.normpath(install_root) != install_root:
        raise SystemExit('install root must be an absolute normalized path')
    commit = git(repository, 'rev-parse', '--verify', commit + '^{commit}').decode().strip()
    commit_object = git(repository, 'cat-file', 'commit', commit)
    tree = re.match(rb'tree ([0-9a-f]{40})\n', commit_object).group(1).decode()
    root_tree = git(repository, 'cat-file', 'tree', tree)
    entries = []
    listing = git(repository, 'ls-tree', '-r', '-z', '--full-tree', commit, '--', 'applications', 'backend')
    for line in listing.split(b'\0'):
        if not line:
            continue
        meta, path = line.split(b'\t', 1)
        mode, kind, oid = meta.decode().split(' ')
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise SystemExit('unsupported tree entry: ' + path.decode())
        entries.append([path.decode(), mode, oid])
    record = dict(schema='bdw.release-identity.v1', install_root=install_root, commit=commit,
                  commit_object=base64.b64encode(commit_object).decode(),
                  root_tree_object=base64.b64encode(root_tree).decode(), entries=sorted(entries))
    data = (json.dumps(record, sort_keys=True, indent=1) + '\n').encode()
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        os.unlink(output)
        raise
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
