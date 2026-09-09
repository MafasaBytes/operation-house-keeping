"""FC-001 exact retained closure and membership-relative lifecycle admission."""

import json
from types import MappingProxyType

import pytest

import backend.model_kernel as kernel
from backend.model_kernel.store import revalidate, validate_record_collection
from tests.model_kernel.builders import CON_B, VAR_B, variable_registration
from tests.model_kernel.fc001_slice_a_helpers import (
    declaration, membership, replace, withdrawal, world,
)
from tests.model_kernel.test_flow_measurement_slice_a import (
    withdrawal as fm_withdrawal,
)
from tests.model_kernel.fl001_slice_a_helpers import VIEW_INDEPENDENT


INDEX_NAMES = (
    "declarations", "withdrawals", "subject_by_id", "ids_by_subject",
    "parent_ids", "successor_ids", "root_by_id", "ancestry_by_id",
    "current_tips_by_root", "withdrawn_by", "effective_body_by_id",
    "ids_by_effective_body",
)


def load(*records, verify_hashes=True):
    return validate_record_collection(
        "fc001-disposable", membership(*records), verify_hashes=verify_hashes)


def index(loaded, name):
    return getattr(loaded, "flow_operating_criterion_" + name)


def reject(records, code, **kwargs):
    with pytest.raises(kernel.ModelIntegrityError) as caught:
        load(*records, **kwargs)
    assert caught.value.error_code == code


@pytest.mark.parametrize("orientation", [
    "aligned", "opposite", "unsigned_magnitude", "not_applicable"])
@pytest.mark.parametrize("context", [None, VIEW_INDEPENDENT], ids=["as_designed", "view_independent"])
@pytest.mark.parametrize("participant", ["source", "sink"])
def test_exact_subject_body_and_immutable_indexes(orientation, context, participant):
    records, witness, crg, vcn = world(orientation=orientation, context=context, participant=participant)
    d = declaration(witness, crg, vcn)
    supplied = membership(*records, d)
    loaded = validate_record_collection("fc001-disposable", supplied)
    supplied.clear()
    subject = (witness.flow_anchor_id, witness.variable_anchor_id,
               witness.participant_port_anchor_id, witness.context,
               "direct_measurement_relevance", orientation)
    assert index(loaded, "subject_by_id")[d.record_id] == subject
    assert index(loaded, "ids_by_subject")[subject] == (d.record_id,)
    assert index(loaded, "current_tips_by_root") == {d.record_id: (d.record_id,)}
    assert index(loaded, "ancestry_by_id")[d.record_id] == ()
    assert loaded.flow_measurement_participant_role_by_id[witness.record_id] == participant
    body = json.loads(index(loaded, "effective_body_by_id")[d.record_id])
    fm = body["flow_measurement_body"]
    assert fm["orientation"] == orientation
    assert fm["flow_declaration_record_id"] == witness.flow_declaration_record_id
    assert set(body) == {"flow_measurement_body", "constraint_registration_record_id",
                         "constraint_declaration_record_id"}
    assert body["constraint_declaration_record_id"] == vcn.record_id
    assert body["constraint_registration_record_id"] == crg.record_id
    assert "record_id" not in fm
    for name in INDEX_NAMES:
        mapping = index(loaded, name)
        assert isinstance(mapping, MappingProxyType)
        with pytest.raises(TypeError):
            mapping["forged"] = ()


@pytest.mark.parametrize("missing", ["witness", "crg", "vcn"])
def test_exact_missing_direct_support_rejects(missing):
    records, witness, crg, vcn = world()
    d = declaration(witness, crg, vcn)
    removed = {"witness": witness, "crg": crg, "vcn": vcn}[missing]
    reject([r for r in (*records, d) if r != removed], "MODEL_REFERENCE_INVALID")


@pytest.mark.parametrize("pin", [
    "flow_registration_record_id", "variable_registration_record_id",
    "port_registration_record_id", "flow_declaration_record_id",
    "variable_port_association_record_id", "variable_semantic_declaration_record_id",
])
def test_each_witness_support_pin_must_be_retained(pin):
    records, witness, crg, vcn = world()
    d = declaration(witness, crg, vcn)
    reject([r for r in (*records, d) if r.record_id != getattr(witness, pin)],
           "MODEL_REFERENCE_INVALID")


