"""L2 installed-release initialization check and installed workflow entry.

`main` runs the maintained initialization sequence of the L2 scope addendum, section 1.3
(docs/superpowers/reports/2026-10-22-t1-linux-ext4-l2-scope-finalization-ADDENDUM.md):

1. deployment admission A1-A7 (`deployment`), before the checked/T1 contract, pinned-schema
   and build-identity modules are imported (the package `__init__` necessarily loads first;
   a failure there is an interpreter traceback, exit 1, not this module's INTERNAL_ERROR);
2. the dispatcher-equivalent imports of the checked, T1, measurement and reassessment
   command families, which execute their pinned-schema integrity loads;
3. maintained build acquisition, `checked_runtime._current_build(ExecutableBuild())`: in an
   installed release this is L1's release-identity witness, without Git, assembled into
   `ct.build.v1` and validated against the loaded schema;
4. maintained T1 output admission (`t1_package.safe_new_dir`) of one new evidence directory
   under the data root, and one durable receipt.

It stops before any operation input. Computing identities is not the claim; the claim is that
the maintained command families initialize in the installed release. It does not evaluate,
verify, replay, author, simulate or contain anything.

`workflow_main` is the installed entry for the maintained `checked-` and `t1-` commands: the
same admission, then the maintained command-line dispatcher, with output, scratch and
diagnostic directories confined to the data root. It adds no command, identity provider or
build override.

Process entry is the release wrapper's fixed `-I -B -c` string. Root must never import from
the release without `-B`.
"""
import importlib
import json
import os
import sys

from . import deployment

PACKAGE = __package__
RECEIPT_SCHEMA = 'ohk-bdw.startup-receipt.v1'
RECEIPT_NAME = 'startup-receipt.json'
FAMILIES = ('checked_cli', 't1_cli', 'measurement_cli', 'reassessment_cli')
WORKFLOW_PREFIXES = ('checked-', 't1-')
CONFINED_FLAGS = ('--output-dir', '--scratch-dir', '--diagnostic-dir')
RECEIPT_BYTES = 65536
EXIT_USAGE, EXIT_INTERNAL = 2, 7


class _Usage(Exception):
    pass


def _emit(fd, wire):
    view = memoryview(wire)
    while view:
        n = os.write(fd, view)
        if n <= 0:
            raise OSError('output unavailable')
        view = view[n:]


def _diagnostic(error):
    """ct.diagnostic.v1 fields of any refusal, classified without importing contract modules."""
    kind = type(error)
    if isinstance(error, deployment.DeploymentRefusal):
        return error.code, error.stage, error.target, error.exit_class
    if isinstance(error, _Usage):
        return 'CLI_USAGE', 0, '/argv', EXIT_USAGE
    # A schema-integrity refusal is raised while its module is still importing, so the
    # class is matched by name and defining module rather than through sys.modules.
    if (kind.__name__, kind.__module__) in (('CheckedRefusal', PACKAGE + '.checked_contracts'),
                                            ('SimRefusal', PACKAGE + '.t1_contracts')):
        stage = error.stage if hasattr(error, 'stage') else int(error.order) if error.order.isdigit() else error.order
        return error.code, stage, error.target, error.exit_class
    return 'INTERNAL_ERROR', 0, '/application', EXIT_INTERNAL


def _fail(error):
    code, stage, target, status = _diagnostic(error)
    diagnostic = {'schema': 'ct.diagnostic.v1', 'code': code, 'stage': stage, 'target': str(target)[:256],
                  'exit_class': status}
    try:
        _emit(2, json.dumps(diagnostic, sort_keys=True, separators=(',', ':')).encode('ascii') + b'\n')
    except OSError:
        return EXIT_INTERNAL
    return status


def _arguments(argv, minimum):
    argv = sys.argv[1:] if argv is None else list(argv)
    if len(argv) < minimum or argv[0] != '--config' or (minimum == 2 and len(argv) != 2):
        raise _Usage()
    return argv[1], argv[2:]


def _initialize():
    """Steps 2 and 3: the four families' imports, then the maintained build acquisition."""
    modules = {name: importlib.import_module(PACKAGE + '.' + name) for name in FAMILIES}
    runtime = modules['checked_cli'].runtime
    wire = runtime._current_build(runtime.ExecutableBuild())
    return modules, wire


