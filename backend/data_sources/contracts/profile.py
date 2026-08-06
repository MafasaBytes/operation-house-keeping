"""Application source profile: planning state only.

A profile entry says what the application intends and where a source family
sits on the roadmap. Runtime truths — availability, configuration,
connectivity, health, validation evidence — live exclusively in the
operational models (ConnectorStatusReport, SourceHealth, runs) and must
never appear here.
"""

from typing import Literal

from pydantic import Field, model_validator

from backend.data_sources.contracts.models import _FrozenModel

Requirement = Literal["required", "optional"]
RoadmapStage = Literal["validated", "next", "later", "not_started"]


class SourceProfileEntry(_FrozenModel):
    source_family: str = Field(min_length=1)
    requirement: Requirement
    roadmap_stage: RoadmapStage
    enabled_for_profile: bool
    justification: str


class SourceProfile(_FrozenModel):
    profile_id: str
    entries: list[SourceProfileEntry]

    @model_validator(mode="after")
    def _unique_families(self) -> "SourceProfile":
        families = [e.source_family for e in self.entries]
        if len(set(families)) != len(families):
            raise ValueError("a source family may appear only once in a profile")
        return self
