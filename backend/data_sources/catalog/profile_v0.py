"""Application Source Profile v0 (owner-approved, 2026-08-06).

Planning state only: what the intended application requires and where each
source family sits on the roadmap. Runtime capability lives exclusively in
the operational models.
"""

from backend.data_sources.contracts import SourceProfile, SourceProfileEntry

APPLICATION_PROFILE_V0 = SourceProfile(
    profile_id="v0",
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
            roadmap_stage="next",
            enabled_for_profile=True,
            justification="DS-002: neutral CAD structure and visualization evidence",
        ),
        SourceProfileEntry(
            source_family="pdf_drawing_manual",
            requirement="required",
            roadmap_stage="later",
            enabled_for_profile=False,
            justification="drawings/manuals needed later with page-level provenance",
        ),
        SourceProfileEntry(
            source_family="operational_api_or_telemetry",
            requirement="required",
            roadmap_stage="later",
            enabled_for_profile=False,
            justification="one live operational source needed for state evidence",
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
