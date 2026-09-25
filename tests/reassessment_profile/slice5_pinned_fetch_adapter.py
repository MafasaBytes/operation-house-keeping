"""Owner-approved test-only pinned-fetch substitution for the S7 clean-root helper.

Second harness commit of the consolidated release plan (SHA-256
51519fefad1b386c88124e3e95dc54d15e9942c2e4ff3fec5efafe60afd3f9b4). Loaded as a
pytest plugin through the external v2 reporter's pytest argv. It substitutes
only the S7 release-test module's ``clone`` function for that module's two
nodes; the test file on disk, both assertion bodies and every child command
stay byte-identical. Each substituted call still creates a fresh, independent
Git database (its own object files; no alternates, hardlinks, shallow
boundary, filter/promisor dependency, network acquisition or result reuse) by
``git init`` plus a fetch of the explicitly retained pinned ref from the test
ROOT's own database, because the ROOT is a detached c321 checkout whose HEAD
alone does not name a fetchable ref. The frozen preflight and fetch argv
below are the manifest this commit is required to carry.
"""
import subprocess
from pathlib import Path

FROZEN_REF = 'refs/heads/frozen-main'
FROZEN_OID = '086a3d8f401478315fb5cdad31f336442a323cf2'
NODES = {'test_two_clean_roots_twelve_constructions_and_exact_replay': 2,
         'test_accepted_s6_archive_recovers_in_clean_matching_build': 1}
CONFIG = [('gc.auto', '0'), ('maintenance.auto', 'false'),
          ('core.logAllRefUpdates', 'false'), ('core.packedGitWindowSize', '32m'),
          ('core.packedGitLimit', '256m'), ('advice.detachedHead', 'false')]
FETCH = ['fetch', '-q', '--no-tags', '--no-recurse-submodules']


def _out(cwd, *args):
    return subprocess.check_output(['git', '-C', str(cwd), *args]).decode().strip()


def pinned_clone(root, path, commit='HEAD'):
    """Fresh independent database at the pinned history; helper substitution only."""
    revision = _out(root, 'rev-parse', commit)
    assert _out(root, 'rev-parse', FROZEN_REF) == FROZEN_OID, \
        'retained pinned source ref absent or moved'
    path = Path(path)
    subprocess.check_call(['git', 'init', '--template=', '-q', str(path)])
    for k, v in CONFIG:
        subprocess.check_call(['git', '-C', str(path), 'config', k, v])
    subprocess.check_call(['git', '-C', str(path), *FETCH,
                           'file://' + str(root), '+' + FROZEN_REF + ':' + FROZEN_REF])
    assert _out(path, 'rev-parse', FROZEN_REF) == FROZEN_OID, 'fetched pin mismatch'
    assert not (path / '.git/objects/info/alternates').exists()
    # Materialization mirrors the retained helper's owner-approved sparse set.
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
