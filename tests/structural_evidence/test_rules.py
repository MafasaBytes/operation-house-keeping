"""Subject-identity rules, fingerprints, and the sx1 namespace (R1-R12).

The K1 contract: changes to rule DATA are content-addressed and
necessarily create a new subject namespace; changes to the shared
interpreter or encoder are guarded by a versioned algorithm contract
(`sx1`, `semantics_version`), the hand-authored vectors in
`golden_rules.py`, and the drift tests here — by tests and review, not by
construction alone.
"""

import ast
import hashlib
import inspect
import json
from urllib.parse import quote

import pytest
from pydantic import ValidationError

from backend.data_sources.extractors.csv_extractor import (
    CsvExtractionConfig,
    csv_extractor_identity,
)
from backend.structural_evidence import rules as rules_module
from backend.structural_evidence.contracts import (
    SourceNativeField,
    SourceStructuralClaim,
)
from backend.structural_evidence.errors import StructuralEvidenceError
from backend.structural_evidence.locators import (
    CsvCellLocator,
    CsvRowLocator,
    StepDefinitionLocator,
    StructuralAddress,
    StructuralSourceRef,
)
from backend.structural_evidence.rules import (
    SUBJECT_RULES,
    CsvColumnLexemeRuleBody,
    CsvPhysicalRowRuleBody,
    StepPathRuleBody,
    SubjectIdentityRule,
    apply_rule,
    parse_structural_namespace,
    rule_fingerprint,
    structural_namespace,
    to_source_subject_ref,
    toolchain_fingerprint,
)

from tests.structural_evidence.golden_rules import (
    CHECKSUM,
    CONFIG_FP,
    ENCODER_VECTORS,
    ITEM_NO_VECTORS,
    PHYSICAL_ROW_VECTORS,
    STEP_PATH_VECTORS,
)

EXTRACTOR = csv_extractor_identity(CsvExtractionConfig())


def source_ref(extractor=EXTRACTOR, source_id="showcase-printer-bom"):
    return StructuralSourceRef(
        source_id=source_id, raw_record_id="cd" * 16,
        payload_checksum=CHECKSUM, extractor=extractor)


def bom_row_claim(field_name="item_no", lexeme="100-002", row=3,
                  extractor=EXTRACTOR):
    ref = source_ref(extractor=extractor)
    address = StructuralAddress(
        source=ref, locator=CsvRowLocator(kind="csv_row",
                                          physical_row_index=row))
    cell = StructuralAddress(
        source=ref,
        locator=CsvCellLocator(kind="csv_cell", physical_row_index=row,
                               column_index=0,
                               column_name_as_extracted=field_name))
    return SourceStructuralClaim(
        claim_kind="bom_row", address=address,
        fields=(SourceNativeField(field_name_as_extracted=field_name,
                                  lexeme=lexeme, address=cell),))


def step_definition_claim(path="0:1:1:3:1"):
    ref = source_ref(source_id="showcase-printer-cad")
    return SourceStructuralClaim(
        claim_kind="step_part_definition",
        address=StructuralAddress(
            source=ref,
            locator=StepDefinitionLocator(kind="step_part_definition",
                                          extractor_path_id=path,
                                          upstream_definition_id="b0" * 16)))


