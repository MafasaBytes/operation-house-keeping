"""SN-001 payload-pinned structural locators.

A `StructuralAddress` is an evidence ADDRESS — "row 3 of these bytes",
"this OCAF entry of this extraction" — never an identity and never a
subject. `SourceSubjectRef` remains the only subject identity, produced
separately by the subject-identity rules. `ExtractorIdentity` is EMBEDDED,
not named: the extractor configuration decides which rows become data and
how the payload is segmented, and is captured only in its fingerprint.

`upstream_definition_id` / `upstream_instance_id` are extractor-local
identifiers (`derive_entity_id` output), never canonical system entity
anchors; they are carried as recorded cross-checks verified on read.
"""

import hashlib
from typing import Annotated, Literal, Union
from urllib.parse import quote, unquote

from pydantic import BaseModel, ConfigDict, Field

from backend.data_sources.contracts.identity import ExtractorIdentity
from backend.model_kernel import StructuralSourceLocatorEvidence
from backend.structural_evidence.errors import StructuralEvidenceError

# The load-bearing bound is on the CANONICAL value (percent-encoding
# expands up to 3x); the per-field 1024 cap is only a cheap early guard.
_CANONICAL_VALUE_MAX = 510
_PATH_MAX = 1024


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class StructuralSourceRef(_Frozen):
    """The exact payload a claim was read from, checksum-pinned."""

    source_id: str = Field(min_length=1)
    raw_record_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    payload_checksum: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    extractor: ExtractorIdentity


class CsvRowLocator(_Frozen):
    kind: Literal["csv_row"]
    physical_row_index: int = Field(ge=0)


class CsvCellLocator(_Frozen):
    """`column_index` is IDENTITY; `column_name_as_extracted` is
    disclosure only — the accepted extractor warns on duplicate headers
    and synthesizes names for ragged overflow, so a name is not
    injective."""

    kind: Literal["csv_cell"]
    physical_row_index: int = Field(ge=0)
    column_index: int = Field(ge=0)
    column_name_as_extracted: str


class StepDefinitionLocator(_Frozen):
    kind: Literal["step_part_definition"]
    extractor_path_id: str = Field(min_length=1, max_length=_PATH_MAX)
    upstream_definition_id: str = Field(pattern=r"^[0-9a-f]{32}$")


class StepUsageLocator(_Frozen):
    """`parent_definition_path_id is None` means exactly "the synthesized
    root usage has no parent"; an empty string is rejected so None and ""
    can never share a canonical value."""

    kind: Literal["step_nauo_usage"]
    extractor_path_id: str = Field(min_length=1, max_length=_PATH_MAX)
    upstream_instance_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    definition_path_id: str = Field(min_length=1, max_length=_PATH_MAX)
    parent_definition_path_id: str | None = Field(
        default=None, min_length=1, max_length=_PATH_MAX)


StructuralLocator = Annotated[
    Union[CsvRowLocator, CsvCellLocator, StepDefinitionLocator,
          StepUsageLocator],
    Field(discriminator="kind"),
]


class StructuralAddress(_Frozen):
    source: StructuralSourceRef
    locator: StructuralLocator


def _q(value: str) -> str:
    return quote(value, safe="")


def canonical_locator_value(locator) -> str:
    """Total, injective per scheme, separator-safe. Every value begins
    `r=` or `p=`, so a bare 32-hex id satisfies no scheme. `None` parent
    encodes as the empty `;pp=` tail — a sentinel character cannot be
    used because `quote("-", safe="")` is `"-"`, a valid quoted path.
    Raises SN_LOCATOR_TOO_LONG beyond the canonical bound; a raw pydantic
    error is never the failure mode at the kernel boundary."""
    if isinstance(locator, CsvRowLocator):
        value = f"r={locator.physical_row_index}"
    elif isinstance(locator, CsvCellLocator):
        value = f"r={locator.physical_row_index};c={locator.column_index}"
    elif isinstance(locator, StepDefinitionLocator):
        value = (f"p={_q(locator.extractor_path_id)}"
                 f";d={locator.upstream_definition_id}")
    elif isinstance(locator, StepUsageLocator):
        parent = locator.parent_definition_path_id
        value = (f"p={_q(locator.extractor_path_id)}"
                 f";i={locator.upstream_instance_id}"
                 f";dp={_q(locator.definition_path_id)}"
                 f";pp={_q(parent) if parent is not None else ''}")
    else:  # pragma: no cover - union is closed
        raise StructuralEvidenceError(
            "SN_LOCATOR_SCHEME_UNKNOWN", "unknown locator kind")
    if len(value) > _CANONICAL_VALUE_MAX:
        raise StructuralEvidenceError(
            "SN_LOCATOR_TOO_LONG",
            f"canonical locator value exceeds {_CANONICAL_VALUE_MAX} "
            "characters after percent-encoding")
    return value


