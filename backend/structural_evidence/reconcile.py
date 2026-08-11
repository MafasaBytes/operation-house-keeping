"""SN-001 multi-set structural reconciliation.

Read-only composition over injected accepted query objects (ADR-0008 D2):
owns no store, no ledger, no revision id. Every participating
`ResolutionResult` and `BindingRevision` is carried VERBATIM — this module
re-expresses no resolution vocabulary.

The join rule, published normatively: two source subjects participate in
a cross-source identity join if and only if, at the required resolution
instant, accepted binding resolutions positively bind both subjects to
the same canonical anchor. Names, labels, part numbers, quantities,
geometry, and display text are never join keys. There is NO fallback
join: `_join_index` is the only function that builds a claim-keyed
mapping.

Findings carry a mandatory `basis` naming which of the three layers they
speak for — what the source reported (`source_claim`), how an authority
interpreted it (`authority_interpretation`), or what was separately
accepted (`accepted_model_record`) — and each basis gates its own
support, cross-validated against the disclosed inputs at construction.

`inputs_digest` (`sid_`) is an input fingerprint, recomputable from
disclosed result fields only. It is not a result, not a revision id, has
no membership tuple, and is not citable as evidence.
"""

import hashlib
import json
import re
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Annotated, Iterator, Literal, Mapping, Sequence

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from backend.identity_binding.contracts import (
    BindingRevision,
    ResolutionResult,
)
from backend.identity_binding.resolver import BindingResolver
from backend.model_kernel import ModelQueries, ModelRevision
from backend.structural_evidence.contracts import (
    SourceStructuralClaim,
    SourceStructuralClaimSet,
)
from backend.structural_evidence.errors import StructuralEvidenceError
from backend.structural_evidence.locators import (
    StructuralAddress,
    canonical_locator_value,
    toolchain_fingerprint,
)
from backend.structural_evidence.rules import (
    SubjectIdentityRule,
    apply_rule,
    to_source_subject_ref,
)
from backend.system_identity import ENTITY_ANCHOR_ID_PATTERN
from backend.temporal_state.contracts import SourceSubjectRef

UtcDatetime = Annotated[AwareDatetime,
                        AfterValidator(lambda v: v.astimezone(UTC))]


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# ------------------------------------------------------- finding vocabulary
FindingBasis = Literal["source_claim", "authority_interpretation",
                       "accepted_model_record"]

Finding = Literal[
    # ---- basis = source_claim (10)
    "supported_by_bom_only", "supported_by_step_only",
    "claims_mutually_contradictory", "claims_not_comparable",
    "duplicate_source_label_not_identity",
    "absence_is_not_evidence_of_absence",
    "evidence_incomplete", "evidence_unavailable",
    "cited_payload_checksum_differs", "extractor_identity_changed",
    "derived_usage_path_ambiguous",
    # ---- basis = authority_interpretation (11)
    "source_subject_unmapped", "mapping_ambiguous", "mapping_conflicted",
    "mappings_jointly_incoherent", "context_unknown", "context_incompatible",
    "subject_bound_in_multiple_sets_consistently",
    "mapping_conflicted_across_sets", "anchor_declared_in_multiple_sets",
    "required_binding_set_missing", "cited_extraction_not_found",
    # ---- basis = accepted_model_record (3)
    "anchor_not_registered",
    "quantity_not_reconcilable_with_registered_instances",
    "corroborated_by_all_mapped_sources",
]

# `cited_extraction_not_found` speaks for the MAPPING that cites absent
# evidence (no claim exists to support a source_claim basis), so it lives
# under authority_interpretation. This is a documented correction to the
# spec's 12/10/3 split (now 11/11/3); the spec is amended alongside.
BASIS_BY_FINDING: Mapping[str, FindingBasis] = MappingProxyType({
    "supported_by_bom_only": "source_claim",
    "supported_by_step_only": "source_claim",
    "claims_mutually_contradictory": "source_claim",
    "claims_not_comparable": "source_claim",
    "duplicate_source_label_not_identity": "source_claim",
    "absence_is_not_evidence_of_absence": "source_claim",
    "evidence_incomplete": "source_claim",
    "evidence_unavailable": "source_claim",
    "cited_payload_checksum_differs": "source_claim",
    "extractor_identity_changed": "source_claim",
    "derived_usage_path_ambiguous": "source_claim",
    "source_subject_unmapped": "authority_interpretation",
    "mapping_ambiguous": "authority_interpretation",
    "mapping_conflicted": "authority_interpretation",
    "mappings_jointly_incoherent": "authority_interpretation",
    "context_unknown": "authority_interpretation",
    "context_incompatible": "authority_interpretation",
    "subject_bound_in_multiple_sets_consistently":
        "authority_interpretation",
    "mapping_conflicted_across_sets": "authority_interpretation",
    "anchor_declared_in_multiple_sets": "authority_interpretation",
    "required_binding_set_missing": "authority_interpretation",
    "cited_extraction_not_found": "authority_interpretation",
    "anchor_not_registered": "accepted_model_record",
    "quantity_not_reconcilable_with_registered_instances":
        "accepted_model_record",
    "corroborated_by_all_mapped_sources": "accepted_model_record",
})

