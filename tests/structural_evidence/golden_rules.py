"""Hand-authored behaviour vectors for the subject-identity rules (R5).

Authored from the rule STATEMENTS in the SN-001 spec — never from the
implementation and never from the showcase generator (independent-oracle
rule). Each row: (rule_id, claim description, expected subject value or
None).

Rule statements the rows are written from:
- bom-item-no-v1: subject identity is the exact lexeme of the cell in the
  column whose name, as exposed by the accepted CSV extractor after its
  documented header processing, is literally `item_no`, matched
  `exact_as_extracted`; an absent field, absent lexeme, or empty lexeme
  means the row HAS NO subject identity — a first-class outcome, never a
  fallback and never an empty string.
- bom-physical-row-v1: subject identity is the payload checksum plus the
  extractor config fingerprint plus the physical row index — valid for
  exactly these bytes under exactly this extraction configuration.
- step-ocaf-entry-v1: subject identity is the extractor's OCAF label
  entry verbatim; the namespace (not the value) carries the extractor and
  toolchain identity.
"""

CHECKSUM = "sha256:" + "ab" * 32
CONFIG_FP = "6f1c2a9d0b3e4517"

# (rule_id, field_name, lexeme, expected)  — bom-item-no-v1 over one row
ITEM_NO_VECTORS = [
    ("exact match yields the verbatim lexeme",
     "item_no", "100-002", "100-002"),
    ("a case-differing name is a DIFFERENT column — no subject identity",
     "Item_No", "100-002", None),
    ("an empty lexeme means no subject identity, never an empty string",
     "item_no", "", None),
    ("an absent lexeme (None cell) means no subject identity",
     "item_no", None, None),
    ("surrounding whitespace in the lexeme is preserved, not stripped",
     "item_no", " 100-002", " 100-002"),
]

# (description, physical_row_index, expected)  — bom-physical-row-v1
PHYSICAL_ROW_VECTORS = [
    ("row identity binds bytes, config, and position",
     3, f"{CHECKSUM};{CONFIG_FP};r=3"),
    ("row zero is a valid position",
     0, f"{CHECKSUM};{CONFIG_FP};r=0"),
]

# (description, extractor_path_id, expected)  — step-ocaf-entry-v1
STEP_PATH_VECTORS = [
    ("the OCAF entry is the value, verbatim", "0:1:1:3:1", "0:1:1:3:1"),
    ("a single-hyphen entry is a value, not a sentinel", "-", "-"),
]

# Exact quote(value, safe="") outputs pinned against encoder drift (R12).
ENCODER_VECTORS = [
    ("a:b", "a%3Ab"),
    ("a/b", "a%2Fb"),
    ("..", ".."),
    ("%3A", "%253A"),
    ("-", "-"),
    ("0:1:1:3:1", "0%3A1%3A1%3A3%3A1"),
    ("sx1:csv:x:1:0:0:r:0", "sx1%3Acsv%3Ax%3A1%3A0%3A0%3Ar%3A0"),
]
