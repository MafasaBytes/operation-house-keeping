"""L1 installed-release source witness. Real Git is used only as an independent oracle.

The production-boundary tests run the production identity functions in subprocesses
against one committed fixture tree observed through both witnesses. Run with an
isolated ext4 --basetemp: the mode cases rely on POSIX permission bits.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from applications.bounded_decision_workflow import release_identity
from applications.bounded_decision_workflow.errors import WorkflowInputError
from applications.bounded_decision_workflow.measurement_wire import Work

ROOT = Path(__file__).parents[3]
TOOL = ROOT / 'tools/release/release_identity_record.py'
FILES = {'applications/__init__.py': b'', 'applications/pkg/a.py': b'A = 1\n',
         'applications/pkg-data.json': b'{}\n', 'backend/__init__.py': b'', 'backend/b.py': b'B = 2\n',
         'docs/outside.md': b'not installed\n'}
DEFECTS = ['extra_pycache', 'changed_byte', 'missing_file', 'symlink', 'git_directory', 'relocated',
           'forged_commit_object', 'record_mode_flip', 'consistent_byte_change', 'consistent_drop',
           'unsorted_entries', 'duplicate_entry', 'installed_exec_added', 'installed_exec_removed']
PROBE = '''import json, sys
sys.path.insert(0, sys.argv[1])
from applications.bounded_decision_workflow import measurement_build
from applications.bounded_decision_workflow.checked_contracts import CheckedRefusal
from applications.bounded_decision_workflow.checked_runtime import ExecutableBuild, _current_build
from applications.bounded_decision_workflow.errors import WorkflowInputError
out = {'root': str(measurement_build.build.ROOT)}
try:
    out['nm'] = measurement_build.identity().decode()
except WorkflowInputError as e:
    out['nm_refused'] = type(e).__name__
try:
    out['ct'] = _current_build(ExecutableBuild()).decode()
except CheckedRefusal as e:
    out['ct_refused'] = [e.code, e.stage, e.exit_class]
sys.stdout.write(json.dumps(out))
'''


def git_env(home):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(HOME=str(home), GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_AUTHOR_NAME='t',
               GIT_AUTHOR_EMAIL='t@example.invalid', GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@example.invalid')
    return env


def commit_all(repository, env, *paths):
    for args in (['init', '-q'], ['add', '-A', '--', *paths], ['commit', '-q', '-m', 'fixture']):
        subprocess.run(['git', '-C', str(repository), *args], check=True, env=env, timeout=60)
    return subprocess.check_output(['git', '-C', str(repository), 'rev-parse', 'HEAD'], env=env,
                                   timeout=60).decode().strip()


def probe(root, env, flags=('-I', '-B')):
    done = subprocess.run([sys.executable, *flags, '-c', PROBE, str(root)], env=env,
                          capture_output=True, timeout=300)
    assert done.returncode == 0, done.stderr.decode(errors='replace')
    return json.loads(done.stdout)


def test_object_ids_match_published_git_vectors():
    assert release_identity._object_id(b'blob', b'') == 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391'
    assert release_identity._object_id(b'blob', b'hello\n') == 'ce013625030ba8dba906f756967f9e9ca394464a'
    assert release_identity._tree({}) == '4b825dc642cb6eb9a060e54bf8d69288fbee4904'


@pytest.fixture
def installed(tmp_path):
    repository = tmp_path / 'repository'
    for name, data in FILES.items():
        (repository / name).parent.mkdir(parents=True, exist_ok=True)
        (repository / name).write_bytes(data)
        os.chmod(repository / name, 0o644)
    os.chmod(repository / 'applications/pkg/a.py', 0o755)   # one 100755 entry
    env = git_env(tmp_path)
    commit = commit_all(repository, env, '.')
    root = (tmp_path / 'install').resolve()
    for name in FILES:
        if name.split('/')[0] in release_identity.TOPS:
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(repository / name, root / name)   # bytes and permission bits
    subprocess.run([sys.executable, '-I', str(TOOL), str(repository), commit, str(root),
                    str(root / release_identity.NAME)], check=True, env=env)
    return root, commit


def test_installed_tree_yields_the_commit_and_exact_paths(installed):
    root, commit = installed
    assert release_identity.verified_source(root) == (commit, [
        'applications/__init__.py', 'applications/pkg-data.json', 'applications/pkg/a.py',
        'backend/__init__.py', 'backend/b.py'])


def test_installed_mode_reads_are_counted_without_sha256_hash_bytes(installed):
    root, commit = installed
    record = json.loads((root / release_identity.NAME).read_bytes())
    work = Work()
    release_identity.verified_source(root, work)
    sizes = [(root / release_identity.NAME).stat().st_size] + [(root / p).stat().st_size for p, _, _ in record['entries']]
    assert work.physical['build_read_operations'] == len(sizes)
    assert work.physical['build_bytes_read'] == sum(sizes)
    assert 'build_hash_bytes' not in work.physical


@pytest.mark.parametrize('defect', DEFECTS)
def test_any_divergence_refuses(installed, defect):
    root, commit = installed
    record_path = root / release_identity.NAME
    record = json.loads(record_path.read_bytes())
    entries = record['entries']
    if defect == 'extra_pycache':
        (root / 'applications/pkg/__pycache__').mkdir()
        (root / 'applications/pkg/__pycache__/a.cpython-313.pyc').write_bytes(b'x')
    elif defect == 'changed_byte':
        (root / 'backend/b.py').write_bytes(b'B = 3\n')
    elif defect == 'missing_file':
        (root / 'applications/pkg/a.py').unlink()
    elif defect == 'symlink':
        (root.parent / 'b-copy.py').write_bytes(FILES['backend/b.py'])
        (root / 'backend/b.py').unlink()
        (root / 'backend/b.py').symlink_to(root.parent / 'b-copy.py')
    elif defect == 'git_directory':
        (root / '.git').mkdir()
    elif defect == 'relocated':
        record['install_root'] = str(root) + '-elsewhere'
    elif defect == 'forged_commit_object':
        record['commit_object'] = record['commit_object'][:-4] + 'AAAA'
    elif defect == 'record_mode_flip':
        # A record-only mode change alters the recomputed tree, so the tree gate refuses.
        entries[-1][1] = '100755'
    elif defect == 'consistent_byte_change':
        (root / 'backend/b.py').write_bytes(b'B = 3\n')
        entries[-1][2] = release_identity._object_id(b'blob', b'B = 3\n')
    elif defect == 'consistent_drop':
        (root / 'backend/b.py').unlink()
        del entries[-1]
    elif defect == 'unsorted_entries':
        entries.reverse()
    elif defect == 'duplicate_entry':
        entries.append(list(entries[-1]))
    elif defect == 'installed_exec_added':
        # Record and tree stay valid; only the installed owner-execute bit differs.
        os.chmod(root / 'backend/b.py', 0o755)
    elif defect == 'installed_exec_removed':
        os.chmod(root / 'applications/pkg/a.py', 0o644)
    if record != json.loads(record_path.read_bytes()):
        record_path.write_bytes(json.dumps(record).encode())
    with pytest.raises(WorkflowInputError):
        release_identity.verified_source(root)


@pytest.fixture(scope='module')
def matched(tmp_path_factory):
    """One committed tree observed through both witnesses: same commit, bytes, interpreter, environment."""
    base = tmp_path_factory.mktemp('matched')
    checkout = base / 'checkout'
    for top in release_identity.TOPS:
        shutil.copytree(ROOT / top, checkout / top, ignore=shutil.ignore_patterns('__pycache__'))
    for path in checkout.rglob('*'):
        os.chmod(path, 0o755 if path.is_dir() else 0o644)   # deterministic modes on any source filesystem
    env = git_env(base)
    commit = commit_all(checkout, env, *release_identity.TOPS)
    installed = (base / 'installed').resolve()
    for top in release_identity.TOPS:
        shutil.copytree(checkout / top, installed / top)
    subprocess.run([sys.executable, '-I', str(TOOL), str(checkout), commit, str(installed),
                    str(installed / release_identity.NAME)], check=True, env=env)
    no_git = base / 'empty-path'
    no_git.mkdir()
    return checkout.resolve(), installed, commit, env, no_git


def test_installed_identity_equals_git_identity_without_git(matched):
    checkout, installed, commit, env, no_git = matched
    git_side = probe(checkout, env)
    installed_side = probe(installed, dict(env, PATH=str(no_git)))
    assert (git_side['root'], installed_side['root']) == (str(checkout), str(installed))
    assert 'nm_refused' not in installed_side and 'ct_refused' not in installed_side, installed_side
    assert json.loads(git_side['nm'])['checkpoint'] == commit
    assert installed_side['nm'] == git_side['nm']
    assert installed_side['ct'] == git_side['ct']


def test_checkout_with_release_record_refuses(matched, tmp_path):
    checkout, installed, commit, env, no_git = matched
    stray = tmp_path / 'stray-checkout'
    shutil.copytree(checkout, stray, symlinks=True)
    control = probe(stray, env)   # twin: the same copied checkout admits before the record appears
    assert 'nm_refused' not in control and json.loads(control['nm'])['checkpoint'] == commit
    shutil.copyfile(installed / release_identity.NAME, stray / release_identity.NAME)
    result = probe(stray, env)
    assert result.get('nm_refused') == 'WorkflowInputError'
    assert result.get('ct_refused') == ['BUILD_IDENTITY_UNAVAILABLE', 5, 3]


def test_writable_installed_root_without_bytecode_suppression_refuses(matched, tmp_path):
    """Imports write __pycache__ into a writable tree before identity runs; the witness refuses it."""
    checkout, installed, commit, env, no_git = matched
    writable = (tmp_path / 'writable-installed').resolve()
    shutil.copytree(installed, writable)
    record = json.loads((writable / release_identity.NAME).read_bytes())
    record['install_root'] = str(writable)
    (writable / release_identity.NAME).write_bytes(json.dumps(record).encode())
    clean_env = {k: v for k, v in env.items() if k != 'PYTHONDONTWRITEBYTECODE'}
    result = probe(writable, dict(clean_env, PATH=str(no_git)), flags=('-I',))
    assert result.get('nm_refused') == 'WorkflowInputError'
    assert any(writable.rglob('__pycache__'))