# Findings whose evidence cannot be a resolution or a claim by their very
# nature: the duplicate DECLARATIONS, the MISSING set, and the mapping
# citing evidence that is not there. Each still gates on what it can
# honestly name (anchor, set id in detail, or the declared subject).
_SUPPORT_EXEMPT: frozenset = frozenset({
    "anchor_declared_in_multiple_sets", "required_binding_set_missing",
    "cited_extraction_not_found"})


# ------------------------------------------------------------- disclosures
class BindingSetResolution(_Frozen):
    binding_set_id: str = Field(pattern=r"^[a-z0-9-]+$")
    resolution: ResolutionResult  # identity_binding, VERBATIM


class ResolvedSubject(_Frozen):
    """One (claim x rule) resolution outcome across EVERY participating
    set. `join_anchor_id` is derived, never settable independently: it is
    non-None exactly when the set of positively-bound anchors across all
    participating sets has exactly one member."""

    claim_address: StructuralAddress
    rule_id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,47}$")
    rule_fingerprint: str = Field(pattern=r"^[0-9a-f]{16}$")
    toolchain_fingerprint: str = Field(pattern=r"^[0-9a-f]{16}$")
    subject: SourceSubjectRef | None
    no_subject_reason: Literal["rule_yielded_none"] | None = None
    resolutions: tuple[BindingSetResolution, ...] = ()
    join_anchor_id: str | None = None

    @model_validator(mode="after")
    def _consistent(self):
        if (self.subject is None) != (self.no_subject_reason is not None):
            raise ValueError("subject and no_subject_reason are exclusive")
        if self.subject is None and (self.resolutions
                                     or self.join_anchor_id):
            raise ValueError("a subject-less outcome resolves nothing")
        ids = [r.binding_set_id for r in self.resolutions]
        if ids != sorted(set(ids)):
            raise ValueError("resolutions must be unique and sorted by set")
        bound = sorted({r.resolution.resolved_target.anchor_id
                        for r in self.resolutions
                        if r.resolution.status == "bound"})
        derived = bound[0] if len(bound) == 1 else None
        if self.join_anchor_id != derived:
            raise ValueError(
                "join_anchor_id must derive from the positively-bound "
                "anchor set (exactly one member) and nothing else")
        return self


class ClaimSetDisclosure(_Frozen):
    """O1: complete one-to-one coverage over (claim_address, rule_id).
    Two rules applying to one claim yield two ResolvedSubjects,
    deliberately. Whether the rule set equals the reconciler's full
    applicable-rule list is checked by the reconciler at construction,
    not by this validator."""

    claim_set: SourceStructuralClaimSet
    resolved_subjects: tuple[ResolvedSubject, ...]

    @model_validator(mode="after")
    def _one_to_one_over_claim_and_rule(self):
        keys = [(canonical_locator_value(rs.claim_address.locator),
                 rs.rule_id) for rs in self.resolved_subjects]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate (claim, rule) resolution")
        claim_values = {canonical_locator_value(c.address.locator)
                        for c in self.claim_set.subject_claims}
        for value, _ in keys:
            if value not in claim_values:
                raise ValueError(
                    "a resolved subject must address a disclosed claim")
        rules_by_kind: dict[str, set] = {}
        for claim in self.claim_set.subject_claims:
            value = canonical_locator_value(claim.address.locator)
            rules = {rule for v, rule in keys if v == value}
            expected = rules_by_kind.setdefault(claim.claim_kind, rules)
            if rules != expected:
                raise ValueError(
                    "claims sharing a claim_kind must carry an identical "
                    "rule set")
        return self


class ModelDisclosure(_Frozen):
    """A model fact read out of the SUPPLIED revision — the only
    constructor reads the supplied LoadedModel, so `verified` has exactly
    one member."""

    anchor_id: str = Field(pattern=r"^ent_[0-9a-f]{32}$")
    model_revision_id: str = Field(pattern=r"^mrv_[0-9a-f]{64}$")
    registration_record_id: str | None = Field(
        default=None, pattern=r"^reg_[0-9a-f]{64}$")
    relationship_record_ids: tuple[str, ...] = ()
    verified: Literal["verified_in_supplied_revision"]

    def cited_record_ids(self) -> tuple[str, ...]:
        head = ((self.registration_record_id,)
                if self.registration_record_id else ())
        return head + self.relationship_record_ids


ComparableClaimKind = Literal["quantity_lexeme", "containment_parent_anchor"]


class ComparisonOperand(_Frozen):
    subject: SourceSubjectRef
    address: StructuralAddress
    operand: str | None  # the VERBATIM lexeme or an anchor id; None=absent


class ClaimComparison(_Frozen):
    comparable: ComparableClaimKind
    left: ComparisonOperand
    right: ComparisonOperand
    verdict: Literal["mutually_contradictory", "identical", "not_comparable"]

    @model_validator(mode="after")
    def _verdict_follows_the_operands(self):
        if self.left.operand is None or self.right.operand is None:
            if self.verdict != "not_comparable":
                raise ValueError("an absent operand is never a contradiction")
        elif (self.left.operand == self.right.operand) != (
                self.verdict == "identical"):
            raise ValueError("verdict must follow byte comparison")
        return self


