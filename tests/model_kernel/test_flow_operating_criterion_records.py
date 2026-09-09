"""Disposable FC record contract and hostile-input tests; no ledger writes."""

import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone, tzinfo
from typing import get_args

import pytest
from pydantic import TypeAdapter, ValidationError

import backend.model_kernel as mk
from backend.model_kernel.contracts import ModelRecord
from backend.model_kernel.canonical import canonical_bytes, compute_record_id


def contract(withdrawal=False):
    name = "FlowOperatingCriterionWithdrawal" if withdrawal else "FlowOperatingCriterionDeclaration"
    cls = getattr(mk, name, None)
    assert cls is not None
    return cls


def fields(withdrawal=False):
    result = dict(recorded_at="2026-09-09T00:00:00Z", authority=dict(
        kind="test_fixture", agent="fixture", method="manual_declaration"))
    if withdrawal:
        result["withdraws"] = "fcd_" + "a" * 64
    else:
        result.update(flow_measurement_association_record_id="fma_" + "a" * 64,
                      constraint_registration_record_id="crg_" + "b" * 64,
                      constraint_declaration_record_id="vcn_" + "c" * 64,
                      evidence=[dict(kind="owner_declaration", statement="designation")])
    return result


def raw(withdrawal=False):
    return dict(record_id=("fcw_" if withdrawal else "fcd_") + "0" * 64,
                **fields(withdrawal))


@pytest.mark.parametrize("withdrawal", [False, True])
def test_exact_schema_and_defaults(withdrawal):
    cls = contract(withdrawal)
    middle = ("withdraws",) if withdrawal else (
        "flow_measurement_association_record_id", "constraint_registration_record_id",
        "constraint_declaration_record_id", "evidence", "supersedes")
    assert tuple(cls.model_fields) == ("record_kind", "schema_version", "record_id", *middle,
                                       "recorded_at", "authority", "note")
    record = cls(**raw(withdrawal))
    assert record.note == "" and record.schema_version == "1"
    assert cls.model_config["frozen"] and cls.model_config["extra"] == "forbid"
    assert cls.model_config["revalidate_instances"] == "always"
    assert get_args(ModelRecord)[-2:] == (contract(), contract(True))
    assert type(TypeAdapter(ModelRecord).validate_python(record)) is cls


def test_exact_append_only_exports():
    assert len(mk.__all__) == len(set(mk.__all__)) == 227
    digest = lambda names: hashlib.sha256(json.dumps(names, separators=(",", ":")).encode()).hexdigest()
    assert digest(mk.__all__[:225]) == "097fe647d38bfd0947d1cac94583a1fd50bda5c15b5386ac3137c781097e414a"
    assert digest(mk.__all__) == "756698e83e44948ed24646d2808b9cfeb1f0d8c6f7d7650b2d61c455851afefd"


@pytest.mark.parametrize("withdrawal", [False, True])
def test_independent_literal_canonical_golden(withdrawal):
    # Literal compact projection, independent of production serialization.
    authority = '"authority":{"agent":"fixture","kind":"test_fixture","method":"manual_declaration"},'
    if withdrawal:
        golden = ('{' + authority + '"note":"","record_kind":"flow_operating_criterion_withdrawal",'
                  '"recorded_at":"2026-09-09T00:00:00+00:00","schema_version":"1",'
                  '"withdraws":"fcd_' + 'a' * 64 + '"}')
    else:
        golden = ('{' + authority + '"constraint_declaration_record_id":"vcn_' + 'c' * 64 + '",'
                  '"constraint_registration_record_id":"crg_' + 'b' * 64 + '",'
                  '"evidence":[{"kind":"owner_declaration","statement":"designation"}],'
                  '"flow_measurement_association_record_id":"fma_' + 'a' * 64 + '",'
                  '"note":"","record_kind":"flow_operating_criterion_declaration",'
                  '"recorded_at":"2026-09-09T00:00:00+00:00","schema_version":"1","supersedes":[]}')
    record = mk.build_record(contract(withdrawal), **fields(withdrawal))
    assert canonical_bytes(record) == golden.encode()
    assert record.record_id == ("fcw_" if withdrawal else "fcd_") + hashlib.sha256(golden.encode()).hexdigest()
    assert contract(withdrawal).model_validate_json(record.model_dump_json()) == record


