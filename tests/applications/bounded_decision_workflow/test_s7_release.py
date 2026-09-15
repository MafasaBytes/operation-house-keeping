"""S7 actual clean-checkout commands; no network, installation or model oracle import.

Run with the approved interpreter/dependencies and an isolated ext4 --basetemp.
The caller provisions a fresh environment offline; these tests never install it.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import zlib


ROOT = Path(__file__).parents[3]
S6 = 'c37c24ee50667121d6b2dc4739aa3b7d12825c96'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def clone(path, commit='HEAD'):
    revision = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', commit]).decode().strip()
    subprocess.run(['git', 'clone', '--quiet', '--no-hardlinks', str(ROOT), str(path)], check=True)
    subprocess.run(['git', '-C', str(path), 'checkout', '--quiet', '--detach', revision], check=True)
    assert not subprocess.check_output(['git', '-C', str(path), 'status', '--porcelain'])
    return path


def command(source, args, seed='1', expected=0):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONHASHSEED=seed, PYTHONNOUSERSITE='1')
    env.pop('PYTHONPATH', None)
    start = time.perf_counter()
    p = subprocess.run([sys.executable, '-m', 'applications.bounded_decision_workflow', *map(str, args)],
                       cwd=source, env=env, capture_output=True, timeout=60)
    elapsed = time.perf_counter() - start
    assert p.returncode == expected, (p.stdout, p.stderr)
    wire = p.stdout if expected == 0 else p.stderr
    assert (p.stderr if expected == 0 else p.stdout) == b''
    assert len(wire) <= 512 and wire.endswith(b'\n') and wire.count(b'\n') == 1
    return json.loads(wire), {'elapsed_seconds': elapsed, 'stdout_bytes': len(p.stdout), 'stderr_bytes': len(p.stderr)}


def reordered(value):
    if type(value) is dict: return {k: reordered(value[k]) for k in reversed(list(value))}
    if type(value) is list: return [reordered(v) for v in value]
    return value


def test_two_clean_roots_twelve_constructions_and_exact_replay(tmp_path):
    roots = [clone(tmp_path / f'source-{n}') for n in range(2)]
    reference = None; build = None; manifest_reference = None; times = set(); records = []
    for index, source in enumerate(roots):
        for seed in ('1', '7', '313'):
            for reverse in (False, True):
                run = tmp_path / f'run-{index}-{seed}-{int(reverse)}'; run.mkdir()
                for name in ('request.json', 'snapshot.json'):
                    wire = (source / 'applications/bounded_decision_workflow/examples' / name).read_bytes()
                    value = json.loads(wire)
                    constructed = canonical(reordered(value) if reverse else value)
                    assert constructed == wire
                    (run / name).write_bytes(constructed)
                bundle = run / 'result'
                _, measure = command(source, ['evaluate', '--request', run / 'request.json',
                    '--snapshot', run / 'snapshot.json', '--output-dir', bundle], seed)
                result = json.loads((bundle / 'result.json').read_bytes())
                # Literal, independent fixed-example expectations, not a call to projection.
                assert result['current_condition']['disposition'] == 'matches'
                assert result['observed_value_admission']['admitted_T0'] == {'numerator': 40, 'denominator': 1}
                assert [r['raw_interval']['lower']['numerator'] for r in result['raw_projections']] == [36,32,36,32,42,42,32,32]
                assert result['selection']['selected_action_ids'] == ['aH']
                assert len(result['reevaluation']['decision_rows']) == 22
                semantic = [(bundle / n).read_bytes() for n in ('result.json', 'trace.json')]
                identity = (bundle / 'build.json').read_bytes()
                if reference is None: reference, build = semantic, identity
                assert semantic == reference and identity == build
                manifest = json.loads((bundle / 'manifest.json').read_bytes())
                metadata = manifest.pop('run_metadata')
                assert set(metadata) == {'created_at_utc', 'filesystem'} and metadata['filesystem'] in ('ext4', 'xfs')
                times.add(metadata['created_at_utc'])
                if manifest_reference is None: manifest_reference = manifest
                assert manifest == manifest_reference
                verifier = roots[1-index]
                answer, verify_measure = command(verifier, ['verify', '--bundle', bundle], seed)
                assert answer['integrity_state'] == 'complete_bundle'
                _, replay_measure = command(verifier, ['replay', '--bundle', bundle, '--output-dir', run / 'replay'], seed)
                assert [(run / 'replay' / n).read_bytes() for n in ('result.json','trace.json')] == reference
                records.append({'root': index, 'seed': seed, 'reversed_construction': reverse,
                    'evaluate': measure, 'verify': verify_measure, 'replay': replay_measure,
                    'result_sha256': hashlib.sha256(reference[0]).hexdigest(),
                    'trace_sha256': hashlib.sha256(reference[1]).hexdigest(),
                    'files': {p.name: len(p.read_bytes()) for p in bundle.iterdir()}})
    assert len(times) >= 2 and len(records) == 12
    # Same source bytes in two independent Git databases; no parent worktree imports.
    assert json.loads(build)['git_commit'] == subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip()
    (tmp_path / 'release-evidence.json').write_bytes(canonical(records))
    # Missing/dirty executable witness: verification remains available, replay refuses.
    witness = roots[0] / 'applications/bounded_decision_workflow/README.md'
    original = witness.read_bytes()
    try:
        witness.unlink()
        command(roots[0], ['verify', '--bundle', bundle])
        d, _ = command(roots[0], ['replay', '--bundle', bundle, '--output-dir', tmp_path / 'refused'], expected=3)
        assert d['code'] == 'REPLAY_BUILD_UNAVAILABLE' and not (tmp_path / 'refused').exists()
    finally: witness.write_bytes(original)
    command(roots[0], ['replay', '--bundle', bundle, '--output-dir', tmp_path / 'valid-twin'])


def test_accepted_s6_archive_recovers_in_clean_matching_build(tmp_path):
    report = ROOT / 'docs/superpowers/reports/2026-09-15-bounded-decision-workflow-s6-resource-and-cli-completion-report.md'
    raw = report.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == 'f808d3fef64c400590ccd90abe21997ab5557f44325f69df4d60aafa8d74c458'
    pack = zlib.decompress(base64.b64decode(re.search(rb'```base64\n(.*?)\n```', raw, re.S)[1]))
    assert hashlib.sha256(pack).hexdigest() == '336b1ffed263df47067238b233fa564d354b9552e3ab404e9748bf9424739a30'
    files = {n:w.encode('utf8') for n,w in json.loads(pack).items()}
    assert set(files) == {'request.json','snapshot.json','resolved-input.json','result.json','trace.json','build.json','manifest.json'}
    recovered = tmp_path / 'recovered'; recovered.mkdir(mode=0o700)
    for name in sorted(set(files)-{'manifest.json'}) + ['manifest.json']:
        with (recovered/name).open('xb') as stream: stream.write(files[name])
    # Fixture extraction only, not an additional publisher/durability guarantee.
    old = clone(tmp_path / 'accepted-source', S6)
    command(old, ['verify', '--bundle', recovered])
    command(old, ['replay', '--bundle', recovered, '--output-dir', tmp_path / 'replayed'])
    for name in ('result.json','trace.json'):
        assert (tmp_path/'replayed'/name).read_bytes() == files[name]
    # Later source identity cannot falsely claim exact compatibility with S6.
    command(ROOT, ['verify', '--bundle', recovered])
    d, _ = command(ROOT, ['replay', '--bundle', recovered, '--output-dir', tmp_path/'mismatch'], expected=3)
    assert d['code'] == 'REPLAY_BUILD_UNAVAILABLE' and not (tmp_path/'mismatch').exists()