def test_constraint_variable_must_equal_subject():
    records, witness, crg, vcn = world()
    bad = replace(crg, variable_anchor_id=VAR_B)
    d = declaration(witness, bad, vcn)
    reject([*(r for r in records if r != crg), variable_registration(VAR_B), bad, d],
           "MODEL_FLOW_CRITERION_SUPPORT_INVALID")


def test_constraint_anchor_must_equal_exact_registration():
    records, witness, crg, vcn = world()
    other = replace(crg, anchor={**crg.anchor.model_dump(), "anchor_id": CON_B})
    other_vcn = replace(vcn, constraint_anchor_id=CON_B)
    d = declaration(witness, crg, other_vcn)
    reject([*records, other, other_vcn, d], "MODEL_FLOW_CRITERION_SUPPORT_INVALID")


@pytest.mark.parametrize("field,value", [
    ("system_edition", "other"), ("code", "measured"),
])
def test_full_expected_observation_role_must_equal_pinned_measured_actual(field, value):
    records, witness, crg, vcn = world()
    semantics = vcn.expected_semantics.model_dump()
    semantics["observation_role"][field] = value
    bad = replace(vcn, expected_semantics=semantics)
    d = declaration(witness, crg, bad)
    reject([*(r for r in records if r != vcn), bad, d],
           "MODEL_FLOW_CRITERION_SEMANTIC_INVALID")


def test_witness_sensitive_records_have_equal_effective_bodies():
    records, witness, crg, vcn = world()
    second = replace(witness, note="Independent authority provenance")
    a, b = declaration(witness, crg, vcn), declaration(second, crg, vcn)
    loaded = load(*records, second, a, b)
    assert a.record_id != b.record_id
    bodies = index(loaded, "effective_body_by_id")
    assert bodies[a.record_id] == bodies[b.record_id]
    assert index(loaded, "ids_by_effective_body")[bodies[a.record_id]] == tuple(sorted((a.record_id, b.record_id)))
    assert len(index(loaded, "current_tips_by_root")) == 2


@pytest.mark.parametrize("history", ["witness_withdrawal", "witness_correction", "vcn_correction", "vcn_conflict"])
def test_historical_support_loads_without_floating(history):
    records, witness, crg, vcn = world()
    d = declaration(witness, crg, vcn)
    if history == "witness_withdrawal":
        extra = [fm_withdrawal(witness)]
    elif history == "witness_correction":
        extra = [replace(witness, supersedes=(witness.record_id,), note="renewed")]
    else:
        extra = [replace(vcn, supersedes=(vcn.record_id,), note="renewed")]
        if history == "vcn_conflict":
            extra.append(replace(vcn, supersedes=(vcn.record_id,), note="other branch"))
    loaded = load(*records, d, *extra)
    retained = index(loaded, "declarations")[d.record_id]
    assert retained.flow_measurement_association_record_id == witness.record_id
    assert retained.constraint_declaration_record_id == vcn.record_id
    assert index(loaded, "current_tips_by_root")[d.record_id] == (d.record_id,)


def test_equal_body_does_not_replace_missing_witness():
    records, witness, crg, vcn = world()
    equal = replace(witness, note="equal independent replacement")
    d = declaration(witness, crg, vcn)
    reject([*(r for r in records if r != witness), equal, d], "MODEL_REFERENCE_INVALID")


def test_forks_partial_correction_convergence_and_selective_withdrawal():
    records, witness, crg, vcn = world()
    root = declaration(witness, crg, vcn)
    a = replace(root, supersedes=(root.record_id,), note="a")
    b = replace(root, supersedes=(root.record_id,), note="b")
    forked = load(*records, root, a, b)
    assert index(forked, "current_tips_by_root")[root.record_id] == tuple(sorted((a.record_id, b.record_id)))
    partial = replace(a, supersedes=(a.record_id,), note="partial")
    loaded = load(*records, root, a, b, partial)
    assert index(loaded, "current_tips_by_root")[root.record_id] == tuple(sorted((b.record_id, partial.record_id)))
    converged = replace(a, supersedes=(b.record_id, partial.record_id), note="converged")
    loaded = load(*records, root, a, b, partial, converged)
    assert index(loaded, "current_tips_by_root")[root.record_id] == (converged.record_id,)
    assert index(loaded, "ancestry_by_id")[converged.record_id] == tuple(sorted((root.record_id, a.record_id, b.record_id, partial.record_id)))
    withdrawn = load(*records, root, a, b, withdrawal(a))
    assert index(withdrawn, "current_tips_by_root")[root.record_id] == (b.record_id,)


