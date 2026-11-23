"""L2 installed-release initialization check and installed workflow entry (scope addendum section 1.3).

The positive and ordering cases run `release_check` in a subprocess against an installed copy of
the current applications/ and backend/ trees, committed to a temporary fixture repository and
witnessed by L1's release-identity record (the pattern of test_release_identity's `matched`
fixture). The child runs with -I -B and a PATH without git. The host is real except that the
test uid stands in for root as owner of the read-only release and configuration, the account
database is simulated, and the running release is named explicitly (the child's interpreter is
the development interpreter, not R_REL/python). Requires a non-root user, an ext4 --basetemp
(data-root admission reads the real mount) and a development interpreter that is exactly CPython
3.13.11 on Linux x86_64 (the A2 platform check runs for real in the child).

These tests establish adapter behaviour with the development interpreter. A real release
interpreter, installation and VM are later evidence.
"""
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from applications.bounded_decision_workflow import deployment, release_check
from applications.bounded_decision_workflow.checked_contracts import SCHEMAS_SHA256 as CHECKED_SCHEMAS
from applications.bounded_decision_workflow.t1_contracts import SCHEMAS_SHA256 as T1_SCHEMAS
from applications.bounded_decision_workflow.release_identity import NAME as RECORD_NAME, TOPS
from tests.applications.bounded_decision_workflow.test_deployment import ACCOUNT, PLATFORM, freeze, make_site, \
    write_config
from tests.applications.bounded_decision_workflow.test_release_identity import (
    PROBE, TOOL as RECORD_TOOL, commit_all, git_env)

ROOT = Path(__file__).parents[3]
PACKAGE = 'applications.bounded_decision_workflow.'
FIXED_RUN = 'startup-20261023t120000z-4242'
RUNNER = r'''import json, os, sys
from datetime import datetime, timezone
from types import SimpleNamespace
sys.path.insert(0, sys.argv[1])
spec = json.loads(sys.argv[2])
from applications.bounded_decision_workflow import deployment, release_check
euid = os.geteuid()
def getpwnam(name):
    if name != spec['account']:
        raise KeyError(name)
    return SimpleNamespace(pw_name=name, pw_uid=euid)
fixed = spec['fixed_clock']
host = deployment.Host(root_uid=os.getuid(), getpwnam=getpwnam, running_release=lambda: spec['release_root'],
                       utcnow=(lambda: datetime(2026, 10, 23, 12, 0, 0, tzinfo=timezone.utc)) if fixed
                       else deployment.Host().utcnow,
                       getpid=(lambda: 4242) if fixed else os.getpid)
code = getattr(release_check, spec['entry'])(spec['argv'], host=host)
loaded = sorted(m for m in sys.modules if m.startswith('applications.'))
with open(spec['report'], 'x') as stream:
    json.dump({'code': code, 'loaded': loaded}, stream)
raise SystemExit(code)
'''


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(root):
    """Every path under root with type, mode and content digest; never follows symlinks."""
    found = {}
    for directory, dirs, files in os.walk(root):
        for name in dirs + files:
            path = Path(directory) / name
            info = path.lstat()
            data = path.read_bytes() if path.is_file() and not path.is_symlink() else b''
            found[str(path.relative_to(root))] = (info.st_mode, sha(data))
    return found


def install_copy(checkout, commit, env, release):
    """An installed copy at release/app with its L1 record, read-only like an installed release."""
    app = release / 'app'
    for top in TOPS:
        shutil.copytree(checkout / top, app / top)
    subprocess.run([sys.executable, '-I', str(RECORD_TOOL), str(checkout), commit, str(app), str(app / RECORD_NAME)],
                   check=True, env=env, timeout=300)
    return app


