"""Checksums, deterministic identifiers, and redaction helpers."""

import hashlib
import re


def payload_checksum(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def derive_record_id(source_id: str, checksum: str, position: int) -> str:
    """Deterministic record id: same source + payload + position ⇒ same id.

    Components are length-prefixed so no combination of values can collide
    through concatenation.
    """
    material = "|".join(
        f"{len(part)}:{part}" for part in (source_id, checksum, str(position))
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]


_ABS_PATH = re.compile(
    r"""
    (?<![\w.\-])                       # not inside a relative path or word
    (?:
      (?:/[^\s/'"()\[\],;]+)+/?        # POSIX absolute path
      | [A-Za-z]:[\\/](?:[^\s'"()\[\],;]+[\\/]?)*   # Windows drive path
    )
    """,
    re.VERBOSE,
)


def redact_text(text: str, base_dir: str) -> str:
    """Replace the store base dir with <store> and any other absolute path
    with <abs>, so persisted messages never leak local filesystem layout."""
    base = base_dir.rstrip("/")

    def _sub(match: re.Match[str]) -> str:
        path = match.group(0)
        if base and path.startswith(base):
            return "<store>" + path[len(base):]
        return "<abs>"

    return _ABS_PATH.sub(_sub, text)
