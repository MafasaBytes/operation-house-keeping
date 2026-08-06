"""Tests for checksums, deterministic record ids, and redaction."""

import hashlib

from backend.data_sources.provenance import (
    derive_record_id,
    payload_checksum,
    redact_text,
)


class TestPayloadChecksum:
    def test_matches_reference_sha256(self):
        data = b"item_no,name\n100-001,Frame\n"
        expected = "sha256:" + hashlib.sha256(data).hexdigest()
        assert payload_checksum(data) == expected

    def test_empty_payload_still_has_a_checksum(self):
        assert payload_checksum(b"").startswith("sha256:")


class TestDeriveRecordId:
    CHECKSUM = "sha256:" + "ab" * 32

    def test_deterministic(self):
        a = derive_record_id("bom-local", self.CHECKSUM, 0)
        b = derive_record_id("bom-local", self.CHECKSUM, 0)
        assert a == b

    def test_shape_is_32_lowercase_hex(self):
        record_id = derive_record_id("bom-local", self.CHECKSUM, 0)
        assert len(record_id) == 32
        assert all(c in "0123456789abcdef" for c in record_id)

    def test_any_component_change_changes_the_id(self):
        base = derive_record_id("bom-local", self.CHECKSUM, 0)
        assert derive_record_id("other-source", self.CHECKSUM, 0) != base
        assert derive_record_id("bom-local", "sha256:" + "cd" * 32, 0) != base
        assert derive_record_id("bom-local", self.CHECKSUM, 1) != base

    def test_no_delimiter_ambiguity(self):
        # ("ab", "c…") and ("a", "bc…") must not collide via concatenation.
        left = derive_record_id("ab", "sha256:" + "0" * 64, 0)
        right = derive_record_id("a", "sha256:" + "0" * 64, 0)
        assert left != right


class TestRedactText:
    def test_base_dir_replaced_with_store_placeholder(self):
        message = "cannot write /data/raw_store/envelopes/x.json"
        assert (
            redact_text(message, base_dir="/data/raw_store")
            == "cannot write <store>/envelopes/x.json"
        )

    def test_other_absolute_paths_replaced(self):
        message = "file /home/someone/private/bom.csv is unreadable"
        redacted = redact_text(message, base_dir="/data/raw_store")
        assert "/home/someone" not in redacted
        assert "<abs>" in redacted

    def test_windows_style_paths_replaced(self):
        message = r"file D:\projects\bom.csv is unreadable"
        redacted = redact_text(message, base_dir="/data/raw_store")
        assert "D:\\" not in redacted
        assert "<abs>" in redacted

    def test_relative_paths_and_plain_text_untouched(self):
        message = "row 3 of fixtures/bom_valid.csv has 4 fields, expected 5"
        assert redact_text(message, base_dir="/data/raw_store") == message
