"""Test-only pinned-fetch S7 substitution, revision 3; revisions 1 and 2 are retained unchanged.

Differences from revision 2 (SHA-256 00e935e858d598e6e2301f597b46a5375652bf9f550b4e4153fc90a24a045285),
and nothing else:

* Teardown is a pluggy new-style wrapper. pytest's own runner teardown
  (``teardown_exact``) always completes first, the substituted ``clone`` is
  always restored in ``finally``, and the call-count assertion is raised only
  afterwards. In revision 2 the assertion was raised by a plain hook that runs
  before the runner's, so a failed node left pytest's setup state dirty and
  the next node errored with "previous item was not torn down properly"
  (rel2-L3-green2). The mismatch still fails its own node.
* ``REL4_GIT_AS_LIMIT`` (optional, bytes): the soft RLIMIT_AS applied to the
  substituted ``git fetch`` child only (and so its upload-pack / pack-objects /
  index-pack descendants), between the inherited soft and hard limits. The
  pytest process and application children are unaffected. Unset: inherited.
* ``REL4_FETCH_EVIDENCE_DIR`` (optional): per fetch, a JSON record of the
  effective limits (a probe child run with the same pre-exec), the pytest
  process's /proc/self/limits, CPU count, Git version, RUSAGE_CHILDREN
  max-RSS before/after (resident set, not address space), exit status and
  elapsed time, plus a GIT_TRACE2_EVENT stream (observation only). Unset:
  nothing is written and the fetch environment is inherited unchanged.

Revision 2 description follows.


Same owner-approved substitution as ``slice5_pinned_fetch_adapter`` (commit
4a41f7b): it replaces only the S7 release-test module's ``clone`` for that
module's two nodes. The test file, both assertion bodies and every child
command stay byte-identical. Each substituted call creates a fresh,
independent Git database (no alternates, hardlinks, shallow boundary,
filter/promisor dependency, network acquisition or result reuse).

Differences from revision 1, and nothing else:

* The retained pinned ref and OID name the release checkout revision
  (``refs/heads/frozen-release`` at FROZEN_OID), not the earlier main pin.
* Operation-specific serving-side limits. Over local ``file://`` transport Git
  removes GIT_CONFIG_PARAMETERS before starting the serving ``upload-pack``, so
  ``git -c ... fetch`` never reaches the serving ``pack-objects`` (the reason
  the rejected pack.threads repair, ledger record 3239, had no effect). The
  fetch therefore names the serving command explicitly with SERVING_CONFIG.
  The inherited RLIMIT_AS (512 MiB) is unchanged; no application limit is
  raised and no limit is inherited into Git beyond what the controller sets.
* ``pinned_clone(..., serving=False)`` reproduces the revision-1 fetch argv
  exactly and exists only for RED qualification.
"""
import json
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

import pytest

FROZEN_REF = 'refs/heads/frozen-release'
FROZEN_OID = 'f28de9e900c700d910eb5edf2b0e6f8c336472fe'
NODES = {'test_two_clean_roots_twelve_constructions_and_exact_replay': 2,
         'test_accepted_s6_archive_recovers_in_clean_matching_build': 1}
CONFIG = [('gc.auto', '0'), ('maintenance.auto', 'false'),
          ('core.logAllRefUpdates', 'false'), ('core.packedGitWindowSize', '32m'),
          ('core.packedGitLimit', '256m'), ('advice.detachedHead', 'false')]
# Serving-side (upload-pack / pack-objects) limits; operation-specific.
SERVING_CONFIG = [('pack.threads', '1'), ('pack.windowMemory', '64m'),
                  ('pack.deltaCacheSize', '16m'), ('core.deltaBaseCacheLimit', '16m'),
                  ('core.packedGitWindowSize', '32m'), ('core.packedGitLimit', '256m')]
FETCH = ['fetch', '-q', '--no-tags', '--no-recurse-submodules']
LIMIT_ENV = 'REL4_GIT_AS_LIMIT'
EVIDENCE_ENV = 'REL4_FETCH_EVIDENCE_DIR'
_FETCHES = [0]


def _git_limit():
    raw = os.environ.get(LIMIT_ENV)
    if raw is None:
        return None
    value = int(raw)
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    if hard == resource.RLIM_INFINITY or not soft <= value <= hard:
        raise ValueError('REL4_GIT_AS_LIMIT outside inherited finite (soft, hard)')
    return value


def _preexec(limit):
    if limit is None:
        return None
    def apply():
        resource.setrlimit(resource.RLIMIT_AS, (limit, resource.getrlimit(resource.RLIMIT_AS)[1]))
    return apply


