"""External Slice 5 process capture, revision 4; revision 3 is retained unchanged.

Only difference from revision 3 (SHA-256 e6dc1df121942d31c4682be2d6a2c1cfad6472c21912ab662b41d4d550815069):
the RLIMIT_AS applied to the captured process is an explicit ``address_space``
(soft, hard) pair. The default is revision 3's exact (512 MiB, 512 MiB). The
soft limit that governs pytest and application processes must remain 512 MiB;
only the hard ceiling may be raised, to at most ADDRESS_SPACE_HARD_MAX, so
that an explicitly named harness operation (the substituted Git fetch) can
raise its own soft limit. No unlimited value is accepted.

Revision 3 description follows.

The caller owns a durable, complete per-operation write reservation and checks
all approved ceilings before calling capture. This module does not infer that a
hard storage/path boundary has been approved or provisioned.
No application source or production resource guard is modified here.
"""

import hashlib
import os
from pathlib import Path
import resource
import selectors
import signal
import subprocess
import time


STREAM_LIMIT = 262144
ADDRESS_SPACE_SOFT = 536870912
ADDRESS_SPACE_HARD_MAX = 2147483648
READ_CHUNK = 8192


def confined_environment(base, writable_root):
    """Route cooperative children; separately account for noncooperative paths."""
    root = Path(writable_root).resolve(strict=True)
    paths = {name: root / name for name in ('tmp', 'home', 'cache', 'config', 'data')}
    if not all(path.is_dir() and path.resolve(strict=True).is_relative_to(root)
               for path in paths.values()):
        raise ValueError('missing confined temporary or home directory')
    env = dict(base)
    env.update(TMPDIR=str(paths['tmp']), TMP=str(paths['tmp']), TEMP=str(paths['tmp']),
               HOME=str(paths['home']), XDG_CACHE_HOME=str(paths['cache']),
               XDG_CONFIG_HOME=str(paths['config']), XDG_DATA_HOME=str(paths['data']),
               PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1')
    return env


def capture(argv, *, cwd, env, stdout_path, stderr_path, timeout_seconds,
            reservation, operation, clone_object_limit=None,
            address_space=(ADDRESS_SPACE_SOFT, ADDRESS_SPACE_SOFT)):
    """Run one separately reserved operation and retain bounded streams.

    The reservation must include all descendant writes, including explicit /tmp,
    home and shm paths and children that replace inherited environment settings.
    Callers may establish that bound by source accounting or a separately
    authorized filesystem mechanism. Environment variables alone do not do it.
    A per-file limit is permitted only for an inventoried Git clone operation;
    pytest and application children receive no blanket RLIMIT_FSIZE.
    """
    required = {'id', 'durable', 'logical_bytes', 'files', 'directories',
                'physical_bytes', 'stdout_stderr_bytes', 'write_paths_accounted'}
    if not isinstance(reservation, dict) or not required.issubset(reservation):
        raise ValueError('complete operation reservation required before spawn')
    if reservation['durable'] is not True or reservation['write_paths_accounted'] is not True:
        raise ValueError('durable reservation and complete write-path accounting required')
    if any(type(reservation[k]) is not int or reservation[k] < 0 for k in
           ('logical_bytes', 'files', 'directories', 'physical_bytes',
            'stdout_stderr_bytes')):
        raise ValueError('invalid operation reservation')
    if reservation['stdout_stderr_bytes'] < STREAM_LIMIT:
        raise ValueError('stream allowance below capture limit')
    soft, hard = address_space
    if (type(soft) is not int or type(hard) is not int or soft != ADDRESS_SPACE_SOFT
            or not soft <= hard <= ADDRESS_SPACE_HARD_MAX):
        raise ValueError('address space must be (512 MiB, finite hard <= 2 GiB)')
    if operation not in ('pytest', 'application', 'git-clone'):
        raise ValueError('unknown operation')
    if (clone_object_limit is None) != (operation != 'git-clone'):
        raise ValueError('Git file limit requires clone-specific source inventory')
    if clone_object_limit is not None and clone_object_limit <= 0:
        raise ValueError('invalid Git object limit')
    for path in (stdout_path, stderr_path):
        path = Path(path)
        if not path.parent.is_dir() or path.exists() or path.is_symlink():
            raise ValueError('stream target is not an absent file in an existing directory')

    def limits():
        resource.setrlimit(resource.RLIMIT_AS, (soft, hard))
        if clone_object_limit is not None:
            resource.setrlimit(resource.RLIMIT_FSIZE,
                               (clone_object_limit, clone_object_limit))

    def stop(child):
        try: os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError: pass

    digests = {'stdout': hashlib.sha256(), 'stderr': hashlib.sha256()}
    lengths = {'stdout': 0, 'stderr': 0}
    reason = None
    started = time.monotonic()
    with Path(stdout_path).open('xb') as stdout, Path(stderr_path).open('xb') as stderr:
        try:
            child = subprocess.Popen(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, preexec_fn=limits,
                                     start_new_session=True)
        except BaseException as exc:
            return {'exit': None, 'termination': 'spawn_failed',
                    'incomplete_evidence': True, 'error': repr(exc),
                    'stdout_bytes': 0, 'stderr_bytes': 0,
                    'stdout_sha256': digests['stdout'].hexdigest(),
                    'stderr_sha256': digests['stderr'].hexdigest(),
                    'elapsed_seconds': time.monotonic() - started}
        streams = {'stdout': stdout, 'stderr': stderr}
        selector = selectors.DefaultSelector()
        selector.register(child.stdout, selectors.EVENT_READ, 'stdout')
        selector.register(child.stderr, selectors.EVENT_READ, 'stderr')
        try:
            while selector.get_map():
                if time.monotonic() - started > timeout_seconds and reason is None:
                    reason = 'timeout'
                    stop(child)
                for key, _ in selector.select(0.1):
                    wire = os.read(key.fileobj.fileno(), READ_CHUNK)
                    if not wire:
                        selector.unregister(key.fileobj)
                        continue
                    remaining = STREAM_LIMIT - sum(lengths.values())
                    retained = wire[:max(0, remaining)]
                    if retained:
                        streams[key.data].write(retained)
                        digests[key.data].update(retained)
                        lengths[key.data] += len(retained)
                    if len(wire) > len(retained) and reason is None:
                        reason = 'stream_truncated'
                        stop(child)
            status = child.wait()
        except BaseException as exc:
            reason = 'controller_interrupted' if isinstance(exc, KeyboardInterrupt) else 'controller_error'
            error = repr(exc)
            stop(child)
            status = child.wait()
        finally:
            selector.close()
        # A child killed by a signal cannot complete its output protocol.  In
        # revision 2 this left termination unset and marked evidence complete.
        if status < 0 and reason is None:
            reason = 'child_signal'
        try:
            stdout.flush(); stderr.flush()
            os.fsync(stdout.fileno()); os.fsync(stderr.fileno())
        except OSError as exc:
            reason = 'retention_error'
            error = repr(exc)
    return {'exit': status, 'termination': reason, 'incomplete_evidence': reason is not None,
            'error': error if reason in ('controller_interrupted', 'controller_error', 'retention_error') else None,
            'stdout_bytes': lengths['stdout'], 'stderr_bytes': lengths['stderr'],
            'stdout_sha256': digests['stdout'].hexdigest(),
            'stderr_sha256': digests['stderr'].hexdigest(),
            'elapsed_seconds': time.monotonic() - started}
