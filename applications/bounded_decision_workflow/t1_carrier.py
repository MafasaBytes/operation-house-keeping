"""Exact carrier arithmetic and injected clocks. No model applicability gates."""
import copy
from datetime import timedelta
from email.utils import format_datetime
from fractions import Fraction
import json
from urllib.parse import urlsplit

from .t1_contracts import instant, refuse

PRINTER_PATH = ('/printer/objects/query?extruder=target,temperature&heater_bed=target,temperature'
                '&print_stats=print_duration,state,total_duration&toolhead=homed_axes,position'
                '&virtual_sdcard=is_active,progress')
PATHS = ('/server/info', PRINTER_PATH)


def fixed(value):
    """Shortest exact fixed point; no rounding, binary floats, or signed zero."""
    if isinstance(value, float):
        raise TypeError('binary float is outside the carrier domain')
    q = Fraction(value)
    scale = 0
    while 10 ** scale % q.denominator:
        scale += 1
        if scale > 32:
            raise ValueError('non-decimal rational')
    n = q.numerator * (10 ** scale // q.denominator)
    digits = str(abs(n)).zfill(scale + 1)
    text = digits if not scale else (digits[:-scale] + '.' + digits[-scale:]).rstrip('0').rstrip('.')
    return ('-' if n < 0 else '') + text


def carrier_bytes(value):
    if value is None:
        return b'null'
    if type(value) is bool:
        return b'true' if value else b'false'
    if isinstance(value, (int, Fraction)):
        return fixed(value).encode('ascii')
    if isinstance(value, str):
        # UTF-8 rejects unpaired surrogates. JSON leaves slash unescaped.
        return json.dumps(value, ensure_ascii=False).encode('utf-8')
    if isinstance(value, list):
        return b'[' + b','.join(carrier_bytes(v) for v in value) + b']'
    if isinstance(value, dict) and all(isinstance(k, str) for k in value):
        return b'{' + b','.join(carrier_bytes(k) + b':' + carrier_bytes(value[k])
                                for k in sorted(value)) + b'}'
    raise TypeError('outside carrier domain')


def derive(preset_wire, world, target, pins):
    """Call only after admission; the world need not satisfy evaluated premises."""
    preset = json.loads(preset_wire, parse_float=Fraction)
    reading = sum((Fraction(world[k]) for k in ('theta', 'beta', 'epsilon')), Fraction())
    marker = {'logical_run_id': target['logical_run_id'], 'simulation_target_sha256': pins['J'],
              'simulation_permission_sha256': pins['G'], 'world_sha256': pins['W']}
    bodies = []
    for name in ('server_info', 'printer_objects'):
        body = copy.deepcopy(preset['responses'][name]['body'])
        if name == 'printer_objects':
            body['result']['status']['extruder']['temperature'] = reading
        body['_application_simulation'] = marker
        bodies.append(carrier_bytes(body))
    return tuple(bodies)


class Clocks:
    def __init__(self, t0, *, wall_limit=64, monotonic_limit=128):
        self.start = instant(t0)
        self.wall_limit, self.monotonic_limit = wall_limit, monotonic_limit
        self.wall_calls, self.monotonic_calls = [], []

    def wall(self, caller):
        def tick():
            k = len(self.wall_calls) + 1
            if k > self.wall_limit:
                refuse('SIM_RESOURCE_LIMIT', 7, '/J/resource_bounds/wall_clock_calls', 4)
            self.wall_calls.append({'caller': caller, 'ordinal': k, 'tick': k})
            return self.start + timedelta(seconds=k)
        return tick

    def monotonic(self, caller):
        def tick():
            k = len(self.monotonic_calls) + 1
            if k > self.monotonic_limit:
                refuse('SIM_RESOURCE_LIMIT', 7, '/J/resource_bounds/monotonic_calls', 4)
            self.monotonic_calls.append({'caller': caller, 'ordinal': k, 'tick': k})
            # k/1024 is exactly representable as binary float, as required by connector API.
            return k / 1024
        return tick


class Transport:
    def __init__(self, origin, bodies, t0, max_response_bytes=16384):
        self.origin, self.bodies = origin, bodies
        self.limit = max_response_bytes
        self.headers = {'Content-Type': 'application/json',
                        'Date': format_datetime(instant(t0) + timedelta(seconds=5), usegmt=True)}
        self.calls = []

    def __call__(self, request):
        from backend.data_sources.connectors.http_api import TransportResponse
        k = len(self.calls)
        parts = urlsplit(request.url)
        origin = parts.scheme + '://' + parts.netloc
        path = parts.path + ('?' + parts.query if parts.query else '')
        if k >= 2 or origin != self.origin or path != PATHS[k] or request.headers:
            refuse('SIM_TRANSPORT_MISMATCH', 7, '/transport/' + str(k))
        if len(self.bodies[k]) > self.limit:
            refuse('SIM_RESOURCE_LIMIT', 7, '/J/resource_bounds/response_bytes', 4)
        self.calls.append({'ordinal': k + 1, 'origin': origin, 'path': parts.path,
                           'query': parts.query, 'request_header_names': [], 'response_status': 200,
                           'response_headers': sorted(self.headers.items())})
        return TransportResponse(status=200, headers=self.headers.copy(), body=self.bodies[k])
