"""Slice 2: measurement evidence and authority admission.

This adapter stops at permission and applicability.  It does not qualify
support, evaluate predictions, rank procedures, dispatch measurements, or
publish a result.
"""

from dataclasses import dataclass
import json

from .admission import admit_request_and_snapshot
from .measurement_contracts import resolve_required_closure


class MeasurementAdmissionError(ValueError):
    def __init__(self, code, *, target, reasons=()):
        super().__init__(code)
        self.code = code
        self.target = target
        self.reasons = tuple(reasons)


@dataclass(frozen=True, slots=True)
class ProcedureApplicability:
    procedure_id: str
    state: str
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MeasurementAdmission:
    permission: bool
    authority_state: str
    evidence_state: str
    current_condition: str
    observed_value: str
    procedures: tuple[ProcedureApplicability, ...]
    hypotheses: tuple[str, ...]
    downstream_work: bool
    reasons: tuple[str, ...]


def assess_procedure(procedure):
    """Assess only declared applicability conditions; no prediction work."""
    states = {item["id"]: item["state"] for item in procedure.get("conditions", ())}
    reasons = tuple(f"{name}_{states.get(name, 'missing')}"
                    for name in ("applicability", "availability", "calibration", "fidelity", "hold")
                    if states.get(name) != "true")
    return ProcedureApplicability(
        procedure_id=procedure["id"],
        state="applicable" if not reasons else "inapplicable",
        reasons=reasons)


def _payload(result, ref):
    key = (ref["kind"], ref["sha256"])
    try:
        return json.loads(result.objects[key])
    except KeyError as error:
        raise MeasurementAdmissionError("REQUIRED_REFERENCE_MISSING", target=key) from error


def admit_measurement(
        invocation_wire, objects, *, authority_pin, public_request_wire,
        public_snapshot_wire):
    """Admit public evidence and D/A/T permission for one closed invocation."""
    closure = resolve_required_closure(invocation_wire, objects,
                                      authority_pin=authority_pin)
    invocation = json.loads(invocation_wire)
    request = _payload(closure, invocation["request"])
    selection = _payload(closure, invocation["selection"])
    declaration = _payload(closure, selection["declaration"])

    # Public reconstruction is the maintained authority for observed inputs.
    public = admit_request_and_snapshot(public_request_wire, public_snapshot_wire)
    current = public.current_condition.disposition
    observed = public.observed_value.status
    if current == "unavailable":
        return MeasurementAdmission(
            permission=False, authority_state="not_evaluated",
            evidence_state="baseline_unavailable", current_condition=current,
            observed_value=observed, procedures=(), hypotheses=(),
            downstream_work=False, reasons=("baseline_unavailable",))

    if current not in {"true", "false"} or observed not in {"admitted", "unavailable"}:
        return MeasurementAdmission(
            permission=False, authority_state="not_evaluated",
            evidence_state="evidence_not_assessable", current_condition=current,
            observed_value=observed, procedures=(), hypotheses=(),
            downstream_work=False, reasons=("evidence_not_assessable",))

    expected = request["context"]
    question = public.request.current_condition_question
    public_context = {
        "as_of": question.as_of.isoformat().replace("+00:00", "Z"),
        "assertion_context": question.assertion_context.model_dump(mode="json"),
    }
    if expected["as_of"] != public_context["as_of"] or expected["assertion_context"] != public_context["assertion_context"]:
        raise MeasurementAdmissionError("EVIDENCE_JOIN_MISMATCH", target="context")

    authority_reasons = []
    if declaration.get("scope_state") != "true":
        authority_reasons.append("declaration_scope_false")
    if selection.get("purpose") != "hypothetical_evaluation":
        authority_reasons.append("selection_purpose_inapplicable")
    permission = not authority_reasons
    if not permission:
        return MeasurementAdmission(
            permission=False, authority_state="denied", evidence_state="admitted",
            current_condition=current, observed_value=observed, procedures=(),
            hypotheses=(), downstream_work=False, reasons=tuple(authority_reasons))

    procedures = []
    for ref in request["measurements"]:
        procedure = _payload(closure, ref)
        procedures.append(assess_procedure(procedure))

    hypotheses = tuple(_payload(closure, ref)["id"] for ref in request["hypotheses"])
    return MeasurementAdmission(
        permission=permission, authority_state="permitted" if permission else "denied",
        evidence_state="admitted", current_condition=current,
        observed_value=observed, procedures=tuple(procedures), hypotheses=hypotheses,
        downstream_work=permission, reasons=tuple(authority_reasons))