def test_inactive_disagreeing_root_retains_body_and_new_assertion_is_new_root():
    records, witness, crg, vcn = world()
    root = declaration(witness, crg, vcn)
    v2 = replace(vcn, supersedes=(vcn.record_id,), note="edition2")
    other = declaration(witness, crg, v2)
    w = withdrawal(root)
    loaded = load(*records, v2, root, other, w)
    assert index(loaded, "current_tips_by_root") == {root.record_id: (), other.record_id: (other.record_id,)}
    assert len(index(loaded, "ids_by_effective_body")) == 2
    assert index(loaded, "withdrawn_by")[root.record_id] == (w.record_id,)


@pytest.mark.parametrize("violation", ["cross_root", "cross_subject", "missing_parent"])
def test_invalid_parent_relations(violation):
    records, witness, crg, vcn = world()
    root = declaration(witness, crg, vcn)
    other = replace(root, note="independent")
    extra = [root, other]
    code = "MODEL_FLOW_CRITERION_LINEAGE_INVALID"
    if violation == "cross_root":
        child = replace(root, supersedes=(root.record_id, other.record_id))
    elif violation == "cross_subject":
        changed = replace(witness, orientation="opposite")
        extra.append(changed)
        child = declaration(changed, crg, vcn, supersedes=(root.record_id,))
    else:
        child = replace(root, supersedes=("fcd_" + "9" * 64,))
        code = "MODEL_REFERENCE_INVALID"
    reject([*records, *extra, child], code)


@pytest.mark.parametrize("violation", ["missing", "duplicate", "superseded", "withdrawn_parent"])
def test_invalid_withdrawals(violation):
    records, witness, crg, vcn = world()
    root = declaration(witness, crg, vcn)
    w = withdrawal(root)
    extra = [root, w]
    code = "MODEL_FLOW_CRITERION_WITHDRAWAL_INVALID"
    if violation == "missing":
        extra = [w]
        code = "MODEL_REFERENCE_INVALID"
    elif violation == "duplicate":
        extra.append(withdrawal(root, note="second"))
    else:
        extra.append(replace(root, supersedes=(root.record_id,), note="successor"))
        if violation == "withdrawn_parent":
            extra.reverse()
    reject([*records, *extra], code)


def test_evidence_closes_and_historical_citation_remains_citable():
    records, witness, crg, vcn = world()
    root = declaration(witness, crg, vcn)
    successor = replace(root, supersedes=(root.record_id,), note="successor")
    cited = declaration(witness, crg, vcn, evidence=(kernel.ModelRecordEvidence(kind="model_record", record_id=root.record_id),))
    loaded = load(*records, root, successor, cited)
    assert cited.record_id in index(loaded, "declarations")
    reject([*records, cited], "MODEL_REFERENCE_INVALID")


@pytest.mark.parametrize("mutation,code", [("hash", "MODEL_RECORD_HASH_MISMATCH"), ("extra", "MODEL_RECORD_INVALID"), ("limit", "MODEL_FLOW_CRITERION_RECORD_LIMIT_EXCEEDED")])
def test_forged_full_instances_reject(mutation, code):
    records, witness, crg, vcn = world()
    root = declaration(witness, crg, vcn)
    update = {"note": "stale"} if mutation == "hash" else {"extra": True} if mutation == "extra" else {"note": "x" * 8193}
    reject([*records, root.model_copy(update=update)], code)


def test_hostile_fc_subclass_rejects_before_dump_callback():
    records, witness, crg, vcn = world()
    root = declaration(witness, crg, vcn)
    calls = []
    class Hostile(kernel.FlowOperatingCriterionDeclaration):
        def model_dump(self, **kwargs):
            calls.append("dump")
            return root.model_dump()
    forged = Hostile.model_construct(**root.model_dump())
    with pytest.raises(kernel.ModelIntegrityError) as caught:
        revalidate(forged)
    assert caught.value.error_code == "MODEL_RECORD_INVALID"
    assert calls == []


