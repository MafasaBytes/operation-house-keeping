from fractions import Fraction
import pytest
from applications.bounded_decision_workflow.t1_carrier import Clocks, carrier_bytes, fixed
from applications.bounded_decision_workflow.t1_contracts import SimRefusal


def test_boundary_decimal_exact_fixed_point():
    assert fixed(Fraction(600001, 10000)) == '60.0001'


def test_sorted_carrier_numbers_and_unicode():
    assert carrier_bytes({'z': Fraction(3, 2), 'a': '/é'}) == b'{"a":"/\xc3\xa9","z":1.5}'


def test_binary_float_cannot_silently_become_exact_carrier():
    with pytest.raises(TypeError):
        carrier_bytes(0.1)


def test_wall_clock_endpoint_and_exhaustion():
    clock = Clocks('2026-10-08T09:00:00Z', wall_limit=2)
    wall = clock.wall('connector')
    assert wall().isoformat() == '2026-10-08T09:00:01+00:00'
    assert wall().isoformat() == '2026-10-08T09:00:02+00:00'
    with pytest.raises(SimRefusal) as exc:
        wall()
    assert (exc.value.exit_class, len(clock.wall_calls)) == (4, 2)


def test_monotonic_ticks_are_exact_binary_values():
    clock = Clocks('2026-10-08T09:00:00Z')
    tick = clock.monotonic('connector')
    assert Fraction(tick()) == Fraction(1, 1024)
    assert Fraction(tick()) == Fraction(1, 512)
