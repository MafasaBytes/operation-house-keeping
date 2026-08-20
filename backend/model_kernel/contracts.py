"""MK-001 model-ledger contracts.

Append-only records of explicit model knowledge over canonical
``system_identity`` anchors, plus result contracts that reject impossible
states. ``recorded_at`` is audit information everywhere — it never selects
winners. Assertions are ACTIVE/inactive; type-definition chain tips are
CURRENT. Registrations have no lifecycle at all: the kernel can never alter
an embedded anchor field, and a mistaken registration has no kernel
correction path.
"""

import re
from datetime import UTC
from decimal import Decimal, InvalidOperation
from typing import Annotated, Literal, Union
from urllib.parse import quote

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictStr,
    model_validator,
)

from backend.model_kernel.canonical import (
    canonical_sort_key,
    compute_revision_id,
    verify_record_id,
)
from backend.system_identity import (
    CONSTRAINT_ANCHOR_ID_PATTERN,
    ENTITY_ANCHOR_ID_PATTERN,
    PORT_ANCHOR_ID_PATTERN,
    VARIABLE_ANCHOR_ID_PATTERN,
    ConstraintAnchor,
    EntityAnchor,
    PortAnchor,
    VariableAnchor,
)

UtcDatetime = Annotated[AwareDatetime, AfterValidator(lambda v: v.astimezone(UTC))]

MODEL_ID_PATTERN = r"^[a-z0-9-]+$"
MODEL_RECORD_ID_PATTERN = r"^(reg|rtd|rel|rwd|vrg|vsp|vsm|crg|vcn|prg|pif|pcn|pcm|ptw)_[0-9a-f]{64}$"

ReferentKind = Literal[
    "logical_instance", "physical_instance", "type_definition", "unknown"
]
LifecycleView = Literal[
    "as_designed", "as_built", "as_configured", "as_operated", "as_maintained"
]


# ---------------------------------------------------------------- errors
# defined in `errors` so `canonical` can raise them without an import cycle
from backend.model_kernel.errors import (  # noqa: E402  (re-export)
    ModelConfigurationError,
    ModelIntegrityError,
    ModelKernelError,
    ModelQueryError,
)


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# ------------------------------------------------------------- authority
class AuthorityRef(_Frozen):
    """A recorded CLAIM of authorship — nothing is authenticated or signed."""

    kind: Literal["human_owner", "test_fixture"]
    agent: str = Field(min_length=1)
    method: Literal["manual_declaration"]


# -------------------------------------------------------------- contexts
class LifecycleViewContext(_Frozen):
    kind: Literal["lifecycle_view"]
    view: LifecycleView


class ViewIndependentContext(_Frozen):
    kind: Literal["view_independent"]


AssertionContext = Annotated[
    Union[LifecycleViewContext, ViewIndependentContext],
    Field(discriminator="kind"),
]


# -------------------------------------------------------------- evidence
class OwnerDeclarationEvidence(_Frozen):
    """The claim's basis is a human decision, honestly labeled as such —
    the only prose-bearing evidence kind."""

    kind: Literal["owner_declaration"]
    statement: str = Field(min_length=1)


class ModelRecordEvidence(_Frozen):
    # registrations (entity AND variable), types, assertions, and constraint
    # records (crg_/vcn_) are citable; a withdrawal is a non-claim and stays
    # uncitable
    kind: Literal["model_record"]
    record_id: str = Field(
        pattern=r"^(reg|rtd|rel|vrg|vsp|vsm|crg|vcn|prg|pif|pcn|pcm)_[0-9a-f]{64}$")


class IdentityBindingRecordEvidence(_Frozen):
    kind: Literal["identity_binding_record"]
    binding_set_id: str = Field(pattern=r"^[a-z0-9-]+$")
    record_id: str = Field(pattern=r"^(anc|iba|ibr|ibc|ibj)_[0-9a-f]{64}$")


class SourceRawRecordEvidence(_Frozen):
    kind: Literal["source_raw_record"]
    raw_record_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    payload_checksum: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class TemporalOccurrenceEvidence(_Frozen):
    kind: Literal["temporal_occurrence"]
    occurrence_id: str = Field(pattern=r"^[0-9a-f]{32}$")


_LOCATOR_INT = r"(?:0|[1-9][0-9]*)"
_LOCATOR_PATH = r"(?:[0-9A-Za-z_.~-]|%[0-9A-F]{2})"
_LOCATOR_VALUE_BY_SCHEME = {
    "csv_row": re.compile(rf"^r={_LOCATOR_INT}$"),
    "csv_cell": re.compile(rf"^r={_LOCATOR_INT};c={_LOCATOR_INT}$"),
    "step_part_definition": re.compile(
        rf"^p=({_LOCATOR_PATH}+);d=[0-9a-f]{{32}}$"),
    "step_nauo_usage": re.compile(
        rf"^p=({_LOCATOR_PATH}+);i=[0-9a-f]{{32}}"
        rf";dp=({_LOCATOR_PATH}+);pp=({_LOCATOR_PATH}*)$"),
}


def _is_canonical_quoted(component: str) -> bool:
    """True exactly when the component is its own quote(decoded,
    safe="") re-encoding under strict UTF-8. Over-encoded unreserved
    characters ("%41" for "A"), non-UTF-8 byte sequences ("%FF"), and
    truncated multi-byte sequences cannot identify an exact source path
    and are refused. The surrounding scheme grammar has already
    guaranteed well-formed "%XX" escapes and the quote() alphabet."""
    data = bytearray()
    index = 0
    while index < len(component):
        if component[index] == "%":
            data.append(int(component[index + 1:index + 3], 16))
            index += 3
        else:
            data.append(ord(component[index]))
            index += 1
    try:
        decoded = bytes(data).decode("utf-8")
    except UnicodeDecodeError:
        return False
    return quote(decoded, safe="") == component


