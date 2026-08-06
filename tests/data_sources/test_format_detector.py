"""Tests for the conservative format detector and FILE_SCHEMA parsing."""

from backend.data_sources.extractors import (
    detect_format,
    parse_declared_schemas,
)

STEP_HEAD = (
    b"ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION((''),'2;1');\n"
    b"FILE_NAME('demo','2026-08-06T12:00:00',(''),(''),'occt','','');\n"
    b"FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));\n"
    b"ENDSEC;\nDATA;\nENDSEC;\nEND-ISO-10303-21;\n"
)

OLE_CFB_MAGIC = bytes.fromhex("d0cf11e0a1b11ae1") + b"\x00" * 24
DWG_HEAD = b"AC1032" + b"\x00" * 26


class TestStepConfirmation:
    def test_plain_step_is_confirmed(self):
        result = detect_format(STEP_HEAD, declared_content_type="model/step")
        assert result.status == "confirmed_step"

    def test_utf8_bom_and_leading_whitespace_tolerated(self):
        payload = b"\xef\xbb\xbf  \r\n" + STEP_HEAD
        result = detect_format(payload, declared_content_type="model/step")
        assert result.status == "confirmed_step"

    def test_step_signature_required_even_if_declared(self):
        result = detect_format(b"item_no,name\n1,Frame\n", declared_content_type="model/step")
        assert result.status == "unsupported_or_unknown_format"


class TestNativeCadRejection:
    def test_ole_compound_container_detected_without_vendor_guess(self):
        result = detect_format(OLE_CFB_MAGIC, declared_content_type="model/step")
        assert result.status == "unsupported_native_cad"
        assert result.detected_container == "ole_compound_container"
        # No vendor is guessed from container magic alone.
        for vendor in ("solidworks", "catia", "inventor"):
            assert vendor not in result.evidence.lower()

    def test_dwg_detected_high_confidence(self):
        result = detect_format(DWG_HEAD, declared_content_type="model/step")
        assert result.status == "unsupported_native_cad"
        assert result.detected_container == "dwg"


class TestUnknownFallback:
    def test_weak_evidence_is_not_a_vendor_claim(self):
        result = detect_format(b"\x00\x01\x02random-binary", declared_content_type="model/step")
        assert result.status == "unsupported_or_unknown_format"

    def test_empty_payload_is_unknown(self):
        result = detect_format(b"", declared_content_type="model/step")
        assert result.status == "unsupported_or_unknown_format"


class TestDeclaredSchemas:
    def test_single_schema_parsed(self):
        assert parse_declared_schemas(STEP_HEAD) == [
            "AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }"
        ]

    def test_multiple_schemas_parsed(self):
        payload = STEP_HEAD.replace(
            b"FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));",
            b"FILE_SCHEMA(('CONFIG_CONTROL_DESIGN','AUTOMOTIVE_DESIGN'));",
        )
        assert parse_declared_schemas(payload) == [
            "CONFIG_CONTROL_DESIGN",
            "AUTOMOTIVE_DESIGN",
        ]

    def test_missing_schema_yields_empty_list(self):
        assert parse_declared_schemas(b"ISO-10303-21;\nHEADER;\nENDSEC;") == []
