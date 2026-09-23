"""Read-only Slice 5 work observation; not a production option or test bypass.

Run at the recorded clean code checkout, with the provisioned interpreter.
Inputs are exact files from the final tests, never expected-result fixtures.
The profiler observes the actual Work object on evaluate's return; it does not
replace functions, resolvers, validators, hashes, inputs or computed results.
"""
import json
from pathlib import Path
import sys
import tempfile

from applications.bounded_decision_workflow import measurement_runtime as runtime

SOURCE = Path('/tmp/nm-slice5-final-Nj7rj9')
DEST = Path(tempfile.mkdtemp(prefix='nm-slice5-observed-', dir='/tmp'))
observations = []


def observe(frame, event, arg):
    if event == 'return' and frame.f_code is runtime.evaluate.__code__:
        work = frame.f_locals['work']
        observations.append({'logical_work': dict(work.logical),
                             'physical_work': dict(work.physical)})


for name, directory in [('P', 'test_exact_frozen_semantic_fie0'),
                        ('history4', 'test_logical_exact_limit_plus_0'),
                        ('denied', 'test_complete_withholding_is_r2')]:
    inputs = SOURCE / directory / 'inputs'
    iv = json.loads((inputs / 'invocation.json').read_bytes())
    sys.setprofile(observe)
    try:
        receipt = runtime.evaluate(inputs / 'invocation.json', inputs / 'objects',
                                   iv['selection']['sha256'], DEST / name.lower())
    finally:
        sys.setprofile(None)
    observations[-1].update(case=name, receipt=receipt, output=str(DEST / name.lower()))

print(json.dumps({'method': 'read-only return-event observation; same author; not independent review',
                  'performance_note': 'profiler overhead is present; use unprofiled CLI records for timings',
                  'observations': observations}, indent=2))
