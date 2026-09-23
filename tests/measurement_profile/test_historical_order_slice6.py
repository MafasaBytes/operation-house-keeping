"""Same-author normative path derivation and real public-input ordering twins."""
import json
import pytest
from tests.measurement_profile.test_delivery_contract_mapping import recover_case, command
from tests.measurement_profile.test_final_boundaries_slice6 import amend_request
from applications.bounded_decision_workflow.measurement_contracts import canonical_json_bytes as wire


@pytest.mark.parametrize('repair', ['none', 'revision2', 'both'])
@pytest.mark.parametrize('reverse', [False, True])
def test_historical_path_order_public_twins(tmp_path, repair, reverse):
    iv, objects, pin = recover_case(tmp_path, 'CL-historical-invalid')
    if repair != 'none':
        def mutation(q, get, put):
            q2 = get(q['predecessor'])
            q1 = get(q2['predecessor'])
            # Reuse a complete, valid nominated procedure already in Q3.
            # Historical support remains empty: eligibility is not imported.
            valid = q['measurements'][0]
            if repair == 'both':
                q1['measurements'] = [valid]
                q2['predecessor'] = put(q1)
            q2['measurements'] = [valid]
            q['predecessor'] = put(q2)
        pin = amend_request(iv, objects, mutation)
    if reverse:
        alternate = tmp_path / 'reverse-objects'; alternate.mkdir()
        for p in sorted(objects.iterdir(), reverse=True):
            data = p.read_bytes()
            if not p.name.endswith('.nm.basis'):
                value = json.loads(data)
                assert wire(dict(reversed(list(value.items())))) == data
            (alternate / p.name).write_bytes(data)
        objects = alternate
        value = json.loads(iv.read_bytes())
        assert wire(dict(reversed(list(value.items())))) == iv.read_bytes()
    out = tmp_path / 'result'
    run = command('measurement-evaluate', '--invocation', iv, '--objects-dir', objects,
                  '--authority-pin', pin, '--output-dir', out)
    (tmp_path/'actual.stdout').write_bytes(run.stdout)
    (tmp_path/'actual.stderr').write_bytes(run.stderr)
    if repair == 'both':
        assert run.returncode == 0, run.stderr
        assert run.stderr == b''
        result = json.loads((out/'result.json').read_bytes())
        assert result['ranking']['disposition'] == 'preferred_within_supplied_set'
        assert [s['worst'] for s in result['ranking']['scores']] == [1, 2]
    else:
        # Hand-derived ordering, never imported from the runtime or oracle.
        paths = ['/predecessor/measurements/0/decoder',
                 '/predecessor/predecessor/measurements/0/decoder']
        assert ord('m') < ord('p') and paths == sorted(paths)
        expected = paths[0 if repair == 'none' else 1]
        assert run.returncode == 3 and run.stdout == b''
        d = json.loads(run.stderr)
        assert d['code'] == 'DECODER_INVALID' and d['stage'] == 'phase_3'
        assert d['target']['field'] == expected
        assert d['target']['request'] == json.loads(iv.read_bytes())['request']
        assert run.stderr == wire(d) + b'\n'
        assert not out.exists()