def test_store_roundtrip_replay_and_atomic_failed_append(tmp_path):
    records, witness, crg, vcn = world()
    d = declaration(witness, crg, vcn)
    store = kernel.ModelStore(tmp_path / "fc001-disposable")
    for r in (*records, d):
        store.append(r)
    baseline = store.load()
    w = withdrawal(d)
    store.append(w)
    assert index(store.load(), "current_tips_by_root")[d.record_id] == ()
    assert store.replay(baseline.revision.record_ids).revision == baseline.revision
    before = {p.name: p.read_bytes() for p in store.records_dir.iterdir()}
    with pytest.raises(kernel.ModelIntegrityError) as caught:
        store.append(replace(d, supersedes=(d.record_id,), note="illegal"))
    assert caught.value.error_code == "MODEL_FLOW_CRITERION_WITHDRAWAL_INVALID"
    assert before == {p.name: p.read_bytes() for p in store.records_dir.iterdir()}
    assert not list(store.staging_dir.iterdir())
    with pytest.raises(kernel.ModelIntegrityError) as caught:
        store.replay(tuple(r for r in baseline.revision.record_ids if r != witness.record_id))
    assert caught.value.error_code == "MODEL_REFERENCE_INVALID"


@pytest.mark.parametrize("raw,code", [(b" " * 1048577, "MODEL_FLOW_CRITERION_RECORD_LIMIT_EXCEEDED"), (b'{"record_kind":"a","record_kind":"b"}', "MODEL_RECORD_INVALID"), (b"[" * 34 + b"]" * 34, "MODEL_FLOW_CRITERION_RECORD_LIMIT_EXCEEDED")], ids=["raw_cap", "duplicate_key", "json_depth"])
def test_new_prefix_json_is_bounded_before_adapter(tmp_path, raw, code):
    store = kernel.ModelStore(tmp_path / "fc001-disposable")
    (store.records_dir / ("fcd_" + "a" * 64 + ".json")).write_bytes(raw)
    with pytest.raises(kernel.ModelIntegrityError) as caught:
        store.load()
    assert caught.value.error_code == code


def test_duck_typed_fc_record_rejects_before_any_callback():
    _, witness, crg, vcn = world()
    root = declaration(witness, crg, vcn)
    calls = []
    class Forged:
        def model_dump(self, **kwargs):
            calls.append("dump")
            return root.model_dump()
    with pytest.raises(kernel.ModelIntegrityError) as caught:
        revalidate(Forged())
    assert caught.value.error_code == "MODEL_RECORD_INVALID"
    assert calls == []


@pytest.mark.parametrize("prefix", ["fcd", "fcw"])
def test_file_kind_and_filename_must_bind_exactly(tmp_path, prefix):
    _, witness, crg, vcn = world()
    root = declaration(witness, crg, vcn)
    wrong = withdrawal(root) if prefix == "fcd" else root
    store = kernel.ModelStore(tmp_path / "fc001-disposable")
    (store.records_dir / (prefix + "_" + "a" * 64 + ".json")).write_text(wrong.model_dump_json())
    with pytest.raises(kernel.ModelIntegrityError) as caught:
        store.load()
    assert caught.value.error_code == "MODEL_RECORD_HASH_MISMATCH"


@pytest.mark.parametrize("family", ["fld", "vpa", "vsm", "pcn", "pif"])
def test_historical_typed_support_is_retained_after_correction(family):
    records, witness, crg, vcn = world()
    d = declaration(witness, crg, vcn)
    target = next(r for r in records if r.record_id.startswith(family + "_"))
    correction = replace(target, supersedes=(target.record_id,), note="historical support renewal")
    loaded = load(*records, d, correction)
    assert index(loaded, "declarations")[d.record_id] == d
    assert index(loaded, "current_tips_by_root")[d.record_id] == (d.record_id,)
    reject([*(r for r in records if r != target), d, correction], "MODEL_REFERENCE_INVALID")


@pytest.mark.parametrize("family,withdrawal_class", [
    ("fld", kernel.FlowDeclarationWithdrawal),
    ("vpa", kernel.VariablePortAssociationWithdrawal),
    ("pcn", kernel.PortClaimWithdrawal),
    ("pif", kernel.PortClaimWithdrawal),
])
def test_withdrawn_selected_typed_support_remains_structurally_admissible(family, withdrawal_class):
    records, witness, crg, vcn = world()
    d = declaration(witness, crg, vcn)
    target = next(r for r in records if r.record_id.startswith(family + "_"))
    w = kernel.build_record(withdrawal_class, withdraws=target.record_id,
                            recorded_at=d.recorded_at, authority=d.authority)
    loaded = load(*records, d, w)
    assert index(loaded, "current_tips_by_root")[d.record_id] == (d.record_id,)


