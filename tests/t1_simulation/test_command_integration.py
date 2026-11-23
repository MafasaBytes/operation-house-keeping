"""Maintained command composition under labelled synthetic development premises.

No subprocesses, physical acquisition, operational authority issuance or real
build qualification occur here. Fixture authors supply J/G/E/R/A independently.
"""
import copy
import json
import os
from fractions import Fraction
from pathlib import Path

import pytest

from applications.bounded_decision_workflow import checked_runtime as checked
from applications.bounded_decision_workflow import t1_acquisition, t1_carrier, t1_cli
from applications.bounded_decision_workflow import t1_package, t1_workflow
from applications.bounded_decision_workflow.t1_contracts import canonical_bytes, rational, ref, sha, SimRefusal
from applications.bounded_decision_workflow.t1_closure import build_manifest, inspect_package
from tests.t1_simulation.admitted_fixtures import admitted_case
from tests.t1_simulation.test_maintained_increment import Phases, request_for, request_inputs_for


def write_package(directory, files):
    directory.mkdir()
    for name, wire in files.items():
        destination = directory / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(wire)


def context(tmp_path, theta='60.1'):
    phases = Phases(tmp_path / 'phase-timing.jsonl')
    with phases('fixture_construction'):
        case = admitted_case(theta=theta, baseline_theta=theta)
    write_package(tmp_path / 'prior', case['prior_files'])
    write_package(tmp_path / 'input', case['objects'])
    return case, phases


def command(case, tmp_path, operation, output, **flags):
    values = dict(expected_target_pin=case['pins']['J'],
        expected_execution_authority_pin=case['pins']['E'],
        expected_permission_pin=case['pins']['G'],
        expected_prior_request_pin=case['prior_pins']['request_sha256'],
        expected_prior_authority_pin=case['prior_pins']['authority_sha256'],
        prior_bundle=tmp_path / 'prior', output_dir=output, **flags)
    argv = [operation]
    for key, value in values.items():
        argv.extend(['--' + key.replace('_', '-'), str(value)])
    result = t1_cli.execute(t1_cli.arguments(argv), build=case['build'])
    assert result['command'] == operation
    assert not (Path(output) / 'PARTIAL').exists()
    return result


def run_producer(case, phases, tmp_path):
    with phases('maintained_producer_command'):
        completion = command(case, tmp_path, 't1-simulation-run', tmp_path / 'producer',
                             objects_dir=tmp_path / 'input')
    package = t1_workflow.read_package(tmp_path / 'producer')
    manifest = package['manifest.json']
    inspect_package(manifest, package, manifest_pin=sha(manifest))
    assert len(manifest) <= 32768
    phases.record(dict(phase='complete_manifest_demand', event='measurement',
                       bytes=len(manifest), members=len(json.loads(manifest)['members']), sha256=sha(manifest)))
    assert all(item['path'] in package for item in completion['published'])
    return package


def forbid_acquisition(*args, **kwargs):
    raise AssertionError('retained verification called acquisition transport/producer')


@pytest.mark.parametrize('theta,disposition,compatible', [
    ('60.1', 'one_compatible', [0]), ('50', 'one_compatible', [1]),
    ('57.5', 'model_prediction_mismatch', [])], ids=['positive', 'h2', 'no-fit'])