@pytest.fixture(scope='module')
def installed(tmp_path_factory):
    base = tmp_path_factory.mktemp('l2-release').resolve()
    checkout = base / 'checkout'
    for top in TOPS:
        shutil.copytree(ROOT / top, checkout / top, ignore=shutil.ignore_patterns('__pycache__'))
    for path in checkout.rglob('*'):
        os.chmod(path, 0o755 if path.is_dir() else 0o644)
    env = git_env(base)
    commit = commit_all(checkout, env, *TOPS)
    release = base / 'release'
    app = install_copy(checkout, commit, env, release)
    freeze(release)
    data = base / 'data'
    for directory in (data, data / 'tmp', data / 'evidence'):
        directory.mkdir()
        os.chmod(directory, 0o700)
    value = {'schema': 'ohk-bdw.deployment.v1', 'release_root': str(release), 'runtime_account': ACCOUNT,
             'data_root': str(data)}
    config = write_config(base / 'etc/deployment.json', value)
    no_git = base / 'empty-path'
    no_git.mkdir()
    # Git-mode computation of the same commit, bytes and interpreter: the independent comparison.
    done = subprocess.run([sys.executable, '-I', '-B', '-c', PROBE, str(checkout.resolve())], env=env,
                          capture_output=True, timeout=300)
    assert done.returncode == 0, done.stderr.decode(errors='replace')
    git_side = json.loads(done.stdout)
    assert 'ct' in git_side and 'nm' in git_side, git_side
    return type('Installed', (), dict(base=base, checkout=checkout, commit=commit, env=env, release=release,
                                      app=app, data=data, config=config, value=value, no_git=no_git,
                                      git_ct=git_side['ct'].encode()))


def run(installed, argv, *, release=None, app=None, entry='main', fixed_clock=False, name='report'):
    report = installed.base / ('%s-%d.json' % (name, len(list(installed.base.glob(name + '-*.json')))))
    spec = dict(account=ACCOUNT, release_root=str(release or installed.release), entry=entry, argv=argv,
                fixed_clock=fixed_clock, report=str(report))
    env = {'PATH': str(installed.no_git), 'TMPDIR': str(installed.data / 'tmp'), 'HOME': str(installed.base),
           'LC_ALL': 'C'}
    done = subprocess.run([sys.executable, '-I', '-B', '-c', RUNNER, str(app or installed.app), json.dumps(spec)],
                          env=env, cwd='/', capture_output=True, timeout=300)
    outcome = json.loads(report.read_bytes()) if report.exists() else None
    assert outcome is not None and outcome['code'] == done.returncode, done.stderr.decode(errors='replace')
    return done, outcome


def diagnostic(done):
    value = json.loads(done.stderr)
    assert set(value) == {'schema', 'code', 'stage', 'target', 'exit_class'} and value['schema'] == 'ct.diagnostic.v1'
    assert done.stdout == b'' and value['exit_class'] == done.returncode
    return value


def evidence_dirs(installed):
    return sorted(p.name for p in (installed.data / 'evidence').iterdir())


def variant(installed, name, mutate):
    """A second installed copy of the same commit at another root, then one mutation."""
    release = installed.base / name
    app = install_copy(installed.checkout, installed.commit, installed.env, release)
    mutate(app)
    freeze(release)
    config = write_config(installed.base / ('etc-' + name) / 'deployment.json',
                          dict(installed.value, release_root=str(release)))
    return release, app, config


