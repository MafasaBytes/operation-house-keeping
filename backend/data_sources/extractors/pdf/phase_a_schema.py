"""Versioned internal contract for the Phase A structural result.

The worker emits this shape as ``manifest_a.json``; the parent validates
the completion checkpoint FIRST (binding checksum + identity) and then
validates the manifest against this contract before Phase B may start.
``extra="forbid"`` everywhere: a checksum-correct but structurally alien
manifest is rejected, mapped to EXTRACT_PDF_CHECKPOINT_INVALID.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PhaseAEncryption(_Strict):
    present: bool
    method: str | None
    authentication_outcome: Literal[
        "not_required", "empty_password_ok", "password_required"
    ]


class PhaseAMetadata(_Strict):
    declared_title: str | None
    declared_author: str | None
    declared_subject: str | None
    declared_producer: str | None
    declared_creator: str | None
    declared_creation_date_raw: str | None
    declared_mod_date_raw: str | None
    pdf_version: str | None
    page_label_spec_present: bool
    encryption: PhaseAEncryption


class PhaseACatalog(_Strict):
    javascript_count: int = Field(ge=0)
    embedded_file_names: list[str | None]
    ocg_names: list[str | None]
    open_action_present: bool = False
    additional_actions_present: bool = False


class PhaseAWord(_Strict):
    text: str
    x0: float
    top: float
    x1: float
    bottom: float
    fontname: str | None
    size: float | None
    upright: bool


class PhaseAImage(_Strict):
    x0: float
    top: float
    x1: float
    bottom: float
    srcwidth: int | None
    srcheight: int | None
    colorspace: str | None
    filters: list[str]


class PhaseAAnnotation(_Strict):
    subtype: str
    rect: list[float] = Field(min_length=4, max_length=4)
    contents: str | None
    uri: str | None


class PhaseATableCell(_Strict):
    row: int = Field(ge=0)
    col: int = Field(ge=0)
    bbox: list[float] = Field(min_length=4, max_length=4)


class PhaseATable(_Strict):
    bbox: list[float] = Field(min_length=4, max_length=4)
    rows_n: int = Field(ge=0)
    cols_n: int = Field(ge=0)
    cells: list[PhaseATableCell]


class PhaseAPage(_Strict):
    page_index: int = Field(ge=0)
    page_label: str | None
    displayed_width: float = Field(gt=0)
    displayed_height: float = Field(gt=0)
    mediabox_raw: list[float] = Field(min_length=4, max_length=4)
    cropbox_raw: list[float] = Field(min_length=4, max_length=4)
    crop_declared: bool
    rotation_raw: Literal[0, 90, 180, 270]
    words: list[PhaseAWord]
    lines_n: int = Field(ge=0)
    rects_n: int = Field(ge=0)
    curves_n: int = Field(ge=0)
    ink_bbox: list[float] | None = Field(default=None, min_length=4, max_length=4)
    images: list[PhaseAImage]
    annotations: list[PhaseAAnnotation]
    tables: list[PhaseATable]
    char_count: int = Field(ge=0)


class PhaseACounts(_Strict):
    total_chars: int = Field(ge=0)
    layout_objects: int = Field(ge=0)


class PhaseAResult(_Strict):
    phase_a_schema_version: Literal[1]
    raw_record_id: str
    extractor_name: str
    extractor_version: str
    config_fingerprint: str
    toolchain: dict[str, str]
    metadata: PhaseAMetadata
    catalog: PhaseACatalog
    pages: list[PhaseAPage]
    counts: PhaseACounts
