"""Hand-authored golden expectations for the frozen Moonraker fixtures.

Independent oracle: values are written from the designed fixture content
(itself hand-authored from the public Moonraker API documentation), never
from extractor output.
"""

CANONICAL_QUERY = (
    "/printer/objects/query"
    "?extruder=target,temperature"
    "&heater_bed=target,temperature"
    "&print_stats=print_duration,state,total_duration"
    "&toolhead=homed_axes,position"
    "&virtual_sdcard=is_active,progress"
)

EVENTTIME_LEXEME = "3721.845"

# pointer -> (subject, value_json, json_type)
PRINTER_OBJECTS_EXPECTED = {
    "/result/status/extruder/temperature": ("extruder", "60.1", "number"),
    "/result/status/extruder/target": ("extruder", "60.0", "number"),
    "/result/status/heater_bed/temperature": ("heater_bed", "45.2", "number"),
    "/result/status/heater_bed/target": ("heater_bed", "45.0", "number"),
    "/result/status/toolhead/homed_axes": ("toolhead", '"xyz"', "string"),
    "/result/status/toolhead/position": ("toolhead", "[1.0,2.0,0.3,0.0]", "array"),
    "/result/status/print_stats/state": ("print_stats", '"printing"', "string"),
    "/result/status/print_stats/print_duration": ("print_stats", "512.4", "number"),
    "/result/status/print_stats/total_duration": ("print_stats", "640.9", "number"),
    "/result/status/virtual_sdcard/progress": ("virtual_sdcard", "0.42", "number"),
    "/result/status/virtual_sdcard/is_active": ("virtual_sdcard", "true", "boolean"),
}

SERVER_INFO_EXPECTED = {
    "/result/klippy_connected": ("server", "true", "boolean"),
    "/result/klippy_state": ("server", '"ready"', "string"),
}

# moonraker_objects_omitted.json: heater_bed and virtual_sdcard objects
# absent; toolhead.position attribute absent.
OMITTED_EXPECTED_WARNING_FRAGMENTS = [
    "requested_field_omitted: heater_bed",
    "requested_field_omitted: virtual_sdcard",
    "requested_field_omitted: toolhead.position",
]

DRIFT_EXPECTED_FRAGMENTS = [
    "chamber",            # unknown object
    "extruder.power",     # unknown attribute
]

HOSTILE_DRIFT_POINTER_FRAGMENTS = ["fan~01", "probe~1z"]  # escaped in warnings
