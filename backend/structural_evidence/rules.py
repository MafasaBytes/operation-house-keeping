"""SN-001 subject-identity rules, fingerprints, and the sx1 namespace.

A rule is an immutable, inspectable, authority-adoptable READING
CONVENTION. It decides which source-native token names a subject; it
NEVER decides canonical identity (CLAUDE.md assigns exactly this decision
to this layer). The rule splits into a fingerprinted `body` — the
complete generation program, the only thing `apply_rule` can see by
signature — and non-fingerprinted disclosure (`statement`, `stability`).

The K1 contract: changes to rule data are content-addressed and
necessarily create a new subject namespace. Changes to this shared
interpreter or the subject encoder are guarded by the versioned algorithm
contract (`sx1` / `semantics_version`), hand-authored behaviour vectors,
and implementation-drift tests; this is enforced by tests and review, not
by construction alone.

`sx1` versions the COMPLETE subject-generation semantics: namespace
grammar, `apply_rule`, missing-value behaviour, field selection,
comparisons, subject-value encoding, percent encoding, and the
normalization policy — which is none. Any behaviour change to those
mechanics requires `sx2` or later: a new identity domain requiring
explicit new mappings.
"""

import hashlib
import json
import re
from types import MappingProxyType
from typing import Annotated, Literal, Mapping, Union
from urllib.parse import quote

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.data_sources.contracts.identity import ExtractorIdentity
from backend.structural_evidence.contracts import (
    SourceStructuralClaim,
    StructuralClaimKind,
)
from backend.structural_evidence.errors import StructuralEvidenceError
from backend.structural_evidence.locators import (
    CsvRowLocator,
    StepDefinitionLocator,
    StepUsageLocator,
    StructuralAddress,
)
from backend.temporal_state.contracts import SourceSubjectRef

_NAMESPACE_MAX = 256
_SUBJECT_IDENTIFIER_MAX = 512


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# ------------------------------------------------------- fingerprinted body
class CsvColumnLexemeRuleBody(_Frozen):
    rule_kind: Literal["csv_column_lexeme"]
    semantics_version: Literal["v1"]  # bumping this rewrites every fingerprint
    column_name_as_extracted: str = Field(min_length=1, max_length=128)
    name_match: Literal["exact_as_extracted"]
    empty_lexeme_outcome: Literal["no_subject_identity"]


class CsvPhysicalRowRuleBody(_Frozen):
    rule_kind: Literal["csv_physical_row"]
    semantics_version: Literal["v1"]
    include_payload_checksum: Literal[True]


class StepPathRuleBody(_Frozen):
    rule_kind: Literal["step_extractor_path"]
    semantics_version: Literal["v1"]
    path_source: Literal["extractor_path_id"]


SubjectIdentityRuleBody = Annotated[
    Union[CsvColumnLexemeRuleBody, CsvPhysicalRowRuleBody, StepPathRuleBody],
    Field(discriminator="rule_kind"),
]


# `applies_to` is a validated MIRROR of the fingerprinted body, never
# independent state: the body's rule kind alone decides which claims the
# rule generates over, so a rule whose applies_to departed from this
# table would change generation behaviour without changing its
# fingerprint (owner audit 2026-08-12, defect 3). Only `statement` and
# `stability` are non-generation disclosure.
_APPLIES_TO_BY_RULE_KIND: Mapping[str, tuple] = MappingProxyType({
    "csv_column_lexeme": ("bom_row",),
    "csv_physical_row": ("bom_row",),
    "step_extractor_path": ("step_part_definition", "step_nauo_usage"),
})


class SubjectIdentityRule(_Frozen):
    """`body` is the complete generation program. `statement` and
    `stability` are disclosure and are NOT fingerprinted — and cannot
    affect generation, because `apply_rule` takes the body, not the
    rule. `applies_to` is a validated mirror derived from the body's
    rule kind: additions, removals, substitutions, and reordering are
    rejected, so it cannot vary independently of the fingerprint."""

    rule_id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,47}$")
    applies_to: tuple[StructuralClaimKind, ...] = Field(min_length=1)
    body: SubjectIdentityRuleBody
    statement: str = Field(min_length=1, max_length=1024)  # NOT fingerprinted
    stability: Literal["source_native_key", "payload_pinned",
                       "toolchain_relative"]               # NOT fingerprinted

    @model_validator(mode="after")
    def _applies_to_mirrors_the_body(self):
        expected = _APPLIES_TO_BY_RULE_KIND[self.body.rule_kind]
        if self.applies_to != expected:
            raise ValueError(
                f"applies_to must be exactly {expected} for rule kind "
                f"{self.body.rule_kind}: it mirrors the fingerprinted "
                "body and cannot vary independently")
        return self

    @property
    def fingerprint(self) -> str:
        return rule_fingerprint(self.body)


