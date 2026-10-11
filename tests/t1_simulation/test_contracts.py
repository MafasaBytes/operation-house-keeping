"""Unexecuted development checks; not a complete workflow proof."""
from pathlib import Path
from applications.bounded_decision_workflow import t1_contracts as c


def test_vendored_schema_exact_commitment():
    assert c.sha(Path(c.__file__).with_name('t1_companion_schemas.json').read_bytes()) == c.SCHEMAS_SHA256


def test_refusal_wire_is_canonical_and_single_lf():
    e = c.SimRefusal('SIM_PRECISION_LIMIT', 5, '/W/theta')
    assert c.diagnostic_bytes(e) == (b'{"code":"SIM_PRECISION_LIMIT","exit_class":3,"order":"5",'
                                    b'"schema":"ct.t1-diagnostic.v1","target":"/W/theta"}\n')