def _publish(config, admission, wire, started, host):
    """Step 4: maintained output admission, one new 0700 directory, one durable receipt."""
    from .t1_contracts import SCHEMAS_SHA256 as T1_SCHEMAS_SHA256, canonical_bytes, refuse, sha
    from .t1_package import safe_new_dir
    from .checked_contracts import SCHEMAS_SHA256 as CHECKED_SCHEMAS_SHA256
    from .checked_cli import filesystem_of
    run_id = 'startup-%s-%d' % (started.strftime('%Y%m%dt%H%M%Sz').lower(), host.getpid())
    directory = safe_new_dir(config.data_root + '/evidence/' + run_id, '/evidence')
    try:
        os.mkdir(directory, 0o700)
    except OSError:
        refuse('SIM_OUTPUT_UNSAFE', 0, '/evidence', 5)
    build = json.loads(wire)
    nm_fields = {key: build[key] for key in ('checkpoint', 'source_manifest', 'environment_manifest')}
    receipt = {
        'schema': RECEIPT_SCHEMA, 'release_root': config.release_root, 'commit': build['checkpoint'],
        'ct_build_sha256': sha(wire), 'nm_fields_sha256': sha(canonical_bytes(nm_fields)),
        'checked_schemas_sha256': CHECKED_SCHEMAS_SHA256, 't1_schemas_sha256': T1_SCHEMAS_SHA256,
        'runtime_account': admission['runtime_account'], 'euid': admission['euid'],
        'data_root': config.data_root, 'data_root_mount': admission['data_root_mount'],
        'evidence_dir': str(directory), 'evidence_filesystem': filesystem_of(directory),
        'core_pattern_observed': admission['core_pattern_observed'],
        'process_limits': host.read_text('/proc/self/limits'),
        'started': started.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'recorded': host.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'claim': 'maintained command families initialized in this installed release; no operation input read',
    }
    data = canonical_bytes(receipt) + b'\n'
    if len(data) > RECEIPT_BYTES:
        refuse('SIM_RESOURCE_LIMIT', 7, '/receipt', 4)
    try:
        fd = os.open(directory / RECEIPT_NAME, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                     0o600)
        try:
            _emit(fd, data)
            os.fsync(fd)
        finally:
            os.close(fd)
        dfd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except OSError:   # partial output is retained, never deleted
        refuse('SIM_OUTPUT_UNSAFE', 0, '/evidence/' + RECEIPT_NAME, 5)
    return data


def main(argv=None, *, host=None):
    """`--config PATH` only. Receipt on stdout and in <data_root>/evidence/<run-id>/; exit 0."""
    host = deployment.Host() if host is None else host
    try:
        deployment.preflight(host)
        path, _ = _arguments(argv, 2)
        started = host.utcnow()
        config = deployment.load_config(path, host)
        admission = deployment.admit(config, host)
        _, wire = _initialize()
        data = _publish(config, admission, wire, started, host)
    except Exception as error:
        return _fail(error)
    try:
        _emit(1, data)
    except OSError:
        return EXIT_INTERNAL
    return 0


def _confined(rest, data_root):
    """Every output-like directory argument must be an absolute normalized path below data_root."""
    for index, item in enumerate(rest):
        flag, inline_form, inline = item.partition('=')
        if flag not in CONFINED_FLAGS:
            continue
        value = inline if inline_form else (rest[index + 1] if index + 1 < len(rest) else None)
        if value is None:
            continue   # the maintained parser refuses the missing value
        if not value.startswith('/') or os.path.normpath(value) != value or \
                not value.startswith(data_root + '/'):
            deployment.refuse('OUTPUT_OUTSIDE_DATA_ROOT', '/argv/' + flag[2:])


def workflow_main(argv=None, *, host=None):
    """`--config PATH <checked-...|t1-...> [maintained arguments]` after admission."""
    host = deployment.Host() if host is None else host
    try:
        deployment.preflight(host)
        path, rest = _arguments(argv, 3)
        config = deployment.load_config(path, host)
        deployment.admit(config, host)
        if not rest[0].startswith(WORKFLOW_PREFIXES):
            # Legacy S1-S7 and governed commands are Git-only and would refuse when installed.
            raise deployment.DeploymentRefusal('INSTALLED_COMMAND_UNSUPPORTED', '/argv/command', 0, EXIT_USAGE)
        _confined(rest, config.data_root)
    except Exception as error:
        return _fail(error)
    # The maintained dispatcher's own routing (cli.main), restricted to the installed-identity
    # families; each command emits its own receipt or diagnostic and exit code.
    family = 't1_cli' if rest[0].startswith('t1-') else 'checked_cli'
    try:
        command = importlib.import_module(PACKAGE + '.' + family)
    except Exception as error:
        return _fail(error)
    return command.main(rest)
