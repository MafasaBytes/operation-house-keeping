"""Format-aware CSV extraction.

Decodes CSV structure into traceable cells without deciding engineering
meaning: values stay strings, the header row is explicit configuration, and
lossy or surprising structure becomes warnings — never silent repair.
"""

import csv
import io

from pydantic import BaseModel, ConfigDict, Field

from backend.data_sources.contracts import (
    ExtractedCell,
    ExtractedRow,
    ExtractedTable,
    ExtractionError,
)


class CsvExtractionConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    encoding: str = "utf-8"
    delimiter: str = ","
    header_row_index: int = Field(default=0, ge=0)


def extract_csv(
    payload: bytes, raw_record_id: str, config: CsvExtractionConfig
) -> ExtractedTable:
    try:
        text = payload.decode(config.encoding)
    except UnicodeDecodeError as error:
        raise ExtractionError(
            "EXTRACT_UNDECODABLE",
            f"payload is not decodable as {config.encoding}",
        ) from error

    physical_rows = list(csv.reader(io.StringIO(text), delimiter=config.delimiter))
    if len(physical_rows) <= config.header_row_index:
        raise ExtractionError(
            "EXTRACT_NO_HEADER_ROW",
            f"configured header_row_index {config.header_row_index} but payload "
            f"has only {len(physical_rows)} row(s)",
        )

    warnings: list[str] = []
    columns = [name.strip() for name in physical_rows[config.header_row_index]]
    if len(set(columns)) != len(columns):
        warnings.append("duplicate header names present; column_name is ambiguous")
    for skipped_index in range(config.header_row_index):
        warnings.append(
            f"physical row {skipped_index} precedes the configured header row "
            "and was not extracted as data"
        )

    rows: list[ExtractedRow] = []
    for physical_index, fields in enumerate(physical_rows):
        if physical_index <= config.header_row_index:
            continue
        if len(fields) != len(columns):
            warnings.append(
                f"ragged row at physical row {physical_index}: expected "
                f"{len(columns)} fields, found {len(fields)}"
            )
        cells = [
            ExtractedCell(
                raw_record_id=raw_record_id,
                physical_row_index=physical_index,
                column_index=column_index,
                column_name=(
                    columns[column_index]
                    if column_index < len(columns)
                    else f"__column_{column_index}__"
                ),
                # Empty field ⇒ None: "absent" is not the same as "empty string",
                # and CSV cannot distinguish them; we record the safer state.
                value=field if field != "" else None,
            )
            for column_index, field in enumerate(fields)
        ]
        rows.append(ExtractedRow(physical_row_index=physical_index, cells=cells))

    return ExtractedTable(
        raw_record_id=raw_record_id,
        header_row_index=config.header_row_index,
        columns=columns,
        rows=rows,
        warnings=warnings,
    )
