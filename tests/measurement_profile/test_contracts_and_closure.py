import hashlib
import json

import pytest

from applications.bounded_decision_workflow.measurement_contracts import (
    PROFILE,
    MeasurementContractError,
    canonical_json_bytes,
    parse_document,
    parse_policy,
    parse_approved_policy,
    resolve_required_closure,
)


def ref(kind, payload):
    return {"kind": kind, "sha256": hashlib.sha256(payload).hexdigest()}


def wire(schema, ident, revision=1, **body):
    value = {"schema": schema, "profile": PROFILE, "id": ident,
             "revision": revision, **body}
    return canonical_json_bytes(value)


def base_objects():
    h = wire("nm.hypothesis.v1", "H1", account_kind="a")
    p = wire("nm.procedure.v1", "P1", method="m")
    s = wire("nm.support.v1", "S1", hypothesis=ref("nm.hypothesis.v1", h),
             procedure=ref("nm.procedure.v1", p))
    q = wire("nm.request.v1", "Q1", hypotheses=[ref("nm.hypothesis.v1", h)],
             measurements=[ref("nm.procedure.v1", p)],
             support=[ref("nm.support.v1", s)], predecessor=None)
    d = wire("nm.declaration.v1", "D1", requests=[ref("nm.request.v1", q)])
    a = wire("nm.selection.v1", "A1", declaration=ref("nm.declaration.v1", d),
             request=ref("nm.request.v1", q))
    policy = open("docs/superpowers/reports/2026-09-19-next-measurement-preparation/resource-policy.json", "rb").read()
    build = wire("nm.build.v1", "B1", status="executable")
    i = wire("nm.invocation.v1", "I1", request=ref("nm.request.v1", q),
             selection=ref("nm.selection.v1", a), adoption=None,
             build_identity=hashlib.sha256(build).hexdigest(),
             resource_policy=hashlib.sha256(policy).hexdigest())
    objects = {
        (kind, digest): payload for kind, payload in (
            ("nm.invocation.v1", i), ("nm.request.v1", q),
            ("nm.selection.v1", a), ("nm.declaration.v1", d),
            ("nm.hypothesis.v1", h), ("nm.procedure.v1", p),
            ("nm.support.v1", s), ("nm.build.v1", build),
            ("nm.resource-policy.v1", policy),
        ) for digest in [hashlib.sha256(payload).hexdigest()]
    }
    return i, objects


def test_canonical_parser_rejects_noncanonical_and_foreign_profile():
    with pytest.raises(MeasurementContractError) as error:
        parse_document(b'{"b":1,"a":2}')
    assert error.value.code == "CANONICAL_FORM_REQUIRED"


def test_policy_is_immutable_and_limits_only_tighten():
    policy = {"schema": "nm.resource-policy.v1", "profile": PROFILE,
              "id": "K1", "revision": 1, "status": "approved",
              "limits": {"unique_objects": 128, "request_chain": 4}}
    parsed = parse_policy(canonical_json_bytes(policy))
    assert parsed.limits["unique_objects"] == 128
    with pytest.raises(MeasurementContractError) as error:
        parse_policy(canonical_json_bytes({**policy, "limits": {"unique_objects": 129}}))
    assert error.value.code == "RESOURCE_POLICY_EXCEEDS_APPROVED"
    exact = open("docs/superpowers/reports/2026-09-19-next-measurement-preparation/resource-policy.json", "rb").read()
    assert parse_approved_policy(exact).limits["unique_objects"] == 128
    with pytest.raises(MeasurementContractError) as error:
        parse_approved_policy(canonical_json_bytes(policy))
    assert error.value.code == "RESOURCE_POLICY_IDENTITY_MISMATCH"


def test_closure_accepts_shared_required_objects_and_rejects_missing_and_cycles():
    invocation, objects = base_objects()
    result = resolve_required_closure(invocation, objects)
    assert result.request_chain == 1
    assert result.reference_occurrences >= len(result.objects)

    missing = dict(objects)
    missing.pop(next(key for key in missing if key[0] == "nm.hypothesis.v1"))
    with pytest.raises(MeasurementContractError) as error:
        resolve_required_closure(invocation, missing)
    assert error.value.code == "REQUIRED_REFERENCE_MISSING"

    cycle = dict(objects)
    qkey = next(key for key in cycle if key[0] == "nm.request.v1")
    q = json.loads(cycle[qkey])
    q["predecessor"] = {"kind": "nm.request.v1", "sha256": qkey[1]}
    cycle[qkey] = canonical_json_bytes(q)
    with pytest.raises(MeasurementContractError) as error:
        resolve_required_closure(invocation, cycle)
    assert error.value.code in {"REFERENCE_DIGEST_MISMATCH", "REFERENCE_CYCLE"}


