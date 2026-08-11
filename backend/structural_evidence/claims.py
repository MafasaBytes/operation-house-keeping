"""SN-001 claim derivation.

A claim set is a pure, replayable function of a PERSISTED extraction
result plus the payload checksum — never of the source file, which may be
gone. Deriving claims decides no engineering meaning: which columns carry
structural roles is a caller-supplied DECLARATION (`CsvStructuralReading`,
by column index), disclosed in the output, never inferred from a name.

The BOM `parent` column resolves WITHIN-SOURCE only — a source-native
structural reading, never a cross-source join. A lexeme matching zero or
multiple rows yields an `UnresolvedParentReference`, never a guess.
"""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.data_sources.contracts import ExtractionResult
from backend.data_sources.provenance import derive_record_id
from backend.structural_evidence.contracts import (
    EngineeringContext,
    QuantityFieldRef,
    SourceContainmentClaim,
    SourceNativeField,
    SourceStructuralClaim,
    SourceStructuralClaimSet,
    UnresolvedParentReference,
)
from backend.structural_evidence.errors import StructuralEvidenceError
from backend.structural_evidence.locators import (
    CsvCellLocator,
    CsvRowLocator,
    StructuralAddress,
    StructuralSourceRef,
)


class CsvStructuralReading(BaseModel):
    """Caller-declared reading of which columns carry structural roles —
    a declaration, never an inference, and always by column index."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    quantity_column_index: int | None = Field(default=None, ge=0)
    parent_column_index: int | None = Field(default=None, ge=0)
    parent_matches_column_index: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _parent_columns_travel_together(self):
        if (self.parent_column_index is None) != (
                self.parent_matches_column_index is None):
            raise ValueError(
                "parent_column_index and parent_matches_column_index must "
                "be declared together")
        return self


def csv_structural_claims(
    extraction: ExtractionResult,
    *,
    source_id: str,
    payload_checksum: str,
    engineering_context: EngineeringContext,
    reading: CsvStructuralReading,
) -> SourceStructuralClaimSet:
    try:
        table = extraction.table_view()
    except ValueError as error:
        raise StructuralEvidenceError(
            "SN_EXTRACTION_KIND_UNSUPPORTED",
            "csv claim derivation requires a csv_table extraction result",
        ) from error
    if table.raw_record_id != extraction.raw_record_id:
        raise StructuralEvidenceError(
            "SN_EXTRACTION_MISMATCH",
            "extraction result and table disagree on the raw record")
    # For file sources raw_record_id = derive_record_id(source_id,
    # checksum, 0), so the caller's checksum is verifiable without the
    # payload bytes: a wrong checksum cannot silently re-point a claim.
    if derive_record_id(source_id, payload_checksum, 0) != \
            extraction.raw_record_id:
        raise StructuralEvidenceError(
            "SN_EXTRACTION_MISMATCH",
            "payload checksum and source id do not derive the extraction's "
            "raw record id")

    column_count = len(table.columns)
    for name, index in (("quantity", reading.quantity_column_index),
                        ("parent", reading.parent_column_index),
                        ("parent-matches",
                         reading.parent_matches_column_index)):
        if index is not None and index >= column_count:
            raise StructuralEvidenceError(
                "SN_READING_COLUMN_ABSENT",
                f"declared {name} column index {index} exceeds the "
                f"extracted column count {column_count}")

    source_ref = StructuralSourceRef(
        source_id=source_id, raw_record_id=extraction.raw_record_id,
        payload_checksum=payload_checksum, extractor=extraction.extractor)

    def row_address(row_index: int) -> StructuralAddress:
        return StructuralAddress(
            source=source_ref,
            locator=CsvRowLocator(kind="csv_row",
                                  physical_row_index=row_index))

    def cell_field(cell) -> SourceNativeField:
        return SourceNativeField(
            field_name_as_extracted=cell.column_name, lexeme=cell.value,
            address=StructuralAddress(
                source=source_ref,
                locator=CsvCellLocator(
                    kind="csv_cell",
                    physical_row_index=cell.physical_row_index,
                    column_index=cell.column_index,
                    column_name_as_extracted=cell.column_name)))

    ordered_rows = sorted(table.rows, key=lambda r: r.physical_row_index)
    lexeme_by_row: dict[int, dict[int, str | None]] = {
        row.physical_row_index: {cell.column_index: cell.value
                                 for cell in row.cells}
        for row in ordered_rows}
    subject_claims = tuple(
        SourceStructuralClaim(
            claim_kind="bom_row",
            address=row_address(row.physical_row_index),
            fields=tuple(sorted(
                (cell_field(cell) for cell in row.cells),
                key=lambda f: (f.field_name_as_extracted,
                               f.address.locator.column_index))))
        for row in ordered_rows)

    containment_claims: tuple[SourceContainmentClaim, ...] = ()
    unresolved: tuple[UnresolvedParentReference, ...] = ()
    if reading.parent_column_index is not None:
        match_index = reading.parent_matches_column_index
        keyed = tuple((cells.get(match_index), row_index)
                      for row_index, cells in sorted(lexeme_by_row.items()))
        rows_by_key = {key: tuple(ri for k, ri in keyed if k == key)
                       for key, _ in keyed if key}
        lookups = tuple(
            (row_index, parent_lexeme,
             rows_by_key.get(parent_lexeme, ()))
            for row_index in sorted(lexeme_by_row)
            for parent_lexeme in
            (lexeme_by_row[row_index].get(reading.parent_column_index),)
            if parent_lexeme)  # a root row: no claim, nothing unresolved
        containment_claims = tuple(
            SourceContainmentClaim(
                claim_kind="bom_parent_column",
                child=row_address(row_index),
                parent=row_address(matches[0]))
            for row_index, _, matches in lookups if len(matches) == 1)
        unresolved = tuple(
            UnresolvedParentReference(
                child=row_address(row_index), parent_lexeme=parent_lexeme,
                reason=("no_matching_row" if not matches
                        else "multiple_matching_rows"))
            for row_index, parent_lexeme, matches in lookups
            if len(matches) != 1)

    quantity_field = None
    if reading.quantity_column_index is not None:
        quantity_field = QuantityFieldRef(
            column_index=reading.quantity_column_index,
            column_name_as_extracted=table.columns[
                reading.quantity_column_index])

    return SourceStructuralClaimSet(
        source_ref=source_ref,
        engineering_context=engineering_context,
        subject_claims=subject_claims,
        containment_claims=containment_claims,
        quantity_field=quantity_field,
        unresolved_parent_references=unresolved,
        extraction_outcome=extraction.outcome,
        extraction_warnings=tuple(extraction.warnings),
    )
