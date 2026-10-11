"""Companion v3 owning bytes and refusals; historical contracts stay unchanged."""
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path

PROFILE = 'bdw.checked-temperature.v1'
SCHEMAS_SHA256 = 'e6fef4ad9501c57a51e1367f9f6e4410b544d019dce0a3a0ddcd09baf9c8c28c'
RULE_SHA256 = '529b18406a7daf8ed0218b72a12d031c7cca76c3fb0cc574b420da620dfb858b'
PRESET_SHA256 = 'c6f0cafaed466ab8a18d3d7340632a9863d0526e4656b8311b8db55c96f03125'
CAPS = {'ct.t1-world.v1': 8192, 'ct.t1-context.v1': 196608,
        'ct.t1-simulation-target.v1': 16384, 'ct.t1-simulation-permission.v1': 4096,
        'ct.t1-producer-manifest.v1': 32768, 'ct.t1-handoff.v1': 32768,
        'ct.t1-workflow-receipt.v1': 16384}
SUBJECT = 'ent_' + '9' * 32
VARIABLE = 'var_' + '1' * 32
REVISION = 'mrv_d93f49fd3a20eabde14c2015430e8382b374d51b6a63cadb5e7eb9dbaad5e5e4'


class SimRefusal(Exception):
    def __init__(self, code, order, target='/', exit_class=3):
        super().__init__(code)
        self.code, self.order, self.target, self.exit_class = code, str(order), target, exit_class

    def record(self):
        return {'schema': 'ct.t1-diagnostic.v1', 'code': self.code, 'order': self.order,
                'target': self.target, 'exit_class': self.exit_class}


def refuse(code, order, target='/', exit_class=3):
    raise SimRefusal(code, order, target, exit_class)


def canonical_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                      allow_nan=False).encode('utf-8')


def sha(wire):
    return hashlib.sha256(wire).hexdigest()


def ref(kind, wire):
    return {'kind': kind, 'sha256': sha(wire)}


def rational(value):
    q = Fraction(value)
    return {'numerator': str(q.numerator), 'denominator': str(q.denominator)}


def fraction(value):
    return Fraction(int(value['numerator']), int(value['denominator']))


def instant(text, target='/J/window'):
    try:
        return datetime.strptime(text, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        refuse('SIM_SCHEMA_INVALID', 0, target)


def diagnostic_bytes(error):
    return canonical_bytes(error.record()) + b'\n'


_wire = Path(__file__).with_name('t1_companion_schemas.json').read_bytes()
if sha(_wire) != SCHEMAS_SHA256:
    refuse('SIM_EDITION_NOT_PERMITTED', 2, '/schemas')
SCHEMAS = json.loads(_wire)