def rule_fingerprint(body: SubjectIdentityRuleBody) -> str:
    """sha256 over the full canonical serialization of the body, first 16
    hex. Canonicalization restates model_kernel's (sort_keys, compact
    separators, utf-8) — restated, never imported: `model_kernel.canonical`
    is deliberately unexported."""
    material = json.dumps(body.model_dump(mode="python"), sort_keys=True,
                          separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def apply_rule(body: SubjectIdentityRuleBody,
               claim: SourceStructuralClaim) -> str | None:
    """Total. Returns the source-native subject VALUE, or None meaning
    "this claim has no subject identity under this rule" — a first-class
    outcome, never a fallback and never an empty string. Reads exactly
    the body's fields (pinned by AST test R4)."""
    if body.rule_kind == "csv_column_lexeme":
        if body.semantics_version != "v1":  # pragma: no cover - Literal
            raise StructuralEvidenceError("SN_RULE_SEMANTICS_UNKNOWN",
                                          "unknown semantics version")
        if body.name_match != "exact_as_extracted":  # pragma: no cover
            raise StructuralEvidenceError("SN_RULE_SEMANTICS_UNKNOWN",
                                          "unknown name-match mode")
        for field in claim.fields:
            if field.field_name_as_extracted == body.column_name_as_extracted:
                if field.lexeme is None or field.lexeme == "":
                    # empty_lexeme_outcome == "no_subject_identity"
                    if body.empty_lexeme_outcome != "no_subject_identity":
                        raise StructuralEvidenceError(  # pragma: no cover
                            "SN_RULE_SEMANTICS_UNKNOWN",
                            "unknown empty-lexeme outcome")
                    return None
                return field.lexeme
        return None
    if body.rule_kind == "csv_physical_row":
        if body.semantics_version != "v1":  # pragma: no cover - Literal
            raise StructuralEvidenceError("SN_RULE_SEMANTICS_UNKNOWN",
                                          "unknown semantics version")
        locator = claim.address.locator
        if not isinstance(locator, CsvRowLocator):
            return None
        if not body.include_payload_checksum:  # pragma: no cover - Literal
            raise StructuralEvidenceError("SN_RULE_SEMANTICS_UNKNOWN",
                                          "checksum inclusion is mandatory")
        source = claim.address.source
        return (f"{source.payload_checksum};"
                f"{source.extractor.config_fingerprint};"
                f"r={locator.physical_row_index}")
    if body.rule_kind == "step_extractor_path":
        if body.semantics_version != "v1":  # pragma: no cover - Literal
            raise StructuralEvidenceError("SN_RULE_SEMANTICS_UNKNOWN",
                                          "unknown semantics version")
        if body.path_source != "extractor_path_id":  # pragma: no cover
            raise StructuralEvidenceError("SN_RULE_SEMANTICS_UNKNOWN",
                                          "unknown path source")
        locator = claim.address.locator
        if isinstance(locator, (StepDefinitionLocator, StepUsageLocator)):
            return locator.extractor_path_id
        return None
    raise StructuralEvidenceError(  # pragma: no cover - union is closed
        "SN_RULE_KIND_UNKNOWN", "unknown rule kind")


# ---------------------------------------------------------- rules shipped
SUBJECT_RULES: Mapping[str, SubjectIdentityRule] = MappingProxyType({
    "bom-item-no-v1": SubjectIdentityRule(
        rule_id="bom-item-no-v1", applies_to=("bom_row",),
        body=CsvColumnLexemeRuleBody(
            rule_kind="csv_column_lexeme", semantics_version="v1",
            column_name_as_extracted="item_no",
            name_match="exact_as_extracted",
            empty_lexeme_outcome="no_subject_identity"),
        statement=(
            "Subject identity is the exact lexeme of the cell in the column "
            "whose name, as exposed by the accepted CSV extractor after its "
            "documented header processing, is literally item_no; an absent "
            "field, absent lexeme, or empty lexeme means the row has no "
            "subject identity — a first-class outcome, never a fallback."),
        stability="source_native_key"),
    "bom-physical-row-v1": SubjectIdentityRule(
        rule_id="bom-physical-row-v1", applies_to=("bom_row",),
        body=CsvPhysicalRowRuleBody(
            rule_kind="csv_physical_row", semantics_version="v1",
            include_payload_checksum=True),
        statement=(
            "Subject identity is the payload checksum plus the extractor "
            "configuration fingerprint plus the physical row index — valid "
            "for exactly these bytes under exactly this extraction "
            "configuration and no others."),
        stability="payload_pinned"),
    "step-ocaf-entry-v1": SubjectIdentityRule(
        rule_id="step-ocaf-entry-v1",
        applies_to=("step_part_definition", "step_nauo_usage"),
        body=StepPathRuleBody(
            rule_kind="step_extractor_path", semantics_version="v1",
            path_source="extractor_path_id"),
        statement=(
            "Subject identity is the extractor's OCAF label entry verbatim; "
            "the entry is meaningful only relative to the extractor "
            "identity, which the namespace carries (name, version, config "
            "fingerprint, toolchain fingerprint). A toolchain change is a "
            "new identity domain, never a silent reinterpretation."),
        stability="toolchain_relative"),
})


# ------------------------------------------------------------ sx1 namespace
_NAMESPACE_PATTERNS = (
    ("scheme", r"sx1"),
    ("family", r"csv|step"),
    ("extractor_name", r"[a-z][a-z0-9_]{0,63}"),
    ("extractor_version", r"[0-9A-Za-z][0-9A-Za-z._+-]{0,31}"),
    ("config_fingerprint", r"[0-9a-f]{16,64}"),
    ("toolchain_fingerprint", r"[0-9a-f]{16}"),
    ("rule_id", r"[a-z][a-z0-9-]{0,47}"),
    ("rule_fingerprint", r"[0-9a-f]{16}"),
)


def toolchain_fingerprint(extractor: ExtractorIdentity) -> str:
    """sha256 over the exact toolchain lexeme, first 16 hex. STEP OCAF
    paths exist only relative to a toolchain; carrying the fingerprint in
    the namespace makes a toolchain change a different identity domain
    instead of a silently re-pointed mapping."""
    return hashlib.sha256(
        extractor.toolchain.encode("utf-8")).hexdigest()[:16]


class ParsedStructuralNamespace(_Frozen):
    scheme: str
    family: str
    extractor_name: str
    extractor_version: str
    config_fingerprint: str
    toolchain_fingerprint: str
    rule_id: str
    rule_fingerprint: str


def structural_namespace(family: Literal["csv", "step"],
                         extractor: ExtractorIdentity,
                         rule: SubjectIdentityRule) -> str:
    """Eight separator-free components joined by `:`. Escaping: none and
    none permitted — every component alphabet excludes `:`, so injectivity
    is a property of the alphabets, not of a decoder."""
    parts = ("sx1", family, extractor.name, extractor.version,
             extractor.config_fingerprint, toolchain_fingerprint(extractor),
             rule.rule_id, rule.fingerprint)
    for (name, pattern), part in zip(_NAMESPACE_PATTERNS, parts):
        if not re.fullmatch(pattern, part):
            raise StructuralEvidenceError(
                "SN_NAMESPACE_INVALID",
                f"namespace component {name} violates its grammar")
    value = ":".join(parts)
    if len(value) > _NAMESPACE_MAX:
        raise StructuralEvidenceError(
            "SN_NAMESPACE_TOO_LONG",
            f"namespace exceeds {_NAMESPACE_MAX} characters")
    return value


def parse_structural_namespace(value: str) -> ParsedStructuralNamespace:
    parts = value.split(":")
    if len(parts) != len(_NAMESPACE_PATTERNS):
        raise StructuralEvidenceError(
            "SN_NAMESPACE_INVALID",
            f"expected {len(_NAMESPACE_PATTERNS)} colon-separated "
            f"components, found {len(parts)}")
    fields = {}
    for (name, pattern), part in zip(_NAMESPACE_PATTERNS, parts):
        if not re.fullmatch(pattern, part):
            raise StructuralEvidenceError(
                "SN_NAMESPACE_INVALID",
                f"namespace component {name} violates its grammar")
        fields[name] = part
    return ParsedStructuralNamespace(**fields)


def _family(address: StructuralAddress) -> Literal["csv", "step"]:
    if isinstance(address.locator, (StepDefinitionLocator, StepUsageLocator)):
        return "step"
    return "csv"


def to_source_subject_ref(address: StructuralAddress,
                          rule: SubjectIdentityRule,
                          value: str) -> SourceSubjectRef:
    """`source_id` is carried verbatim and participates in identity: a
    structural mapping is scoped to one source id (limitation 16). A rule
    that yielded None produces NO SourceSubjectRef at all — this builder
    refuses None rather than inventing a placeholder."""
    if value is None:
        raise StructuralEvidenceError(
            "SN_NO_SUBJECT_IDENTITY",
            "a rule that yielded no subject identity produces no subject")
    identifier = quote(value, safe="")
    if len(identifier) > _SUBJECT_IDENTIFIER_MAX:
        raise StructuralEvidenceError(
            "SN_SUBJECT_IDENTIFIER_TOO_LONG",
            f"encoded subject identifier exceeds "
            f"{_SUBJECT_IDENTIFIER_MAX} characters")
    return SourceSubjectRef(
        source_id=address.source.source_id,
        adapter_id=structural_namespace(_family(address),
                                        address.source.extractor, rule),
        subject_identifier=identifier)
