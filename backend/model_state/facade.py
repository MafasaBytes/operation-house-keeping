"""VM-001 bound model-state facade.

Model-variable-first, read-only, composition-only: injected accepted
query objects, public APIs, no stores, no hidden repositories, no state
of its own. One resolver — supplied once — governs reverse discovery AND
every forward resolution, so a discovery/resolution binding-revision
mismatch is unconstructible. Upstream typed errors (ModelKernelError,
IdentityBindingError, TemporalError — including the typed temporal
storage-unavailability error) propagate unchanged; this module never
recognizes storage implementation details.

The pipeline ALWAYS runs for valid input — an unregistered model variable
still gets discovery, querying, and per-occurrence resolution, and its
evidence is returned in identity/model limbo with an honest per-candidate
attachment status. Nothing is suppressed, ranked, aggregated, converted,
or presented as a single current value.
"""

import re
from datetime import UTC, datetime

from pydantic import TypeAdapter, ValidationError

from backend.identity_binding.facade import BoundTemporalQueries
from backend.identity_binding.resolver import BindingResolver
from backend.model_kernel import AssertionContext, LoadedModel, ModelQueries
from backend.model_state.contracts import (
    AssociatedPortVariableStateResult,
    CandidateObservation,
    ModelStateConfigurationError,
    ModelStateQueryError,
    SourceSelector,
    VariableStateResult,
)
from backend.system_identity import (
    ENTITY_ANCHOR_ID_PATTERN,
    PORT_ANCHOR_ID_PATTERN,
    VARIABLE_ANCHOR_ID_PATTERN,
)
from backend.temporal_state.queries import TemporalQueries

_VARIABLE_ID = re.compile(VARIABLE_ANCHOR_ID_PATTERN)
_PORT_ID = re.compile(PORT_ANCHOR_ID_PATTERN)
_ENTITY_ID = re.compile(ENTITY_ANCHOR_ID_PATTERN)
_ASSERTION_CONTEXT = TypeAdapter(AssertionContext)

_DISCOVERY_STATUS = {
    "declared": "declared_candidates",
    "none_declared": "no_declared_candidates",
    "anchor_not_declared": "anchor_unknown_to_binding_set",
}