def toolchain_fingerprint(extractor: ExtractorIdentity) -> str:
    """sha256 over the exact toolchain lexeme, first 16 hex. STEP OCAF
    paths exist only relative to a toolchain; carrying the fingerprint
    makes a toolchain change a different identity domain instead of a
    silently re-pointed mapping."""
    return hashlib.sha256(
        extractor.toolchain.encode("utf-8")).hexdigest()[:16]


class StructuralEvidenceProjection(_Frozen):
    """The projection of a StructuralAddress into kernel evidence, plus
    the NAMED fields the projection deliberately drops: `source_id` is
    binding knowledge and forbidden in a model record; the toolchain
    PROSE is dropped while its fingerprint is carried. Both are required
    keyword arguments of `from_kernel_evidence`, so the loss is a typed
    obligation, never a silent default."""

    evidence: StructuralSourceLocatorEvidence
    dropped: tuple[Literal["extractor_toolchain", "source_id"], ...]


def to_kernel_evidence(address: StructuralAddress) -> \
        StructuralEvidenceProjection:
    return StructuralEvidenceProjection(
        evidence=StructuralSourceLocatorEvidence(
            kind="structural_source_locator",
            raw_record_id=address.source.raw_record_id,
            payload_checksum=address.source.payload_checksum,
            extractor_name=address.source.extractor.name,
            extractor_version=address.source.extractor.version,
            extractor_config_fingerprint=(
                address.source.extractor.config_fingerprint),
            extractor_toolchain_fingerprint=toolchain_fingerprint(
                address.source.extractor),
            locator_scheme=address.locator.kind,
            locator_value=canonical_locator_value(address.locator)),
        dropped=("extractor_toolchain", "source_id"))


def _parse_fields(value: str, prefixes: tuple[str, ...]) -> tuple[str, ...]:
    parts = value.split(";")
    if len(parts) != len(prefixes) or not all(
            part.startswith(prefix)
            for part, prefix in zip(parts, prefixes)):
        raise StructuralEvidenceError(
            "SN_LOCATOR_VALUE_INVALID",
            "canonical locator value does not match its scheme grammar")
    return tuple(part[len(prefix):]
                 for part, prefix in zip(parts, prefixes))


def from_kernel_evidence(ref: StructuralSourceLocatorEvidence, *,
                         source_id: str,
                         extractor_toolchain: str) -> StructuralAddress:
    """Inverse of `to_kernel_evidence`. Display names are not carried by
    a citation (the canonical value deliberately excludes them), so a
    reconstructed csv_cell locator has an empty disclosure name."""
    if toolchain_fingerprint(ExtractorIdentity(
            name=ref.extractor_name, version=ref.extractor_version,
            toolchain=extractor_toolchain,
            config_fingerprint=ref.extractor_config_fingerprint)) != \
            ref.extractor_toolchain_fingerprint:
        raise StructuralEvidenceError(
            "SN_TOOLCHAIN_FINGERPRINT_MISMATCH",
            "the supplied toolchain prose does not fingerprint to the "
            "cited toolchain — a different identity domain")
    source = StructuralSourceRef(
        source_id=source_id, raw_record_id=ref.raw_record_id,
        payload_checksum=ref.payload_checksum,
        extractor=ExtractorIdentity(
            name=ref.extractor_name, version=ref.extractor_version,
            toolchain=extractor_toolchain,
            config_fingerprint=ref.extractor_config_fingerprint))
    if ref.locator_scheme == "csv_row":
        (row,) = _parse_fields(ref.locator_value, ("r=",))
        locator = CsvRowLocator(kind="csv_row", physical_row_index=int(row))
    elif ref.locator_scheme == "csv_cell":
        row, column = _parse_fields(ref.locator_value, ("r=", "c="))
        locator = CsvCellLocator(kind="csv_cell",
                                 physical_row_index=int(row),
                                 column_index=int(column),
                                 column_name_as_extracted="")
    elif ref.locator_scheme == "step_part_definition":
        path, upstream = _parse_fields(ref.locator_value, ("p=", "d="))
        locator = StepDefinitionLocator(
            kind="step_part_definition", extractor_path_id=unquote(path),
            upstream_definition_id=upstream)
    else:  # step_nauo_usage
        path, upstream, def_path, parent = _parse_fields(
            ref.locator_value, ("p=", "i=", "dp=", "pp="))
        locator = StepUsageLocator(
            kind="step_nauo_usage", extractor_path_id=unquote(path),
            upstream_instance_id=upstream,
            definition_path_id=unquote(def_path),
            parent_definition_path_id=(unquote(parent) if parent else None))
    return StructuralAddress(source=source, locator=locator)
