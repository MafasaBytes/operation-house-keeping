"""BH-001 Slice A canonical bytes, IDs, grammar, and revalidation vectors."""

import re

import pytest
from pydantic import TypeAdapter, ValidationError

import backend.model_kernel as kernel
from backend.model_kernel.canonical import (
    _behavior_effective_body_bytes,
    canonical_bytes,
    verify_record_id,
)
from backend.model_kernel.contracts import MODEL_RECORD_ID_PATTERN

from tests.model_kernel.bh001_slice_a_helpers import (
    AS_DESIGNED,
    BEHAVIOR_A,
    RULE_DECLARATION,
    VAR_A,
    VAR_B,
    behavior_declaration,
    behavior_registration,
    behavior_withdrawal,
    semantic_lock,
)


BRG_ID = "brg_ecd5a9b669f91dca639fde20202ce4f3c4ff17006d7f0ffd23f09ed44f1f9e3e"
BHD_ID = "bhd_9e3af9219521d1b3c5dfd5d41ae359dc8d3fb4c5db4b002586998e52f0a823eb"
BHW_ID = "bhw_4c2456b2a6473f6a37c47b9aadedc10b1a8610c80e6650ba70cdbd7b2dd938f6"

BRG_BYTES = (
    '{"anchor":{"anchor_id":"bhv_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",'
    '"display_name":"Synthetic equality behavior","namespace":'
    '"demo-printer","role_name":null},"authority":{"agent":'
    '"bh001_test_fixture","kind":"test_fixture","method":'
    '"manual_declaration"},"evidence":[{"kind":"model_record",'
    '"record_id":"vrg_6809e209906f8b620096ac4c39f4b4d3291e750b3fd6eba516d620dee5b414bb"},'
    '{"kind":"model_record","record_id":'
    '"vrg_94aec6e0670adfd915a82217b40ca329a4026d4b14b39b290b6eff59da94e3ab"},'
    '{"kind":"owner_declaration","statement":'
    '"Synthetic authority explicitly registers this BH relation."}],'
    '"note":"","participant_variable_anchor_ids":'
    '["var_11111111111111111111111111111111",'
    '"var_22222222222222222222222222222222"],"record_kind":'
    '"behavior_registration","recorded_at":"2026-08-29T12:00:00+00:00",'
    '"rule_family":"exact_numeric_equality","schema_version":"1"}')

BHD_BYTES = (
    '{"authority":{"agent":"bh001_test_fixture","kind":"test_fixture",'
    '"method":"manual_declaration"},"behavior_anchor_id":'
    '"bhv_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","context":{"kind":'
    '"lifecycle_view","view":"as_designed"},"evaluation_basis":'
    '"same_acquisition_cohort","evidence":[{"kind":"model_record",'
    f'"record_id":"{BRG_ID}"}},{{"kind":"owner_declaration",'
    '"statement":"Synthetic authority explicitly declares exact numeric '
    'equality."}],"note":"","participant_semantics":[{"signature":'
    '{"observation_role":{"code":"measured","system_edition":'
    '"ohk-semantics-1","system_id":"project_local"},"quantity_kind":'
    '{"code":"temperature","system_edition":"ohk-semantics-1",'
    '"system_id":"project_local"},"unit":{"code":"degree_celsius",'
    '"system_edition":"ohk-units-1","system_id":"project_local"}},'
    '"variable_anchor_id":"var_11111111111111111111111111111111"},'
    '{"signature":{"observation_role":{"code":"reported",'
    '"system_edition":"ohk-semantics-1","system_id":"project_local"},'
    '"quantity_kind":{"code":"temperature","system_edition":'
    '"ohk-semantics-1","system_id":"project_local"},"unit":{"code":'
    '"degree_celsius","system_edition":"ohk-units-1","system_id":'
    '"project_local"}},"variable_anchor_id":'
    '"var_22222222222222222222222222222222"}],"record_kind":'
    '"behavior_rule_declaration","recorded_at":'
    '"2026-08-29T12:00:00+00:00","rule":{"kind":'
    '"exact_numeric_equality"},"schema_version":"1","supersedes":[]}')

BHW_BYTES = (
    '{"authority":{"agent":"bh001_test_fixture","kind":"test_fixture",'
    '"method":"manual_declaration"},"note":"","record_kind":'
    '"behavior_rule_withdrawal","recorded_at":'
    f'"2026-08-29T13:00:00+00:00","schema_version":"1","withdraws":"{BHD_ID}"}}')


def test_exact_golden_bytes_ids_and_verification():
    registration = behavior_registration()
    declaration = behavior_declaration(registration)
    withdrawal = behavior_withdrawal(declaration)
    assert (registration.record_id, canonical_bytes(registration).decode()) == (
        BRG_ID, BRG_BYTES)
    assert (declaration.record_id, canonical_bytes(declaration).decode()) == (
        BHD_ID, BHD_BYTES)
    assert (withdrawal.record_id, canonical_bytes(withdrawal).decode()) == (
        BHW_ID, BHW_BYTES)
    assert all(verify_record_id(record)
               for record in (registration, declaration, withdrawal))


