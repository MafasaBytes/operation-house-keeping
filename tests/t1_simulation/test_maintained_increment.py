"""In-process development evidence; authorities/worlds are synthetic premises.

Exercises maintained components and unchanged checked reassessment independently
of a complete companion command. No physical or real-build success is claimed.
"""
import copy
import json
import os
import time
from contextlib import contextmanager
import pytest

from applications.bounded_decision_workflow import checked_runtime as rt
from applications.bounded_decision_workflow.t1_acquisition import produce
from applications.bounded_decision_workflow.t1_contracts import canonical_bytes, ref, sha, SimRefusal
from applications.bounded_decision_workflow.t1_records import preflight
from applications.bounded_decision_workflow.t1_simulation import _artifacts, _values, build_carriage
from applications.bounded_decision_workflow.t1_oracle import receipt_values
from applications.bounded_decision_workflow.t1_reassessment_handoff import assemble_carriage
from tests.t1_simulation.admitted_fixtures import admitted_case
from tests.checked_temperature.fixtures import co1, run_reassessment
# request_for/request_inputs_for moved unchanged; re-exported here for test_command_integration.
from tests.t1_simulation.request_fixtures import request_for, request_inputs_for


class Phases:
    """Bounded diagnostic BOOTTIME journal; begin survives a killed test.

    Does not cover interpreter startup or substitute for the enclosing driver.
    """
    def __init__(self, path):
        self.path, self.count = path, 0

    def record(self, value):
        self.count += 1
        if self.count > 64:
            raise AssertionError('phase observation reservation exhausted')
        wire = canonical_bytes(value) + b'\n'
        assert len(wire) <= 512
        with self.path.open('ab') as stream:
            stream.write(wire)
            stream.flush()
            os.fsync(stream.fileno())
        print('T1_PHASE', wire.decode().strip(), flush=True)

    @contextmanager
    def __call__(self, name):
        begin = time.clock_gettime(time.CLOCK_BOOTTIME)
        self.record(dict(phase=name,event='begin',boottime=begin))
        try:
            yield
        except BaseException:
            self.record(dict(phase=name,event='end',boottime=time.clock_gettime(time.CLOCK_BOOTTIME),outcome='failed'))
            raise
        else:
            end = time.clock_gettime(time.CLOCK_BOOTTIME)
            self.record(dict(phase=name,event='end',boottime=end,elapsed=end-begin,outcome='completed'))


def acquired(tmp_path, **world):
    phases = Phases(tmp_path/'phase-timing.jsonl')
    with phases('fixture_construction'):
        case = admitted_case(**world)
    keys = {k:case[k] for k in ('objects','prior_files','pins','prior_pins','build')}
    produced = produce(**keys, workspace=tmp_path/'acquisition', observe=phases)
    admitted = produced['admission']
    with phases('carriage_construction'):
        files, retained = _artifacts(produced)
        values = _values(admitted)
    with phases('diagnostic_recomputation'):
        assert values == receipt_values(admitted.root('J'),admitted.root('E'),admitted.get)
    case['phases'] = phases
    return case, admitted, produced, files, dict(values, **retained)


@pytest.mark.parametrize('theta,old,beta,epsilon,expected', [
    ('60.1','60.1','0','0','60.1'), ('50','50','0','0','50'),
    ('57.5','57.5','0','0','57.5'), ('55.1','55.1','0','0.5','55.6'),
    ('50','50','10','0','60'), ('60','50','0','0','60')],
    ids=['positive','h2','no-fit','mixed','bad-calibration','bad-hold'])
def test_independent_world_backend_observation(tmp_path,theta,old,beta,epsilon,expected):
    case,a,p,files,receipt=acquired(tmp_path,theta=theta,baseline_theta=old,beta=beta,epsilon=epsilon)
    assert receipt['r']==expected
    assert len(receipt['evidence']['raw_envelopes'])==2
    assert len(receipt['evidence']['acquisition_attempts'])==2
    assert len(receipt['evidence']['extraction_results'])==2
    for key,digest in receipt['raw_response_digests'].items():
        assert sha(files['evidence/raw/'+digest])==digest
    from fractions import Fraction
    raw=json.loads(files['evidence/raw/'+receipt['raw_response_digests']['printer_objects']],parse_float=Fraction)
    assert Fraction(raw['result']['status']['extruder']['temperature'])==Fraction(expected)
    assert receipt['diagnostics']['reference_calibration']['beta_in_b_ref'] == (beta=='0')
    assert receipt['diagnostics']['state_hold']['theta_equals_baseline_theta'] == (theta==old)


