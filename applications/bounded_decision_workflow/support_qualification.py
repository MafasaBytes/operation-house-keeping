"""Slice 3: qualification of supplied support into outcome cells.

This module deliberately stops at qualified support.  It does not discover
predictions, adjudicate conflicts, rank procedures, or prune nominations.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SupportCell:
    outcome: str
    relation: str
    reasons: tuple[str, ...]
    source_ids: tuple[str, ...]


class SupportQualificationError(ValueError):
    def __init__(self, code, target):
        super().__init__(code)
        self.code = code
        self.target = target


def _same_ref(left, right):
    return (isinstance(left, dict) and isinstance(right, dict)
            and left.get("kind") == right.get("kind")
            and left.get("sha256") == right.get("sha256"))


def qualify_supplied_support(rows, *, hypothesis, procedure, context,
                             decoder, evidence, outcomes):
    """Return every outcome cell, retaining gaps, exclusions and conflicts.

    A positive permit never infers the complement.  Exclusions require an
    explicitly exclusion-qualified row.  Rows with stale semantic references
    are rejected before any cell is produced.
    """
    cells = {outcome: [] for outcome in outcomes}
    for row in rows:
        if not _same_ref(row.get("hypothesis"), hypothesis):
            raise SupportQualificationError("SUPPORT_SUBJECT_MISMATCH", "hypothesis")
        if not _same_ref(row.get("procedure"), procedure):
            raise SupportQualificationError("SUPPORT_SUBJECT_MISMATCH", "procedure")
        if row.get("context") != context:
            raise SupportQualificationError("SUPPORT_CONTEXT_MISMATCH", "context")
        if not _same_ref(row.get("decoder"), decoder):
            raise SupportQualificationError("SUPPORT_DECODER_MISMATCH", "decoder")
        if not _same_ref(row.get("evidence"), evidence):
            raise SupportQualificationError("SUPPORT_EVIDENCE_MISMATCH", "evidence")
        if row.get("qualification", {}).get("status") == "unavailable":
            for outcome in outcomes:
                cells[outcome].append(("unavailable", "support_unavailable", row["id"]))
            continue
        for outcome in row.get("permits", ()):
            if outcome in cells:
                cells[outcome].append(("supports", "positive_support", row["id"]))
        for outcome in row.get("excludes", ()):
            if outcome not in cells:
                continue
            if row.get("coverage") != "explicit_exclusions" or not row.get("exclusion_basis"):
                cells[outcome].append(("unknown", "unsupported_exclusion", row["id"]))
            else:
                cells[outcome].append(("excludes", "qualified_exclusion", row["id"]))

    result = []
    for outcome in outcomes:
        entries = cells[outcome]
        ids = tuple(sorted({entry[2] for entry in entries}))
        relations = {entry[0] for entry in entries}
        if not entries:
            result.append(SupportCell(outcome, "unavailable", ("support_missing",), ()))
        elif "unavailable" in relations or ("supports" in relations and "excludes" in relations):
            result.append(SupportCell(outcome, "unknown", ("support_conflict_or_gap",), ids))
        elif "unknown" in relations:
            result.append(SupportCell(outcome, "unknown", ("unsupported_exclusion",), ids))
        elif "supports" in relations:
            result.append(SupportCell(outcome, "supports", ("positive_support",), ids))
        else:
            result.append(SupportCell(outcome, "excludes", ("qualified_exclusion",), ids))
    return tuple(result)