def test_installed_release_initializes_through_the_maintained_sequence(installed):
    before_release, before_evidence = snapshot(installed.release), evidence_dirs(installed)
    done, outcome = run(installed, ['--config', str(installed.config)])
    assert done.returncode == 0, done.stderr.decode(errors='replace')
    assert done.stderr == b''
    receipt = json.loads(done.stdout)
    new = sorted(set(evidence_dirs(installed)) - set(before_evidence))
    assert len(new) == 1 and new[0].startswith('startup-') and receipt['evidence_dir'] == str(
        installed.data / 'evidence' / new[0])
    directory = installed.data / 'evidence' / new[0]
    assert [p.name for p in directory.iterdir()] == ['startup-receipt.json']
    assert (directory / 'startup-receipt.json').read_bytes() == done.stdout   # the durable copy is the same bytes
    assert oct(directory.stat().st_mode & 0o777) == '0o700'
    # Identities equal the Git-mode computation of the same commit; no git was reachable here.
    git_ct = json.loads(installed.git_ct)
    assert receipt['commit'] == installed.commit == git_ct['checkpoint']
    assert receipt['ct_build_sha256'] == sha(installed.git_ct)
    assert receipt['nm_fields_sha256'] == sha(canonical(
        {k: git_ct[k] for k in ('checkpoint', 'source_manifest', 'environment_manifest')}))
    assert (receipt['checked_schemas_sha256'], receipt['t1_schemas_sha256']) == (CHECKED_SCHEMAS, T1_SCHEMAS)
    assert receipt['schema'] == 'ohk-bdw.startup-receipt.v1' and receipt['release_root'] == str(installed.release)
    assert (receipt['runtime_account'], receipt['euid']) == (ACCOUNT, os.geteuid())
    assert receipt['evidence_filesystem'] == 'ext4' and receipt['data_root_mount']['fstype'] == 'ext4'
    assert 'Max address space' in receipt['process_limits']
    # The maintained initialization path really ran: the four families, the checked runtime and L1.
    for module in ('checked_cli', 't1_cli', 'measurement_cli', 'reassessment_cli', 'checked_runtime',
                   'measurement_build', 'release_identity', 't1_package'):
        assert PACKAGE + module in outcome['loaded'], module
    # Nothing written under the release, nothing in TMPDIR, no bytecode.
    assert snapshot(installed.release) == before_release
    assert not any(installed.release.rglob('__pycache__'))
    assert list((installed.data / 'tmp').iterdir()) == []


def test_existing_evidence_directory_refuses_and_writes_nothing(installed):
    blocked = installed.data / 'evidence' / FIXED_RUN
    blocked.mkdir(mode=0o700)
    before = evidence_dirs(installed)
    done, outcome = run(installed, ['--config', str(installed.config)], fixed_clock=True)
    value = diagnostic(done)
    assert (value['code'], value['stage'], value['exit_class'], value['target']) == ('SIM_OUTPUT_UNSAFE', 0, 5,
                                                                                       '/evidence')
    assert evidence_dirs(installed) == before and list(blocked.iterdir()) == []
    assert PACKAGE + 'measurement_build' in outcome['loaded']   # build acquisition precedes output admission


def test_build_identity_failure_refuses_before_any_output(installed):
    release, app, config = variant(installed, 'extra-file', lambda app: (app / 'applications/extra.py').write_bytes(
        b'EXTRA = 1\n'))
    before = evidence_dirs(installed)
    done, _ = run(installed, ['--config', str(config)], release=release, app=app)
    value = diagnostic(done)
    assert (value['code'], value['stage'], value['exit_class']) == ('BUILD_IDENTITY_UNAVAILABLE', 5, 3)
    assert evidence_dirs(installed) == before


def test_tampered_pinned_schema_refuses_at_import_before_the_build(installed):
    def tamper(app):
        path = app / 'applications/bounded_decision_workflow/checked_temperature_schemas.json'
        path.write_bytes(path.read_bytes() + b' ')
    release, app, config = variant(installed, 'tampered-schema', tamper)
    before = evidence_dirs(installed)
    done, outcome = run(installed, ['--config', str(config)], release=release, app=app)
    value = diagnostic(done)
    # Imports come before build acquisition (addendum 1.3), so the existing schema refusal wins
    # over the L1 identity refusal the same tamper would also cause.
    assert (value['code'], value['stage'], value['exit_class']) == ('EDITION_CONTENT_MISMATCH', 4, 3)
    assert PACKAGE + 'measurement_build' not in outcome['loaded']
    assert evidence_dirs(installed) == before


def test_admission_refusal_precedes_checked_t1_schema_and_build_imports(installed):
    done, outcome = run(installed, ['--config', str(installed.base / 'absent.json')])
    value = diagnostic(done)
    assert (value['code'], value['exit_class']) == ('CONFIG_INVALID', 5)
    for module in ('checked_contracts', 'checked_runtime', 't1_contracts', 'checked_cli', 't1_cli', 'measurement_cli',
                   'reassessment_cli', 'measurement_build', 'release_identity'):
        assert PACKAGE + module not in outcome['loaded'], module
    # Only the package __init__ chain (S1-S7 contracts) and the two L2 modules precede admission.
    assert PACKAGE + 'deployment' in outcome['loaded'] and PACKAGE + 'contracts' in outcome['loaded']