def test_record_and_filename_grammar_accept_only_exact_behavior_prefixes():
    for prefix in ("brg", "bhd", "bhw"):
        assert re.fullmatch(MODEL_RECORD_ID_PATTERN, prefix + "_" + "a" * 64)
    for malformed in (
        "BHD_" + "a" * 64,
        "bh_" + "a" * 64,
        "bhr_" + "a" * 64,
        "bhd_" + "A" * 64,
        "bhd_" + "a" * 63,
        "bhd_" + "a" * 65,
    ):
        assert not re.fullmatch(MODEL_RECORD_ID_PATTERN, malformed)


def test_participant_lock_evidence_and_parent_permutations_have_one_identity():
    registration = behavior_registration(participants=(VAR_B, VAR_A))
    root = behavior_declaration(registration, note="root")
    other = behavior_declaration(registration, note="other root")
    locks = (semantic_lock(VAR_B, role="reported"), semantic_lock(VAR_A))
    extra = RULE_DECLARATION.model_copy(update={"statement": "extra support"})
    evidence = (
        kernel.ModelRecordEvidence(
            kind="model_record", record_id=registration.record_id),
        RULE_DECLARATION,
        extra,
    )
    forward = behavior_declaration(
        registration, locks=locks, evidence=evidence,
        supersedes=(root.record_id, other.record_id), note="merge")
    reverse = behavior_declaration(
        registration, locks=tuple(reversed(locks)),
        evidence=tuple(reversed(evidence)),
        supersedes=(other.record_id, root.record_id), note="merge")
    assert forward.record_id == reverse.record_id
    assert canonical_bytes(forward) == canonical_bytes(reverse)


def test_every_engineering_and_audit_field_changes_record_identity():
    registration = behavior_registration()
    base = behavior_declaration(registration)
    variants = (
        behavior_declaration(registration, behavior_anchor_id="bhv_" + "b" * 32),
        behavior_declaration(registration, context={
            "kind": "lifecycle_view", "view": "as_built"}),
        behavior_declaration(registration, locks=(
            semantic_lock(VAR_A), semantic_lock(VAR_B, role="estimated"))),
        behavior_declaration(registration, note="audit note changed"),
        behavior_declaration(registration, evidence=(
            kernel.ModelRecordEvidence(
                kind="model_record", record_id=registration.record_id),
            RULE_DECLARATION.model_copy(update={"statement": "new basis"}),
        )),
    )
    assert all(item.record_id != base.record_id for item in variants)


def test_stale_ids_and_kind_prefix_substitution_fail_at_authoritative_boundaries():
    adapter = TypeAdapter(kernel.ModelRecord)
    valid = behavior_declaration()
    stale = adapter.validate_python({
        **valid.model_dump(), "record_id": "bhd_" + "0" * 64})
    assert verify_record_id(stale) is False
    for attack in (
        {**valid.model_dump(), "record_id": "bhw_" + "0" * 64},
        {**valid.model_dump(), "record_kind": "behavior_rule_withdrawal"},
    ):
        with pytest.raises(ValidationError):
            adapter.validate_python(attack)


def test_nested_construct_and_copy_forgery_is_reconstructed_not_trusted():
    adapter = TypeAdapter(kernel.ModelRecord)
    valid = behavior_declaration()
    hostile_context = AS_DESIGNED.model_copy(update={"view": "future_view"})
    hostile_signature = valid.participant_semantics[0].signature.model_copy(
        update={"unit": valid.participant_semantics[0].signature.unit.model_copy(
            update={"code": ""})})
    hostile_lock = valid.participant_semantics[0].model_copy(
        update={"signature": hostile_signature})
    hostile_rule = valid.rule.model_construct(kind="affine")
    hostile_evidence = RULE_DECLARATION.model_copy(update={"statement": ""})
    hostile_authority = valid.authority.model_copy(update={"kind": "future"})
    for forged in (
        valid.model_copy(update={"context": hostile_context}),
        valid.model_copy(update={
            "participant_semantics": (
                hostile_lock, valid.participant_semantics[1])}),
        valid.model_copy(update={"rule": hostile_rule}),
        valid.model_copy(update={"evidence": (hostile_evidence,)}),
        valid.model_copy(update={"authority": hostile_authority}),
    ):
        with pytest.raises(ValidationError):
            adapter.validate_python(forged)


def test_self_id_is_excluded_only_from_its_own_hash():
    registration = behavior_registration()
    declaration = behavior_declaration(registration)
    assert registration.record_id.encode() in canonical_bytes(declaration)
    assert declaration.record_id.encode() not in canonical_bytes(declaration)


def test_effective_engineering_body_is_exact_private_canonical_projection():
    registration = behavior_registration()
    first = behavior_declaration(registration, note="authority one")
    second = behavior_declaration(
        registration, recorded_at=first.recorded_at.replace(hour=13),
        note="authority two")
    expected = {
        "behavior_anchor_id", "context", "participant_semantics", "rule",
        "evaluation_basis",
    }
    import json

    assert set(json.loads(_behavior_effective_body_bytes(first))) == expected
    assert _behavior_effective_body_bytes(first) == (
        _behavior_effective_body_bytes(second))
    changed = behavior_declaration(registration, locks=(
        semantic_lock(VAR_A, role="estimated"),
        semantic_lock(VAR_B, role="reported")))
    assert _behavior_effective_body_bytes(first) != (
        _behavior_effective_body_bytes(changed))
