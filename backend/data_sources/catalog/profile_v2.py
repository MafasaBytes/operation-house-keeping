"""Application Source Profile v2 (DS-004, 2026-08-07).

All four required source families are now validated. Planning state only —
runtime capability remains evidence-driven through the connector status
ladder, and the operational family's `validated` stage rests on a real
accepted ingestion run against actual Moonraker software (virtual
Klipper/printer stack, image digest-pinned; evidence recorded in the
DS-004 spec and completion report).
"""

from backend.data_sources.contracts import SourceProfile, SourceProfileEntry

APPLICATION_PROFILE_V2 = SourceProfile(
    profile_id="v2",
    entries=[
        SourceProfileEntry(
            source_family="csv_bom",
            requirement="required",
            roadmap_stage="validated",
            enabled_for_profile=True,
            justification="DS-001 validated the source boundary with a BOM CSV",
        ),
        SourceProfileEntry(
            source_family="step_assembly",
            requirement="required",
            roadmap_stage="validated",
            enabled_for_profile=True,
            justification="DS-002 accepted: neutral CAD structure + glTF evidence",
        ),
        SourceProfileEntry(
            source_family="pdf_drawing_manual",
            requirement="required",
            roadmap_stage="validated",
            enabled_for_profile=True,
            justification="DS-003 + repair slices accepted: page/region provenance",
        ),
        SourceProfileEntry(
            source_family="operational_api_or_telemetry",
            requirement="required",
            roadmap_stage="validated",
            enabled_for_profile=True,
            justification="DS-004: accepted ingestion runs against real "
            "Moonraker software on a digest-pinned virtual Klipper stack "
            "(Klipper d865997, Moonraker API 1.5.0)",
        ),
        SourceProfileEntry(
            source_family="excel_workbook",
            requirement="optional",
            roadmap_stage="not_started",
            enabled_for_profile=False,
            justification="optional until an application need justifies it",
        ),
        SourceProfileEntry(
            source_family="sql_snapshot",
            requirement="optional",
            roadmap_stage="not_started",
            enabled_for_profile=False,
            justification="optional until an application need justifies it",
        ),
        SourceProfileEntry(
            source_family="additional_apis",
            requirement="optional",
            roadmap_stage="not_started",
            enabled_for_profile=False,
            justification="optional until an application need justifies it",
        ),
        SourceProfileEntry(
            source_family="native_cad",
            requirement="optional",
            roadmap_stage="not_started",
            enabled_for_profile=False,
            justification="vendor pipelines only if the application demands them",
        ),
        SourceProfileEntry(
            source_family="other_sensor_protocols",
            requirement="optional",
            roadmap_stage="not_started",
            enabled_for_profile=False,
            justification="optional until an application need justifies it",
        ),
    ],
)