@pytest.mark.parametrize("family", ["pcn", "pif"])
def test_missing_selected_transitive_support_rejects(family):
    records, witness, crg, vcn = world()
    d = declaration(witness, crg, vcn)
    removed = next(r for r in records if r.record_id.startswith(family + "_"))
    reject([*(r for r in records if r != removed), d], "MODEL_REFERENCE_INVALID")


def test_incompatible_quantity_and_unit_do_not_invent_fc_evaluation():
    records, witness, crg, vcn = world()
    semantics = vcn.expected_semantics.model_dump()
    semantics["quantity_kind"]["code"] = "unspecified_other_quantity"
    semantics["unit"]["code"] = "unspecified_other_unit"
    other = replace(vcn, expected_semantics=semantics)
    d = declaration(witness, crg, other)
    loaded = load(*(r for r in records if r != vcn), other, d)
    assert index(loaded, "declarations")[d.record_id] == d


def test_cycle_rejects_with_hash_checks_disabled_for_structural_probe():
    records, witness, crg, vcn = world()
    a = declaration(witness, crg, vcn)
    b = replace(a, note="b")
    a = a.model_copy(update={"supersedes": (b.record_id,)})
    b = b.model_copy(update={"supersedes": (a.record_id,)})
    reject([*records, a, b], "MODEL_FLOW_CRITERION_LINEAGE_INVALID", verify_hashes=False)


def test_record_order_does_not_change_any_fc_mapping():
    records, witness, crg, vcn = world()
    a = declaration(witness, crg, vcn)
    b = replace(a, supersedes=(a.record_id,), note="b")
    c = replace(a, supersedes=(a.record_id,), note="c")
    whole = (*records, a, b, c, withdrawal(b))
    forward, reverse = load(*whole), load(*reversed(whole))
    assert forward.revision == reverse.revision
    for name in INDEX_NAMES:
        assert index(forward, name) == index(reverse, name)


def test_replay_retains_withdrawn_witness_and_rejects_omission_with_equal_body(tmp_path):
    records, witness, crg, vcn = world()
    equal = replace(witness, note="independent equal witness")
    d = declaration(witness, crg, vcn)
    store = kernel.ModelStore(tmp_path / "fc001-disposable")
    for record in (*records, equal, d, fm_withdrawal(witness)):
        store.append(record)
    loaded = store.load()
    replayed = store.replay(loaded.revision.record_ids)
    assert replayed.revision == loaded.revision
    assert index(replayed, "declarations")[d.record_id].flow_measurement_association_record_id == witness.record_id
    omitted = [r for r in loaded.revision.record_ids if r != witness.record_id and not r.startswith("fmw_")]
    with pytest.raises(kernel.ModelIntegrityError) as caught:
        store.replay(omitted)
    assert caught.value.error_code == "MODEL_REFERENCE_INVALID"


def test_idempotent_append_revalidates_corrupted_sibling_without_staging(tmp_path):
    records, witness, crg, vcn = world()
    d = declaration(witness, crg, vcn)
    store = kernel.ModelStore(tmp_path / "fc001-disposable")
    for record in (*records, d):
        store.append(record)
    assert store.append(d) == d.record_id
    sibling = store.records_dir / (vcn.record_id + ".json")
    payload = json.loads(sibling.read_text())
    payload["note"] = "tampered sibling"
    sibling.write_text(json.dumps(payload))
    before = {p.name: p.read_bytes() for p in store.records_dir.iterdir()}
    with pytest.raises(kernel.ModelIntegrityError) as caught:
        store.append(d)
    assert caught.value.error_code == "MODEL_RECORD_HASH_MISMATCH"
    assert before == {p.name: p.read_bytes() for p in store.records_dir.iterdir()}
    assert not list(store.staging_dir.iterdir())


def test_subject_index_enumerates_exact_orientation_rank():
    records, witness, crg, vcn = world()
    orientations = ("aligned", "opposite", "unsigned_magnitude", "not_applicable")
    additions = []
    for orientation in orientations:
        oriented = replace(witness, orientation=orientation)
        additions.extend((oriented, declaration(oriented, crg, vcn)))
    loaded = load(*records, *additions)
    assert tuple(subject[-1] for subject in index(loaded, "ids_by_subject")) == orientations


def test_all_fc_mapping_enumeration_is_independent_of_input_order():
    records, witness, crg, vcn = world()
    a = declaration(witness, crg, vcn)
    b = replace(a, supersedes=(a.record_id,), note="b")
    c = replace(a, supersedes=(a.record_id,), note="c")
    whole = (*records, a, b, c)
    forward, reverse = load(*whole), load(*reversed(whole))
    for name in INDEX_NAMES:
        assert tuple(index(forward, name).items()) == tuple(index(reverse, name).items())