class ReconciliationFinding(_Frozen):
    finding: Finding
    basis: FindingBasis  # NO DEFAULT
    subject: SourceSubjectRef | None = None
    anchor_id: str | None = Field(default=None,
                                  pattern=r"^ent_[0-9a-f]{32}$")
    supporting_claims: tuple[SourceStructuralClaim, ...] = ()   # VERBATIM
    supporting_resolutions: tuple[BindingSetResolution, ...] = ()
    model_disclosures: tuple[ModelDisclosure, ...] = ()
    comparisons: tuple[ClaimComparison, ...] = ()
    detail: str = Field(default="", max_length=1024)

    @model_validator(mode="after")
    def _basis_and_support_are_load_bearing(self):
        if self.basis != BASIS_BY_FINDING[self.finding]:
            raise ValueError(
                f"{self.finding} speaks for "
                f"{BASIS_BY_FINDING[self.finding]}, not {self.basis}")
        if self.finding not in _SUPPORT_EXEMPT:
            if self.basis == "source_claim" and not self.supporting_claims:
                raise ValueError(
                    "a source_claim finding requires supporting claims")
            if self.basis == "authority_interpretation" and \
                    not self.supporting_resolutions:
                raise ValueError("an authority_interpretation finding "
                                 "requires supporting resolutions")
        if self.basis == "accepted_model_record":
            if not self.model_disclosures:
                raise ValueError("a model finding requires disclosures")
            if self.anchor_id is None:
                raise ValueError("a model-basis finding names its anchor")
            if self.finding == "anchor_not_registered":
                # the absence form: there is no record to cite
                if any(d.cited_record_ids() for d in self.model_disclosures):
                    raise ValueError(
                        "an absence finding cites no record ids")
            else:
                for disclosure in self.model_disclosures:
                    if not disclosure.cited_record_ids():
                        raise ValueError(
                            "a positive model finding cites at least one "
                            "record id per disclosure")
        if self.finding == "anchor_declared_in_multiple_sets" and \
                self.anchor_id is None:
            raise ValueError("the duplicate-declaration finding names its "
                             "anchor")
        if self.finding == "cited_extraction_not_found" and \
                self.subject is None:
            raise ValueError("the absent-citation finding names the "
                             "declared subject")
        contradicting = any(c.verdict == "mutually_contradictory"
                            for c in self.comparisons)
        if (self.finding == "claims_mutually_contradictory") != contradicting:
            raise ValueError("a contradicting comparison appears exactly on "
                             "a contradiction finding")
        return self


class PayloadVerification(_Frozen):
    raw_record_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    supplied_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    matches_cited: bool


class BindingSetParticipation(_Frozen):
    binding_set_id: str = Field(pattern=r"^[a-z0-9-]+$")
    revision: BindingRevision  # identity_binding, VERBATIM


def _canon(model) -> str:
    return json.dumps(model.model_dump(mode="json"), sort_keys=True,
                      separators=(",", ":"), ensure_ascii=False)


def compute_inputs_digest(result) -> str:
    """Recomputable from DISCLOSED RESULT FIELDS ONLY. An input
    fingerprint, never a revision: findings are a deterministic function
    of the disclosed inputs and are not digested."""
    lines = (
        "sn001-inputs-v1",
        result.resolution_at.astimezone(UTC).isoformat(),
        result.model_revision.revision_id,
        *(f"required={set_id}"
          for set_id in result.required_binding_set_ids),
        *(f"{p.binding_set_id}={p.revision.revision_id}"
          for p in result.participations),
        *(f"rule:{rule_id}={fingerprint}"
          for rule_id, fingerprint in result.rules_used),
        *(f"toolchain={fp}" for fp in result.toolchain_fingerprints_used),
        *(f"payload:{v.raw_record_id}={v.supplied_sha256}"
          for v in result.verified_payloads),
        *(_canon(d.claim_set) for d in result.claim_sets),
        *(_canon(s) for d in result.claim_sets
          for s in d.resolved_subjects),
    )
    return "sid_" + hashlib.sha256(
        "\n".join(lines).encode("utf-8")).hexdigest()


