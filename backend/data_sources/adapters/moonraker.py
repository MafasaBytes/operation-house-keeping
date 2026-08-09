"""Moonraker protocol adapter (DS-004 showcase).

Owns everything Moonraker-specific: the fixed bounded endpoint plan,
canonical request construction, ``{"result": ...}`` envelope
interpretation, subject-identifier extraction, and observation selection.
Requested-but-omitted objects/attributes are expected evidence — the
official API omits missing requested items without an error — and are
never treated as malformed responses or schema drift.
"""

import hashlib
from dataclasses import dataclass

from backend.data_sources.contracts import (
    ApiExtractionManifest,
    ExtractionError,
    ExtractorIdentity,
    MonotonicTimeMarker,
    OperationalObservation,
    UnavailableTimeMarker,
)
from backend.data_sources.extractors.operational import (
    JsonLimits,
    canonical_json,
    json_pointer_of,
    json_type_of,
    parse_bounded_json,
)
from backend.data_sources.provenance import derive_entity_id

MOONRAKER_ADAPTER_ID = "moonraker"
MOONRAKER_EXTRACTION_ROUTE = "api:moonraker:v1"
MOONRAKER_EXTRACTOR_VERSION = "1.0.0"

# Owner-approved bounded object selection (attributes sorted).
REQUESTED_OBJECTS: dict[str, tuple[str, ...]] = {
    "extruder": ("target", "temperature"),
    "heater_bed": ("target", "temperature"),
    "print_stats": ("print_duration", "state", "total_duration"),
    "toolhead": ("homed_axes", "position"),
    "virtual_sdcard": ("is_active", "progress"),
}

SERVER_INFO_PROPERTIES = ("klippy_connected", "klippy_state")


@dataclass(frozen=True)
class PlanItem:
    item_key: str
    endpoint_id: str
    path_and_query: str


def _canonical_query() -> str:
    parts = [
        f"{obj}={','.join(attrs)}" for obj, attrs in sorted(REQUESTED_OBJECTS.items())
    ]
    return "/printer/objects/query?" + "&".join(parts)


