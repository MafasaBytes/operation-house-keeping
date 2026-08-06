"""Conservative payload format detection.

Rules (spec §Format detection): confirm STEP only on its ISO-10303-21
signature (tolerating a UTF-8 BOM and leading whitespace); identify a
proprietary native-CAD family only on high-confidence signatures and never
guess a vendor from container magic; everything else is
``unsupported_or_unknown_format``.
"""

import re
from typing import Literal

from pydantic import ConfigDict

from backend.data_sources.contracts.models import _FrozenModel

DetectionStatus = Literal[
    "confirmed_step", "unsupported_native_cad", "unsupported_or_unknown_format"
]

_OLE_CFB_MAGIC = bytes.fromhex("d0cf11e0a1b11ae1")
_DWG_PREFIX = re.compile(rb"^AC10\d\d")


class FormatDetection(_FrozenModel):
    model_config = ConfigDict(frozen=True)

    status: DetectionStatus
    detected_container: str | None
    evidence: str


def detect_format(payload: bytes, declared_content_type: str) -> FormatDetection:
    head = payload[:4096]

    if head.startswith(_OLE_CFB_MAGIC):
        return FormatDetection(
            status="unsupported_native_cad",
            detected_container="ole_compound_container",
            evidence="payload begins with the OLE compound-file signature; "
            "native CAD formats require a vendor extraction pipeline and are "
            "not supported",
        )
    if _DWG_PREFIX.match(head):
        return FormatDetection(
            status="unsupported_native_cad",
            detected_container="dwg",
            evidence="payload begins with a DWG version signature; native CAD "
            "formats require a vendor extraction pipeline and are not supported",
        )

    stripped = head
    if stripped.startswith(b"\xef\xbb\xbf"):
        stripped = stripped[3:]
    stripped = stripped.lstrip(b" \t\r\n")
    if stripped.startswith(b"ISO-10303-21"):
        return FormatDetection(
            status="confirmed_step",
            detected_container=None,
            evidence=f"ISO-10303-21 signature present; declared content type "
            f"{declared_content_type!r}",
        )

    return FormatDetection(
        status="unsupported_or_unknown_format",
        detected_container=None,
        evidence="payload matches no supported signature with high "
        "confidence; refusing to guess a format",
    )


_FILE_SCHEMA = re.compile(rb"FILE_SCHEMA\s*\(\s*\((?P<body>.*?)\)\s*\)\s*;", re.DOTALL)
_SCHEMA_STRING = re.compile(rb"'((?:[^']|'')*)'")


def parse_declared_schemas(payload: bytes) -> list[str]:
    """Parse the Part 21 FILE_SCHEMA header record.

    A file may declare several schemas or long schema identifiers; all are
    returned verbatim. Absence yields an empty list, never a guess.
    """
    match = _FILE_SCHEMA.search(payload[:65536])
    if not match:
        return []
    return [
        raw.decode("utf-8", errors="replace").replace("''", "'")
        for raw in _SCHEMA_STRING.findall(match.group("body"))
    ]
