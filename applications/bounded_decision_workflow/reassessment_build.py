"""Actual clean executable identity for the approved reassessment contract set."""
import json
from . import measurement_build
from .measurement_contracts import canonical_json_bytes
from .measurement_wire import sha
from .reassessment_contracts import PROFILE

# Exact approved package manifest binds the complete design, amendment, schemas,
# accounting policy and plan. No loose preparation directory is consulted.
CONTRACT_SHA = '3a7c1d176c2231e8b9b938e404b2500e32eb87bfd12cdf046f144d0953edf0cf'


def identity(work=None):
    original = measurement_build.identity(work)
    actual = json.loads(original)
    if work is not None:work.physical['build_json_decode_bytes']=work.physical.get('build_json_decode_bytes',0)+len(original)
    body = {k:actual[k] for k in ('checkpoint','source_manifest','environment_manifest',
                                'entrypoint','contract_sha256','resource_policy_sha256')}
    body['contract_sha256'] = CONTRACT_SHA
    body['supported_nm_contract_sha256'] = measurement_build.CONTRACT_SHA
    if work is not None:work.physical['build_hash_bytes']=work.physical.get('build_hash_bytes',0)+len(canonical_json_bytes(body))
    raw = canonical_json_bytes(dict(schema='nr.build.v2',profile=PROFILE,
        id=sha(canonical_json_bytes(body)),revision=1,predecessor=None,**body))
    if work is not None:work.high('build_bytes',len(raw))
    return raw