def _fetch(path, root, serving):
    argv = fetch_argv(path, root, serving)
    limit = _git_limit()
    pre = _preexec(limit)
    env = dict(os.environ)
    evidence = os.environ.get(EVIDENCE_ENV)
    record = None
    if evidence:
        _FETCHES[0] += 1
        stem = Path(evidence) / ('fetch-%02d' % _FETCHES[0])
        trace = Path(str(stem) + '.trace2.json')
        env['GIT_TRACE2_EVENT'] = str(trace)
        probe = subprocess.check_output(
            [sys.executable, '-c', 'import resource;print(resource.getrlimit(resource.RLIMIT_AS))'],
            preexec_fn=pre).decode().strip()
        record = dict(call=_FETCHES[0], path=str(path), argv=argv, requested_git_as_limit=limit,
                      effective_child_rlimit_as=probe,
                      pytest_rlimit_as=list(resource.getrlimit(resource.RLIMIT_AS)),
                      pytest_proc_limits=Path('/proc/self/limits').read_text(),
                      pytest_pid=os.getpid(), cpu_count=os.cpu_count(),
                      git_version=subprocess.check_output(['git', '--version']).decode().strip(),
                      rusage_children_maxrss_kib_before=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
    started = time.monotonic()
    status = None
    try:
        status = subprocess.call(argv, env=env, preexec_fn=pre)
    finally:
        if record is not None:
            raw = trace.read_bytes() if trace.exists() else None
            record.update(exit=status, elapsed_seconds=time.monotonic() - started,
                          rusage_children_maxrss_kib_after=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                          trace2=str(trace), trace2_bytes=None if raw is None else len(raw))
            with open(str(stem) + '.json', 'x') as stream:
                json.dump(record, stream, sort_keys=True)
    if status:
        raise subprocess.CalledProcessError(status, argv)


def upload_pack_command():
    return 'git ' + ' '.join('-c %s=%s' % pair for pair in SERVING_CONFIG) + ' upload-pack'


def fetch_argv(path, root, serving=True):
    argv = ['git', '-C', str(path), *FETCH]
    if serving:
        argv.append('--upload-pack=' + upload_pack_command())
    return argv + ['file://' + str(root), '+' + FROZEN_REF + ':' + FROZEN_REF]


def _out(cwd, *args):
    return subprocess.check_output(['git', '-C', str(cwd), *args]).decode().strip()


def pinned_clone(root, path, commit='HEAD', serving=True):
    """Fresh independent database at the pinned history; helper substitution only."""
    revision = _out(root, 'rev-parse', commit)
    assert _out(root, 'rev-parse', FROZEN_REF) == FROZEN_OID, \
        'retained pinned source ref absent or moved'
    path = Path(path)
    subprocess.check_call(['git', 'init', '--template=', '-q', str(path)])
    for k, v in CONFIG:
        subprocess.check_call(['git', '-C', str(path), 'config', k, v])
    _fetch(path, root, serving)
    assert _out(path, 'rev-parse', FROZEN_REF) == FROZEN_OID, 'fetched pin mismatch'
    assert not (path / '.git/objects/info/alternates').exists()
    paths = ['/applications/', '/backend/']
    if commit == 'HEAD':
        paths += [
            '/docs/superpowers/reports/2026-09-23-reassessment-preparation/package.zip',
            '/docs/superpowers/specs/2026-09-16-maintained-admissibility-enforcement-shared-reference-corrected-design.md',
            '/docs/superpowers/reports/2026-09-16-maintained-admissibility-amendment/AMENDMENT.md',
            '/docs/superpowers/reports/2026-09-16-maintained-admissibility-amendment/policy.json',
            '/docs/superpowers/reports/2026-09-16-maintained-admissibility-amendment/schemas.json',
            '/docs/superpowers/reports/2026-09-16-maintained-admissibility-consolidation/CONTRACT-AND-PLAN.md',
            '/docs/superpowers/reports/2026-09-16-maintained-admissibility-consolidation/build.schema.json',
        ]
    subprocess.run(['git', '-C', str(path), 'sparse-checkout', 'set', '--no-cone', '--stdin'],
                   input='\n'.join(paths) + '\n', text=True, check=True)
    subprocess.check_call(['git', '-C', str(path), 'checkout', '--quiet', '--detach', revision])
    assert not subprocess.check_output(['git', '-C', str(path), 'status', '--porcelain'])
    assert not (path / '.git/objects/info/alternates').exists()
    assert _out(path, 'rev-parse', 'HEAD') == revision
    for name in subprocess.check_output(
            ['git', '-C', str(path), 'ls-files', 'applications', 'backend']).decode().splitlines():
        assert (path / name).read_bytes() == subprocess.check_output(
            ['git', '-C', str(path), 'show', revision + ':' + name])
    return path


def pytest_runtest_setup(item):
    if item.name not in NODES:
        return
    module = item.module
    assert not hasattr(module, '_pinned_fetch_restore'), 'adapter already active'
    original = module.clone
    calls = []

    def substituted(path, commit='HEAD'):
        calls.append((str(path), commit))
        return pinned_clone(module.ROOT, path, commit)

    module._pinned_fetch_restore = (original, calls, NODES[item.name])
    module.clone = substituted


@pytest.hookimpl(wrapper=True)
def pytest_runtest_teardown(item):
    if item.name not in NODES:
        return (yield)
    module = item.module
    try:
        result = yield
    finally:
        state = getattr(module, '_pinned_fetch_restore', None)
        if state is not None:
            module.clone = state[0]
            del module._pinned_fetch_restore
    assert state is not None, 'adapter state absent at teardown'
    original, calls, expected = state
    assert len(calls) == expected, ('unexpected substituted clone calls', calls)
    return result
