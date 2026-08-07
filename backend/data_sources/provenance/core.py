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


def derive_keyed_record_id(source_id: str, item_key: str, checksum: str) -> str:
    """API raw-record identity: same source + acquisition item + payload
    bytes yields the same id. Sweep position is never identity (ordering
    evidence only); the DS-001-003 positional derivation is untouched."""
    material = "|".join(
        f"{len(part)}:{part}" for part in ("keyed", source_id, item_key, checksum)
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]


def derive_entity_id(raw_record_id: str, extractor_version: str, path_id: str) -> str:
    """Deterministic id for an extracted entity: same raw payload, extractor
    version, and toolchain path ⇒ same id."""
    material = "|".join(
        f"{len(part)}:{part}" for part in (raw_record_id, extractor_version, path_id)
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


_SECRET_KV = re.compile(
    r"(?i)\b(password|passwd|pwd|token|secret|api[_-]?key|apikey|auth|credential)"
    r"\s*[=:]\s*[^\s&\"';,]+"
)
_URL_USERINFO = re.compile(r"://[^/@\s]+@")
_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]")


def scrub_secrets(text: str) -> str:
    """Remove credential-shaped substrings: key=value secrets and URL
    userinfo. Complements redact_text (paths); both run before anything is
    persisted."""
    text = _SECRET_KV.sub(lambda m: f"{m.group(1)}=<redacted>", text)
    return _URL_USERINFO.sub("://<redacted>@", text)


def sanitize_uri(uri: str, max_len: int = 200) -> str:
    """Reduce a URI to non-sensitive evidence: scheme, host[:port], and a
    safe basename. Userinfo, query values, and fragments never survive."""
    from urllib.parse import urlsplit

    try:
        parts = urlsplit(str(uri)[:1000])
        host = parts.hostname or ""
        port = f":{parts.port}" if parts.port else ""
    except ValueError:
        return "<unparseable-uri>"
    scheme = parts.scheme or "uri"
    basename = _SAFE_NAME.sub("_", parts.path.rsplit("/", 1)[-1])[:80]
    path = f"/{basename}" if basename else ""
    query = "?<redacted-query>" if parts.query else ""
    fragment = "#<redacted-fragment>" if parts.fragment else ""
    return f"{scheme}://{host}{port}{path}{query}{fragment}"[:max_len]


def sanitize_source_text(text, max_len: int = 500) -> str | None:
    """Bound, secret-scrub, and path-redact an untrusted source-derived
    string before it may appear in any persisted artifact."""
    if text is None:
        return None
    bounded = str(text)[:max_len]
    return redact_text(scrub_secrets(bounded), base_dir="")


def safe_basename(name) -> str:
    """A filesystem-path-free, safe rendering of an untrusted filename."""
    if name is None:
        return "<unnamed>"
    tail = str(name).replace("\\", "/").rsplit("/", 1)[-1]
    return _SAFE_NAME.sub("_", tail)[:120] or "<unnamed>"


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