def test_nominations_reject_duplicate_logical_ids_and_wrong_profile():
    invocation, objects = base_objects()
    qkey = next(key for key in objects if key[0] == "nm.request.v1")
    q = json.loads(objects[qkey])
    q["hypotheses"] = [q["hypotheses"][0], q["hypotheses"][0]]
    new_q = canonical_json_bytes(q)
    new_qref = ref("nm.request.v1", new_q)
    old_qref = {"kind": qkey[0], "sha256": qkey[1]}
    for key, payload in list(objects.items()):
        value = json.loads(payload)
        changed = False
        for field in ("request", "requests"):
            if field in value:
                if isinstance(value[field], list):
                    value[field] = [new_qref if x == old_qref else x for x in value[field]]
                elif value[field] == old_qref:
                    value[field] = new_qref
                changed = True
        if changed:
            replacement = canonical_json_bytes(value)
            objects.pop(key)
            objects[(key[0], hashlib.sha256(replacement).hexdigest())] = replacement
    objects.pop(qkey)
    objects[new_qref["kind"], new_qref["sha256"]] = new_q
    invocation = next(payload for (kind, _), payload in objects.items()
                      if kind == "nm.invocation.v1")
    with pytest.raises(MeasurementContractError) as error:
        resolve_required_closure(invocation, objects)
    assert error.value.code == "DUPLICATE_NOMINATION_REFERENCE"

    invocation, objects = base_objects()
    ikey = next(key for key in objects if key[0] == "nm.invocation.v1")
    bad = json.loads(objects[ikey]); bad["profile"] = "singleton-gamma-beta.v1"
    objects[ikey] = canonical_json_bytes(bad)
    with pytest.raises(MeasurementContractError) as error:
        resolve_required_closure(objects[ikey], objects)
    assert error.value.code == "PROFILE_MISMATCH"


def test_prepared_build_witness_never_confers_production_identity():
    invocation, objects = base_objects()
    bkey = next(key for key in objects if key[0] == "nm.build.v1")
    build = json.loads(objects[bkey]); build["schema"] = "nm.prepared-build.v1"; build["status"] = "prepared_not_executable"
    payload = canonical_json_bytes(build)
    old = bkey
    objects.pop(old)
    objects[("nm.prepared-build.v1", hashlib.sha256(payload).hexdigest())] = payload
    ikey = next(key for key in objects if key[0] == "nm.invocation.v1")
    current = json.loads(objects[ikey]); current["build_identity"] = hashlib.sha256(payload).hexdigest()
    objects[ikey] = canonical_json_bytes(current)
    with pytest.raises(MeasurementContractError) as error:
        resolve_required_closure(objects[ikey], objects)
    assert error.value.code == "NONEXECUTABLE_BUILD_WITNESS"


def test_plus_one_limits_and_history_envelope_refuse_without_truncation():
    invocation, objects = base_objects()
    with pytest.raises(MeasurementContractError) as error:
        resolve_required_closure(invocation, objects, limits={"unique_objects": 1})
    assert error.value.code == "RESOURCE_LIMIT_EXCEEDED"

    # A syntactically complete request declaring revision five is over the
    # approved history envelope even before any ancestor can be squashed.
    qkey = next(key for key in objects if key[0] == "nm.request.v1")
    q = json.loads(objects[qkey]); q["revision"] = 5
    revised = canonical_json_bytes(q)
    qref = ref("nm.request.v1", revised)
    objects.pop(qkey); objects[qref["kind"], qref["sha256"]] = revised
    for key, payload in list(objects.items()):
        value = json.loads(payload)
        changed = False
        for field in ("request", "requests"):
            if field not in value:
                continue
            old = {"kind": qkey[0], "sha256": qkey[1]}
            if isinstance(value[field], list):
                value[field] = [qref if x == old else x for x in value[field]]
            elif value[field] == old:
                value[field] = qref
            changed = True
        if changed:
            replacement = canonical_json_bytes(value)
            objects.pop(key)
            objects[(key[0], hashlib.sha256(replacement).hexdigest())] = replacement
    invocation = next(payload for (kind, _), payload in objects.items()
                      if kind == "nm.invocation.v1")
    with pytest.raises(MeasurementContractError) as error:
        resolve_required_closure(invocation, objects)
    assert error.value.code in {"REQUIRED_REFERENCE_MISSING", "RESOURCE_LIMIT_EXCEEDED"}

    # A non-root revision cannot be accepted with a digest-free predecessor.
    invocation, objects = base_objects()
    qkey = next(key for key in objects if key[0] == "nm.request.v1")
    q = json.loads(objects[qkey]); q["revision"] = 2
    revised = canonical_json_bytes(q); qref = ref("nm.request.v1", revised)
    objects.pop(qkey); objects[qref["kind"], qref["sha256"]] = revised
    invocation_value = json.loads(invocation)
    invocation_value["request"] = qref
    invocation = canonical_json_bytes(invocation_value)
    with pytest.raises(MeasurementContractError) as error:
        resolve_required_closure(invocation, objects)
    assert error.value.code == "REQUIRED_REFERENCE_MISSING"


