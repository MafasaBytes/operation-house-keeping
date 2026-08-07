"""CAD extraction contracts (DS-002).

Identity honesty rules:

- ``extractor_path_id`` is a toolchain identifier (XCAF/OCAF label entry),
  meaningful only relative to the extractor identity.
- ``source_native_id`` may only be set together with a stated
  ``source_native_id_basis`` describing the verified mapping. Nothing in
  DS-002 sets it.
- Units are never defaulted; every unit context declares its provenance.
"""

from typing import Annotated, Literal

from pydantic import Field, StringConstraints, field_validator, model_validator

from backend.data_sources.contracts.identity import ExtractorIdentity
from backend.data_sources.contracts.models import (
    RecordId,
    Sha256Checksum,
    _FrozenModel,
)

EntityId = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{32}$")]


class PropertyValue(_FrozenModel):
    name: str
    value: str
    value_type: Literal["string", "integer", "real", "boolean", "enumeration", "unknown"]
    unit: str | None = None
    raw_representation: str
    locator: str | None = None


UnitProvenance = Literal[
    "explicitly_declared", "verified_context", "configuration_supplied", "unavailable"
]


class UnitContext(_FrozenModel):
    context_id: str
    length_unit: str | None
    angle_unit: str | None
    provenance: UnitProvenance
    source_representation: str | None

    @model_validator(mode="after")
    def _declared_needs_source(self) -> "UnitContext":
        if self.provenance == "explicitly_declared" and not self.source_representation:
            raise ValueError(
                "an explicitly_declared unit context must carry the source "
                "representation it was read from"
            )
        return self


class TransformSpec(_FrozenModel):
    matrix: list[float] = Field(min_length=16, max_length=16)
    layout: Literal["row_major_4x4"]
    source_frame: str
    destination_frame: str
    handedness: Literal["right_handed", "left_handed"]
    length_unit_ref: str


class _SourceIdentified(_FrozenModel):
    extractor_path_id: str
    source_native_id: str | None = None
    source_native_id_basis: str | None = None
    raw_locator: str | None = None

    @model_validator(mode="after")
    def _native_id_needs_basis(self) -> "_SourceIdentified":
        if (self.source_native_id is None) != (self.source_native_id_basis is None):
            raise ValueError(
                "source_native_id and source_native_id_basis must be set "
                "together: a source-native identifier may only be claimed "
                "with the verified mapping that justifies it"
            )
        return self


class PartDefinition(_SourceIdentified):
    definition_id: EntityId
    name: str | None
    is_assembly: bool
    properties: list[PropertyValue] = Field(default_factory=list)
    unit_context_ref: str


class ComponentInstance(_SourceIdentified):
    """A usage occurrence: this definition is installed inside that parent
    definition (STEP NAUO semantics). A flattened per-path instance tree is
    a downstream view, not this contract. ``parent_definition_ref`` is None
    only for the synthesized root occurrence."""

    instance_id: EntityId
    definition_ref: EntityId
    parent_definition_ref: EntityId | None
    occurrence_name: str | None
    transform: TransformSpec


class TessellationParameters(_FrozenModel):
    linear_deflection: float = Field(gt=0)
    angular_deflection: float = Field(gt=0)
    relative: bool


class CoordinateConversion(_FrozenModel):
    source_frame: str
    target_frame: str
    target_length_unit: str
    converter: str


class ExtractionEnvironment(_FrozenModel):
    """Where/with-what a derivative was produced.

    ``component_versions`` names each output-affecting component (e.g.
    occt, pdfium, pillow). DS-002-era JSON carried a flat ``occt_version``
    field; it is converted on read and never rewritten on disk.
    """

    platform: str
    architecture: str
    component_versions: dict[str, str]

    @model_validator(mode="before")
    @classmethod
    def _legacy_occt_version(cls, data):
        if (
            isinstance(data, dict)
            and "occt_version" in data
            and "component_versions" not in data
        ):
            data = dict(data)
            data["component_versions"] = {"occt": data.pop("occt_version")}
        return data


class DerivativeCore(_FrozenModel):
    """Shared identity/integrity core of every derivative record."""

    derivative_id: EntityId
    raw_record_id: RecordId
    payload_reference: Sha256Checksum
    checksum: Sha256Checksum
    generator: ExtractorIdentity
    environment: ExtractionEnvironment


class GltfDerivativeRecord(DerivativeCore):
    kind: Literal["visualization_gltf"] = "visualization_gltf"
    media_type: Literal["model/gltf-binary"]
    tessellation: TessellationParameters
    coordinate_conversion: CoordinateConversion
    node_map: dict[str, EntityId] = Field(default_factory=dict)

    @field_validator("node_map")
    @classmethod
    def _keys_are_gltf_node_indices(cls, value: dict[str, str]) -> dict[str, str]:
        for key in value:
            if not key.isdigit():
                raise ValueError(
                    f"node_map key {key!r} must be a glTF node index; node "
                    "names are not identity"
                )
        return value


class PageRenderDerivativeRecord(DerivativeCore):
    kind: Literal["page_render_png"] = "page_render_png"
    media_type: Literal["image/png"]
    page_index: int = Field(ge=0)
    dpi: int = Field(gt=0)
    colorspace: str
    pixel_width: int = Field(gt=0)
    pixel_height: int = Field(gt=0)


# DS-002-era name, kept as an alias for readability in STEP code paths.
DerivativeRecord = GltfDerivativeRecord


class StepExtractionManifest(_FrozenModel):
    raw_record_id: RecordId
    extractor: ExtractorIdentity
    declared_schemas: list[str]
    unit_contexts: list[UnitContext]
    definitions: list[PartDefinition]
    instances: list[ComponentInstance]
    root_instance_ids: list[EntityId]
    derivatives: list[GltfDerivativeRecord] = Field(default_factory=list)
    levels_supported: list[int]
    levels_achieved: list[int]
    unsupported_features: list[str] = Field(default_factory=list)
    lossy_conversions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _achieved_subset_of_supported(self) -> "StepExtractionManifest":
        extra = set(self.levels_achieved) - set(self.levels_supported)
        if extra:
            raise ValueError(
                f"levels_achieved {sorted(extra)} exceed levels_supported; an "
                "extractor may not claim levels it does not support"
            )
        return self