def restated_fingerprint(body) -> str:
    """Independent restatement of the published formula — the two
    canonicalizers must agree (house pattern)."""
    material = json.dumps(body.model_dump(mode="python"), sort_keys=True,
                          separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


class TestR1GoldenFingerprints:
    def test_shipped_fingerprints_match_the_restated_formula(self):
        for rule in SUBJECT_RULES.values():
            assert rule.fingerprint == restated_fingerprint(rule.body)

    def test_shipped_rule_ids(self):
        assert set(SUBJECT_RULES) == {
            "bom-item-no-v1", "bom-physical-row-v1", "step-ocaf-entry-v1"}


class TestR2R3FingerprintScope:
    def test_r2_body_change_changes_fingerprint_and_namespace(self):
        rule = SUBJECT_RULES["bom-item-no-v1"]
        changed = SubjectIdentityRule(
            rule_id=rule.rule_id, applies_to=rule.applies_to,
            body=CsvColumnLexemeRuleBody(
                rule_kind="csv_column_lexeme", semantics_version="v1",
                column_name_as_extracted="part_number",
                name_match="exact_as_extracted",
                empty_lexeme_outcome="no_subject_identity"),
            statement=rule.statement, stability=rule.stability)
        assert changed.fingerprint != rule.fingerprint
        assert (structural_namespace("csv", EXTRACTOR, changed)
                != structural_namespace("csv", EXTRACTOR, rule))

    def test_r3_statement_and_stability_are_not_fingerprinted(self):
        rule = SUBJECT_RULES["bom-item-no-v1"]
        reworded = SubjectIdentityRule(
            rule_id=rule.rule_id, applies_to=rule.applies_to, body=rule.body,
            statement="Reworded prose, same behaviour.",
            stability="payload_pinned")
        assert reworded.fingerprint == rule.fingerprint
        assert (structural_namespace("csv", EXTRACTOR, reworded)
                == structural_namespace("csv", EXTRACTOR, rule))


class TestR4InterpreterReadsOnlyTheFingerprint:
    def test_apply_rule_reads_exactly_the_body_fields(self):
        """The set of attributes apply_rule reads off its body parameter
        equals the union of the body classes' model_fields. Reading a new
        field requires adding it to a body class — changing every
        fingerprint."""
        tree = ast.parse(inspect.getsource(rules_module))
        reads: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "apply_rule":
                for sub in ast.walk(node):
                    if (isinstance(sub, ast.Attribute)
                            and isinstance(sub.value, ast.Name)
                            and sub.value.id == "body"):
                        reads.add(sub.attr)
        expected = (set(CsvColumnLexemeRuleBody.model_fields)
                    | set(CsvPhysicalRowRuleBody.model_fields)
                    | set(StepPathRuleBody.model_fields))
        assert reads == expected


class TestR5BehaviourVectors:
    @pytest.mark.parametrize("description,field_name,lexeme,expected",
                             ITEM_NO_VECTORS)
    def test_item_no_vectors(self, description, field_name, lexeme, expected):
        claim = bom_row_claim(field_name=field_name, lexeme=lexeme)
        body = SUBJECT_RULES["bom-item-no-v1"].body
        assert apply_rule(body, claim) == expected, description

    @pytest.mark.parametrize("description,row,expected", PHYSICAL_ROW_VECTORS)
    def test_physical_row_vectors(self, description, row, expected):
        # the vectors are authored against this exact pinned identity
        pinned = EXTRACTOR.model_copy(
            update={"config_fingerprint": CONFIG_FP})
        claim = bom_row_claim(row=row, extractor=pinned)
        body = SUBJECT_RULES["bom-physical-row-v1"].body
        assert apply_rule(body, claim) == expected, description

    @pytest.mark.parametrize("description,path,expected", STEP_PATH_VECTORS)
    def test_step_path_vectors(self, description, path, expected):
        claim = step_definition_claim(path=path)
        body = SUBJECT_RULES["step-ocaf-entry-v1"].body
        assert apply_rule(body, claim) == expected, description


class TestR6R7NamespaceCollisions:
    def test_r6_header_lexeme_collision(self):
        a = SUBJECT_RULES["bom-item-no-v1"]
        b = SubjectIdentityRule(
            rule_id="bom-part-number-v1", applies_to=a.applies_to,
            body=CsvColumnLexemeRuleBody(
                rule_kind="csv_column_lexeme", semantics_version="v1",
                column_name_as_extracted="part_number",
                name_match="exact_as_extracted",
                empty_lexeme_outcome="no_subject_identity"),
            statement="Part-number reading.", stability="source_native_key")
        assert (structural_namespace("csv", EXTRACTOR, a)
                != structural_namespace("csv", EXTRACTOR, b))

    def test_r7_config_fingerprint_through_the_real_extractor_identity(self):
        """The previous design's bug: extractor NAME as the namespace.
        Two configs differing only in header_row_index must produce
        different namespaces."""
        default = csv_extractor_identity(CsvExtractionConfig())
        shifted = csv_extractor_identity(
            CsvExtractionConfig(header_row_index=2))
        assert default.config_fingerprint != shifted.config_fingerprint
        rule = SUBJECT_RULES["bom-item-no-v1"]
        assert (structural_namespace("csv", default, rule)
                != structural_namespace("csv", shifted, rule))


class TestR8R12EncodingSafety:
    @pytest.mark.parametrize("value,encoded", ENCODER_VECTORS)
    def test_r12_encoder_drift_literals(self, value, encoded):
        assert quote(value, safe="") == encoded

    @pytest.mark.parametrize("value", [v for v, _ in ENCODER_VECTORS])
    def test_r8_no_value_forges_a_namespace_boundary(self, value):
        rule = SUBJECT_RULES["bom-item-no-v1"]
        subject = to_source_subject_ref(
            bom_row_claim().address, rule, value)
        assert subject.adapter_id.count(":") == 7
        parsed = parse_structural_namespace(subject.adapter_id)
        assert parsed.rule_id == "bom-item-no-v1"
        assert ":" not in subject.subject_identifier or value == ""


class TestR9R10R11Namespace:
    def test_r9_nine_way_perturbation(self):
        """Changing exactly one identity dimension changes the subject."""
        rule = SUBJECT_RULES["bom-item-no-v1"]
        base = to_source_subject_ref(bom_row_claim().address, rule, "100-002")
        variants = []
        # 1-2: family is builder input; different family, different namespace
        variants.append(structural_namespace("step", EXTRACTOR, rule))
        # 3: extractor version
        other = EXTRACTOR.model_copy(update={"version": "9.9.9"})
        variants.append(structural_namespace("csv", other, rule))
        # 4: config fingerprint
        other = EXTRACTOR.model_copy(update={"config_fingerprint": "f" * 16})
        variants.append(structural_namespace("csv", other, rule))
        # 5: toolchain
        other = EXTRACTOR.model_copy(update={"toolchain": "occt 8.0"})
        variants.append(structural_namespace("csv", other, rule))
        # 6: rule id
        renamed = SubjectIdentityRule(
            rule_id="bom-item-no-v2", applies_to=rule.applies_to,
            body=rule.body, statement=rule.statement, stability=rule.stability)
        variants.append(structural_namespace("csv", EXTRACTOR, renamed))
        # 7: rule fingerprint (body change)
        changed = SubjectIdentityRule(
            rule_id=rule.rule_id, applies_to=rule.applies_to,
            body=CsvColumnLexemeRuleBody(
                rule_kind="csv_column_lexeme", semantics_version="v1",
                column_name_as_extracted="x",
                name_match="exact_as_extracted",
                empty_lexeme_outcome="no_subject_identity"),
            statement=rule.statement, stability=rule.stability)
        variants.append(structural_namespace("csv", EXTRACTOR, changed))
        # 8: extractor name
        other = EXTRACTOR.model_copy(update={"name": "step_extractor"})
        variants.append(structural_namespace("csv", other, rule))
        assert len({base.adapter_id, *variants}) == 8
        # 9: source_id — same namespace, different subject
        moved = to_source_subject_ref(
            bom_row_claim(extractor=EXTRACTOR).address.model_copy(
                update={"source": source_ref(source_id="bom-elsewhere")}),
            rule, "100-002")
        assert moved.adapter_id == base.adapter_id
        assert moved != base

    def test_r10_round_trip_and_malformed_rejection(self):
        rule = SUBJECT_RULES["step-ocaf-entry-v1"]
        value = structural_namespace("step", EXTRACTOR, rule)
        parsed = parse_structural_namespace(value)
        assert (parsed.scheme, parsed.family) == ("sx1", "step")
        assert parsed.rule_fingerprint == rule.fingerprint
        assert parsed.toolchain_fingerprint == toolchain_fingerprint(EXTRACTOR)
        for bad in (value.rsplit(":", 1)[0],          # 7 parts
                    value + ":extra",                  # 9 parts
                    value.replace("sx1", "sx9", 1)):   # unknown scheme
            with pytest.raises(StructuralEvidenceError) as err:
                parse_structural_namespace(bad)
            assert err.value.error_code == "SN_NAMESPACE_INVALID"

    def test_r11_length_cap(self):
        rule = SUBJECT_RULES["bom-item-no-v1"]
        value = structural_namespace("csv", EXTRACTOR, rule)
        assert len(value) <= 256
        # worst case: every component at its alphabet maximum, with the
        # 4-char family "step", is exactly 254 (3+4+64+32+64+16+48+16 + 7)
        widest = EXTRACTOR.model_copy(update={
            "name": "a" * 64, "version": "9" * 32,
            "config_fingerprint": "f" * 64})
        widest_rule = SubjectIdentityRule(
            rule_id="r" + "x" * 47, applies_to=("bom_row",), body=rule.body,
            statement="s", stability="source_native_key")
        assert len(structural_namespace("step", widest, widest_rule)) == 254

    def test_rule_returning_none_produces_no_subject_ref(self):
        rule = SUBJECT_RULES["bom-item-no-v1"]
        claim = bom_row_claim(lexeme="")
        assert apply_rule(rule.body, claim) is None
        with pytest.raises(StructuralEvidenceError):
            to_source_subject_ref(claim.address, rule, None)


class TestRuleContract:
    def test_rules_are_frozen_and_registry_is_read_only(self):
        rule = SUBJECT_RULES["bom-item-no-v1"]
        with pytest.raises(ValidationError):
            rule.statement = "edited"
        with pytest.raises(TypeError):
            SUBJECT_RULES["new-rule"] = rule
