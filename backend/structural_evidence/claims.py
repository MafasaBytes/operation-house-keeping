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
from backend.data_sources.provenance import derive_entity_id, derive_record_id
from backend.structural_evidence.contracts import (
    DerivedUsagePath,
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
    StepDefinitionLocator,
    StepUsageLocator,
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


def step_structural_claims(
    extraction: ExtractionResult,
    *,
    source_id: str,
    payload_checksum: str,
    engineering_context: EngineeringContext,
) -> SourceStructuralClaimSet:
    """STEP definition/usage claims from a persisted extraction result.

    A usage occurrence is NAUO-shaped: this definition inside that parent
    DEFINITION. Parenthood comes only from `parent_definition_ref` (None
    only for the synthesized root); a flattened per-path tree is SN-001's
    own derivation, labelled, with ambiguity reported rather than picked
    when a parent definition is used more than once. Upstream ids are
    recomputed on read — a manifest whose ids do not re-derive is
    malformation, never a silent wrong binding.
    """
    try:
        manifest = extraction.manifest_view()
    except ValueError as error:
        raise StructuralEvidenceError(
            "SN_EXTRACTION_KIND_UNSUPPORTED",
            "step claim derivation requires a step_manifest extraction "
            "result") from error
    if not hasattr(manifest, "instances"):
        raise StructuralEvidenceError(
            "SN_EXTRACTION_KIND_UNSUPPORTED",
            "step claim derivation requires a step_manifest extraction "
            "result")
    if derive_record_id(source_id, payload_checksum, 0) != \
            extraction.raw_record_id:
        raise StructuralEvidenceError(
            "SN_EXTRACTION_MISMATCH",
            "payload checksum and source id do not derive the extraction's "
            "raw record id")
    version = extraction.extractor.version
    for definition in manifest.definitions:
        if derive_entity_id(extraction.raw_record_id, version,
                            f"def:{definition.extractor_path_id}") != \
                definition.definition_id:
            raise StructuralEvidenceError(
                "SN_EXTRACTION_MISMATCH",
                "a definition id does not re-derive from its path — the "
                "manifest was produced by a different ingestion or "
                "toolchain")

    source_ref = StructuralSourceRef(
        source_id=source_id, raw_record_id=extraction.raw_record_id,
        payload_checksum=payload_checksum, extractor=extraction.extractor)
    path_by_definition_id = {d.definition_id: d.extractor_path_id
                             for d in manifest.definitions}

    def definition_address(definition) -> StructuralAddress:
        return StructuralAddress(
            source=source_ref,
            locator=StepDefinitionLocator(
                kind="step_part_definition",
                extractor_path_id=definition.extractor_path_id,
                upstream_definition_id=definition.definition_id))

    def usage_locator(instance) -> StepUsageLocator:
        return StepUsageLocator(
            kind="step_nauo_usage",
            extractor_path_id=instance.extractor_path_id,
            upstream_instance_id=instance.instance_id,
            definition_path_id=path_by_definition_id[instance.definition_ref],
            parent_definition_path_id=(
                path_by_definition_id[instance.parent_definition_ref]
                if instance.parent_definition_ref is not None else None))

    def name_field(name, address) -> tuple[SourceNativeField, ...]:
        if name is None:
            return ()
        return (SourceNativeField(field_name_as_extracted="name",
                                  lexeme=name, address=address),)

    definition_claims = tuple(
        SourceStructuralClaim(
            claim_kind="step_part_definition",
            address=definition_address(definition),
            fields=name_field(definition.name,
                              definition_address(definition)))
        for definition in sorted(manifest.definitions,
                                 key=lambda d: d.extractor_path_id))

    non_root = tuple(sorted(
        (instance for instance in manifest.instances
         if instance.parent_definition_ref is not None),
        key=lambda i: i.extractor_path_id))
    usage_claims = tuple(
        SourceStructuralClaim(
            claim_kind="step_nauo_usage",
            address=StructuralAddress(source=source_ref,
                                      locator=usage_locator(instance)),
            fields=name_field(
                instance.occurrence_name,
                StructuralAddress(source=source_ref,
                                  locator=usage_locator(instance))))
        for instance in non_root)

    definition_by_id = {d.definition_id: d for d in manifest.definitions}
    containment_claims = tuple(
        SourceContainmentClaim(
            claim_kind="step_nauo_usage_edge",
            child=StructuralAddress(source=source_ref,
                                    locator=usage_locator(instance)),
            parent=definition_address(
                definition_by_id[instance.parent_definition_ref]))
        for instance in non_root)

    uses_of_definition = {
        definition.definition_id: tuple(
            instance for instance in manifest.instances
            if instance.definition_ref == definition.definition_id)
        for definition in manifest.definitions}
    root_definitions = {
        instance.definition_ref for instance in manifest.instances
        if instance.parent_definition_ref is None}

    def derived_path(instance) -> DerivedUsagePath:
        # root-first chain; ambiguous the moment any ancestor definition
        # is used by more than one non-root usage
        chain = (usage_locator(instance),)
        current = instance
        while current.parent_definition_ref not in root_definitions:
            parent_uses = tuple(
                use for use in uses_of_definition[
                    current.parent_definition_ref]
                if use.parent_definition_ref is not None)
            if len(parent_uses) != 1:
                return DerivedUsagePath(
                    derivation="nauo_parent_definition_chain_v1",
                    for_usage=usage_locator(instance),
                    steps=(), ambiguity="multiple_parent_uses")
            current = parent_uses[0]
            chain = (usage_locator(current),) + chain
        return DerivedUsagePath(
            derivation="nauo_parent_definition_chain_v1",
            for_usage=usage_locator(instance),
            steps=chain, ambiguity="unique")

    derived_paths = tuple(derived_path(instance) for instance in non_root)

    return SourceStructuralClaimSet(
        source_ref=source_ref,
        engineering_context=engineering_context,
        subject_claims=definition_claims + usage_claims,
        containment_claims=containment_claims,
        derived_paths=derived_paths,
        quantity_field=None,  # STEP declares no quantity column, ever
        extraction_outcome=extraction.outcome,
        extraction_warnings=tuple(extraction.warnings),
    )
