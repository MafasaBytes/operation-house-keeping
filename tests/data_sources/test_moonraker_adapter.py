"""Moonraker adapter and hardened-parser tests against the frozen,
hand-authored fixtures (oracle: golden_moonraker.py)."""

from pathlib import Path

import pytest

from backend.data_sources.adapters.moonraker import (
    MOONRAKER_EXTRACTION_ROUTE,
    MoonrakerAdapter,
)
from backend.data_sources.contracts import ExtractionError
from backend.data_sources.extractors.operational import (
    JsonLimits,
    parse_bounded_json,
)

from tests.data_sources import golden_moonraker as golden

FIXTURES = Path("backend/data_sources/testing/fixtures/api")
RID = "a" * 32


def load(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def extract(name: str, item_key: str = "printer_objects"):
    return MoonrakerAdapter().extract(load(name), RID, item_key)


class TestHardenedParser:
    def test_duplicate_keys_rejected(self):
        with pytest.raises(ExtractionError) as excinfo:
            parse_bounded_json(load("moonraker_dup_key.json"), JsonLimits())
        assert excinfo.value.error_code == "EXTRACT_API_MALFORMED_JSON"
        assert "duplicate" in str(excinfo.value)

    def test_nan_rejected(self):
        with pytest.raises(ExtractionError):
            parse_bounded_json(load("moonraker_nan.json"), JsonLimits())

    def test_invalid_utf8_rejected(self):
        with pytest.raises(ExtractionError) as excinfo:
            parse_bounded_json(load("moonraker_bad_utf8.bin"), JsonLimits())
        assert "utf-8" in str(excinfo.value).lower()

    def test_depth_bomb_rejected(self):
        with pytest.raises(ExtractionError) as excinfo:
            parse_bounded_json(load("moonraker_depth_bomb.json"),
                               JsonLimits(max_depth=64))
        assert excinfo.value.error_code == "EXTRACT_API_LIMIT_EXCEEDED"

    def test_node_and_string_limits(self):
        with pytest.raises(ExtractionError):
            parse_bounded_json(b'[1,2,3,4,5]', JsonLimits(max_nodes=3))
        with pytest.raises(ExtractionError):
            parse_bounded_json(b'["' + b"x" * 100 + b'"]',
                               JsonLimits(max_string_length=10))

    def test_malformed_rejected(self):
        with pytest.raises(ExtractionError) as excinfo:
            parse_bounded_json(load("moonraker_malformed.json"), JsonLimits())
        assert excinfo.value.error_code == "EXTRACT_API_MALFORMED_JSON"


class TestPlan:
    def test_canonical_query_matches_designed_selection(self):
        plan = MoonrakerAdapter().plan()
        assert [item.item_key for item in plan] == ["server_info", "printer_objects"]
        assert plan[0].path_and_query == "/server/info"
        assert plan[1].path_and_query == golden.CANONICAL_QUERY

    def test_route(self):
        assert MOONRAKER_EXTRACTION_ROUTE == "api:moonraker:v1"


class TestPrinterObjectsExtraction:
    def test_observations_match_golden_oracle(self):
        manifest = extract("moonraker_printer_objects.json")
        by_pointer = {o.json_pointer: o for o in manifest.observations}
        assert set(by_pointer) == set(golden.PRINTER_OBJECTS_EXPECTED)
        for pointer, (subject, value_json, json_type) in (
            golden.PRINTER_OBJECTS_EXPECTED.items()
        ):
            obs = by_pointer[pointer]
            assert obs.subject_identifier == subject, pointer
            assert obs.value_json == value_json, pointer
            assert obs.json_type == json_type, pointer
            assert obs.declared_unit is None
            assert obs.semantics == "snapshot"
            assert "unit_not_declared" in obs.quality_flags
        assert manifest.levels_achieved == [0, 1, 2]

    def test_monotonic_marker_on_every_observation(self):
        manifest = extract("moonraker_printer_objects.json")
        for obs in manifest.observations:
            marker = obs.source_time
            assert marker.kind == "monotonic"
            assert marker.value == golden.EVENTTIME_LEXEME  # verbatim lexeme
            assert marker.clock_id == "klipper_host_monotonic"
            assert marker.unit == "seconds"
            assert marker.pointer == "/result/eventtime"

    def test_position_array_survives_with_number_types(self):
        manifest = extract("moonraker_printer_objects.json")
        position = next(o for o in manifest.observations
                        if o.json_pointer.endswith("/position"))
        assert position.value_json == "[1.0,2.0,0.3,0.0]"  # numbers, not strings
        assert position.json_type == "array"

    def test_deterministic_across_replay(self):
        first = extract("moonraker_printer_objects.json")
        second = extract("moonraker_printer_objects.json")
        assert first.model_dump_json() == second.model_dump_json()

    def test_changed_snapshot_changes_only_designed_values(self):
        changed = extract("moonraker_printer_objects_changed.json")
        by_pointer = {o.json_pointer: o.value_json for o in changed.observations}
        assert by_pointer["/result/status/extruder/temperature"] == "60.4"
        assert by_pointer["/result/status/heater_bed/temperature"] == "45.2"


class TestOmissionAndDrift:
    def test_requested_field_omitted_is_specific_evidence(self):
        manifest = extract("moonraker_objects_omitted.json")
        joined = " ".join(manifest.warnings)
        for fragment in golden.OMITTED_EXPECTED_WARNING_FRAGMENTS:
            assert fragment in joined
        assert "schema_drift" not in joined  # omission is NOT drift
        pointers = {o.json_pointer for o in manifest.observations}
        assert "/result/status/heater_bed/temperature" not in pointers
        assert "/result/status/toolhead/homed_axes" in pointers

    def test_unknown_objects_and_attributes_are_drift(self):
        manifest = extract("moonraker_drift.json")
        drift = [w for w in manifest.warnings if w.startswith("schema_drift")]
        joined = " ".join(drift)
        for fragment in golden.DRIFT_EXPECTED_FRAGMENTS:
            assert fragment in joined
        # drift never becomes observations
        assert all("chamber" not in o.json_pointer for o in manifest.observations)

    def test_hostile_names_render_escaped_in_drift(self):
        manifest = extract("moonraker_hostile_names.json")
        joined = " ".join(manifest.warnings)
        for fragment in golden.HOSTILE_DRIFT_POINTER_FRAGMENTS:
            assert fragment in joined

    def test_missing_eventtime_flags_not_fabricates(self):
        manifest = extract("moonraker_no_eventtime.json")
        for obs in manifest.observations:
            assert obs.source_time.kind == "unavailable"
            assert "missing_source_timestamp" in obs.quality_flags


class TestServerInfoExtraction:
    def test_selected_properties_only_no_drift_noise(self):
        manifest = extract("moonraker_server_info.json", item_key="server_info")
        by_pointer = {o.json_pointer: o for o in manifest.observations}
        assert set(by_pointer) == set(golden.SERVER_INFO_EXPECTED)
        for pointer, (subject, value_json, json_type) in (
            golden.SERVER_INFO_EXPECTED.items()
        ):
            assert by_pointer[pointer].subject_identifier == subject
            assert by_pointer[pointer].value_json == value_json
            assert by_pointer[pointer].json_type == json_type
            assert by_pointer[pointer].source_time.kind == "unavailable"
        # documented rich response: unknown keys are NOT drift here
        assert not any(w.startswith("schema_drift") for w in manifest.warnings)

    def test_envelope_without_result_quarantinable(self):
        with pytest.raises(ExtractionError) as excinfo:
            MoonrakerAdapter().extract(b'{"data": {}}', RID, "server_info")
        assert excinfo.value.error_code == "EXTRACT_API_MALFORMED_JSON"