@pytest.mark.parametrize('theta,expected', [('60.1','one_compatible'),('50','one_compatible'),('57.5','model_prediction_mismatch')],ids=['positive','h2','no-fit'])
def test_maintained_handoff_checked_reassessment_verify_replay(tmp_path,monkeypatch,theta,expected):
    case,a,p,files,receipt=acquired(tmp_path,theta=theta,baseline_theta=theta)
    supplied=request_for(case,p,receipt)
    from applications.bounded_decision_workflow import t1_closure
    enforcing_serializer=t1_closure.manifest_bytes
    def measure_manifest(value):
        wire=canonical_bytes(value)
        assert len(wire)<=4*1048576  # diagnostic file reservation, never an M cap
        with (tmp_path/'manifest-demand.bin').open('xb') as stream:
            stream.write(wire);stream.flush();os.fsync(stream.fileno())
        case['phases'].record(dict(phase='complete_manifest_demand',event='measurement',
                                  bytes=len(wire),members=len(value['members']),sha256=sha(wire)))
        return enforcing_serializer(value)  # unchanged 32768-byte refusal
    monkeypatch.setattr(t1_closure,'manifest_bytes',measure_manifest)
    with case['phases']('complete_carriage_construction'):
        package=build_carriage(admission=a,produced=p)
    m=package['manifest.json']
    from applications.bounded_decision_workflow.t1_closure import inspect_package
    with case['phases']('carriage_closure_verification'):
        inspect_package(m,package,manifest_pin=sha(m))
    assert len(m) <= 32768
    print('T1_COMPLETE_MANIFEST_BYTES',len(m),'MEMBERS',len(json.loads(m)['members']))
    for name,wire in package.items():
        destination=tmp_path/'producer-package'/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(wire)
    # Fresh owning-backend component reconstruction is explicitly distinct from
    # the still-guarded transport-free verification command.
    reconstructed=produce(**{k:case[k] for k in ('objects','prior_files','pins','prior_pins','build')},
                          workspace=tmp_path/'component-reconstruction',observe=case['phases'])
    expected_files,expected_retained=_artifacts(reconstructed)
    submitted_receipt=json.loads(package['receipt/receipt.json'])
    from applications.bounded_decision_workflow.t1_simulation import check_artifacts
    from applications.bounded_decision_workflow.t1_oracle import check_receipt
    with case['phases']('ordered_component_verification'):
        check_artifacts(files=package,expected_files=expected_files,retained=expected_retained,
                        receipt=submitted_receipt,admission=a)
        check_receipt(submitted_receipt,a.root('J'),a.root('E'),a.get,receipt)
    before=supplied.request_wire
    h=assemble_carriage(request_wire=before,manifest_wire=m,admission=a,receipt=receipt,prior_pins=case['prior_pins'],request_objects=request_inputs_for(supplied,case),producer_evidence_wire=p['public_evidence'])
    (tmp_path/'handoff.json').write_bytes(h)
    assert supplied.request_wire==before and json.loads(h)['request']==ref('ct.request.v1',before)
    with case['phases']('checked_reassessment'):
        bundle=run_reassessment(supplied,case['prior_files'])
    for name,wire in bundle.items():
        destination=tmp_path/'checked-bundle'/name
        destination.parent.mkdir(exist_ok=True)
        destination.write_bytes(wire)
    result=json.loads(bundle['result.json'])
    print('T1_CHECKED_RESULT',theta,'result_bytes',len(bundle['result.json']))
    assert result['disposition']==expected
    compatible=[i for i,hypothesis in enumerate(result['hypotheses']) if hypothesis['status']=='compatible_under_declared_model']
    assert compatible==({'60.1':[0],'50':[1],'57.5':[]}[theta])
    assert result['ranking']=='not_reassessed' and result['adoption']=='derived_not_adopted'
    from fractions import Fraction
    from applications.bounded_decision_workflow.t1_contracts import rational
    assert result['interval']=={'lo':rational(Fraction(theta)-Fraction(1,2)), 'hi':rational(Fraction(theta)+Fraction(1,2))}
    with case['phases']('standalone_checked_verify_replay'):
        rt.verify(bundle_files=bundle,request_pin=supplied.request_pin,authority_pin=supplied.authority_pin,build=case['build'])
        replay=rt.replay(bundle_files=bundle,request_pin=supplied.request_pin,authority_pin=supplied.authority_pin,build=case['build'],created_at='2026-10-05T12:00:00Z')
    for name,wire in replay.items():
        destination=tmp_path/'replay-bundle'/name
        destination.parent.mkdir(exist_ok=True)
        destination.write_bytes(wire)
    replay_result=json.loads(replay['result.json'])
    assert replay_result['disposition']==result['disposition']
    assert replay_result['hypotheses']==result['hypotheses']