def test_maintained_commands_complete_synthetic_workflow(tmp_path, monkeypatch, theta, disposition, compatible):
    case, phases = context(tmp_path, theta)
    package = run_producer(case, phases, tmp_path)
    manifest_pin = sha(package['manifest.json'])
    receipt = json.loads(package['receipt/receipt.json'])
    supplied = request_for(case, {'public_evidence': package['evidence/public/evidence.json']}, receipt)
    request_objects = request_inputs_for(supplied, case)
    request_objects[sha(supplied.request_wire)] = supplied.request_wire
    write_package(tmp_path / 'request-input', request_objects)
    # Separately supplied A is retained unchanged. Assembly does not issue it.
    authority_wire = supplied.objects[supplied.authority_pin]
    write_package(tmp_path / 'evaluation-input', {supplied.authority_pin: authority_wire})
    monkeypatch.setattr(t1_acquisition, 'produce', forbid_acquisition)
    monkeypatch.setattr(t1_carrier, 'Transport', forbid_acquisition)
    producer_flags = dict(producer_package=tmp_path / 'producer', expected_producer_manifest_pin=manifest_pin)
    with phases('transport_free_simulation_verification'):
        verified = command(case, tmp_path, 't1-simulation-verify', tmp_path / 'producer-report',
                           scratch_dir=tmp_path / 'verify-scratch', **producer_flags)
    assert verified['guarantee'] == 'simulation-verified'
    with phases('maintained_handoff_command'):
        command(case, tmp_path, 't1-reassessment-prepare', tmp_path / 'handoff',
                objects_dir=tmp_path / 'request-input', scratch_dir=tmp_path / 'handoff-scratch', **producer_flags)
    handoff = (tmp_path / 'handoff/handoff.json').read_bytes()
    assert json.loads(handoff)['request'] == ref('ct.request.v1', supplied.request_wire)
    workflow_flags = dict(handoff_package=tmp_path / 'handoff', expected_handoff_pin=sha(handoff),
        expected_request_pin=supplied.request_pin, expected_authority_pin=supplied.authority_pin, **producer_flags)
    with phases('maintained_separately_authorized_reassessment'):
        completion = command(case, tmp_path, 't1-reassessment-evaluate', tmp_path / 'workflow',
            scratch_dir=tmp_path / 'evaluate-scratch', objects_dir=tmp_path / 'evaluation-input', **workflow_flags)
    assert completion['guarantee'] == 'producer-checked-primary-calibration-gated-v1'
    bundle = t1_workflow.read_package(tmp_path / 'workflow/bundle')
    result = json.loads(bundle['result.json'])
    assert result['disposition'] == disposition
    assert [i for i, h in enumerate(result['hypotheses']) if h['status'] == 'compatible_under_declared_model'] == compatible
    assert [h['status'] for h in result['hypotheses']] == {
        '60.1': ['compatible_under_declared_model', 'conditionally_incompatible'],
        '50': ['conditionally_incompatible', 'compatible_under_declared_model'],
        '57.5': ['conditionally_incompatible', 'conditionally_incompatible'],
    }[theta]
    assert result['interval'] == dict(lo=rational(Fraction(theta)-Fraction(1, 2)), hi=rational(Fraction(theta)+Fraction(1, 2)))
    assert result['ranking'] == 'not_reassessed'
    assert result['adoption'] == 'derived_not_adopted'
    fwire = (tmp_path / 'workflow/workflow-receipt.json').read_bytes()
    f = json.loads(fwire)
    assert f['finding']['subjects']['evaluation_authority'] == ref('ct.authority.v1', authority_wire)
    with phases('maintained_workflow_verification'):
        completion = command(case, tmp_path, 't1-workflow-verify', tmp_path / 'workflow-report',
            scratch_dir=tmp_path / 'workflow-verify-scratch', workflow_package=tmp_path / 'workflow',
            expected_workflow_receipt_pin=sha(fwire), **workflow_flags)
    assert completion['guarantee'] == 'producer-checked-primary-calibration-gated-v1'
    with phases('owning_standalone_replay'):
        replay = checked.replay(bundle_files=bundle, request_pin=supplied.request_pin,
            authority_pin=supplied.authority_pin, build=case['build'], created_at='2026-10-05T12:00:00Z')
        checked.verify(bundle_files=replay, request_pin=supplied.request_pin,
                       authority_pin=supplied.authority_pin, build=case['build'])
    write_package(tmp_path / 'replay', replay)
    replay_result = json.loads(replay['result.json'])
    assert replay_result['hypotheses'] == result['hypotheses']
    assert replay_result['disposition'] == result['disposition']
    assert supplied.request_wire == request_objects[sha(supplied.request_wire)]
    assert authority_wire == (tmp_path / 'evaluation-input' / supplied.authority_pin).read_bytes()
    assert not any('adoption' in path or 'human-disposition' in path for path in t1_workflow.read_package(tmp_path / 'workflow'))


@pytest.mark.parametrize('fault', ['wrong-pin', 'wrong-permission'])
def test_producer_denies_before_side_effects(tmp_path, monkeypatch, fault):
    case, _ = context(tmp_path)
    input_dir = tmp_path / 'input'
    if fault == 'wrong-pin':
        case['pins']['G'] = '0' * 64
        expected = ('SIM_PIN_MISMATCH', '1', '/G')
    else:
        old = case['pins']['G']
        permission = json.loads(case['objects'].pop(old))
        permission['valid']['to'] = '2026-10-05T09:00:30Z'
        wire = canonical_bytes(permission)
        case['pins']['G'] = sha(wire)
        case['objects'][sha(wire)] = wire
        input_dir = tmp_path / 'denial-input'
        write_package(input_dir, case['objects'])
        expected = ('SIM_PERMISSION_SCOPE_MISMATCH', '3', '/G/valid')
    monkeypatch.setattr(t1_acquisition, 'produce', forbid_acquisition)
    with pytest.raises(SimRefusal) as denied:
        command(case, tmp_path, 't1-simulation-run', tmp_path / 'denied', objects_dir=input_dir)
    assert (denied.value.code, denied.value.order, denied.value.target) == expected
    assert not (tmp_path / 'denied').exists()


