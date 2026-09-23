"""Storage-only historical fixtures must not be accepted as semantic bundles."""
import json
import pytest
from applications.bounded_decision_workflow.measurement_delivery import FILES,verify_measurement_bundle
from applications.bounded_decision_workflow.measurement_contracts import MeasurementContractError
from tests.measurement_profile.test_delivery_contract_mapping import command


def test_storage_fixture_is_not_supported_measurement_delivery(tmp_path):
    for name in FILES:(tmp_path/name).write_text(json.dumps({'name':name},separators=(',',':'),sort_keys=True))
    with pytest.raises(MeasurementContractError):verify_measurement_bundle(tmp_path)
    assert command('measurement-verify','--bundle',tmp_path).returncode==3


def test_incomplete_bundle_is_not_a_completed_withholding(tmp_path):
    (tmp_path/'invocation.json').write_bytes(b'{}')
    with pytest.raises(MeasurementContractError) as error:verify_measurement_bundle(tmp_path)
    assert error.value.code=='BUNDLE_INCOMPLETE'
    run=command('measurement-verify','--bundle',tmp_path)
    assert run.returncode==3 and json.loads(run.stderr)['code']=='BUNDLE_INCOMPLETE'


def test_obsolete_cli_does_not_accept_caller_computed_bytes(tmp_path):
    run=command('measurement-replay','--bundle',tmp_path,'--output-dir',tmp_path/'new',
                '--result','caller.json','--trace','caller.json')
    assert run.returncode==2 and not run.stdout