def test_witness_and_normalization():
    cls = contract()
    values = fields()
    base = mk.build_record(cls, **values)
    values["recorded_at"] = datetime(2026, 9, 9, 2, tzinfo=timezone(timedelta(hours=2)))
    values["evidence"] *= 2
    assert mk.build_record(cls, **values) == base
    values["flow_measurement_association_record_id"] = "fma_" + "d" * 64
    assert mk.build_record(cls, **values).record_id != base.record_id
    values["evidence"] += [dict(kind="owner_declaration", statement="another")]
    values["supersedes"] = ["fcd_" + c * 64 for c in "ba"]
    first = mk.build_record(cls, **values)
    values["evidence"].reverse()
    values["supersedes"].reverse()
    assert mk.build_record(cls, **values) == first


@pytest.mark.parametrize("change", [dict(evidence=[]), dict(evidence=None), dict(note=None),
    dict(supersedes=["fcd_" + "a" * 64] * 2), dict(supersedes=["fcd_" + "0" * 64]),
    dict(supersedes=["fcw_" + "a" * 64]), dict(recorded_at=0), dict(recorded_at="2026-09-09"),
    dict(note=b"secret"), dict(record_kind="other"), dict(schema_version=1), dict(extra="secret")])
def test_invalid_shapes_have_fixed_value_free_outer_error(change):
    with pytest.raises(ValidationError) as raised:
        contract()(**(raw() | change))
    assert "FC_RECORD_INVALID" in str(raised.value)
    assert "secret" not in str(raised.value)
    assert len(raised.value.errors()) == 1
    assert raised.value.errors()[0]["input"] is None


def test_positive_only_citability_and_withdrawal_fields():
    cls = contract(True)
    mk.ModelRecordEvidence(kind="model_record", record_id="fcd_" + "a" * 64)
    with pytest.raises(ValidationError):
        mk.ModelRecordEvidence(kind="model_record", record_id="fcw_" + "a" * 64)
    for extra in (dict(evidence=[]), dict(supersedes=[])):
        with pytest.raises(ValidationError, match="FC_RECORD_INVALID"):
            cls(**(raw(True) | extra))


