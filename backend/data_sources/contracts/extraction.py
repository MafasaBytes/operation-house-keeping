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
from backend.data_sources.contracts.api import ApiExtractionManifest
from backend.data_sources.contracts.pdf import PdfExtractionManifest


class CsvTableResult(_FrozenModel):
    kind: Literal["csv_table"] = "csv_table"
    table: ExtractedTable


class StepManifestResult(_FrozenModel):
    kind: Literal["step_manifest"] = "step_manifest"
    manifest: StepExtractionManifest


class PdfManifestResult(_FrozenModel):
    kind: Literal["pdf_manifest"] = "pdf_manifest"
    manifest: PdfExtractionManifest


class ApiObservationsResult(_FrozenModel):
    kind: Literal["api_observations"] = "api_observations"
    manifest: ApiExtractionManifest


ExtractionOutcome = Literal["succeeded", "partial"]


class ExtractionResult(_FrozenModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    # 1 = DS-002-era artifacts (readable, never rewritten); 2 = current.
    schema_version: Literal[1, 2] = 2
    raw_record_id: RecordId
    extractor: ExtractorIdentity
    outcome: ExtractionOutcome
    warnings: list[str] = Field(default_factory=list)
    result: Union[
        CsvTableResult, StepManifestResult, PdfManifestResult, ApiObservationsResult
    ] = Field(discriminator="kind")

    def manifest_view(
        self,
    ) -> StepExtractionManifest | PdfExtractionManifest | ApiExtractionManifest:
        manifest = getattr(self.result, "manifest", None)
        if manifest is None:
            raise ValueError(f"result kind is {self.result.kind!r}, not a manifest")
        return manifest

    def table_view(self) -> ExtractedTable:
        if self.result.kind != "csv_table":
            raise ValueError(f"result kind is {self.result.kind!r}, not a CSV table")
        return self.result.table
