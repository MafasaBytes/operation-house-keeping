"""Test-only pinned-fetch S7 substitution, revision 2; revision 1 is retained unchanged.

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
import subprocess
from pathlib import Path

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
    subprocess.check_call(fetch_argv(path, root, serving))
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


def pytest_runtest_teardown(item):
    if item.name not in NODES:
        return
    module = item.module
    original, calls, expected = module._pinned_fetch_restore
    module.clone = original
    del module._pinned_fetch_restore
    assert len(calls) == expected, ('unexpected substituted clone calls', calls)