class StructuralSourceLocatorEvidence(_Frozen):
    """An EXACT structural position inside one immutable source payload,
    declared by the authoring authority (SN-001, ADR-0010 decision 10).

    SELF-CONTAINED: every field is a canonical scalar. The kernel imports
    nothing to interpret it, resolves nothing, and verifies nothing about
    it — disclosure is always verification="declared_reference", because
    the kernel structurally cannot import data_sources. This is a
    CITATION, never a locator ledger and never an identity: it names
    where a claim was read, not what the claim is about. It has no
    lifecycle and no applicability, cannot resolve source identity, and
    cannot discover or replace a BindingAssertion. The toolchain
    fingerprint makes a STEP locator exact: an OCAF path exists only
    relative to a toolchain."""

    kind: Literal["structural_source_locator"]
    raw_record_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    payload_checksum: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    extractor_name: str = Field(pattern=r"^[a-z][a-z0-9_]{0,63}$")
    extractor_version: str = Field(
        pattern=r"^[0-9A-Za-z][0-9A-Za-z._+-]{0,31}$")
    extractor_config_fingerprint: str = Field(pattern=r"^[0-9a-f]{16,64}$")
    extractor_toolchain_fingerprint: str = Field(pattern=r"^[0-9a-f]{16}$")
    locator_scheme: Literal["csv_row", "csv_cell",
                            "step_part_definition", "step_nauo_usage"]
    locator_value: str = Field(
        pattern=r"^(?:r=|p=)[0-9A-Za-z._~:@!$&*+,;=%/-]{1,508}$")

    @model_validator(mode="after")
    def _locator_value_matches_its_scheme(self):
        # Each scheme's own canonical grammar, restated here as regular
        # expressions over canonical scalars so the kernel stays
        # self-contained (owner audit 2026-08-12): canonical decimal
        # integers (no sign, no leading zero), 32-hex upstream
        # identifiers, and percent-encoded path components with
        # uppercase escapes exactly as `quote(value, safe="")` emits.
        match = _LOCATOR_VALUE_BY_SCHEME[self.locator_scheme].fullmatch(
            self.locator_value)
        if not match:
            raise ValueError(
                "locator_value does not satisfy the canonical grammar "
                f"of locator_scheme {self.locator_scheme}")
        # Owner follow-up (2026-08-12): every STEP path component (p,
        # dp, and a non-empty pp — the empty pp root sentinel is exempt)
        # must be genuinely canonical, not merely alphabet-conformant.
        for component in match.groups():
            if component and not _is_canonical_quoted(component):
                raise ValueError(
                    "a STEP path component is not the canonical "
                    'quote(value, safe="") encoding of any exact '
                    "source path")
        return self


EvidenceRef = Annotated[
    Union[OwnerDeclarationEvidence, ModelRecordEvidence,
          IdentityBindingRecordEvidence, SourceRawRecordEvidence,
          TemporalOccurrenceEvidence, StructuralSourceLocatorEvidence],
    Field(discriminator="kind"),
]


def _normalized_kinds(value: tuple) -> tuple:
    normalized = tuple(sorted(set(value)))
    if not normalized:
        raise ValueError("at least one referent kind is required")
    return normalized


ReferentKindTuple = Annotated[
    tuple[ReferentKind, ...], AfterValidator(_normalized_kinds)
]


def _canonical_evidence(value: tuple) -> tuple:
    """Evidence order carries no engineering meaning and repeating identical
    evidence adds no support: sort by the FULL canonical serialization of
    each reference (including cited record ids — distinct citations are
    distinct evidence), normalize exact duplicates away. Min-1 applies
    after normalization."""
    by_key = {canonical_sort_key(ref): ref for ref in value}
    normalized = tuple(by_key[key] for key in sorted(by_key))
    if not normalized:
        raise ValueError("at least one evidence reference is required")
    return normalized


# --------------------------------------------------------- ledger records
class EntityRegistration(_Frozen):
    """Membership claim for one already-declared canonical identity. NO
    lifecycle: the kernel provides no supersession, no withdrawal, and no
    path that alters any embedded anchor field."""

    record_kind: Literal["entity_registration"] = "entity_registration"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^reg_[0-9a-f]{64}$")
    anchor: EntityAnchor
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""


class VariableRegistration(_Frozen):
    """Membership claim for one already-declared canonical VARIABLE of a
    registered entity. Ownership is identity (`anchor.entity_anchor_id`),
    never a relationship edge; like entity registrations there is NO
    lifecycle and no kernel correction path. Membership only — no state,
    no units, no datatype, no meaning."""

    record_kind: Literal["variable_registration"] = "variable_registration"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^vrg_[0-9a-f]{64}$")
    anchor: VariableAnchor
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""


class RelationshipTypeDefinition(_Frozen):
    """One member of a type LINEAGE named by its invariant type_name.
    Supersession preserves {type_name, directionality, hierarchy_semantics,
    context_requirement}; changing any of these requires a new type name."""

    record_kind: Literal["relationship_type_definition"] = (
        "relationship_type_definition")
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^rtd_[0-9a-f]{64}$")
    type_name: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    forward_label: str = Field(min_length=1)
    inverse_label: str = Field(min_length=1)
    directionality: Literal["directed"]
    source_referent_kinds: ReferentKindTuple
    target_referent_kinds: ReferentKindTuple
    self_relation_allowed: bool
    hierarchy_semantics: Literal["containment", "none"]
    context_requirement: Literal["lifecycle_view", "view_independent"]
    supersedes: str | None = Field(default=None,
                                   pattern=r"^rtd_[0-9a-f]{64}$")
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""

    @model_validator(mode="after")
    def _containment_never_self_relating(self):
        if self.hierarchy_semantics == "containment" and self.self_relation_allowed:
            raise ValueError(
                "a containment type permitting self-relations is contradictory")
        return self


class RelationshipAssertion(_Frozen):
    """One directed, typed, evidence-backed edge claim, judged by the EXACT
    definition it cites."""

    record_kind: Literal["relationship_assertion"] = "relationship_assertion"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^rel_[0-9a-f]{64}$")
    type_id: str = Field(pattern=r"^rtd_[0-9a-f]{64}$")
    source_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    target_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    context: AssertionContext
    evidence: Annotated[tuple[EvidenceRef, ...],
                        AfterValidator(_canonical_evidence)]
    # correction only: same LINEAGE + source + target + context
    supersedes: str | None = Field(default=None, pattern=r"^rel_[0-9a-f]{64}$")
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""


class RelationshipWithdrawal(_Frozen):
    """"No longer asserted" — never a claim the original was wrong, and
    never a claim about when it stopped being true."""

    record_kind: Literal["relationship_withdrawal"] = "relationship_withdrawal"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^rwd_[0-9a-f]{64}$")
    withdraws: str = Field(pattern=r"^rel_[0-9a-f]{64}$")
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""