@pytest.mark.parametrize("field,limit", [("note", 8192), ("agent", 1024), ("statement", 16384)])
def test_inclusive_utf8_limits(field, limit):
    cls = contract()
    for size in (limit, limit + 1):
        values = raw()
        target = values if field == "note" else values["authority"] if field == "agent" else values["evidence"][0]
        target[field] = "é" * (size // 2) + "x" * (size % 2)
        if size == limit:
            cls(**values)
        else:
            with pytest.raises(ValidationError, match="FC_RECORD_LIMIT_EXCEEDED"):
                cls(**values)
            with pytest.raises(mk.ModelIntegrityError) as raised:
                mk.build_record(cls, **{k: v for k, v in values.items() if k != "record_id"})
            assert raised.value.error_code == "MODEL_FLOW_CRITERION_RECORD_LIMIT_EXCEEDED"


@pytest.mark.parametrize("field", ["evidence", "supersedes"])
def test_pre_normalization_cardinality(field):
    cls = contract()
    values = raw()
    values[field] = ([dict(kind="owner_declaration", statement="same")] * 64 if field == "evidence"
                     else ["fcd_" + format(i + 1, "064x") for i in range(64)])
    cls(**values)
    values[field].append(values[field][0])
    with pytest.raises(ValidationError, match="FC_RECORD_LIMIT_EXCEEDED"):
        cls(**values)


@pytest.mark.parametrize("attack", ["cycle", "dag", "depth", "nodes", "containers", "mapping", "integer", "surrogate", "nonfinite"])
def test_graph_preflight_before_field_validation(attack):
    cls = contract()
    node = []
    expected = "FC_RECORD_LIMIT_EXCEEDED"
    if attack == "cycle":
        node.append(node)
        expected = "FC_RECORD_INVALID"
    elif attack == "dag":
        for _ in range(20):
            node = [node, node]
    elif attack == "depth":
        for _ in range(33):
            node = [node]
    elif attack == "nodes":
        node = [[None] * 256] * 40
    elif attack == "containers":
        node = [[[]] * 200] * 20
    elif attack == "mapping":
        node = {str(i): None for i in range(257)}
    elif attack == "integer":
        node = 1 << 4096
    elif attack == "surrogate":
        node = "\ud800"
        expected = "FC_RECORD_INVALID"
    else:
        node = float("inf")
        expected = "FC_RECORD_INVALID"
    with pytest.raises(ValidationError, match=expected):
        cls(**(raw() | dict(extra=node)))


def test_full_instance_revalidation_and_hostile_callbacks():
    cls = contract()
    calls = []
    class Hostile(str):
        def __str__(self):
            calls.append("str")
            raise AssertionError
    class HostileAuthority(mk.AuthorityRef):
        def model_dump(self, **kwargs):
            calls.append("dump")
            raise AssertionError
    class HostileZone(tzinfo):
        def utcoffset(self, dt):
            calls.append("timezone")
            raise AssertionError
    attacks = [dict(note=Hostile("secret")), dict(authority=HostileAuthority.model_construct()),
               dict(recorded_at=datetime(2026, 9, 9, tzinfo=HostileZone()))]
    valid = cls(**raw())
    forged = valid.model_copy(update={"note": Hostile("secret")})
    private = valid.model_copy()
    object.__setattr__(private, "_cache", "secret")
    for value in [*(raw() | a for a in attacks), forged, private]:
        with pytest.raises(ValidationError, match="FC_RECORD_INVALID"):
            cls.model_validate(value)
    assert calls == []


@pytest.mark.parametrize("attack,expected", [("duplicate", "INVALID"), ("depth", "LIMIT_EXCEEDED"),
    ("raw", "LIMIT_EXCEEDED"), ("integer", "LIMIT_EXCEEDED"), ("bytes-subclass", "INVALID")])
def test_json_preparse_boundary(attack, expected):
    cls = contract()
    if attack == "duplicate":
        value = '{"note":"secret","note":"other"}'
    elif attack == "depth":
        value = "[" * 34 + "0" + "]" * 34
    elif attack == "raw":
        value = " " * 1048577
    elif attack == "integer":
        value = '{"note":' + "9" * 1235 + "}"
    else:
        class Sub(bytes):
            pass
        value = Sub(b"{}")
    with pytest.raises(ValidationError, match="FC_RECORD_" + expected) as raised:
        cls.model_validate_json(value)
    assert "secret" not in str(raised.value)


def test_alternate_strings_entrypoint_rejects():
    with pytest.raises(ValidationError, match="FC_RECORD_INVALID"):
        contract().model_validate_strings(raw())


def test_builder_rejects_unknown_and_subclass_without_callbacks():
    cls = contract()
    calls = []
    class Sub(cls):
        @classmethod
        def model_validate(cls, *args, **kwargs):
            calls.append("validate")
            raise AssertionError
    class Forged:
        def __getattribute__(self, name):
            calls.append(name)
            raise AssertionError
    for target in (Sub, Forged()):
        with pytest.raises(mk.ModelIntegrityError) as raised:
            mk.build_record(target, **fields())
        assert raised.value.error_code == "MODEL_RECORD_INVALID"
    assert calls == []


@pytest.mark.parametrize("operation", [canonical_bytes, compute_record_id])
def test_canonical_revalidates_forged_fc_before_dump(operation):
    cls = contract()
    valid = cls(**raw())
    forged = valid.model_copy(update={"note": "x" * 8193})
    with pytest.raises(mk.ModelIntegrityError) as raised:
        operation(forged)
    assert raised.value.error_code == "MODEL_FLOW_CRITERION_RECORD_LIMIT_EXCEEDED"


def test_aggregate_bytes_inclusive_and_pre_normalization():
    cls = contract()
    values = raw()
    # Supply defaults explicitly to independently measure the complete envelope.
    values.update(record_kind="flow_operating_criterion_declaration", schema_version="1",
                  note="", supersedes=[], recorded_at="2026-09-09T00:00:00+00:00")
    values["evidence"] = [dict(kind="owner_declaration", statement=str(i) + "x" * 15999)
                          for i in range(8)]
    size = len(json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())
    values["note"] = "n" * (131072 - size)
    cls(**values)
    values["note"] += "x"
    with pytest.raises(ValidationError, match="FC_RECORD_LIMIT_EXCEEDED"):
        cls(**values)


def test_json_raw_inclusive_and_escaped_duplicate_key():
    cls = contract()
    value = json.dumps(raw())
    cls.model_validate_json(value + " " * (1048576 - len(value)))
    with pytest.raises(ValidationError, match="FC_RECORD_INVALID"):
        cls.model_validate_json('{"note":"a","no\\u0074e":"b"}')


def test_model_metadata_rejects_hostile_fields_set_without_callbacks():
    cls = contract()
    record = cls(**raw())
    class HostileSet(set):
        def __iter__(self):
            raise AssertionError("callback")
    object.__setattr__(record, "__pydantic_fields_set__", HostileSet())
    with pytest.raises(ValidationError, match="FC_RECORD_INVALID"):
        cls.model_validate(record)


@pytest.mark.parametrize("budget,maximum", [("nodes", 8192), ("containers", 2048), ("depth", 32)])
def test_expanded_budget_exact_edge_and_one_over(budget, maximum):
    cls = contract()
    def counts(value, depth=0):
        if type(value) is dict:
            children = [counts(child, depth + 1) for pair in value.items() for child in pair]
        elif type(value) is list:
            children = [counts(child, depth + 1) for child in value]
        else:
            return (1, 0, depth)
        return (1 + sum(c[0] for c in children), 1 + sum(c[1] for c in children),
                max([depth, *(c[2] for c in children)]))
    index = {"nodes": 0, "containers": 1, "depth": 2}[budget]
    for limit in (maximum, maximum + 1):
        values = raw()
        values["extra"] = []
        if budget == "depth":
            node = None
            for _ in range(limit - 1):
                node = [node]
            values["extra"] = node
        else:
            groups = values["extra"]
            used = counts(values)[index]
            while used < limit:
                if not groups or len(groups[-1]) == 200:
                    groups.append([])
                    used += 1
                if used < limit:
                    groups[-1].append(None if budget == "nodes" else [])
                    used += 1
        assert counts(values)[index] == limit
        message = "FC_RECORD_INVALID" if limit == maximum else "FC_RECORD_LIMIT_EXCEEDED"
        with pytest.raises(ValidationError, match=message):
            cls(**values)


@pytest.mark.parametrize("bits", [4096, 4097])
def test_integer_bit_boundary(bits):
    cls = contract()
    values = raw() | dict(extra=(1 << bits) - 1)
    message = "FC_RECORD_INVALID" if bits == 4096 else "FC_RECORD_LIMIT_EXCEEDED"
    with pytest.raises(ValidationError, match=message):
        cls(**values)
    with pytest.raises(ValidationError, match=message):
        cls.model_validate_json(json.dumps(values))


def test_json_integer_boundary_independent_of_ambient_digit_limit():
    cls = contract()
    # 1,001 digits, safely below 4,096 bits, but above the ambient limit.
    value = '{"extra":1' + '0' * 1000 + '}'
    previous = sys.get_int_max_str_digits()
    try:
        sys.set_int_max_str_digits(640)
        with pytest.raises(ValidationError, match="FC_RECORD_INVALID") as raised:
            cls.model_validate_json(value)
        # Inspect the private chained parse cause: semantic invalidity must
        # follow successful bounded reconstruction, not the ambient int guard.
        cause = raised.value.__cause__
        while cause is not None:
            assert "Exceeds the limit" not in str(cause)
            cause = cause.__cause__
    finally:
        sys.set_int_max_str_digits(previous)