class MoonrakerAdapter:
    adapter_id = MOONRAKER_ADAPTER_ID
    extraction_route = MOONRAKER_EXTRACTION_ROUTE

    def plan(self) -> list[PlanItem]:
        return [
            PlanItem("server_info", "server_info", "/server/info"),
            PlanItem("printer_objects", "printer_objects_query", _canonical_query()),
        ]

    def auth_headers(self, resolver, credential_reference: str | None) -> dict:
        if credential_reference is None:
            return {}
        return {"X-Api-Key": resolver.resolve(credential_reference)}

    # -- extraction
    def identity(self) -> ExtractorIdentity:
        fingerprint = hashlib.sha256(_canonical_query().encode()).hexdigest()[:16]
        return ExtractorIdentity(
            name="moonraker_extractor",
            version=MOONRAKER_EXTRACTOR_VERSION,
            toolchain="python-stdlib-json",
            config_fingerprint=fingerprint,
        )

    def extract(
        self, payload: bytes, raw_record_id: str, item_key: str,
        limits: JsonLimits | None = None,
    ) -> ApiExtractionManifest:
        document = parse_bounded_json(payload, limits or JsonLimits())
        if not isinstance(document, dict) or not isinstance(
            document.get("result"), dict
        ):
            raise ExtractionError(
                "EXTRACT_API_MALFORMED_JSON",
                "response envelope is unusable: no {'result': ...} object",
            )
        result = document["result"]
        if item_key == "printer_objects":
            return self._extract_printer_objects(result, raw_record_id)
        if item_key == "server_info":
            return self._extract_server_info(result, raw_record_id)
        raise ExtractionError(
            "EXTRACT_API_MALFORMED_JSON", f"unknown acquisition item {item_key!r}"
        )

    def _observation(self, raw_record_id, pointer, subject, value, marker, flags):
        return OperationalObservation(
            observation_id=derive_entity_id(
                raw_record_id, MOONRAKER_EXTRACTOR_VERSION, f"obs:{pointer}"
            ),
            raw_record_id=raw_record_id,
            json_pointer=pointer,
            subject_identifier=subject,
            value_json=canonical_json(value),
            json_type=json_type_of(value),
            declared_unit=None,  # Moonraker declares no units — honestly None
            semantics="snapshot",
            source_time=marker,
            quality_flags=flags,
        )

    def _manifest(self, raw_record_id, item_key, observations, warnings):
        return ApiExtractionManifest(
            raw_record_id=raw_record_id,
            extractor=self.identity(),
            adapter_id=self.adapter_id,
            item_key=item_key,
            observations=observations,
            levels_supported=[0, 1, 2],
            levels_achieved=[0, 1, 2] if observations else [0, 1],
            unsupported_features=[],
            warnings=warnings,
        )

    def _extract_printer_objects(self, result, raw_record_id):
        warnings: list[str] = []
        eventtime = result.get("eventtime")
        if eventtime is not None and json_type_of(eventtime) == "number":
            marker = MonotonicTimeMarker(
                value=canonical_json(eventtime),  # exact lexeme, no epoch fabrication
                unit="seconds",
                clock_id="klipper_host_monotonic",
                origin="unknown",
                pointer="/result/eventtime",
            )
            base_flags = ["unit_not_declared"]
        else:
            marker = UnavailableTimeMarker(
                reason="response carries no eventtime source marker"
            )
            base_flags = ["unit_not_declared", "missing_source_timestamp"]
            warnings.append("missing_source_timestamp: /result/eventtime absent")

        status = result.get("status")
        if not isinstance(status, dict):
            raise ExtractionError(
                "EXTRACT_API_MALFORMED_JSON",
                "response envelope is unusable: no result.status object",
            )

        observations = []
        for obj_name, attrs in sorted(REQUESTED_OBJECTS.items()):
            obj = status.get(obj_name)
            if obj is None:
                warnings.append(f"requested_field_omitted: {obj_name}")
                continue
            if not isinstance(obj, dict):
                warnings.append(
                    f"schema_drift: requested object {obj_name!r} is not an object"
                )
                continue
            for attr in attrs:
                if attr not in obj:
                    warnings.append(f"requested_field_omitted: {obj_name}.{attr}")
                    continue
                observations.append(self._observation(
                    raw_record_id,
                    json_pointer_of("result", "status", obj_name, attr),
                    obj_name, obj[attr], marker, list(base_flags),
                ))
            for unknown in sorted(set(obj) - set(attrs)):
                warnings.append(
                    "schema_drift: unrequested attribute at "
                    + json_pointer_of("result", "status", obj_name, unknown)
                    + f" ({obj_name}.{unknown})"
                )
        for unknown in sorted(set(status) - set(REQUESTED_OBJECTS)):
            warnings.append(
                "schema_drift: unrequested object at "
                + json_pointer_of("result", "status", unknown)
                + f" ({unknown})"
            )
        return self._manifest(raw_record_id, "printer_objects", observations, warnings)

    def _extract_server_info(self, result, raw_record_id):
        # /server/info's documented response is rich; only the selected
        # properties are observed and unknown keys are expected (no drift).
        marker = UnavailableTimeMarker(reason="endpoint provides no source time")
        warnings: list[str] = []
        observations = []
        for prop in SERVER_INFO_PROPERTIES:
            if prop not in result:
                warnings.append(f"requested_field_omitted: {prop}")
                continue
            observations.append(self._observation(
                raw_record_id, json_pointer_of("result", prop), "server",
                result[prop], marker,
                ["unit_not_declared", "missing_source_timestamp"],
            ))
        return self._manifest(raw_record_id, "server_info", observations, warnings)