@pytest.mark.parametrize('fault', ['diagnostic', 'extra', 'missing'])
def test_retained_verification_rejects_substitution(tmp_path, monkeypatch, fault):
    case, phases = context(tmp_path)
    package = run_producer(case, phases, tmp_path)
    if fault == 'diagnostic':
        receipt = json.loads(package['receipt/receipt.json'])
        receipt['diagnostics']['reference_mapping']['variable_mapping_matches'] = False
        wire = canonical_bytes(receipt)
        roots = copy.deepcopy(json.loads(package.pop('manifest.json'))['roots'])
        package['receipt/receipt.json'] = wire
        roots['receipt'] = ref('ct.t1-producer-receipt.v1', wire)
        package['manifest.json'] = build_manifest(package, roots)
        inspect_package(package['manifest.json'], package, manifest_pin=sha(package['manifest.json']))
        expected = 'SIM_DERIVATION_MISMATCH'
    elif fault == 'extra':
        package['evidence/query/free.bin'] = b'not reachable'
        expected = 'SIM_REFERENCE_INVALID'
    else:
        receipt = json.loads(package['receipt/receipt.json'])
        package.pop('evidence/raw/' + receipt['raw_response_digests']['printer_objects'])
        expected = 'SIM_REFERENCE_MISSING'
    write_package(tmp_path / 'substituted', package)
    monkeypatch.setattr(t1_acquisition, 'produce', forbid_acquisition)
    monkeypatch.setattr(t1_carrier, 'Transport', forbid_acquisition)
    with pytest.raises(SimRefusal) as denied:
        command(case, tmp_path, 't1-simulation-verify', tmp_path / 'denied',
            producer_package=tmp_path / 'substituted', expected_producer_manifest_pin=sha(package['manifest.json']),
            scratch_dir=tmp_path / 'scratch')
    assert denied.value.code == expected
    assert not (tmp_path / 'denied').exists()


def test_workflow_authority_substitution_refuses(tmp_path, monkeypatch):
    case, phases = context(tmp_path)
    package = run_producer(case, phases, tmp_path)
    receipt = json.loads(package['receipt/receipt.json'])
    supplied = request_for(case, {'public_evidence': package['evidence/public/evidence.json']}, receipt)
    request_objects = request_inputs_for(supplied, case)
    request_objects[sha(supplied.request_wire)] = supplied.request_wire
    write_package(tmp_path / 'request-input', request_objects)
    monkeypatch.setattr(t1_acquisition, 'produce', forbid_acquisition)
    monkeypatch.setattr(t1_carrier, 'Transport', forbid_acquisition)
    flags = dict(producer_package=tmp_path / 'producer', expected_producer_manifest_pin=sha(package['manifest.json']))
    command(case, tmp_path, 't1-reassessment-prepare', tmp_path / 'handoff',
            objects_dir=tmp_path / 'request-input', scratch_dir=tmp_path / 'prepare-scratch', **flags)
    handoff_wire = (tmp_path / 'handoff/handoff.json').read_bytes()
    handoff = json.loads(handoff_wire)
    handoff['execution_authority'] = ref('ct.authority.v1', supplied.objects[supplied.authority_pin])
    forged = canonical_bytes(handoff)
    forged_package = t1_workflow.read_package(tmp_path / 'handoff')
    forged_package['handoff.json'] = forged
    write_package(tmp_path / 'forged-handoff', forged_package)
    write_package(tmp_path / 'evaluation-input', {supplied.authority_pin: supplied.objects[supplied.authority_pin]})
    with pytest.raises(SimRefusal) as denied:
        command(case, tmp_path, 't1-reassessment-evaluate', tmp_path / 'denied',
            scratch_dir=tmp_path / 'evaluate-scratch', objects_dir=tmp_path / 'evaluation-input',
            handoff_package=tmp_path / 'forged-handoff', expected_handoff_pin=sha(forged),
            expected_request_pin=supplied.request_pin, expected_authority_pin=supplied.authority_pin, **flags)
    assert (denied.value.code, denied.value.target) == ('HANDOFF_AUTHORITY_JOIN_MISMATCH', '/H/execution_authority')
    assert not (tmp_path / 'denied').exists()