class StructuralReconciliationResult(_Frozen):
    findings: tuple[ReconciliationFinding, ...]
    claim_sets: tuple[ClaimSetDisclosure, ...]
    participations: tuple[BindingSetParticipation, ...] = Field(min_length=1)
    model_revision: ModelRevision  # model_kernel, VERBATIM
    resolution_at: UtcDatetime
    rules_used: tuple[tuple[str, str], ...]
    toolchain_fingerprints_used: tuple[str, ...] = ()
    required_binding_set_ids: tuple[str, ...] = ()
    verified_payloads: tuple[PayloadVerification, ...] = ()
    inputs_digest: str = Field(pattern=r"^sid_[0-9a-f]{64}$")

    @model_validator(mode="after")
    def _canonical_and_honest(self):
        set_keys = [(d.claim_set.source_ref.source_id,
                     d.claim_set.source_ref.raw_record_id)
                    for d in self.claim_sets]
        if set_keys != sorted(set_keys):
            raise ValueError("claim sets must be canonically ordered")
        participation_ids = [p.binding_set_id for p in self.participations]
        if participation_ids != sorted(set(participation_ids)):
            raise ValueError("participations must be unique and sorted")
        derived_rules = tuple(sorted({
            (rs.rule_id, rs.rule_fingerprint)
            for d in self.claim_sets for rs in d.resolved_subjects}))
        if self.rules_used != derived_rules:
            raise ValueError("rules_used must derive from the disclosed "
                             "resolved subjects")
        derived_toolchains = tuple(sorted({
            rs.toolchain_fingerprint
            for d in self.claim_sets for rs in d.resolved_subjects}))
        if self.toolchain_fingerprints_used != derived_toolchains:
            raise ValueError("toolchain fingerprints must derive from the "
                             "disclosed resolved subjects")
        if list(self.required_binding_set_ids) != sorted(
                set(self.required_binding_set_ids)):
            raise ValueError("required set ids must be unique and sorted")
        payload_ids = [v.raw_record_id for v in self.verified_payloads]
        if payload_ids != sorted(set(payload_ids)):
            raise ValueError("payload verifications must be unique/sorted")
        finding_keys = [(f.finding,
                         _canon(f.subject) if f.subject else "",
                         f.anchor_id or "") for f in self.findings]
        if finding_keys != sorted(finding_keys):
            raise ValueError("findings must be canonically ordered")
        self._no_subject_silently_dropped()
        self._support_is_disclosed()
        if self.inputs_digest != compute_inputs_digest(self):
            raise ValueError("inputs_digest must recompute from the "
                             "disclosed fields")
        return self

    def _no_subject_silently_dropped(self):
        covered = {_canon(f.subject) for f in self.findings if f.subject}
        covered |= {_canon(op.subject) for f in self.findings
                    for c in f.comparisons for op in (c.left, c.right)}
        anchors = {f.anchor_id for f in self.findings if f.anchor_id}
        for disclosure in self.claim_sets:
            for rs in disclosure.resolved_subjects:
                if rs.subject is None:
                    continue  # disclosed via no_subject_reason itself
                if _canon(rs.subject) in covered:
                    continue
                if rs.join_anchor_id and rs.join_anchor_id in anchors:
                    continue
                raise ValueError(
                    "every subject-bearing resolved subject must appear in "
                    "at least one finding")

    def _support_is_disclosed(self):
        disclosed_claims = {_canon(c) for d in self.claim_sets
                            for c in d.claim_set.subject_claims}
        disclosed_resolutions = {_canon(r) for d in self.claim_sets
                                 for rs in d.resolved_subjects
                                 for r in rs.resolutions}
        record_ids = set(self.model_revision.record_ids)
        for finding in self.findings:
            for claim in finding.supporting_claims:
                if _canon(claim) not in disclosed_claims:
                    raise ValueError("a supporting claim must BE a "
                                     "disclosed input claim")
            if finding.finding not in _SUPPORT_EXEMPT:
                for resolution in finding.supporting_resolutions:
                    if _canon(resolution) not in disclosed_resolutions:
                        raise ValueError("a supporting resolution must BE a "
                                         "disclosed input resolution")
            for disclosure in finding.model_disclosures:
                if disclosure.model_revision_id != \
                        self.model_revision.revision_id:
                    raise ValueError("model disclosures cite the supplied "
                                     "revision only")
                for record_id in disclosure.cited_record_ids():
                    if record_id not in record_ids:
                        raise ValueError("a cited model record must be in "
                                         "the supplied revision")


# --------------------------------------------------------------- reconciler
def _family_of(claim: SourceStructuralClaim) -> str:
    return "bom" if claim.claim_kind == "bom_row" else "step"


