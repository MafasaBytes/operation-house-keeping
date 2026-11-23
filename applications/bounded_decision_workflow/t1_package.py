"""Safe new output roots and failure-retaining, final-record-last publication.

This module does not infer or approve a producer manifest's semantic edge set.
"""
import os
from pathlib import Path, PurePosixPath
import re

from .t1_contracts import canonical_bytes, refuse


def safe_new_dir(path, target='/argv/output-dir'):
    candidate = Path(path)
    absolute = Path(os.path.abspath(candidate))
    if '..' in candidate.parts or candidate.name in ('.', '..'):
        refuse('SIM_OUTPUT_UNSAFE', 0, target, 5)
    for component in (absolute, *absolute.parents):
        if component.is_symlink():
            refuse('SIM_OUTPUT_UNSAFE', 0, target, 5)
    if absolute.exists() or not absolute.parent.is_dir():
        refuse('SIM_OUTPUT_UNSAFE', 0, target, 5)
    return absolute


def member_path(path):
    parts = PurePosixPath(path)
    if parts.is_absolute() or any(x in ('.', '..', '') for x in path.split('/')) or \
            re.fullmatch(r'(objects|evidence|receipt)(/[A-Za-z0-9_.-]+)+', path) is None:
        refuse('SIM_REFERENCE_INVALID', 1, '/M/members')
    return path


def manifest_bytes(value):
    wire = canonical_bytes(value)
    if len(wire) > 32768:
        refuse('SIM_RESOURCE_LIMIT', 7, '/M', 4)
    return wire


def _fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


class Publication:
    """Fresh root, immutable members, PARTIAL preserved on every write failure."""
    def __init__(self, output, *, final='manifest.json', target='/M'):
        allowed = {'manifest.json': 7, 'handoff.json': 8, 'workflow-receipt.json': 9, 'report.json': 7}
        if final not in allowed:
            refuse('SIM_OUTPUT_UNSAFE', 0, '/argv/output-dir', 5)
        self.order = allowed[final]
        self.root = safe_new_dir(output)
        self.final, self.target = final, target
        try:
            self.root.mkdir()
            self.write('PARTIAL', b'publication incomplete\n')
            _fsync_dir(self.root.parent)
        except OSError:
            refuse('SIM_PUBLICATION_INCOMPLETE', self.order, target, 5)

    def write(self, relative, wire):
        if not isinstance(wire, bytes):
            raise TypeError('publication requires frozen bytes')
        if relative not in ('PARTIAL', self.final) and relative != self.final + '.tmp':
            member_path(relative)
        destination = self.root / relative
        for parent in destination.parents:
            if parent == self.root.parent:
                break
            if parent.is_symlink():
                refuse('SIM_PUBLICATION_INCOMPLETE', self.order, self.target, 5)
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, 'wb') as stream:
                stream.write(wire)
                stream.flush()
                os.fsync(stream.fileno())
            # Persist each newly introduced nested directory entry bottom-up.
            parent = destination.parent
            while True:
                _fsync_dir(parent)
                if parent == self.root.parent:
                    break
                parent = parent.parent
        except OSError:
            refuse('SIM_PUBLICATION_INCOMPLETE', self.order, self.target, 5)

    def finish(self, wire):
        if self.final == 'manifest.json' and len(wire) > 32768:
            refuse('SIM_RESOURCE_LIMIT', 7, '/M', 4)
        temporary = self.final + '.tmp'
        self.write(temporary, wire)
        try:
            if (self.root / self.final).exists():
                refuse('SIM_PUBLICATION_INCOMPLETE', self.order, self.target, 5)
            os.rename(self.root / temporary, self.root / self.final)
            _fsync_dir(self.root)
            # PARTIAL remains until every final-file publication step succeeded.
            (self.root / 'PARTIAL').unlink()
            _fsync_dir(self.root)
        except BaseException:
            # Marker removal plus directory-sync failure is ambiguous. Restore
            # conservative incomplete evidence; never delete retained final.
            try:
                fd = os.open(self.root / 'PARTIAL', os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW, 0o600)
                os.write(fd, b'publication incomplete\n')
                os.fsync(fd)
                os.close(fd)
                _fsync_dir(self.root)
            except OSError:
                pass
            refuse('SIM_PUBLICATION_INCOMPLETE', self.order, self.target, 5)

    def seal_existing(self, relative, wire):
        """Freeze a diagnostic DB produced directly inside this output root."""
        if not relative.startswith('evidence/db/'):
            refuse('SIM_PUBLICATION_INCOMPLETE', self.order, self.target, 5)
        path = self.root / member_path(relative)
        try:
            if path.is_symlink() or path.read_bytes() != wire:
                refuse('SIM_PUBLICATION_INCOMPLETE', self.order, self.target, 5)
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
            _fsync_dir(path.parent)
        except OSError:
            refuse('SIM_PUBLICATION_INCOMPLETE', self.order, self.target, 5)