@pytest.mark.parametrize('fault', ['file-write', 'file-fsync', 'rename', 'directory-sync', 'marker-removal'])
def test_publication_failure_retains_incomplete(tmp_path, monkeypatch, fault):
    output = tmp_path / 'publication'
    publication = t1_package.Publication(output, final='report.json', target='/report')
    rename, sync_dir, unlink = t1_package.os.rename, t1_package._fsync_dir, Path.unlink
    open_file, sync_file = t1_package.os.open, t1_package.os.fsync
    def fail_open(path, *args, **kwargs):
        if Path(path) == output / 'report.json.tmp':
            raise OSError('injected temporary file creation failure')
        return open_file(path, *args, **kwargs)
    def fail_fsync(fd):
        if os.readlink('/proc/self/fd/' + str(fd)) == str(output / 'report.json.tmp'):
            raise OSError('injected temporary file synchronization failure')
        return sync_file(fd)
    def fail_rename(source, destination):
        rename(source, destination)
        raise OSError('injected failure after final rename')
    def fail_sync(path):
        if (output / 'report.json').exists():
            raise OSError('injected final directory synchronization failure')
        return sync_dir(path)
    def fail_unlink(path, *args, **kwargs):
        if path == output / 'PARTIAL':
            raise OSError('injected marker removal failure')
        return unlink(path, *args, **kwargs)
    if fault == 'rename': monkeypatch.setattr(t1_package.os, 'rename', fail_rename)
    if fault == 'file-write': monkeypatch.setattr(t1_package.os, 'open', fail_open)
    if fault == 'file-fsync': monkeypatch.setattr(t1_package.os, 'fsync', fail_fsync)
    if fault == 'directory-sync': monkeypatch.setattr(t1_package, '_fsync_dir', fail_sync)
    if fault == 'marker-removal': monkeypatch.setattr(Path, 'unlink', fail_unlink)
    with pytest.raises(SimRefusal) as denied:
        publication.finish(b'{"retained":"final is not success"}')
    assert denied.value.code == 'SIM_PUBLICATION_INCOMPLETE'
    assert (output / 'report.json').exists() == (fault not in ('file-write', 'file-fsync'))
    assert (output / 'PARTIAL').exists()
    with pytest.raises(SimRefusal) as incomplete:
        t1_workflow.read_package(output)
    assert incomplete.value.code == 'SIM_PUBLICATION_INCOMPLETE'


def test_completed_delegation_retained_after_workflow_publication_failure(tmp_path, monkeypatch):
    case, phases = context(tmp_path)
    package = run_producer(case, phases, tmp_path)
    receipt = json.loads(package['receipt/receipt.json'])
    supplied = request_for(case, {'public_evidence': package['evidence/public/evidence.json']}, receipt)
    request_objects = request_inputs_for(supplied, case)
    request_objects[sha(supplied.request_wire)] = supplied.request_wire
    write_package(tmp_path / 'request-input', request_objects)
    write_package(tmp_path / 'evaluation-input', {supplied.authority_pin: supplied.objects[supplied.authority_pin]})
    monkeypatch.setattr(t1_acquisition, 'produce', forbid_acquisition)
    monkeypatch.setattr(t1_carrier, 'Transport', forbid_acquisition)
    flags = dict(producer_package=tmp_path / 'producer', expected_producer_manifest_pin=sha(package['manifest.json']))
    command(case, tmp_path, 't1-reassessment-prepare', tmp_path / 'handoff',
        objects_dir=tmp_path / 'request-input', scratch_dir=tmp_path / 'prepare-scratch', **flags)
    handoff_wire = (tmp_path / 'handoff/handoff.json').read_bytes()
    original_finish = t1_package.Publication.finish
    def fail_workflow(publication, wire):
        if publication.final == 'workflow-receipt.json':
            from applications.bounded_decision_workflow.t1_contracts import refuse
            refuse('SIM_PUBLICATION_INCOMPLETE', 9, '/F', 5)
        return original_finish(publication, wire)
    monkeypatch.setattr(t1_package.Publication, 'finish', fail_workflow)
    with phases('completed_delegate_then_failed_workflow_publication'):
        with pytest.raises(SimRefusal) as denied:
            command(case, tmp_path, 't1-reassessment-evaluate', tmp_path / 'failed-workflow',
                scratch_dir=tmp_path / 'evaluate-scratch', objects_dir=tmp_path / 'evaluation-input',
                handoff_package=tmp_path / 'handoff', expected_handoff_pin=sha(handoff_wire),
                expected_request_pin=supplied.request_pin, expected_authority_pin=supplied.authority_pin, **flags)
    assert (denied.value.code, denied.value.target) == ('SIM_PUBLICATION_INCOMPLETE', '/F')
    assert (tmp_path / 'failed-workflow/PARTIAL').exists()
    assert not (tmp_path / 'failed-workflow/workflow-receipt.json').exists()
    bundle = t1_workflow.read_package(tmp_path / 'failed-workflow/bundle')
    assert set(bundle) == set(checked.BUNDLE_NAMES)
    with phases('retained_delegation_independent_verification'):
        checked.verify(bundle_files=bundle, request_pin=supplied.request_pin,
                       authority_pin=supplied.authority_pin, build=case['build'])
    with pytest.raises(SimRefusal) as incomplete:
        t1_workflow.read_package(tmp_path / 'failed-workflow')
    assert incomplete.value.code == 'SIM_PUBLICATION_INCOMPLETE'