class StructuralReconciler:
    """Every resolver is queried for every subject — no short-circuit, no
    first-match, no priority, never a preferred set. The result is
    canonicalized independently of caller order."""

    def __init__(self, *, resolvers: Sequence[BindingResolver],
                 rules: Sequence[SubjectIdentityRule],
                 model,
                 required_binding_set_ids: frozenset = frozenset(),
                 payloads: Mapping[str, bytes] | None = None) -> None:
        if not resolvers:
            raise StructuralEvidenceError(
                "SN_NO_BINDING_RESOLVER",
                "at least one binding resolver is required")
        by_id: dict[str, BindingResolver] = {}
        for resolver in resolvers:
            set_id = resolver.loaded.revision.binding_set_id
            if set_id in by_id:
                raise StructuralEvidenceError(
                    "SN_DUPLICATE_BINDING_SET",
                    f"binding set {set_id} supplied more than once")
            by_id[set_id] = resolver
        self._resolvers = dict(sorted(by_id.items()))
        self._rules = tuple(rules)
        self._model = model
        self._queries = ModelQueries(model)
        self._required = frozenset(required_binding_set_ids)
        self._payloads = payloads

    # -- public --------------------------------------------------------
    def reconcile(self, claim_sets: Sequence[SourceStructuralClaimSet], *,
                  resolution_at: datetime) -> StructuralReconciliationResult:
        if (not isinstance(resolution_at, datetime)
                or resolution_at.tzinfo is None
                or resolution_at.tzinfo.utcoffset(resolution_at) is None):
            raise StructuralEvidenceError(
                "SN_NAIVE_RESOLUTION_AT",
                "resolution_at must be a timezone-aware instant on the "
                "ingestion-receipt axis")
        disclosures = tuple(sorted(
            (self._disclose(claim_set, resolution_at)
             for claim_set in claim_sets),
            key=lambda d: (d.claim_set.source_ref.source_id,
                           d.claim_set.source_ref.raw_record_id)))
        payload_verifications = self._verify_payloads(disclosures)
        findings = tuple(sorted(
            self._generate_findings(disclosures, resolution_at,
                                    payload_verifications),
            key=lambda f: (f.finding,
                           _canon(f.subject) if f.subject else "",
                           f.anchor_id or "")))
        draft = dict(
            findings=findings, claim_sets=disclosures,
            participations=tuple(
                BindingSetParticipation(
                    binding_set_id=set_id,
                    revision=resolver.loaded.revision)
                for set_id, resolver in self._resolvers.items()),
            model_revision=self._model.revision,
            resolution_at=resolution_at,
            rules_used=tuple(sorted({
                (rs.rule_id, rs.rule_fingerprint)
                for d in disclosures for rs in d.resolved_subjects})),
            toolchain_fingerprints_used=tuple(sorted({
                rs.toolchain_fingerprint
                for d in disclosures for rs in d.resolved_subjects})),
            required_binding_set_ids=tuple(sorted(self._required)),
            verified_payloads=payload_verifications)

        class _Draft:
            def __init__(self, fields):
                self.__dict__.update(fields)
        digest = compute_inputs_digest(_Draft(draft))
        return StructuralReconciliationResult(**draft,
                                              inputs_digest=digest)

    # -- resolution ----------------------------------------------------
    def _disclose(self, claim_set, resolution_at) -> ClaimSetDisclosure:
        def resolved(claim, rule) -> ResolvedSubject:
            value = apply_rule(rule.body, claim)
            base = dict(
                claim_address=claim.address, rule_id=rule.rule_id,
                rule_fingerprint=rule.fingerprint,
                toolchain_fingerprint=toolchain_fingerprint(
                    claim.address.source.extractor))
            if value is None:
                return ResolvedSubject(**base, subject=None,
                                       no_subject_reason="rule_yielded_none")
            subject = to_source_subject_ref(claim.address, rule, value)
            resolutions = tuple(
                BindingSetResolution(
                    binding_set_id=set_id,
                    resolution=resolver.resolve_subject(
                        subject, at=resolution_at))
                for set_id, resolver in self._resolvers.items())
            bound = sorted({
                r.resolution.resolved_target.anchor_id
                for r in resolutions if r.resolution.status == "bound"})
            return ResolvedSubject(
                **base, subject=subject, resolutions=resolutions,
                join_anchor_id=bound[0] if len(bound) == 1 else None)

        subjects = tuple(
            resolved(claim, rule)
            for claim in claim_set.subject_claims
            for rule in self._rules
            if claim.claim_kind in rule.applies_to)
        ordered = tuple(sorted(
            subjects,
            key=lambda rs: (canonical_locator_value(rs.claim_address.locator),
                            rs.rule_id)))
        return ClaimSetDisclosure(claim_set=claim_set,
                                  resolved_subjects=ordered)

    def _verify_payloads(self, disclosures):
        if self._payloads is None:
            return ()
        cited = {d.claim_set.source_ref.raw_record_id:
                 d.claim_set.source_ref.payload_checksum
                 for d in disclosures}
        return tuple(sorted(
            (PayloadVerification(
                raw_record_id=raw_id,
                supplied_sha256="sha256:" + hashlib.sha256(data).hexdigest(),
                matches_cited=(
                    raw_id in cited
                    and "sha256:" + hashlib.sha256(data).hexdigest()
                    == cited[raw_id]))
             for raw_id, data in self._payloads.items()),
            key=lambda v: v.raw_record_id))

    # -- findings ------------------------------------------------------
    def _generate_findings(self, disclosures, resolution_at,
                           payload_verifications
                           ) -> Iterator[ReconciliationFinding]:
        yield from self._per_subject_findings(disclosures)
        yield from self._anchor_findings(disclosures)
        yield from self._label_findings(disclosures)
        yield from self._derived_path_findings(disclosures)
        yield from self._cross_set_declaration_findings()
        yield from self._required_set_findings()
        yield from self._payload_findings(disclosures,
                                          payload_verifications)
        yield from self._mapping_citation_findings(disclosures,
                                                   resolution_at)

    def _per_subject_findings(self, disclosures):
        for disclosure in disclosures:
            unknown = disclosure.claim_set.engineering_context.kind == \
                "unknown"
            for rs in disclosure.resolved_subjects:
                if rs.subject is None:
                    continue
                bound = tuple(r for r in rs.resolutions
                              if r.resolution.status == "bound")
                anchors = sorted({r.resolution.resolved_target.anchor_id
                                  for r in bound})
                if not anchors:
                    statuses = {r.resolution.status for r in rs.resolutions}
                    if "ambiguous" in statuses:
                        finding, support = "mapping_ambiguous", tuple(
                            r for r in rs.resolutions
                            if r.resolution.status == "ambiguous")
                    elif "conflicted" in statuses:
                        finding, support = "mapping_conflicted", tuple(
                            r for r in rs.resolutions
                            if r.resolution.status == "conflicted")
                    else:
                        finding, support = ("source_subject_unmapped",
                                            rs.resolutions)
                    yield ReconciliationFinding(
                        finding=finding, basis="authority_interpretation",
                        subject=rs.subject,
                        supporting_resolutions=support)
                    continue
                if len(anchors) > 1:
                    yield ReconciliationFinding(
                        finding="mapping_conflicted_across_sets",
                        basis="authority_interpretation",
                        subject=rs.subject, supporting_resolutions=bound)
                    continue
                if len(bound) > 1:
                    yield ReconciliationFinding(
                        finding="subject_bound_in_multiple_sets_consistently",
                        basis="authority_interpretation",
                        subject=rs.subject, anchor_id=anchors[0],
                        supporting_resolutions=bound)
                if unknown:
                    yield ReconciliationFinding(
                        finding="context_unknown",
                        basis="authority_interpretation",
                        subject=rs.subject, anchor_id=anchors[0],
                        supporting_resolutions=bound,
                        detail="the mapping is positively bound but no "
                               "authority declared a reading context for "
                               "this source")

    def _join_index(self, disclosures):
        """The ONLY claim-keyed mapping builder in this package."""
        index: dict = {}
        for disclosure in disclosures:
            for rs in disclosure.resolved_subjects:
                if rs.join_anchor_id is not None:
                    index[rs.join_anchor_id] = (
                        *index.get(rs.join_anchor_id, ()),
                        (disclosure, rs))
        return dict(sorted(index.items()))

    def _member_claim(self, disclosure, rs) -> SourceStructuralClaim:
        value = canonical_locator_value(rs.claim_address.locator)
        for claim in disclosure.claim_set.subject_claims:
            if canonical_locator_value(claim.address.locator) == value:
                return claim
        raise StructuralEvidenceError(  # pragma: no cover - O1 guarantees
            "SN_INTERNAL", "resolved subject without its claim")

    def _quantity_lexeme(self, disclosure, claim) -> str | None:
        field_ref = disclosure.claim_set.quantity_field
        if field_ref is None:
            return None
        for field in claim.fields:
            locator = field.address.locator
            if locator.kind == "csv_cell" and \
                    locator.column_index == field_ref.column_index:
                return field.lexeme if field.lexeme else ""
        return ""

    def _anchor_findings(self, disclosures):
        for anchor_id, members in self._join_index(disclosures).items():
            entity = self._queries.entity(anchor_id)
            revision_id = self._model.revision.revision_id
            member_claims = tuple(self._member_claim(d, rs)
                                  for d, rs in members)
            bound_support = tuple(
                r for _, rs in members for r in rs.resolutions
                if r.resolution.status == "bound")
            if entity.status != "registered":
                yield ReconciliationFinding(
                    finding="anchor_not_registered",
                    basis="accepted_model_record", anchor_id=anchor_id,
                    model_disclosures=(ModelDisclosure(
                        anchor_id=anchor_id, model_revision_id=revision_id,
                        verified="verified_in_supplied_revision"),),
                    detail="searched the supplied revision; no "
                           "registration exists for this anchor")
                continue
            reg_id = entity.registration.record_id
            disclosure_record = ModelDisclosure(
                anchor_id=anchor_id, model_revision_id=revision_id,
                registration_record_id=reg_id,
                verified="verified_in_supplied_revision")
            kinds = {claim.claim_kind for claim in member_claims}
            if {"step_part_definition", "step_nauo_usage"} <= kinds:
                yield ReconciliationFinding(
                    finding="mappings_jointly_incoherent",
                    basis="authority_interpretation", anchor_id=anchor_id,
                    supporting_resolutions=bound_support,
                    detail="one anchor is mapped as both a reusable part "
                           "definition and a particular usage occurrence")
                continue
            declared_views = {
                d.claim_set.engineering_context.view
                for d, _ in members
                if d.claim_set.engineering_context.kind ==
                "declared_lifecycle_view"}
            if len(declared_views) > 1:
                yield ReconciliationFinding(
                    finding="context_incompatible",
                    basis="authority_interpretation", anchor_id=anchor_id,
                    supporting_resolutions=bound_support,
                    detail="the mapped sources declare different lifecycle "
                           "views; corroboration is not asserted across "
                           f"views {sorted(declared_views)}")
            else:
                partial = any(
                    d.claim_set.extraction_outcome == "partial"
                    for d, _ in members)
                families = {_family_of(claim) for claim in member_claims}
                if partial:
                    yield ReconciliationFinding(
                        finding="evidence_incomplete", basis="source_claim",
                        anchor_id=anchor_id,
                        supporting_claims=member_claims,
                        detail="a supporting extraction is partial; "
                               "corroboration is not asserted over "
                               "incomplete evidence")
                elif families == {"bom", "step"}:
                    yield ReconciliationFinding(
                        finding="corroborated_by_all_mapped_sources",
                        basis="accepted_model_record", anchor_id=anchor_id,
                        supporting_claims=member_claims,
                        model_disclosures=(disclosure_record,))
                elif families == {"bom"}:
                    yield ReconciliationFinding(
                        finding="supported_by_bom_only",
                        basis="source_claim", anchor_id=anchor_id,
                        supporting_claims=member_claims)
                else:
                    yield ReconciliationFinding(
                        finding="supported_by_step_only",
                        basis="source_claim", anchor_id=anchor_id,
                        supporting_claims=member_claims)
            yield from self._quantity_findings(
                anchor_id, members, member_claims, disclosure_record)
            yield from self._comparator_findings(anchor_id, members)
            yield from self._absence_findings(anchor_id, members,
                                              member_claims)

    def _quantity_findings(self, anchor_id, members, member_claims,
                           disclosure_record):
        for (disclosure, rs), claim in zip(members, member_claims):
            lexeme = self._quantity_lexeme(disclosure, claim)
            if lexeme is None:
                continue  # this source declares no quantity column
            if lexeme == "":
                yield ReconciliationFinding(
                    finding="evidence_incomplete", basis="source_claim",
                    subject=rs.subject, anchor_id=anchor_id,
                    supporting_claims=(claim,),
                    detail="the declared quantity field is absent or empty")
                continue
            # the join binds exactly one registered canonical anchor, so
            # the registered count is 1 by construction; the comparison is
            # LEXICAL and nothing is numerically normalized
            if lexeme != "1":
                yield ReconciliationFinding(
                    finding=(
                        "quantity_not_reconcilable_with_registered_instances"),
                    basis="accepted_model_record",
                    subject=rs.subject, anchor_id=anchor_id,
                    supporting_claims=(claim,),
                    model_disclosures=(disclosure_record,),
                    detail=f"quantity lexeme {lexeme!r} against 1 "
                           "registered canonical instance; the model has "
                           "no instance-multiplicity representation")

    def _comparator_findings(self, anchor_id, members):
        # C1 over pairs of members from different claim sets
        for left_index in range(len(members)):
            for right_index in range(left_index + 1, len(members)):
                left_d, left_rs = members[left_index]
                right_d, right_rs = members[right_index]
                if left_d is right_d:
                    continue
                left_claim = self._member_claim(left_d, left_rs)
                right_claim = self._member_claim(right_d, right_rs)
                left_operand = self._quantity_lexeme(left_d, left_claim)
                right_operand = self._quantity_lexeme(right_d, right_claim)
                left_operand = left_operand or None
                right_operand = right_operand or None
                comparison = ClaimComparison(
                    comparable="quantity_lexeme",
                    left=ComparisonOperand(subject=left_rs.subject,
                                           address=left_claim.address,
                                           operand=left_operand),
                    right=ComparisonOperand(subject=right_rs.subject,
                                            address=right_claim.address,
                                            operand=right_operand),
                    verdict=("not_comparable"
                             if left_operand is None or right_operand is None
                             else "identical"
                             if left_operand == right_operand
                             else "mutually_contradictory"))
                if comparison.verdict == "mutually_contradictory":
                    yield ReconciliationFinding(
                        finding="claims_mutually_contradictory",
                        basis="source_claim", anchor_id=anchor_id,
                        supporting_claims=(left_claim, right_claim),
                        comparisons=(comparison,))
                elif comparison.verdict == "not_comparable":
                    yield ReconciliationFinding(
                        finding="claims_not_comparable",
                        basis="source_claim", anchor_id=anchor_id,
                        supporting_claims=(left_claim, right_claim),
                        comparisons=(comparison,),
                        detail="no comparator row applies: only an "
                               "authority can reconcile these claim kinds")

    def _absence_findings(self, anchor_id, members, member_claims):
        joined = {anchor_id}
        seen = ()
        for assertion in self._model.assertions.values():
            endpoints = (assertion.source_anchor_id,
                         assertion.target_anchor_id)
            if anchor_id not in endpoints:
                continue
            other = (endpoints[1] if endpoints[0] == anchor_id
                     else endpoints[0])
            if other in joined or other in seen:
                continue
            seen = (*seen, other)
            yield ReconciliationFinding(
                finding="absence_is_not_evidence_of_absence",
                basis="source_claim", anchor_id=other,
                supporting_claims=member_claims,
                detail="the model relates the joined anchor to this "
                       "anchor, which no supplied source supports; absence "
                       "is not evidence of deletion or nonexistence")

    def _label_findings(self, disclosures):
        for disclosure in disclosures:
            claim_set = disclosure.claim_set
            def labels(claim):
                if claim.claim_kind == "bom_row":
                    if claim_set.label_field is None:
                        return ()
                    return tuple(
                        f.lexeme for f in claim.fields
                        if f.address.locator.kind == "csv_cell"
                        and f.address.locator.column_index ==
                        claim_set.label_field.column_index and f.lexeme)
                # a STEP claim's single `name` field is its label
                return tuple(f.lexeme for f in claim.fields
                             if f.field_name_as_extracted == "name"
                             and f.lexeme)
            by_label: dict = {}
            for claim in claim_set.subject_claims:
                for label in labels(claim):
                    by_label[label] = (*by_label.get(label, ()), claim)
            for label in sorted(by_label):
                claims = by_label[label]
                if len(claims) >= 2:
                    yield ReconciliationFinding(
                        finding="duplicate_source_label_not_identity",
                        basis="source_claim", supporting_claims=claims,
                        detail=f"label {label!r} appears on "
                               f"{len(claims)} distinct source subjects; "
                               "a label is never identity")

    def _derived_path_findings(self, disclosures):
        for disclosure in disclosures:
            for path in disclosure.claim_set.derived_paths:
                if path.ambiguity == "unique":
                    continue
                value = canonical_locator_value(path.for_usage)
                support = tuple(
                    claim for claim in disclosure.claim_set.subject_claims
                    if canonical_locator_value(claim.address.locator)
                    == value)
                yield ReconciliationFinding(
                    finding="derived_usage_path_ambiguous",
                    basis="source_claim", supporting_claims=support,
                    detail="the parent definition is used more than once; "
                           "SN-001 reports the ambiguity rather than "
                           "picking a path")

    def _cross_set_declaration_findings(self):
        counts: dict = {}
        for set_id, resolver in self._resolvers.items():
            for declared_id in resolver.loaded.anchors_by_id:
                counts[declared_id] = (*counts.get(declared_id, ()), set_id)
        for declared_id in sorted(counts):
            sets = counts[declared_id]
            if len(sets) >= 2 and re.fullmatch(ENTITY_ANCHOR_ID_PATTERN,
                                               declared_id):
                yield ReconciliationFinding(
                    finding="anchor_declared_in_multiple_sets",
                    basis="authority_interpretation", anchor_id=declared_id,
                    detail="declared in binding sets "
                           f"{sorted(sets)}; reported, never merged")

    def _required_set_findings(self):
        for set_id in sorted(self._required - set(self._resolvers)):
            yield ReconciliationFinding(
                finding="required_binding_set_missing",
                basis="authority_interpretation",
                detail=f"required binding set {set_id!r} was not supplied; "
                       "its subjects are outside this reconciliation")

    def _payload_findings(self, disclosures, payload_verifications):
        if self._payloads is None:
            return
        supplied = {v.raw_record_id: v for v in payload_verifications}
        for disclosure in disclosures:
            source_ref = disclosure.claim_set.source_ref
            claims = disclosure.claim_set.subject_claims
            verification = supplied.get(source_ref.raw_record_id)
            if verification is None:
                yield ReconciliationFinding(
                    finding="evidence_unavailable", basis="source_claim",
                    supporting_claims=claims,
                    detail="the declared payload universe does not contain "
                           "the payload this claim set cites")
            elif not verification.matches_cited:
                yield ReconciliationFinding(
                    finding="cited_payload_checksum_differs",
                    basis="source_claim", supporting_claims=claims,
                    detail=f"cited {source_ref.payload_checksum}; supplied "
                           f"bytes are {verification.supplied_sha256}")

    def _mapping_citation_findings(self, disclosures, resolution_at):
        """sx1-namespaced mappings whose subjects no supplied claim
        produced: the mapping cites structural evidence that is not
        there, or an extractor identity that moved."""
        produced = {}
        for disclosure in disclosures:
            for rs in disclosure.resolved_subjects:
                if rs.subject is not None:
                    produced[(rs.subject.source_id,
                              rs.subject.adapter_id,
                              rs.subject.subject_identifier)] = rs
        produced_by_rule = {
            (source_id, tuple(adapter.split(":")[:4]),
             adapter.split(":")[6]): adapter
            for (source_id, adapter, _) in produced
            if adapter.startswith("sx1:")}
        seen = ()
        for set_id, resolver in sorted(self._resolvers.items()):
            for assertion in resolver.loaded.assertions.values():
                if assertion.binding_kind != "subject":
                    continue
                subject = assertion.subject
                if not subject.adapter_id.startswith("sx1:"):
                    continue
                key = (subject.source_id, subject.adapter_id,
                       subject.subject_identifier)
                if key in produced or key in seen:
                    continue
                seen = (*seen, key)
                parts = subject.adapter_id.split(":")
                rule_key = (subject.source_id, tuple(parts[:4]), parts[6])
                changed = (rule_key in produced_by_rule
                           and produced_by_rule[rule_key]
                           != subject.adapter_id)
                if changed:
                    claims = tuple(
                        self._member_claim(d, rs)
                        for d in disclosures
                        for rs in d.resolved_subjects
                        if rs.subject is not None
                        and rs.subject.source_id == subject.source_id
                        and rs.subject.adapter_id
                        == produced_by_rule[rule_key])
                    yield ReconciliationFinding(
                        finding="extractor_identity_changed",
                        basis="source_claim", subject=subject,
                        supporting_claims=claims,
                        detail="a mapping cites this source under a "
                               "different extractor identity domain — the "
                               "toolchain or configuration moved, the "
                               "authority did not")
                else:
                    yield ReconciliationFinding(
                        finding="cited_extraction_not_found",
                        basis="authority_interpretation", subject=subject,
                        detail=f"binding set {set_id!r} maps this "
                               "structural subject, but no supplied claim "
                               "set produced it")
