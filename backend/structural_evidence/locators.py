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

from typing import Annotated, Literal, Union
from urllib.parse import quote

from pydantic import BaseModel, ConfigDict, Field

from backend.data_sources.contracts.identity import ExtractorIdentity
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