# ------------------------------------------------- value specification
_LOCAL_IDENTIFIER = r"^[a-z0-9][a-z0-9._-]*$"
_LOCAL_IDENTIFIER_RE = re.compile(r"[a-z0-9][a-z0-9._-]*")
_LOCAL_IDENTIFIER_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyz0123456789._-")


def _identifier(value: str) -> str:
    r"""Behavioural grammar guard. The `pattern=` constraint is correct
    under pydantic's default engine, but the guarantee must not rest on an
    engine default: `$` admits a trailing newline under Python's `re`, and
    `\A..\Z` is rejected outright by the default engine. fullmatch plus an
    explicit character set is engine-independent."""
    if not isinstance(value, str):
        raise ValueError("identifier must be a string")
    if not _LOCAL_IDENTIFIER_RE.fullmatch(value):
        raise ValueError("identifier grammar violation")
    if not set(value) <= _LOCAL_IDENTIFIER_CHARS:
        raise ValueError("identifier contains a forbidden character")
    return value


LocalIdentifier = Annotated[
    str, Field(min_length=1, max_length=128,
               pattern=_LOCAL_IDENTIFIER),
    AfterValidator(_identifier)]


class UnitReference(_Frozen):
    """An identity TOKEN for a unit, never a unit definition. It asserts no
    dimension, convertibility, scale or offset, SI traceability, or
    equivalence to any external standard. Identity is the exact triple
    (system_id, system_edition, code), compared byte-for-byte."""

    system_id: Literal["project_local"]
    system_edition: LocalIdentifier
    code: LocalIdentifier


class QuantityKindReference(_Frozen):
    """Exact identity token for a quantity kind, never an ontology."""

    system_id: Literal["project_local"]
    system_edition: LocalIdentifier
    code: LocalIdentifier


class ObservationRoleReference(_Frozen):
    """Exact identity token for an observation role, never behaviour."""

    system_id: Literal["project_local"]
    system_edition: LocalIdentifier
    code: LocalIdentifier


class DeclaredUnit(_Frozen):
    kind: Literal["declared"]
    unit: UnitReference


class UnitNotDeclared(_Frozen):
    """The model declares no unit for this variable — an explicit claim,
    distinct from a source that supplied no unit."""

    kind: Literal["not_declared"]


UnitDeclaration = Annotated[
    Union[DeclaredUnit, UnitNotDeclared], Field(discriminator="kind")]


# ------------------------------------------------------ canonical decimal
_CANONICAL_DECIMAL = re.compile(
    r"(?:0|-?(?:0\.[0-9]*[1-9]|[1-9][0-9]*(?:\.[0-9]*[1-9])?))")