def test_handoff_authority_substitution_is_refused(tmp_path):
    case,a,p,files,receipt=acquired(tmp_path)
    supplied=request_for(case,p,receipt)
    request=json.loads(supplied.request_wire)
    authority=json.loads(supplied.objects[request['result']['execution_authority']['sha256']])
    authority['id']='substituted-execution-authority'
    wire=canonical_bytes(authority)
    supplied.objects[sha(wire)]=wire
    request['result']['execution_authority']=ref('ct.authority.v1',wire)
    with pytest.raises(SimRefusal) as denied:
        assemble_carriage(request_wire=canonical_bytes(request),manifest_wire=b'{}',admission=a,receipt=receipt,prior_pins=case['prior_pins'],request_objects=request_inputs_for(supplied,case,canonical_bytes(request)),producer_evidence_wire=p['public_evidence'])
    assert (denied.value.code,denied.value.target)==('HANDOFF_AUTHORITY_JOIN_MISMATCH','/R/result/execution_authority')


def test_wrong_pin_denies_before_acquisition(tmp_path):
    case=admitted_case()
    pins=dict(case['pins'],G='0'*64)
    with pytest.raises(SimRefusal) as denied:
        produce(objects=case['objects'],prior_files=case['prior_files'],pins=pins,
                prior_pins=case['prior_pins'],build=case['build'],workspace=tmp_path/'denied')
    assert (denied.value.code,denied.value.order,denied.value.target)==('SIM_PIN_MISMATCH','1','/G')
    assert not (tmp_path/'denied').exists()


def test_invalid_world_denies_before_acquisition(tmp_path):
    case=admitted_case(theta='1001',baseline_theta='1001')
    with pytest.raises(SimRefusal) as denied:
        produce(**{k:case[k] for k in ('objects','prior_files','pins','prior_pins','build')},workspace=tmp_path/'invalid')
    assert (denied.value.code,denied.value.order,denied.value.target)==('SIM_WORLD_DOMAIN','5','/W/theta')
    assert not (tmp_path/'invalid').exists()


def test_rehashed_diagnostic_and_closure_substitutions(tmp_path):
    case,a,p,_files,_receipt=acquired(tmp_path,theta='50',baseline_theta='50')
    package=build_carriage(admission=a,produced=p)
    from applications.bounded_decision_workflow.t1_closure import build_manifest,inspect_package
    from applications.bounded_decision_workflow.t1_oracle import check_receipt
    receipt=json.loads(package['receipt/receipt.json'])
    _original,retained=_artifacts(p)
    changed=copy.deepcopy(receipt)
    changed['diagnostics']['reference_mapping']['variable_mapping_matches']=False
    replacement=canonical_bytes(changed)
    forged=dict(package)
    forged['receipt/receipt.json']=replacement
    roots=copy.deepcopy(json.loads(package['manifest.json'])['roots'])
    roots['receipt']=ref('ct.t1-producer-receipt.v1',replacement)
    forged.pop('manifest.json')
    forged['manifest.json']=build_manifest(forged,roots)
    # Lawful rehashing restores carriage integrity, not asserted provenance.
    inspect_package(forged['manifest.json'],forged,manifest_pin=sha(forged['manifest.json']))
    with pytest.raises(SimRefusal) as denied:
        check_receipt(changed,a.root('J'),a.root('E'),a.get,retained)
    assert (denied.value.code,denied.value.target)==('SIM_DERIVATION_MISMATCH','/receipt/diagnostics/reference_mapping/variable_mapping_matches')
    missing=dict(package)
    missing.pop('evidence/raw/'+receipt['raw_response_digests']['printer_objects'])
    with pytest.raises(SimRefusal) as absent:
        inspect_package(package['manifest.json'],missing,manifest_pin=sha(package['manifest.json']))
    assert absent.value.code=='SIM_REFERENCE_MISSING'
    free=dict(package)
    free['evidence/query/free.bin']=b'free member has no reference'
    with pytest.raises(SimRefusal) as extra:
        inspect_package(package['manifest.json'],free,manifest_pin=sha(package['manifest.json']))
    assert extra.value.code=='SIM_REFERENCE_INVALID'