class ModelStateQueries:
    def __init__(self, model: LoadedModel, resolver: BindingResolver,
                 temporal: TemporalQueries) -> None:
        for value, kind in ((model, LoadedModel),
                            (resolver, BindingResolver),
                            (temporal, TemporalQueries)):
            if not isinstance(value, kind):
                raise ModelStateConfigurationError(
                    "MODEL_STATE_INPUT_INVALID",
                    f"composition requires a {kind.__name__} instance")
        self.model = model
        self.resolver = resolver
        self.bound = BoundTemporalQueries(resolver, temporal)

    # -- input guards ------------------------------------------------------

    def _require_variable_id(self, anchor_id):
        if not isinstance(anchor_id, str) or not _VARIABLE_ID.fullmatch(
                anchor_id):
            raise ModelStateQueryError(
                "MODEL_STATE_INPUT_INVALID",
                f"{anchor_id!r} is not a canonical variable anchor id")
        return anchor_id

    def _require_as_of(self, as_of):
        if not isinstance(as_of, datetime):
            raise ModelStateQueryError(
                "MODEL_STATE_INPUT_INVALID",
                "as_of must be a timezone-aware datetime")
        if as_of.tzinfo is None or as_of.tzinfo.utcoffset(as_of) is None:
            raise ModelStateQueryError(
                "MODEL_STATE_NAIVE_AS_OF",
                "the query cutoff must be a timezone-aware datetime")
        return as_of.astimezone(UTC)

    def _require_port_id(self, anchor_id):
        if not isinstance(anchor_id, str) or not _PORT_ID.fullmatch(anchor_id):
            raise ModelStateQueryError(
                "MODEL_STATE_INPUT_INVALID",
                f"{anchor_id!r} is not a canonical port anchor id")
        return anchor_id

    def _require_context(self, context):
        try:
            payload = (context.model_dump(mode="python", warnings=False)
                       if hasattr(context, "model_dump") else context)
            return _ASSERTION_CONTEXT.validate_python(payload)
        except (ValidationError, ValueError, TypeError, AttributeError,
                KeyError, UnicodeError, Warning) as error:
            raise ModelStateQueryError(
                "MODEL_STATE_INPUT_INVALID",
                "context must be a structurally valid AssertionContext",
            ) from error

    # -- the query ---------------------------------------------------------

    def variable_state(self, variable_anchor_id: str, *,
                       as_of: datetime,
                       entity_anchor_id: str | None = None,
                       source: SourceSelector | None = None,
                       ) -> VariableStateResult:
        variable_anchor_id = self._require_variable_id(variable_anchor_id)
        as_of = self._require_as_of(as_of)
        if entity_anchor_id is not None and (
                not isinstance(entity_anchor_id, str)
                or not _ENTITY_ID.fullmatch(entity_anchor_id)):
            raise ModelStateQueryError(
                "MODEL_STATE_INPUT_INVALID",
                f"{entity_anchor_id!r} is not a canonical entity anchor id")
        if source is not None:
            if not isinstance(source, SourceSelector):
                raise ModelStateQueryError(
                    "MODEL_STATE_INPUT_INVALID",
                    "an explicit source selector must be a SourceSelector")
            try:
                # structural revalidation from field data (kernel
                # precedent): model_construct forgeries never reach the
                # pipeline or surface downstream error codes
                source = SourceSelector.model_validate(
                    source.model_dump(mode="python", warnings=False))
            except (ValidationError, ValueError, TypeError, AttributeError,
                    KeyError, UnicodeError, Warning) as error:
                raise ModelStateQueryError(
                    "MODEL_STATE_INPUT_INVALID",
                    "the source selector is not structurally valid",
                ) from error

        # model membership (never fabricated)
        registration = self.model.variable_registrations_by_anchor.get(
            variable_anchor_id)
        registered = registration is not None
        owner = (self.model.registrations_by_anchor.get(
            registration.anchor.entity_anchor_id) if registered else None)

        # requested entity — disclosure only; never stops the evidence
        if entity_anchor_id is None:
            entity_membership = entity_agreement = "not_supplied"
            entity_registration = None
        else:
            entity_registration = self.model.registrations_by_anchor.get(
                entity_anchor_id)
            entity_membership = ("registered"
                                 if entity_registration is not None
                                 else "not_registered")
            if not registered:
                entity_agreement = "owner_unavailable"
            elif entity_anchor_id == registration.anchor.entity_anchor_id:
                entity_agreement = "matches_owner"
            else:
                entity_agreement = "differs_from_owner"

        # binding-declared anchor and agreement — disclosed, never
        # reconciled
        declared_anchor = self.resolver.loaded.anchors_by_id.get(
            variable_anchor_id)
        divergent_fields = ()
        if not registered:
            agreement = "model_registration_absent"
        elif declared_anchor is None:
            agreement = "binding_declaration_absent"
        else:
            divergent_fields = tuple(sorted(
                name for name in type(declared_anchor).model_fields
                if getattr(declared_anchor, name) != getattr(
                    registration.anchor, name)))
            agreement = "divergent" if divergent_fields else "exact"

        # discovery (always) + candidate construction
        discovery = self.resolver.declared_property_locators(
            variable_anchor_id)
        declared_locator_count = len(discovery.locators)
        if source is None:
            binding_discovery = _DISCOVERY_STATUS[discovery.status]
            selector_declaration = "not_applicable"
            specs = [(entry.subject, entry.property, entry,
                      "declared_binding") for entry in discovery.locators]
        else:
            binding_discovery = "explicit_selector"
            entry = self.resolver.declared_locator(source.subject,
                                                   source.property)
            if entry is None:
                selector_declaration = "undeclared"
            elif any(summary.target_anchor_id == variable_anchor_id
                     for summary in entry.assertion_summaries):
                selector_declaration = "ever_declared_for_requested_variable"
            else:
                selector_declaration = "ever_declared_for_other_variable"
            specs = [(source.subject, source.property, entry,
                      "explicit_selector")]

        candidates = []
        for subject, prop, entry, origin in specs:
            bound = self.bound.latest_observed(subject, prop, as_of)
            declared_via = (tuple(sorted(
                summary.record_id for summary in entry.assertion_summaries
                if summary.target_anchor_id == variable_anchor_id))
                if entry is not None else ())
            candidates.append(CandidateObservation(
                subject=subject, property=prop, origin=origin,
                declaration=entry, declared_via_assertion_ids=declared_via,
                bound=bound,
                attachment=self._attachment(bound, variable_anchor_id,
                                            registered, agreement)))

        bound_any = any(candidate.bound is not None
                        for candidate in candidates)
        availability = ("not_evaluated" if not candidates
                        else "observed" if bound_any
                        else "none_before_cutoff")
        selection = ("explicit" if source is not None
                     else "none" if not candidates
                     else "single" if len(candidates) == 1 else "multiple")

        return VariableStateResult(
            variable_anchor_id=variable_anchor_id, as_of=as_of,
            requested_entity_anchor_id=entity_anchor_id,
            model_membership=("registered" if registered
                              else "not_registered"),
            requested_entity_membership=entity_membership,
            requested_entity_agreement=entity_agreement,
            binding_discovery=binding_discovery,
            selector_declaration=selector_declaration,
            observation_availability=availability, selection=selection,
            variable_registration=registration, owner_registration=owner,
            requested_entity_registration=entity_registration,
            model_revision=self.model.revision,
            binding_revision=self.resolver.loaded.revision,
            binding_declared_anchor=declared_anchor,
            anchor_agreement=agreement,
            divergent_anchor_fields=divergent_fields,
            declared_locator_count=declared_locator_count,
            candidates=tuple(candidates))

    def associated_port_variable_state(
            self, variable_anchor_id, port_anchor_id, *, context, as_of,
            entity_anchor_id=None, source=None,
    ) -> AssociatedPortVariableStateResult:
        """Disclose explicit association beside independent variable state.

        This is composition only.  The observation remains attached to the
        variable by the existing binding/temporal pipeline and is never
        represented as having occurred at or passed through the port.
        """
        variable_anchor_id = self._require_variable_id(variable_anchor_id)
        port_anchor_id = self._require_port_id(port_anchor_id)
        context = self._require_context(context)
        as_of = self._require_as_of(as_of)

        association = ModelQueries(self.model).variable_port_association(
            variable_anchor_id, port_anchor_id, context=context)
        # Always execute the accepted state pipeline for valid composition
        # input.  Association absence, conflict, or inactivity never filters
        # or suppresses temporal evidence.
        variable_state = self.variable_state(
            variable_anchor_id, as_of=as_of,
            entity_anchor_id=entity_anchor_id, source=source)

        if (association.endpoint_status != "both_registered"
                or association.owner_alignment != "same_owner"):
            status = "endpoint_not_admitted"
        elif association.conclusion == "not_declared":
            status = "association_not_declared"
        elif association.conclusion == "inactive":
            status = "association_inactive"
        elif (association.conclusion == "asserted"
              and association.lineage_summary == "conflicted"):
            status = "association_conflicted"
        elif (association.conclusion == "asserted"
              and association.lineage_summary == "healthy"):
            status = "associated"
        else:
            raise ModelStateQueryError(
                "MODEL_STATE_RESULT_INVALID",
                "association returned an impossible lifecycle result")

        return AssociatedPortVariableStateResult(
            variable_anchor_id=variable_anchor_id,
            port_anchor_id=port_anchor_id,
            context=context,
            as_of=as_of,
            status=status,
            association=association,
            variable_state=variable_state,
        )

    @staticmethod
    def _attachment(bound, variable_anchor_id, registered, agreement):
        """Deterministic precedence: identity questions outrank model
        membership; every underlying fact stays independently
        inspectable in the result."""
        if bound is None:
            return "not_evaluated"
        resolution = bound.resolution
        if resolution.status != "bound":
            return "not_attachable_resolution_nonpositive"
        if resolution.resolved_target.anchor_id != variable_anchor_id:
            return "not_attachable_resolution_mismatch"
        if not registered:
            return "not_attachable_variable_unregistered"
        if agreement == "divergent":
            return "not_attachable_anchor_divergent"
        return "attached"