@pytest.mark.parametrize("prefix", ["fcd", "fcw"])
def test_new_prefix_raw_cap_is_inclusive(tmp_path, prefix):
    records, witness, crg, vcn = world()
    d = declaration(witness, crg, vcn)
    chosen = d if prefix == "fcd" else withdrawal(d)
    store = kernel.ModelStore(tmp_path / "fc001-disposable")
    for record in (*records, d):
        store.append(record)
    if prefix == "fcw":
        store.append(chosen)
    path = store.records_dir / (chosen.record_id + ".json")
    raw = path.read_bytes()
    path.write_bytes(raw + b" " * (1048576 - len(raw)))
    assert chosen.record_id in store.load().records
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(kernel.ModelIntegrityError) as caught:
        store.load()
    assert caught.value.error_code == "MODEL_FLOW_CRITERION_RECORD_LIMIT_EXCEEDED"


@pytest.mark.parametrize("mutation,code", [
    ("stale_id", "MODEL_RECORD_HASH_MISMATCH"),
    ("wrong_shape", "MODEL_RECORD_INVALID"),
    ("wrong_subject", "MODEL_FLOW_MEASUREMENT_SUPPORT_INVALID"),
])
def test_entire_witness_is_revalidated_before_fc_relations(mutation, code):
    records, witness, crg, vcn = world()
    if mutation == "stale_id":
        bad = witness.model_copy(update={"note": "forged stale id"})
    elif mutation == "wrong_shape":
        bad = witness.model_copy(update={"orientation": "guessed"})
    else:
        bad = replace(witness, variable_anchor_id=VAR_B)
    d = declaration(bad, crg, vcn)
    reject([*(r for r in records if r != witness), bad, d], code)


def test_active_independent_different_bodies_are_both_retained():
    records, witness, crg, vcn = world()
    a = declaration(witness, crg, vcn)
    other_vcn = replace(vcn, supersedes=(vcn.record_id,), note="explicit new edition")
    b = declaration(witness, crg, other_vcn)
    loaded = load(*records, other_vcn, a, b)
    assert index(loaded, "current_tips_by_root") == {a.record_id: (a.record_id,), b.record_id: (b.record_id,)}
    assert len(index(loaded, "ids_by_effective_body")) == 2


def test_conflicted_fm_witness_support_remains_structurally_admissible():
    records, witness, crg, vcn = world()
    left = replace(witness, supersedes=(witness.record_id,), note="left")
    right = replace(witness, supersedes=(witness.record_id,), note="right")
    d = declaration(witness, crg, vcn)
    loaded = load(*records, left, right, d)
    assert len(loaded.current_flow_measurement_tips_by_root[witness.record_id]) == 2
    assert index(loaded, "current_tips_by_root")[d.record_id] == (d.record_id,)


@pytest.mark.parametrize("attribute", [
    "__pydantic_fields_set__", "__pydantic_extra__", "__pydantic_private__"])
def test_missing_fc_instance_metadata_is_typed_invalid(attribute):
    _, witness, crg, vcn = world()
    forged = declaration(witness, crg, vcn)
    object.__delattr__(forged, attribute)
    with pytest.raises(kernel.ModelIntegrityError) as caught:
        revalidate(forged)
    assert caught.value.error_code == "MODEL_RECORD_INVALID"


def test_stored_record_normalized_limit_after_defaults_keeps_limit_code(tmp_path):
    _, witness, crg, vcn = world()
    d = declaration(witness, crg, vcn)
    payload = d.model_dump(mode="json")
    for field in ("record_kind", "schema_version", "supersedes"):
        payload.pop(field)
    payload["evidence"] = [dict(kind="owner_declaration", statement=str(i) + "x" * 15999)
                           for i in range(8)]
    size = len(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())
    payload["note"] = "n" * (131072 - size)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    assert len(raw) == 131072
    store = kernel.ModelStore(tmp_path / "fc001-disposable")
    (store.records_dir / (d.record_id + ".json")).write_bytes(raw)
    with pytest.raises(kernel.ModelIntegrityError) as caught:
        store.load()
    assert caught.value.error_code == "MODEL_FLOW_CRITERION_RECORD_LIMIT_EXCEEDED"
