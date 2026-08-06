"""Extraction result envelope and extractor identity (DS-002 amendments).

Every persisted extraction is wrapped in an ``ExtractionResult`` carrying a
schema version, the extractor's identity, and an explicit outcome. A
quarantined extraction is represented by a ``QuarantineRecord`` and never by
an ``ExtractionResult``.
"""

from typing import Literal, Union

from pydantic import ConfigDict, Field

from backend.data_sources.contracts.cad import StepExtractionManifest
from backend.data_sources.contracts.identity import ExtractorIdentity
from backend.data_sources.contracts.models import (
    ExtractedTable,
    RecordId,
    _FrozenModel,
)


class CsvTableResult(_FrozenModel):
    kind: Literal["csv_table"] = "csv_table"
    table: ExtractedTable


class StepManifestResult(_FrozenModel):
    kind: Literal["step_manifest"] = "step_manifest"
    manifest: StepExtractionManifest


ExtractionOutcome = Literal["succeeded", "partial"]


class ExtractionResult(_FrozenModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal[1] = 1
    raw_record_id: RecordId
    extractor: ExtractorIdentity
    outcome: ExtractionOutcome
    warnings: list[str] = Field(default_factory=list)
    result: Union[CsvTableResult, StepManifestResult] = Field(discriminator="kind")

    def manifest_view(self) -> StepExtractionManifest:
        if self.result.kind != "step_manifest":
            raise ValueError(f"result kind is {self.result.kind!r}, not a STEP manifest")
        return self.result.manifest

    def table_view(self) -> ExtractedTable:
        if self.result.kind != "csv_table":
            raise ValueError(f"result kind is {self.result.kind!r}, not a CSV table")
        return self.result.table