def test_cross_profile_reference_is_rejected_before_resolution():
    invocation, objects = base_objects()
    ikey = next(key for key in objects if key[0] == "nm.invocation.v1")
    value = json.loads(objects[ikey])
    value["selection"] = value["request"]
    changed = canonical_json_bytes(value)
    with pytest.raises(MeasurementContractError) as error:
        resolve_required_closure(changed, objects)
    assert error.value.code == "REFERENCE_ROLE_MISMATCH"


def test_same_logical_id_different_revision_is_not_silently_collapsed():
    invocation, objects = base_objects()
    hkey = next(key for key in objects if key[0] == "nm.hypothesis.v1")
    original_h = json.loads(objects[hkey])
    revised_h = dict(original_h, revision=2, account_kind="different")
    revised_h_wire = canonical_json_bytes(revised_h)
    revised_h_ref = ref("nm.hypothesis.v1", revised_h_wire)
    objects[revised_h_ref["kind"], revised_h_ref["sha256"]] = revised_h_wire

    qkey = next(key for key in objects if key[0] == "nm.request.v1")
    q = json.loads(objects[qkey])
    q["hypotheses"] = [q["hypotheses"][0], revised_h_ref]
    q_wire = canonical_json_bytes(q)
    old_q_ref = {"kind": qkey[0], "sha256": qkey[1]}
    new_q_ref = ref("nm.request.v1", q_wire)
    objects.pop(qkey)
    objects[new_q_ref["kind"], new_q_ref["sha256"]] = q_wire
    # Rebind the exact request through its declaration, selection and root.
    for key, payload in list(objects.items()):
        value = json.loads(payload)
        changed = False
        for field in ("request", "requests"):
            if field not in value:
                continue
            if isinstance(value[field], list):
                value[field] = [new_q_ref if x == old_q_ref else x for x in value[field]]
                changed = True
            elif value[field] == old_q_ref:
                value[field] = new_q_ref
                changed = True
        if changed:
            replacement = canonical_json_bytes(value)
            objects.pop(key)
            objects[(key[0], hashlib.sha256(replacement).hexdigest())] = replacement
    invocation = next(payload for (kind, _), payload in objects.items()
                      if kind == "nm.invocation.v1")
    with pytest.raises(MeasurementContractError) as error:
        resolve_required_closure(invocation, objects)
    assert error.value.code == "DUPLICATE_NOMINATION_ID"


def test_reference_digest_mismatch_is_distinct_from_missing_content():
    invocation, objects = base_objects()
    ikey = next(key for key in objects if key[0] == "nm.invocation.v1")
    value = json.loads(objects[ikey])
    value["request"]["sha256"] = "0" * 64
    mutated = canonical_json_bytes(value)
    with pytest.raises(MeasurementContractError) as error:
        resolve_required_closure(mutated, objects)
    assert error.value.code == "REQUIRED_REFERENCE_MISSING"

    objects["nm.request.v1", "0" * 64] = objects[next(key for key in objects if key[0] == "nm.request.v1")]
    with pytest.raises(MeasurementContractError) as error:
        resolve_required_closure(mutated, objects)
    assert error.value.code == "REFERENCE_DIGEST_MISMATCH"