_AUTHORING_DECIMAL = re.compile(
    r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")


def _canonical_decimal(value: str) -> str:
    """A plain, exact decimal string. Any accepted string is already
    canonical, so the content-derived record id is deterministic and the
    ``Decimal.normalize()`` exponent trap never arises (no ``0.0``, no
    ``1.230``, no exponent). Bound to 128 digits each side of the point;
    negative zero, leading zeros, a bare point, trailing fractional zeros,
    exponents, and whitespace are refused. Non-string input is refused by
    ``StrictStr`` before this validator runs."""
    if len(value.encode("utf-8")) > 386 or not _CANONICAL_DECIMAL.fullmatch(value):
        raise ValueError("not a canonical decimal string")
    unsigned = value.removeprefix("-")
    integer, dot, fraction = unsigned.partition(".")
    coefficient_digits = len(integer) + len(fraction)
    if (coefficient_digits > 256 or len(integer) > 256
            or (dot and len(fraction) > 128)):
        raise ValueError("canonical decimal exceeds declaration limits")
    return value


#: A scalar numeric value carried as its exact canonical decimal string.
CanonicalDecimal = Annotated[StrictStr, AfterValidator(_canonical_decimal)]


def canonical_constraint_decimal(value: str) -> str:
    """Canonicalize an authoring lexeme before record construction.

    Direct contracts and ledger load never call this helper.  Its deliberately
    small exponent preflight prevents hostile fixed-point expansion."""
    if not isinstance(value, str) or len(value.encode("utf-8")) > 386:
        raise ValueError("decimal authoring input is invalid")
    match = _AUTHORING_DECIMAL.fullmatch(value)
    if match is None:
        raise ValueError("decimal authoring input is invalid")
    mantissa, separator, exponent_text = value.lower().partition("e")
    unsigned = mantissa.removeprefix("-")
    integer, dot, fraction = unsigned.partition(".")
    if (len(integer) + len(fraction) > 256 or len(integer) > 256
            or (dot and len(fraction) > 128)):
        raise ValueError("decimal authoring input exceeds coefficient limits")
    if exponent_text and abs(int(exponent_text)) > 256:
        raise ValueError("decimal authoring input exceeds expansion limits")
    try:
        number = Decimal(value)
    except InvalidOperation as error:
        raise ValueError("decimal authoring input is invalid") from error
    if not number.is_finite():
        raise ValueError("decimal authoring input must be finite")
    rendered = format(number, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    if Decimal(rendered).is_zero():
        rendered = "0"
    return _canonical_decimal(rendered)


# ----------------------------------------------------------- v1 predicate
class _ConstraintValue(_Frozen):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")


class NumericBoundary(_ConstraintValue):
    value: CanonicalDecimal
    inclusion: Literal["inclusive", "exclusive"]


class ExactNumericLowerBound(_ConstraintValue):
    kind: Literal["lower_bound"] = "lower_bound"
    lower: NumericBoundary


class ExactNumericUpperBound(_ConstraintValue):
    kind: Literal["upper_bound"] = "upper_bound"
    upper: NumericBoundary


class ExactNumericInterval(_ConstraintValue):
    kind: Literal["interval"] = "interval"
    lower: NumericBoundary
    upper: NumericBoundary

    @model_validator(mode="after")
    def _interval_is_nonempty(self):
        lower = Decimal(self.lower.value)
        upper = Decimal(self.upper.value)
        if lower > upper:
            raise ValueError("interval lower boundary exceeds upper boundary")
        if lower == upper and (
                self.lower.inclusion != "inclusive"
                or self.upper.inclusion != "inclusive"):
            raise ValueError("an equal-endpoint interval must be inclusive")
        return self


ConstraintPredicate = Annotated[
    Union[ExactNumericLowerBound, ExactNumericUpperBound,
          ExactNumericInterval], Field(discriminator="kind")]


def _canonical_parents(value: tuple) -> tuple:
    """Accept any input order, reject duplicates, sort canonically. The
    normalized tuple is what the digest sees, so the parent SET is part of
    identity while the caller's ordering is not."""
    if len(set(value)) != len(value):
        raise ValueError("superseded specification ids must be unique")
    return tuple(sorted(value))


class VariableValueSpecification(_Frozen):
    """What the MODEL requires this variable's value representation to be.

    An unauthenticated authority CLAIM about the model — never a claim
    about any source, adapter, connector, or observation, and never
    evidence that an observed value carries the specified unit. It
    specifies value shape, nullability, and an optional model-unit
    identity only: no quantity kind, no physical meaning, no limits, no
    behaviour. The variable anchor is REFERENCED, not embedded: the
    registration already embeds it verbatim."""

    record_kind: Literal["variable_value_specification"] = (
        "variable_value_specification")
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^vsp_[0-9a-f]{64}$")
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    value_shape: Literal["boolean", "number", "string"]
    nullable: bool = False
    unit: UnitDeclaration
    evidence: Annotated[tuple[EvidenceRef, ...], Field(min_length=1),
                        AfterValidator(_canonical_evidence)]
    supersedes: Annotated[
        tuple[str, ...],
        AfterValidator(_canonical_parents)] = ()
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""

    @model_validator(mode="after")
    def _parent_ids_well_formed(self):
        for parent_id in self.supersedes:
            if not re.fullmatch(r"vsp_[0-9a-f]{64}", parent_id):
                raise ValueError(
                    f"{parent_id!r} is not a specification record id")
        if self.record_id in self.supersedes:
            raise ValueError("a specification cannot supersede itself")
        return self


class QuantityKindDeclaration(_Frozen):
    dimension: Literal["quantity_kind"]
    quantity_kind: QuantityKindReference


class ObservationRoleDeclaration(_Frozen):
    dimension: Literal["observation_role"]
    observation_role: ObservationRoleReference


SemanticDimensionDeclaration = Annotated[
    Union[QuantityKindDeclaration, ObservationRoleDeclaration],
    Field(discriminator="dimension")]


class VariableSemanticDeclaration(_Frozen):
    """One authority claim about one dimension of model-side meaning."""

    record_kind: Literal["variable_semantic_declaration"] = (
        "variable_semantic_declaration")
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^vsm_[0-9a-f]{64}$")
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    declaration: SemanticDimensionDeclaration
    evidence: Annotated[tuple[EvidenceRef, ...], Field(min_length=1),
                        AfterValidator(_canonical_evidence)]
    supersedes: Annotated[tuple[str, ...],
                          AfterValidator(_canonical_parents)] = ()
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""

    @model_validator(mode="after")
    def _parent_ids_well_formed(self):
        for parent_id in self.supersedes:
            if not re.fullmatch(r"vsm_[0-9a-f]{64}", parent_id):
                raise ValueError(f"{parent_id!r} is not a semantic record id")
        if self.record_id in self.supersedes:
            raise ValueError("a semantic declaration cannot supersede itself")
        return self


class ConstraintSemanticSignature(_Frozen):
    quantity_kind: QuantityKindReference
    observation_role: ObservationRoleReference
    unit: UnitReference


class ConstraintRegistration(_Frozen):
    """PERMANENT, evidence-bearing membership claim: one constraint identity
    (``con_`` anchor) targets one variable. Unlike entity/variable
    registrations (membership-only envelopes), a constraint registration
    carries nonempty ``EvidenceRef`` evidence, canonicalized by the uniform
    rules. It has NO ``supersedes``, withdrawal, or lifecycle field: the
    target-variable association must not become an unsupported model fact
    when a later declaration is superseded. The complete ``ConstraintAnchor``
    is embedded; the target variable is referenced by id, never embedded."""

    record_kind: Literal["constraint_registration"] = "constraint_registration"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^crg_[0-9a-f]{64}$")
    anchor: ConstraintAnchor
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    evidence: Annotated[tuple[EvidenceRef, ...], Field(min_length=1),
                        AfterValidator(_canonical_evidence)]
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""


class VariableConstraintDeclaration(_Frozen):
    """The correctable numeric constraint claim. Its LINEAGE KEY is the
    ``con_`` anchor only. Predicate form, boundaries, inclusivity, and all
    expected semantic tokens may change under a correction. The permanent
    registration owns the target variable. Locks are intentionally not
    cross-validated against VSM/VSP at append; mismatch belongs to Slice B."""

    record_kind: Literal["variable_constraint_declaration"] = (
        "variable_constraint_declaration")
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^vcn_[0-9a-f]{64}$")
    constraint_anchor_id: str = Field(pattern=CONSTRAINT_ANCHOR_ID_PATTERN)
    expected_semantics: ConstraintSemanticSignature
    predicate: ConstraintPredicate
    evidence: Annotated[tuple[EvidenceRef, ...], Field(min_length=1),
                        AfterValidator(_canonical_evidence)]
    supersedes: Annotated[tuple[str, ...],
                          AfterValidator(_canonical_parents)] = ()
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""

    @model_validator(mode="after")
    def _parent_ids_well_formed(self):
        for parent_id in self.supersedes:
            if not re.fullmatch(r"vcn_[0-9a-f]{64}", parent_id):
                raise ValueError(
                    f"{parent_id!r} is not a constraint declaration record id")
        if self.record_id in self.supersedes:
            raise ValueError("a constraint declaration cannot supersede itself")
        return self


class InterfaceDomainToken(_Frozen):
    """Exact interface-domain identity token; no ontology is implied."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")
    token_kind: Literal["interface_domain"] = "interface_domain"
    system_id: Literal["project_local"]
    system_edition: LocalIdentifier
    code: LocalIdentifier


class InterfaceTypeToken(_Frozen):
    """Exact interface-type identity token; no compatibility is implied."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")
    token_kind: Literal["interface_type"] = "interface_type"
    system_id: Literal["project_local"]
    system_edition: LocalIdentifier
    code: LocalIdentifier


class InterfaceDomainDeclaration(_Frozen):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")
    dimension: Literal["interface_domain"] = "interface_domain"
    value: InterfaceDomainToken


class DirectionRoleDeclaration(_Frozen):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")
    dimension: Literal["direction_role"] = "direction_role"
    value: Literal["input", "output", "bidirectional", "non_directional"]


class InterfaceTypeDeclaration(_Frozen):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")
    dimension: Literal["interface_type"] = "interface_type"
    value: InterfaceTypeToken


PortInterfaceDeclarationBody = Annotated[
    Union[InterfaceDomainDeclaration, DirectionRoleDeclaration,
          InterfaceTypeDeclaration],
    Field(discriminator="dimension"),
]


def _canonical_port_endpoints(value: tuple[str, ...]) -> tuple[str, ...]:
    for endpoint in value:
        if not isinstance(endpoint, str) or not re.fullmatch(
                PORT_ANCHOR_ID_PATTERN, endpoint):
            raise ValueError("a connection endpoint is not a port anchor id")
    if len(set(value)) != len(value):
        raise ValueError("connection endpoints must be unique")
    if not 2 <= len(value) <= 64:
        raise ValueError("a connection requires between 2 and 64 endpoints")
    return tuple(sorted(value))


CanonicalPortEndpointTuple = Annotated[
    tuple[str, ...], AfterValidator(_canonical_port_endpoints)]


class PortRegistration(_Frozen):
    record_kind: Literal["port_registration"] = "port_registration"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^prg_[0-9a-f]{64}$")
    anchor: PortAnchor
    owner_entity_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    evidence: Annotated[tuple[EvidenceRef, ...], Field(min_length=1),
                        AfterValidator(_canonical_evidence)]
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""


class PortInterfaceDeclaration(_Frozen):
    record_kind: Literal["port_interface_declaration"] = (
        "port_interface_declaration")
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^pif_[0-9a-f]{64}$")
    port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    context: AssertionContext
    declaration: PortInterfaceDeclarationBody
    evidence: Annotated[tuple[EvidenceRef, ...], Field(min_length=1),
                        AfterValidator(_canonical_evidence)]
    supersedes: Annotated[tuple[str, ...],
                          AfterValidator(_canonical_parents)] = ()
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""

    @model_validator(mode="after")
    def _parent_ids_well_formed(self):
        if any(not re.fullmatch(r"pif_[0-9a-f]{64}", parent)
               for parent in self.supersedes):
            raise ValueError("an interface parent is not a PIF record id")
        if self.record_id in self.supersedes:
            raise ValueError("an interface declaration cannot supersede itself")
        return self


class PortConnectionAssertion(_Frozen):
    record_kind: Literal["port_connection_assertion"] = (
        "port_connection_assertion")
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^pcn_[0-9a-f]{64}$")
    endpoint_port_anchor_ids: CanonicalPortEndpointTuple
    context: AssertionContext
    evidence: Annotated[tuple[EvidenceRef, ...], Field(min_length=1),
                        AfterValidator(_canonical_evidence)]
    supersedes: Annotated[tuple[str, ...],
                          AfterValidator(_canonical_parents)] = ()
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""

    @model_validator(mode="after")
    def _parent_ids_well_formed(self):
        if any(not re.fullmatch(r"pcn_[0-9a-f]{64}", parent)
               for parent in self.supersedes):
            raise ValueError("a connection parent is not a PCN record id")
        if self.record_id in self.supersedes:
            raise ValueError("a connection assertion cannot supersede itself")
        return self


class PortInterfaceCitation(_Frozen):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")
    port_anchor_id: str = Field(pattern=PORT_ANCHOR_ID_PATTERN)
    declaration_record_id: str = Field(pattern=r"^pif_[0-9a-f]{64}$")


_PT_DIMENSION_RANK = {
    "interface_domain": 0,
    "direction_role": 1,
    "interface_type": 2,
}
CompatibilityBasisDimension = Literal[
    "interface_domain", "direction_role", "interface_type"]


def _canonical_citations(
        value: tuple[PortInterfaceCitation, ...],
) -> tuple[PortInterfaceCitation, ...]:
    if len(value) != 2:
        raise ValueError("a compatibility dimension requires two citations")
    ids = tuple(citation.port_anchor_id for citation in value)
    if len(set(ids)) != 2:
        raise ValueError("compatibility citations require distinct endpoints")
    return tuple(sorted(value, key=lambda citation: citation.port_anchor_id))


class CompatibilityDimensionBasis(_Frozen):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")
    dimension: CompatibilityBasisDimension
    citations: Annotated[tuple[PortInterfaceCitation, ...],
                         AfterValidator(_canonical_citations)]


def _canonical_basis_dimensions(
        value: tuple[CompatibilityDimensionBasis, ...],
) -> tuple[CompatibilityDimensionBasis, ...]:
    if not value:
        raise ValueError("a compatibility basis requires a dimension")
    dimensions = tuple(item.dimension for item in value)
    if len(set(dimensions)) != len(dimensions):
        raise ValueError("compatibility basis dimensions must be unique")
    return tuple(sorted(value, key=lambda item: _PT_DIMENSION_RANK[item.dimension]))


class PortCompatibilityBasis(_Frozen):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")
    statement: str = Field(min_length=1)
    dimensions: Annotated[tuple[CompatibilityDimensionBasis, ...],
                          AfterValidator(_canonical_basis_dimensions)]


class PortCompatibilityDeclaration(_Frozen):
    record_kind: Literal["port_compatibility_declaration"] = (
        "port_compatibility_declaration")
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^pcm_[0-9a-f]{64}$")
    endpoint_port_anchor_ids: CanonicalPortEndpointTuple
    context: AssertionContext
    outcome: Literal["declared_compatible", "declared_incompatible"]
    basis: PortCompatibilityBasis
    evidence: Annotated[tuple[EvidenceRef, ...], Field(min_length=1),
                        AfterValidator(_canonical_evidence)]
    supersedes: Annotated[tuple[str, ...],
                          AfterValidator(_canonical_parents)] = ()
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""

    @model_validator(mode="after")
    def _pair_and_parents_are_well_formed(self):
        if len(self.endpoint_port_anchor_ids) != 2:
            raise ValueError("compatibility requires exactly two endpoints")
        if any(not re.fullmatch(r"pcm_[0-9a-f]{64}", parent)
               for parent in self.supersedes):
            raise ValueError("a compatibility parent is not a PCM record id")
        if self.record_id in self.supersedes:
            raise ValueError("a compatibility declaration cannot supersede itself")
        return self


class PortClaimWithdrawal(_Frozen):
    record_kind: Literal["port_claim_withdrawal"] = "port_claim_withdrawal"
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^ptw_[0-9a-f]{64}$")
    withdraws: str = Field(pattern=r"^(pif|pcn|pcm)_[0-9a-f]{64}$")
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""



ModelRecord = Union[
    EntityRegistration, VariableRegistration, VariableValueSpecification,
    VariableSemanticDeclaration,
    ConstraintRegistration, VariableConstraintDeclaration,
    RelationshipTypeDefinition, RelationshipAssertion,
    RelationshipWithdrawal,
    PortRegistration, PortInterfaceDeclaration, PortConnectionAssertion,
    PortCompatibilityDeclaration, PortClaimWithdrawal,
]


# ---------------------------------------------------------------- revision
class ModelRevision(_Frozen):
    """COMPUTED ONLY — never a file, never a ledger record; the membership
    pattern structurally excludes mrv_. Canonical order is the sorted
    record ids, never filesystem enumeration."""

    revision_id: str = Field(pattern=r"^mrv_[0-9a-f]{64}$")
    record_ids: tuple[str, ...]
    record_count: int = Field(ge=0)
    model_id: str = Field(pattern=MODEL_ID_PATTERN)

    @model_validator(mode="after")
    def _membership_consistent(self):
        ids = self.record_ids
        for record_id in ids:
            if not re.fullmatch(MODEL_RECORD_ID_PATTERN, record_id):
                raise ValueError(f"{record_id!r} is not a model record id")
        if list(ids) != sorted(set(ids)):
            raise ValueError("record_ids must be unique and sorted")
        if self.record_count != len(ids):
            raise ValueError("record_count must equal len(record_ids)")
        if self.revision_id != compute_revision_id(self.model_id, ids):
            raise ValueError("revision_id does not match the membership")
        return self


# --------------------------------------------------------------- results
class _ConstraintResultFrozen(_Frozen):
    model_config = ConfigDict(
        frozen=True, extra="forbid", revalidate_instances="always")


class ConstraintDeclarationResult(_ConstraintResultFrozen):
    constraint_anchor_id: str = Field(pattern=CONSTRAINT_ANCHOR_ID_PATTERN)
    status: Literal[
        "not_registered", "not_declared", "declared", "conflicted"]
    registration: ConstraintRegistration | None = None
    declaration: VariableConstraintDeclaration | None = None
    conflicting_declarations: tuple[VariableConstraintDeclaration, ...] = ()
    superseded_declaration_ids: tuple[str, ...] = ()
    revision: ModelRevision

    @model_validator(mode="after")
    def _coherent(self):
        # Rebuild nested objects from serialized fields. Existing lower-layer
        # bases remain unchanged while this new public boundary rejects forged
        # model_construct/model_copy instances.
        revision = ModelRevision.model_validate(self.revision.model_dump())
        registration = self.registration
        if registration is not None:
            registration = ConstraintRegistration.model_validate(
                registration.model_dump())
        declarations = tuple(
            VariableConstraintDeclaration.model_validate(item.model_dump())
            for item in self.conflicting_declarations)
        declaration = self.declaration
        if declaration is not None:
            declaration = VariableConstraintDeclaration.model_validate(
                declaration.model_dump())
        try:
            registration_valid = (registration is None
                                  or verify_record_id(registration))
            declaration_valid = (declaration is None
                                 or verify_record_id(declaration))
            conflicts_valid = all(verify_record_id(item)
                                  for item in declarations)
        except ModelIntegrityError as error:
            # Direct pydantic construction follows the normal ValidationError
            # contract; operational typed kernel errors belong to store/query
            # entry points, not nested field validation.
            raise ValueError(
                "carried constraint content is not canonically valid") from error
        if not registration_valid:
            raise ValueError("registration content does not match its record id")
        if not declaration_valid:
            raise ValueError("declaration content does not match its record id")
        if not conflicts_valid:
            raise ValueError("conflict content does not match its record id")

        registered = self.status != "not_registered"
        if registered != (registration is not None):
            raise ValueError("registration is present exactly when registered")
        if (self.status == "declared") != (declaration is not None):
            raise ValueError("one declaration is carried exactly when declared")
        if (self.status == "conflicted") != bool(declarations):
            raise ValueError("conflicting tips are carried exactly when conflicted")
        if self.status == "conflicted" and len(declarations) < 2:
            raise ValueError("a constraint conflict needs at least two tips")
        if self.status in ("not_registered", "not_declared") and (
                declarations or self.superseded_declaration_ids):
            raise ValueError("absence statuses carry no declaration history")
        if registration is not None and (
                registration.anchor.anchor_id != self.constraint_anchor_id):
            raise ValueError("registration must belong to the requested constraint")
        carried = (*declarations,) if declaration is None else (
            declaration, *declarations)
        if any(item.constraint_anchor_id != self.constraint_anchor_id
               for item in carried):
            raise ValueError("carried declarations must share the requested anchor")
        conflict_ids = [item.record_id for item in declarations]
        if conflict_ids != sorted(set(conflict_ids)):
            raise ValueError("conflicting declarations must be unique and sorted")
        if not _sorted_unique(self.superseded_declaration_ids):
            raise ValueError("superseded declaration ids must be unique and sorted")
        active_ids = set(conflict_ids)
        if declaration is not None:
            active_ids.add(declaration.record_id)
        if active_ids.intersection(self.superseded_declaration_ids):
            raise ValueError("current tips cannot also be disclosed as superseded")
        members = set(revision.record_ids)
        ids = ([registration.record_id] if registration is not None else [])
        ids.extend(item.record_id for item in carried)
        ids.extend(self.superseded_declaration_ids)
        if not set(ids) <= members:
            raise ValueError("every carried constraint record must belong to revision")
        return self


class VariableConstraintCollectionResult(_ConstraintResultFrozen):
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    status: Literal["registered", "not_registered"]
    constraints: tuple[ConstraintDeclarationResult, ...] = ()
    revision: ModelRevision

    @model_validator(mode="after")
    def _coherent(self):
        revision = ModelRevision.model_validate(self.revision.model_dump())
        entries = tuple(ConstraintDeclarationResult.model_validate(
            item.model_dump()) for item in self.constraints)
        if self.status == "not_registered" and entries:
            raise ValueError("an unregistered variable carries no constraints")
        anchors = [item.constraint_anchor_id for item in entries]
        if anchors != sorted(set(anchors)):
            raise ValueError("constraints must be unique and ordered by anchor")
        for item in entries:
            if item.revision != revision:
                raise ValueError("one model revision governs the collection")
            if (item.registration is None
                    or item.registration.variable_anchor_id
                    != self.variable_anchor_id):
                raise ValueError("every constraint must target the requested variable")
        return self


def _sorted_unique(values) -> bool:
    return list(values) == sorted(set(values))


class EvidenceDisclosure(_Frozen):
    ref: EvidenceRef
    verification: Literal["verified_in_revision", "declared_reference"]


class RelationshipSummary(_Frozen):
    record_id: str = Field(pattern=r"^rel_[0-9a-f]{64}$")
    type_id: str = Field(pattern=r"^rtd_[0-9a-f]{64}$")
    type_name: str
    forward_label: str
    inverse_label: str
    cited_type_current: bool
    source_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    target_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    context: AssertionContext
    authority: AuthorityRef
    evidence: tuple[EvidenceDisclosure, ...]
    supersedes: str | None = None
    superseded_by: tuple[str, ...] = ()
    withdrawn_by: tuple[str, ...] = ()
    active: bool
    recorded_at: UtcDatetime

    @model_validator(mode="after")
    def _lifecycle_consistent(self):
        if self.active != (not self.superseded_by and not self.withdrawn_by):
            raise ValueError(
                "active is equivalent to having no lifecycle links")
        for values, prefix in ((self.superseded_by, "rel"),
                               (self.withdrawn_by, "rwd")):
            if not _sorted_unique(values):
                raise ValueError("lifecycle links must be unique/sorted")
            for record_id in values:
                if not re.fullmatch(rf"^{prefix}_[0-9a-f]{{64}}$", record_id):
                    raise ValueError(f"{record_id!r} is not a {prefix} id")
        return self


class LineageConflict(_Frozen):
    """Competing ACTIVE successors of one predecessor — reported here
    exclusively; a second hierarchy parent candidate is never fabricated."""

    predecessor_id: str = Field(pattern=r"^rel_[0-9a-f]{64}$")
    competing_successor_ids: tuple[str, ...] = Field(min_length=2)

    @model_validator(mode="after")
    def _competitors_canonical(self):
        if not _sorted_unique(self.competing_successor_ids):
            raise ValueError("competitors must be unique/sorted")
        return self


class RelationshipsResult(_Frozen):
    """Absence is a structured status: an entity unknown to this revision is
    never conflated with a registered entity that has no declared edge."""

    status: Literal["registered", "not_registered"]
    anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    direction: Literal["incoming", "outgoing", "both"]
    type_name: str | None
    context: AssertionContext
    active: tuple[RelationshipSummary, ...]
    inactive: tuple[RelationshipSummary, ...]
    lineage_conflicts: tuple[LineageConflict, ...]
    revision: ModelRevision

    @model_validator(mode="after")
    def _placement_matches_state(self):
        if any(not summary.active for summary in self.active):
            raise ValueError("inactive summary placed in the active tuple")
        if any(summary.active for summary in self.inactive):
            raise ValueError("active summary placed in the inactive tuple")
        if self.status == "not_registered" and (
                self.active or self.inactive or self.lineage_conflicts):
            raise ValueError(
                "an unregistered anchor carries no relationships")
        return self


class RegistrationSummary(_Frozen):
    record_id: str = Field(pattern=r"^reg_[0-9a-f]{64}$")
    anchor: EntityAnchor
    authority: AuthorityRef
    recorded_at: UtcDatetime


class EntityResult(_Frozen):
    status: Literal["registered", "not_registered"]
    anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    registration: RegistrationSummary | None = None
    revision: ModelRevision

    @model_validator(mode="after")
    def _registration_iff_registered(self):
        if (self.status == "registered") != (self.registration is not None):
            raise ValueError("registration is present exactly when registered")
        return self


class VariableRegistrationSummary(_Frozen):
    record_id: str = Field(pattern=r"^vrg_[0-9a-f]{64}$")
    anchor: VariableAnchor
    authority: AuthorityRef
    recorded_at: UtcDatetime


class VariableResult(_Frozen):
    status: Literal["registered", "not_registered"]
    anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    registration: VariableRegistrationSummary | None = None
    revision: ModelRevision

    @model_validator(mode="after")
    def _registration_iff_registered(self):
        if (self.status == "registered") != (self.registration is not None):
            raise ValueError("registration is present exactly when registered")
        return self


class EntityVariablesResult(_Frozen):
    """Variables owned by one entity in this revision. `status` is the
    ENTITY's membership: an unregistered entity is never conflated with a
    registered entity that owns zero variables."""

    status: Literal["registered", "not_registered"]
    entity_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    entries: tuple[VariableRegistrationSummary, ...] = ()
    revision: ModelRevision

    @model_validator(mode="after")
    def _absence_is_structured(self):
        if self.status == "not_registered" and self.entries:
            raise ValueError("an unregistered entity carries no variables")
        ids = [entry.anchor.anchor_id for entry in self.entries]
        if ids != sorted(ids):
            raise ValueError("entries must be ordered by anchor id")
        return self


class VariableSpecificationResult(_Frozen):
    """The SINGLE source of specification status. `conflicted` carries every
    competing current tip verbatim and is never resolved by recency,
    authority, record id, file order, or append order."""

    status: Literal["specified", "not_specified", "conflicted",
                    "not_registered"]
    anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    specification: VariableValueSpecification | None = None
    conflicting_specifications: tuple[VariableValueSpecification, ...] = ()
    superseded_specification_ids: tuple[str, ...] = ()
    revision: ModelRevision

    @model_validator(mode="after")
    def _status_consistent(self):
        if (self.status == "specified") != (self.specification is not None):
            raise ValueError(
                "a specification is carried exactly when specified")
        if (self.status == "conflicted") != bool(
                self.conflicting_specifications):
            raise ValueError("competing tips are carried exactly when "
                             "conflicted")
        if self.status == "conflicted" and len(
                self.conflicting_specifications) < 2:
            raise ValueError("a conflict needs at least two current tips")
        ids = [record.record_id for record in self.conflicting_specifications]
        if ids != sorted(ids):
            raise ValueError("competing tips must be canonically ordered")
        if not _sorted_unique(self.superseded_specification_ids):
            raise ValueError("superseded ids must be unique and sorted")
        if self.status == "not_registered" and (
                self.superseded_specification_ids):
            raise ValueError(
                "an unregistered variable carries no specification history")
        return self


class SemanticDimensionResult(_Frozen):
    dimension: Literal["quantity_kind", "observation_role"]
    status: Literal["declared", "not_declared", "conflicted",
                    "not_registered"]
    declaration: VariableSemanticDeclaration | None = None
    conflicting_declarations: tuple[VariableSemanticDeclaration, ...] = ()
    superseded_declaration_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _status_consistent(self):
        if (self.status == "declared") != (self.declaration is not None):
            raise ValueError("declaration is carried exactly when declared")
        if (self.status == "conflicted") != bool(self.conflicting_declarations):
            raise ValueError("competing declarations occur exactly when conflicted")
        if self.status == "conflicted" and len(self.conflicting_declarations) < 2:
            raise ValueError("a conflict requires at least two declarations")
        ids = [record.record_id for record in self.conflicting_declarations]
        if ids != sorted(set(ids)):
            raise ValueError(
                "competing declarations must be unique and canonically ordered")
        carried = (() if self.declaration is None else (self.declaration,))
        carried += self.conflicting_declarations
        if any(record.declaration.dimension != self.dimension
               for record in carried):
            raise ValueError(
                "carried declarations must match the result dimension")
        if not _sorted_unique(self.superseded_declaration_ids):
            raise ValueError("superseded declaration ids must be unique and sorted")
        if self.status == "not_registered" and self.superseded_declaration_ids:
            raise ValueError("an unregistered variable carries no semantic history")
        return self


class VariableSemanticsResult(_Frozen):
    anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    quantity_kind: SemanticDimensionResult
    observation_role: SemanticDimensionResult
    revision: ModelRevision

    @model_validator(mode="after")
    def _dimensions_consistent(self):
        if self.quantity_kind.dimension != "quantity_kind":
            raise ValueError("quantity_kind result has the wrong dimension")
        if self.observation_role.dimension != "observation_role":
            raise ValueError("observation_role result has the wrong dimension")
        unregistered = (self.quantity_kind.status == "not_registered",
                        self.observation_role.status == "not_registered")
        if unregistered[0] != unregistered[1]:
            raise ValueError("both dimensions are unregistered exactly together")
        carried = []
        for result in (self.quantity_kind, self.observation_role):
            if result.declaration is not None:
                carried.append(result.declaration)
            carried.extend(result.conflicting_declarations)
        if any(record.variable_anchor_id != self.anchor_id
               for record in carried):
            raise ValueError(
                "carried declarations must belong to the requested variable")
        return self


ParentStatus = Literal[
    "resolved", "no_declared_parent", "conflicted", "cyclic", "not_registered"
]


class ParentResult(_Frozen):
    status: ParentStatus
    child_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    parent: EntityAnchor | None = None
    supporting: tuple[RelationshipSummary, ...] = ()
    candidate_parents: tuple[EntityAnchor, ...] = ()
    cycle_members: tuple[str, ...] = ()
    type_name: str
    view: LifecycleView | None = None
    revision: ModelRevision

    @model_validator(mode="after")
    def _fields_match_status(self):
        if (self.status == "resolved") != (self.parent is not None):
            raise ValueError("parent is set exactly when resolved")
        if self.status == "resolved" and not self.supporting:
            raise ValueError("a resolved parent cites its supporting assertions")
        if (self.status == "conflicted") != (len(self.candidate_parents) >= 2):
            raise ValueError("candidates exist exactly when conflicted")
        if (self.status == "cyclic") != bool(self.cycle_members):
            raise ValueError("cycle members exist exactly when cyclic")
        if not _sorted_unique([a.anchor_id for a in self.candidate_parents]):
            raise ValueError("candidates must be unique/sorted")
        if not _sorted_unique(self.cycle_members):
            raise ValueError("cycle members must be unique/sorted")
        return self


class TraversalAnnotation(_Frozen):
    kind: Literal["multiple_parents"]
    candidate_parent_anchor_ids: tuple[str, ...] = Field(min_length=2)
    via_assertion_ids: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _canonical(self):
        if not _sorted_unique(self.candidate_parent_anchor_ids):
            raise ValueError("candidates must be unique/sorted")
        if not _sorted_unique(self.via_assertion_ids):
            raise ValueError("assertion ids must be unique/sorted")
        return self


class ChildEntry(_Frozen):
    anchor: EntityAnchor
    supporting: tuple[RelationshipSummary, ...] = Field(min_length=1)
    annotations: tuple[TraversalAnnotation, ...] = ()


class ChildrenResult(_Frozen):
    status: Literal["listed", "not_registered", "cyclic"]
    parent_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    entries: tuple[ChildEntry, ...] = ()
    cycle_members: tuple[str, ...] = ()
    type_name: str
    view: LifecycleView | None = None
    revision: ModelRevision

    @model_validator(mode="after")
    def _fields_match_status(self):
        if self.status != "listed" and self.entries:
            raise ValueError("entries exist only when listed")
        if (self.status == "cyclic") != bool(self.cycle_members):
            raise ValueError("cycle members exist exactly when cyclic")
        return self


class TraversalStep(_Frozen):
    anchor: EntityAnchor
    supporting: tuple[RelationshipSummary, ...] = Field(min_length=1)
    annotations: tuple[TraversalAnnotation, ...] = ()


class TraversalBlock(_Frozen):
    anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    reason: Literal["conflicted", "cyclic"]


class TraversalResult(_Frozen):
    status: Literal["complete", "partial", "not_registered"]
    origin_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    steps: tuple[TraversalStep, ...] = ()
    blocked: tuple[TraversalBlock, ...] = ()
    type_name: str
    view: LifecycleView | None = None
    revision: ModelRevision

    @model_validator(mode="after")
    def _partial_iff_blocked(self):
        if (self.status == "partial") != bool(self.blocked):
            raise ValueError("partial exactly when something blocked")
        if self.status == "not_registered" and (self.steps or self.blocked):
            raise ValueError("not_registered carries no steps or blocks")
        return self


class CycleReport(_Frozen):
    members: tuple[str, ...] = Field(min_length=2)
    via_assertion_ids: tuple[str, ...] = Field(min_length=1)


class ParentConflictReport(_Frozen):
    child_anchor_id: str = Field(pattern=ENTITY_ANCHOR_ID_PATTERN)
    candidate_parent_anchor_ids: tuple[str, ...] = Field(min_length=2)
    via_assertion_ids: tuple[str, ...] = Field(min_length=2)


class HierarchyHealth(_Frozen):
    type_name: str
    view: LifecycleView | None = None
    cycles: tuple[CycleReport, ...] = ()
    parent_conflicts: tuple[ParentConflictReport, ...] = ()
    stale_type_assertions: tuple[str, ...] = ()
    revision: ModelRevision