def test_usage_and_root_refusals_in_process(tmp_path, capfd):
    site = make_site(tmp_path)
    for argv in ([], ['--config'], ['--config', str(site.config), 'extra'], ['--other', str(site.config)]):
        assert release_check.main(argv, host=site.host) == 2
        assert json.loads(capfd.readouterr().err)['code'] == 'CLI_USAGE'
    root = dataclasses.replace(site.host, geteuid=lambda: 0)
    assert release_check.main(['--bogus'], host=root) == 5   # A1 precedes even argument checks
    assert json.loads(capfd.readouterr().err)['code'] == 'RUNTIME_ACCOUNT_INVALID'


def test_workflow_entry_admits_then_refuses_unsupported_families(tmp_path, capfd):
    site = make_site(tmp_path)
    for command in ('measurement-evaluate', 'reassessment-evaluate', 'evaluate', '--request'):
        assert release_check.workflow_main(['--config', str(site.config), command], host=site.host) == 2
        value = json.loads(capfd.readouterr().err)
        assert (value['code'], value['target']) == ('INSTALLED_COMMAND_UNSUPPORTED', '/argv/command')
    assert release_check.workflow_main(['--config', str(site.config)], host=site.host) == 2
    assert json.loads(capfd.readouterr().err)['code'] == 'CLI_USAGE'
    os.chmod(site.config, 0o644)   # admission still governs the workflow entry
    assert release_check.workflow_main(['--config', str(site.config), 't1-simulation-run'], host=site.host) == 5
    assert json.loads(capfd.readouterr().err)['code'] == 'CONFIG_INVALID'


@pytest.mark.parametrize('arguments', [['--output-dir', '/srv/elsewhere/out'],
                                       ['--output-dir=/srv/elsewhere/out'],
                                       ['--scratch-dir', 'relative/scratch'],
                                       ['--diagnostic-dir', '{data}/../escape'],
                                       ['--output-dir', '{data}'],
                                       ['--output-dir=', '{data}/work/out']])   # empty inline value
def test_workflow_outputs_are_confined_to_the_data_root(tmp_path, capfd, arguments):
    site = make_site(tmp_path)
    arguments = [a.replace('{data}', str(site.data)) for a in arguments]
    code = release_check.workflow_main(['--config', str(site.config), 'checked-selection-evaluate', *arguments],
                                       host=site.host)
    value = json.loads(capfd.readouterr().err)
    assert (code, value['code']) == (5, 'OUTPUT_OUTSIDE_DATA_ROOT')


def test_workflow_entry_dispatches_to_the_maintained_command_after_admission(tmp_path, capfd):
    site = make_site(tmp_path)
    missing = site.data / 'work' / 'no-such-bundle'
    code = release_check.workflow_main(['--config', str(site.config), 'checked-selection-verify',
                                        '--expected-request-pin', 'a' * 64, '--expected-authority-pin', 'b' * 64,
                                        '--bundle', str(missing)], host=site.host)
    value = json.loads(capfd.readouterr().err)
    # The maintained checked CLI's own refusal and exit class: the command was reached unchanged.
    assert (code, value['schema'], value['code']) == (5, 'ct.diagnostic.v1', 'REFERENCE_MISSING')


def test_entry_points_run_no_git_and_wrappers_use_the_fixed_isolated_form():
    for module in (release_check, deployment):
        text = Path(module.__file__).read_text('utf-8')
        assert 'subprocess' not in text and "'git'" not in text
    build = (ROOT / 'tools/release/build_release.sh').read_text('utf-8')
    for entry in ('main', 'workflow_main'):
        assert ("exec $R_REL/python/bin/python3.13 -I -B -c 'import sys; sys.path.insert(0, \"$R_REL/app\"); "
                "from applications.bounded_decision_workflow.release_check import %s; raise SystemExit(%s())' "
                '"\\$@"' % (entry, entry)) in build
    assert release_check.RECEIPT_SCHEMA == 'ohk-bdw.startup-receipt.v1' and PLATFORM[3] == deployment.PYTHON_VERSION
